import json

# Load Kalshi data - handle BOM
with open('kalshi_markets_raw.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

print('Analyzing Kalshi markets for weekly spikes >= 20%...')
print('=' * 80)

spikes = []
for market in data:
    weekly_change = market.get('weekly_change_pct', 0)
    if weekly_change is not None and weekly_change >= 20:
        spikes.append({
            'ticker': market['ticker_name'],
            'title': market['title'],
            'name': market['name'],
            'category': market['category'],
            'current_price': market['last_price'],
            'previous_week_price': market['previous_week_price'],
            'weekly_change_pct': weekly_change,
            'volume': market['volume'],
            'open_interest': market['open_interest']
        })

print(f'Found {len(spikes)} markets with weekly spikes >= 20%')
print()

# Sort by biggest spikes
spikes.sort(key=lambda x: x['weekly_change_pct'], reverse=True)

for i, spike in enumerate(spikes[:20]):
    print(f'{i+1}. {spike["ticker"]}')
    print(f'   Title: {spike["title"]}')
    print(f'   Name: {spike["name"]}')
    print(f'   Category: {spike["category"]}')
    print(f'   Current: {spike["current_price"]}c, Previous Week: {spike["previous_week_price"]}c')
    print(f'   Weekly Change: {spike["weekly_change_pct"]:.2f}%')
    print(f'   Volume: {spike["volume"]}, Open Interest: {spike["open_interest"]}')
    print()

# Now analyze Polymarket data
print('\n' + '=' * 80)
print('Analyzing Polymarket data for price changes...')
print('=' * 80)

with open('active-markets.json', 'r', encoding='utf-8-sig') as f:
    poly_data = json.load(f)

poly_spikes = []
for market in poly_data:
    one_week_change = market.get('oneWeekPriceChange')
    if one_week_change is not None and abs(one_week_change) >= 0.20:  # 20% change
        # Parse outcomePrices which is a string like "[\"0.058\", \"0.942\"]"
        outcome_prices_str = market.get('outcomePrices', '["0", "0"]')
        try:
            # Clean the string and parse as JSON
            if isinstance(outcome_prices_str, str):
                import ast
                outcome_prices = ast.literal_eval(outcome_prices_str)
                current_price = float(outcome_prices[0]) if outcome_prices else 0
            else:
                current_price = 0
        except:
            current_price = 0
            
        poly_spikes.append({
            'id': market['id'],
            'question': market['question'],
            'current_price': current_price,
            'one_week_change': one_week_change,
            'volume24hr': market.get('volume24hr', 0),
            'volume1wk': market.get('volume1wk', 0),
            'slug': market.get('slug', '')
        })

print(f'Found {len(poly_spikes)} Polymarket markets with weekly changes >= 20%')
print()

# Sort by absolute change
poly_spikes.sort(key=lambda x: abs(x['one_week_change']), reverse=True)

for i, spike in enumerate(poly_spikes[:20]):
    direction = 'UP' if spike['one_week_change'] > 0 else 'DOWN'
    print(f'{i+1}. ID: {spike["id"]}')
    print(f'   Question: {spike["question"][:100]}...')
    print(f'   Current Price: {spike["current_price"]:.3f}')
    print(f'   Weekly Change: {spike["one_week_change"]:.3f} ({direction})')
    print(f'   24h Volume: ${spike["volume24hr"]:,.2f}, Weekly Volume: ${spike["volume1wk"]:,.2f}')
    print()