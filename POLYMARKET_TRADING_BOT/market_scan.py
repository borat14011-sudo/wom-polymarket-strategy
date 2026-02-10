import requests
import json

# Get all active markets
url = 'https://gamma-api.polymarket.com/events'
params = {'active': 'true', 'closed': 'false', 'limit': 200}
resp = requests.get(url, params=params, timeout=15)
events = resp.json()

print(f"Total active markets: {len(events)}")
print("\n=== SEARCHING FOR KEY MARKETS ===\n")

# Find Trump deport markets
trump_deport = [e for e in events if 'trump' in e.get('title','').lower() and 'deport' in e.get('title','').lower()]
print(f"Trump deport markets found: {len(trump_deport)}")
for e in trump_deport:
    print(f"  - {e.get('title')[:70]}")
    print(f"    Vol: ${float(e.get('volume24hr',0) or 0):,.0f} | Liq: ${float(e.get('liquidity',0) or 0):,.0f}")
    markets = e.get('markets',[])
    for m in markets[:3]:
        price = float(m.get('price',0) or 0) * 100
        print(f"    -> {m.get('outcome','N/A')}: {price:.1f}c")
    print()

# Find Elon/DOGE markets  
elon_doge = [e for e in events if any(x in e.get('title','').lower() for x in ['elon','doge','musk'])]
print(f"\nElon/DOGE markets found: {len(elon_doge)}")
for e in elon_doge[:5]:
    print(f"  - {e.get('title')[:70]}")
    print(f"    Vol: ${float(e.get('volume24hr',0) or 0):,.0f}")
    print()

# Find BTC/MSTR markets
btc = [e for e in events if any(x in e.get('title','').lower() for x in ['bitcoin','btc','microstrategy'])]
print(f"\nBTC/MSTR markets found: {len(btc)}")
for e in btc[:3]:
    print(f"  - {e.get('title')[:70]}")
    print(f"    Vol: ${float(e.get('volume24hr',0) or 0):,.0f}")
    print()

# Check for markets with high volume (>50k)
high_vol = [e for e in events if float(e.get('volume24hr',0) or 0) > 50000]
print(f"\n=== HIGH VOLUME MARKETS (>$50K 24h) ===")
print(f"Count: {len(high_vol)}")
for e in sorted(high_vol, key=lambda x: float(x.get('volume24hr',0) or 0), reverse=True)[:10]:
    vol = float(e.get('volume24hr',0) or 0)
    print(f"  ${vol:>10,.0f} - {e.get('title')[:60]}")
