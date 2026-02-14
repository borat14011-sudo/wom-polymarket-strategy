import json
import requests
from collections import defaultdict
from datetime import datetime

API_BASE = "https://api.elections.kalshi.com/trade-api/v2"

print("=" * 80)
print("KALSHI MARKET SCANNER - Comprehensive Analysis")
print("=" * 80)

# Get all series to understand categories
print("\n[1/4] Fetching series (categories)...")
series_resp = requests.get(f"{API_BASE}/series?limit=200")
series_data = series_resp.json()
series_list = series_data.get('series', [])

categories = defaultdict(list)
for s in series_list:
    cat = s.get('category', 'Unknown')
    categories[cat].append(s)

print(f"Found {len(series_list)} series across {len(categories)} categories:")
for cat, series in sorted(categories.items()):
    print(f"  - {cat}: {len(series)} series")

# Get high-volume markets by fetching with different parameters
print("\n[2/4] Fetching open markets...")
all_markets = []
cursor = None

for i in range(3):  # Fetch multiple pages
    url = f"{API_BASE}/markets?limit=200&status=open"
    if cursor:
        url += f"&cursor={cursor}"
    
    resp = requests.get(url)
    data = resp.json()
    markets = data.get('markets', [])
    all_markets.extend(markets)
    cursor = data.get('cursor')
    
    print(f"  Page {i+1}: {len(markets)} markets")
    
    if not cursor:
        break

print(f"\nTotal markets fetched: {len(all_markets)}")

# Analyze markets
market_analysis = []
high_volume = []
dip_opportunities = []
liquid_markets = []

for m in all_markets:
    ticker = m.get('ticker', '')
    title = m.get('title', '')
    volume_24h = int(m.get('volume_24h', 0))
    volume_total = int(m.get('volume', 0))
    last_price = float(str(m.get('last_price_dollars', '0')).replace('$', ''))
    previous_price = float(str(m.get('previous_price_dollars', '0')).replace('$', ''))
    yes_bid = float(str(m.get('yes_bid_dollars', '0')).replace('$', ''))
    yes_ask = float(str(m.get('yes_ask_dollars', '0')).replace('$', ''))
    liquidity = float(str(m.get('liquidity_dollars', '0')).replace('$', ''))
    open_interest = float(m.get('open_interest_fp', '0'))
    
    # Price change
    price_change_pct = 0
    if previous_price > 0 and last_price > 0:
        price_change_pct = ((last_price - previous_price) / previous_price) * 100
    
    # Categorize by ticker pattern
    category = 'other'
    if any(x in ticker for x in ['NBA', 'NFL', 'MLB', 'NHL', 'NCAA', 'MVE']):
        category = 'sports'
    elif any(x in ticker for x in ['PRES', 'SENATE', 'CONGRESS', 'ELECT', 'TRUMP', 'ADMIN', 'DEEPSEEK']):
        category = 'politics'
    elif any(x in ticker for x in ['BTC', 'ETH', 'BCH', 'CRYPTO', 'COIN']):
        category = 'crypto'
    elif any(x in ticker for x in ['FED', 'INRATE', 'CPI', 'GDP', 'UNEMP', 'INFLATION']):
        category = 'economics'
    elif any(x in ticker for x in ['TEMP', 'PRECIP', 'SNOW', 'WEATHER']):
        category = 'weather'
    
    market_info = {
        'ticker': ticker,
        'title': title[:80],
        'category': category,
        'volume_24h': volume_24h,
        'volume_total': volume_total,
        'last_price': last_price,
        'previous_price': previous_price,
        'price_change_pct': price_change_pct,
        'yes_bid': yes_bid,
        'yes_ask': yes_ask,
        'spread': yes_ask - yes_bid if yes_ask > 0 and yes_bid > 0 else 0,
        'liquidity': liquidity,
        'open_interest': open_interest
    }
    
    market_analysis.append(market_info)
    
    # High volume filter
    if volume_24h > 1000:
        high_volume.append(market_info)
    
    # Buy the Dip filter (price dropped >10%, good volume)
    if price_change_pct < -10 and volume_24h > 100:
        dip_opportunities.append(market_info)
    
    # High liquidity filter
    if liquidity > 10:
        liquid_markets.append(market_info)

# Sort
high_volume.sort(key=lambda x: x['volume_24h'], reverse=True)
dip_opportunities.sort(key=lambda x: x['price_change_pct'])
liquid_markets.sort(key=lambda x: x['liquidity'], reverse=True)

