"""
LIVE POLYMARKET BATCH MONITOR
Fetches active markets and processes in batches following ROOT DIRECTIVE
"""
import json
import time
import requests
from datetime import datetime
from typing import List, Dict
from batch_signal_processor import BatchSignalProcessor

class LiveBatchMonitor:
    """Monitors Polymarket and processes markets in high-throughput batches"""
    
    GAMMA_API = "https://gamma-api.polymarket.com/markets"
    CLOB_API = "https://clob.polymarket.com/prices-history"
    
    def __init__(self, batch_size=100, check_interval=300):
        """
        Args:
            batch_size: Markets to process per batch (50-300 recommended)
            check_interval: Seconds between market checks (default 5min)
        """
        self.processor = BatchSignalProcessor()
        self.batch_size = batch_size
        self.check_interval = check_interval
        self.seen_markets = set()
        self.signals_log = []
    
    def fetch_active_markets(self, limit=200) -> List[Dict]:
        """Fetch active markets from Polymarket Gamma API"""
        try:
            params = {
                'limit': limit,
                'active': 'true',
                'closed': 'false'
            }
            
            resp = requests.get(self.GAMMA_API, params=params, timeout=10)
            resp.raise_for_status()
            
            markets_raw = resp.json()
            
            # Normalize to our format
            markets = []
            for m in markets_raw:
                markets.append({
                    'market_id': m.get('id', m.get('condition_id', 'unknown')),
                    'question': m.get('question', m.get('title', 'Unknown')),
                    'category': m.get('category', ''),
                    'end_date': m.get('end_date_iso'),
                    'volume': m.get('volume', 0),
                    'liquidity': m.get('liquidity', 0)
                })
            
            return markets
        
        except Exception as e:
            print(f"⚠️ API Error: {e}")
            return []
    
    def fetch_current_prices(self, market_ids: List[str]) -> Dict[str, float]:
        """Fetch current prices for markets (for signal generation)"""
        prices = {}
        
        for mid in market_ids[:50]:  # Limit to avoid rate limits
            try:
                url = f"{self.CLOB_API}?market={mid}&interval=max"
                resp = requests.get(url, timeout=5)
                
                if resp.ok:
                    data = resp.json()
                    if data and 'history' in data and data['history']:
                        latest = data['history'][-1]
                        prices[mid] = latest.get('p', 0.5)
                
                time.sleep(0.1)  # Rate limit protection
            
            except:
                prices[mid] = 0.5  # Default if fetch fails
        
        return prices
    
    def run_single_batch(self) -> Dict:
        """Fetch and process one batch of markets"""
        print(f"🔍 Fetching active markets...")
        
        markets = self.fetch_active_markets(limit=self.batch_size)
        
        if not markets:
            return {"status": "no_markets", "timestamp": datetime.utcnow().isoformat()}
        
        # Filter out previously seen markets (for NEW signals only)
        new_markets = [m for m in markets if m['market_id'] not in self.seen_markets]
        
        if not new_markets:
            print("   No new markets since last check")
            return {"status": "no_new_markets", "checked": len(markets)}
        
        print(f"   Found {len(new_markets)} new markets")
        
        # Update seen set
        for m in new_markets:
            self.seen_markets.add(m['market_id'])
        
        # Process batch
        print(f"⚙️ Processing batch ({len(new_markets)} markets)...")
        result = self.processor.process_batch(new_markets)
        
        # Enrich with timestamp
        result['batch_timestamp'] = datetime.utcnow().isoformat() + "Z"
        result['markets_processed'] = len(new_markets)
        
        # Log signals
        if result.get('review_queue'):
            self.signals_log.append({
                'timestamp': result['batch_timestamp'],
                'signals': len(result['review_queue']),
                'top_priority': result['review_queue'][0] if result['review_queue'] else None
            })
        
        return result
    
    def run_continuous(self, max_batches=None):
        """Run continuous monitoring loop"""
        batch_count = 0
        
        print(f"🚀 Starting continuous monitor (batch_size={self.batch_size}, interval={self.check_interval}s)")
        
        while True:
            try:
                batch_count += 1
                print(f"\n{'='*60}")
                print(f"BATCH #{batch_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print('='*60)
                
                result = self.run_single_batch()
                
                # Display summary
                if result.get('review_queue'):
                    print(f"\n✅ Signals Generated: {len(result['review_queue'])}")
                    
                    # Show top 3 signals
                    for i, sig in enumerate(result['review_queue'][:3], 1):
                        print(f"   {i}. {sig.get('analysis_question', 'Unknown')} (priority={sig.get('priority', 0):.2f})")
                
                # Save to file
                output_file = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Saved to: {output_file}")
                
                # Check if should stop
                if max_batches and batch_count >= max_batches:
                    print(f"\n🛑 Reached max_batches={max_batches}, stopping")
                    break
                
                # Wait before next batch
                print(f"\n⏳ Sleeping {self.check_interval}s until next batch...")
                time.sleep(self.check_interval)
            
            except KeyboardInterrupt:
                print("\n\n⚠️ Stopped by user")
                break
            
            except Exception as e:
                print(f"\n❌ Error in batch: {e}")
                time.sleep(60)  # Wait 1 min on error


def main():
    """Run live monitor"""
    import sys
    
    # Parse args
    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    max_batches = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    monitor = LiveBatchMonitor(batch_size=batch_size, check_interval=interval)
    monitor.run_continuous(max_batches=max_batches)


if __name__ == "__main__":
    # Quick test: python live_batch_monitor.py 50 60 2
    # (50 markets, 60s interval, 2 batches)
    main()
