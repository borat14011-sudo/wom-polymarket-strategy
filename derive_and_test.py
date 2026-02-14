#!/usr/bin/env python3
"""
Derive API credentials and test L2 authentication
"""
import sys
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import BalanceAllowanceParams, AssetType
import json

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("Deriving API credentials")
print("="*60)

account = Account.from_key(PRIVATE_KEY)
wallet_address = account.address
print(f"Wallet address: {wallet_address}")

# Initialize client with signer only (L1)
client_l1 = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=POLYGON,
    key=account.key,
    signature_type=0,
    funder=account.address
)

print("Client L1 initialized.")

# Create or derive API credentials
print("\nDeriving API credentials...")
creds = client_l1.create_or_derive_api_creds()
api_key = creds.api_key
api_secret = creds.api_secret
api_passphrase = creds.api_passphrase
print(f"API Key: {api_key}")
print(f"API Secret: {api_secret[:10]}...")
print(f"API Passphrase: {api_passphrase[:10]}...")

# Save to .env for later use
with open('derived_creds.env', 'w') as f:
    f.write(f"POLYMARKET_API_KEY={api_key}\n")
    f.write(f"POLYMARKET_API_SECRET={api_secret}\n")
    f.write(f"POLYMARKET_PASSPHRASE={api_passphrase}\n")
    f.write(f"POLY_WALLET_ADDRESS={wallet_address}\n")
print("Saved to derived_creds.env")

# Now test L2 authentication using polymarket_api_client
print("\n" + "="*60)
print("Testing L2 authentication with derived credentials")
print("="*60)

sys.path.append('.')
from POLYMARKET_TRADING_BOT.polymarket_api_client import PolymarketAPIClient

client_l2 = PolymarketAPIClient(api_key, api_secret, api_passphrase, wallet_address)

# Test public endpoint
print("\n1. Testing public endpoint (server time)...")
try:
    server_time = client_l2.get_server_time()
    print(f"   Success: {server_time}")
except Exception as e:
    print(f"   Error: {e}")

# Test authenticated endpoint (balance)
print("\n2. Testing authenticated endpoint (balance)...")
try:
    # Try signature_type 1 (POLY_PROXY) - email login? Actually we have private key, maybe signature_type 0
    balance = client_l2.get_balance_allowance({
        "asset_type": "COLLATERAL",
        "signature_type": 0
    })
    print(f"   Success: {balance}")
except Exception as e:
    print(f"   Error: {e}")
    # Try signature_type 1
    try:
        balance = client_l2.get_balance_allowance({
            "asset_type": "COLLATERAL",
            "signature_type": 1
        })
        print(f"   Success with type 1: {balance}")
    except Exception as e2:
        print(f"   Error with type 1: {e2}")

# Test orders
print("\n3. Testing orders endpoint...")
try:
    orders = client_l2.get_orders()
    print(f"   Success: {len(orders)} orders")
except Exception as e:
    print(f"   Error: {e}")

# Now test using py_clob_client with derived creds (L2)
print("\n" + "="*60)
print("Testing py_clob_client with derived creds (L2)")
print("="*60)

client_l2_full = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=POLYGON,
    key=account.key,
    api_creds=creds,
    signature_type=0,
    funder=account.address
)

# Get balance allowance using py_clob_client
print("\nTesting balance allowance via py_clob_client...")
try:
    params = BalanceAllowanceParams(
        asset_type=AssetType.COLLATERAL,
        signature_type=0
    )
    balance = client_l2_full.get_balance_allowance(params)
    print(f"   Success: {balance}")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\nDone.")