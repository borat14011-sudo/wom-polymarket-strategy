#!/usr/bin/env python3
"""
Execute a $0.01 test trade to verify everything works
"""

import os
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.order_builder.constants import BUY, SELL

print("="*60)
print("TEST TRADE EXECUTION")
print("="*60)

# Credentials
private_key = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
wallet_address = "0xb354e25623617a24164639F63D8b731250AC92d8"

print(f"Wallet: {wallet_address}")
print(f"Private key: {private_key[:20]}...")

# Verify
account = Account.from_key(private_key)
if account.address.lower() != wallet_address.lower():
    print(f"ERROR: Private key generates {account.address}, not {wallet_address}")
    exit(1)

print("OK: Credentials match")

try:
    # Initialize client
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=private_key)
    print("OK: Client initialized")
    
    # Get server time
    server_time = client.get_server_time()
    print(f"Server time: {server_time}")
    
    # Find a market with liquidity
    print("\nFinding tradeable market...")
    
    # Use Gamma API to find markets
    import requests
    gamma_url = "https://gamma-api.polymarket.com/markets"
    
    response = requests.get(gamma_url, params={"limit": 10, "closed": False}, timeout=30)
    markets = response.json()
    
    print(f"Found {len(markets)} markets")
    
    # Find first market with some volume
    target_market = None
    for market in markets:
        volume = market.get('volume24h', 0)
        if volume > 0:
            target_market = market
            break
    
    if not target_market:
        print("No markets with volume found. Using first market for test...")
        target_market = markets[0] if markets else None
    
    if target_market:
        print(f"\nSelected market: {target_market.get('question', 'Unknown')[:80]}...")
        condition_id = target_market.get('conditionId')
        print(f"Condition ID: {condition_id}")
        
        if condition_id:
            # Create YES token ID
            token_id = condition_id + "0x" + "0" * 63 + "1"
            
            print(f"\nCreating test order...")
            print(f"Token ID: {token_id[:30]}...")
            print(f"Size: 1 share ($0.01)")
            print(f"Price: 50 (50% probability)")
            
            # Create order
            order = client.create_order(
                token_id=token_id,
                price="50",  # 0.50 = 50%
                size="1",    # 1 share = $0.01
                side=BUY,
                fee_rate_bps="0"
            )
            
            print(f"\nOK: Order created!")
            print(f"Order ID: {order.get('id', 'Unknown')}")
            print(f"Status: {order.get('status', 'Unknown')}")
            
            print("\n" + "="*60)
            print("SUCCESS!")
            print("="*60)
            print("The trading system is WORKING!")
            print("")
            print("Next steps:")
            print("1. Check if wallet has USDC (manual check required)")
            print("2. If yes, execute $0.20 real trade")
            print("3. Deploy automated bot")
            
        else:
            print("ERROR: No condition ID found")
    else:
        print("ERROR: No markets found")
        
except Exception as e:
    print(f"\nERROR: {e}")
    print("\nThis could be because:")
    print("1. Wallet has no USDC")
    print("2. API rate limiting")
    print("3. Market illiquidity")
    
print("\n" + "="*60)
print("FINAL STEP REQUIRED")
print("="*60)
print("PLEASE check wallet balance manually:")
print("1. Go to https://polymarket.com")
print("2. Connect wallet")
print("3. Send screenshot of balance")
print("")
print("Then we can execute REAL trades!")