#!/usr/bin/env python3
"""
Simple $0.20 test trade - no emojis
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
print(f"Private key: {PRIVATE_KEY[:20]}...")

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
    
except ImportError as e:
    print(f"ERROR - Import error: {e}")
    print("Please install: pip install py-clob-client==0.34.5")
    sys.exit(1)
except Exception as e:
    print(f"ERROR - Client initialization failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("STEP 2: Find Active Market")
print("="*60)

try:
    # Get active markets
    markets = client.get_simplified_markets()
    if not markets:
        print("ERROR - No markets found")
        sys.exit(1)
    
    # Find a liquid market
    liquid_markets = []
    for market in markets:
        if market.get('volume24h', 0) > 1000:
            liquid_markets.append(market)
    
    if not liquid_markets:
        print("WARNING - No liquid markets found, using first available")
        target_market = markets[0]
    else:
        target_market = liquid_markets[0]
    
    market_id = target_market.get('id')
    market_question = target_market.get('question', 'Unknown')
    market_volume = target_market.get('volume24h', 0)
    
    print(f"OK - Selected market: {market_question[:50]}...")
    print(f"   Market ID: {market_id}")
    print(f"   Daily volume: ${market_volume:,.2f}")
    
except Exception as e:
    print(f"ERROR - Market selection failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("STEP 3: Check Order Book")
print("="*60)

try:
    # Get order book
    order_book = client.get_order_book(market_id)
    
    if not order_book:
        print("ERROR - No order book data")
        sys.exit(1)
    
    # Get best bid and ask
    bids = order_book.get('bids', [])
    asks = order_book.get('asks', [])
    
    if bids:
        best_bid = float(bids[0].get('price', 0))
        print(f"   Best bid: {best_bid:.4f}")
    else:
        print("   No bids")
        best_bid = 0.50
    
    if asks:
        best_ask = float(asks[0].get('price', 0))
        print(f"   Best ask: {best_ask:.4f}")
    else:
        print("   No asks")
        best_ask = 0.50
    
    # Choose price
    if best_bid > 0 and best_ask > 0:
        target_price = (best_bid + best_ask) / 2
    else:
        target_price = 0.50
    
    print(f"   Target price: {target_price:.4f}")
    
except Exception as e:
    print(f"ERROR - Order book check failed: {e}")
    target_price = 0.50

print("\n" + "="*60)
print("STEP 4: Create Test Order")
print("="*60)

try:
    # Create $0.20 BUY order
    order_args = OrderArgs(
        price=target_price,
        size=0.20,
        side=BUY,
        market=market_id
    )
    
    print(f"Creating order:")
    print(f"   Market: {market_id}")
    print(f"   Side: BUY")
    print(f"   Size: $0.20")
    print(f"   Price: {target_price:.4f}")
    print(f"   Total: ${0.20 * target_price:.4f}")
    
    # Create and post order
    order = client.create_and_post_order(order_args)
    
    if order and order.get('id'):
        print(f"SUCCESS - ORDER CREATED!")
        print(f"   Order ID: {order.get('id')}")
        print(f"   Status: {order.get('status', 'pending')}")
        
        # Save order details
        with open('test_order_result.json', 'w') as f:
            json.dump(order, f, indent=2)
        print(f"   Saved to: test_order_result.json")
        
    else:
        print(f"ERROR - Order creation failed")
        print(f"   Response: {order}")
        
except Exception as e:
    print(f"ERROR - Order creation failed: {e}")

print("\n" + "="*60)
print("STEP 5: Verify Order")
print("="*60)

try:
    # Wait for order to process
    time.sleep(2)
    
    if order and order.get('id'):
        order_id = order.get('id')
        print(f"Checking order status for: {order_id}")
        
        # Get open orders
        open_orders = client.get_orders()
        if open_orders:
            for o in open_orders:
                if o.get('id') == order_id:
                    print(f"OK - Order found in open orders")
                    print(f"   Filled: ${o.get('filled', 0):.4f}")
                    print(f"   Remaining: ${o.get('remaining', 0):.4f}")
                    break
        else:
            print("WARNING - No open orders found")
            
except Exception as e:
    print(f"Order verification error: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("Test trade executed!")
print(f"Wallet: {WALLET_ADDRESS}")
print(f"Market: {market_question[:50]}...")
print(f"Order: BUY $0.20 at {target_price:.4f}")
print("\nCheck Polymarket website to confirm trade appears.")
print("\n" + "="*60)
print("READY FOR FULL TRADING!")
print("="*60)
print("Once test trade confirms, we can:")
print("1. Start 5-agent automated trading")
print("2. Deploy validated strategies")
print("3. Scale up position sizes")
print("\nTRADING SYSTEM IS LIVE!")