import requests
import json
from datetime import datetime

url = 'https://gamma-api.polymarket.com/markets?limit=200&active=true'
resp = requests.get(url, timeout=30)
data = resp.json()

print(f"Fetched {len(data)} markets at {datetime.now().strftime('%H:%M:%S')}")
print()

# Look for Elon/DOGE markets
elon_markets = [m for m in data if 'elon' in m.get('question', '').lower() or 'doge' in m.get('question', '').lower() or 'musk' in m.get('question', '').lower()]
print(f"Found {len(elon_markets)} Elon/DOGE/Musk markets:")
for m in elon_markets[:10]:
    q = m.get('question', 'N/A')
    print(f"  - {q[:70]}...")
    vol = float(m.get('volume', 0) or 0)
    liq = float(m.get('liquidity', 0) or 0)
    print(f"    Volume: ${vol:,.0f}, Liquidity: ${liq:,.0f}")
    if 'outcomePrices' in m and m['outcomePrices']:
        print(f"    Prices: {m.get('outcomePrices')}")
    print()

# Look for Trump deportation markets
trump_markets = [m for m in data if 'trump' in m.get('question', '').lower() and 'deport' in m.get('question', '').lower()]
print(f"Found {len(trump_markets)} Trump deportation markets")
for m in trump_markets[:5]:
    q = m.get('question', 'N/A')
    print(f"  - {q[:70]}...")
    print(f"    Volume: ${m.get('volume', 0):,.0f}")
    if 'outcomePrices' in m and m['outcomePrices']:
        print(f"    Prices: {m.get('outcomePrices')}")
    print()

# Check for any markets with recent activity (last 24h)
print("\n=== MARKETS WITH RECENT ACTIVITY ===")
for m in sorted(data, key=lambda x: x.get('volume24hr', 0), reverse=True)[:10]:
    vol24 = m.get('volume24hr', 0)
    if vol24 > 1000:
        print(f"{m.get('question', 'N/A')[:60]}...")
        print(f"  24h Volume: ${vol24:,.0f}, Total: ${m.get('volume', 0):,.0f}")
