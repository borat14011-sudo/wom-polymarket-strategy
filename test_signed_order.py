#!/usr/bin/env python3
"""
Test SignedOrder object
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
order = client.create_order(order_args)

print(f"Type of order: {type(order)}")
print(f"Order attributes: {dir(order)}")

# Check for common attributes
for attr in ['hash', 'order_hash', 'signature', 'signed_order', 'order']:
    if hasattr(order, attr):
        print(f"  Has '{attr}': {getattr(order, attr)}")

# Check if it's a dataclass
if hasattr(order, '__dataclass_fields__'):
    print(f"\nDataclass fields: {order.__dataclass_fields__}")
    
# Try to convert to dict
try:
    import json
    print(f"\nAs dict: {order.__dict__}")
except:
    pass