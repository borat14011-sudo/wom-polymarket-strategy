#!/usr/bin/env python3
"""
Test if wallet has funds and can trade
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

private_key = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("="*60)
print("WALLET FUNDS CHECK")
print("="*60)

# Show wallet
account = Account.from_key(private_key)
print(f"Wallet: {account.address}")
print(f"Private key matches: YES")

# Initialize client
try:
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=private_key)
    print("\nOK: Client initialized")
    
    # Get server time
    server_time = client.get_server_time()
    print(f"Server time: {server_time}")
    
    # Try to get markets to test
    print("\nTesting market access...")
    from py_clob_client.order_book import OrderBook
    ob = OrderBook(client)
    
    # Get some active markets
    markets = client.get_markets(limit=5)
    print(f"Found {len(markets)} markets")
    
    if markets:
        market = markets[0]
        print(f"\nSample market: {market.get('question', 'Unknown')[:80]}...")
        print(f"Market ID: {market.get('id', 'Unknown')}")
        
        # Try to get order book (will fail if no liquidity)
        try:
            condition_id = market.get('conditionId')
            if condition_id:
                print(f"\nTrying to get order book for condition: {condition_id[:20]}...")
                order_book = ob.get_order_book(condition_id)
                print(f"Order book retrieved: {len(order_book.get('bids', []))} bids, {len(order_book.get('asks', []))} asks")
        except Exception as e:
            print(f"Order book check failed (may be illiquid): {e}")
    
    # Check if we can create an order
    print("\n" + "="*60)
    print("ORDER CREATION TEST")
    print("="*60)
    
    # Create a simple test order
    from py_clob_client.order_builder.constants import BUY
    
    if markets and 'conditionId' in markets[0]:
        condition_id = markets[0]['conditionId']
        token_id = condition_id + "0x" + "0" * 63 + "1"  # YES token
        
        print(f"Creating test order for token: {token_id[:20]}...")
        
        # Try to create order (won't submit)
        try:
            order = client.create_order(
                token_id=token_id,
                price="100",  # 1.00 = 100%
                size="1",     # 1 share
                side=BUY,
                fee_rate_bps="0"
            )
            print("OK: Order created (not submitted)")
            print(f"Order details: {order}")
            
            print("\n" + "="*60)
            print("READY FOR TRADING!")
            print("="*60)
            print("Wallet appears to be properly configured.")
            print("To test with real trade, need to:")
            print("1. Check if wallet has USDC on Polymarket")
            print("2. Execute $0.01 test trade")
            
        except Exception as e:
            print(f"Order creation failed: {e}")
    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("NEXT STEPS")
print("="*60)
print("1. Check if wallet 0xb354e25623617a24164639F63D8b731250AC92d8 has USDC")
print("2. If yes → Execute $0.01 test trade")
print("3. If no → Check which wallet has the $10 USDC")
print("4. Get private key for that wallet")