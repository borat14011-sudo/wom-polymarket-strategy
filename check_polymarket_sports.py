import json
import datetime

# Read the active-markets.json file
with open('active-markets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

current_date = datetime.datetime.now(datetime.timezone.utc)

print(f"Total Polymarket markets: {len(data)}")

# Look for sports markets
sports_markets = []
for market in data:
    question = market.get('question', '').lower()
    title = market.get('title', '').lower() if market.get('title') else ''
    
    sports_keywords = ['nba', 'nfl', 'mlb', 'nhl', 'soccer', 'football', 'basketball', 'baseball', 'hockey', 'tennis', 'golf', 'fight', 'boxing', 'ufc']
    
    is_sports = any(keyword in question or keyword in title for keyword in sports_keywords)
    
    if is_sports:
        end_date_str = market.get('endDate')
        days_to_resolution = None
        if end_date_str:
            try:
                end_date = datetime.datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                days_to_resolution = (end_date - current_date).days
            except:
                pass
        
        # Get best price (use outcomePrices)
        outcome_prices = market.get('outcomePrices', '[]')
        try:
            prices = json.loads(outcome_prices)
            if prices and len(prices) >= 2:
                yes_price = float(prices[0]) * 100  # Convert to cents
                no_price = float(prices[1]) * 100
        except:
            yes_price = 50  # Default
        
        sports_markets.append({
            'id': market.get('id'),
            'question': market.get('question', ''),
            'end_date': end_date_str,
            'days_to_resolution': days_to_resolution,
            'yes_price': yes_price,
            'volume': market.get('volumeNum', 0),
            'liquidity': market.get('liquidityNum', 0)
        })

print(f"\nFound {len(sports_markets)} sports-related markets")

# Find markets resolving soon (<3 days)
soon_sports = [m for m in sports_markets if m['days_to_resolution'] is not None and 0 <= m['days_to_resolution'] <= 3]
soon_sports.sort(key=lambda x: x['days_to_resolution'])

print(f"\nSports markets resolving in <=3 days: {len(soon_sports)}")
for market in soon_sports[:10]:
    print(f"\n{market['question'][:80]}...")
    print(f"  ID: {market['id']}")
    print(f"  Resolves in: {market['days_to_resolution']} days")
    print(f"  Yes price: {market['yes_price']:.1f}¢")
    print(f"  Volume: ${market['volume']:,.0f}")
    print(f"  Liquidity: ${market['liquidity']:,.0f}")

# Also check for markets with high volume
high_volume = [m for m in sports_markets if m['volume'] > 10000]
print(f"\n\nSports markets with volume > $10K: {len(high_volume)}")
for market in high_volume[:10]:
    print(f"\n{market['question'][:80]}...")
    print(f"  Volume: ${market['volume']:,.0f}")
    print(f"  Yes price: {market['yes_price']:.1f}¢")
    if market['days_to_resolution']:
        print(f"  Resolves in: {market['days_to_resolution']} days")