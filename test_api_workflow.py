#!/usr/bin/env python3
"""
Test API Workflow - Step by step verification
"""

import os
import sys
from dotenv import load_dotenv

print("Polymarket API Workflow Test")
print("=" * 60)

# Load credentials
env_path = 'POLYMARKET_TRADING_BOT/.env.api'
if os.path.exists(env_path):
    load_dotenv(env_path)
    print("[OK] Loaded credentials from .env.api")
else:
    print("❌ .env.api not found")
    print(f"   Expected at: {os.path.abspath(env_path)}")
    sys.exit(1)

# Check required credentials
required = ['POLYMARKET_API_KEY', 'POLYMARKET_API_SECRET', 'POLYMARKET_PASSPHRASE']
missing = [var for var in required if not os.getenv(var) or os.getenv(var) == 'your_api_key_here']

if missing:
    print(f"\n❌ Missing credentials: {missing}")
    print("\nPlease edit .env.api with your Polymarket API credentials:")
    print("""
POLYMARKET_API_KEY=your_actual_api_key
POLYMARKET_API_SECRET=your_base64url_secret
POLYMARKET_PASSPHRASE=your_passphrase
POLYMARKET_WALLET_ADDRESS=0xYourWalletAddress
    """)
    sys.exit(1)

print("\n[OK] All required credentials found")

# Test 1: Check if we can access public endpoints
print("\n" + "=" * 60)
print("TEST 1: Public API Access")
print("=" * 60)

import requests

public_endpoints = [
    ("Gamma API Markets", "https://gamma-api.polymarket.com/markets"),
    ("CLOB API Markets", "https://clob.polymarket.com/markets"),
    ("CLOB Health", "https://clob.polymarket.com/health")
]

for name, url in public_endpoints:
    try:
        response = requests.get(url, timeout=10)
        print(f"{name}: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   [OK] Accessible")
            # Check response format
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"   📊 Returns list with {len(data)} items")
                elif isinstance(data, dict):
                    print(f"   📊 Returns dictionary")
            except:
                print(f"   📄 Returns {len(response.text)} characters")
        elif response.status_code == 403:
            print(f"   [ERROR] Blocked by Cloudflare")
        else:
            print(f"   ⚠️  Unexpected status")
            
    except Exception as e:
        print(f"{name}: Error - {e}")

# Test 2: Check authentication headers
print("\n" + "=" * 60)
print("TEST 2: Authentication Header Format")
print("=" * 60)

api_key = os.getenv('POLYMARKET_API_KEY')
wallet_address = os.getenv('POLYMARKET_WALLET_ADDRESS')

print("Expected headers for authenticated requests:")
print(f"""
POLY-ADDRESS: {wallet_address or 'MISSING'}
POLY-API-KEY: {api_key[:10]}...
POLY-PASSPHRASE: [hidden]
POLY-TIMESTAMP: [current_unix_timestamp]
POLY-SIGNATURE: [hmac_signature]
Content-Type: application/json
""")

if not wallet_address or wallet_address == 'your_wallet_address_here':
    print("[ERROR] WALLET ADDRESS NOT CONFIGURED")
    print("   Add to .env.api: POLYMARKET_WALLET_ADDRESS=\"0xYourAddress\"")

# Test 3: Check if we can make a simple authenticated request
print("\n" + "=" * 60)
print("TEST 3: Simple Authenticated Request Test")
print("=" * 60)

print("Testing with curl command (run this manually):")
print()
print(f'curl -X GET "https://clob.polymarket.com/balances" \\')
print(f'  -H "POLY-ADDRESS: {wallet_address or "0xYOUR_ADDRESS"}" \\')
print(f'  -H "POLY-API-KEY: {api_key}" \\')
print(f'  -H "POLY-PASSPHRASE: [YOUR_PASSPHRASE]" \\')
print(f'  -H "POLY-TIMESTAMP: $(date +%s)" \\')
print(f'  -H "POLY-SIGNATURE: [CALCULATED_HMAC]" \\')
print(f'  -H "Content-Type: application/json"')

print("\nTo calculate HMAC signature:")
print("""
1. Get current timestamp: date +%s
2. Build message: timestamp + "GET" + "/balances"
3. Calculate HMAC-SHA256 with base64url encoded secret
4. Encode result as base64url
""")

# Test 4: Check for common issues
print("\n" + "=" * 60)
print("TEST 4: Common Issues Check")
print("=" * 60)

issues = []

# Check API secret format
api_secret = os.getenv('POLYMARKET_API_SECRET', '')
if api_secret and 'your_' in api_secret:
    issues.append("API secret not configured (still has placeholder)")
elif api_secret:
    # Check if it looks like base64url
    import re
    if not re.match(r'^[A-Za-z0-9_-]+$', api_secret):
        issues.append("API secret doesn't look like base64url")
    else:
        print("[OK] API secret format looks like base64url")

# Check passphrase
passphrase = os.getenv('POLYMARKET_PASSPHRASE', '')
if not passphrase or 'your_' in passphrase:
    issues.append("Passphrase not configured")

# Check wallet address format
if wallet_address and wallet_address != 'your_wallet_address_here':
    if not wallet_address.startswith('0x') or len(wallet_address) != 42:
        issues.append(f"Wallet address format invalid: {wallet_address}")
    else:
        print("[OK] Wallet address format looks valid")

if issues:
    print("[ERROR] Issues found:")
    for issue in issues:
        print(f"   • {issue}")
else:
    print("[OK] No obvious configuration issues")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print("""
1. MANUAL VERIFICATION:
   Run the curl command above to test authentication
   If it works, our Python client should work

2. If curl fails:
   a. Check API credentials in Polymarket account
   b. Ensure wallet address matches API key
   c. Check timestamp synchronization
   d. Verify HMAC calculation

3. If Cloudflare blocks:
   a. Access Polymarket in browser first
   b. Try different User-Agent
   c. Add delays between requests

4. Final test:
   python complete_api_client.py
   (after installing dependencies)
""")

print("\nDEPENDENCIES TO INSTALL:")
print("-" * 40)
print("pip install requests eth-account python-dotenv")

print("\n" + "=" * 60)
print("READY FOR ACTION!")
print("=" * 60)
print("Once credentials are verified, we can:")
print("1. Get market data")
print("2. Check balance")
print("3. Place test order ($0.20)")
print("4. Implement full trading system")