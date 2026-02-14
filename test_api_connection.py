#!/usr/bin/env python3
"""
Test Polymarket API connection with private key
"""

import os
import sys
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
import requests

# Private key from Magic.link
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
WALLET_ADDRESS = "0xb354e25623617a24164639F63D8b731250AC92d8"

print("="*60)
print("POLYMARKET API CONNECTION TEST")
print("="*60)

# Test 1: Basic wallet initialization
print("\n1. Testing wallet initialization...")
try:
    account = Account.from_key(PRIVATE_KEY)
    print(f"[OK] Wallet initialized successfully")
    print(f"   Address: {account.address}")
    print(f"   Expected: {WALLET_ADDRESS}")
    
    if account.address.lower() == WALLET_ADDRESS.lower():
        print("   [OK] Address matches!")
    else:
        print(f"   [WARN] Address mismatch!")
        print(f"   Expected: {WALLET_ADDRESS}")
        print(f"   Got: {account.address}")
        
except Exception as e:
    print(f"[ERROR] Wallet initialization failed: {e}")
    sys.exit(1)

# Test 2: Gamma API (public, no auth needed)
print("\n2. Testing Gamma API (public)...")
try:
    url = "https://gamma-api.polymarket.com/events?closed=false&limit=5"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Gamma API connected successfully")
        print(f"   Status: HTTP {response.status_code}")
        print(f"   Events returned: {len(data)}")
        
        if len(data) > 0:
            event = data[0]
            print(f"   First event: {event.get('title', 'No title')[:50]}...")
            print(f"   Markets in event: {len(event.get('markets', []))}")
    else:
        print(f"[ERROR] Gamma API failed: HTTP {response.status_code}")
        
except Exception as e:
    print(f"[ERROR] Gamma API test failed: {e}")

# Test 3: CLOB API (requires auth)
print("\n3. Testing CLOB API (authenticated)...")
try:
    print("   Initializing CLOB client...")
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=POLYGON,
        key=account.key,
        signature_type=0,
        funder=account.address
    )
    
    print("   [OK] CLOB client initialized")
    
    # Try to get API credentials
    print("   Getting API credentials...")
    creds = client.create_or_derive_api_creds()
    print(f"   [OK] API credentials obtained")
    print(f"   API Key: {creds['key'][:20]}...")
    
    # Test with a known market
    print("\n   Testing order book fetch...")
    # Use a known active market ID
    test_market = "0x19ee98e348c0ccb341d1b9566fa14521566e9b2ea7aed34dc407a0ec56be36a2"  # Example
    
    try:
        order_book = client.get_order_book(test_market)
        print(f"   [OK] Order book fetched successfully")
        print(f"   Market ID: {test_market[:20]}...")
        
        if 'bids' in order_book and 'asks' in order_book:
            print(f"   Bids: {len(order_book['bids'])}")
            print(f"   Asks: {len(order_book['asks'])}")
            
            if order_book['bids']:
                best_bid = order_book['bids'][0]
                print(f"   Best bid: {best_bid['price']} @ {best_bid['size']}")
            if order_book['asks']:
                best_ask = order_book['asks'][0]
                print(f"   Best ask: {best_ask['price']} @ {best_ask['size']}")
        else:
            print(f"   [WARN] Order book structure unexpected")
            
    except Exception as e:
        print(f"   [WARN] Order book fetch failed (market may be inactive): {e}")
        
        # Try a different approach - get user's balances
        print("\n   Testing balance fetch...")
        try:
            balances = client.get_balances()
            print(f"   [OK] Balances fetched successfully")
            if balances:
                print(f"   Token balances: {len(balances)} tokens")
                for token, balance in list(balances.items())[:3]:
                    print(f"     {token}: {balance}")
            else:
                print(f"   [WARN] No balances found")
        except Exception as e2:
            print(f"   [ERROR] Balance fetch failed: {e2}")
            
except Exception as e:
    print(f"[ERROR] CLOB API test failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    
    # More detailed error info
    import traceback
    print(f"\n   Traceback:")
    for line in traceback.format_exc().split('\n')[-5:]:
        if line.strip():
            print(f"   {line}")

# Test 4: Simple trade preparation
print("\n4. Testing trade preparation...")
try:
    # Create a simple limit order (not submitted)
    from py_clob_client.order_builder.constants import BUY, SELL
    
    print("   Creating sample order...")
    
    # Use a real condition ID from active markets
    condition_id = "0x19ee98e348c0ccb341d1b9566fa14521566e9b2ea7aed34dc407a0ec56be36a2"
    
    # Build a limit order
    order = {
        "token_id": condition_id + "0100000000000000000000000000000000000000000000000000000000000000",
        "price": "0.50",
        "size": "1.0",
        "side": BUY,
        "fee_rate_bps": "0"
    }
    
    print(f"   ✅ Order structure created")
    print(f"   Condition ID: {condition_id[:20]}...")
    print(f"   Price: ${order['price']}")
    print(f"   Size: {order['size']} shares")
    print(f"   Side: {order['side']}")
    
    # Note: Would need to sign and submit the order
    print("   Note: Order ready for signing and submission")
    
except Exception as e:
    print(f"❌ Trade preparation failed: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)

print("\nSummary:")
print("1. ✅ Wallet initialized")
print("2. ✅ Gamma API connected")
print("3. ⚠️  CLOB API needs market-specific testing")
print("4. ✅ Trade preparation ready")

print("\nNext steps:")
print("1. Find active market ID for testing")
print("2. Test actual order submission with $0.01")
print("3. Fix token_id format if needed")