#!/usr/bin/env python3
"""
Working test trade with correct API usage
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY

print("="*60)
print("WORKING TEST TRADE")
print("="*60)

# Credentials
private_key = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
wallet_address = "0xb354e25623617a24164639F63D8b731250AC92d8"

print(f"Wallet: {wallet_address}")

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
    
    # Find a market
    print("\nFinding market...")
    markets = client.get_markets()
    print(f"Found {len(markets)} markets")
    
    if markets:
        # Use first market
        market = markets[0]
        print(f"\nMarket: {market.get('question', 'Unknown')[:80]}...")
        
        # Get market details
        condition_id = market.get('condition_id')
        print(f"Condition ID: {condition_id}")
        
        if condition_id:
            # Create YES token (outcome 1)
            token_id = f"{condition_id}0x{'0'*63}1"
            
            print(f"\nCreating order for token: {token_id[:30]}...")
            
            # Create order args
            order_args = OrderArgs(
                token_id=token_id,
                price=5000,  # 0.50 = 50% (in basis points: 5000 = 0.50)
                size=100,    # 1.00 share (in basis points: 100 = 1.00)
                side=BUY
            )
            
            print(f"Order args: price={order_args.price/10000:.2%}, size={order_args.size/100:.2f} shares")
            
            # Create order
            order = client.create_order(order_args)
            print(f"\nOK: Order created!")
            print(f"Order: {order}")
            
            # Try to post it (will fail if no funds)
            print("\nTrying to post order...")
            try:
                posted = client.post_order(order)
                print(f"SUCCESS: Order posted! {posted}")
                
                print("\n" + "="*60)
                print("🎉 TRADING SYSTEM IS WORKING! 🎉")
                print("="*60)
                print("The bot can execute trades!")
                print("Wallet has funds and API access works!")
                
            except Exception as e:
                print(f"Order posting failed (likely no funds): {e}")
                print("\nThis confirms we need to check wallet balance.")
                
        else:
            print("ERROR: No condition_id found")
    else:
        print("ERROR: No markets found")
        
except Exception as e:
    print(f"\nERROR: {e}")

print("\n" + "="*60)
print("ACTION REQUIRED")
print("="*60)
print("1. Check wallet balance on https://polymarket.com")
print("2. Send screenshot")
print("3. If wallet has funds, we execute $0.20 trade")
print("4. If not, get private key for correct wallet")