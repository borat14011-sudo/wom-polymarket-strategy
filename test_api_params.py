import requests
import json

# Try different parameter combinations
tests = [
    {'limit': 50, 'closed': False},
    {'limit': 50, 'active': True, 'closed': False},
    {'limit': 50, 'archived': False},
    {'limit': 50},  # no filters
]

url = 'https://gamma-api.polymarket.com/markets'

for i, params in enumerate(tests):
    print(f"\n--- Test {i+1}: {params} ---")
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        markets = response.json()
        open_count = sum(1 for m in markets if m.get('closed') == False)
        archived_count = sum(1 for m in markets if m.get('archived') == True)
        print(f"  Total: {len(markets)}, Open (closed=False): {open_count}, Archived: {archived_count}")
        if markets:
            sample = markets[0]
            print(f"  Sample: {sample.get('question', 'N/A')[:50]}...")
            print(f"    closed={sample.get('closed')}, active={sample.get('active')}, archived={sample.get('archived')}")
    else:
        print(f"  Error: {response.status_code}")
