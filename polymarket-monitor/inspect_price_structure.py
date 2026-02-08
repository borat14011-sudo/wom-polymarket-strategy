"""Quick check of price data structure"""
import json

with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
    markets = json.load(f)

print(f"Total markets: {len(markets)}")
print(f"\nSample market structure:")

sample = markets[0]
print(f"Keys: {list(sample.keys())}")

print(f"\nQuestion: {sample.get('question')}")
print(f"Outcome: {sample.get('outcome')}")

# Check price_history field
ph = sample.get('price_history', [])
print(f"\nPrice history type: {type(ph)}")
print(f"Price history length: {len(ph) if isinstance(ph, list) else 'N/A'}")

if isinstance(ph, list) and ph:
    print(f"First price entry: {ph[0]}")
    print(f"Last price entry: {ph[-1]}")

# Find a market with non-empty prices
for i, m in enumerate(markets[:100]):
    ph = m.get('price_history', [])
    if isinstance(ph, list) and len(ph) > 0:
        print(f"\nFound market with prices at index {i}:")
        print(f"Question: {m.get('question')[:80]}")
        print(f"Price history length: {len(ph)}")
        print(f"First entry: {ph[0]}")
        print(f"Type of first entry: {type(ph[0])}")
        
        if isinstance(ph[0], dict):
            print(f"Dict keys: {list(ph[0].keys())}")
        break
