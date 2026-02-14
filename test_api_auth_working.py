#!/usr/bin/env python3
"""
Test API authentication with current credentials
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

print("Testing API Authentication")
print("="*60)
print(f"API Key: {API_KEY[:10]}...")
print(f"Wallet: {WALLET_ADDRESS}")
print()

# Import our client
sys.path.append('.')
from POLYMARKET_TRADING_BOT.polymarket_api_client import PolymarketAPIClient

client = PolymarketAPIClient(API_KEY, API_SECRET, PASSPHRASE, WALLET_ADDRESS)

# Test public endpoint
print("1. Testing public endpoint (server time)...")
try:
    server_time = client.get_server_time()
    print(f"   Success: {server_time}")
except Exception as e:
    print(f"   Error: {e}")

# Test authenticated endpoint (balance)
print("\n2. Testing authenticated endpoint (balance)...")
try:
    # Try signature_type 1 (POLY_PROXY) - email login
    balance = client.get_balance_allowance({
        "asset_type": "COLLATERAL",
        "signature_type": 1
    })
    print(f"   Success: {balance}")
except Exception as e:
    print(f"   Error: {e}")
    # Try signature_type 0 (EOA)
    try:
        balance = client.get_balance_allowance({
            "asset_type": "COLLATERAL",
            "signature_type": 0
        })
        print(f"   Success with type 0: {balance}")
    except Exception as e2:
        print(f"   Error with type 0: {e2}")

# Test orders
print("\n3. Testing orders endpoint...")
try:
    orders = client.get_orders()
    print(f"   Success: {len(orders)} orders")
except Exception as e:
    print(f"   Error: {e}")

print("\nDone.")