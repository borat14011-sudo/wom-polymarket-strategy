import requests
import json
import time

api_key = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

def test_api_with_retry(url, max_retries=3, initial_delay=1):
    """Test API endpoint with exponential backoff retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries} for {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                return response
            else:
                print(f"Error: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        
        # Exponential backoff
        if attempt < max_retries - 1:
            delay = initial_delay * (2 ** attempt)
            print(f"Waiting {delay} seconds before retry...")
            time.sleep(delay)
    
    return None

# Test the new API endpoint
print("=== Testing Kalshi Elections API ===")
base_url = "https://api.elections.kalshi.com/trade-api/v2"

# Test endpoints
endpoints = [
    f"{base_url}/events",
    f"{base_url}/markets",
    f"{base_url}/markets?limit=10",
    f"{base_url}/user/balance"
]

for endpoint in endpoints:
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    response = test_api_with_retry(endpoint)
    
    if response and response.status_code == 200:
        data = response.json()
        print(f"Success! Response keys: {list(data.keys())}")
        
        if 'events' in data:
            print(f"Number of events: {len(data['events'])}")
            if data['events']:
                event = data['events'][0]
                print(f"Sample event: {event.get('event_ticker')} - {event.get('title')}")
        
        elif 'markets' in data:
            print(f"Number of markets: {len(data['markets'])}")
            if data['markets']:
                market = data['markets'][0]
                print(f"Sample market: {market.get('ticker')} - {market.get('title')}")
                print(f"Yes price: {market.get('yes_price')}, No price: {market.get('no_price')}")
        
        elif 'balance_cents' in data:
            print(f"Balance: ${data['balance_cents'] / 100:.2f}")
    
    elif response:
        print(f"Failed with status: {response.status_code}")
    else:
        print("All retries failed")

# Also test the old endpoints for comparison
print(f"\n{'='*60}")
print("Testing old endpoints for comparison:")
old_endpoints = [
    "https://api.kalshi.com/trade-api/v2/markets",
    "https://trading-api.kalshi.com/trade-api/v2/markets"
]

for endpoint in old_endpoints:
    print(f"\nTesting: {endpoint}")
    try:
        response = requests.get(endpoint, headers=headers, timeout=5)
        print(f"Status: {response.status_code}, Response: {response.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")