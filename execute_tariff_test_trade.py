#!/usr/bin/env python3
"""
Execute $0.20 test trade on "Will the U.S. collect less than $100b in revenue in 2025?"
NO position at 13.55% - Optimal longshot range
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

# Private key
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("="*70)
print("POLYMARKET TEST TRADE - TARIFF REVENUE MARKET")
print("="*70)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Market details from live_bets_output.json
MARKET_DETAILS = {
    "question": "Will the U.S. collect less than $100b in revenue in 2025?",
    "condition_id": "0x6acea3596be0a8126e8658d39ecc1ac44bee1246c162e51a8062b380bcf147c2",
    "slug": "will-the-us-collect-less-than-100b-in-revenue-in-2025",
    "volume": 1333580.65,
    "yes_price": 0.8645,  # 86.45%
    "no_price": 0.1355,   # 13.55% - OPTIMAL LONGSHOT RANGE!
    "best_bid": 0.859,
    "best_ask": 0.87,
    "end_date": "2026-02-28T12:00:00Z"
}

print("TARGET MARKET:")
print(f"   {MARKET_DETAILS['question']}")
print(f"   Condition ID: {MARKET_DETAILS['condition_id'][:20]}...")
print(f"   Volume: ${MARKET_DETAILS['volume']:,.0f}")
print(f"   YES: {MARKET_DETAILS['yes_price']:.3f} ({(MARKET_DETAILS['yes_price']*100):.1f}%)")
print(f"   NO: {MARKET_DETAILS['no_price']:.3f} ({(MARKET_DETAILS['no_price']*100):.1f}%)")
print(f"   End Date: {MARKET_DETAILS['end_date'][:10]}")
print(f"   URL: https://polymarket.com/event/{MARKET_DETAILS['slug']}")
print()

print("TRADE THESIS:")
print("   • NO at 13.55% is in optimal longshot range (8-20%)")
print("   • Avoids slippage extremes (>95% or <5%)")
print("   • $1.3M volume ensures good liquidity")
print("   • Resolves Feb 28, 2026 (17 days) - good time horizon")
print("   • Tariff revenue data will be published before resolution")
print()

# Initialize wallet
print("1. Initializing wallet...")
try:
    account = Account.from_key(PRIVATE_KEY)
    wallet_address = account.address
    print(f"   [OK] Wallet: {wallet_address[:10]}...")
    print(f"   [INFO] Full: {wallet_address}")
except Exception as e:
    print(f"   [ERROR] Wallet init: {e}")
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
    print(f"   [OK] CLOB client ready")
except Exception as e:
    print(f"   [ERROR] CLOB init: {e}")
    sys.exit(1)

# Check order book
print("\n3. 📊 Checking order book...")
try:
    order_book = client.get_order_book(MARKET_DETAILS['condition_id'])
    print(f"   [OK] Order book fetched")
    
    if 'asks' in order_book and order_book['asks']:
        best_ask = order_book['asks'][0]
        target_price = best_ask['price']
        ask_size = best_ask['size']
        print(f"   [INFO] Best ask: {target_price} @ ${ask_size}")
    else:
        print(f"   [WARNING] No asks, using market price")
        target_price = str(MARKET_DETAILS['no_price'])
        
except Exception as e:
    print(f"   [WARNING] Order book error: {e}")
    target_price = str(MARKET_DETAILS['no_price'])

# Prepare order
print("\n4. 💰 Preparing $0.20 test order...")
try:
    # Token ID for NO position (outcome index 0)
    token_id = MARKET_DETAILS['condition_id'] + "0000000000000000000000000000000000000000000000000000000000000000"
    
    price_float = float(target_price)
    target_cost = 0.20  # $0.20 (2% of $10 capital)
    size = target_cost / price_float
    size_str = f"{size:.4f}"
    
    # Calculate metrics
    payout_per_share = 1.0 - price_float
    total_payout = payout_per_share * float(size_str)
    potential_profit = total_payout - target_cost
    implied_probability = price_float * 100
    
    print(f"   [OK] Order details:")
    print(f"   [INFO] Token ID: {token_id[:20]}...")
    print(f"   [INFO] Side: BUY (NO position)")
    print(f"   [INFO] Price: ${target_price}")
    print(f"   [INFO] Size: {size_str} shares")
    print(f"   [INFO] Cost: ${target_cost:.4f}")
    print(f"   [INFO] Implied Probability: {implied_probability:.1f}%")
    print(f"   [INFO] Payout if NO: ${total_payout:.4f}")
    print(f"   [INFO] Potential Profit: ${potential_profit:.4f}")
    print(f"   [INFO] ROI if NO: {(potential_profit/target_cost*100):.1f}%")
    
except Exception as e:
    print(f"   [ERROR] Order prep: {e}")
    sys.exit(1)

# Confirm execution
print("\n" + "="*70)
print("⚠️  READY FOR EXECUTION")
print("="*70)
print()
print("SUMMARY:")
print(f"  Market: {MARKET_DETAILS['question'][:60]}...")
print(f"  Position: BUY NO @ {implied_probability:.1f}% probability")
print(f"  Size: ${target_cost:.4f} (2% of $10 capital)")
print(f"  Potential Profit: ${potential_profit:.4f}")
print(f"  Resolution: {MARKET_DETAILS['end_date'][:10]} (17 days)")
print()
print("This is a REAL trade with REAL funds.")
print("Press Ctrl+C in the next 10 seconds to cancel...")
print()

# Countdown
try:
    for i in range(10, 0, -1):
        print(f"Executing in {i}...", end='\r')
        time.sleep(1)
    print("Executing now...")
    
    # Create and sign order
    order = client.create_order(
        token_id=token_id,
        price=target_price,
        size=size_str,
        side=BUY,  # BUY = NO position
        fee_rate_bps="200"  # 2% Polymarket fee
    )
    
    print(f"\n   [OK] Order signed: {order['hash'][:20]}...")
    
    # Submit order
    print(f"   [WAIT] Submitting to Polymarket...")
    order_resp = client.post_order(order)
    
    print(f"   [SUCCESS] Order submitted!")
    print(f"   [INFO] Response: {json.dumps(order_resp, indent=2)[:200]}...")
    
    # Save trade record
    trade_record = {
        "execution_time": datetime.now().isoformat(),
        "wallet": wallet_address,
        "market": MARKET_DETAILS,
        "order": {
            "token_id": token_id,
            "price": target_price,
            "size": size_str,
            "side": "BUY (NO)",
            "cost": target_cost,
            "order_hash": order['hash'],
            "response": order_resp
        },
        "calculations": {
            "implied_probability": implied_probability,
            "payout_per_share": payout_per_share,
            "total_payout": total_payout,
            "potential_profit": potential_profit,
            "roi_percent": (potential_profit/target_cost*100)
        },
        "risk_parameters": {
            "position_size_percent": 2.0,
            "total_capital": 10.0,
            "max_position_size": 0.20,
            "total_exposure_limit": 2.50
        }
    }
    
    # Save to file
    filename = f"test_trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(trade_record, f, indent=2)
    
    print(f"\n   [OK] Trade saved to {filename}")
    
except KeyboardInterrupt:
    print("\n\n[INFO] Trade cancelled by user")
    sys.exit(0)
except Exception as e:
    print(f"\n   [ERROR] Execution failed: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("🎉 TEST TRADE EXECUTED SUCCESSFULLY!")
print("="*70)

print("\nNEXT STEPS:")
print("1. Verify on Polymarket: https://polymarket.com/account/" + wallet_address)
print("2. Check position in portfolio")
print("3. Monitor until resolution (Feb 28, 2026)")
print("4. Scale to $1 trades after verification")
print()

print("TRADE VERIFICATION:")
print(f"• Wallet: {wallet_address}")
print(f"• Market: {MARKET_DETAILS['slug']}")
print(f"• Position: NO @ {implied_probability:.1f}%")
print(f"• Cost: ${target_cost:.4f}")
print(f"• Order Hash: {order['hash'][:20]}...")

print("\n" + "="*70)