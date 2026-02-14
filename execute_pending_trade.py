#!/usr/bin/env python3
"""
Execute the pending trade once wallet is funded
"""

import json
import os
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY

print("="*60)
print("EXECUTE PENDING TRADE")
print("="*60)

# Load trade details
try:
    with open('pending_trade.json', 'r') as f:
        trade = json.load(f)
    
    print(f"Market: {trade['question'][:100]}...")
    print(f"Condition ID: {trade['condition_id'][:30]}...")
    print(f"Token ID: {trade['token_id'][:30]}...")
    print(f"Price: {trade['price_bps']/10000:.2%}")
    print(f"Size: ${trade['size_cents']/100:.2f}")
    
except FileNotFoundError:
    print("[ERROR] No pending trade found. Run ready_to_trade.py first.")
    exit(1)

# Credentials
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
WALLET_ADDRESS = "0xb354e25623617a24164639F63D8b731250AC92d8"

# Verify wallet
account = Account.from_key(PRIVATE_KEY)
if account.address.lower() != WALLET_ADDRESS.lower():
    print(f"[ERROR] Wallet mismatch: {account.address} != {WALLET_ADDRESS}")
    exit(1)

print(f"\n[OK] Wallet: {WALLET_ADDRESS}")

try:
    # Initialize client
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=PRIVATE_KEY)
    print("[OK] API client initialized")
    
    # Check server
    server_time = client.get_server_time()
    print(f"[OK] Server time: {server_time}")
    
    # Create order
    print("\nCreating order...")
    order_args = OrderArgs(
        token_id=trade['token_id'],
        price=trade['price_bps'],
        size=trade['size_cents'],
        side=BUY
    )
    
    print(f"Order: price={order_args.price/10000:.2%}, size=${order_args.size/100:.2f}")
    
    # Create and post order
    print("\nPosting order to Polymarket...")
    order = client.create_order(order_args)
    posted_order = client.post_order(order)
    
    print("\n" + "="*60)
    print("🎉 TRADE EXECUTED SUCCESSFULLY! 🎉")
    print("="*60)
    print(f"Order ID: {posted_order.get('id', 'Unknown')}")
    print(f"Status: {posted_order.get('status', 'Unknown')}")
    print(f"Market: {trade['question'][:80]}...")
    print(f"Position: BUY YES")
    print(f"Amount: ${trade['size_cents']/100:.2f}")
    print(f"Price: {trade['price_bps']/10000:.2%}")
    
    # Save confirmation
    with open('trade_confirmation.json', 'w') as f:
        json.dump({
            'timestamp': server_time,
            'order': posted_order,
            'market': trade['question'],
            'amount': trade['size_cents']/100,
            'price': trade['price_bps']/10000
        }, f, indent=2)
    
    print(f"\n[OK] Trade confirmation saved to trade_confirmation.json")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Check Polymarket website to confirm trade")
    print("2. Monitor position in 'My Positions'")
    print("3. Run agent system for automated trading")
    
except Exception as e:
    print(f"\n[ERROR] Trade execution failed: {e}")
    
    if "insufficient" in str(e).lower() or "balance" in str(e).lower():
        print("\n[INFO] This usually means:")
        print("1. Wallet not funded yet")
        print("2. USDC not deposited")
        print("3. Need to approve token spending")
        
        print("\nACTION REQUIRED:")
        print(f"1. Send $10 USDC to {WALLET_ADDRESS}")
        print("2. Network: Polygon")
        print("3. Token: USDC")
        print("4. Try again after funding")
    
    elif "signature" in str(e).lower() or "auth" in str(e).lower():
        print("\n[INFO] Authentication issue")
        print("Check private key and wallet match")
        
    else:
        print(f"\n[INFO] Unknown error: {type(e).__name__}")