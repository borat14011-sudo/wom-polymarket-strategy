import requests
from bs4 import BeautifulSoup
import json
import re

# Try to scrape Kalshi markets page
url = "https://kalshi.com/markets"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for market data in script tags
        scripts = soup.find_all('script')
        market_data = []
        
        for script in scripts:
            if script.string:
                # Look for JSON data or market information
                content = script.string
                # Try to find market data patterns
                if 'ticker' in content.lower() or 'market' in content.lower():
                    print(f"Found script with market keywords: {content[:200]}...")
                    
                    # Try to extract JSON
                    json_pattern = r'\{.*"markets".*\}'
                    matches = re.findall(json_pattern, content, re.DOTALL)
                    for match in matches:
                        try:
                            data = json.loads(match)
                            if 'markets' in data:
                                print(f"Found markets data with {len(data['markets'])} markets")
                                market_data.append(data)
                        except:
                            pass
        
        if not market_data:
            print("No market data found in scripts, trying to find market listings in HTML")
            # Look for market cards or listings
            market_elements = soup.find_all(class_=re.compile(r'market|ticker|prediction', re.I))
            print(f"Found {len(market_elements)} potential market elements")
            
    else:
        print(f"Failed to fetch page: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")