import json
import datetime

# Read the kalshi_markets_raw.json file
with open('kalshi_markets_raw.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# Get current date for time calculations
current_date = datetime.datetime.now(datetime.timezone.utc)

opportunities = []
for market in data:
    # Skip if not active
    if market.get('status') != 'active':
        continue
    
    # Get price information
    yes_ask = market.get('yes_ask', 100)  # Use ask price for entry
    last_price = market.get('last_price', yes_ask)
    
    # Check price range (8-92%)
    if yes_ask < 8 or yes_ask > 92:
        continue
    
    # Check volume (in dollars, volume is in cents * 100?)
    volume = market.get('volume', 0)
    # Assuming volume is in cents, convert to dollars: volume * 0.01
    volume_dollars = volume * 0.01
    if volume_dollars < 10000:  # $10K threshold
        continue
    
    # Check for dips (daily or weekly change >10% drop)
    daily_change = market.get('daily_change_pct', 0)
    weekly_change = market.get('weekly_change_pct', 0)
    
    is_dip = (daily_change < -10) or (weekly_change < -10)
    
    # Check time to resolution
    close_date_str = market.get('close_date')
    if close_date_str:
        try:
            close_date = datetime.datetime.fromisoformat(close_date_str.replace('Z', '+00:00'))
            days_to_resolution = (close_date - current_date).days
            
            # Check time filter: <7 days or >30 days
            time_ok = (days_to_resolution < 7) or (days_to_resolution > 30)
        except:
            time_ok = False
    else:
        time_ok = False
    
    if is_dip and time_ok:
        # Calculate expected value (after 2% Kalshi fees)
        # If we buy at yes_ask, payout is 100 if YES, 0 if NO
        # Expected return = (100 - yes_ask) / yes_ask * 0.98 (after 2% fee)
        expected_return_pct = ((100 - yes_ask) / yes_ask * 0.98) * 100
        
        opportunities.append({
            'ticker': market['ticker_name'],
            'title': market['title'],
            'name': market.get('name', ''),
            'category': market.get('category', ''),
            'yes_ask': yes_ask,
            'last_price': last_price,
            'daily_change_pct': daily_change,
            'weekly_change_pct': weekly_change,
            'volume': volume,
            'volume_dollars': volume_dollars,
            'close_date': close_date_str,
            'days_to_resolution': days_to_resolution if 'days_to_resolution' in locals() else None,
            'expected_return_pct': expected_return_pct,
            'is_dip_candidate': market.get('is_dip_candidate', False)
        })

# Sort by expected return (highest first)
opportunities.sort(key=lambda x: x['expected_return_pct'], reverse=True)

print(f'Found {len(opportunities)} opportunities matching Buy the Dip criteria')
print('\nTop 10 opportunities:')
for i, opp in enumerate(opportunities[:10]):
    print(f'{i+1}. {opp["ticker"]}')
    print(f'   Title: {opp["title"][:80]}...')
    print(f'   Price: {opp["yes_ask"]}¢, Daily Change: {opp["daily_change_pct"]}%, Weekly Change: {opp["weekly_change_pct"]}%')
    print(f'   Volume: ${opp["volume_dollars"]:,.0f}, Days to resolution: {opp["days_to_resolution"]}')
    print(f'   Expected Return: {opp["expected_return_pct"]:.1f}%')
    print()