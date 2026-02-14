import json
import datetime

# Read the kalshi_latest.json file
with open('kalshi_latest.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

print(f"Total events in latest data: {len(data.get('events', []))}")

current_date = datetime.datetime.now(datetime.timezone.utc)

# Look for markets with recent close dates
all_markets = []
for event in data.get('events', []):
    for market in event.get('markets', []):
        if market.get('status') == 'active':
            close_date_str = market.get('close_date')
            if close_date_str:
                try:
                    close_date = datetime.datetime.fromisoformat(close_date_str.replace('Z', '+00:00'))
                    days_to_resolution = (close_date - current_date).days
                    
                    yes_ask = market.get('yes_ask', 100)
                    volume = market.get('volume', 0)
                    volume_fp = market.get('volume_fp', 0)
                    
                    # Calculate expected return
                    expected_return_pct = ((100 - yes_ask) / yes_ask * 0.98) * 100
                    
                    all_markets.append({
                        'ticker': market.get('ticker_name'),
                        'title': market.get('title', ''),
                        'yes_ask': yes_ask,
                        'volume': volume,
                        'volume_fp': volume_fp,
                        'close_date': close_date_str,
                        'days_to_resolution': days_to_resolution,
                        'expected_return_pct': expected_return_pct,
                        'last_price': market.get('last_price', yes_ask),
                        'previous_day_price': market.get('previous_day_price', yes_ask),
                        'previous_week_price': market.get('previous_week_price', yes_ask)
                    })
                except Exception as e:
                    continue

print(f"Total active markets: {len(all_markets)}")

# Find markets resolving soon (<30 days)
soon_markets = [m for m in all_markets if 0 < m['days_to_resolution'] < 30]
soon_markets.sort(key=lambda x: x['days_to_resolution'])

print(f"\nMarkets resolving in <30 days: {len(soon_markets)}")
print("\n=== SOONEST RESOLVING MARKETS ===")
for i, market in enumerate(soon_markets[:15]):
    # Calculate price changes
    prev_day = market.get('previous_day_price', market['yes_ask'])
    prev_week = market.get('previous_week_price', market['yes_ask'])
    daily_change = ((market['yes_ask'] - prev_day) / prev_day * 100) if prev_day else 0
    weekly_change = ((market['yes_ask'] - prev_week) / prev_week * 100) if prev_week else 0
    
    print(f"{i+1}. {market['ticker']}")
    print(f"   Title: {market['title'][:60]}...")
    print(f"   Price: {market['yes_ask']}¢, Days: {market['days_to_resolution']}")
    print(f"   Close: {market['close_date'][:10]}")
    print(f"   Volume: {market['volume_fp']:,}")
    print(f"   Expected Return: {market['expected_return_pct']:.1f}%")
    print(f"   Daily Change: {daily_change:.1f}%, Weekly: {weekly_change:.1f}%")
    print()

# Find markets with dips (>10% drop from previous day)
print("\n=== MARKETS WITH RECENT DIPS (>10% daily drop) ===")
dip_markets = []
for market in all_markets:
    prev_day = market.get('previous_day_price', market['yes_ask'])
    if prev_day and prev_day > 0:
        daily_change_pct = ((market['yes_ask'] - prev_day) / prev_day * 100)
        if daily_change_pct < -10:  # Drop of more than 10%
            dip_markets.append((market, daily_change_pct))

dip_markets.sort(key=lambda x: x[1])  # Sort by largest drop

for i, (market, drop_pct) in enumerate(dip_markets[:15]):
    print(f"{i+1}. {market['ticker']}")
    print(f"   Title: {market['title'][:60]}...")
    print(f"   Price: {market['yes_ask']}¢ (was {market.get('previous_day_price', 'N/A')}¢)")
    print(f"   Drop: {drop_pct:.1f}%")
    print(f"   Days to resolution: {market['days_to_resolution']}")
    print(f"   Expected Return: {market['expected_return_pct']:.1f}%")
    print()