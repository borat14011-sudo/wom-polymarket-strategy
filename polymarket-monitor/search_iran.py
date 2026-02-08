import requests

# Get more markets
print("Searching for Iran markets...")

response = requests.get(
    'https://gamma-api.polymarket.com/markets',
    params={'limit': 500, 'active': True, 'closed': False},
    timeout=20
)

markets = response.json()
print(f"Total markets fetched: {len(markets)}\n")

# Search for Iran
iran_markets = []
for m in markets:
    question = m.get('question', '')
    if 'iran' in question.lower():
        iran_markets.append(m)

print(f"Iran markets found: {len(iran_markets)}\n")

if iran_markets:
    for m in iran_markets:
        print(f"Market: {m.get('question')}")
        prices = m.get('outcomePrices', [])
        if len(prices) >= 2:
            print(f"  YES: {float(prices[0])*100:.1f}%")
            print(f"  NO: {float(prices[1])*100:.1f}%")
        print(f"  Volume 24h: ${float(m.get('volume24hr', 0)):,.0f}")
        print(f"  End Date: {m.get('endDate')}")
        print()
else:
    print("NO IRAN MARKETS FOUND")
    print("\nMaybe try searching for 'strike' instead...")
    
    strike_markets = [m for m in markets if 'strike' in m.get('question', '').lower()]
    print(f"Strike markets found: {len(strike_markets)}")
    for m in strike_markets[:5]:
        print(f"  - {m.get('question')}")
