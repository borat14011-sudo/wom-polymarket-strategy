#!/usr/bin/env python3
"""
Test our current API implementation to see exact error
"""

import os
import sys
from dotenv import load_dotenv

# Add the trading bot directory to path
sys.path.append('POLYMARKET_TRADING_BOT')

# Load credentials
load_dotenv('POLYMARKET_TRADING_BOT/.env.api')

API_KEY = os.getenv('POLYMARKET_API_KEY')
API_SECRET = os.getenv('POLYMARKET_API_SECRET')
PASSPHRASE = os.getenv('POLYMARKET_PASSPHRASE')
WALLET_ADDRESS = os.getenv('POLYMARKET_WALLET_ADDRESS')

print("=" * 60)
print("Testing Current API Implementation")
print("=" * 60)

print(f"API Key: {API_KEY[:10]}...")
print(f"Wallet Address: {WALLET_ADDRESS}")
print()

# Try to import and test the client
try:
    from polymarket_api_client import PolymarketAPIClient
    
    print("1. Testing client initialization...")
    client = PolymarketAPIClient(API_KEY, API_SECRET, PASSPHRASE, WALLET_ADDRESS)
    print("   Client created successfully")
    
    print("\n2. Testing public endpoint (no auth)...")
    try:
        # Test a public endpoint
        import requests
        response = requests.get("https://clob.polymarket.com/markets", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Public endpoint accessible")
        else:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Testing authenticated endpoint...")
    try:
        # This will likely fail due to authentication
        balance = client.get_balance()
        print(f"   Balance: ${balance}")
    except Exception as e:
        print(f"   Authentication error: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Check if it's a Cloudflare error
        error_str = str(e).lower()
        if 'cloudflare' in error_str or '403' in error_str or 'forbidden' in error_str:
            print("   [ISSUE] Cloudflare blocking request")
        if '401' in error_str or 'unauthorized' in error_str:
            print("   [ISSUE] Authentication failed")
        if 'signature' in error_str:
            print("   [ISSUE] Signature validation failed")
    
    print("\n4. Checking authentication method...")
    print("   Current implementation uses HMAC")
    print("   Polymarket may require EIP-712 for certain endpoints")
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS:")
    print("=" * 60)
    
    if not WALLET_ADDRESS:
        print("❌ MISSING: Wallet address not configured")
        print("   Add to .env.api: POLYMARKET_WALLET_ADDRESS=\"your_wallet_address\"")
    
    print("\nPossible issues:")
    print("1. Wrong authentication method (HMAC vs EIP-712)")
    print("2. Missing wallet address")
    print("3. Cloudflare protection")
    print("4. Incorrect API endpoint")
    print("5. Rate limiting")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("\nMake sure polymarket_api_client.py is in POLYMARKET_TRADING_BOT/")
except Exception as e:
    print(f"General error: {e}")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print("1. Check official documentation for correct authentication")
print("2. Look at working Python examples on GitHub")
print("3. Test with Postman/curl to verify API works")
print("4. Implement EIP-712 if required")
print("5. Add proper error handling for Cloudflare")