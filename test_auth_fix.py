#!/usr/bin/env python3
"""
Test authentication fix for Polymarket API
"""

import os
import sys
from dotenv import load_dotenv

# Load API credentials
load_dotenv('POLYMARKET_TRADING_BOT/.env.api')

API_KEY = os.getenv('POLYMARKET_API_KEY')
API_SECRET = os.getenv('POLYMARKET_API_SECRET')
PASSPHRASE = os.getenv('POLYMARKET_PASSPHRASE')
WALLET_ADDRESS = os.getenv('POLY_WALLET_ADDRESS')

print("=" * 60)
print("Polymarket Authentication Test")
print("=" * 60)

print(f"\nAPI Key: {API_KEY[:10]}...")
print(f"API Secret: {API_SECRET[:10]}...")
print(f"Passphrase: {PASSPHRASE[:10]}...")
print(f"Wallet Address: {WALLET_ADDRESS}")

# Test if we can import the client
try:
    sys.path.insert(0, 'POLYMARKET_TRADING_BOT')
    from polymarket_api_client import PolymarketAPIClient, build_hmac_signature
    print("\n[OK] Successfully imported polymarket_api_client")
except ImportError as e:
    print(f"\n❌ Failed to import polymarket_api_client: {e}")
    sys.exit(1)

# Test HMAC signature generation
print("\n" + "-" * 60)
print("Testing HMAC signature generation...")
try:
    timestamp = 1700000000
    method = "GET"
    request_path = "/balance-allowance"
    
    signature = build_hmac_signature(
        API_SECRET,
        timestamp,
        method,
        request_path
    )
    print(f"[OK] HMAC signature generated: {signature[:20]}...")
except Exception as e:
    print(f"❌ HMAC signature failed: {e}")

# Test client initialization
print("\n" + "-" * 60)
print("Testing client initialization...")
try:
    client = PolymarketAPIClient(API_KEY, API_SECRET, PASSPHRASE, WALLET_ADDRESS)
    print("[OK] Client initialized successfully")
except Exception as e:
    print(f"❌ Client initialization failed: {e}")
    sys.exit(1)

# Test public endpoint (no auth required)
print("\n" + "-" * 60)
print("Testing public endpoint (server time)...")
try:
    server_time = client.get_server_time()
    print(f"[OK] Server time: {server_time}")
except Exception as e:
    print(f"❌ Server time failed: {e}")

# Test authenticated endpoint
print("\n" + "-" * 60)
print("Testing authenticated endpoint (balance)...")
try:
    balance = client.get_balance_allowance({
        "asset_type": "COLLATERAL",
        "signature_type": 1  # Try Magic/Email login
    })
    print(f"[OK] Balance response received")
    print(f"   Response keys: {list(balance.keys())}")
except Exception as e:
    print(f"[ERROR] Balance check failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check if wallet address matches API key")
    print("2. Try different signature_type values:")
    print("   - 0 for EOA (MetaMask)")
    print("   - 1 for POLY_PROXY (Magic email login)")
    print("   - 2 for GNOSIS_SAFE")
    print("3. Verify API credentials are valid")

# Test market data
print("\n" + "-" * 60)
print("Testing market data endpoint...")
try:
    markets = client.get_markets()
    data = markets.get('data', [])
    print(f"[OK] Retrieved {len(data)} markets")
    if data:
        print(f"   Sample market: {data[0].get('question', 'N/A')[:50]}...")
except Exception as e:
    print(f"❌ Market data failed: {e}")

print("\n" + "=" * 60)
print("Authentication Test Complete")
print("=" * 60)