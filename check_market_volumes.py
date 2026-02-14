#!/usr/bin/env python3
"""
Check market volumes in active-markets.json
"""

import json

with open('active-markets.json', 'r') as f:
    data = json.load(f)

markets = data.get('markets', [])
print(f"Total markets: {len(markets)}")

# Check first 10 markets
print("\nFirst 10 markets:")
for i, m in enumerate(markets[:10]):
    question = m.get('question', 'Unknown')[:60]
    volume = m.get('volume24h', 0)
    yes_price = m.get('yesPrice', 0)
    no_price = m.get('noPrice', 0)
    
    print(f"{i+1}. {question}...")
    print(f"   Volume: ${volume}")
    print(f"   YES: {yes_price:.3f} | NO: {no_price:.3f}")
    print()

# Find markets with any volume
markets_with_volume = [m for m in markets if m.get('volume24h', 0) > 0]
print(f"\nMarkets with volume > 0: {len(markets_with_volume)}")

if markets_with_volume:
    print("\nTop 5 markets by volume:")
    sorted_markets = sorted(markets_with_volume, key=lambda x: x.get('volume24h', 0), reverse=True)[:5]
    for i, m in enumerate(sorted_markets):
        question = m.get('question', 'Unknown')[:60]
        volume = m.get('volume24h', 0)
        yes_price = m.get('yesPrice', 0)
        no_price = m.get('noPrice', 0)
        
        print(f"{i+1}. {question}...")
        print(f"   Volume: ${volume:,.2f}")
        print(f"   YES: {yes_price:.3f} | NO: {no_price:.3f}")
        print()