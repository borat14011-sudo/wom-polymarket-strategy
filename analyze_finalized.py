import json
import codecs
from datetime import datetime

# Read file with UTF-8 encoding, handling BOM if present
with codecs.open('kalshi_markets_raw.json', 'r', 'utf-8-sig') as f:
    data = json.load(f)

print("Finalized markets that might show market lag patterns:")
print("=" * 100)

finalized_markets = []
for market in data:
    if market.get('status') == 'finalized' and market.get('last_price') is not None:
        price = market['last_price']
        # Look for markets that were likely near-certainties at resolution
        if price < 90:
            finalized_markets.append(market)

print(f"Total finalized markets with price < 90%: {len(finalized_markets)}")
print()

# Sort by volume to see most traded markets
finalized_markets.sort(key=lambda x: x.get('volume', 0), reverse=True)

for market in finalized_markets[:20]:  # Top 20 by volume
    print(f"Ticker: {market['ticker_name']}")
    print(f"Title: {market['title']}")
    print(f"Name: {market['name']}")
    print(f"Last Price: {market['last_price']}%")
    print(f"Volume: {market['volume']}")
    print(f"Close Date: {market['close_date']}")
    print("-" * 80)

# Look for markets that resolved YES but had low prices
print("\n\nMarkets that might have resolved YES despite low prices:")
print("=" * 100)

# We need to infer resolution from price patterns or external knowledge
# For now, look at markets with very low prices that might have been obvious NOs
low_price_finalized = []
for market in data:
    if market.get('status') == 'finalized' and market.get('last_price') is not None:
        price = market['last_price']
        if price < 30:  # Markets priced below 30%
            low_price_finalized.append(market)

print(f"Finalized markets priced below 30%: {len(low_price_finalized)}")
print()

for market in low_price_finalized[:10]:
    print(f"Ticker: {market['ticker_name']}")
    print(f"Title: {market['title']}")
    print(f"Name: {market['name']}")
    print(f"Last Price: {market['last_price']}%")
    print(f"Volume: {market['volume']}")
    print("-" * 60)