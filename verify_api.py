import requests
import json
import time

api_key = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

def make_request_with_retry(url, max_retries=3, timeout=10):
    """Make HTTP request with exponential backoff retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: {url}")
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                return response
            else:
                print(f"HTTP {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {type(e).__name__}: {e}")
        
        # Exponential backoff
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1, 2, 4 seconds
            print(f"Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    return None

# Test the API
print("=== Testing Kalshi API Connectivity ===")
base_url = "https://api.elections.kalshi.com/trade-api/v2"

# Test basic endpoints
test_endpoints = [
    f"{base_url}/markets?limit=5",
    f"{base_url}/events?limit=3",
    f"{base_url}/user/balance"
]

for endpoint in test_endpoints:
    print(f"\n{'='*60}")
    response = make_request_with_retry(endpoint)
    
    if response:
        data = response.json()
        print(f"SUCCESS: {endpoint}")
        
        if 'markets' in data:
            markets = data['markets']
            print(f"Found {len(markets)} markets")
            for i, market in enumerate(markets[:2]):
                print(f"  {i+1}. {market.get('ticker')}: {market.get('title')}")
                print(f"     Yes: {market.get('yes_price', 'N/A')}, No: {market.get('no_price', 'N/A')}")
        
        elif 'events' in data:
            events = data['events']
            print(f"Found {len(events)} events")
            for i, event in enumerate(events[:2]):
                print(f"  {i+1}. {event.get('event_ticker')}: {event.get('title')}")
        
        elif 'balance_cents' in data:
            balance = data['balance_cents'] / 100
            print(f"Account balance: ${balance:.2f}")
        
        else:
            print(f"Response keys: {list(data.keys())}")
    else:
        print(f"FAILED: All retries exhausted for {endpoint}")

# Test pagination with cursor
print(f"\n{'='*60}")
print("Testing pagination with cursor...")
response = make_request_with_retry(f"{base_url}/markets?limit=2")
if response and response.status_code == 200:
    data = response.json()
    print(f"First page: {len(data.get('markets', []))} markets")
    print(f"Cursor: {data.get('cursor', 'No cursor')[:50]}...")
    
    # Test next page if cursor exists
    if data.get('cursor'):
        next_url = f"{base_url}/markets?limit=2&cursor={data['cursor']}"
        print(f"\nFetching next page...")
        next_response = make_request_with_retry(next_url)
        if next_response and next_response.status_code == 200:
            next_data = next_response.json()
            print(f"Second page: {len(next_data.get('markets', []))} markets")
            if next_data.get('markets'):
                print(f"First market on page 2: {next_data['markets'][0].get('ticker')}")

print(f"\n{'='*60}")
print("API Connectivity Test Complete!")