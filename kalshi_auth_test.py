import requests
import json
import time

print("=== KALSHI AUTHENTICATION INVESTIGATION ===\n")

# Test credentials
username = "Borat14011@gmail.com"
password = "Montenegro@"

print(f"Testing with credentials:")
print(f"Username: {username}")
print(f"Password: {password[:3]}...\n")

# Try to find login endpoint
print("1. Searching for login endpoint...")
login_endpoints = [
    "https://api.kalshi.com/trade-api/v2/login",
    "https://trading-api.kalshi.com/trade-api/v2/login",
    "https://api.kalshi.com/v1/login",
    "https://kalshi.com/api/login",
    "https://www.kalshi.com/api/login"
]

for endpoint in login_endpoints:
    print(f"\nTrying POST to: {endpoint}")
    try:
        # Try POST with credentials
        payload = {
            "email": username,
            "password": password
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ SUCCESS! Login endpoint found!")
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            
            # Check for session token
            if "token" in data:
                print(f"   Found token: {data['token'][:50]}...")
            if "access_token" in data:
                print(f"   Found access_token: {data['access_token'][:50]}...")
            if "session_token" in data:
                print(f"   Found session_token: {data['session_token'][:50]}...")
                
            # Save the response
            with open("kalshi_login_response.json", "w") as f:
                json.dump(data, f, indent=2)
            print("   Saved response to kalshi_login_response.json")
            
        elif response.status_code == 401:
            print(f"   ❌ 401 Unauthorized - Invalid credentials or endpoint")
        elif response.status_code == 404:
            print(f"   ❌ 404 Not Found - Wrong endpoint")
        else:
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error")
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout")
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:80]}")

print("\n2. Checking if we can access public endpoints without auth...")
public_endpoints = [
    "https://api.kalshi.com/v1/events",
    "https://api.kalshi.com/v1/markets",
    "https://trading-api.kalshi.com/trade-api/v2/events",
    "https://trading-api.kalshi.com/trade-api/v2/markets"
]

for endpoint in public_endpoints:
    print(f"\nTrying GET: {endpoint}")
    try:
        response = requests.get(endpoint, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Public endpoint accessible!")
            data = response.json()
            print(f"   Response type: {type(data)}")
            if isinstance(data, dict):
                print(f"   Keys: {list(data.keys())}")
        elif response.status_code == 401:
            print(f"   ❌ 401 - Requires authentication")
        elif response.status_code == 403:
            print(f"   ❌ 403 - Forbidden")
        else:
            print(f"   Response: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:80]}")

print("\n3. Checking Kalshi website for API clues...")
try:
    response = requests.get("https://kalshi.com", timeout=10)
    if response.status_code == 200:
        # Look for API references
        if "api" in response.text.lower():
            print("   Found 'api' references in HTML")
        # Extract potential API endpoints
        import re
        # Look for URLs containing /api/ or /v1/ or /v2/
        api_patterns = re.findall(r'["\'](https?://[^"\']+?/(?:api|v1|v2|trade-api)[^"\']*)["\']', response.text)
        if api_patterns:
            print(f"   Found {len(api_patterns)} potential API URLs")
            for url in api_patterns[:5]:  # Show first 5
                print(f"     - {url}")
except Exception as e:
    print(f"   Error: {str(e)[:80]}")

print("\n=== INVESTIGATION COMPLETE ===")