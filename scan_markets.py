import json

with open('active-markets.json', 'r') as f:
    markets = json.load(f)

# Sort by 24h volume
sorted_markets = sorted(markets, key=lambda x: x.get('volume24hr', 0), reverse=True)

print("=" * 80)
print("TOP VOLUME MARKETS (Last 24h)")
print("=" * 80)

for m in sorted_markets[:30]:
    vol = m.get('volume24hr', 0)
    if vol < 1000:
        continue
    question = m.get('question', '')[:55]
    prices = m.get('outcomePrices', '[]')
    try:
        p = json.loads(prices) if isinstance(prices, str) else prices
        yes_price = float(p[0]) * 100
    except:
        yes_price = 0
    print(f"{question:55} | YES: {yes_price:5.1f}% | Vol: ${vol:>12,.0f}")

print("\n" + "=" * 80)
print("POTENTIAL OPPORTUNITIES - Low Price Markets (YES 5-25%)")
print("=" * 80)

low_price = [m for m in markets if m.get('volume24hr', 0) > 1000]
for m in low_price:
    try:
        prices = m.get('outcomePrices', '[]')
        p = json.loads(prices) if isinstance(prices, str) else prices
        yes_price = float(p[0])
        if 0.05 <= yes_price <= 0.25:
            question = m.get('question', '')[:55]
            vol = m.get('volume24hr', 0)
            print(f"{question:55} | YES: {yes_price*100:5.1f}% | Vol: ${vol:>10,.0f}")
    except:
        pass

print("\n" + "=" * 80)
print("NEAR-CERTAINTY OPPORTUNITIES (YES 85-97%)")
print("=" * 80)

for m in sorted_markets:
    try:
        prices = m.get('outcomePrices', '[]')
        p = json.loads(prices) if isinstance(prices, str) else prices
        yes_price = float(p[0])
        vol = m.get('volume24hr', 0)
        if 0.85 <= yes_price <= 0.97 and vol > 500:
            question = m.get('question', '')[:55]
            print(f"{question:55} | YES: {yes_price*100:5.1f}% | Vol: ${vol:>10,.0f}")
    except:
        pass
