#!/usr/bin/env python3
import json

# Check complete data file
with open('historical-data-scraper/data/polymarket_complete.json', 'r') as f:
    data = json.load(f)

print(f"✓ Total events: {len(data):,}")
print(f"✓ First event: {data[0]['question'][:60]}...")
print(f"✓ Last event: {data[-1]['question'][:60]}...")
print(f"✓ Sample market ID: {data[0].get('id', 'N/A')}")
print(f"\n📊 Data fields in each event:")
for key in list(data[0].keys())[:10]:
    print(f"  - {key}")
