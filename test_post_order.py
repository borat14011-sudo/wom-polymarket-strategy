#!/usr/bin/env python3
"""
Test post_order with API credentials
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import OrderArgs

# Private key
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

# Initialize
account = Account.from_key(PRIVATE_KEY)
client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=POLYGON,
    key=account.key,
    signature_type=0,
    funder=account.address
)

# Create API credentials
print("Creating API credentials...")
creds = client.create_or_derive_api_creds()
print(f"API Key: {creds.api_key[:10]}...")

# Create a small test order
order_args = OrderArgs(
    token_id="2067891916326150127826753884863730268931932594834881748788499812590988545417",
    price=0.137,  # 13.7%
    size=0.01,    # $0.01 test
    side="BUY",
    fee_rate_bps=200
)

print("\nCreating order...")
order = client.create_order(order_args)
print(f"Order created: {order.order.hash_struct()[:20]}...")

print("\nSubmitting order...")
try:
    # Try with explicit API credentials
    response = client.post_order(order, api_creds=creds)
    print(f"Response: {response}")
except Exception as e:
    print(f"Error with explicit creds: {e}")
    
    # Try without
    try:
        print("\nTrying without explicit creds...")
        response = client.post_order(order)
        print(f"Response: {response}")
    except Exception as e2:
        print(f"Error without creds: {e2}")