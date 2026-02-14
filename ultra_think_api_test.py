import requests
import json

print('=== ULTRA-THINK API TEST ===')

# Test 1: Public API (No Authentication)
print('\n1. Testing PUBLIC API (api.kalshi.com)...')
try:
    response = requests.get('https://api.kalshi.com/v1/markets', timeout=10)
    print(f'   Status Code: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        market_count = len(data.get('markets', []))
        print(f'   ✅ SUCCESS! Found {market_count} markets')
        
        if market_count > 0:
            market = data['markets'][0]
            print(f'   Sample Market:')
            print(f'     Ticker: {market.get("ticker")}')
            print(f'     Title: {market.get("title")[:60]}...')
            print(f'     Status: {market.get("status")}')
            print(f'     Yes Price: {market.get("yes_price")}')
            print(f'     No Price: {market.get("no_price")}')
    else:
        print(f'   ❌ Error: {response.text[:150]}')
except Exception as e:
    print(f'   ❌ Exception: {e}')

# Test 2: Trading API with our API Key
print('\n2. Testing TRADING API with our key...')
try:
    headers = {'Authorization': 'Bearer 14a525cf-42d7-4746-8e36-30a8d9c17c96'}
    response = requests.get('https://trading-api.kalshi.com/trade-api/v2/events', 
                           headers=headers, timeout=10)
    print(f'   Status Code: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'   ✅ SUCCESS! Trading API works!')
        print(f'   Response keys: {list(data.keys())}')
    elif response.status_code == 401:
        print(f'   ❌ AUTH FAILED: Invalid API key or expired')
        print(f'   Response: {response.text[:150]}')
    else:
        print(f'   ❌ Error {response.status_code}: {response.text[:150]}')
except Exception as e:
    print(f'   ❌ Exception: {e}')

# Test 3: Alternative endpoint
print('\n3. Testing alternative endpoint...')
try:
    response = requests.get('https://api.kalshi.com/v1/events', timeout=10)
    print(f'   Status Code: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        event_count = len(data.get('events', []))
        print(f'   ✅ Found {event_count} events')
    else:
        print(f'   Response: {response.text[:150]}')
except Exception as e:
    print(f'   ❌ Exception: {e}')

print('\n=== TEST COMPLETE ===')