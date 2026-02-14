#!/usr/bin/env python3
"""
Search for tariff markets more broadly
"""
import json

# Read the current market data
with open('active-markets.json', 'r') as f:
    data = json.load(f)

markets = data['markets']

print("=== SEARCHING FOR TARIFF MARKETS ===")

tariff_keywords = ['tariff', 'trade', 'china', 'mexico', 'canada', 'import', 'export', 'duty', 'customs']

tariff_markets = []
for market in markets:
    question = market.get('question', '').lower()
    volume = float(market.get('volume', 0))
    
    for keyword in tariff_keywords:
        if keyword in question:
            tariff_markets.append(market)
            break

print(f"Found {len(tariff_markets)} potential tariff/trade related markets:")

# Sort by volume
tariff_markets_sorted = sorted(tariff_markets, key=lambda x: float(x.get('volume', 0)), reverse=True)

for market in tariff_markets_sorted[:15]:  # Top 15
    question = market.get('question', '')
    volume = float(market.get('volume', 0))
    prices = market.get('outcomePrices', '[]')
    print(f"\n- {question}")
    print(f"  Volume: ${volume:,.0f} | Prices: {prices}")