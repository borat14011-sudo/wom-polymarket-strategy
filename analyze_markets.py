#!/usr/bin/env python3
import json

with open(r'C:\Users\Borat\.openclaw\workspace\active-markets.json') as f:
    markets = json.load(f)

print('=== LOW PRICE FADE OPPORTUNITIES (5-35% YES) ===')
print('Strategy: BET NO on these longshots')
print()
low_price = []
for m in markets:
    try:
        prices = json.loads(m.get('outcomePrices', '[]'))
        yes_price = float(prices[0]) if prices else 0
        vol24 = m.get('volume24hr', 0) or 0
        if 0.05 <= yes_price <= 0.35 and vol24 > 500:
            low_price.append({
                'q': m.get('question', '')[:65],
                'yes': yes_price,
                'vol24': vol24,
                'chg1d': m.get('oneDayPriceChange', 0) or 0,
                'slug': m.get('slug', '')
            })
    except: pass

for x in sorted(low_price, key=lambda x: -x['vol24'])[:15]:
    print(f"{x['yes']*100:5.1f}% YES | ${x['vol24']:>10,.0f} 24h | {x['chg1d']*100:+5.1f}% | {x['q']}")

print()
print('=== NEAR-CERTAINTIES (85-95% YES) ===')
print('Strategy: Check if truly >95% certain - info edge')
print()
high_price = []
for m in markets:
    try:
        prices = json.loads(m.get('outcomePrices', '[]'))
        yes_price = float(prices[0]) if prices else 0
        vol24 = m.get('volume24hr', 0) or 0
        if 0.85 <= yes_price <= 0.95 and vol24 > 3000:
            high_price.append({
                'q': m.get('question', '')[:65],
                'yes': yes_price,
                'vol24': vol24,
                'chg1d': m.get('oneDayPriceChange', 0) or 0,
                'slug': m.get('slug', '')
            })
    except: pass

for x in sorted(high_price, key=lambda x: -x['vol24'])[:12]:
    print(f"{x['yes']*100:5.1f}% YES | ${x['vol24']:>10,.0f} 24h | {x['chg1d']*100:+5.1f}% | {x['q']}")

print()
print('=== BIG MOVERS (>5% 1-day change, volume>$2k) ===')
print('Strategy: Momentum follow OR hype fade depending on news')
print()
movers = []
for m in markets:
    try:
        prices = json.loads(m.get('outcomePrices', '[]'))
        yes_price = float(prices[0]) if prices else 0
        vol24 = m.get('volume24hr', 0) or 0
        chg = m.get('oneDayPriceChange', 0) or 0
        if abs(chg) > 0.05 and vol24 > 2000:
            movers.append({
                'q': m.get('question', '')[:55],
                'yes': yes_price,
                'vol24': vol24,
                'chg1d': chg,
                'slug': m.get('slug', '')
            })
    except: pass

for x in sorted(movers, key=lambda x: -abs(x['chg1d']))[:12]:
    direction = "UP" if x['chg1d'] > 0 else "DOWN"
    print(f"{x['chg1d']*100:+6.1f}% {direction:<4} | {x['yes']*100:5.1f}% now | ${x['vol24']:>8,.0f} | {x['q']}")

print()
print('=== TRUMP MARKET FADE CANDIDATES ===')
trump = []
for m in markets:
    try:
        q = m.get('question', '').lower()
        if 'trump' in q or 'doge' in q or 'tariff' in q or 'deport' in q:
            prices = json.loads(m.get('outcomePrices', '[]'))
            yes_price = float(prices[0]) if prices else 0
            vol24 = m.get('volume24hr', 0) or 0
            if vol24 > 1000:
                trump.append({
                    'q': m.get('question', '')[:65],
                    'yes': yes_price,
                    'vol24': vol24,
                    'chg1d': m.get('oneDayPriceChange', 0) or 0
                })
    except: pass

for x in sorted(trump, key=lambda x: -x['vol24'])[:10]:
    print(f"{x['yes']*100:5.1f}% YES | ${x['vol24']:>10,.0f} | {x['chg1d']*100:+5.1f}% | {x['q']}")

print()
print(f"Total markets analyzed: {len(markets)}")
