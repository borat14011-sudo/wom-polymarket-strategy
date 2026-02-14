import json
import codecs

# Read file with UTF-8 encoding, handling BOM if present
with codecs.open('kalshi_markets_raw.json', 'r', 'utf-8-sig') as f:
    data = json.load(f)

print("Sports-related markets:")
print("=" * 100)

sports_keywords = ['NBA', 'NFL', 'MLB', 'NHL', 'Super Bowl', 'championship', 'playoff', 'team', 'sports', 'football', 'basketball', 'baseball', 'hockey']
sports_markets = []

for market in data:
    title = market.get('title', '').lower()
    category = market.get('category', '').lower()
    
    for keyword in sports_keywords:
        if keyword.lower() in title or keyword.lower() in category:
            sports_markets.append(market)
            break

print(f"Total sports markets found: {len(sports_markets)}")
print()

# Look for active sports markets with prices in our target range
target_sports = []
for market in sports_markets:
    if market.get('status') == 'active' and market.get('last_price') is not None:
        price = market['last_price']
        if 70 <= price <= 85:
            target_sports.append(market)

print(f"Active sports markets priced 70-85%: {len(target_sports)}")
print()

for market in target_sports:
    print(f"Ticker: {market['ticker_name']}")
    print(f"Title: {market['title']}")
    print(f"Name: {market['name']}")
    print(f"Last Price: {market['last_price']}%")
    print(f"Category: {market['category']}")
    print(f"Close Date: {market['close_date']}")
    print("-" * 80)

# Also look for any sports markets that might be obvious based on current season status
print("\n\nAll active sports markets (for reference):")
print("=" * 100)

for market in sports_markets:
    if market.get('status') == 'active':
        print(f"Ticker: {market['ticker_name']}")
        print(f"Title: {market['title']}")
        print(f"Name: {market['name']}")
        if market.get('last_price') is not None:
            print(f"Last Price: {market['last_price']}%")
        print(f"Category: {market['category']}")
        print(f"Close Date: {market['close_date']}")
        print("-" * 60)