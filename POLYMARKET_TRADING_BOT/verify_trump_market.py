import requests
import json

# Fetch the specific Trump deportation event
url = 'https://gamma-api.polymarket.com/events'
params = {'slug': 'how-many-people-will-trump-deport-in-2025'}

resp = requests.get(url, params=params, timeout=30)
data = resp.json()

print('=== TRUMP DEPORTATION MARKET ===')
print(f"Event Title: {data[0].get('title', 'N/A')}")
print(f"Volume: ${float(data[0].get('volume', 0)):,.0f}")
print()

markets = data[0].get('markets', [])
print(f'Number of outcome markets: {len(markets)}')
print()

for m in markets:
    question = m.get('question', 'N/A')
    bid = float(m.get('bestBid', 0))
    ask = float(m.get('bestAsk', 0))
    vol = float(m.get('volume', 0))
    prices = m.get('outcomePrices', '[]')
    print(f'Market: {question}')
    print(f'  Bid: {bid:.3f} | Ask: {ask:.3f}')
    print(f'  Volume: ${vol:,.0f}')
    print(f'  Prices: {prices}')
    print()
