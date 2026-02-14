#!/usr/bin/env python3
"""Cross-platform arbitrage and opportunity scanner"""
import json
import re
from datetime import datetime

# Load both datasets
with open('polymarket_latest.json', encoding='utf-8') as f:
    pm_data = json.load(f)
with open('kalshi_latest.json', encoding='utf-8') as f:
    kalshi_data = json.load(f)

# Extract markets from nested structure
if isinstance(pm_data, dict) and 'markets' in pm_data:
    pm_markets = pm_data['markets']
elif isinstance(pm_data, list):
    pm_markets = pm_data
else:
    pm_markets = pm_data.get('data', [])

if isinstance(kalshi_data, dict) and 'events' in kalshi_data:
    kalshi_events = kalshi_data['events']
elif isinstance(kalshi_data, list):
    kalshi_events = kalshi_data
else:
    kalshi_events = []

print('='*70)
print(f'MARKET ANALYSIS REPORT - {datetime.now().strftime("%Y-%m-%d %H:%M")}')
print('='*70)

def normalize(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())

def get_pm_price(pm):
    """Get YES price from Polymarket market"""
    prices = pm.get('outcomePrices', [])
    if prices and isinstance(prices, str):
        import ast
        try:
            prices = ast.literal_eval(prices)
        except:
            return 0
    return float(prices[0]) * 100 if prices and len(prices) > 0 else 0

# POLYMARKET ANALYSIS
print(f'\n[1] POLYMARKET DATA ({len(pm_markets)} markets)')
print('-'*70)

# High volume markets
high_vol = []
low_price = []
high_price = []

for pm in pm_markets:
    vol = float(pm.get('volume', 0) or pm.get('volumeNum', 0) or 0)
    price = get_pm_price(pm)
    title = pm.get('question', pm.get('title', ''))[:55]
    
    if vol > 50000 and 5 < price < 95:
        high_vol.append({'title': title, 'price': price, 'volume': vol})
    if 2 < price < 10 and vol > 10000:
        low_price.append({'title': title, 'price': price, 'volume': vol})
    if 90 < price < 98 and vol > 10000:
        high_price.append({'title': title, 'price': price, 'volume': vol})

print('\n  HIGH VOLUME MARKETS (>$50K, 5-95%):')
for m in sorted(high_vol, key=lambda x: x['volume'], reverse=True)[:8]:
    print(f"    {m['title']}")
    print(f"      YES: {m['price']:.1f}%  Vol: ${m['volume']:,.0f}")

print('\n  LONGSHOT OPPORTUNITIES (2-10%):')
for m in sorted(low_price, key=lambda x: x['volume'], reverse=True)[:5]:
    print(f"    {m['title']}: {m['price']:.1f}% (${m['volume']:,.0f})")

print('\n  NEAR-CERTAINTIES (90-98%):')
for m in sorted(high_price, key=lambda x: x['volume'], reverse=True)[:5]:
    print(f"    {m['title']}: {m['price']:.1f}% (${m['volume']:,.0f})")

# KALSHI ANALYSIS
print(f'\n\n[2] KALSHI DATA ({len(kalshi_events)} events)')
print('-'*70)

for e in kalshi_events:
    title = e.get('title', 'Unknown')
    category = e.get('category', 'N/A')
    print(f"\n  {title} [{category}]")
    
    for m in e.get('markets', []):
        name = m.get('name', m.get('ticker', ''))
        try:
            yes_bid = int(m.get('yes_bid', 0) or 0)
            yes_ask = int(m.get('yes_ask', 0) or 0)
            last = int(m.get('last_price', 0) or 0)
            vol = int(m.get('volume', 0) or 0)
        except:
            continue
        
        spread = yes_ask - yes_bid if yes_ask and yes_bid else 0
        print(f"    {name[:40]}: Last={last}c Bid={yes_bid}c Ask={yes_ask}c Spread={spread}c Vol={vol}")

# CROSS-PLATFORM CHECK
print('\n\n[3] CROSS-PLATFORM ARBITRAGE SCAN')
print('-'*70)

# Build searchable index
pm_keywords = {}
for pm in pm_markets:
    q = pm.get('question', pm.get('title', ''))
    key_terms = ['trump', 'bitcoin', 'btc', 'elon', 'musk', 'fed', 'rate', 'inflation', 'recession', 'gdp']
    for term in key_terms:
        if term in q.lower():
            price = get_pm_price(pm)
            if term not in pm_keywords:
                pm_keywords[term] = []
            pm_keywords[term].append({'q': q[:50], 'price': price})

kalshi_keywords = {}
for e in kalshi_events:
    title = e.get('title', '')
    key_terms = ['trump', 'bitcoin', 'btc', 'elon', 'musk', 'fed', 'rate', 'inflation', 'recession', 'gdp']
    for term in key_terms:
        if term in title.lower():
            for m in e.get('markets', []):
                try:
                    mid = (int(m.get('yes_bid', 0) or 0) + int(m.get('yes_ask', 0) or 0)) / 2
                except:
                    mid = 0
                if term not in kalshi_keywords:
                    kalshi_keywords[term] = []
                kalshi_keywords[term].append({'q': title[:50], 'price': mid})

# Compare overlapping keywords
found_arb = False
for term in pm_keywords:
    if term in kalshi_keywords:
        print(f"\n  KEYWORD: {term.upper()}")
        print(f"    Polymarket markets: {len(pm_keywords[term])}")
        for p in pm_keywords[term][:3]:
            print(f"      {p['q']}: {p['price']:.1f}%")
        print(f"    Kalshi events: {len(kalshi_keywords[term])}")
        for k in kalshi_keywords[term][:3]:
            print(f"      {k['q']}: {k['price']:.1f}c")
        found_arb = True

if not found_arb:
    print("  No overlapping keywords found between platforms")

# Summary
print('\n\n[4] SUMMARY & RECOMMENDATIONS')
print('-'*70)
print(f"  Polymarket: {len(pm_markets)} markets")
print(f"  Kalshi: {len(kalshi_events)} events")
print(f"  High-volume PM opportunities: {len(high_vol)}")
print(f"  Longshot opportunities: {len(low_price)}")
print(f"  Near-certainties: {len(high_price)}")

if high_vol:
    top = max(high_vol, key=lambda x: x['volume'])
    print(f"\n  TOP OPPORTUNITY: {top['title']}")
    print(f"    Price: {top['price']:.1f}%  Volume: ${top['volume']:,.0f}")

print('\n' + '='*70)
