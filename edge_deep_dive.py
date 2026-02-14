import json
from datetime import datetime, timezone
from collections import defaultdict

with open('kalshi_markets_raw.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

print("=" * 80)
print("DEEP EDGE ANALYSIS - Cross-Market Patterns")
print("=" * 80)

# 1. LOOK FOR ARBITRAGE IN MULTI-OUTCOME MARKETS
print("\n### MULTI-OUTCOME MARKET ARBITRAGE ###")

# Group by event_title
events = defaultdict(list)
for m in data:
    events[m.get('event_title', 'Unknown')].append(m)

for event, markets in events.items():
    if len(markets) > 2:  # Multi-outcome event
        total_bid = sum(m['yes_bid'] for m in markets)
        total_ask = sum(m['yes_ask'] for m in markets)
        if total_bid < 85 or total_bid > 115:  # Significant deviation from 100%
            print(f"\n{event[:60]}:")
            print(f"  Total Bid: {total_bid}% | Total Ask: {total_ask}%")
            if total_bid < 85:
                print(f"  [EDGE] UNDERPRICED: Buy all outcomes, guaranteed {100-total_ask}c profit if ask < 100")
            if total_bid > 115:
                print(f"  [EDGE] OVERPRICED: Sell all outcomes, collect {total_bid-100}c")
            for m in sorted(markets, key=lambda x: -x['yes_bid'])[:5]:
                print(f"    - {m['name'][:30]:30s}: {m['yes_bid']:2d}c bid / {m['yes_ask']:2d}c ask")

# 2. TIME VALUE ANALYSIS - Early Resolution Opportunities
print("\n\n### TIME VALUE: EARLY RESOLUTION OPPORTUNITIES ###")
print("Markets that could resolve BEFORE deadline (capture time premium):")

early_resolve = []
for m in data:
    # Markets with high probability and long time horizons
    if m['yes_bid'] >= 80 and '2030' in m.get('close_date', ''):
        early_resolve.append(m)
    if m['yes_bid'] >= 85 and '2045' in m.get('close_date', ''):
        early_resolve.append(m)

for m in sorted(early_resolve, key=lambda x: -x['yes_bid'])[:10]:
    print(f"  {m['ticker_name'][:40]:40s} | Bid: {m['yes_bid']:2d}c | Closes: {m['close_date'][:10]}")

# 3. VOLATILITY CLUSTERING - Find markets moving together
print("\n\n### VOLATILITY PATTERNS ###")
print("Markets with unusual weekly moves (potential correlation or catalyst):")

volatile_by_cat = defaultdict(list)
for m in data:
    weekly = abs(m.get('weekly_change_pct', 0) or 0)
    if weekly > 20:
        volatile_by_cat[m.get('category', 'Unknown')].append(m)

for cat, markets in sorted(volatile_by_cat.items(), key=lambda x: -len(x[1])):
    if len(markets) >= 2:
        print(f"\n{cat} ({len(markets)} volatile markets):")
        for m in sorted(markets, key=lambda x: abs(x.get('weekly_change_pct', 0) or 0), reverse=True)[:5]:
            print(f"  {m['ticker_name'][:35]:35s} | Weekly: {m.get('weekly_change_pct', 0):+.1f}%")

# 4. CONTRARIAN OPPORTUNITIES - Extreme moves that might revert
print("\n\n### CONTRARIAN: EXTREME MOVES (Potential Reversion) ###")

contrarian = []
for m in data:
    weekly = m.get('weekly_change_pct', 0) or 0
    vol = m.get('volume', 0)
    bid = m['yes_bid']
    # Large drop but still has value, high volume = real price discovery
    if weekly < -25 and bid >= 5 and vol > 5000:
        contrarian.append(m)
    # Large spike on low volume = potential manipulation to fade
    if weekly > 50 and vol < 2000 and bid < 30:
        contrarian.append(m)

for m in sorted(contrarian, key=lambda x: x.get('weekly_change_pct', 0))[:10]:
    label = "OVERSOLD" if m.get('weekly_change_pct', 0) < 0 else "OVERBOUGHT"
    print(f"  [{label}] {m['ticker_name'][:35]:35s} | Bid: {m['yes_bid']:2d}c | Weekly: {m.get('weekly_change_pct', 0):+.1f}% | Vol: {m['volume']:,}")

# 5. SPREAD EXPLOITATION - Market Making Opportunities
print("\n\n### SPREAD EXPLOITATION (Market Making Potential) ###")
print("High volume markets with wide spreads = profit from providing liquidity:")

mm_opps = []
for m in data:
    spread = (m.get('yes_ask', 0) or 0) - (m.get('yes_bid', 0) or 0)
    vol = m.get('volume', 0)
    oi = m.get('open_interest', 0)
    if spread >= 4 and vol > 10000:
        mm_opps.append({**m, 'spread': spread, 'spread_pct': spread / max(m['yes_ask'], 1) * 100})

for m in sorted(mm_opps, key=lambda x: -x['volume'])[:10]:
    print(f"  {m['ticker_name'][:40]:40s} | Spread: {m['spread']:2d}c ({m['spread_pct']:.1f}%) | Vol: {m['volume']:>10,}")

# 6. CORRELATION ARBITRAGE - Related markets that should move together
print("\n\n### CORRELATION ANALYSIS ###")
print("Markets that SHOULD be correlated but show divergence:")

# Elon Musk related markets
elon_markets = [m for m in data if 'elon' in m.get('ticker_name', '').lower() or 'musk' in m.get('title', '').lower()]
print(f"\nElon Musk markets ({len(elon_markets)}):")
for m in sorted(elon_markets, key=lambda x: -x['yes_bid'])[:5]:
    print(f"  {m['ticker_name'][:40]:40s} | Bid: {m['yes_bid']:2d}c | Weekly: {m.get('weekly_change_pct', 0):+.1f}%")

# Trump related markets
trump_markets = [m for m in data if 'trump' in m.get('ticker_name', '').lower() or 'trump' in m.get('title', '').lower()]
print(f"\nTrump-related markets ({len(trump_markets)}):")
for m in sorted(trump_markets, key=lambda x: -x['yes_bid'])[:5]:
    print(f"  {m['ticker_name'][:40]:40s} | Bid: {m['yes_bid']:2d}c | Weekly: {m.get('weekly_change_pct', 0):+.1f}%")

# 7. CALENDAR EFFECTS
print("\n\n### CALENDAR EFFECT OPPORTUNITIES ###")
print("Markets with resolution dates that create predictable patterns:")

q1_2026 = [m for m in data if '2026-03' in m.get('close_date', '') or '2026-04' in m.get('close_date', '')]
print(f"\nResolving Q1-Q2 2026 ({len(q1_2026)} markets):")
for m in sorted(q1_2026, key=lambda x: -x['volume'])[:5]:
    print(f"  {m['ticker_name'][:40]:40s} | Bid: {m['yes_bid']:2d}c | Closes: {m['close_date'][:10]}")

# 8. HIDDEN VALUE - Markets at 0c bid that might not be dead
print("\n\n### HIDDEN VALUE: 0c BID MARKETS ###")
print("Markets trading at 0c but with high historical volume (zombie markets with potential):")

zombies = [m for m in data if m['yes_bid'] == 0 and m.get('volume', 0) > 50000]
for m in sorted(zombies, key=lambda x: -x['volume'])[:10]:
    print(f"  {m['ticker_name'][:40]:40s} | Ask: {m['yes_ask']:2d}c | Vol: {m['volume']:>10,} | OI: {m.get('open_interest', 0):,}")

print("\n" + "=" * 80)
