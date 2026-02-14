#!/usr/bin/env python3
"""
Execute a $0.20 test trade on Polymarket
Using GTA VI market for good liquidity
"""

import os
import sys
import time
import json
from datetime import datetime
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.order_builder.constants import BUY, SELL
import requests

# Private key from agent_manager.py
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("="*60)
print("POLYMARKET TEST TRADE EXECUTION - $0.20")
print("="*60)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Initialize wallet
print("1. 🔑 Initializing wallet...")
try:
    account = Account.from_key(PRIVATE_KEY)
    wallet_address = account.address
    print(f"   [✅] Wallet initialized: {wallet_address[:10]}...")
    print(f"   [ℹ️] Full address: {wallet_address}")
except Exception as e:
    print(f"   [❌] Wallet init failed: {e}")
    sys.exit(1)

# Initialize CLOB client
print("\n2. 🔌 Initializing CLOB client...")
try:
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=POLYGON,
        key=account.key,
        signature_type=0,
        funder=account.address
    )
    print(f"   [✅] CLOB client initialized")
    
    # Get API credentials
    creds = client.create_or_derive_api_creds()
    print(f"   [✅] API credentials obtained")
except Exception as e:
    print(f"   [❌] CLOB client init failed: {e}")
    sys.exit(1)

# Find the GTA VI market (Market #7 from live scan)
print("\n3. 🔍 Finding GTA VI market...")
try:
    # Get active markets
    url = "https://gamma-api.polymarket.com/markets"
    params = {
        "active": "true",
        "closed": "false",
        "limit": 20
    }
    
    response = requests.get(url, params=params, timeout=10)
    if response.status_code != 200:
        print(f"   [❌] Failed to get markets: HTTP {response.status_code}")
        sys.exit(1)
    
    markets = response.json()
    print(f"   [✅] Found {len(markets)} active markets")
    
    # Find GTA VI market
    gta_market = None
    for market in markets:
        question = market.get('question', '').lower()
        if 'gta vi' in question and 'released before june 2026' in question:
            gta_market = market
            break
    
    if not gta_market:
        print("   [❌] GTA VI market not found")
        # Try alternative search
        for market in markets:
            if 'gta' in market.get('question', '').lower():
                gta_market = market
                print(f"   [⚠️] Using alternative GTA market")
                break
    
    if gta_market:
        condition_id = gta_market['conditionId']
        question = gta_market.get('question', 'Unknown')
        volume = gta_market.get('volume', 0)
        yes_price = gta_market.get('yesPrice', 0)
        no_price = gta_market.get('noPrice', 0)
        
        print(f"   [✅] Found market: {condition_id[:20]}...")
        print(f"   [ℹ️] Question: {question[:80]}...")
        print(f"   [ℹ️] Volume: ${volume:,.0f}")
        print(f"   [ℹ️] YES price: {yes_price:.3f} ({(yes_price*100):.1f}%)")
        print(f"   [ℹ️] NO price: {no_price:.3f} ({(no_price*100):.1f}%)")
    else:
        print("   [❌] No suitable market found")
        sys.exit(1)
        
except Exception as e:
    print(f"   [❌] Market search failed: {e}")
    sys.exit(1)

# Check order book
print("\n4. 📊 Checking order book...")
try:
    order_book = client.get_order_book(condition_id)
    print(f"   [✅] Order book fetched")
    
    if 'bids' in order_book and order_book['bids']:
        best_bid = order_book['bids'][0]
        print(f"   [ℹ️] Best bid: {best_bid['price']} @ ${best_bid['size']}")
    else:
        print(f"   [⚠️] No bids available")
    
    if 'asks' in order_book and order_book['asks']:
        best_ask = order_book['asks'][0]
        print(f"   [ℹ️] Best ask: {best_ask['price']} @ ${best_ask['size']}")
        
        # Use best ask price for NO position (buying NO)
        target_price = best_ask['price']
        print(f"   [ℹ️] Using ask price for NO: ${target_price}")
    else:
        print(f"   [⚠️] No asks available")
        # Use market price if no order book
        target_price = str(no_price)
        print(f"   [ℹ️] Using market NO price: ${target_price}")
        
except Exception as e:
    print(f"   [⚠️] Order book fetch failed: {e}")
    print(f"   [ℹ️] Using market NO price: ${no_price}")
    target_price = str(no_price)

