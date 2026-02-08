#!/usr/bin/env python3
"""
Build backtest dataset from latest checkpoint
"""
import json
from pathlib import Path

DATA_DIR = Path("historical-data-scraper/data")

print("Loading latest checkpoint...")
checkpoint_files = sorted(DATA_DIR.glob("prices_checkpoint_*.json"), key=lambda x: x.stat().st_mtime)
# Use second-to-last to avoid incomplete file
latest = checkpoint_files[-2] if len(checkpoint_files) > 1 else checkpoint_files[-1]
print(f"Using: {latest.name} ({latest.stat().st_size / 1024 / 1024:.1f} MB)")

with open(latest) as f:
    prices_data = json.load(f)

print(f"Loaded {len(prices_data):,} tokens")

# Index by token_id
prices_index = {p['token_id']: p.get('prices', []) for p in prices_data if p.get('success')}

print(f"Success: {len(prices_index):,} tokens with price data")

# Load events
print("Loading events...")
with open(DATA_DIR / 'polymarket_complete.json') as f:
    events = json.load(f)

print(f"Loaded {len(events):,} events")

# Build dataset
print("Building backtest dataset...")
dataset = []

for event in events:
    volume = event.get('volume')
    if not volume or volume < 100000:
        continue
    
    for market in event.get('markets', []):
        token_ids = market.get('clob_token_ids', '[]')
        if isinstance(token_ids, str):
            try:
                token_ids = json.loads(token_ids)
            except:
                continue
        
        if token_ids and token_ids[0] in prices_index:
            prices = prices_index[token_ids[0]]
            if len(prices) > 10:
                dataset.append({
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

print(f"\n[OK] Dataset ready!")
print(f"Markets with prices: {len(dataset):,}")

# Save
output = DATA_DIR / "backtest_dataset_v1.json"
with open(output, 'w') as f:
    json.dump(dataset, f)

print(f"Saved: {output}")
print(f"Size: {output.stat().st_size / 1024 / 1024:.1f} MB")
