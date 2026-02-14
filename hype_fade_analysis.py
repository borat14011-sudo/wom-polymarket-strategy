import json
import ast
from datetime import datetime
import sys

# Set encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

print('HYPE FADE ANALYSIS - Markets that spiked on news/hype and likely to crash')
print('=' * 100)

# Load Kalshi data
with open('kalshi_markets_raw.json', 'r', encoding='utf-8-sig') as f:
    kalshi_data = json.load(f)

# Load Polymarket data
with open('active-markets.json', 'r', encoding='utf-8-sig') as f:
    poly_data = json.load(f)

# Focus on specific patterns mentioned in the task
# 1. Trump announcement markets
# 2. Elon Musk tweet effects  
# 3. Celebrity/culture markets
# 4. Political drama
# 5. Crypto markets

print('\n1. TRUMP-RELATED MARKETS (Potential hype spikes):')
print('-' * 50)

trump_keywords = ['trump', 'deport', 'tariff', 'greenland', 'immigration']
trump_markets = []

for market in poly_data:
    question = market.get('question', '').lower()
    if any(keyword in question for keyword in trump_keywords):
        # Parse outcome prices
        outcome_prices_str = market.get('outcomePrices', '["0", "0"]')
        try:
            if isinstance(outcome_prices_str, str):
                outcome_prices = ast.literal_eval(outcome_prices_str)
                current_price = float(outcome_prices[0]) if outcome_prices else 0
            else:
                current_price = 0
        except:
            current_price = 0
            
        one_week_change = market.get('oneWeekPriceChange', 0)
        trump_markets.append({
            'id': market['id'],
            'question': market['question'],
            'current_price': current_price,
            'one_week_change': one_week_change,
            'volume1wk': market.get('volume1wk', 0)
        })

# Sort by weekly change
trump_markets.sort(key=lambda x: abs(x['one_week_change']), reverse=True)

for i, market in enumerate(trump_markets[:10]):
    direction = 'UP' if market['one_week_change'] > 0 else 'DOWN'
    print(f'{i+1}. {market["question"][:80]}...')
    print(f'   Price: {market["current_price"]:.3f} | Weekly: {market["one_week_change"]:.3f} {direction}')
    print(f'   Weekly Volume: ${market["volume1wk"]:,.2f}')
    print()

print('\n2. ELON MUSK / CRYPTO MARKETS:')
print('-' * 50)

elon_crypto_markets = []
for market in kalshi_data:
    title = market.get('title', '').lower()
    name = market.get('name', '').lower()
    if 'elon' in title or 'musk' in title or 'mars' in title or 'doge' in title or 'crypto' in title:
        weekly_change = market.get('weekly_change_pct', 0)
        if weekly_change is not None and weekly_change >= 20:
            elon_crypto_markets.append({
                'ticker': market['ticker_name'],
                'title': market['title'],
                'current_price': market['last_price'],
                'weekly_change_pct': weekly_change,
                'volume': market['volume']
            })

elon_crypto_markets.sort(key=lambda x: x['weekly_change_pct'], reverse=True)

for i, market in enumerate(elon_crypto_markets[:10]):
    print(f'{i+1}. {market["ticker"]}')
    print(f'   {market["title"][:80]}...')
    print(f'   Price: {market["current_price"]}c | Weekly: +{market["weekly_change_pct"]:.1f}%')
    print(f'   Volume: {market["volume"]:,}')
    print()

print('\n3. CELEBRITY / CULTURE MARKETS (Viral moments that fade):')
print('-' * 50)

celebrity_keywords = ['tom hardy', 'james bond', 'miami vice', 'harvey weinstein', 'actor', 'celebrity']
celebrity_markets = []

# Check Kalshi
for market in kalshi_data:
    title = market.get('title', '').lower()
    name = market.get('name', '').lower()
    if any(keyword in title or keyword in name for keyword in celebrity_keywords):
        weekly_change = market.get('weekly_change_pct', 0)
        if weekly_change is not None and abs(weekly_change) >= 20:
            celebrity_markets.append({
                'source': 'Kalshi',
                'ticker': market['ticker_name'],
                'title': market['title'],
                'current_price': market['last_price'],
                'change': weekly_change,
                'volume': market['volume']
            })

# Check Polymarket
for market in poly_data:
    question = market.get('question', '').lower()
    if any(keyword in question for keyword in ['weinstein', 'bitboy', 'celebrity', 'actor']):
        one_week_change = market.get('oneWeekPriceChange', 0)
        if abs(one_week_change) >= 0.20:
            # Parse outcome prices
            outcome_prices_str = market.get('outcomePrices', '["0", "0"]')
            try:
                if isinstance(outcome_prices_str, str):
                    outcome_prices = ast.literal_eval(outcome_prices_str)
                    current_price = float(outcome_prices[0]) if outcome_prices else 0
                else:
                    current_price = 0
            except:
                current_price = 0
                
            celebrity_markets.append({
                'source': 'Polymarket',
                'id': market['id'],
                'question': market['question'],
                'current_price': current_price,
                'change': one_week_change,
                'volume1wk': market.get('volume1wk', 0)
            })

