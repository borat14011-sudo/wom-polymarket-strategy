#!/usr/bin/env python3
"""Scan active markets for opportunities in the sweet spot price range."""

import json

with open('active-markets.json', 'r') as f:
    markets = json.load(f)

print(f"Loaded {len(markets)} markets")
print()

# Find opportunities in the sweet spot (8-20% or 80-92%)
opportunities = []
for m in markets:
    try:
        prices = json.loads(m.get('outcomePrices', '[]'))
        if not prices:
            continue
        yes_price = float(prices[0])
        volume = float(m.get('volume', 0))
        liquidity = float(m.get('liquidityNum', 0) or 0)
        question = m.get('question', '')
        slug = m.get('slug', '')
        volume_24h = float(m.get('volume24hr', 0) or 0)
        end_date = m.get('endDateIso', '')
        spread = float(m.get('spread', 0) or 0)
        
        # Sweet spot check
        if (0.08 <= yes_price <= 0.20) or (0.80 <= yes_price <= 0.92):
            if volume > 100000:  # Reasonable volume
                opportunities.append({
                    'question': question[:80],
                    'price': yes_price,
                    'volume': volume,
                    'vol24h': volume_24h,
                    'liquidity': liquidity,
                    'slug': slug,
                    'end_date': end_date,
                    'spread': spread
                })
    except Exception as e:
        pass

# Sort by 24h volume
opportunities.sort(key=lambda x: x['vol24h'], reverse=True)

print(f'Found {len(opportunities)} opportunities in sweet spot (8-20% or 80-92%)')
print('='*80)
print()

for i, opp in enumerate(opportunities[:25]):
    price_str = f"{opp['price']:.1%}"
    vol24h_str = f"${opp['vol24h']:,.0f}"
    total_str = f"${opp['volume']:,.0f}"
    liq_str = f"${opp['liquidity']:,.0f}"
    
    print(f"{i+1}. {opp['question']}")
    print(f"   Price: {price_str} | 24h Vol: {vol24h_str} | Total: {total_str}")
    print(f"   Liquidity: {liq_str} | Spread: {opp['spread']:.1%} | Ends: {opp['end_date']}")
    print(f"   Slug: {opp['slug']}")
    print()
