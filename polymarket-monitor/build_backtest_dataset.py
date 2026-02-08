#!/usr/bin/env python3
"""
Build backtest dataset from checkpoint 40K (no more API calls needed)
"""
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("historical-data-scraper/data")
MIN_VOLUME = 100000

print(f"\n{'='*70}")
print(f"BUILDING BACKTEST DATASET FROM CHECKPOINT 40K")
print(f"No API calls - 100% local processing")
print(f"{'='*70}\n")

# Load checkpoint
print("Loading checkpoint 40K...")
with open(DATA_DIR / "prices_checkpoint_40000.json") as f:
    prices_data = json.load(f)
print(f"[OK] Loaded {len(prices_data):,} price results")

# Index by token_id
print("Indexing prices by token_id...")
prices_index = {}
for p in prices_data:
    if p.get('success') and p.get('prices'):
        prices_index[p['token_id']] = p['prices']
print(f"[OK] {len(prices_index):,} tokens with price data")

# Load events
print("\nLoading event data...")
with open(DATA_DIR / "polymarket_complete.json") as f:
    events_data = json.load(f)
print(f"[OK] Loaded {len(events_data):,} events")

# Build combined dataset
print(f"\nBuilding combined dataset (min volume: ${MIN_VOLUME:,})...")
backtest_data = []
markets_processed = 0
markets_skipped_volume = 0
markets_skipped_no_prices = 0

for event in events_data:
    volume = event.get('volume')
    if not volume or volume < MIN_VOLUME:
        markets_skipped_volume += len(event.get('markets', []))
        continue
    
    for market in event.get('markets', []):
        markets_processed += 1
        
        token_ids = market.get('clob_token_ids', '[]')
        if isinstance(token_ids, str):
            try:
                token_ids = json.loads(token_ids)
            except:
                markets_skipped_no_prices += 1
                continue
        
        # Get price history for first token (YES side typically)
        if token_ids and token_ids[0] in prices_index:
            prices = prices_index[token_ids[0]]
            
            if len(prices) > 10:  # Need meaningful history
                backtest_data.append({
                    'event_id': event.get('event_id'),
                    'market_id': market.get('market_id'),
                    'question': market.get('question'),
                    'volume': volume,
                    'start_date': event.get('start_date'),
                    'end_date': event.get('end_date'),
                    'closed': event.get('closed'),
                    'outcome': market.get('outcome'),
                    'price_history': prices,
                    'token_id': token_ids[0]
                })
        else:
            markets_skipped_no_prices += 1

# Save dataset
output_file = DATA_DIR / "backtest_dataset_v2.json"
print(f"\nSaving dataset...")
with open(output_file, 'w') as f:
    json.dump(backtest_data, f)

# Stats
print(f"\n{'='*70}")
print(f"DATASET COMPLETE")
print(f"{'='*70}")
print(f"Markets with price data: {len(backtest_data):,}")
print(f"Markets skipped (low volume): {markets_skipped_volume:,}")
print(f"Markets skipped (no prices): {markets_skipped_no_prices:,}")
print(f"Output: {output_file}")
print(f"Size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
print(f"{'='*70}\n")

# Sample stats
if backtest_data:
    avg_price_points = sum(len(d['price_history']) for d in backtest_data) / len(backtest_data)
    total_volume = sum(d['volume'] for d in backtest_data)
    
    print(f"DATASET STATS:")
    print(f"  Avg price points per market: {avg_price_points:.0f}")
    print(f"  Total volume: ${total_volume:,.0f}")
    print(f"  Date range: {min(d['start_date'] for d in backtest_data if d.get('start_date'))}")
    print(f"              to {max(d['end_date'] for d in backtest_data if d.get('end_date'))}")
    print()