# Prepare test order
print("\n5. 💰 Preparing test order ($0.20)...")
try:
    # Create token ID for NO position (condition ID + outcome index 0)
    token_id = condition_id + "0000000000000000000000000000000000000000000000000000000000000000"
    
    # Calculate size for $0.20 position
    # Cost = price × size
    # We want cost = $0.20
    # size = cost / price
    price_float = float(target_price)
    if price_float <= 0:
        print(f"   [❌] Invalid price: {target_price}")
        sys.exit(1)
    
    target_cost = 0.20  # $0.20 test trade (2% of $10 capital)
    size = target_cost / price_float
    
    # Round to reasonable precision
    size_str = f"{size:.4f}"
    
    print(f"   [✅] Order prepared:")
    print(f"   [ℹ️] Token ID: {token_id[:20]}...")
    print(f"   [ℹ️] Side: BUY (NO position)")
    print(f"   [ℹ️] Price: ${target_price}")
    print(f"   [ℹ️] Size: {size_str} shares")
    print(f"   [ℹ️] Cost: ${target_cost:.4f}")
    print(f"   [ℹ️] Implied probability: {(price_float*100):.1f}%")
    
    # Calculate expected payout if YES (market resolves NO)
    # Payout per share = $1 - price
    payout_per_share = 1.0 - price_float
    total_payout = payout_per_share * float(size_str)
    print(f"   [ℹ️] Potential payout if NO: ${total_payout:.4f}")
    print(f"   [ℹ️] Potential profit: ${(total_payout - target_cost):.4f}")
    
except Exception as e:
    print(f"   [❌] Order preparation failed: {e}")
    sys.exit(1)

# Execute the trade
print("\n6. 🚀 Executing trade...")
print("   [⚠️] WARNING: This will execute a REAL trade with $0.20")
print("   [ℹ️] Press Ctrl+C in the next 5 seconds to cancel...")

try:
    time.sleep(5)
    print("   [✅] Proceeding with trade execution...")
    
    # Create and sign order
    order = client.create_order(
        token_id=token_id,
        price=target_price,
        size=size_str,
        side=BUY,  # BUY = NO position
        fee_rate_bps="200"  # 2% fee
    )
    
    print(f"   [✅] Order created and signed")
    print(f"   [ℹ️] Order hash: {order['hash'][:20]}...")
    
    # Submit order
    print(f"   [⏳] Submitting order to Polymarket...")
    order_resp = client.post_order(order)
    
    print(f"   [✅] Order submitted successfully!")
    print(f"   [ℹ️] Response: {json.dumps(order_resp, indent=2)[:200]}...")
    
    # Save trade details
    trade_details = {
        "timestamp": datetime.now().isoformat(),
        "wallet": wallet_address,
        "market": {
            "condition_id": condition_id,
            "question": question,
            "volume": volume,
            "yes_price": yes_price,
            "no_price": no_price
        },
        "order": {
            "token_id": token_id,
            "price": target_price,
            "size": size_str,
            "side": "BUY (NO)",
            "cost": target_cost,
            "order_hash": order['hash'],
            "response": order_resp
        },
        "calculated": {
            "implied_probability": price_float * 100,
            "payout_per_share": payout_per_share,
            "total_payout": total_payout,
            "potential_profit": total_payout - target_cost
        }
    }
    
    # Save to file
    with open('test_trade_executed.json', 'w') as f:
        json.dump(trade_details, f, indent=2)
    
    print(f"\n   [✅] Trade details saved to test_trade_executed.json")
    
except KeyboardInterrupt:
    print("\n   [⚠️] Trade cancelled by user")
    sys.exit(0)
except Exception as e:
    print(f"   [❌] Trade execution failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("🎉 TEST TRADE EXECUTED SUCCESSFULLY!")
print("="*60)

print("\n📋 Trade Summary:")
print(f"   Wallet: {wallet_address[:10]}...")
print(f"   Market: {question[:60]}...")
print(f"   Position: BUY NO @ ${target_price}")
print(f"   Size: {size_str} shares")
print(f"   Cost: ${target_cost:.4f}")
print(f"   Implied Probability: {(price_float*100):.1f}%")
print(f"   Potential Payout: ${total_payout:.4f}")
print(f"   Potential Profit: ${(total_payout - target_cost):.4f}")

print("\n🔍 Next Steps:")
print("   1. Check Polymarket portfolio for position")
print("   2. Verify trade execution on blockchain")
print("   3. Monitor position until resolution")
print("   4. Scale to larger trades after verification")

print("\n" + "="*60)