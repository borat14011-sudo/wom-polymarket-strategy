import json

with open('C:/Users/Borat/.openclaw/workspace/active-markets.json', 'r') as f:
    data = json.load(f)

print('=== MARKET ANALYSIS ===')
print(f'Total markets loaded: {len(data)}')
print()

trump_markets = []
elon_markets = []

for market in data:
    q = market.get('question', '').lower()
    if 'deport' in q or ('trump' in q and '250' in q):
        trump_markets.append(market)
    if 'elon' in q or 'doge' in q or 'musk' in q:
        elon_markets.append(market)

print('=== TRUMP DEPORTATION MARKETS ===')
for m in trump_markets:
    print(f"{m.get('question', 'N/A')}")
    print(f"  Price: {m.get('outcomePrices', 'N/A')}")
    print(f"  Volume 24h: ${m.get('volume24hr', 0):,.0f}")
    print(f"  Last Trade: {m.get('lastTradePrice', 'N/A')}")
    print(f"  Best Bid: {m.get('bestBid', 'N/A')}, Best Ask: {m.get('bestAsk', 'N/A')}")
    print()

print('=== ELON/DOGE MARKETS ===')
for m in elon_markets[:5]:
    print(f"{m.get('question', 'N/A')}")
    print(f"  Price: {m.get('outcomePrices', 'N/A')}")
    print(f"  Volume 24h: ${m.get('volume24hr', 0):,.0f}")
    print()

# Check for significant price movements
print('=== PRICE CHANGE ANALYSIS ===')
for m in data:
    one_hour = m.get('oneHourPriceChange', 0)
    one_day = m.get('oneDayPriceChange', 0)
    if abs(one_hour) > 0.01 or abs(one_day) > 0.03:
        print(f"{m.get('question', 'N/A')[:60]}...")
        print(f"  1h change: {one_hour:+.4f}, 1d change: {one_day:+.4f}")
