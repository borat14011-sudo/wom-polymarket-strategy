import requests
import json
import time

print("=== TESTING API AFTER VPN DISCONNECT ===")
print("Timestamp:", time.strftime("%Y-%m-%d %H:%M:%S"))
print()

# Test 1: Public API
print("1. Testing Public API (api.kalshi.com/v1/markets)...")
try:
    start = time.time()
    response = requests.get('https://api.kalshi.com/v1/markets', timeout=15)
    elapsed = time.time() - start
    
    print(f"   Status: {response.status_code}")
    print(f"   Response time: {elapsed:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        markets = data.get('markets', [])
        print(f"   ✅ SUCCESS! Found {len(markets)} markets")
        
        if markets:
            # Show first few markets
            print(f"   Sample markets:")
            for i, market in enumerate(markets[:3]):
                print(f"     {i+1}. {market.get('ticker')} - {market.get('title')[:50]}...")
                print(f"        Price: {market.get('yes_price')}¢ | Status: {market.get('status')}")
    else:
        print(f"   ❌ Error: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Exception: {str(e)[:100]}")

print()

# Test 2: Events endpoint
print("2. Testing Events API (api.kalshi.com/v1/events)...")
try:
    response = requests.get('https://api.kalshi.com/v1/events', timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        events = data.get('events', [])
        print(f"   ✅ Found {len(events)} events")
    else:
        print(f"   Response: {response.text[:150]}")
        
except Exception as e:
    print(f"   ❌ Exception: {str(e)[:100]}")

print()

# Test 3: Trading API with our key
print("3. Testing Trading API with our key...")
try:
    headers = {'Authorization': 'Bearer 14a525cf-42d7-4746-8e36-30a8d9c17c96'}
    response = requests.get('https://trading-api.kalshi.com/trade-api/v2/events', 
                           headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Trading API works!")
    elif response.status_code == 401:
        print(f"   ⚠️ Auth failed (expected - needs login credentials)")
    else:
        print(f"   Response: {response.text[:150]}")
        
except Exception as e:
    print(f"   ❌ Exception: {str(e)[:100]}")

print()
print("=== TEST COMPLETE ===")