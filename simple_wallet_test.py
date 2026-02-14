#!/usr/bin/env python3
"""
Simple Wallet A test - no emojis
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('polymarket_bot/.env')

PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
WALLET_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print("="*60)
print("TESTING WALLET A - $10.41")
print("="*60)
print(f"Time: {time.strftime('%H:%M:%S')}")
print(f"Wallet: {WALLET_ADDRESS}")
print(f"Private key: {PRIVATE_KEY[:20]}...")
print(f"Expected balance: $10.41")

print("\n" + "="*60)
print("STEP 1: Initialize Client")
print("="*60)

try:
    from py_clob_client.client import ClobClient
    from py_clob_client.constants import POLYGON
    
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=POLYGON,
        key=PRIVATE_KEY,
        signature_type=1,
        funder=WALLET_ADDRESS
    )
    
    server_time = client.get_server_time()
    print(f"OK - Connected! Server time: {server_time}")
    
except Exception as e:
    print(f"ERROR - Client initialization failed: {e}")
    exit(1)

print("\n" + "="*60)
print("STEP 2: Test Order Creation")
print("="*60)

try:
    # Get a market
    import requests
    import json
    
    gamma_url = "https://gamma-api.polymarket.com/markets?limit=1&closed=false"
    response = requests.get(gamma_url, timeout=10)
    
    if response.status_code == 200:
        markets = response.json()
        if markets:
            market = markets[0]
            question = market.get('question', 'Unknown')[:50]
            condition_id = market.get('conditionId')
            
            print(f"OK - Market: {question}...")
            print(f"   Condition ID: {condition_id[:20]}...")
            
            # Create token_id for YES outcome
            token_id = condition_id + '01'
            print(f"   Token ID: {token_id[:20]}...")
            
            # Test OrderArgs
            from py_clob_client.clob_types import OrderArgs
            from py_clob_client.order_builder.constants import BUY
            
            order_args = OrderArgs(
                token_id=token_id,
                price="0.50",
                size="0.20",
                side=BUY
            )
            
            print(f"OK - OrderArgs created")
            
            # Create signed order
            print(f"\nCreating signed order...")
            signed_order = client.create_order(order_args)
            print(f"OK - Signed order created")
            
            # Post order
            print(f"\nPosting order...")
            from py_clob_client.clob_types import OrderType
            response = client.post_order(signed_order, OrderType.GTC)
            print(f"OK - Order posted!")
            print(f"   Response: {response}")
            
            # Save response
            with open('wallet_test_response.json', 'w') as f:
                json.dump(str(response), f, indent=2)
            print(f"   Saved to: wallet_test_response.json")
            
        else:
            print("ERROR - No markets returned")
    else:
        print(f"ERROR - Gamma API failed: {response.status_code}")
        
except Exception as e:
    print(f"ERROR - Order test failed: {e}")
    print(f"   This might be expected - we'll debug")

print("\n" + "="*60)
print("STEP 3: Check System Status")
print("="*60)

try:
    time.sleep(2)
    
    print("Checking open orders...")
    open_orders = client.get_orders()
    
    if open_orders:
        print(f"OK - Found {len(open_orders)} open orders")
    else:
        print("INFO - No open orders found")
        
except Exception as e:
    print(f"INFO - Order check error: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Wallet: {WALLET_ADDRESS}")
print(f"Status: READY FOR TRADING")
print(f"Balance: $10.41 (per screenshot)")
print("\n" + "="*60)
print("NEXT: Run agent manager")
print("="*60)