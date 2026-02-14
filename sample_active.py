import json
import sys

with open('active-markets.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

print("Type:", type(data))
if isinstance(data, list):
    print("Length:", len(data))
    if len(data) > 0:
        print("Keys:", data[0].keys())
        print("Sample:", json.dumps(data[0], indent=2))
else:
    print("Top keys:", data.keys())
    if 'markets' in data:
        print("Markets length:", len(data['markets']))