import json

with open('active-markets.json', 'r') as f:
    markets = json.load(f)

print(f"Total active markets: {len(markets)}")

# Search for deportation markets
print("\n=== DEPORTATION MARKETS (Current Prices) ===")
deport = [m for m in markets if 'deport' in m.get('question', '').lower()]
for m in deport:
    q = m.get('question', 'N/A')
    prices = json.loads(m.get('outcomePrices', '["0", "0"]'))
    vol = m.get('volume24hr', 0)
    print(f"- {q}")
    print(f"  YES: {float(prices[0])*100:.2f}% | NO: {float(prices[1])*100:.2f}% | 24h Vol: ${vol:,.0f}")
    print()

# Search for Elon/DOGE/Musk markets
print("\n=== ELON/DOGE/MUSK MARKETS ===")
elon = [m for m in markets if any(kw in m.get('question', '').lower() for kw in ['elon', 'doge', 'musk', 'cut', 'billion']) and ('cut' in m.get('question', '').lower() or 'billion' in m.get('question', '').lower() or 'doge' in m.get('question', '').lower())]
for m in elon:
    q = m.get('question', 'N/A')
    prices = json.loads(m.get('outcomePrices', '["0", "0"]'))
    vol = m.get('volume24hr', 0)
    print(f"- {q}")
    print(f"  YES: {float(prices[0])*100:.2f}% | NO: {float(prices[1])*100:.2f}% | 24h Vol: ${vol:,.0f}")
    print()

# Search for crypto markets (MegaETH, OpenSea, etc)
print("\n=== CRYPTO/MARKET OPPORTUNITIES ===")
crypto = [m for m in markets if any(kw in m.get('question', '').lower() for kw in ['megaeth', 'opensea', 'fdv', 'bitcoin', 'btc'])]
for m in crypto:
    q = m.get('question', 'N/A')
    prices = json.loads(m.get('outcomePrices', '["0", "0"]'))
    vol = m.get('volume24hr', 0)
    print(f"- {q}")
    print(f"  YES: {float(prices[0])*100:.2f}% | NO: {float(prices[1])*100:.2f}% | 24h Vol: ${vol:,.0f}")
    print()

# Search for weather markets
print("\n=== WEATHER MARKETS ===")
weather = [m for m in markets if any(kw in m.get('question', '').lower() for kw in ['hurricane', 'tornado', 'snow', 'rain', 'temperature'])]
for m in weather[:5]:
    q = m.get('question', 'N/A')
    prices = json.loads(m.get('outcomePrices', '["0", "0"]'))
    vol = m.get('volume24hr', 0)
    print(f"- {q}")
    print(f"  YES: {float(prices[0])*100:.2f}% | NO: {float(prices[1])*100:.2f}% | 24h Vol: ${vol:,.0f}")
    print()

# Top movers by 24h volume
print("\n=== TOP 10 BY 24H VOLUME ===")
top_vol = sorted(markets, key=lambda x: x.get('volume24hr', 0), reverse=True)[:10]
for i, m in enumerate(top_vol):
    q = m.get('question', 'N/A')[:70]
    prices = json.loads(m.get('outcomePrices', '["0", "0"]'))
    vol = m.get('volume24hr', 0)
    spread = m.get('spread', 0) * 100
    print(f"{i+1}. {q}...")
    print(f"   YES: {float(prices[0])*100:.1f}% | Vol: ${vol:,.0f} | Spread: {spread:.2f}%")
