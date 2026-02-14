import re

# Read the HTML file
with open("kalshi_page.html", "r", encoding="utf-8") as f:
    content = f.read()

# Look for market data patterns
print("Searching for market data patterns...")

# Look for ticker patterns (like KXGOVTSHUTDOWN-26FEB14)
ticker_pattern = r'([A-Z0-9]+-[A-Z0-9]+(?:-[A-Z0-9]+)?)'
tickers = re.findall(ticker_pattern, content)
print(f"Found {len(tickers)} potential tickers")

# Filter for likely market tickers (contain dash and have reasonable length)
market_tickers = [t for t in tickers if '-' in t and 10 <= len(t) <= 30]
print(f"Filtered to {len(market_tickers)} likely market tickers")

# Look for yes_bid/yes_ask patterns
bid_pattern = r'"yes_bid":(\d+)'
ask_pattern = r'"yes_ask":(\d+)'
volume_pattern = r'"volume":(\d+)'
category_pattern = r'"category":"([^"]+)"'
title_pattern = r'"series_title":"([^"]+)"'

bids = re.findall(bid_pattern, content)
asks = re.findall(ask_pattern, content)
volumes = re.findall(volume_pattern, content)
categories = re.findall(category_pattern, content)
titles = re.findall(title_pattern, content)

print(f"\nFound:")
print(f"  {len(bids)} yes_bid values")
print(f"  {len(asks)} yes_ask values")
print(f"  {len(volumes)} volume values")
print(f"  {len(categories)} categories: {set(categories)}")
print(f"  {len(titles)} series titles")

# Try to extract complete market entries
# Look for pattern: "ticker":"...","yes_subtitle":"...","yes_bid":...,"yes_ask":...,"volume":...
market_entry_pattern = r'"ticker":"([^"]+)".*?"yes_subtitle":"([^"]*)".*?"yes_bid":(\d+).*?"yes_ask":(\d+).*?"volume":(\d+)'
market_entries = re.findall(market_entry_pattern, content, re.DOTALL)

print(f"\nFound {len(market_entries)} complete market entries")

# Create a list of markets
markets = []
for i, entry in enumerate(market_entries[:50]):  # First 50
    ticker, subtitle, yes_bid, yes_ask, volume = entry
    
    # Get category if available
    category = categories[i] if i < len(categories) else "Unknown"
    
    # Get title if available
    title = titles[i] if i < len(titles) else f"Market {ticker}"
    
    markets.append({
        'ticker': ticker,
        'title': f"{title} - {subtitle}" if subtitle else title,
        'yes_bid': int(yes_bid),
        'yes_ask': int(yes_ask),
        'volume': int(volume),
        'category': category
    })

print(f"\nCreated {len(markets)} market entries")

# Filter for non-sports categories with volume > 100 and bid/ask > 0
non_sports_categories = ['Politics', 'Economics', 'Climate', 'Entertainment', 'Technology']
filtered_markets = []

for market in markets:
    if (market['category'] in non_sports_categories and 
        market['yes_bid'] > 0 and 
        market['yes_ask'] > 0 and 
        market['volume'] > 100):
        filtered_markets.append(market)

print(f"\nFiltered to {len(filtered_markets)} markets (non-sports, bid/ask > 0, volume > 100)")

# Save to file
import json
with open("kalshi_filtered_markets.json", "w") as f:
    json.dump(filtered_markets, f, indent=2)

# Print results
print("\n=== KALSHI PREDICTION MARKET SCAN RESULTS ===")
print(f"Total markets found: {len(filtered_markets)}")
print("\nMarkets by category:")
category_counts = {}
for market in filtered_markets:
    category = market['category']
    category_counts[category] = category_counts.get(category, 0) + 1

for category, count in sorted(category_counts.items()):
    print(f"  {category}: {count} markets")

print("\nTop 20 markets by volume:")
sorted_markets = sorted(filtered_markets, key=lambda x: x['volume'], reverse=True)
for i, market in enumerate(sorted_markets[:20]):
    print(f"{i+1:2d}. {market['ticker']:30} {market['title'][:50]:50} "
          f"Bid/Ask: {market['yes_bid']:3d}/{market['yes_ask']:3d} "
          f"Vol: {market['volume']:12,} "
          f"Cat: {market['category']}")

# Also create a CSV format for easy viewing
print("\n\nCSV Format (ticker, title, yes_bid, yes_ask, volume, category):")
for market in sorted_markets[:50]:
    print(f"{market['ticker']}, \"{market['title']}\", {market['yes_bid']}, {market['yes_ask']}, {market['volume']}, {market['category']}")