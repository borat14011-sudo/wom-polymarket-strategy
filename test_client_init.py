#!/usr/bin/env python3
"""
Test ClobClient initialization with API credentials
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

# Private key
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

# Initialize account
account = Account.from_key(PRIVATE_KEY)

print("Testing different client initializations...")

# Method 1: Standard initialization
print("\n1. Standard initialization:")
try:
    client1 = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=POLYGON,
        key=account.key,
        signature_type=0,
        funder=account.address
    )
    print(f"   Success")
    
    # Try to get creds
    creds1 = client1.create_or_derive_api_creds()
    print(f"   Got API creds: {creds1.api_key[:10]}...")
    
except Exception as e:
    print(f"   Error: {e}")

# Method 2: Check if there's an api_key parameter
print("\n2. Looking for api_key parameter...")
import inspect
sig = inspect.signature(ClobClient.__init__)
params = list(sig.parameters.keys())
print(f"   Parameters: {params}")

# Method 3: Try to see if creds are stored
print("\n3. Checking client attributes...")
client3 = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=POLYGON,
    key=account.key,
    signature_type=0,
    funder=account.address
)

# Get creds
creds3 = client3.create_or_derive_api_creds()
print(f"   Created creds: {creds3.api_key[:10]}...")

# Check if client has creds attribute
print(f"   Has 'api_creds' attr: {hasattr(client3, 'api_creds')}")
print(f"   Has '_api_creds' attr: {hasattr(client3, '_api_creds')}")

# Check all attributes
print(f"\n   All attributes starting with 'api' or 'cred':")
for attr in dir(client3):
    if 'api' in attr.lower() or 'cred' in attr.lower():
        print(f"     {attr}")