# Category summary
print("\n[3/4] Market Analysis by Category:")
category_summary = defaultdict(lambda: {'count': 0, 'total_volume': 0})
for m in market_analysis:
    cat = m['category']
    category_summary[cat]['count'] += 1
    category_summary[cat]['total_volume'] += m['volume_24h']

for cat in sorted(category_summary.keys()):
    info = category_summary[cat]
    print(f"  {cat:15s}: {info['count']:4d} markets | ${info['total_volume']:>10,.0f} 24h vol")

# Reports
print("\n[4/4] Generating reports...")

print(f"\n{'='*80}")
print("HIGH VOLUME MARKETS (>$1,000 in 24h)")
print(f"{'='*80}")
if high_volume:
    for i, m in enumerate(high_volume[:20], 1):
        print(f"{i:2d}. [{m['category']:8s}] ${m['volume_24h']:>8,} vol | ${m['last_price']:.2f} | {m['title']}")
else:
    print("No markets found with >$1,000 24h volume")
    print("\nShowing markets with ANY volume:")
    any_volume = [m for m in market_analysis if m['volume_24h'] > 0]
    any_volume.sort(key=lambda x: x['volume_24h'], reverse=True)
    for i, m in enumerate(any_volume[:10], 1):
        print(f"{i:2d}. [{m['category']:8s}] ${m['volume_24h']:>8,} vol | ${m['last_price']:.2f} | {m['title']}")

print(f"\n{'='*80}")
print("BUY THE DIP OPPORTUNITIES (Price dropped >10%, volume >$100)")
print(f"{'='*80}")
if dip_opportunities:
    for i, m in enumerate(dip_opportunities[:15], 1):
        print(f"{i:2d}. [{m['category']:8s}] {m['price_change_pct']:>6.1f}% drop | ${m['volume_24h']:>6,} vol | ${m['last_price']:.3f} price")
        print(f"    {m['title']}")
else:
    print("No BUY THE DIP opportunities found with current criteria")
    print("\nLowering threshold: Any price drops with volume >$10:")
    any_drops = [m for m in market_analysis if m['price_change_pct'] < 0 and m['volume_24h'] > 10]
    any_drops.sort(key=lambda x: x['price_change_pct'])
    if any_drops:
        for i, m in enumerate(any_drops[:10], 1):
            print(f"{i:2d}. [{m['category']:8s}] {m['price_change_pct']:>6.1f}% drop | ${m['volume_24h']:>6,} vol | ${m['last_price']:.3f} price")
            print(f"    {m['title']}")
    else:
        print("No price history available in current market snapshot")

print(f"\n{'='*80}")
print("HIGH LIQUIDITY MARKETS (>$10)")
print(f"{'='*80}")
for i, m in enumerate(liquid_markets[:20], 1):
    print(f"{i:2d}. [{m['category']:8s}] ${m['liquidity']:>8.2f} liq | ${m['volume_24h']:>6,} vol | ${m['last_price']:.2f}")
    print(f"    {m['title']}")

print(f"\n{'='*80}")
print("NON-SPORTS MARKETS (Politics, Crypto, Economics)")
print(f"{'='*80}")
non_sports = [m for m in market_analysis if m['category'] not in ['sports', 'other']]
non_sports.sort(key=lambda x: x['volume_24h'], reverse=True)
if non_sports:
    for i, m in enumerate(non_sports[:25], 1):
        print(f"{i:2d}. [{m['category']:8s}] ${m['volume_24h']:>6,} vol | ${m['last_price']:.3f} | {m['title']}")
else:
    print("No non-sports markets found in current snapshot")
    print("Note: API may be returning mostly sports markets. Try different query parameters or time.")

# Save comprehensive report
output_data = {
    'scan_time': datetime.now().isoformat(),
    'summary': {
        'total_markets': len(all_markets),
        'categories': dict(category_summary),
        'high_volume_count': len(high_volume),
        'dip_opportunities_count': len(dip_opportunities),
        'liquid_markets_count': len(liquid_markets)
    },
    'series_categories': {cat: len(series) for cat, series in categories.items()},
    'high_volume_markets': high_volume[:30],
    'dip_opportunities': dip_opportunities[:20] if dip_opportunities else any_drops[:20] if 'any_drops' in locals() else [],
    'liquid_markets': liquid_markets[:30],
    'non_sports_markets': non_sports[:50]
}

with open('kalshi_scan_results.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\nFull results saved to kalshi_scan_results.json")
