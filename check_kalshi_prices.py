import requests
import json

api_key = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

# Get sample markets
response = requests.get('https://api.elections.kalshi.com/v1/events', headers=headers, params={'limit': 20})
data = response.json()

print("Sample market data:")
print("=" * 80)

market_count = 0
for event in data.get('events', []):
    for market in event.get('markets', []):
        if market.get('status') == 'active':
            market_count += 1
            print(f"\nMarket {market_count}:")
            print(f"  Title: {market.get('title')}")
            print(f"  Ticker: {market.get('ticker')}")
            print(f"  Yes Price: {market.get('yes_price')}")
            print(f"  No Price: {market.get('no_price')}")
            print(f"  Volume: ${market.get('volume')}")
            print(f"  Category: {event.get('category')}")
            print(f"  Previous Week: {market.get('previous_week_price')}")
            
            if market_count >= 10:
                break
    if market_count >= 10:
        break

print("\n" + "=" * 80)
print("Checking price ranges...")

# Collect all prices
all_prices = []
for event in data.get('events', []):
    for market in event.get('markets', []):
        if market.get('status') == 'active' and market.get('yes_price') is not None:
            all_prices.append(market.get('yes_price'))

if all_prices:
    print(f"Min price: {min(all_prices)}")
    print(f"Max price: {max(all_prices)}")
    print(f"Avg price: {sum(all_prices)/len(all_prices):.2f}")
    
    # Count by ranges
    ranges = {
        '0-10': 0,
        '10-20': 0,
        '20-30': 0,
        '30-40': 0,
        '40-50': 0,
        '50-60': 0,
        '60-70': 0,
        '70-80': 0,
        '80-90': 0,
        '90-100': 0
    }
    
    for price in all_prices:
        if price <= 10:
            ranges['0-10'] += 1
        elif price <= 20:
            ranges['10-20'] += 1
        elif price <= 30:
            ranges['20-30'] += 1
        elif price <= 40:
            ranges['30-40'] += 1
        elif price <= 50:
            ranges['40-50'] += 1
        elif price <= 60:
            ranges['50-60'] += 1
        elif price <= 70:
            ranges['60-70'] += 1
        elif price <= 80:
            ranges['70-80'] += 1
        elif price <= 90:
            ranges['80-90'] += 1
        else:
            ranges['90-100'] += 1
    
    print("\nPrice distribution:")
    for range_name, count in ranges.items():
        if count > 0:
            print(f"  {range_name}: {count} markets")