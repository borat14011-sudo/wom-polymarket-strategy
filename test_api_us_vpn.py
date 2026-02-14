import requests
import json
import time
import socket

print("=== TESTING API FROM US LOCATION ===")
print("Timestamp:", time.strftime("%Y-%m-%d %H:%M:%S"))
print()

# First test DNS resolution
print("1. Testing DNS Resolution...")
try:
    ip_address = socket.gethostbyname('api.kalshi.com')
    print(f"   ✅ DNS Resolution: api.kalshi.com -> {ip_address}")
except socket.gaierror as e:
    print(f"   ❌ DNS Failed: {e}")
    print("   Trying alternative DNS...")
    try:
        # Try with Google DNS
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        answer = resolver.resolve('api.kalshi.com', 'A')
        ip_address = str(answer[0])
        print(f"   ✅ Google DNS Resolution: {ip_address}")
    except Exception as dns_e:
        print(f"   ❌ Google DNS also failed: {dns_e}")

print()

# Test 1: Public API
print("2. Testing Public API (api.kalshi.com/v1/markets)...")
try:
    start = time.time()
    response = requests.get('https://api.kalshi.com/v1/markets', 
                          timeout=20,
                          headers={
                              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                              'Accept': 'application/json'
                          })
    elapsed = time.time() - start
    
    print(f"   Status: {response.status_code}")
    print(f"   Response time: {elapsed:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        markets = data.get('markets', [])
        print(f"   ✅ SUCCESS! Found {len(markets)} markets")
        
        if markets:
            # Show first few markets
            print(f"   Sample markets (first 3):")
            for i, market in enumerate(markets[:3]):
                ticker = market.get('ticker', 'N/A')
                title = market.get('title', 'N/A')[:60]
                yes_price = market.get('yes_price', 'N/A')
                status = market.get('status', 'N/A')
                print(f"     {i+1}. {ticker}")
                print(f"        Title: {title}...")
                print(f"        Yes Price: {yes_price}¢ | Status: {status}")
                
            # Check for our top markets
            print(f"\n   Looking for our top markets...")
            top_markets = [
                "KXNEXTISRAELPM-45JAN01-YGAL",
                "KXMEDIARELEASEPRISONBREAK-30JAN01-26JUL01", 
                "KXRAMPBREX-40-BREX"
            ]
            
            found_count = 0
            for market in markets:
                if market.get('ticker') in top_markets:
                    found_count += 1
                    print(f"     Found: {market.get('ticker')} - {market.get('title')[:50]}...")
                    
            print(f"   Found {found_count}/3 of our top markets")
            
    elif response.status_code == 403:
        print(f"   ❌ 403 Forbidden - Kalshi might block this IP/region")
    elif response.status_code == 404:
        print(f"   ❌ 404 Not Found - Endpoint might have changed")
    else:
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print(f"   ❌ Request timed out after 20 seconds")
except requests.exceptions.ConnectionError as e:
    print(f"   ❌ Connection Error: {e}")
except Exception as e:
    print(f"   ❌ Exception: {str(e)[:100]}")

print()

# Test 2: Alternative endpoint
print("3. Testing Events endpoint (api.kalshi.com/v1/events)...")
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

# Test 3: Series endpoint (might work)
print("4. Testing Series endpoint (api.kalshi.com/v1/series)...")
try:
    response = requests.get('https://api.kalshi.com/v1/series', timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        series = data.get('series', [])
        print(f"   ✅ Found {len(series)} series")
    else:
        print(f"   Response: {response.text[:150]}")
        
except Exception as e:
    print(f"   ❌ Exception: {str(e)[:100]}")

print()
print("=== TEST COMPLETE ===")