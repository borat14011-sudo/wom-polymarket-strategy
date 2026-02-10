import requests
import json

# Try different endpoints
endpoints = [
    'https://gamma-api.polymarket.com/markets?limit=100',
    'https://gamma-api.polymarket.com/markets?active=true&limit=100',
    'https://clob.polymarket.com/markets',
]

for url in endpoints:
    try:
        print(f'\n=== Testing: {url[:50]}... ===')
        r = requests.get(url, timeout=15)
        print(f'Status: {r.status_code}')
        data = r.json()
        print(f'Type: {type(data)}')
        if isinstance(data, list):
            print(f'Markets count: {len(data)}')
            if data:
                print(f'Sample: {data[0].get("question", "N/A")[:60]}')
        elif isinstance(data, dict):
            print(f'Keys: {list(data.keys())[:5]}')
    except Exception as e:
        print(f'Error: {e}')
