#!/usr/bin/env python3
"""
Direct test trade - simplest possible
"""

import requests
import time

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
WALLET_ADDRESS = "0xb354e25623617a24164639F63D8b731250AC92d8"

print("DIRECT TEST TRADE")
print("="*60)
print(f"Time: {time.strftime('%H:%M:%S')}")
print(f"Wallet: {WALLET_ADDRESS}")

print("\n" + "="*60)
print("STEP 1: Get Market and Token ID")
print("="*60)

# Get a market
url = "https://gamma-api.polymarket.com/markets?limit=1&closed=false"
response = requests.get(url, timeout=10)

if response.status_code == 200:
    markets = response.json()
    if markets:
        market = markets[0]
        market_id = market.get('id')
        question = market.get('question', 'Unknown')[:50]
        condition_id = market.get('conditionId')
        
        print(f"Market: {question}...")
        print(f"Market ID: {market_id}")
        print(f"Condition ID: {condition_id[:20]}...")
        
        # For YES outcome: condition_id + '01'
        token_id = condition_id + '01'
        print(f"Token ID (YES): {token_id[:20]}...")
        
        # For NO outcome: condition_id + '00'
        token_id_no = condition_id + '00'
        print(f"Token ID (NO): {token_id_no[:20]}...")
        
        # Save token_id
        with open('token_id.txt', 'w') as f:
            f.write(token_id)
        print(f"Saved token_id to token_id.txt")
        
    else:
        print("No markets found")
        exit(1)
else:
    print(f"Failed to get markets: {response.status_code}")
    exit(1)

print("\n" + "="*60)
print("STEP 2: Initialize Client")
print("="*60)

try:
    from py_clob_client.client import ClobClient
    from py_clob_client.constants import POLYGON
    from py_clob_client.clob_types import OrderArgs, OrderType
    from py_clob_client.order_builder.constants import BUY, SELL
    
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=POLYGON,
        key=PRIVATE_KEY,
        signature_type=1,  # Magic/email login
        funder=WALLET_ADDRESS
    )
    
    print(f"Connected! Server time: {client.get_server_time()}")
    
except Exception as e:
    print(f"Client init failed: {e}")
    exit(1)

print("\n" + "="*60)
print("STEP 3: Create Test Order")
print("="*60)

try:
    # Create OrderArgs
    order_args = OrderArgs(
        token_id=token_id,  # BUY YES
        price="0.50",       # 50% probability
        size="0.20",        # $0.20
        side=BUY
    )
    
    print(f"OrderArgs created:")
    print(f"  Token ID: {token_id[:20]}...")
    print(f"  Price: 0.50 (50% probability)")
    print(f"  Size: 0.20 ($0.20)")
    print(f"  Side: BUY")
    print(f"  Cost: $0.10")
    
    # Create signed order
    print(f"\nCreating signed order...")
    signed_order = client.create_order(order_args)
    print(f"Signed order created")
    
    # Post order
    print(f"\nPosting order to Polymarket...")
    response = client.post_order(signed_order, OrderType.GTC)
    print(f"Order posted!")
    print(f"Response: {response}")
    
    # Save response
    import json
    with open('order_response.json', 'w') as f:
        json.dump(str(response), f)
    print(f"Saved response to order_response.json")
    
except Exception as e:
    print(f"Order creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("STEP 4: Check Order Status")
print("="*60)

try:
    time.sleep(2)
    
    print("Checking open orders...")
    open_orders = client.get_orders()
    
    if open_orders:
        print(f"Found {len(open_orders)} open orders")
        for i, order in enumerate(open_orders[:3]):
            print(f"  Order {i+1}:")
            print(f"    ID: {order.get('id', 'N/A')}")
            print(f"    Token: {order.get('token', 'N/A')}")
            print(f"    Side: {order.get('side', 'N/A')}")
            print(f"    Size: {order.get('size', 0)}")
            print(f"    Price: {order.get('price', 0)}")
    else:
        print("No open orders found")
        
except Exception as e:
    print(f"Order check error: {e}")

print("\n" + "="*60)
print("TEST COMPLETE!")
print("="*60)
print(f"Wallet: {WALLET_ADDRESS}")
print(f"Market: {question}...")
print(f"Order: BUY $0.20 YES at 50%")
print(f"Time: {time.strftime('%H:%M:%S')}")
print("\nCheck Polymarket website to confirm order!")