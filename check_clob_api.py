import requests
import json

# Try to get order book data from CLOB API for the 500-750k market
market_id = "517313"  # 500-750k deportations

print("Checking CLOB API for market order book...")
print(f"Market ID: {market_id}")

# Try CLOB API endpoints
endpoints = [
    f"https://clob.polymarket.com/markets/{market_id}",
    f"https://clob.polymarket.com/book?market={market_id}",
]

for url in endpoints:
    print(f"\nTrying: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Keys: {list(data.keys())[:10]}")
            if 'bids' in data:
                print(f"Bids: {data['bids'][:3]}")
            if 'asks' in data:
                print(f"Asks: {data['asks'][:3]}")
    except Exception as e:
        print(f"Error: {e}")

# Also check if there's a different market slug
print("\n" + "="*60)
print("Checking all deportation market IDs:")

url = "https://gamma-api.polymarket.com/markets"
params = {'limit': 20, 'closed': False}
response = requests.get(url, params=params, timeout=10)

if response.status_code == 200:
    markets = response.json()
    for m in markets:
        q = m.get('question', '')
        if 'deport' in q.lower() and '500' in q:
            print(f"\nID: {m.get('id')}")
            print(f"Q: {q}")
            print(f"Prices: {m.get('outcomePrices')}")
            print(f"Slug: {m.get('slug')}")
