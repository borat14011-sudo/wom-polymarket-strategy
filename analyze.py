import json
from datetime import datetime

with open('active-markets.json', 'r', encoding='utf-8') as f:
    pm_markets = json.load(f)

with open('kalshi_analysis.json', 'r', encoding='utf-8') as f:
    kalshi_data = json.load(f)

print('=' * 60)
print('CROSS-PLATFORM MARKET ANALYSIS')
print('Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print('=' * 60)

print('\n[POLYMARKET SUMMARY]')
print('Total markets:', len(pm_markets))

pm_sorted = sorted(pm_markets, key=lambda x: float(x.get('volumeNum', 0) or 0), reverse=True)

print('\n[TOP 10 MARKETS BY VOLUME]')
for i, m in enumerate(pm_sorted[:10], 1):
    try:
        prices = json.loads(m.get('outcomePrices', '["0","0"]'))
        yes_price = float(prices[0]) if prices else 0
        vol = float(m.get('volumeNum', 0) or 0)
        vol_24h = float(m.get('volume24hr', 0) or 0)
        q = m.get('question', 'Unknown')[:55]
        print(f'  {i}. {q}...')
        print(f'     YES: {yes_price:.1%} | Vol: ${vol/1000000:.1f}M | 24h: ${vol_24h/1000:.0f}K')
    except Exception as e:
        pass

print('\n[RECENT MOVERS - High 24h Volume]')
movers = sorted(pm_markets, key=lambda x: float(x.get('volume24hr', 0) or 0), reverse=True)[:8]
for m in movers:
    try:
        prices = json.loads(m.get('outcomePrices', '["0","0"]'))
        yes_price = float(prices[0]) if prices else 0
        vol_24h = float(m.get('volume24hr', 0) or 0)
        q = m.get('question', 'Unknown')[:50]
        print(f'  * {q}... @ {yes_price:.1%} | 24h: ${vol_24h/1000:.0f}K')
    except Exception as e:
        pass

print('\n[BUY THE DIP - Low price, high volume]')
dip_candidates = []
for m in pm_markets:
    try:
        if not m.get('outcomePrices'): continue
        prices = json.loads(m['outcomePrices'])
        yes_price = float(prices[0])
        vol = float(m.get('volumeNum', 0) or 0)
        liq = float(m.get('liquidityNum', 0) or 0)
        if 0.05 <= yes_price <= 0.20 and vol > 50000 and liq > 5000:
            dip_candidates.append({'q': m['question'], 'p': yes_price, 'v': vol, 'l': liq})
    except Exception as e:
        pass

dip_candidates.sort(key=lambda x: x['v'], reverse=True)
for d in dip_candidates[:6]:
    print(f'  * {d["q"][:50]}...')
    print(f'    YES: {d["p"]:.1%} | Vol: ${d["v"]/1000:.0f}K | Liq: ${d["l"]/1000:.1f}K')

print('\n[KALSHI SUMMARY]')
print('Markets:', kalshi_data['summary']['total_markets'])

# Save to file
results = {
    'timestamp': datetime.now().isoformat(),
    'pm_count': len(pm_markets),
    'kalshi_count': kalshi_data['summary']['total_markets'],
    'top_movers': [m['question'][:60] for m in movers[:5]],
    'dips': [{'q': d['q'][:60], 'price': d['p'], 'volume': d['v']} for d in dip_candidates[:5]]
}
with open('research_market_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)
print('\nSaved to research_market_analysis.json')
