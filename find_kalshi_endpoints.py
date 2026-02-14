import requests
import re

# Try different Kalshi URLs
urls = [
    "https://kalshi.com",
    "https://kalshi.com/exchange",
    "https://kalshi.com/trading",
    "https://kalshi.com/api/v1/markets",
    "https://kalshi.com/api/markets",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

for url in urls:
    print(f"\nTrying: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Look for API endpoints or market data in the page
            content = response.text
            # Find all URLs in the page
            urls_in_page = re.findall(r'https?://[^\s"\'<>]+', content)
            api_urls = [u for u in urls_in_page if 'api' in u.lower() and 'kalshi' in u.lower()]
            if api_urls:
                print(f"Found API URLs: {api_urls[:5]}")
                
            # Look for market data
            if 'market' in content.lower() or 'ticker' in content.lower():
                print("Page contains market-related content")
                
    except Exception as e:
        print(f"Error: {e}")