#!/usr/bin/env python3
"""
Test Polymarket API authentication methods
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load credentials
load_dotenv('POLYMARKET_TRADING_BOT/.env.api')

API_KEY = os.getenv('POLYMARKET_API_KEY')
API_SECRET = os.getenv('POLYMARKET_API_SECRET')
PASSPHRASE = os.getenv('POLYMARKET_PASSPHRASE')
WALLET_ADDRESS = os.getenv('POLYMARKET_WALLET_ADDRESS')

print("=" * 60)
print("TESTING Polymarket API Authentication Methods")
print("=" * 60)

print(f"API Key: {API_KEY[:10]}...")
print(f"Wallet Address: {WALLET_ADDRESS}")
print()

# Test 1: Direct API call to check Cloudflare status
print("Test 1: Checking API endpoint accessibility...")
url = "https://clob.polymarket.com/health"
try:
    response = requests.get(url, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    
    if response.status_code == 403:
        print("   ⚠️  403 Forbidden - Cloudflare protection active")
        # Check for Cloudflare headers
        if 'cf-ray' in response.headers:
            print(f"   ⚠️  Cloudflare Ray ID: {response.headers['cf-ray']}")
        if 'server' in response.headers and 'cloudflare' in response.headers['server'].lower():
            print("   ⚠️  Server: Cloudflare")
            
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 2: Check if we can access without authentication
print("Test 2: Testing public endpoints...")
public_endpoints = [
    "https://gamma-api.polymarket.com/markets",
    "https://clob.polymarket.com/markets",
    "https://clob.polymarket.com/orderbook/microstrategy-500k-btc-dec-31"
]

for endpoint in public_endpoints:
    try:
        response = requests.get(endpoint, timeout=10)
        print(f"   {endpoint}: {response.status_code}")
        
        if response.status_code == 403:
            print("      [WARNING] Blocked by Cloudflare")
        elif response.status_code == 200:
            print("      [OK] Accessible")
            # Check response size
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"      📊 {len(data)} items")
                elif isinstance(data, dict):
                    print(f"      📊 Dict with {len(data)} keys")
            except:
                print(f"      📄 {len(response.text)} chars")
                
    except Exception as e:
        print(f"   {endpoint}: Error - {e}")

print()

# Test 3: Check authentication requirements
print("Test 3: Testing authentication methods...")
print("   Based on research, Polymarket uses:")
print("   1. HMAC for CLOB API (trading)")
print("   2. EIP-712 signatures for wallet authentication")
print("   3. Cloudflare protection for rate limiting")

print()

# Test 4: Check if manual browser access works
print("Test 4: Manual workaround options:")
print("   1. Use browser automation (Selenium/Playwright)")
print("   2. Use Polymarket's official SDK if available")
print("   3. Reverse engineer mobile app API")
print("   4. Use proxy/VPN rotation")
print("   5. Manual trading with API for data only")

print()

# Check for existing solutions
print("Test 5: Looking for known solutions...")
print("   Searching memory for previous API work...")

# Check our memory for API issues
try:
    with open('MEMORY.md', 'r') as f:
        content = f.read()
        if 'API' in content or 'Cloudflare' in content:
            print("   Found API references in memory")
            lines = content.split('\n')
            api_lines = [line for line in lines if 'API' in line or 'Cloudflare' in line]
            for line in api_lines[:5]:
                print(f"      • {line[:80]}...")
except:
    print("   No memory file found")

print()

print("=" * 60)
print("RECOMMENDED WORKAROUNDS:")
print("=" * 60)
print("1. **Browser Automation**: Use Selenium/Playwright to automate browser")
print("   - Can bypass Cloudflare")
print("   - Slower but reliable")
print()
print("2. **Mobile API**: Reverse engineer mobile app API calls")
print("   - Mobile might have different authentication")
print("   - Use mitmproxy to intercept")
print()
print("3. **Proxy Rotation**: Use rotating proxies to avoid rate limits")
print("   - Services like BrightData, ScraperAPI")
print("   - Can be expensive")
print()
print("4. **Manual + API Hybrid**:")
print("   - Use API for market data only")
print("   - Execute trades manually")
print("   - Our current approach")
print()
print("5. **Official SDK**: Check if Polymarket has official Python SDK")
print("   - Might handle authentication correctly")