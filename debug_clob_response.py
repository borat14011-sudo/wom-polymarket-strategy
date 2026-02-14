#!/usr/bin/env python3
"""
Debug CLOB API response structure
"""

import requests
import json

url = "https://clob.polymarket.com/markets?limit=3"
print(f"Fetching: {url}")

response = requests.get(url, timeout=10)
data = response.json()

print(f"\nResponse structure:")
print(json.dumps(data, indent=2)[:1000])

# Check first market structure
markets = data.get('data', [])
if markets:
    print(f"\n\nFirst market structure:")
    print(json.dumps(markets[0], indent=2)[:800])
    
    # Check keys
    print(f"\nKeys in first market:")
    for key in markets[0].keys():
        print(f"  - {key}: {type(markets[0][key])}")
        
    # Check outcomes if present
    if 'outcomes' in markets[0]:
        outcomes = markets[0]['outcomes']
        print(f"\nOutcomes: {len(outcomes)}")
        for i, outcome in enumerate(outcomes):
            print(f"  Outcome {i}: {outcome}")