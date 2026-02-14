#!/usr/bin/env python3
"""
Comprehensive authentication test for Polymarket API
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

print("=" * 70)
print("Polymarket Comprehensive Authentication Test")
print("=" * 70)

print(f"\nWallet Address: {WALLET_ADDRESS}")

# Import client
try:
    sys.path.insert(0, 'POLYMARKET_TRADING_BOT')
    from polymarket_api_client import PolymarketAPIClient
    print("[OK] Successfully imported polymarket_api_client")
except ImportError as e:
    print(f"[ERROR] Failed to import polymarket_api_client: {e}")
    sys.exit(1)

# Initialize client
try:
    client = PolymarketAPIClient(API_KEY, API_SECRET, PASSPHRASE, WALLET_ADDRESS)
    print("[OK] Client initialized successfully")
except Exception as e:
    print(f"[ERROR] Client initialization failed: {e}")
    sys.exit(1)

# Test different signature types
signature_types = [0, 1, 2]
signature_names = {
    0: "EOA (MetaMask)",
    1: "POLY_PROXY (Magic email login)", 
    2: "GNOSIS_SAFE"
}

print("\n" + "-" * 70)
print("Testing different signature types for balance check...")
print("-" * 70)

for sig_type in signature_types:
    print(f"\nTrying signature_type={sig_type} ({signature_names[sig_type]})...")
    
    try:
        balance = client.get_balance_allowance({
            "asset_type": "COLLATERAL",
            "signature_type": sig_type
        })
        print(f"  [SUCCESS] Balance response received!")
        print(f"  Response: {balance}")
        break  # Stop if one works
    except Exception as e:
        print(f"  [FAILED] {e}")
        
# Also test without signature_type
print("\n" + "-" * 70)
print("Testing without signature_type parameter...")
print("-" * 70)

try:
    balance = client.get_balance_allowance({
        "asset_type": "COLLATERAL"
    })
    print(f"[SUCCESS] Balance response received without signature_type!")
    print(f"Response: {balance}")
except Exception as e:
    print(f"[FAILED] {e}")

# Test market data (should work regardless)
print("\n" + "-" * 70)
print("Testing market data (public endpoint)...")
print("-" * 70)

try:
    markets = client.get_markets()
    data = markets.get('data', [])
    print(f"[OK] Retrieved {len(data)} markets")
    if data:
        # Show some active markets
        active = [m for m in data if m.get('active')]
        print(f"  Active markets: {len(active)}")
        for i, market in enumerate(active[:3]):
            print(f"  {i+1}. {market.get('question', 'N/A')[:60]}...")
except Exception as e:
    print(f"[ERROR] Market data failed: {e}")

print("\n" + "=" * 70)
print("Test Complete - Analysis")
print("=" * 70)

print("\nIf all signature types failed with 401 Unauthorized:")
print("1. The API key may be expired or invalid")
print("2. The wallet address may not match the API key")
print("3. You may need to regenerate API credentials")
print("\nNext steps:")
print("1. Log into Polymarket with the wallet: 0x32684d1162eF8A6E13213A67269271734182E667")
print("2. Check if API credentials are still valid")
print("3. Regenerate API key if needed")
print("4. Verify wallet address matches the one used to create API key")