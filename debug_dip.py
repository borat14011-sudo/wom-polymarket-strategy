import json
from datetime import datetime, timezone

# Load the data
with open('kalshi_markets_raw.json', 'r', encoding='utf-8-sig') as f:
    markets = json.load(f)

# Check a few markets with price drops
print("Checking markets with price drops...")
count = 0
for market in markets[:50]:  # Check first 50
    status = market.get('status', '').lower()
    if status != 'active':
        continue
    
    daily_drop = market.get('daily_change_pct', 0)
    weekly_drop = market.get('weekly_change_pct', 0)
    
    max_drop = 0
    if daily_drop < 0:
        max_drop = abs(daily_drop)
    if weekly_drop < 0 and abs(weekly_drop) > max_drop:
        max_drop = abs(weekly_drop)
    
    if max_drop > 10:
        count += 1
        print(f"\n{count}. {market.get('ticker_name')}")
        print(f"   Daily change: {daily_drop}%")
        print(f"   Weekly change: {weekly_drop}%")
        print(f"   Max drop: {max_drop}%")
        print(f"   Yes bid: {market.get('yes_bid')}¢")
        print(f"   Status: {market.get('status')}")

print(f"\nFound {count} markets with >10% drops in first 50 active markets")