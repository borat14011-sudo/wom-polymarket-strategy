import requests
import json
import time

print("=== INVESTIGATING KALSHI API ENDPOINTS ===")
print()

# Try different possible API endpoints
endpoints = [
    "https://api.kalshi.com/v1/markets",
    "https://api.kalshi.com/api/v1/markets",
    "https://kalshi.com/api/v1/markets",
    "https://www.kalshi.com/api/v1/markets",
    "https://trading-api.kalshi.com/trade-api/v2/markets",
    "https://api.kalshi.com/events",
    "https://kalshi.com/events",
    "https://api.kalshi.com/markets",
    "https://kalshi.com/markets"
]

for i, endpoint in enumerate(endpoints):
    print(f"{i+1}. Testing: {endpoint}")
    try:
        response = requests.get(endpoint, timeout=10, 
                              headers={'User-Agent': 'Mozilla/5.0'})
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ SUCCESS! Endpoint works!")
            try:
                data = response.json()
                if 'markets' in data:
                    print(f"   Found {len(data['markets'])} markets")
                elif 'events' in data:
                    print(f"   Found {len(data['events'])} events")
                else:
                    print(f"   Response keys: {list(data.keys())}")
            except:
                print(f"   Response (first 200 chars): {response.text[:200]}")
        elif response.status_code == 403:
            print(f"   ❌ 403 Forbidden")
        elif response.status_code == 404:
            print(f"   ❌ 404 Not Found")
        else:
            print(f"   Response: {response.text[:100]}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection Error: {str(e)[:80]}")
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout")
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:80]}")
    
    print()

print("=== CHECKING KALSHI WEBSITE ===")
print()

# Try to get the main website
try:
    print("Testing main website: https://kalshi.com")
    response = requests.get('https://kalshi.com', timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Website loads successfully")
        # Look for API endpoints in the page
        if 'api' in response.text.lower():
            print("   Found 'api' in page content")
        # Look for JavaScript files that might contain API endpoints
        import re
        js_files = re.findall(r'src="([^"]+\.js)"', response.text)
        print(f"   Found {len(js_files)} JavaScript files")
    else:
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {str(e)[:80]}")

print()
print("=== CHECKING DOCUMENTATION ===")
print()

# Check if there's documentation
try:
    print("Testing documentation: https://trading-api.readme.io")
    response = requests.get('https://trading-api.readme.io', timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Documentation site loads")
        if 'kalshi' in response.text.lower():
            print("   Found 'Kalshi' in documentation")
    else:
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {str(e)[:80]}")

print()
print("=== INVESTIGATION COMPLETE ===")