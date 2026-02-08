import requests

response = requests.get('https://clob.polymarket.com/markets', params={'active': 'true'}, timeout=10)
data = response.json()

print(f"CLOB API Response:")
print(f"Total markets: {data.get('count', 'unknown')}")
print(f"Markets in this batch: {len(data.get('data', []))}")
print()

markets = data.get('data', [])

# Search for Iran
iran_markets = [m for m in markets if 'iran' in m.get('question', '').lower()]
print(f"Iran markets found: {len(iran_markets)}")

for m in iran_markets:
    print(f"\nMarket: {m.get('question')}")
    print(f"  Tokens: {m.get('tokens', [])}")
    print(f"  Active: {m.get('active')}")
    print(f"  End date: {m.get('end_date_iso')}")
    print(f"  CLOB tokens: {[t.get('token_id') for t in m.get('tokens', [])]}")
