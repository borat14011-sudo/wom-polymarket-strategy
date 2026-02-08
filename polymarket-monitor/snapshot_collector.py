"""
PRICE SNAPSHOT COLLECTOR
Collects hourly price snapshots for top-volume markets
Builds time-series data for backtesting
"""
import sqlite3
import requests
import time
from datetime import datetime, timezone
from typing import List, Tuple

class SnapshotCollector:
    """Hourly price snapshot collector for high-volume markets"""
    
    CLOB_API = "https://clob.polymarket.com/prices-history"
    DB_PATH = "polymarket_data.db"
    
    # Snapshot settings
    TOP_N_MARKETS = 100  # Track top 100 by volume
    DELAY_BETWEEN_CALLS = 0.5  # Seconds (more aggressive than full scraper)
    MAX_RETRIES = 3
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or self.DB_PATH
    
    def get_top_markets(self, limit: int = 100) -> List[Tuple[str, str]]:
        """Get top N markets by volume (market_id, question)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT market_id, question
            FROM markets
            WHERE active = 1 AND volume > 10000
            ORDER BY volume DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def fetch_current_price(self, market_id: str) -> dict:
        """Fetch current price for a market"""
        url = f"{self.CLOB_API}?market={market_id}&interval=max"
        
        for attempt in range(self.MAX_RETRIES):
            try:
                resp = requests.get(url, timeout=10)
                
                if resp.status_code == 429:
                    wait_time = 2 ** attempt * 30
                    print(f"[WARN] Rate limited on {market_id[:8]}, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                if resp.status_code == 404:
                    return None  # Market not found
                
                resp.raise_for_status()
                data = resp.json()
                
                # Extract latest price
                if data and 'history' in data and data['history']:
                    latest = data['history'][-1]
                    return {
                        'price': latest.get('p', 0.5),
                        'timestamp': latest.get('t'),
                        'volume_24h': data.get('volume_24h', 0)
                    }
                
                return None
            
            except Exception as e:
                if attempt == self.MAX_RETRIES - 1:
                    print(f"[ERROR] Failed to fetch {market_id[:8]}: {e}")
                    return None
                
                time.sleep(2 ** attempt)
        
        return None
    
    def store_snapshot(self, market_id: str, price_data: dict):
        """Store price snapshot in database"""
        if not price_data:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Use provided timestamp or current time
        timestamp = price_data.get('timestamp')
        if timestamp:
            # Convert unix timestamp to ISO
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            timestamp_iso = dt.isoformat()
        else:
            timestamp_iso = datetime.now(timezone.utc).isoformat()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO prices (market_id, timestamp, price, volume_24h)
                VALUES (?, ?, ?, ?)
            """, (
                market_id,
                timestamp_iso,
                price_data['price'],
                price_data.get('volume_24h', 0)
            ))
            
            conn.commit()
        except Exception as e:
            print(f"[WARN] Failed to store snapshot for {market_id[:8]}: {e}")
        finally:
            conn.close()
    
    def run_snapshot_round(self):
        """Run one round of snapshots for top markets"""
        print(f"[SNAPSHOT] Starting round at {datetime.now().strftime('%H:%M:%S')}")
        
        markets = self.get_top_markets(limit=self.TOP_N_MARKETS)
        
        if not markets:
            print("   [INFO] No markets to snapshot")
            return
        
        print(f"   Found {len(markets)} top markets")
        
        success_count = 0
        fail_count = 0
        
        for i, (market_id, question) in enumerate(markets, 1):
            # Progress indicator
            if i % 10 == 0:
                print(f"   Progress: {i}/{len(markets)}")
            
            price_data = self.fetch_current_price(market_id)
            
            if price_data:
                self.store_snapshot(market_id, price_data)
                success_count += 1
            else:
                fail_count += 1
            
            # Rate limit protection
            time.sleep(self.DELAY_BETWEEN_CALLS)
        
        print(f"[COMPLETE] Snapshot round: {success_count} success, {fail_count} failed")
    
    def run_continuous(self, interval_minutes: int = 60):
        """Run snapshots continuously every N minutes"""
        print(f"[START] Continuous snapshots (every {interval_minutes} min)")
        
        while True:
            try:
                self.run_snapshot_round()
                
                print(f"[WAIT] Sleeping {interval_minutes} minutes until next round...")
                time.sleep(interval_minutes * 60)
            
            except KeyboardInterrupt:
                print("\n[STOP] Stopped by user")
                break
            
            except Exception as e:
                print(f"[ERROR] Error in snapshot round: {e}")
                print("   Waiting 5 minutes before retry...")
                time.sleep(300)


def main():
    """Run snapshot collector"""
    import sys
    
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    
    collector = SnapshotCollector()
    
    # Run one round or continuous?
    if len(sys.argv) > 2 and sys.argv[2] == '--once':
        collector.run_snapshot_round()
    else:
        collector.run_continuous(interval_minutes=interval)


if __name__ == "__main__":
    # Run once: python snapshot_collector.py 60 --once
    # Continuous: python snapshot_collector.py 60
    main()
