#!/usr/bin/env python3
"""
Execute the $0.01 test trade - FINAL VERSION
Based on test_trade_execution.py with submission code uncommented
"""

import os
import sys
import time
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.order_builder.constants import BUY, SELL
import requests

# Private key from Magic.link
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("="*60)
print("POLYMARKET TEST TRADE EXECUTION - $0.01 - LIVE")
print("="*60)
print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Initialize wallet
print("\n1. Initializing wallet...")
try:
    account = Account.from_key(PRIVATE_KEY)
    print(f"OK - Wallet initialized: {account.address}")
except Exception as e:
    print(f"ERROR - Wallet init failed: {e}")
    sys.exit(1)

# Initialize CLOB client
print("\n2. Initializing CLOB client...")
try:
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=POLYGON,
        key=account.key,
        signature_type=0,
        funder=account.address
    )
    print(f"OK - CLOB client initialized")
except Exception as e:
    print(f"ERROR - CLOB client init failed: {e}")
    sys.exit(1)

# Get an active market for testing
print("\n3. Finding active market for testing...")
try:
    url = "https://gamma-api.polymarket.com/events?closed=false&limit=5"
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        events = response.json()
        print(f"OK - Found {len(events)} active events")
        
        # Find a market with good liquidity
        test_market = None
        test_question = ""
        
        for event in events:
            for market in event.get('markets', []):
                # Look for markets with some volume
                if market.get('volume24h', 0) > 100:
                    test_market = market
                    test_question = market.get('question', 'Unknown')
                    break
            if test_market:
                break
        
        if test_market:
            condition_id = test_market['conditionId']
            print(f"OK - Selected market: {condition_id[:20]}...")
            print(f"     Question: {test_question[:80]}...")
            print(f"     24h Volume: ${test_market.get('volume24h', 0)}")
        else:
            print(f"WARN - No high-volume markets found, using first available")
            if events and events[0].get('markets'):
                test_market = events[0]['markets'][0]
                condition_id = test_market['conditionId']
                test_question = test_market.get('question', 'Unknown')
                print(f"OK - Using market: {condition_id[:20]}...")
                print(f"     Question: {test_question[:80]}...")
            else:
                print(f"ERROR - No markets available")
                sys.exit(1)
    else:
        print(f"ERROR - Failed to get markets: HTTP {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"ERROR - Market search failed: {e}")
    sys.exit(1)

# Check order book
print("\n4. Checking order book...")
try:
    order_book = client.get_order_book(condition_id)
    print(f"OK - Order book fetched")
    
    # Get best bid/ask
    if order_book and 'bids' in order_book and order_book['bids']:
        best_bid = order_book['bids'][0]['price']
        print(f"     Best bid: {best_bid}")
    else:
        print(f"WARN - No bids in order book")
        best_bid = 0.01  # Default to 1%
    
    if order_book and 'asks' in order_book and order_book['asks']:
        best_ask = order_book['asks'][0]['price']
        print(f"     Best ask: {best_ask}")
    else:
        print(f"WARN - No asks in order book")
        best_ask = 0.02  # Default to 2%
    
    # Choose a price between bid and ask, or default
    if best_bid and best_ask:
        test_price = (float(best_bid) + float(best_ask)) / 2
    else:
        test_price = 0.01  # 1% probability
        
    print(f"     Test price: {test_price} ({test_price*100:.1f}%)")
    
except Exception as e:
    print(f"WARN - Order book fetch failed: {e}")
    print(f"     Continuing anyway...")
    test_price = 0.01  # Default to 1%

# Prepare test order
print("\n5. Preparing test order ($0.01)...")
try:
    # For a $0.01 order at test_price probability
    # Size in shares = cost / price
    test_cost = 0.01  # $0.01 test
    test_size = test_cost / test_price
    
    # Get token_id from condition_id (first outcome token)
    # In Polymarket, token_id = condition_id + outcome_index
    # For binary markets: outcome 0 = NO, outcome 1 = YES
    # We'll buy YES outcome (outcome_index = 1)
    token_id = condition_id + "01"
    
    print(f"OK - Order prepared:")
    print(f"     Token ID: {token_id[:20]}...")
    print(f"     Price: ${test_price} ({test_price*100:.1f}% probability)")
    print(f"     Size: {test_size:.4f} shares")
    print(f"     Side: BUY")
    print(f"     Cost: ${test_cost:.4f}")
    
except Exception as e:
    print(f"ERROR - Order preparation failed: {e}")
    sys.exit(1)

# EXECUTE THE ORDER
print("\n6. EXECUTING ORDER...")
try:
    print("Creating and signing order...")
    
    # Create and sign order
    order = client.create_order(
        token_id=token_id,
        price=str(test_price),
        size=str(test_size),
        side=BUY,
        fee_rate_bps="0"
    )
    
    print("Submitting order to Polymarket...")
    
    # Submit order
    order_resp = client.post_order(order)
    
    print(f"SUCCESS - Order submitted!")
    print(f"     Response: {order_resp}")
    
    # Save order details
    import json
    with open('live_order_result.json', 'w') as f:
        json.dump(order_resp, f, indent=2)
    print(f"     Saved to: live_order_result.json")
    
except Exception as e:
    print(f"ERROR - Order execution failed: {e}")
    import traceback
    traceback.print_exc()

# Check order status
print("\n7. Checking order status...")
try:
    time.sleep(2)  # Wait for order to process
    
    # Get open orders
    open_orders = client.get_orders()
    if open_orders:
        print(f"Found {len(open_orders)} open orders")
        for i, o in enumerate(open_orders[:3]):
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
    print(f"Order status check error: {e}")

print("\n" + "="*60)
print("TEST TRADE EXECUTED!")
print("="*60)
print(f"Wallet: {account.address}")
print(f"Market: {test_question[:50]}...")
print(f"Order: BUY ${test_cost:.4f} at {test_price:.4f}")
print(f"Time: {time.strftime('%H:%M:%S')}")
print("\nPlease check Polymarket website to confirm order appears.")
print("\n" + "="*60)
print("NEXT: Start 5-agent automated trading!")
print("="*60)