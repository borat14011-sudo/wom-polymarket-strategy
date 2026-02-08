"""
Find opportunities for VALIDATED strategies ONLY
BTC_TIME_BIAS (58.8%) and WEATHER_FADE (85.1%)
"""
import requests
import json
import re
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com/markets"

print("="*80)
print("FINDING VALIDATED STRATEGY OPPORTUNITIES")
print("="*80)

# Fetch active markets
params = {
    'limit': 500,
    'active': 'true',
    'closed': 'false',
    'order': 'volume24hr',
    'ascending': 'false'
}

resp = requests.get(GAMMA_API, params=params, timeout=15)
markets = resp.json()

print(f"\n[OK] Fetched {len(markets)} active markets")

# Strategy 1: BTC_TIME_BIAS
# Look for "Bitcoin up or down" markets
btc_updown_markets = []

for m in markets:
    question = m.get('question', m.get('title', ''))
    
    if re.search(r'bitcoin.*up.*down', question, re.I) or re.search(r'btc.*higher.*lower', question, re.I):
        outcome_prices = m.get('outcomePrices', ['0.5', '0.5'])
        if isinstance(outcome_prices, str):
            try:
                outcome_prices = json.loads(outcome_prices)
            except:
                outcome_prices = ['0.5', '0.5']
        
        try:
            price = float(outcome_prices[0])
        except:
            price = 0.5
        
        btc_updown_markets.append({
            'question': question,
            'price': price,
            'volume': m.get('volume', 0),
            'end_date': m.get('end_date_iso', 'Unknown')
        })

print(f"\n[BTC_TIME_BIAS] Found {len(btc_updown_markets)} Bitcoin up/down markets")

if btc_updown_markets:
    btc_updown_markets.sort(key=lambda x: float(x['volume']) if x['volume'] else 0, reverse=True)
    
    print(f"\nTop 5 by volume:")
    for i, m in enumerate(btc_updown_markets[:5], 1):
        vol = float(m['volume']) if m['volume'] else 0
        print(f"\n  {i}. {m['question'][:70]}")
        print(f"     Price: {m['price']:.3f} | Volume: ${vol/1000:.0f}K")
        print(f"     End: {m['end_date'][:10]}")

# Strategy 2: WEATHER_FADE_LONGSHOTS
# Look for temperature/weather markets priced <30%
weather_markets = []

for m in markets:
    question = m.get('question', m.get('title', ''))
    
    if re.search(r'\btemperature\b|\bweather\b|\bdegrees\b', question, re.I):
        outcome_prices = m.get('outcomePrices', ['0.5', '0.5'])
        if isinstance(outcome_prices, str):
            try:
                outcome_prices = json.loads(outcome_prices)
            except:
                outcome_prices = ['0.5', '0.5']
        
        try:
            price = float(outcome_prices[0])
        except:
            price = 0.5
        
        if price < 0.30:  # Longshot threshold
            weather_markets.append({
                'question': question,
                'price': price,
                'volume': m.get('volume', 0),
                'end_date': m.get('end_date_iso', 'Unknown')
            })

print(f"\n[WEATHER_FADE_LONGSHOTS] Found {len(weather_markets)} weather longshots (<30%)")

if weather_markets:
    weather_markets.sort(key=lambda x: float(x['volume']) if x['volume'] else 0, reverse=True)
    
    print(f"\nTop 5 by volume:")
    for i, m in enumerate(weather_markets[:5], 1):
        vol = float(m['volume']) if m['volume'] else 0
        print(f"\n  {i}. {m['question'][:70]}")
        print(f"     Price: {m['price']:.3f} (Bet NO)")
        print(f"     Volume: ${vol/1000:.0f}K")
        print(f"     End: {m['end_date'][:10]}")
        print(f"     Expected win: 85.1%")

# Summary
print(f"\n{'='*80}")
print("SUMMARY")
print('='*80)
print(f"  BTC_TIME_BIAS markets: {len(btc_updown_markets)}")
print(f"  WEATHER_FADE markets: {len(weather_markets)}")
print(f"  Total validated opportunities: {len(btc_updown_markets) + len(weather_markets)}")

# Save
with open('validated_opportunities.json', 'w') as f:
    json.dump({
        'btc_time_bias': btc_updown_markets,
        'weather_fade': weather_markets,
        'timestamp': datetime.now().isoformat()
    }, f, indent=2)

print(f"\n[SAVED] validated_opportunities.json")
