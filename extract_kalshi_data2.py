import json
import re

# Read the HTML file
with open("kalshi_page.html", "r", encoding="utf-8") as f:
    content = f.read()

# I saw "pages" data in the script, let me look for it more carefully
# The data seems to be in a script with self.__next_f.push

# Look for any JSON-like data with market information
patterns = [
    r'\"markets\"\s*:\s*\[(.*?)\]',
    r'\"ticker\"\s*:\s*\"([^\"]+)\"',
    r'\"yes_bid\"\s*:\s*(\d+)',
    r'\"series_title\"\s*:\s*\"([^\"]+)\"',
]

print("Searching for market patterns...")

# Let me try to extract all script content that might contain market data
script_pattern = r'<script[^>]*>(.*?)</script>'
scripts = re.findall(script_pattern, content, re.DOTALL | re.IGNORECASE)

print(f"Found {len(scripts)} script tags")

# Look for scripts containing market data
market_scripts = []
for i, script in enumerate(scripts):
    if 'ticker' in script.lower() or 'market' in script.lower() or 'yes_bid' in script.lower():
        market_scripts.append((i, script[:500]))  # Store first 500 chars
        print(f"\nScript {i} contains market keywords (first 500 chars):")
        print(script[:500])

print(f"\nFound {len(market_scripts)} scripts with market keywords")

# Now let me try to find the actual data by looking for the pattern I saw
# I saw: "pages":[{"current_page":[{"series_ticker":"KXGOVTSHUTDOWN"...
# Let me search for this pattern specifically
pages_pattern = r'\"pages\"\s*:\s*\[(.*?)\]'
pages_matches = re.findall(pages_pattern, content, re.DOTALL)

print(f"\nFound {len(pages_matches)} 'pages' matches")

if pages_matches:
    # Take the first match and try to extract more context
    pages_match = pages_matches[0]
    print(f"First pages match length: {len(pages_match)} chars")
    print(f"First 500 chars of match: {pages_match[:500]}...")
    
    # Try to reconstruct the full JSON
    # Look for the start of this object
    start_idx = content.find('"pages":[')
    if start_idx > 0:
        # Go back to find the opening brace
        brace_count = 0
        for i in range(start_idx, max(0, start_idx - 1000), -1):
            if content[i] == '{':
                brace_count += 1
                if brace_count == 1:
                    start = i
                    break
            elif content[i] == '}':
                brace_count -= 1
        
        # Now find the end
        if 'start' in locals():
            brace_count = 0
            for i in range(start, min(len(content), start + 10000)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            if 'end' in locals():
                json_str = content[start:end]
                print(f"\nExtracted JSON string (length: {len(json_str)})")
                
                try:
                    data = json.loads(json_str)
                    print("Successfully parsed JSON!")
                    
                    # Now extract market data
                    if 'pages' in data:
                        market_data = []
                        for page in data['pages']:
                            if 'current_page' in page:
                                for item in page['current_page']:
                                    if isinstance(item, dict) and 'markets' in item:
                                        series_title = item.get('series_title', 'Unknown')
                                        category = item.get('category', 'Unknown')
                                        
                                        for market in item['markets']:
                                            market_info = {
                                                'ticker': market.get('ticker', ''),
                                                'title': f"{series_title} - {market.get('yes_subtitle', '')}",
                                                'yes_bid': market.get('yes_bid', 0),
                                                'yes_ask': market.get('yes_ask', 0),
                                                'volume': market.get('volume', 0),
                                                'category': category
                                            }
                                            market_data.append(market_info)
                        
                        print(f"\nExtracted {len(market_data)} markets")
                        
                        # Filter and save
                        filtered = [m for m in market_data if m['yes_bid'] > 0 and m['yes_ask'] > 0 and m['volume'] > 100]
                        print(f"Filtered to {len(filtered)} markets (bid/ask > 0, volume > 100)")
                        
                        # Save to file
                        with open("kalshi_markets_extracted.json", "w") as f:
                            json.dump(filtered, f, indent=2)
                        
                        # Print sample
                        print("\nSample markets:")
                        for i, m in enumerate(filtered[:5]):
                            print(f"{i+1}. {m['ticker']}")
                            print(f"   Title: {m['title']}")
                            print(f"   Bid/Ask: {m['yes_bid']}/{m['yes_ask']}")
                            print(f"   Volume: {m['volume']}")
                            print(f"   Category: {m['category']}")
                            print()
                            
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"First 200 chars of JSON: {json_str[:200]}")
                    print(f"Last 200 chars of JSON: {json_str[-200:]}")
                    
                    # Try to fix common issues
                    # Remove trailing commas
                    json_str_fixed = re.sub(r',\s*}', '}', json_str)
                    json_str_fixed = re.sub(r',\s*]', ']', json_str_fixed)
                    
                    try:
                        data = json.loads(json_str_fixed)
                        print("Fixed JSON and parsed successfully!")
                    except:
                        print("Could not fix JSON")