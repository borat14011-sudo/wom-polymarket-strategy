#!/usr/bin/env python3
"""Full market opportunity scanner using all available data"""
import json
from datetime import datetime

print('='*70)
print(f'FULL MARKET SCAN - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('='*70)

# Load Polymarket data
with open('active-markets.json', encoding='utf-8') as f:
    pm_markets = json.load(f)

# Load Kalshi data if comprehensive version exists
try:
    with open('kalshi_full_events.json', encoding='utf-8') as f:
        kalshi_data = json.load(f)
    kalshi_events = kalshi_data.get('events', kalshi_data) if isinstance(kalshi_data, dict) else kalshi_data
except:
    kalshi_events = []

print(f'\nData loaded: {len(pm_markets)} Polymarket | {len(kalshi_events)} Kalshi events')

def parse_prices(pm):
    """Extract YES price"""
    prices = pm.get('outcomePrices', pm.get('outcomes', []))
    if isinstance(prices, str):
        import ast
        try:
            prices = ast.literal_eval(prices)
        except:
            return 0, 0
    if prices and len(prices) >= 2:
        return float(prices[0]) * 100, float(prices[1]) * 100
    return 0, 0

# POLYMARKET SCAN
print('\n' + '='*70)
print('[1] POLYMARKET OPPORTUNITY SCAN')
print('='*70)

opportunities = []
for pm in pm_markets:
    yes_price, no_price = parse_prices(pm)
    vol = float(pm.get('volume', 0) or pm.get('volumeNum', 0) or 0)
    liquidity = float(pm.get('liquidity', 0) or 0)
    title = pm.get('question', '')[:60]
    end_date = pm.get('endDate', '')[:10]
    
    # Calculate opportunity metrics
    if yes_price > 0:
        opportunities.append({
            'title': title,
            'yes': yes_price,
            'no': no_price,
            'volume': vol,
            'liquidity': liquidity,
            'end': end_date,
            'slug': pm.get('slug', '')
        })

# Sort by different criteria
print('\n--- TOP BY VOLUME ---')
by_vol = sorted(opportunities, key=lambda x: x['volume'], reverse=True)[:8]
for m in by_vol:
    print(f"  {m['title']}")
    print(f"    YES: {m['yes']:.1f}% | Vol: ${m['volume']:,.0f} | Liq: ${m['liquidity']:,.0f} | End: {m['end']}")

print('\n--- LONGSHOTS (5-15%) with VOLUME ---')
longshots = [o for o in opportunities if 5 < o['yes'] < 15 and o['volume'] > 10000]
longshots = sorted(longshots, key=lambda x: x['volume'], reverse=True)[:6]
for m in longshots:
    print(f"  {m['title']}")
    print(f"    YES: {m['yes']:.1f}% | Vol: ${m['volume']:,.0f} | End: {m['end']}")

print('\n--- NEAR-CERTAIN (85-95%) with VOLUME ---')
certs = [o for o in opportunities if 85 < o['yes'] < 95 and o['volume'] > 10000]
certs = sorted(certs, key=lambda x: x['volume'], reverse=True)[:6]
for m in certs:
    print(f"  {m['title']}")
    print(f"    YES: {m['yes']:.1f}% | Vol: ${m['volume']:,.0f} | End: {m['end']}")

print('\n--- MID-RANGE VOLATILE (40-60%) ---')
volatile = [o for o in opportunities if 40 < o['yes'] < 60 and o['volume'] > 20000]
volatile = sorted(volatile, key=lambda x: x['volume'], reverse=True)[:6]
for m in volatile:
    print(f"  {m['title']}")
    print(f"    YES: {m['yes']:.1f}% | Vol: ${m['volume']:,.0f} | End: {m['end']}")

# KALSHI SCAN
if kalshi_events:
    print('\n' + '='*70)
    print('[2] KALSHI OPPORTUNITY SCAN')
    print('='*70)
    
    k_opps = []
    for e in kalshi_events[:50]:  # Sample
        title = e.get('title', '')
        for m in e.get('markets', []):
            try:
                yes_bid = int(m.get('yes_bid', 0) or 0)
                yes_ask = int(m.get('yes_ask', 0) or 0)
                vol = int(m.get('volume', 0) or 0)
            except:
                continue
            
            if yes_bid > 0 and yes_ask > 0:
                spread = yes_ask - yes_bid
                mid = (yes_bid + yes_ask) / 2
                k_opps.append({
                    'title': title[:50],
                    'mid': mid,
                    'spread': spread,
                    'volume': vol
                })
    
    print('\n--- WIDE SPREADS (Liquidity Opportunities) ---')
    wide = sorted([o for o in k_opps if o['spread'] > 4], key=lambda x: x['spread'], reverse=True)[:6]
    for m in wide:
        print(f"  {m['title']}: Mid={m['mid']:.0f}c Spread={m['spread']}c Vol={m['volume']}")

# ACTIONABLE RECOMMENDATIONS
print('\n' + '='*70)
print('[3] ACTIONABLE RECOMMENDATIONS')
print('='*70)

if by_vol:
    print('\n  TOP PICK (by volume):', by_vol[0]['title'])
    print(f"    Price: {by_vol[0]['yes']:.1f}% YES | Vol: ${by_vol[0]['volume']:,.0f}")

if longshots:
    print('\n  LONGSHOT PICK:', longshots[0]['title'])
    print(f"    Price: {longshots[0]['yes']:.1f}% YES | Potential: {100/longshots[0]['yes']:.1f}x")

if volatile:
    print('\n  VOLATILE PLAY:', volatile[0]['title'])
    print(f"    Price: {volatile[0]['yes']:.1f}% (coin-flip territory)")

# Summary stats
print('\n' + '='*70)
print('[4] SUMMARY STATS')
print('='*70)
total_vol = sum(o['volume'] for o in opportunities)
total_liq = sum(o['liquidity'] for o in opportunities)
print(f"  Total markets analyzed: {len(opportunities)}")
print(f"  Total volume: ${total_vol:,.0f}")
print(f"  Total liquidity: ${total_liq:,.0f}")
print(f"  Longshot opportunities: {len([o for o in opportunities if 5 < o['yes'] < 15])}")
print(f"  High-certainty opportunities: {len([o for o in opportunities if o['yes'] > 85])}")
print(f"  Volatile (40-60%): {len([o for o in opportunities if 40 < o['yes'] < 60])}")

print('\n' + '='*70)
print('SCAN COMPLETE')
print('='*70)
