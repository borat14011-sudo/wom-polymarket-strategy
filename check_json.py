import json

with open('polymarket_latest.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Type: {type(data)}")
if isinstance(data, list):
    print(f"Length: {len(data)}")
    if len(data) > 0:
        print(f"First item keys: {list(data[0].keys())}")
elif isinstance(data, dict):
    print(f"Keys: {list(data.keys())}")
    if 'markets' in data:
        print(f"Markets length: {len(data['markets'])}")