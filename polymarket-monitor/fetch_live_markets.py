"""
Fetch LIVE active markets from Polymarket API RIGHT NOW
Find real-time betting opportunities
"""
import requests
import json
import re
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com/markets"

print("="*80)
print("FETCHING LIVE MARKETS FROM POLYMARKET")
print("="*80)

# Fetch active markets
print("\n[FETCH] Getting active markets from Polymarket...")

params = {
    'limit': 500,
    'active': 'true',
    'closed': 'false',
    'order': 'volume24hr',  # Sort by volume
    'ascending': 'false'
}

try:
    resp = requests.get(GAMMA_API, params=params, timeout=15)
    resp.raise_for_status()
    markets = resp.json()
    
    print(f"[OK] Fetched {len(markets)} active markets")
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

# Apply our strategies to find opportunities
STRATEGIES = {
    'MUSK_FADE_EXTREMES': {
        'pattern': r'musk.*tweet',
        'check': lambda q: bool(re.search(r'(\d+)-(\d+)\s+tweets', q, re.I)) and check_extreme(q),
        'expected_win': 97.1
    },
    'WEATHER_FADE_LONGSHOTS': {
        'pattern': r'\btemperature\b|\bweather\b',
        'check': lambda q: True,  # Check price later
        'expected_win': 93.9
    },
    'ALTCOIN_FADE_HIGH': {
        'pattern': r'\bsolana\b|\bxrp\b|\bcardano\b',
        'check': lambda q: True,  # Check price later
        'expected_win': 92.3
    },
    'CRYPTO_FAVORITE_FADE': {
        'pattern': r'\bbitcoin\b.*\$\d+',
        'check': lambda q: True,  # Check price later
        'expected_win': 61.9
    }
}

def check_extreme(question):
    """Check if Musk tweet range is extreme"""
    match = re.search(r'(\d+)-(\d+)\s+tweets', question, re.I)
    if not match:
        return False
    low = int(match.group(1))
    high = int(match.group(2))
    return low < 40 or high > 200

# Find opportunities
print("\n[SCAN] Scanning for strategy matches...")

opportunities = []

for market in markets:
    question = market.get('question', market.get('title', ''))
    volume = market.get('volume', 0)
    liquidity = market.get('liquidity', 0)
    end_date = market.get('end_date_iso', market.get('endDate'))
    
    # Get current price (outcomePrices or similar)
    outcome_prices = market.get('outcomePrices', ['0.5', '0.5'])
    
    # Parse if it's a JSON string
    if isinstance(outcome_prices, str):
        try:
            outcome_prices = json.loads(outcome_prices)
        except:
            outcome_prices = ['0.5', '0.5']
    
    try:
        current_price = float(outcome_prices[0]) if outcome_prices else 0.5
    except:
        current_price = 0.5
    
    # Check each strategy
    for strategy_name, params in STRATEGIES.items():
        if re.search(params['pattern'], question, re.I):
            if params['check'](question):
                opportunities.append({
                    'market_id': market.get('id', market.get('conditionId')),
                    'question': question,
                    'strategy': strategy_name,
                    'current_price': current_price,
                    'volume': volume,
                    'liquidity': liquidity,
                    'end_date': end_date,
                    'expected_win': params['expected_win']
                })

print(f"\n[FOUND] {len(opportunities)} live opportunities")

# Breakdown
from collections import Counter
strategy_counts = Counter([o['strategy'] for o in opportunities])

print(f"\n[BREAKDOWN]")
for strategy, count in strategy_counts.most_common():
    print(f"  {strategy:30} {count:4} markets")

# Show top 10
print("\n" + "="*80)
print("TOP 10 LIVE OPPORTUNITIES (Ready to Paper Trade)")
print("="*80)

opportunities.sort(key=lambda o: (o['expected_win'], o['volume']), reverse=True)

for i, opp in enumerate(opportunities[:10], 1):
    volume = float(opp['volume']) if opp['volume'] else 0
    
    print(f"\n{i}. [{opp['strategy']}] Win: {opp['expected_win']:.1f}%")
    print(f"   {opp['question'][:70]}")
    print(f"   Price: {opp['current_price']:.4f} | Volume: ${volume/1000:.0f}K")
    print(f"   End: {opp.get('end_date', 'Unknown')[:10]}")

# Save
with open('live_markets_now.json', 'w') as f:
    json.dump(opportunities, f, indent=2)

print(f"\n[SAVED] live_markets_now.json")
print(f"  {len(opportunities)} opportunities ready for real-time paper trading")
