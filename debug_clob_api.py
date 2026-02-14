#!/usr/bin/env python3
"""
Debug CLOB API response
"""

import requests

url = 'https://clob.polymarket.com/markets'
print(f"Fetching: {url}")

response = requests.get(url, timeout=10)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")

# Try to parse as JSON
try:
    data = response.json()
    print(f"JSON parsed successfully")
    print(f"Type: {type(data)}")
    
    if isinstance(data, list):
        print(f"List length: {len(data)}")
        if len(data) > 0:
            print(f"First item keys: {list(data[0].keys())}")
    elif isinstance(data, dict):
        print(f"Dict keys: {list(data.keys())}")
        
except Exception as e:
    print(f"JSON parse error: {e}")
    print(f"First 200 chars of response: {response.text[:200]}")