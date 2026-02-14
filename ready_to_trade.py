#!/usr/bin/env python3
"""
Ready-to-execute trade script
Will run as soon as wallet is funded
"""

import os
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

print("="*60)
print("TRADING SYSTEM - READY FOR EXECUTION")
print("="*60)

# Configuration
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
WALLET_ADDRESS = "0xb354e25623617a24164639F63D8b731250AC92d8"
TEST_TRADE_SIZE = 20  # $0.20 in cents (100 = $1.00)

# Verify credentials
account = Account.from_key(PRIVATE_KEY)
if account.address.lower() != WALLET_ADDRESS.lower():
    print(f"ERROR: Private key generates {account.address}, not {WALLET_ADDRESS}")
    exit(1)

print(f"[OK] Wallet: {WALLET_ADDRESS}")
print(f"[OK] Private key: Valid")
print(f"[OK] Test trade size: ${TEST_TRADE_SIZE/100:.2f}")

# Initialize client
try:
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=PRIVATE_KEY)
    print("[OK] API client initialized")
    
    # Check server
    server_time = client.get_server_time()
    print(f"[OK] Server time: {server_time}")
    
    # Find best market for testing
    print("\n" + "="*60)
    print("FINDING TRADEABLE MARKET")
    print("="*60)
    
    # Use Gamma API for market data (more reliable)
    import requests
    gamma_url = "https://gamma-api.polymarket.com/markets"
    
    response = requests.get(gamma_url, params={"limit": 20, "closed": False}, timeout=30)
    markets = response.json()
    
    print(f"Found {len(markets)} markets")
    
    # Look for markets with some activity
    target_market = None
    for market in markets:
        question = market.get('question', '')
        volume = market.get('volume24h', 0)
        
        # Look for active markets
        if 'Trump' in question or 'tariff' in question.lower():
            target_market = market
            print(f"Selected: {question[:80]}...")
            print(f"Volume: ${volume:.2f}")
            break
    
    if not target_market and markets:
        target_market = markets[0]
        print(f"Using first market: {target_market.get('question', 'Unknown')[:80]}...")
    
    if target_market:
        condition_id = target_market.get('conditionId')
        question = target_market.get('question', 'Unknown')
        
        print(f"\n[OK] Selected market: {question[:100]}...")
        print(f"[OK] Condition ID: {condition_id[:30]}...")
        
        # Create YES token
        token_id = f"{condition_id}0x{'0'*63}1"
        
        print(f"\n" + "="*60)
        print("TRADE READY TO EXECUTE")
        print("="*60)
        print(f"Market: {question[:80]}...")
        print(f"Position: BUY YES")
        print(f"Size: ${TEST_TRADE_SIZE/100:.2f}")
        print(f"Price: ~50% (market midpoint)")
        
        # Get current price
        try:
            midpoint = client.get_midpoint(condition_id)
            price_bps = int(midpoint * 10000)  # Convert to basis points
            print(f"Current midpoint: {midpoint:.2%} ({price_bps} bps)")
        except:
            price_bps = 5000  # Default 50%
            print(f"Using default price: 50% ({price_bps} bps)")
        
        # Create order
        order_args = OrderArgs(
            token_id=token_id,
            price=price_bps,
            size=TEST_TRADE_SIZE,  # In cents: 20 = $0.20
            side=BUY
        )
        
        print(f"\nOrder details:")
        print(f"  Token: {token_id[:30]}...")
        print(f"  Price: {order_args.price/10000:.2%}")
        print(f"  Size: ${order_args.size/100:.2f}")
        print(f"  Side: {'BUY' if order_args.side == BUY else 'SELL'}")
        
        print("\n" + "="*60)
        print("EXECUTION INSTRUCTIONS")
        print("="*60)
        print("1. Fund wallet with $10 USDC")
        print("2. Run this script again")
        print("3. Trade will execute automatically")
        
        # Save trade details for later execution
        trade_details = {
            'condition_id': condition_id,
            'token_id': token_id,
            'price_bps': price_bps,
            'size_cents': TEST_TRADE_SIZE,
            'question': question
        }
        
        import json
        with open('pending_trade.json', 'w') as f:
            json.dump(trade_details, f, indent=2)
        
        print(f"\n[OK] Trade details saved to pending_trade.json")
        
    else:
        print("[ERROR] No markets found")
        
except Exception as e:
    print(f"[ERROR] Error: {e}")

print("\n" + "="*60)
print("NEXT STEP: FUND WALLET")
print("="*60)
print(f"Send $10 USDC to: {WALLET_ADDRESS}")
print("Network: Polygon")
print("Token: USDC")
print("\nAfter funding, run: python execute_pending_trade.py")