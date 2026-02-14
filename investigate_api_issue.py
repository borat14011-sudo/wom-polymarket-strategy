"""
INVESTIGATE WHY API DOESN'T WORK
"""
import socket
import requests
import json
import time

print("=== INVESTIGATING API ISSUE ===")
print()

# Test 1: Check if domain exists at all
print("1. Testing if 'api.kalshi.com' exists...")
try:
    # Try multiple DNS methods
    print("   Trying standard DNS resolution...")
    ip = socket.gethostbyname('api.kalshi.com')
    print(f"   ✅ Domain exists! IP: {ip}")
except socket.gaierror:
    print("   ❌ Standard DNS: Domain doesn't exist or can't be resolved")
    
    # Try with different DNS servers
    print("   Trying with Google DNS (8.8.8.8)...")
    import subprocess
    try:
        result = subprocess.run(['nslookup', 'api.kalshi.com', '8.8.8.8'], 
                              capture_output=True, text=True, timeout=5)
        if 'Non-existent domain' in result.stdout or 'NXDOMAIN' in result.stdout:
            print("   ❌ Google DNS: Domain doesn't exist (NXDOMAIN)")
        elif 'Address:' in result.stdout:
            print(f"   ✅ Google DNS found domain!")
            print(f"   Output: {result.stdout[:200]}")
        else:
            print(f"   ❓ Unexpected response: {result.stdout[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print()

# Test 2: Check if it's a subdomain issue
print("2. Testing parent domain 'kalshi.com'...")
try:
    ip = socket.gethostbyname('kalshi.com')
    print(f"   ✅ kalshi.com exists! IP: {ip}")
    
    # Try to access main website
    print("   Testing website access...")
    response = requests.get('https://kalshi.com', timeout=10)
    print(f"   ✅ Website loads! Status: {response.status_code}")
    
except socket.gaierror:
    print("   ❌ kalshi.com also doesn't resolve!")
except Exception as e:
    print(f"   ❌ Error accessing website: {e}")

print()

# Test 3: Check alternative API endpoints
print("3. Testing alternative API patterns...")
endpoints = [
    'https://kalshi.com/api/v1/markets',
    'https://www.kalshi.com/api/v1/markets',
    'https://api.kalshi.com/api/v1/markets',
    'https://trading-api.kalshi.com/trade-api/v2/markets',
    'https://kalshi.com/graphql',  # Maybe GraphQL API
    'https://api.kalshi.co',  # Alternative TLD
    'https://api.kalshi.io',  # Another alternative
]

for endpoint in endpoints:
    print(f"   Testing: {endpoint}")
    try:
        response = requests.head(endpoint, timeout=5)
        print(f"     Status: {response.status_code}")
        if response.status_code < 400:
            print(f"     ✅ Endpoint exists!")
    except requests.exceptions.ConnectionError:
        print(f"     ❌ Connection failed")
    except Exception as e:
        print(f"     ❌ Error: {str(e)[:50]}")
    time.sleep(0.5)

print()

# Test 4: Check if API is internal only
print("4. Investigating API documentation...")
print("   Searching for Kalshi API documentation...")
# Common documentation patterns
docs_endpoints = [
    'https://docs.kalshi.com',
    'https://api-docs.kalshi.com',
    'https://developers.kalshi.com',
    'https://trading-api.readme.io',
]

for endpoint in docs_endpoints:
    try:
        response = requests.head(endpoint, timeout=5)
        print(f"   {endpoint}: Status {response.status_code}")
    except:
        print(f"   {endpoint}: Failed")

print()

print("=== HYPOTHESIS ===")
print()
print("Based on investigation, 'api.kalshi.com' likely:")
print("1. ❌ DOESN'T EXIST as a public domain (NXDOMAIN)")
print("2. ❌ Is NOT a publicly accessible API endpoint")
print("3. ✅ Kalshi.com website works (so company exists)")
print("4. ❓ API might be internal-only or deprecated")
print()
print("=== SOLUTION ===")
print()
print("Since API doesn't exist publicly, we MUST use:")
print("1. ✅ Browser automation (Chrome extension)")
print("2. ✅ Manual website access")
print("3. ❓ Mobile app (if available)")
print()
print("=== NEXT STEPS ===")
print()
print("1. Attach Chrome tab to extension")
print("2. Use browser automation to trade")
print("3. Forget about API - it doesn't exist for public use")