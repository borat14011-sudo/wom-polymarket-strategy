import requests
import json

api_key = "14a525cf-42d7-4746-8e36-30a8d9c17c96"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Based on the documentation, try the correct endpoint structure
# The docs show example at docs.kalshi.com/api-reference/market/get-markets
# Let me try to find the actual API base URL

# First, let me check if there's CORS or preflight issue
test_urls = [
    "https://api.kalshi.com/v1/markets",
    "https://api.kalshi.com/trade-api/v2/markets",
    "https://api.kalshi.com/trade-api/v1/markets",
    "https://kalshi.com/api/v1/markets",
]

for url in test_urls:
    print(f"\nTesting: {url}")
    try:
        # First try OPTIONS to check CORS
        options_response = requests.options(url, headers=headers, timeout=5)
        print(f"OPTIONS Status: {options_response.status_code}")
        
        # Then try GET
        response = requests.get(url, headers=headers, timeout=10)
        print(f"GET Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Found {len(data.get('markets', []))} markets")
            if data.get('markets'):
                print(f"First market ticker: {data['markets'][0].get('ticker')}")
                print(f"First market title: {data['markets'][0].get('title')}")
            break
        elif response.status_code == 401:
            print("Unauthorized - API key issue")
        elif response.status_code == 403:
            print("Forbidden")
        else:
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Error: {e}")