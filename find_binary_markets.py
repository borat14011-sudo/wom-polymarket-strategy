import requests
import json

api_key = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

# Get events
response = requests.get('https://api.elections.kalshi.com/v1/events', headers=headers, params={'limit': 50})
data = response.json()

print("Looking for binary YES/NO markets with prices...")
print("=" * 80)

binary_markets = []
for event in data.get('events', []):
    event_title = event.get('title', '')
    
    # Look for binary markets (not "Who will" or multi-choice)
    if "Will " in event_title and "Who will" not in event_title:
        for market in event.get('markets', []):
            if market.get('status') == 'active' and market.get('yes_price') is not None:
                binary_markets.append({
                    'event_title': event_title,
                    'market_title': market.get('title'),
                    'yes_price': market.get('yes_price'),
                    'no_price': market.get('no_price'),
                    'volume': market.get('volume'),
                    'category': event.get('category'),
                    'previous_week': market.get('previous_week_price')
                })

print(f"Found {len(binary_markets)} binary markets with prices")
print("\nSample binary markets:")
for i, market in enumerate(binary_markets[:10]):
    print(f"\n{i+1}. {market['event_title']}")
    print(f"   Yes: {market['yes_price']}¢, No: {market['no_price']}¢")
    print(f"   Volume: ${market['volume']}, Category: {market['category']}")
    if market['previous_week']:
        change = ((market['yes_price'] - market['previous_week']) / market['previous_week'] * 100) if market['previous_week'] else 0
        print(f"   Previous week: {market['previous_week']}¢ ({change:+.1f}%)")

# Analyze price distribution
if binary_markets:
    prices = [m['yes_price'] for m in binary_markets]
    print(f"\nPrice analysis for {len(prices)} binary markets:")
    print(f"Min: {min(prices)}¢")
    print(f"Max: {max(prices)}¢")
    print(f"Avg: {sum(prices)/len(prices):.1f}¢")
    
    # Find dip opportunities
    dip_ops = []
    for market in binary_markets:
        if market['previous_week'] and market['previous_week'] > 0:
            drop_pct = (market['yes_price'] - market['previous_week']) / market['previous_week'] * 100
            if drop_pct < -10:
                dip_ops.append((market, drop_pct))
    
    print(f"\nDip opportunities (>10% drop): {len(dip_ops)}")
    for market, drop_pct in sorted(dip_ops, key=lambda x: x[1])[:5]:
        print(f"  - {market['event_title'][:50]}...")
        print(f"    Price: {market['yes_price']}¢ (was {market['previous_week']}¢, drop: {drop_pct:.1f}%)")