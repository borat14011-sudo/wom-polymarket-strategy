import json
from datetime import datetime, timezone

with open('kalshi_markets_raw.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

now = datetime.now(timezone.utc)

print("=" * 80)
print("EDGE HUNTER DEEP ANALYSIS - Feb 12, 2026")
print("=" * 80)

# 1. SUPERVOLCANO ANALYSIS
print("\n### EDGE #1: SUPERVOLCANO MISPRICING ###")
supervolcano = [m for m in data if 'ERUPTSUPER' in m.get('ticker_name', '')]
for m in supervolcano:
    bid = m['yes_bid']
    ask = m['yes_ask']
    print(f"Market: {m['title']}")
    print(f"  Bid: {bid}¢ | Ask: {ask}¢ | Mid: {(bid+ask)/2:.1f}¢")
    print(f"  Volume: {m['volume']:,} | Open Interest: {m['open_interest']:,}")
    
    # Base rate analysis
    # Supervolcano eruptions happen roughly once every 50,000-100,000 years
    # By 2050 that's ~24 years, probability ~0.024% to 0.048%
    base_rate_annual = 0.001  # Being generous: 0.1% per year
    years_to_2050 = 24
    expected_prob = base_rate_annual * years_to_2050  # ~2.4%
    
    print(f"\n  BASE RATE ANALYSIS:")
    print(f"    - Historical frequency: ~1 per 50,000-100,000 years")
    print(f"    - Annual probability: ~0.001% to 0.002%")
    print(f"    - 24-year probability: ~0.02% to 0.05%")
    print(f"    - Market implied: {bid}% to {ask}%")
    print(f"    - OVERPRICED BY: ~{(bid/0.05):.0f}x to ~{(bid/0.02):.0f}x")
    print(f"\n  [EDGE]: SELL NO contracts (or short YES) for ~87-93c")
    print(f"  [RISK]: Black swan definition - low prob, catastrophic if wrong")

# 2. POPE MARKET ARBITRAGE
print("\n\n### EDGE #2: POPE MARKET ANALYSIS ###")
pope_70 = [m for m in data if 'KXNEWPOPE-70' in m.get('ticker_name', '')]
pope_35 = [m for m in data if 'KXNEXTPOPE-35' in m.get('ticker_name', '')]

print("\nKXNEWPOPE-70 (Active - expires 2070):")
total_implied = 0
for m in sorted(pope_70, key=lambda x: -x['yes_bid']):
    print(f"  {m['name'][:25]:25s} | Bid: {m['yes_bid']:2d}¢ | Ask: {m['yes_ask']:2d}¢ | Weekly: {m.get('weekly_change_pct', 0):+.1f}%")
    total_implied += m['yes_bid']
print(f"  TOTAL IMPLIED (bids): {total_implied}%")
print(f"  [EDGE]: If total > 100% or < 100%, arbitrage exists")

# Check for big weekly drops that might be oversold
dips = [m for m in pope_70 if (m.get('weekly_change_pct', 0) or 0) < -30]
if dips:
    print("\n  OVERSOLD CANDIDATES (dropped >30% this week):")
    for m in dips:
        print(f"    {m['name']}: {m.get('weekly_change_pct', 0):+.1f}% - POTENTIAL REVERSION")

# 3. POLITICAL SUCCESSION MARKETS
print("\n\n### EDGE #3: SUCCESSION MARKET INEFFICIENCIES ###")
xi_markets = [m for m in data if 'XISUCCESSOR' in m.get('ticker_name', '')]
total_xi = sum(m['yes_bid'] for m in xi_markets)
print(f"Xi Successor markets - Total implied (bids): {total_xi}%")
if total_xi != 100:
    print(f"  [EDGE]: Gap from 100%: {100 - total_xi}% - Possible 'Other' value or mispricing")

# 4. TIME DECAY PATTERNS  
print("\n\n### EDGE #4: TIME DECAY ANALYSIS ###")
print("Markets with long time horizons trading at extreme prices:")

long_term_extremes = []
for m in data:
    close_date = m.get('close_date', '')
    if '2045' in close_date or '2050' in close_date or '2070' in close_date or '2099' in close_date:
        bid = m['yes_bid']
        if bid >= 85 or bid <= 15:
            long_term_extremes.append(m)

for m in sorted(long_term_extremes, key=lambda x: x['yes_bid'])[:10]:
    print(f"  {m['ticker_name'][:35]:35s} | Bid: {m['yes_bid']:2d}¢ | Closes: {m['close_date'][:10]}")

# 5. MOMENTUM / REVERSION OPPORTUNITIES
print("\n\n### EDGE #5: MEAN REVERSION CANDIDATES ###")
print("Markets that dropped heavily but have high volume (potential overreaction):")

reversion = []
for m in data:
    weekly = m.get('weekly_change_pct', 0) or 0
    vol = m.get('volume', 0)
    if weekly < -40 and vol > 5000 and m['yes_bid'] > 5:  # Not dead markets
        reversion.append(m)

for m in sorted(reversion, key=lambda x: x.get('weekly_change_pct', 0))[:10]:
    print(f"  {m['ticker_name'][:35]:35s} | Bid: {m['yes_bid']:2d}¢ | Weekly: {m.get('weekly_change_pct', 0):+.1f}% | Vol: {m['volume']:,}")

# 6. CATEGORY-SPECIFIC BIASES
print("\n\n### EDGE #6: CATEGORY PATTERNS ###")
categories = {}
for m in data:
    cat = m.get('category', 'Unknown')
    if cat not in categories:
        categories[cat] = {'count': 0, 'total_bid': 0, 'avg_spread': 0}
    categories[cat]['count'] += 1
    categories[cat]['total_bid'] += m['yes_bid']
    spread = m['yes_ask'] - m['yes_bid'] if m['yes_ask'] and m['yes_bid'] else 0
    categories[cat]['avg_spread'] += spread

print("Category analysis (avg bid suggests optimism/pessimism bias):")
for cat, stats in sorted(categories.items(), key=lambda x: -x[1]['count']):
    avg_bid = stats['total_bid'] / stats['count'] if stats['count'] else 0
    avg_spread = stats['avg_spread'] / stats['count'] if stats['count'] else 0
    print(f"  {cat:25s} | n={stats['count']:3d} | Avg Bid: {avg_bid:5.1f}¢ | Avg Spread: {avg_spread:.1f}¢")

# 7. LIQUIDITY GAPS
print("\n\n### EDGE #7: HIGH VOLUME / WIDE SPREAD (Liquidity Provider Opportunity) ###")
lp_opps = []
for m in data:
    vol = m.get('volume', 0)
    spread = (m.get('yes_ask', 0) or 0) - (m.get('yes_bid', 0) or 0)
    if vol > 20000 and spread > 5:
        lp_opps.append({**m, 'spread': spread})

for m in sorted(lp_opps, key=lambda x: -x['spread'])[:10]:
    print(f"  {m['ticker_name'][:40]:40s} | Spread: {m['spread']:2d}¢ | Vol: {m['volume']:>10,}")

print("\n" + "=" * 80)
print("END ANALYSIS")
print("=" * 80)
