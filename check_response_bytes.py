#!/usr/bin/env python3
"""
Check API response - write bytes
"""

import requests
import json

clob_base = "https://clob.polymarket.com"
markets_url = f"{clob_base}/markets"

response = requests.get(markets_url, timeout=10)
print(f"Status: {response.status_code}")

# Write bytes to avoid encoding issues
with open('clob_response_bytes.json', 'wb') as f:
    f.write(response.content)

print(f"Response saved (bytes)")

# Try to parse
try:
    data = response.json()
    print(f"\nParsed successfully")
    print(f"Type: {type(data)}")
    
    if isinstance(data, dict):
        print(f"Dict keys: {list(data.keys())}")
        
        # Check structure
        for key, value in data.items():
            print(f"\n{key}: {type(value)}")
            if isinstance(value, list):
                print(f"  List length: {len(value)}")
                if value and isinstance(value[0], dict):
                    print(f"  First item keys: {list(value[0].keys())[:10]}...")
                    
except Exception as e:
    print(f"Parse error: {e}")