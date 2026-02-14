import requests
import json

api_key = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

# Get events with markets
print("Fetching Kalshi events with markets...")
response = requests.get('https://api.elections.kalshi.com/v1/events', headers=headers, params={'limit': 50})
data = response.json()

print(f"Total events: {len(data.get('events', []))}")

# Count total markets
total_markets = 0
active_markets = 0
dip_opportunities = []

for event in data.get('events', []):
    markets = event.get('markets', [])
    total_markets += len(markets)
    
    for market in markets:
        if market.get('status') == 'active':
            active_markets += 1
            
            # Check for dip opportunities
            yes_price = market.get('yes_price')
            prev_week = market.get('previous_week_price')
            
            if yes_price and prev_week and prev_week > 0:
                drop_pct = (yes_price - prev_week) / prev_week * 100
                if drop_pct < -10:  # More than 10% drop
                    dip_opportunities.append({
                        'ticker': market.get('ticker'),
                        'title': market.get('title'),
                        'current_price': yes_price,
                        'prev_week_price': prev_week,
                        'drop_pct': drop_pct,
                        'volume': market.get('volume'),
                        'category': event.get('category')
                    })

print(f"Total markets: {total_markets}")
print(f"Active markets: {active_markets}")
print(f"Dip opportunities (>10% drop): {len(dip_opportunities)}")

# Sort dip opportunities by drop percentage
dip_opportunities.sort(key=lambda x: x['drop_pct'])

print("\nTop 20 dip opportunities:")
for i, opp in enumerate(dip_opportunities[:20]):
    print(f"{i+1:2d}. {opp['title'][:60]}...")
    print(f"     Price: {opp['current_price']}¢ (was {opp['prev_week_price']}¢, drop: {opp['drop_pct']:.1f}%)")
    print(f"     Category: {opp['category']}, Volume: ${opp['volume']}")
    print()

# Save to file
with open('kalshi_dip_opportunities.json', 'w') as f:
    json.dump(dip_opportunities, f, indent=2)

print(f"\nSaved {len(dip_opportunities)} dip opportunities to kalshi_dip_opportunities.json")