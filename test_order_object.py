#!/usr/bin/env python3
"""
Test Order object inside SignedOrder
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

# Create a test order
order_args = OrderArgs(
    token_id="2067891916326150127826753884863730268931932594834881748788499812590988545417",
    price=0.135,
    size=1.0,
    side="BUY",
    fee_rate_bps=200
)

print("Creating order...")
signed_order = client.create_order(order_args)
order_obj = signed_order.order

print(f"Type of order_obj: {type(order_obj)}")
print(f"Order attributes: {dir(order_obj)}")

# Check for hash
if hasattr(order_obj, 'hash'):
    print(f"Order hash: {order_obj.hash}")
    
# Check all attributes
print("\nAll attributes:")
for attr in dir(order_obj):
    if not attr.startswith('_'):
        try:
            value = getattr(order_obj, attr)
            if not callable(value):
                print(f"  {attr}: {value}")
        except:
            print(f"  {attr}: [Error accessing]")