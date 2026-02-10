#!/usr/bin/env python3
"""
Execute trade using OFFICIAL Polymarket Python client
"""

import os
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from dotenv import load_dotenv

load_dotenv('.env.api')

# Credentials
API_KEY = os.getenv('POLYMARKET_API_KEY')
API_SECRET = os.getenv('POLYMARKET_API_SECRET')
PASSPHRASE = os.getenv('POLYMARKET_PASSPHRASE')
WALLET = os.getenv('POLY_WALLET_ADDRESS')

print("=" * 60)
print("OFFICIAL POLYMARKET CLIENT TEST")
print("=" * 60)

# Create API credentials
creds = ApiCreds(
    api_key=API_KEY,
    api_secret=API_SECRET,
    api_passphrase=PASSPHRASE
)

# Create client
client = ClobClient(
    host="https://clob.polymarket.com",
    key=WALLET,  # This might need to be a private key, not wallet address
    chain_id=137,  # Polygon
    creds=creds
)

print("\nTesting connection...")
try:
    # Try to get balance
    balance = client.get_balance_allowance()
    print(f"[OK] Connected!")
    print(f"Balance: {balance}")
except Exception as e:
    print(f"[FAIL] {e}")
    print("\nNOTE: The 'key' parameter may need to be a PRIVATE KEY")
    print("not a wallet address for L1 authentication.")
    print("\nFor L2 (API key) auth, we may need different setup.")
