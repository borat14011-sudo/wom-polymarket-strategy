"""Quick script to inspect existing data"""
import json
import os

# Check backtest dataset
print("[BACKTEST DATASET]")
with open('backtest_dataset_v1.json', 'r') as f:
    data = json.load(f)
    print(f"Keys: {list(data.keys())}")
    if 'markets' in data:
        print(f"Total markets: {len(data['markets'])}")
        if data['markets']:
            print(f"Sample market keys: {list(data['markets'][0].keys())}")
            print(f"Sample market: {data['markets'][0]['question'][:100]}")

print("\n[EVENTS RAW]")
# Check file size only (too big to load)
size = os.path.getsize('events_raw.json')
print(f"File size: {size / 1024 / 1024 / 1024:.2f} GB")

print("\n[POLYMARKET COMPLETE]")
size = os.path.getsize('polymarket_complete.json')
print(f"File size: {size / 1024 / 1024:.2f} MB")

# Try to load first line
with open('polymarket_complete.json', 'r') as f:
    first_line = f.readline()[:200]
    print(f"First line: {first_line}")
