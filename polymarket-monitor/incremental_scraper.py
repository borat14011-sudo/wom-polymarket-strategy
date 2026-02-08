"""
INCREMENTAL MARKET SCRAPER
Rate-limit-safe batch data collection for Polymarket
Builds dataset over time without overwhelming API
"""
import sqlite3
import requests
import time
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional

class IncrementalScraper:
    """Smart batch scraper with deduplication and rate-limit protection"""
    
    GAMMA_API = "https://gamma-api.polymarket.com/markets"
    DB_PATH = "polymarket_data.db"
    
    # Rate limit protection
    BATCH_SIZE = 500  # Markets per API call
    DELAY_BETWEEN_CALLS = 1.0  # Seconds
    MAX_RETRIES = 3
    
    # Quality filters (focus on tradeable markets)
    MIN_VOLUME = 10000  # $10K minimum
    MAX_DAYS_OUT = 30   # End date within 30 days
    
    # High-signal categories
    FOCUS_CATEGORIES = [
        'Crypto', 'Weather', 'Tech', 'Politics', 'Economy'
    ]
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self.DB_PATH
        self._init_database()
    
    def _init_database(self):
        """Create database schema if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Markets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS markets (
                market_id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                category TEXT,
                created_at TEXT,
                end_date TEXT,
                volume REAL,
                liquidity REAL,
                active INTEGER,
                first_seen TEXT,
                last_updated TEXT
            )
        """)
        
        # Price snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                price REAL NOT NULL,
                volume_24h REAL,
                FOREIGN KEY (market_id) REFERENCES markets(market_id),
                UNIQUE(market_id, timestamp)
            )
        """)
        
        # Resolutions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resolutions (
                market_id TEXT PRIMARY KEY,
                resolved_date TEXT NOT NULL,
                outcome TEXT,
                final_price REAL,
                FOREIGN KEY (market_id) REFERENCES markets(market_id)
            )
        """)
        
        # Create indexes for fast queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_markets_category ON markets(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_markets_volume ON markets(volume)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_markets_active ON markets(active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_market ON prices(market_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON prices(timestamp)")
        
        conn.commit()
        conn.close()
        
        print(f"[OK] Database initialized: {self.db_path}")
    
    def fetch_markets_batch(self, offset: int = 0, limit: int = 500) -> List[Dict]:
        """Fetch one batch of markets from Gamma API with retry logic"""
        params = {
            'offset': offset,
            'limit': limit,
            'active': 'true',
            'closed': 'false'
        }
        
        for attempt in range(self.MAX_RETRIES):
            try:
                resp = requests.get(self.GAMMA_API, params=params, timeout=15)
                
                # Handle rate limit (429)
                if resp.status_code == 429:
                    wait_time = 2 ** attempt * 60  # Exponential backoff
                    print(f"[WARN] Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                resp.raise_for_status()
                return resp.json()
            
            except Exception as e:
                if attempt == self.MAX_RETRIES - 1:
                    print(f"[ERROR] Failed after {self.MAX_RETRIES} attempts: {e}")
                    return []
                
                print(f"[WARN] Attempt {attempt+1} failed: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return []
    
    def normalize_market(self, raw: Dict) -> Dict:
        """Convert API response to our schema"""
        return {
            'market_id': raw.get('id', raw.get('condition_id', 'unknown')),
            'question': raw.get('question', raw.get('title', 'Unknown')),
            'category': raw.get('category', ''),
            'created_at': raw.get('created_at', raw.get('start_date_iso')),
            'end_date': raw.get('end_date_iso'),
            'volume': float(raw.get('volume', 0)),
            'liquidity': float(raw.get('liquidity', 0)),
            'active': 1 if raw.get('active', True) else 0
        }
    
    def should_track(self, market: Dict) -> bool:
        """Filter: Only track high-signal markets"""
        # Volume filter
        if market['volume'] < self.MIN_VOLUME:
            return False
        
        # Category filter (optional - commented out for now to get more data)
        # category = market.get('category', '').lower()
        # if not any(cat.lower() in category for cat in self.FOCUS_CATEGORIES):
        #     return False
        
        # Time horizon filter (optional)
        # if market.get('end_date'):
        #     try:
        #         end_date = datetime.fromisoformat(market['end_date'].replace('Z', '+00:00'))
        #         days_until = (end_date - datetime.now(timezone.utc)).days
        #         if days_until > self.MAX_DAYS_OUT:
        #             return False
        #     except:
        #         pass
        
        return True
    
    def store_markets(self, markets: List[Dict]):
        """Store markets in database with deduplication"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now(timezone.utc).isoformat()
        stored_count = 0
        updated_count = 0
        
        for m in markets:
            normalized = self.normalize_market(m)
            
            # Skip low-signal markets
            if not self.should_track(normalized):
                continue
            
            market_id = normalized['market_id']
            
            # Check if exists
            cursor.execute("SELECT market_id FROM markets WHERE market_id = ?", (market_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing
                cursor.execute("""
                    UPDATE markets SET
                        question = ?,
                        category = ?,
                        volume = ?,
                        liquidity = ?,
                        active = ?,
                        last_updated = ?
                    WHERE market_id = ?
                """, (
                    normalized['question'],
                    normalized['category'],
                    normalized['volume'],
                    normalized['liquidity'],
                    normalized['active'],
                    now,
                    market_id
                ))
                updated_count += 1
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO markets (
                        market_id, question, category, created_at, end_date,
                        volume, liquidity, active, first_seen, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    market_id,
                    normalized['question'],
                    normalized['category'],
                    normalized['created_at'],
                    normalized['end_date'],
                    normalized['volume'],
                    normalized['liquidity'],
                    normalized['active'],
                    now,
                    now
                ))
                stored_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"   [STORED] {stored_count} new, {updated_count} updated")
        return stored_count, updated_count
    
    def run_full_collection(self, max_markets: int = 5000):
        """Collect markets in batches until we hit max or API runs out"""
        total_fetched = 0
        total_stored = 0
        offset = 0
        
        print(f"[START] Full collection (max {max_markets} markets)...")
        
        while total_fetched < max_markets:
            print(f"\n[FETCH] Batch at offset {offset}...")
            
            batch = self.fetch_markets_batch(offset=offset, limit=self.BATCH_SIZE)
            
            if not batch:
                print("   [INFO] No more markets available")
                break
            
            total_fetched += len(batch)
            stored, updated = self.store_markets(batch)
            total_stored += stored
            
            # If we got fewer than batch size, we've reached the end
            if len(batch) < self.BATCH_SIZE:
                print("   [INFO] Reached end of available markets")
                break
            
            offset += self.BATCH_SIZE
            
            # Rate limit protection
            print(f"   [WAIT] Sleeping {self.DELAY_BETWEEN_CALLS}s...")
            time.sleep(self.DELAY_BETWEEN_CALLS)
        
        print(f"\n[COMPLETE] Collection complete!")
        print(f"   Total fetched: {total_fetched}")
        print(f"   Total stored (new): {total_stored}")
        
        self.print_stats()
    
    def print_stats(self):
        """Print database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM markets")
        total_markets = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM markets WHERE active = 1")
        active_markets = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT market_id) FROM prices")
        markets_with_prices = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM prices")
        total_snapshots = cursor.fetchone()[0]
        
        cursor.execute("SELECT category, COUNT(*) FROM markets GROUP BY category ORDER BY COUNT(*) DESC LIMIT 10")
        top_categories = cursor.fetchall()
        
        conn.close()
        
        print(f"\n[STATS] DATABASE STATS")
        print(f"   Total markets: {total_markets}")
        print(f"   Active markets: {active_markets}")
        print(f"   Markets with price data: {markets_with_prices}")
        print(f"   Total price snapshots: {total_snapshots}")
        print(f"\n   Top categories:")
        for cat, count in top_categories:
            print(f"      {cat or 'Unknown'}: {count}")


def main():
    """Run incremental collection"""
    scraper = IncrementalScraper()
    scraper.run_full_collection(max_markets=5000)


if __name__ == "__main__":
    main()
