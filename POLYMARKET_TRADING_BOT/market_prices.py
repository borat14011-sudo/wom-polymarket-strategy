import requests
import json

# Get markets directly (not events)
url = 'https://gamma-api.polymarket.com/markets'
params = {'active': 'true', 'archived': 'false', 'closed': 'false', 'limit': 200}
resp = requests.get(url, params=params, timeout=15)
markets = resp.json()

print(f"Total active markets: {len(markets)}")

# Find specific markets
targets = ['trump deport 250', 'trump deport 750', 'elon 50b', 'elon 250b', 'microstrategy 500k', 'doge cut']

print("\n=== SCANNING FOR TARGET MARKETS ===\n")

for market in markets:
    question = market.get('question', '').lower()
    
    # Check Trump deportation
    if 'trump' in question and 'deport' in question:
        print(f"TRUMP DEPORT: {market.get('question')}")
        print(f"  Volume 24h: ${float(market.get('volume24hr',0) or 0):,.0f}")
        print(f"  Best Bid: {float(market.get('bestBid',0) or 0)*100:.1f}c")
        print(f"  Best Ask: {float(market.get('bestAsk',0) or 0)*100:.1f}c")
        print(f"  Last Price: {float(market.get('lastTradePrice',0) or 0)*100:.1f}c")
        print()
    
    # Check Elon/DOGE
    if any(x in question for x in ['elon', 'doge', 'musk']):
        print(f"ELON/DOGE: {market.get('question')}")
        print(f"  Volume 24h: ${float(market.get('volume24hr',0) or 0):,.0f}")
        print(f"  Best Bid: {float(market.get('bestBid',0) or 0)*100:.1f}c")
        print(f"  Best Ask: {float(market.get('bestAsk',0) or 0)*100:.1f}c")
        print()
    
    # Check BTC/MSTR
    if any(x in question for x in ['microstrategy', 'mstr 500k', 'bitcoin 150k']):
        print(f"BTC/MSTR: {market.get('question')}")
        print(f"  Volume 24h: ${float(market.get('volume24hr',0) or 0):,.0f}")
        print(f"  Best Bid: {float(market.get('bestBid',0) or 0)*100:.1f}c")
        print(f"  Best Ask: {float(market.get('bestAsk',0) or 0)*100:.1f}c")
        print()

print("=== SCAN COMPLETE ===")
