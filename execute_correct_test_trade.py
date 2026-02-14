#!/usr/bin/env python3
"""
Execute $0.20 test trade with CORRECT API syntax
"""

import os
import sys
import time
import json
from datetime import datetime
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL
import requests

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("="*70)
print("POLYMARKET TEST TRADE - CORRECT API SYNTAX")
print("="*70)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Market details
MARKET_DETAILS = {
    "question": "Will the U.S. collect less than $100b in revenue in 2025?",
    "condition_id": "0x6acea3596be0a8126e8658d39ecc1ac44bee1246c162e51a8062b380bcf147c2",
    "slug": "will-the-us-collect-less-than-100b-in-revenue-in-2025",
    "volume": 1333580.65,
    "yes_price": 0.8645,
    "no_price": 0.1355,
    "end_date": "2026-02-28T12:00:00Z"
}

print("TARGET MARKET:")
print(f"   {MARKET_DETAILS['question']}")
print(f"   Condition ID: {MARKET_DETAILS['condition_id'][:20]}...")
print(f"   NO Price: {MARKET_DETAILS['no_price']:.3f} ({(MARKET_DETAILS['no_price']*100):.1f}%)")
print(f"   Optimal Range: 8-20% (YES for longshots)")
print()

# Initialize
print("1. Initializing...")
account = Account.from_key(PRIVATE_KEY)
wallet_address = account.address
print(f"   Wallet: {wallet_address[:10]}...")

client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=POLYGON,
    key=account.key,
    signature_type=0,
    funder=account.address
)
print(f"   CLOB client ready")

# Prepare order
print("\n2. Preparing order...")
try:
    # Token ID for NO position (condition_id + outcome index 0)
    token_id = MARKET_DETAILS['condition_id'] + "0000000000000000000000000000000000000000000000000000000000000000"
    
    price = MARKET_DETAILS['no_price']  # 0.1355
    target_cost = 0.20  # $0.20
    size = target_cost / price  # shares needed
    
    print(f"   Token ID: {token_id[:20]}...")
    print(f"   Price: ${price:.4f}")
    print(f"   Size: {size:.4f} shares")
    print(f"   Cost: ${target_cost:.4f}")
    print(f"   Side: BUY (NO position)")
    
    # Create OrderArgs object
    order_args = OrderArgs(
        token_id=token_id,
        price=price,
        size=size,
        side=BUY,  # BUY = NO position
        fee_rate_bps=200  # 2% fee
    )
    
    print(f"   OrderArgs created successfully")
    
except Exception as e:
    print(f"   [ERROR] Order prep: {e}")
    sys.exit(1)

# Execute
print("\n3. Executing trade...")
print("   WARNING: This will execute a REAL $0.20 trade")
print("   Press Ctrl+C in the next 5 seconds to cancel...")
print()

try:
    time.sleep(5)
    print("   Proceeding with execution...")
    
    # Create and sign order
    order = client.create_order(order_args)
    print(f"   Order created: {order['hash'][:20]}...")
    
    # Submit order
    order_resp = client.post_order(order)
    print(f"   Order submitted!")
    print(f"   Response: {json.dumps(order_resp, indent=2)[:200]}...")
    
    # Save record
    trade_record = {
        "time": datetime.now().isoformat(),
        "wallet": wallet_address,
        "market": MARKET_DETAILS,
        "order": {
            "token_id": token_id,
            "price": price,
            "size": size,
            "side": "BUY (NO)",
            "cost": target_cost,
            "hash": order['hash'],
            "response": order_resp
        }
    }
    
    filename = f"trade_executed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(trade_record, f, indent=2)
    
    print(f"\n   Trade saved to {filename}")
    
except KeyboardInterrupt:
    print("\n   Trade cancelled")
    sys.exit(0)
except Exception as e:
    print(f"\n   [ERROR] Execution failed: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("TRADE EXECUTED!")
print("="*70)

print("\nVERIFICATION:")
print(f"1. Check portfolio: https://polymarket.com/account/{wallet_address}")
print(f"2. Login: Borat14011@gmail.com / Montenegro@")
print(f"3. Look for position in '{MARKET_DETAILS['question'][:40]}...'")
print(f"4. Position should be NO @ {price:.3f}")

print("\nNEXT: Scale to $1 trades after verification")
print("="*70)