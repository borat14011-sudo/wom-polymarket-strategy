#!/usr/bin/env python3
"""
Fixed test trade - handle API response format
"""

import os
import sys
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('polymarket_bot/.env')

PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
WALLET_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print("="*60)
print("EXECUTING $0.20 TEST TRADE")
print("="*60)
print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Wallet: {WALLET_ADDRESS}")

print("\n" + "="*60)
print("STEP 1: Initialize Client")
print("="*60)

try:
    from py_clob_client.client import ClobClient
    from py_clob_client.constants import POLYGON
    from py_clob_client.clob_types import OrderArgs
    from py_clob_client.order_builder.constants import BUY, SELL
    
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
    sys.exit(1)

print("\n" + "="*60)
print("STEP 2: Find Market via Gamma API")
print("="*60)

try:
    # Use Gamma API to find markets (more reliable)
    import requests
    
    gamma_url = "https://gamma-api.polymarket.com/markets?limit=10&closed=false"
    response = requests.get(gamma_url, timeout=10)
    
    if response.status_code == 200:
        markets = response.json()
        if markets:
            # Find a liquid market
            for market in markets:
                volume = market.get('volume24h', 0)
                if volume > 1000:
                    market_id = market.get('id')
                    market_question = market.get('question', 'Unknown')
                    print(f"OK - Selected market: {market_question[:50]}...")
                    print(f"   Market ID: {market_id}")
                    print(f"   Daily volume: ${volume:,.2f}")
                    break
            else:
                # Use first market if none liquid
                market = markets[0]
                market_id = market.get('id')
                market_question = market.get('question', 'Unknown')
                print(f"WARNING - Using first market: {market_question[:50]}...")
        else:
            print("ERROR - No markets returned from Gamma API")
            sys.exit(1)
    else:
        print(f"ERROR - Gamma API failed: {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"ERROR - Market selection failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("STEP 3: Create Simple Order")
print("="*60)

try:
    # Create a simple $0.20 BUY order at 50% probability
    order_args = OrderArgs(
        price=0.50,  # 50% probability
        size=0.20,   # $0.20
        side=BUY,
        market=market_id
    )
    
    print(f"Creating order:")
    print(f"   Market: {market_id}")
    print(f"   Side: BUY")
    print(f"   Size: $0.20")
    print(f"   Price: 0.50 (50% probability)")
    print(f"   Total: $0.10")
    
    # Create and post order
    order = client.create_and_post_order(order_args)
    
    if order:
        print(f"SUCCESS - ORDER CREATED!")
        print(f"   Order response: {order}")
        
        # Save order details
        with open('test_order_result.json', 'w') as f:
            json.dump(order, f, indent=2)
        print(f"   Saved to: test_order_result.json")
        
        # Check if it's a dict with id
        if isinstance(order, dict) and order.get('id'):
            print(f"   Order ID: {order.get('id')}")
        elif isinstance(order, str):
            print(f"   Order ID (string): {order}")
            
    else:
        print(f"ERROR - Order creation failed (empty response)")
        
except Exception as e:
    print(f"ERROR - Order creation failed: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("STEP 4: Check Open Orders")
print("="*60)

try:
    # Wait for order to process
    time.sleep(3)
    
    print("Checking open orders...")
    open_orders = client.get_orders()
    
    if open_orders:
        print(f"Found {len(open_orders)} open orders:")
        for i, o in enumerate(open_orders[:3]):  # Show first 3
            print(f"  Order {i+1}:")
            print(f"    ID: {o.get('id', 'N/A')}")
            print(f"    Market: {o.get('market', 'N/A')}")
            print(f"    Side: {o.get('side', 'N/A')}")
            print(f"    Size: ${o.get('size', 0):.4f}")
            print(f"    Price: {o.get('price', 0):.4f}")
            print(f"    Filled: ${o.get('filled', 0):.4f}")
    else:
        print("No open orders found")
        
except Exception as e:
    print(f"Order check error: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("Test trade attempted!")
print(f"Wallet: {WALLET_ADDRESS}")
print(f"Market: {market_question[:50]}...")
print(f"Order: BUY $0.20 at 0.50")
print("\nPlease check Polymarket website to see if order appears.")
print("\n" + "="*60)
print("NEXT STEPS")
print("="*60)
print("1. Check if order appears on Polymarket")
print("2. If successful, we'll start automated trading")
print("3. If failed, we'll debug the issue")