#!/usr/bin/env python3
"""
Polymarket Historical Data Collector (2025-2026)
Collects price history for all resolved markets from Jan 2025 to Feb 2026
"""

import requests
import sqlite3
import json
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional
import sys

# API Configuration
BASE_URL = "https://gamma-api.polymarket.com"
RATE_LIMIT_DELAY = 0.5  # seconds between requests
MAX_RETRIES = 3

# Date range: Jan 1, 2025 to Feb 28, 2026
START_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2026, 2, 28, 23, 59, 59, tzinfo=timezone.utc)

class PolymarketCollector:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.session = requests.Session()
        self.stats = {
            'markets_found': 0,
            'markets_processed': 0,
            'price_points_collected': 0,
            'errors': [],
            'skipped_markets': []
        }
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Markets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS markets (
                market_id TEXT PRIMARY KEY,
                question TEXT,
                end_date_iso TEXT,
                volume REAL,
                liquidity REAL,
                created_at TEXT,
                resolved_at TEXT,
                outcome TEXT
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_id TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                price REAL NOT NULL,
                volume REAL,
                FOREIGN KEY (market_id) REFERENCES markets(market_id)
            )
        ''')
        
        # Create indexes for efficient querying
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_price_market_time 
            ON price_history(market_id, timestamp)
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Database initialized: {self.db_path}")
    
    def fetch_resolved_markets(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Fetch resolved markets from Gamma API"""
        url = f"{BASE_URL}/markets"
        params = {
            'limit': limit,
            'offset': offset,
            'closed': 'true'  # Only resolved markets
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                time.sleep(RATE_LIMIT_DELAY)
                return response.json()
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    self.stats['errors'].append(f"Failed to fetch markets (offset={offset}): {str(e)}")
                    return []
                time.sleep(2 ** attempt)  # Exponential backoff
        return []
    
    def is_in_date_range(self, market: Dict) -> bool:
        """Check if market resolved within our date range"""
        try:
            # Try different date fields
            end_date_str = market.get('endDate') or market.get('end_date_iso') or market.get('closed_time')
            if not end_date_str:
                return False
            
            # Parse ISO date
            if isinstance(end_date_str, str):
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            else:
                # Unix timestamp
                end_date = datetime.fromtimestamp(int(end_date_str), tz=timezone.utc)
            
            return START_DATE <= end_date <= END_DATE
        except Exception as e:
            return False
    
    def fetch_price_history(self, market_id: str) -> Optional[List[Dict]]:
        """Fetch price history for a specific market"""
        # Try different possible endpoints
        endpoints = [
            f"{BASE_URL}/prices-history",
            f"{BASE_URL}/markets/{market_id}/prices-history",
            f"{BASE_URL}/prices",
        ]
        
        for endpoint in endpoints:
            for attempt in range(MAX_RETRIES):
                try:
                    params = {'market': market_id} if 'prices-history' in endpoint else {}
                    response = self.session.get(endpoint, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        time.sleep(RATE_LIMIT_DELAY)
                        data = response.json()
                        # Handle different response formats
                        if isinstance(data, list):
                            return data
                        elif isinstance(data, dict) and 'history' in data:
                            return data['history']
                        elif isinstance(data, dict) and 'data' in data:
                            return data['data']
                        return []
                    elif response.status_code == 404:
                        break  # Try next endpoint
                    
                    time.sleep(2 ** attempt)
                except Exception as e:
                    if attempt == MAX_RETRIES - 1:
                        continue  # Try next endpoint
                    time.sleep(2 ** attempt)
        
        return None
    
    def store_market(self, market: Dict):
        """Store market metadata in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO markets 
                (market_id, question, end_date_iso, volume, liquidity, created_at, resolved_at, outcome)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                market.get('id') or market.get('condition_id'),
                market.get('question') or market.get('description'),
                market.get('endDate') or market.get('end_date_iso'),
                float(market.get('volume', 0) or 0),
                float(market.get('liquidity', 0) or 0),
                market.get('createdAt') or market.get('created_at'),
                market.get('resolvedAt') or market.get('resolved_at'),
                market.get('outcome')
            ))
            conn.commit()
        finally:
            conn.close()
    
    def store_price_history(self, market_id: str, history: List[Dict]):
        """Store price history in database"""
        if not history:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for point in history:
                # Extract timestamp and price from different possible formats
                timestamp = point.get('t') or point.get('timestamp') or point.get('time')
                price = point.get('p') or point.get('price')
                volume = point.get('v') or point.get('volume')
                
                if timestamp and price is not None:
                    cursor.execute('''
                        INSERT INTO price_history (market_id, timestamp, price, volume)
                        VALUES (?, ?, ?, ?)
                    ''', (market_id, int(timestamp), float(price), float(volume) if volume else None))
            
            conn.commit()
            self.stats['price_points_collected'] += len(history)
        finally:
            conn.close()
    
    def collect_all_data(self):
        """Main collection loop"""
        print("🚀 Starting Polymarket data collection (2025-2026)")
        print(f"📅 Date range: {START_DATE.date()} to {END_DATE.date()}\n")
        
        offset = 0
        limit = 100
        markets_in_range = []
        
        # Step 1: Collect all markets in date range
        print("📊 Phase 1: Discovering resolved markets...")
        while True:
            markets = self.fetch_resolved_markets(limit=limit, offset=offset)
            if not markets:
                break
            
            for market in markets:
                if self.is_in_date_range(market):
                    markets_in_range.append(market)
                    self.stats['markets_found'] += 1
            
            print(f"  Scanned {offset + len(markets)} markets, found {len(markets_in_range)} in range...", end='\r')
            
            if len(markets) < limit:
                break
            
            offset += limit
            
            # Safety limit to avoid infinite loops
            if offset > 10000:
                print("\n⚠️  Reached safety limit of 10,000 markets")
                break
        
        print(f"\n✓ Found {len(markets_in_range)} markets in date range")
        
        # Step 2: Sort by volume (high-volume first)
        markets_in_range.sort(key=lambda m: float(m.get('volume', 0) or 0), reverse=True)
        
        # Step 3: Collect price history
        print(f"\n📈 Phase 2: Collecting price history...")
        for i, market in enumerate(markets_in_range, 1):
            market_id = market.get('id') or market.get('condition_id')
            question = market.get('question', 'Unknown')[:60]
            volume = market.get('volume', 0)
            
            print(f"  [{i}/{len(markets_in_range)}] {question}... (vol: ${volume:,.0f})")
            
            # Store market metadata
            self.store_market(market)
            
            # Fetch and store price history
            history = self.fetch_price_history(market_id)
            if history:
                self.store_price_history(market_id, history)
                print(f"    ✓ Collected {len(history)} price points")
            else:
                self.stats['skipped_markets'].append({
                    'id': market_id,
                    'question': question,
                    'reason': 'No price history available'
                })
                print(f"    ⚠️  No price history found")
            
            self.stats['markets_processed'] += 1
        
        print("\n✅ Collection complete!")
        self.print_stats()
    
    def print_stats(self):
        """Print collection statistics"""
        print("\n" + "="*60)
        print("📊 COLLECTION STATISTICS")
        print("="*60)
        print(f"Markets found in range:     {self.stats['markets_found']}")
        print(f"Markets processed:          {self.stats['markets_processed']}")
        print(f"Price points collected:     {self.stats['price_points_collected']:,}")
        print(f"Markets skipped:            {len(self.stats['skipped_markets'])}")
        print(f"Errors encountered:         {len(self.stats['errors'])}")
        print("="*60)
    
    def generate_quality_report(self, report_path: str):
        """Generate data quality report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Gather statistics
        cursor.execute("SELECT COUNT(*) FROM markets")
        total_markets = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM price_history")
        total_prices = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT m.market_id, m.question, COUNT(ph.id) as price_count
            FROM markets m
            LEFT JOIN price_history ph ON m.market_id = ph.market_id
            GROUP BY m.market_id
            HAVING price_count = 0
        """)
        markets_without_prices = cursor.fetchall()
        
        cursor.execute("""
            SELECT market_id, COUNT(*) as count
            FROM price_history
            GROUP BY market_id
            ORDER BY count ASC
            LIMIT 10
        """)
        sparse_markets = cursor.fetchall()
        
        conn.close()
        
        # Write report
        with open(report_path, 'w') as f:
            f.write("# Data Quality Report: Polymarket Historical Prices (2025-2026)\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Markets:** {total_markets}\n")
            f.write(f"- **Total Price Points:** {total_prices:,}\n")
            f.write(f"- **Average Price Points per Market:** {total_prices/total_markets if total_markets > 0 else 0:.1f}\n")
            f.write(f"- **Markets Without Price Data:** {len(markets_without_prices)}\n\n")
            
            f.write("## Data Gaps\n\n")
            if markets_without_prices:
                f.write("### Markets Missing Price History\n\n")
                for market_id, question, _ in markets_without_prices[:20]:
                    f.write(f"- `{market_id}`: {question}\n")
                if len(markets_without_prices) > 20:
                    f.write(f"\n*... and {len(markets_without_prices) - 20} more*\n")
            else:
                f.write("✅ All markets have price history data.\n")
            
            f.write("\n### Markets with Sparse Data (<50 points)\n\n")
            for market_id, count in sparse_markets:
                f.write(f"- `{market_id}`: {count} price points\n")
            
            if self.stats['errors']:
                f.write("\n## Errors Encountered\n\n")
                for error in self.stats['errors']:
                    f.write(f"- {error}\n")
            
            if self.stats['skipped_markets']:
                f.write("\n## Skipped Markets\n\n")
                for skip in self.stats['skipped_markets'][:50]:
                    f.write(f"- `{skip['id']}`: {skip['question']} - {skip['reason']}\n")
                if len(self.stats['skipped_markets']) > 50:
                    f.write(f"\n*... and {len(self.stats['skipped_markets']) - 50} more*\n")
            
            f.write("\n## Notes\n\n")
            f.write("- Data source: Polymarket Gamma API\n")
            f.write("- Only resolved markets included\n")
            f.write("- Markets sorted by volume (high to low) during collection\n")
            f.write("- Rate limiting: 0.5s delay between requests\n")
        
        print(f"✓ Quality report generated: {report_path}")


if __name__ == "__main__":
    db_path = "historical_2025_2026.db"
    report_path = "DATA_QUALITY_2025_2026.md"
    
    collector = PolymarketCollector(db_path)
    
    try:
        collector.collect_all_data()
        collector.generate_quality_report(report_path)
        
        print(f"\n✅ SUCCESS!")
        print(f"   Database: {db_path}")
        print(f"   Report:   {report_path}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Collection interrupted by user")
        collector.generate_quality_report(report_path)
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
