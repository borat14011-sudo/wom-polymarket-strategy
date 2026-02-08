"""
Polymarket Snapshot Collector
Collects current state of all markets for baseline dataset
"""
import sys
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import requests
import json
import time
from datetime import datetime, timezone
from collections import defaultdict
from typing import List, Dict

class PolymarketSnapshotCollector:
    """Collects comprehensive snapshot of all Polymarket markets"""
    
    def __init__(self, min_volume: float = 100, target_year: int = 2024):
        self.base_url = "https://gamma-api.polymarket.com"
        self.min_volume = min_volume
        self.target_year = target_year
        self.markets = []
        self.stats = defaultdict(int)
        
    def fetch_markets_paginated(self, closed: bool = None, limit_pages: int = None) -> List[Dict]:
        """Fetch all markets with pagination"""
        all_markets = []
        offset = 0
        limit = 100
        page = 0
        
        status_filter = "closed" if closed else "active" if closed is False else "all"
        print(f"\nFetching {status_filter} markets...")
        
        while True:
            page += 1
            if limit_pages and page > limit_pages:
                break
                
            params = {
                "limit": limit,
                "offset": offset
            }
            
            if closed is not None:
                params["closed"] = "true" if closed else "false"
            
            try:
                response = requests.get(
                    f"{self.base_url}/markets",
                    params=params,
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"  Error on page {page}: HTTP {response.status_code}")
                    break
                
                markets = response.json()
                
                if not markets or len(markets) == 0:
                    break
                
                all_markets.extend(markets)
                print(f"  Page {page:3d}: {len(markets):3d} markets (total: {len(all_markets):5d})", end='\r', flush=True)
                
                if len(markets) < limit:
                    break
                
                offset += limit
                time.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                print(f"\n  Error on page {page}: {e}")
                break
        
        print(f"\n  Total {status_filter} markets fetched: {len(all_markets)}")
        return all_markets
    
    def filter_and_enrich_market(self, market: Dict) -> Dict:
        """Filter and enrich a single market"""
        # Parse dates
        created = market.get('createdAt', '')
        end_date = market.get('endDate', '')
        
        # Check volume threshold
        volume = float(market.get('volumeNum', 0))
        if volume < self.min_volume:
            self.stats['filtered_low_volume'] += 1
            return None
        
        # Check year filter (optional)
        if self.target_year and created:
            try:
                year = int(created[:4])
                if year < self.target_year:
                    self.stats['filtered_old_year'] += 1
                    return None
            except:
                pass
        
        # Extract outcome prices
        outcome_prices_raw = market.get('outcomePrices', '[]')
        try:
            outcome_prices = json.loads(outcome_prices_raw) if isinstance(outcome_prices_raw, str) else outcome_prices_raw
            outcome_prices = [float(p) for p in outcome_prices]
        except:
            outcome_prices = []
        
        # Extract outcomes
        outcomes_raw = market.get('outcomes', '[]')
        try:
            outcomes = json.loads(outcomes_raw) if isinstance(outcomes_raw, str) else outcomes_raw
        except:
            outcomes = []
        
        # Build enriched market data
        enriched = {
            'id': market.get('id'),
            'question': market.get('question', ''),
            'slug': market.get('slug', ''),
            'category': market.get('category'),
            'created_at': created,
            'end_date': end_date,
            'closed': market.get('closed', False),
            
            # Volume metrics
            'volume': volume,
            'volume_24hr': float(market.get('volume24hr', 0)),
            
            # Current prices
            'outcomes': outcomes,
            'outcome_prices': outcome_prices,
            'last_trade_price': float(market.get('lastTradePrice', 0)),
            
            # Price changes
            'price_change_1h': float(market.get('oneHourPriceChange', 0)),
            'price_change_24h': float(market.get('oneDayPriceChange', 0)),
            'price_change_7d': float(market.get('oneWeekPriceChange', 0)),
            
            # Market identifiers
            'condition_id': market.get('conditionId'),
            'clob_token_ids': market.get('clobTokenIds', '[]'),
            
            # Resolution (for closed markets)
            'outcome_winner': market.get('winner'),
        }
        
        self.stats['total_processed'] += 1
        if enriched['closed']:
            self.stats['closed_markets'] += 1
        else:
            self.stats['active_markets'] += 1
        
        # Track by category
        category = enriched['category'] or 'uncategorized'
        self.stats[f'category_{category}'] += 1
        
        return enriched
    
    def collect_all(self, limit_pages: int = None):
        """Main collection method"""
        print("="*70)
        print("POLYMARKET SNAPSHOT COLLECTOR")
        print("="*70)
        print(f"Start time: {datetime.now(timezone.utc).isoformat()}")
        print(f"Filters: volume >= ${self.min_volume:,.0f}, year >= {self.target_year}")
        
        start_time = time.time()
        
        # Fetch all markets (closed and active)
        print("\n[1/3] Fetching markets from API...")
        raw_markets = []
        
        # Get closed markets
        closed = self.fetch_markets_paginated(closed=True, limit_pages=limit_pages)
        raw_markets.extend(closed)
        
        # Get active markets
        active = self.fetch_markets_paginated(closed=False, limit_pages=limit_pages)
        raw_markets.extend(active)
        
        print(f"\nTotal raw markets: {len(raw_markets)}")
        
        # Process and filter
        print("\n[2/3] Processing and filtering markets...")
        for i, market in enumerate(raw_markets, 1):
            if i % 1000 == 0:
                print(f"  Processed {i}/{len(raw_markets)}...", end='\r', flush=True)
            
            enriched = self.filter_and_enrich_market(market)
            if enriched:
                self.markets.append(enriched)
        
        print(f"  Processed {len(raw_markets)}/{len(raw_markets)}    ")
        
        # Generate statistics
        print("\n[3/3] Generating statistics...")
        self.generate_stats()
        
        elapsed = time.time() - start_time
        print(f"\nCollection complete in {elapsed:.1f} seconds")
        
        return self.markets
    
    def generate_stats(self):
        """Generate summary statistics"""
        # Category breakdown
        categories = defaultdict(lambda: {'count': 0, 'volume': 0})
        total_volume = 0
        
        for market in self.markets:
            cat = market['category'] or 'uncategorized'
            categories[cat]['count'] += 1
            categories[cat]['volume'] += market['volume']
            total_volume += market['volume']
        
        # Sort by volume
        sorted_categories = sorted(
            categories.items(),
            key=lambda x: x[1]['volume'],
            reverse=True
        )
        
        # Volume distribution
        volume_buckets = {
            '< $1K': 0,
            '$1K - $10K': 0,
            '$10K - $100K': 0,
            '$100K - $1M': 0,
            '> $1M': 0
        }
        
        for market in self.markets:
            vol = market['volume']
            if vol < 1000:
                volume_buckets['< $1K'] += 1
            elif vol < 10000:
                volume_buckets['$1K - $10K'] += 1
            elif vol < 100000:
                volume_buckets['$10K - $100K'] += 1
            elif vol < 1000000:
                volume_buckets['$100K - $1M'] += 1
            else:
                volume_buckets['> $1M'] += 1
        
        self.summary = {
            'total_markets': len(self.markets),
            'active_markets': self.stats['active_markets'],
            'closed_markets': self.stats['closed_markets'],
            'total_volume': total_volume,
            'categories': dict(sorted_categories),
            'volume_distribution': volume_buckets,
            'collection_timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def save(self, base_filename: str = "markets_snapshot"):
        """Save collected data"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        # Save full dataset
        json_file = f"{base_filename}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'collection_time': self.summary['collection_timestamp'],
                    'min_volume_filter': self.min_volume,
                    'target_year': self.target_year,
                    'total_markets': len(self.markets)
                },
                'summary': self.summary,
                'markets': self.markets
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved dataset: {json_file} ({len(self.markets)} markets)")
        
        # Save summary report
        report_file = f"snapshot_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("POLYMARKET SNAPSHOT REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Collection Time: {self.summary['collection_timestamp']}\n")
            f.write(f"Total Markets: {len(self.markets):,}\n")
            f.write(f"Active Markets: {self.stats['active_markets']:,}\n")
            f.write(f"Closed Markets: {self.stats['closed_markets']:,}\n")
            f.write(f"Total Volume: ${self.summary['total_volume']:,.2f}\n\n")
            
            f.write("TOP CATEGORIES BY VOLUME:\n")
            f.write("-"*70 + "\n")
            for i, (cat, data) in enumerate(list(self.summary['categories'].items())[:10], 1):
                pct = (data['volume'] / self.summary['total_volume']) * 100
                f.write(f"{i:2d}. {cat:30s}: {data['count']:5d} markets, ${data['volume']:15,.0f} ({pct:5.1f}%)\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("VOLUME DISTRIBUTION:\n")
            f.write("-"*70 + "\n")
            for bucket, count in self.summary['volume_distribution'].items():
                pct = (count / len(self.markets)) * 100
                f.write(f"{bucket:20s}: {count:5d} markets ({pct:5.1f}%)\n")
        
        print(f"✓ Saved report: {report_file}")
        
        return json_file, report_file

if __name__ == "__main__":
    collector = PolymarketSnapshotCollector(
        min_volume=100,  # $100 minimum
        target_year=2024  # Feb 2024+
    )
    
    # Collect (limit to first 50 pages for testing, remove limit for full collection)
    markets = collector.collect_all(limit_pages=None)  # Set to None for full collection
    
    # Save
    json_file, report_file = collector.save()
    
    print("\n" + "="*70)
    print("COLLECTION COMPLETE!")
    print("="*70)
    print(f"Markets collected: {len(markets):,}")
    print(f"Output files:")
    print(f"  - {json_file}")
    print(f"  - {report_file}")
