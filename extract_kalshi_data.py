import json
import re

# Read the HTML file
with open("kalshi_page.html", "r", encoding="utf-8") as f:
    content = f.read()

# Look for the JSON data pattern - I saw "pages" array in the data
# The data seems to be in a script tag with JSON
pattern = r'\"pages\"\s*:\s*\[(.*?)\]'

# Try to find the full JSON structure
# Look for the larger JSON object containing "pages"
full_pattern = r'\{.*\"pages\"\s*:\s*\[.*?\].*?\}'

matches = re.findall(full_pattern, content, re.DOTALL)
print(f"Found {len(matches)} potential JSON matches")

market_data = []

for i, match in enumerate(matches[:5]):  # Check first 5 matches
    try:
        # Try to parse as JSON
        data = json.loads(match)
        if 'pages' in data:
            print(f"\nMatch {i}: Found pages data")
            pages = data['pages']
            for page in pages:
                if 'current_page' in page:
                    for item in page['current_page']:
                        if 'markets' in item:
                            print(f"  Found series: {item.get('series_title', 'Unknown')}")
                            print(f"  Category: {item.get('category', 'Unknown')}")
                            print(f"  Markets: {len(item['markets'])}")
                            
                            for market in item['markets']:
                                market_info = {
                                    'ticker': market.get('ticker', ''),
                                    'title': item.get('series_title', '') + ' - ' + market.get('yes_subtitle', ''),
                                    'yes_bid': market.get('yes_bid', 0),
                                    'yes_ask': market.get('yes_ask', 0),
                                    'volume': market.get('volume', 0),
                                    'category': item.get('category', '')
                                }
                                market_data.append(market_info)
    except json.JSONDecodeError as e:
        # Try to fix common JSON issues
        try:
            # Sometimes the JSON might be truncated, try to find the end
            if match.count('{') > match.count('}'):
                # Add missing closing braces
                match += '}' * (match.count('{') - match.count('}'))
                data = json.loads(match)
                if 'pages' in data:
                    print(f"\nMatch {i} (fixed): Found pages data")
        except:
            pass

print(f"\nTotal markets extracted: {len(market_data)}")

# Filter markets based on criteria
filtered_markets = []
for market in market_data:
    # Check filters: active (yes_bid and yes_ask > 0), volume > 100
    if (market['yes_bid'] > 0 and market['yes_ask'] > 0 and 
        market['volume'] > 100):
        filtered_markets.append(market)

print(f"\nMarkets after filtering (bid/ask > 0, volume > 100): {len(filtered_markets)}")

# Save the filtered data
with open("filtered_kalshi_markets.json", "w") as f:
    json.dump(filtered_markets, f, indent=2)

print("\nFirst 10 filtered markets:")
for i, market in enumerate(filtered_markets[:10]):
    print(f"{i+1}. {market['ticker']}")
    print(f"   Title: {market['title']}")
    print(f"   Yes Bid: {market['yes_bid']} ({market['yes_bid']/100:.2f}¢)")
    print(f"   Yes Ask: {market['yes_ask']} ({market['yes_ask']/100:.2f}¢)")
    print(f"   Volume: {market['volume']}")
    print(f"   Category: {market['category']}")
    print()