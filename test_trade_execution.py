#!/usr/bin/env python3
"""
Test trade execution - $0.01 test trade
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
print("POLYMARKET TEST TRADE EXECUTION - $0.01")
print("="*60)

# Initialize wallet
print("\n1. Initializing wallet...")
try:
    account = Account.from_key(PRIVATE_KEY)
    print(f"[OK] Wallet initialized: {account.address[:10]}...")
except Exception as e:
    print(f"[ERROR] Wallet init failed: {e}")
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
    print(f"[OK] CLOB client initialized")
except Exception as e:
    print(f"[ERROR] CLOB client init failed: {e}")
    sys.exit(1)

# Get an active market for testing
print("\n3. Finding active market for testing...")
try:
    url = "https://gamma-api.polymarket.com/events?closed=false&limit=5"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        events = response.json()
        print(f"[OK] Found {len(events)} active events")
        
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
            print(f"[OK] Selected market: {condition_id[:20]}...")
            print(f"     Question: {test_question[:80]}...")
            print(f"     24h Volume: ${test_market.get('volume24h', 0)}")
        else:
            print(f"[WARN] No high-volume markets found, using first available")
            if events and events[0].get('markets'):
                test_market = events[0]['markets'][0]
                condition_id = test_market['conditionId']
                test_question = test_market.get('question', 'Unknown')
                print(f"[OK] Using market: {condition_id[:20]}...")
                print(f"     Question: {test_question[:80]}...")
            else:
                print(f"[ERROR] No markets available")
                sys.exit(1)
    else:
        print(f"[ERROR] Failed to get markets: HTTP {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"[ERROR] Market search failed: {e}")
    sys.exit(1)

# Check order book
print("\n4. Checking order book...")
try:
    order_book = client.get_order_book(condition_id)
    print(f"[OK] Order book fetched")
    
    if 'bids' in order_book and order_book['bids']:
        best_bid = order_book['bids'][0]
        print(f"     Best bid: {best_bid['price']} @ {best_bid['size']}")
    else:
        print(f"     No bids available")
    
    if 'asks' in order_book and order_book['asks']:
        best_ask = order_book['asks'][0]
        print(f"     Best ask: {best_ask['price']} @ {best_ask['size']}")
    else:
        print(f"     No asks available")
        
except Exception as e:
    print(f"[WARN] Order book fetch failed: {e}")
    print(f"     Continuing anyway...")

# Prepare test order
print("\n5. Preparing test order ($0.01)...")
try:
    # Create token ID (condition ID + outcome index 1 for YES)
    token_id = condition_id + "0100000000000000000000000000000000000000000000000000000000000000"
    
    # Use a very low price for testing (0.01 = 1%)
    test_price = "0.01"
    test_size = "1.0"  # 1 share
    
    print(f"[OK] Order prepared:")
    print(f"     Token ID: {token_id[:20]}...")
    print(f"     Price: ${test_price} (1% probability)")
    print(f"     Size: {test_size} share")
    print(f"     Side: BUY")
    print(f"     Cost: ${float(test_price) * float(test_size):.4f}")
    
    # Note: In production, we would:
    # 1. Create the signed order
    # 2. Submit to CLOB
    # 3. Wait for confirmation
    # 4. Check fill status
    
    print("\n[INFO] Test order ready for execution")
    print("       To execute, uncomment the order submission code")
    print("       and run with real funds.")
    
except Exception as e:
    print(f"[ERROR] Order preparation failed: {e}")

# Check balances (if API supports it)
print("\n6. Checking balances...")
try:
    # Try to get balances
    balances = client.get_balances()
    if balances:
        print(f"[OK] Balances found:")
        for token, balance in balances.items():
            if float(balance) > 0:
                print(f"     {token}: {balance}")
    else:
        print(f"[INFO] No balances returned or zero balance")
except Exception as e:
    print(f"[INFO] Balance check not available: {e}")

print("\n" + "="*60)
print("TEST TRADE READY")
print("="*60)

print("\nSummary:")
print(f"1. [OK] Wallet: {account.address[:10]}...")
print(f"2. [OK] Market: {condition_id[:10]}...")
print(f"3. [OK] Order: BUY {test_size} @ ${test_price}")
print(f"4. [OK] Cost: ${float(test_price) * float(test_size):.4f}")

print("\nNext steps:")
print("1. Uncomment order submission code")
print("2. Execute $0.01 test trade")
print("3. Verify execution on Polymarket")
print("4. Scale to $1 trades")

print("\nTo execute, add this code:")
print("""
# Create and sign order
order = client.create_order(
    token_id=token_id,
    price=test_price,
    size=test_size,
    side=BUY,
    fee_rate_bps="0"
)

# Submit order
order_resp = client.post_order(order)
print(f"Order submitted: {order_resp}")
""")

print("\n" + "="*60)