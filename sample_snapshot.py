import json
import sys

# read first 1000 lines to find first market entry
with open('markets_snapshot_20260207_221914.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

print("Keys:", data.keys())
if 'markets' in data:
    markets = data['markets']
    print(f"Number of markets: {len(markets)}")
    if len(markets) > 0:
        print("First market keys:", markets[0].keys())
        print("First market:", json.dumps(markets[0], indent=2))
else:
    # maybe the root is an array?
    print("Root type:", type(data))
    if isinstance(data, list):
        print("First item keys:", data[0].keys())
        print("First item:", json.dumps(data[0], indent=2))