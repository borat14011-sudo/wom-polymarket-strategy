import requests
import json
from datetime import datetime

# Get active markets
url = 'https://gamma-api.polymarket.com/events'
params = {'active': 'true', 'closed': 'false', 'limit': 100, 'offset': 0}

resp = requests.get(url, params=params, timeout=15)
print(f"Status: {resp.status_code}")
data = resp.json()
print(f"Total events: {len(data)}")

# Find key markets
trump_markets = []
elon_markets = []
btc_markets = []

for event in data:
    title = event.get('title', '').lower()
    vol = float(event.get('volume24hr', 0) or 0)
    
    if 'trump' in title and 'deport' in title:
        trump_markets.append({'title': event.get('title'), 'volume24hr': vol, 'liquidity': event.get('liquidity', 0)})
    if any(x in title for x in ['elon', 'doge', 'musk']):
        elon_markets.append({'title': event.get('title'), 'volume24hr': vol, 'liquidity': event.get('liquidity', 0)})
    if any(x in title for x in ['bitcoin', 'btc', 'microstrategy', 'mstr']):
        btc_markets.append({'title': event.get('title'), 'volume24hr': vol, 'liquidity': event.get('liquidity', 0)})

print("\n=== TRUMP DEPORTATION MARKETS ===")
total_trump_vol = 0
for m in sorted(trump_markets, key=lambda x: x['volume24hr'], reverse=True)[:5]:
    print(f"{m['title'][:55]}... Vol: ${m['volume24hr']:,.0f}")
    total_trump_vol += m['volume24hr']
print(f"Total Trump deport 24h volume: ${total_trump_vol:,.0f}")

print("\n=== ELON/DOGE MARKETS ===")
total_elon_vol = 0
for m in sorted(elon_markets, key=lambda x: x['volume24hr'], reverse=True)[:5]:
    print(f"{m['title'][:55]}... Vol: ${m['volume24hr']:,.0f}")
    total_elon_vol += m['volume24hr']
print(f"Total Elon/DOGE 24h volume: ${total_elon_vol:,.0f}")

print("\n=== BTC/MSTR MARKETS ===")
for m in sorted(btc_markets, key=lambda x: x['volume24hr'], reverse=True)[:3]:
    print(f"{m['title'][:55]}... Vol: ${m['volume24hr']:,.0f}")

# Check for market changes - compare with prior
print(f"\n=== SCAN TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
