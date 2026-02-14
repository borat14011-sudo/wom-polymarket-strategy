#!/usr/bin/env python3
"""
Check actual API response
"""

import requests
import json

clob_base = "https://clob.polymarket.com"
markets_url = f"{clob_base}/markets"

response = requests.get(markets_url, timeout=10)
print(f"Status: {response.status_code}")
print(f"Content type: {response.headers.get('content-type')}")

# Save response
with open('clob_response.json', 'w') as f:
    f.write(response.text)

print(f"\nFirst 500 chars:")
print(response.text[:500])

# Try to parse
try:
    data = response.json()
    print(f"\nParsed JSON type: {type(data)}")
    
    if isinstance(data, list):
        print(f"List length: {len(data)}")
        if data:
            print(f"First item keys: {list(data[0].keys())}")
    elif isinstance(data, dict):
        print(f"Dict keys: {list(data.keys())}")
        print(f"Full dict: {json.dumps(data, indent=2)[:500]}...")
        
except Exception as e:
    print(f"Parse error: {e}")