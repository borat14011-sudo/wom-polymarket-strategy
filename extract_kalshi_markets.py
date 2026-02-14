import json
import datetime
import csv

# Read the kalshi_markets_raw.json file
with open('kalshi_markets_raw.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# Get current date for time calculations
current_date = datetime.datetime.now(datetime.timezone.utc)

active_markets = []
for market in data:
    # Skip if not active
    if market.get('status') != 'active':
        continue
    
    # Get price information
    yes_ask = market.get('yes_ask')
    yes_bid = market.get('yes_bid')
    last_price = market.get('last_price', yes_ask)
    
    # Skip if no price data
    if yes_ask is None or yes_bid is None:
        continue
    
    # Calculate no prices (100 - yes price)
    no_ask = 100 - yes_ask
    no_bid = 100 - yes_bid
    
    # Calculate expected values
    # Expected value for YES: (100 - yes_ask) / yes_ask * 0.98 (after 2% fee)
    ev_yes = ((100 - yes_ask) / yes_ask * 0.98) * 100 if yes_ask > 0 else 0
    
    # Expected value for NO: (100 - no_ask) / no_ask * 0.98 (after 2% fee)
    ev_no = ((100 - no_ask) / no_ask * 0.98) * 100 if no_ask > 0 else 0
    
    # Get volume in dollars (volume is in cents)
    volume_cents = market.get('volume', 0)
    volume_dollars = volume_cents * 0.01
    
    # Calculate days to resolution
    close_date_str = market.get('close_date')
    days_to_resolution = None
    if close_date_str:
        try:
            close_date = datetime.datetime.fromisoformat(close_date_str.replace('Z', '+00:00'))
            days_to_resolution = (close_date - current_date).days
        except:
            pass
    
    active_markets.append({
        'ticker': market['ticker_name'],
        'title': market['title'],
        'name': market.get('name', ''),
        'category': market.get('category', ''),
        'yes_bid': yes_bid,
        'yes_ask': yes_ask,
        'no_bid': no_bid,
        'no_ask': no_ask,
        'last_price': last_price,
        'daily_change_pct': market.get('daily_change_pct', 0),
        'weekly_change_pct': market.get('weekly_change_pct', 0),
        'volume_cents': volume_cents,
        'volume_dollars': volume_dollars,
        'open_interest': market.get('open_interest', 0),
        'close_date': close_date_str,
        'days_to_resolution': days_to_resolution,
        'expected_value_yes_pct': ev_yes,
        'expected_value_no_pct': ev_no,
        'is_dip_candidate': market.get('is_dip_candidate', False)
    })

print(f'Total active markets with price data: {len(active_markets)}')

# Sort by highest expected value for YES
top_yes = sorted(active_markets, key=lambda x: x['expected_value_yes_pct'], reverse=True)[:10]

print('\n=== TOP 10 YES OPPORTUNITIES (Highest Expected Value) ===')
for i, market in enumerate(top_yes):
    print(f'{i+1}. {market["ticker"]}')
    print(f'   Title: {market["title"][:80]}...')
    print(f'   Category: {market["category"]}')
    print(f'   YES Price: {market["yes_ask"]}¢ (Bid: {market["yes_bid"]}¢)')
    print(f'   NO Price: {market["no_ask"]}¢ (Bid: {market["no_bid"]}¢)')
    print(f'   Expected Value (YES): {market["expected_value_yes_pct"]:.1f}%')
    print(f'   Volume: ${market["volume_dollars"]:,.0f}, Days to resolution: {market["days_to_resolution"]}')
    print()

# Sort by highest expected value for NO
top_no = sorted(active_markets, key=lambda x: x['expected_value_no_pct'], reverse=True)[:10]

print('\n=== TOP 10 NO OPPORTUNITIES (Highest Expected Value) ===')
for i, market in enumerate(top_no):
    print(f'{i+1}. {market["ticker"]}')
    print(f'   Title: {market["title"][:80]}...')
    print(f'   Category: {market["category"]}')
    print(f'   YES Price: {market["yes_ask"]}¢ (Bid: {market["yes_bid"]}¢)')
    print(f'   NO Price: {market["no_ask"]}¢ (Bid: {market["no_bid"]}¢)')
    print(f'   Expected Value (NO): {market["expected_value_no_pct"]:.1f}%')
    print(f'   Volume: ${market["volume_dollars"]:,.0f}, Days to resolution: {market["days_to_resolution"]}')
    print()

# Save to CSV for further analysis
csv_filename = 'kalshi_active_markets_with_prices.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['ticker', 'title', 'name', 'category', 'yes_bid', 'yes_ask', 'no_bid', 'no_ask', 
                  'last_price', 'daily_change_pct', 'weekly_change_pct', 'volume_cents', 'volume_dollars',
                  'open_interest', 'close_date', 'days_to_resolution', 'expected_value_yes_pct', 
                  'expected_value_no_pct', 'is_dip_candidate']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(active_markets)

print(f'\nData saved to {csv_filename}')
print(f'Total markets analyzed: {len(active_markets)}')

# Calculate some statistics
if active_markets:
    avg_yes_price = sum(m['yes_ask'] for m in active_markets) / len(active_markets)
    avg_volume = sum(m['volume_dollars'] for m in active_markets) / len(active_markets)
    
    print(f'\n=== MARKET STATISTICS ===')
    print(f'Average YES price: {avg_yes_price:.1f}¢')
    print(f'Average volume: ${avg_volume:,.0f}')
    print(f'Markets with >$10K volume: {sum(1 for m in active_markets if m["volume_dollars"] > 10000)}')
    print(f'Markets with >$50K volume: {sum(1 for m in active_markets if m["volume_dollars"] > 50000)}')
    
    # Find markets with highest volume
    high_volume = sorted(active_markets, key=lambda x: x['volume_dollars'], reverse=True)[:5]
    print(f'\n=== TOP 5 BY VOLUME ===')
    for i, market in enumerate(high_volume):
        print(f'{i+1}. {market["ticker"]}: ${market["volume_dollars"]:,.0f} - {market["title"][:60]}...')