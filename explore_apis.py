import requests
import json
from datetime import datetime

# Test Gamma API
print("=== Testing Gamma API ===")
try:
    response = requests.get("https://gamma-api.polymarket.com/markets?limit=1")
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Sample market structure:")
    print(json.dumps(data[0] if isinstance(data, list) else data, indent=2)[:2000])
except Exception as e:
    print(f"Error: {e}")

print("\n=== Testing CLOB API ===")
# Need to find a market ID first from Gamma
try:
    markets_response = requests.get("https://gamma-api.polymarket.com/markets?limit=5&closed=true")
    markets = markets_response.json()
    
    if markets and len(markets) > 0:
        market = markets[0]
        print(f"Testing with market: {market.get('question', 'Unknown')}")
        
        # Try to get price history
        # CLOB API typically uses condition_id or token_id
        if 'tokens' in market and market['tokens']:
            token_id = market['tokens'][0].get('token_id')
            print(f"Token ID: {token_id}")
            
            # Try prices-history endpoint
            prices_url = f"https://clob.polymarket.com/prices-history?market={token_id}&interval=1h"
            print(f"Trying: {prices_url}")
            prices_response = requests.get(prices_url, timeout=10)
            print(f"Status: {prices_response.status_code}")
            if prices_response.status_code == 200:
                prices_data = prices_response.json()
                print(f"Price history structure:")
                print(json.dumps(prices_data, indent=2)[:1000])
except Exception as e:
    print(f"Error: {e}")

print("\n=== Checking available parameters ===")
try:
    # Test date filtering
    response = requests.get("https://gamma-api.polymarket.com/markets?limit=5&closed=true&order=start_date_min")
    print(f"Markets with date ordering: {response.status_code}")
    
    # Check what fields are available
    if response.status_code == 200:
        market = response.json()[0]
        print(f"\nAvailable fields in market:")
        print(json.dumps(list(market.keys()), indent=2))
except Exception as e:
    print(f"Error: {e}")
