#!/usr/bin/env python3
import json
from pathlib import Path

data_file = Path("historical-data-scraper/data/backtest_dataset_v2.json")
with open(data_file) as f:
    data = json.load(f)

print(f"Markets with price data: {len(data):,}")
if data:
    print(f"\nSample market:")
    print(f"  Question: {data[0]['question'][:80]}")
    print(f"  Volume: ${data[0]['volume']:,.0f}")
    print(f"  Price points: {len(data[0]['price_history'])}")
