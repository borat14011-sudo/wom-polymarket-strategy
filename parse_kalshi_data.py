import json
import re

# Read the HTML file
with open("kalshi_page.html", "r", encoding="utf-8") as f:
    content = f.read()

# The data is in self.__next_f.push calls
# Look for the pattern: self.__next_f.push([1, "..."])
pattern = r'self\.__next_f\.push\(\[1,"(.*?)"\]\)'

matches = re.findall(pattern, content, re.DOTALL)
print(f"Found {len(matches)} self.__next_f.push calls")

# Look for the one with market data (contains "pages" and "markets")
market_data_script = None
for i, match in enumerate(matches):
    if '"pages"' in match and '"markets"' in match:
        print(f"\nFound market data in push call {i}")
        market_data_script = match
        break

if market_data_script:
    # The data seems to be encoded, let me try to extract the JSON part
    # Look for the JSON structure starting with {"pages":
    json_pattern = r'\{"pages".*?\}'
    json_matches = re.findall(json_pattern, market_data_script, re.DOTALL)
    
    if json_matches:
        print(f"Found {len(json_matches)} JSON matches")
        
        # Try to parse each JSON match
        for i, json_str in enumerate(json_matches[:3]):
            try:
                # Clean up the JSON string - remove escape sequences
                json_str_clean = json_str.replace('\\"', '"').replace('\\\\', '\\')
                
                # Try to parse
                data = json.loads(json_str_clean)
                print(f"\nSuccessfully parsed JSON match {i}")
                
                # Extract market data
                market_data = []
                if 'pages' in data:
                    for page in data['pages']:
                        if 'current_page' in page:
                            for item in page['current_page']:
                                if isinstance(item, dict) and 'markets' in item:
                                    series_title = item.get('series_title', 'Unknown')
                                    category = item.get('category', 'Unknown')
                                    
                                    # Check if this is a non-sports category
                                    non_sports_categories = ['Politics', 'Economics', 'Climate', 'Entertainment', 'Technology']
                                    if category in non_sports_categories:
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
                
                print(f"Extracted {len(market_data)} markets from this JSON")
                
                # Filter: active (bid/ask > 0), volume > 100
                filtered = [
                    m for m in market_data 
                    if m['yes_bid'] > 0 and m['yes_ask'] > 0 and m['volume'] > 100
                ]
                
                print(f"Filtered to {len(filtered)} markets (bid/ask > 0, volume > 100)")
                
                # Save to file
                with open(f"kalshi_markets_batch_{i}.json", "w") as f:
                    json.dump(filtered, f, indent=2)
                
                # Print sample
                print("\nSample markets:")
                for j, m in enumerate(filtered[:5]):
                    print(f"{j+1}. {m['ticker']}")
                    print(f"   Title: {m['title']}")
                    print(f"   Bid/Ask: {m['yes_bid']}/{m['yes_ask']} ({m['yes_bid']/100:.2f}¢/{m['yes_ask']/100:.2f}¢)")
                    print(f"   Volume: {m['volume']:,}")
                    print(f"   Category: {m['category']}")
                    print()
                    
            except json.JSONDecodeError as e:
                print(f"JSON decode error for match {i}: {e}")
                print(f"First 200 chars: {json_str[:200]}")
    else:
        print("Could not find JSON structure in the script")
        
        # Let me try a different approach - look for the data more directly
        # The data I saw earlier was in the output
        # Let me search for specific patterns
        print("\nTrying direct pattern matching...")
        
        # Look for market entries
        market_pattern = r'\{"ticker":"([^"]+)","yes_subtitle":"([^"]*)".*?"yes_bid":(\d+).*?"yes_ask":(\d+).*?"volume":(\d+)'
        market_matches = re.findall(market_pattern, market_data_script, re.DOTALL)
        
        print(f"Found {len(market_matches)} direct market matches")
        
        if market_matches:
            # Try to get category info too
            category_pattern = r'"category":"([^"]+)"'
            category_matches = re.findall(category_pattern, market_data_script)
            
            print(f"Found {len(category_matches)} category references")
            
            # Create simple market list
            simple_markets = []
            for i, match in enumerate(market_matches[:20]):  # First 20
                ticker, subtitle, yes_bid, yes_ask, volume = match
                category = category_matches[i] if i < len(category_matches) else "Unknown"
                
                # Filter
                if int(yes_bid) > 0 and int(yes_ask) > 0 and int(volume) > 100:
                    simple_markets.append({
                        'ticker': ticker,
                        'title': f"Market - {subtitle}" if subtitle else ticker,
                        'yes_bid': int(yes_bid),
                        'yes_ask': int(yes_ask),
                        'volume': int(volume),
                        'category': category
                    })
            
            print(f"\nCreated {len(simple_markets)} simple market entries")
            
            # Save
            with open("kalshi_simple_markets.json", "w") as f:
                json.dump(simple_markets, f, indent=2)
            
            # Print
            for i, m in enumerate(simple_markets[:10]):
                print(f"{i+1}. {m['ticker']}")
                print(f"   Title: {m['title']}")
                print(f"   Bid/Ask: {m['yes_bid']}/{m['yes_ask']}")
                print(f"   Volume: {m['volume']:,}")
                print(f"   Category: {m['category']}")
                print()
else:
    print("Could not find market data in any push call")