#!/usr/bin/env python3
"""
Test order book fetching
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

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

# Token ID for NO position
token_id = "2067891916326150127826753884863730268931932594834881748788499812590988545417"

print("Fetching order book...")
order_book = client.get_order_book(token_id)

print(f"Type of order_book: {type(order_book)}")
print(f"Order book keys: {dir(order_book)}")

# Try to access attributes
try:
    print(f"\nTrying to access as object:")
    print(f"  Has asks? {hasattr(order_book, 'asks')}")
    print(f"  Has bids? {hasattr(order_book, 'bids')}")
    
    if hasattr(order_book, 'asks'):
        print(f"  Asks: {order_book.asks}")
    if hasattr(order_book, 'bids'):
        print(f"  Bids: {order_book.bids}")
        
except Exception as e:
    print(f"Error accessing attributes: {e}")

# Try to access as dict
try:
    print(f"\nTrying to access as dict:")
    print(f"  'asks' in order_book: {'asks' in order_book}")
    print(f"  'bids' in order_book: {'bids' in order_book}")
    
    if 'asks' in order_book:
        print(f"  Asks: {order_book['asks']}")
    if 'bids' in order_book:
        print(f"  Bids: {order_book['bids']}")
        
except Exception as e:
    print(f"Error accessing as dict: {e}")

# Print the actual object
print(f"\nFull order book object:")
print(order_book)