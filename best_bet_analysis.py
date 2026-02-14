import json

with open('active-markets.json', 'r') as f:
    data = json.load(f)

markets = data.get('markets', [])

print("=" * 70)
print("BEST BETS - DETAILED ANALYSIS")
print("=" * 70)

# Check deportation markets in detail
print("\n[DEPORTATION MARKETS] - Best liquidity, clear thesis")
print("-" * 70)
deportation = []
for m in markets:
    q = m.get('question', '')
    if 'deport' in q.lower() and '250' in q:
        prices_str = m.get('outcomePrices', '[]')
        try:
            prices = json.loads(prices_str)
            if len(prices) == 2:
                deportation.append({
                    'question': q,
                    'yes': float(prices[0]),
                    'no': float(prices[1]),
                    'volume': float(m.get('volume', 0)),
                    'volume_24h': float(m.get('volume24hr', 0)),
                    'updated': m.get('updatedAt', 'N/A')[:16]
                })
        except:
            pass

for d in deportation:
    print(f"\n{d['question']}")
    print(f"  YES: {d['yes']:.1%} | NO: {d['no']:.1%}")
    print(f"  Volume: ${d['volume']:,.0f} (24h: ${d['volume_24h']:,.0f})")

# Find Elon/Musk markets
print("\n[ELON MUSK MARKETS] - Event-driven opportunities")
print("-" * 70)
musk = []
for m in markets:
    q = m.get('question', '').lower()
    if 'elon' in q or 'musk' in q or 'doge' in q:
        prices_str = m.get('outcomePrices', '[]')
        try:
            prices = json.loads(prices_str)
            if len(prices) == 2:
                musk.append({
                    'question': m.get('question', 'N/A'),
                    'yes': float(prices[0]),
                    'volume': float(m.get('volume', 0)),
                    'end': m.get('endDate', 'N/A')[:10]
                })
        except:
            pass

for m in musk[:5]:
    print(f"\n{m['question']}")
    print(f"  YES: {m['yes']:.1%} | Volume: ${m['volume']:,.0f} | Ends: {m['end']}")

# Find high-ROI short-term opportunities
print("\n[SHORT-TERM OPPORTUNITIES] - Ending within 30 days")
print("-" * 70)
from datetime import datetime, timedelta

now = datetime.now()
short_term = []

for m in markets:
    end_str = m.get('endDate', '')
    try:
        end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00').replace('+00:00', ''))
        days_until = (end_date - now).days
        
        if 0 < days_until <= 30:
            prices_str = m.get('outcomePrices', '[]')
            prices = json.loads(prices_str)
            if len(prices) == 2:
                yes = float(prices[0])
                volume = float(m.get('volume', 0))
                if volume > 50000:  # Minimum liquidity
                    short_term.append({
                        'question': m.get('question', 'N/A'),
                        'yes': yes,
                        'days': days_until,
                        'volume': volume
                    })
    except:
        pass

short_term.sort(key=lambda x: x['days'])
for st in short_term[:5]:
    print(f"\n{st['question'][:60]}...")
    print(f"  YES: {st['yes']:.1%} | {st['days']} days left | ${st['volume']:,.0f}")

# RECOMMENDATION
print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print("""
Based on current prices and validated strategies:

[BEST BET] Trump 250-500k deportations YES at 87%
- Highest volume deportation market ($3.8M)
- Historical baseline (271k in 2024) supports this range
- Market consensus strong at 87%
- Risk: Overpriced at 87%, limited upside

[VALUE PLAY] Trump 500-750k deportations YES at 1.4%
- Extreme longshot pricing
- If deportations exceed 500k due to policy shift, massive upside
- Historical precedent doesn't support it, but political uncertainty exists
- Risk: Very low probability, could go to 0

[AVOID] NBA Finals longshots at 0.15%
- Strategy says fade these, but they pay NOTHING on NO
- Tied up capital for months

With $10 capital and 2% risk rule: $0.20 max per trade
Not much to work with until you deposit more.
""")
