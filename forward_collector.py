"""
Polymarket Forward Collector
Continuous data collection system for building historical dataset
Runs 4x per day (00:00, 06:00, 12:00, 18:00 UTC)
"""
import sys
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import requests
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

class ForwardCollector:
    """Collects market snapshots at regular intervals"""
    
    def __init__(self, data_dir: str = "historical_data"):
        self.base_url = "https://gamma-api.polymarket.com"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def fetch_active_markets(self) -> List[Dict]:
        """Fetch all active markets"""
        markets = []
        offset = 0
        limit = 100
        
        print(f"Fetching active markets...", end='', flush=True)
        
        while True:
            try:
                response = requests.get(
                    f"{self.base_url}/markets",
                    params={
                        "active": "true",
                        "limit": limit,
                        "offset": offset
                    },
                    timeout=30
                )
                
                if response.status_code != 200:
                    break
                
                batch = response.json()
                if not batch:
                    break
                
                markets.extend(batch)
                
                if len(batch) < limit:
                    break
                
                offset += limit
                
            except Exception as e:
                print(f" Error: {e}")
                break
        
        print(f" {len(markets)} markets")
        return markets
    
    def collect_snapshot(self) -> Dict:
        """Collect one snapshot of all active markets"""
        timestamp = datetime.now(timezone.utc)
        print(f"\n{'='*70}")
        print(f"Collecting snapshot: {timestamp.isoformat()}")
        print(f"{'='*70}")
        
        # Fetch markets
        markets = self.fetch_active_markets()
        
        # Extract relevant fields for time series
        snapshot = []
        for market in markets:
            # Parse outcome prices
            try:
                outcome_prices_raw = market.get('outcomePrices', '[]')
                outcome_prices = json.loads(outcome_prices_raw) if isinstance(outcome_prices_raw, str) else outcome_prices_raw
                outcome_prices = [float(p) for p in outcome_prices]
            except:
                outcome_prices = []
            
            # Parse outcomes
            try:
                outcomes_raw = market.get('outcomes', '[]')
                outcomes = json.loads(outcomes_raw) if isinstance(outcomes_raw, str) else outcomes_raw
            except:
                outcomes = []
            
            snapshot.append({
                'id': market.get('id'),
                'question': market.get('question', ''),
                'category': market.get('category'),
                'end_date': market.get('endDate'),
                
                # Core price data (what we need for strategies)
                'outcomes': outcomes,
                'prices': outcome_prices,
                'last_trade_price': float(market.get('lastTradePrice', 0)),
                
                # Metrics
                'volume': float(market.get('volumeNum', 0)),
                'volume_24hr': float(market.get('volume24hr', 0)),
                'liquidity': float(market.get('liquidityNum', 0)),
                
                # Changes (for tracking momentum)
                'price_change_1h': float(market.get('oneHourPriceChange', 0)),
                'price_change_24h': float(market.get('oneDayPriceChange', 0)),
            })
        
        print(f"Collected {len(snapshot)} active markets")
        
        return {
            'timestamp': timestamp.isoformat(),
            'timestamp_unix': int(timestamp.timestamp()),
            'market_count': len(snapshot),
            'markets': snapshot
        }
    
    def save_snapshot(self, snapshot: Dict):
        """Save snapshot to daily file (append mode)"""
        timestamp = datetime.fromisoformat(snapshot['timestamp'])
        
        # Organize by year/month/day
        year_dir = self.data_dir / str(timestamp.year)
        month_dir = year_dir / f"{timestamp.month:02d}"
        month_dir.mkdir(parents=True, exist_ok=True)
        
        # Daily file (JSONL format for easy appending)
        daily_file = month_dir / f"{timestamp.day:02d}.jsonl"
        
        # Append snapshot
        with open(daily_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(snapshot) + '\n')
        
        print(f"✓ Saved to: {daily_file}")
        
        # Also save to latest snapshot for quick access
        latest_file = self.data_dir / "latest_snapshot.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2)
        
        print(f"✓ Updated: {latest_file}")
    
    def run_collection(self):
        """Run one collection cycle"""
        try:
            snapshot = self.collect_snapshot()
            self.save_snapshot(snapshot)
            
            print(f"\n{'='*70}")
            print("Collection complete!")
            print(f"{'='*70}\n")
            
            return snapshot
            
        except Exception as e:
            print(f"\n[ERROR] Collection failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Log error
            error_log = self.data_dir / "errors.log"
            with open(error_log, 'a') as f:
                f.write(f"{datetime.now(timezone.utc).isoformat()} - {e}\n")
                traceback.print_exc(file=f)
                f.write("\n")
            
            return None
    
    def get_historical_data(self, market_id: str) -> List[Dict]:
        """Retrieve all snapshots for a specific market"""
        snapshots = []
        
        # Walk through all daily files
        for year_dir in sorted(self.data_dir.glob("*")):
            if not year_dir.is_dir() or not year_dir.name.isdigit():
                continue
            
            for month_dir in sorted(year_dir.glob("*")):
                if not month_dir.is_dir():
                    continue
                
                for daily_file in sorted(month_dir.glob("*.jsonl")):
                    with open(daily_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            snapshot = json.loads(line)
                            for market in snapshot['markets']:
                                if market['id'] == market_id:
                                    snapshots.append({
                                        'timestamp': snapshot['timestamp'],
                                        **market
                                    })
        
        return snapshots
    
    def generate_summary(self) -> Dict:
        """Generate summary statistics of collected data"""
        total_snapshots = 0
        date_range = []
        total_markets = set()
        
        for year_dir in sorted(self.data_dir.glob("*")):
            if not year_dir.is_dir() or not year_dir.name.isdigit():
                continue
            
            for month_dir in sorted(year_dir.glob("*")):
                if not month_dir.is_dir():
                    continue
                
                for daily_file in sorted(month_dir.glob("*.jsonl")):
                    with open(daily_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            snapshot = json.loads(line)
                            total_snapshots += 1
                            date_range.append(snapshot['timestamp'])
                            
                            for market in snapshot['markets']:
                                total_markets.add(market['id'])
        
        return {
            'total_snapshots': total_snapshots,
            'unique_markets_tracked': len(total_markets),
            'date_range': {
                'start': min(date_range) if date_range else None,
                'end': max(date_range) if date_range else None
            },
            'expected_daily_snapshots': 4,
            'coverage_days': total_snapshots / 4 if total_snapshots > 0 else 0
        }

# Cron job setup instructions
CRON_SETUP = """
# ============================================================================
# CRON SETUP INSTRUCTIONS
# ============================================================================

For Linux/Mac:
--------------
1. Edit crontab:
   crontab -e

2. Add these lines (runs 4x per day at 00:00, 06:00, 12:00, 18:00 UTC):
   
   0 0,6,12,18 * * * cd /path/to/workspace && /path/to/python forward_collector.py >> cron.log 2>&1

3. Make sure Python path is correct:
   which python3

For Windows (Task Scheduler):
------------------------------
1. Open Task Scheduler
2. Create Basic Task: "Polymarket Forward Collector"
3. Trigger: Daily at 00:00
4. Action: Start a program
   Program: C:\\Path\\To\\Python\\python.exe
   Arguments: C:\\Path\\To\\forward_collector.py
5. In "Settings" tab:
   - Check "Run task as soon as possible after a scheduled start is missed"
   - Check "If the task fails, restart every: 10 minutes"
6. Create 3 more identical tasks for 06:00, 12:00, and 18:00

Alternative (Python Scheduler):
--------------------------------
Use the provided scheduler_daemon.py which runs continuously

For Docker:
-----------
See docker-compose.yml for containerized deployment

# ============================================================================
"""

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Polymarket Forward Collector")
    parser.add_argument('--data-dir', default='historical_data', help='Data directory')
    parser.add_argument('--summary', action='store_true', help='Show collection summary')
    parser.add_argument('--market-history', type=str, help='Get history for specific market ID')
    
    args = parser.parse_args()
    
    collector = ForwardCollector(data_dir=args.data_dir)
    
    if args.summary:
        summary = collector.generate_summary()
        print("\n" + "="*70)
        print("COLLECTION SUMMARY")
        print("="*70)
        print(json.dumps(summary, indent=2))
        print()
    elif args.market_history:
        history = collector.get_historical_data(args.market_history)
        print(f"\nHistory for market {args.market_history}:")
        print(f"Found {len(history)} snapshots")
        if history:
            for snapshot in history[:5]:
                print(f"  {snapshot['timestamp']}: {snapshot['prices']}")
            if len(history) > 5:
                print(f"  ... ({len(history) - 5} more)")
    else:
        # Run collection
        print(CRON_SETUP)
        snapshot = collector.run_collection()
        
        if snapshot:
            # Show quick summary
            summary = collector.generate_summary()
            print(f"\nTotal snapshots collected so far: {summary['total_snapshots']}")
            print(f"Coverage: {summary['coverage_days']:.1f} days")
