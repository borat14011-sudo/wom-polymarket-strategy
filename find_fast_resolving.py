import json
import datetime

# Read the kalshi_markets_raw.json file
with open('kalshi_markets_raw.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# Get current date for time calculations
current_date = datetime.datetime.now(datetime.timezone.utc)

print(f"Total markets in data: {len(data)}")

# Look for markets resolving in <7 days
fast_markets = []
for market in data:
    # Skip if not active
    if market.get('status') != 'active':
        continue
    
    # Check time to resolution
    close_date_str = market.get('close_date')
    if close_date_str:
        try:
            close_date = datetime.datetime.fromisoformat(close_date_str.replace('Z', '+00:00'))
            days_to_resolution = (close_date - current_date).days
            
            if days_to_resolution < 7 and days_to_resolution > 0:
                yes_ask = market.get('yes_ask', 100)
                last_price = market.get('last_price', yes_ask)
                volume = market.get('volume', 0)
                
                # Calculate expected return
                expected_return_pct = ((100 - yes_ask) / yes_ask * 0.98) * 100
                
                fast_markets.append({
                    'ticker': market['ticker_name'],
                    'title': market['title'],
                    'yes_ask': yes_ask,
                    'last_price': last_price,
                    'volume': volume,
                    'close_date': close_date_str,
                    'days_to_resolution': days_to_resolution,
                    'expected_return_pct': expected_return_pct,
                    'daily_change_pct': market.get('daily_change_pct', 0),
                    'weekly_change_pct': market.get('weekly_change_pct', 0)
                })
        except Exception as e:
            continue

# Sort by days to resolution (soonest first)
fast_markets.sort(key=lambda x: x['days_to_resolution'])

print(f'\nFound {len(fast_markets)} markets resolving in <7 days')
print('\n=== MARKETS RESOLVING SOON (<7 days) ===')
for i, market in enumerate(fast_markets[:20]):
    print(f'{i+1}. {market["ticker"]}')
    print(f'   Title: {market["title"][:70]}...')
    print(f'   Price: {market["yes_ask"]}¢, Days: {market["days_to_resolution"]}')
    print(f'   Close Date: {market["close_date"]}')
    print(f'   Volume: {market["volume"]:,}')
    print(f'   Expected Return: {market["expected_return_pct"]:.1f}%')
    print(f'   Daily Change: {market["daily_change_pct"]}%, Weekly: {market["weekly_change_pct"]}%')
    print()

# Also check for economic data releases this week
print('\n=== CHECKING FOR ECONOMIC DATA MARKETS ===')
economic_keywords = ['CPI', 'Fed', 'inflation', 'jobs', 'unemployment', 'GDP', 'retail sales']
for market in data:
    if market.get('status') != 'active':
        continue
    
    title = market.get('title', '').lower()
    for keyword in economic_keywords:
        if keyword.lower() in title:
            yes_ask = market.get('yes_ask', 100)
            volume = market.get('volume', 0)
            
            close_date_str = market.get('close_date')
            days_to_resolution = None
            if close_date_str:
                try:
                    close_date = datetime.datetime.fromisoformat(close_date_str.replace('Z', '+00:00'))
                    days_to_resolution = (close_date - current_date).days
                except:
                    pass
            
            print(f'{market["ticker_name"]}')
            print(f'   Title: {market["title"]}')
            print(f'   Price: {yes_ask}¢, Volume: {volume:,}')
            if days_to_resolution:
                print(f'   Days to resolution: {days_to_resolution}')
            print()