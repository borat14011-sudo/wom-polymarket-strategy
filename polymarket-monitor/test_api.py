import requests

response = requests.get('https://gamma-api.polymarket.com/markets', params={'limit': 20, 'active': True}, timeout=10)
markets = response.json()

print(f"Found {len(markets)} markets:\n")
for i, m in enumerate(markets, 1):
    print(f"{i}. {m.get('question', 'Unknown')}")
