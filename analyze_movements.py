import json
import codecs

# Read file with UTF-8 encoding, handling BOM if present
with codecs.open('kalshi_markets_raw.json', 'r', 'utf-8-sig') as f:
    data = json.load(f)

print("Markets with large recent price movements (weekly change > 50%):")
print("=" * 100)

large_movements = []
for market in data:
    if market.get('status') == 'active' and market.get('last_price') is not None:
        price = market['last_price']
        weekly_change = market.get('weekly_change_pct')
        
        if weekly_change is not None and abs(weekly_change) > 50:
            large_movements.append((market, weekly_change))

# Sort by absolute change
large_movements.sort(key=lambda x: abs(x[1]), reverse=True)

print(f"Total markets with >50% weekly change: {len(large_movements)}")
print()

for market, change in large_movements[:30]:  # Top 30
    price = market['last_price']
    print(f"Ticker: {market['ticker_name']}")
    print(f"Title: {market['title']}")
    print(f"Name: {market['name']}")
    print(f"Last Price: {price}% (Weekly change: {change}%)")
    
    # Highlight potential near-certainties
    if 70 <= price <= 85 and change > 0:
        print("*** POTENTIAL NEAR-CERTAINTY: Price in target range with positive momentum ***")
    
    print(f"Category: {market['category']}")
    print(f"Volume: {market['volume']}")
    print("-" * 80)

# Look specifically for markets that have moved UP significantly but still below 90%
print("\n\nMarkets that have moved UP >50% weekly but still below 90%:")
print("=" * 100)

up_movers = []
for market in data:
    if market.get('status') == 'active' and market.get('last_price') is not None:
        price = market['last_price']
        weekly_change = market.get('weekly_change_pct')
        
        if weekly_change is not None and weekly_change > 50 and price < 90:
            up_movers.append((market, weekly_change))

up_movers.sort(key=lambda x: x[1], reverse=True)

for market, change in up_movers[:20]:
    price = market['last_price']
    print(f"Ticker: {market['ticker_name']}")
    print(f"Title: {market['title']}")
    print(f"Name: {market['name']}")
    print(f"Last Price: {price}% (Weekly change: {change}%)")
    
    # Check if this might be approaching certainty
    if price >= 70:
        print("*** IN TARGET RANGE 70-85% ***")
    
    print(f"Category: {market['category']}")
    print(f"Volume: {market['volume']}")
    print("-" * 60)