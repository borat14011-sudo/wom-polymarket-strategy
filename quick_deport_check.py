import requests
import json

url = 'https://gamma-api.polymarket.com/markets'
params = {'limit': 50, 'closed': False}

response = requests.get(url, params=params, timeout=10)
if response.status_code == 200:
    markets = response.json()
    print("CURRENT DEPORTATION MARKET PRICES:")
    print("=" * 60)
    for m in markets:
        q = m.get('question', '')
        if 'deport' in q.lower():
            prices = m.get('outcomePrices', 'N/A')
            print(f"\n{q[:55]}...")
            print(f"  YES price: {prices}")
