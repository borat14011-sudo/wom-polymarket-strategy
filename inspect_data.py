#!/usr/bin/env python3
import json

print("Loading dataset...")
with open('polymarket-monitor/historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
    data = json.load(f)

markets = data if isinstance(data, list) else data.get('markets', [])

print(f"Total markets: {len(markets):,}")
print(f"\nFirst market structure:")
if markets:
    first = markets[0]
    print(json.dumps(first, indent=2)[:2000])  # First 2000 chars
    print("\n\nAvailable keys:")
    print(list(first.keys()))
