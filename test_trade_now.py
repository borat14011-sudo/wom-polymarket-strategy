#!/usr/bin/env python3
"""
Minimal test trade - VPN should be active
"""

import os
import json
from dotenv import load_dotenv

load_dotenv('polymarket_bot/.env')

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, MarketOrderArgs
from py_clob_client.order_builder.constants import BUY

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137

PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
FUNDER_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print("="*60)
print("MINIMAL TRADE TEST - VPN ACTIVE")
print("="*60)

# Create client
print("\n1. Creating client...")
client = ClobClient(
    HOST,
    key=PRIVATE_KEY,
    chain_id=CHAIN_ID,
    signature_type=1,  # POLY_PROXY
    funder=FUNDER_ADDRESS
)

# Derive credentials
print("2. Deriving API credentials...")
api_creds = client.create_or_derive_api_creds()
client.set_api_creds(api_creds)
print(f"   API Key: {api_creds.api_key[:20]}...")

# Test server
print("\n3. Testing server connection...")
try:
    server_time = client.get_server_time()
    print(f"   Server time: {server_time}")
except Exception as e:
    print(f"   Error: {e}")

# Get a token_id from Gamma API
print("\n4. Getting market data...")
import requests
gamma_url = "https://gamma-api.polymarket.com/markets?limit=1&closed=false"
gamma_resp = requests.get(gamma_url, timeout=10)
market = gamma_resp.json()[0]
question = market.get('question', '')[:50]
clob_token_ids = json.loads(market.get('clobTokenIds', '[]'))

if not clob_token_ids:
    print("   No token IDs found!")
    exit(1)

token_id = clob_token_ids[0]  # YES token
print(f"   Market: {question}...")
print(f"   Token ID: {token_id[:30]}...")

# Get orderbook
print("\n5. Getting orderbook...")
try:
    book = client.get_order_book(token_id)
    print(f"   Bids: {len(book.bids)}")
    print(f"   Asks: {len(book.asks)}")
    
    if book.asks:
        best_ask = float(book.asks[0].price)
        print(f"   Best ask: ${best_ask}")
    else:
        best_ask = 0.10  # Default
        print(f"   No asks, using default: ${best_ask}")
except Exception as e:
    print(f"   Orderbook error: {e}")
    best_ask = 0.10

# Try to place order
print("\n6. Placing $0.01 test order...")
try:
    # Create order args
    order_args = OrderArgs(
        price=0.01,  # $0.01 per share
        size=1.0,    # 1 share
        side=BUY,
        token_id=token_id
    )
    
    print(f"   Creating order...")
    signed_order = client.create_order(order_args)
    print(f"   Order created: {type(signed_order)}")
    
    print(f"   Posting order...")
    result = client.post_order(signed_order)
    print(f"   Result: {result}")
    
    if result:
        print("\n✅ ORDER PLACED SUCCESSFULLY!")
    else:
        print("\n⚠️ Order returned None - check for errors above")
        
except Exception as e:
    print(f"\n❌ Order failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
