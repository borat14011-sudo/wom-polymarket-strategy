import json
from datetime import datetime

# Load fresh market data
with open('active-markets.json', 'r') as f:
    data = json.load(f)

markets = data.get('markets', [])
fetch_time = data.get('fetch_timestamp', 'N/A')

print("=" * 70)
print("LIVE OPPORTUNITY SCAN")
print(f"Data fetched: {fetch_time}")
print("=" * 70)

opportunities = []

# Strategy 1: WEATHER_FADE_LONGSHOTS - Find extreme longshots (>95% NO)
print("\n[STRATEGY] WEATHER_FADE_LONGSHOTS - Extreme Longshots")
print("-" * 70)
longshots = []
for m in markets:
    prices_str = m.get('outcomePrices', '[]')
    try:
        prices = json.loads(prices_str)
        if len(prices) == 2:
            yes_price = float(prices[0])
            no_price = float(prices[1])
            volume = float(m.get('volume', 0))
            
            # Look for YES < 5% (extreme longshot)
            if yes_price < 0.05 and volume > 100000:
                longshots.append({
                    'question': m.get('question', 'N/A'),
                    'yes_price': yes_price,
                    'no_price': no_price,
                    'volume': volume,
                    'end_date': m.get('endDate', 'N/A')[:10]
                })
    except:
        pass

# Sort by volume
longshots.sort(key=lambda x: x['volume'], reverse=True)
for ls in longshots[:5]:
    print(f"\n  {ls['question'][:60]}...")
    print(f"    YES: {ls['yes_price']:.3f} | Volume: ${ls['volume']:,.0f}")
    print(f"    Ends: {ls['end_date']}")

# Strategy 2: BTC_TIME_BIAS - Time-based crypto patterns
print("\n[STRATEGY] BTC_TIME_BIAS - Crypto/Macro Timing")
print("-" * 70)
crypto_markets = []
for m in markets:
    q = m.get('question', '').lower()
    if any(k in q for k in ['bitcoin', 'btc', 'crypto', 'microstrategy', 'mstr']):
        prices_str = m.get('outcomePrices', '[]')
        try:
            prices = json.loads(prices_str)
            if len(prices) == 2:
                yes_price = float(prices[0])
                volume = float(m.get('volume', 0))
                crypto_markets.append({
                    'question': m.get('question', 'N/A'),
                    'yes_price': yes_price,
                    'volume': volume,
                    'end_date': m.get('endDate', 'N/A')[:10]
                })
        except:
            pass

crypto_markets.sort(key=lambda x: x['volume'], reverse=True)
for cm in crypto_markets[:5]:
    print(f"\n  {cm['question'][:60]}...")
    print(f"    YES: {cm['yes_price']:.3f} | Volume: ${cm['volume']:,.0f}")

# Strategy 3: High volume, reasonable odds (70-90% YES)
print("\n[STRATEGY] High-Confidence YES (70-90% range)")
print("-" * 70)
high_conf = []
for m in markets:
    prices_str = m.get('outcomePrices', '[]')
    try:
        prices = json.loads(prices_str)
        if len(prices) == 2:
            yes_price = float(prices[0])
            volume = float(m.get('volume', 0))
            
            if 0.70 <= yes_price <= 0.90 and volume > 500000:
                high_conf.append({
                    'question': m.get('question', 'N/A'),
                    'yes_price': yes_price,
                    'volume': volume,
                    'end_date': m.get('endDate', 'N/A')[:10]
                })
    except:
        pass

high_conf.sort(key=lambda x: x['volume'], reverse=True)
for hc in high_conf[:5]:
    print(f"\n  {hc['question'][:60]}...")
    print(f"    YES: {hc['yes_price']:.2f} | Volume: ${hc['volume']:,.0f}")
    print(f"    Ends: {hc['end_date']}")

# Top opportunities overall
print("\n" + "=" * 70)
print("TOP OPPORTUNITIES SUMMARY")
print("=" * 70)

print("\n1. HIGHEST VOLUME MARKETS:")
top_volume = sorted(markets, key=lambda x: float(x.get('volume', 0)), reverse=True)[:3]
for m in top_volume:
    q = m.get('question', 'N/A')
    vol = float(m.get('volume', 0))
    prices = m.get('outcomePrices', 'N/A')
    print(f"   ${vol:,.0f} - {q[:50]}...")
    print(f"   Prices: {prices}")