celebrity_markets.sort(key=lambda x: abs(x['change']), reverse=True)

for i, market in enumerate(celebrity_markets[:10]):
    if market['source'] == 'Kalshi':
        print(f'{i+1}. [Kalshi] {market["ticker"]}')
        print(f'   {market["title"][:80]}...')
        print(f'   Price: {market["current_price"]}c | Weekly: {market["change"]:.1f}%')
        print(f'   Volume: {market["volume"]:,}')
    else:
        direction = 'UP' if market['change'] > 0 else 'DOWN'
        print(f'{i+1}. [Polymarket] ID: {market["id"]}')
        print(f'   {market["question"][:80]}...')
        print(f'   Price: {market["current_price"]:.3f} | Weekly: {market["change"]:.3f} {direction}')
        print(f'   Weekly Volume: ${market["volume1wk"]:,.2f}')
    print()

print('\n4. POLITICAL DRAMA MARKETS (Spikes that blow over):')
print('-' * 50)

political_markets = []
for market in kalshi_data:
    category = market.get('category', '').lower()
    if category == 'politics':
        weekly_change = market.get('weekly_change_pct', 0)
        if weekly_change is not None and weekly_change >= 20:
            political_markets.append({
                'ticker': market['ticker_name'],
                'title': market['title'],
                'name': market['name'],
                'current_price': market['last_price'],
                'weekly_change_pct': weekly_change,
                'volume': market['volume'],
                'open_interest': market['open_interest']
            })

political_markets.sort(key=lambda x: x['weekly_change_pct'], reverse=True)

print(f'Found {len(political_markets)} political markets with >=20% weekly spikes')
print('Top candidates for fade:')

# Filter for markets that are likely overreactions
# Look for: low absolute prices (5-20c), high percentage spikes, political speculation
fade_candidates = []
for market in political_markets:
    # Markets in 5-20c range with huge spikes are good fade candidates
    if 5 <= market['current_price'] <= 20 and market['weekly_change_pct'] >= 100:
        fade_candidates.append(market)

for i, market in enumerate(fade_candidates[:15]):
    print(f'{i+1}. {market["ticker"]}')
    print(f'   {market["title"]}')
    if market['name']:
        print(f'   Candidate: {market["name"]}')
    print(f'   Current: {market["current_price"]}c | Weekly: +{market["weekly_change_pct"]:.1f}%')
    print(f'   Volume: {market["volume"]:,} | OI: {market["open_interest"]:,}')
    print(f'   FADE POTENTIAL: HIGH - Political speculation, likely overreaction')
    print()

print('\n5. BEST FADE OPPORTUNITIES (Summary):')
print('-' * 50)
print('Based on analysis, these are the top hype fade candidates:')
print()

top_fades = [
    {
        'reason': 'Political speculation spike - Gadi Eisenkot as next Israel PM',
        'ticker': 'KXNEXTISRAELPM-45JAN01-GEIS',
        'current': '8c',
        'spike': '+700%',
        'target': '2-3c',
        'rationale': 'Sudden political rumor spike. Eisenkot not a frontrunner. Likely reverts.'
    },
    {
        'reason': 'Multiple Chinese political succession candidates',
        'tickers': ['KXXISUCCESSOR-45JAN01-YLI', 'KXXISUCCESSOR-45JAN01-LGAN', 'KXXISUCCESSOR-45JAN01-HLIF'],
        'current': '5-6c',
        'spike': '+400-500%',
        'target': '1-2c',
        'rationale': 'Speculative spikes on obscure candidates. Xi unlikely to name successor soon.'
    },
    {
        'reason': 'Tom Hardy Miami Vice casting rumor',
        'ticker': 'KXACTORSONNYCROCKETT-35-TOM',
        'current': '12c',
        'spike': '+1100%',
        'target': '3-5c',
        'rationale': 'Entertainment rumor spike. No official announcement. Likely fades.'
    },
    {
        'reason': 'Harvey Weinstein sentencing market',
        'source': 'Polymarket ID: 544092',
        'current': '0.369',
        'spike': '+0.210',
        'target': '0.20-0.25',
        'rationale': 'Sentencing news spike. Market overreacting to headlines.'
    },
    {
        'reason': 'Next Pope speculation - massive spike',
        'ticker': 'KXNEXTPOPE-35-RPRE',
        'current': '99c',
        'spike': '+9800%',
        'target': '50-70c',
        'rationale': 'Extreme spike to near-certainty. Pope health rumors often overblown.'
    }
]

for i, fade in enumerate(top_fades):
    print(f'{i+1}. {fade["reason"]}')
    if 'ticker' in fade:
        print(f'   Market: {fade["ticker"]}')
    elif 'tickers' in fade:
        print(f'   Markets: {", ".join(fade["tickers"])}')
    else:
        print(f'   Market: {fade["source"]}')
    print(f'   Current: {fade["current"]} | Spike: {fade["spike"]} | Target: {fade["target"]}')
    print(f'   Rationale: {fade["rationale"]}')
    print()