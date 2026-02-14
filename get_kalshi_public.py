import requests
import json
import re

# Get the main Kalshi page and look for data
url = "https://kalshi.com"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

try:
    print("Fetching Kalshi homepage...")
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        
        # Save for inspection
        with open("kalshi_page.html", "w", encoding="utf-8") as f:
            f.write(content[:50000])  # First 50k chars
        
        print("Saved page content to kalshi_page.html")
        
        # Look for JSON data in script tags
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, content, re.DOTALL | re.IGNORECASE)
        
        print(f"Found {len(scripts)} script tags")
        
        market_data_found = False
        for i, script in enumerate(scripts[:20]):  # Check first 20 scripts
            if 'market' in script.lower() or 'ticker' in script.lower() or 'prediction' in script.lower():
                print(f"\nScript {i} contains market keywords")
                # Try to find JSON
                json_patterns = [
                    r'\{.*"markets".*\}',
                    r'\{.*"ticker".*\}',
                    r'\[.*\{.*"title".*\}.*\]'
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, script, re.DOTALL)
                    for match in matches[:3]:  # Check first 3 matches
                        try:
                            data = json.loads(match)
                            print(f"Found JSON data: {type(data)}")
                            if isinstance(data, dict) and 'markets' in data:
                                print(f"Found markets data with {len(data['markets'])} markets")
                                market_data_found = True
                                # Save the data
                                with open("kalshi_markets.json", "w") as f:
                                    json.dump(data, f, indent=2)
                                break
                            elif isinstance(data, list) and len(data) > 0 and 'title' in data[0]:
                                print(f"Found list data with {len(data)} items")
                                market_data_found = True
                                with open("kalshi_markets_list.json", "w") as f:
                                    json.dump(data, f, indent=2)
                                break
                        except json.JSONDecodeError:
                            continue
                    if market_data_found:
                        break
            if market_data_found:
                break
                
        if not market_data_found:
            print("\nCould not find market data in scripts, looking for other patterns...")
            # Look for inline data attributes
            data_patterns = [
                r'data-markets=\'([^\']+)\'',
                r'data-markets="([^"]+)"',
                r'initialState\s*=\s*(\{.*?\})',
                r'__INITIAL_STATE__\s*=\s*(\{.*?\})'
            ]
            
            for pattern in data_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    print(f"Found pattern: {pattern}")
                    for match in matches[:2]:
                        try:
                            # Try to decode if it's URL encoded
                            decoded = match
                            if '%' in match:
                                import urllib.parse
                                decoded = urllib.parse.unquote(match)
                            
                            data = json.loads(decoded)
                            print(f"Found data: {type(data)}")
                            with open(f"kalshi_pattern_{hash(pattern)}.json", "w") as f:
                                json.dump(data, f, indent=2)
                            break
                        except:
                            print(f"Could not parse as JSON: {match[:100]}...")
                            
    else:
        print(f"Failed to fetch page: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()