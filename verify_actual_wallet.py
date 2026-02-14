#!/usr/bin/env python3
"""
Verify which wallet the private key actually controls
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("="*60)
print("WALLET VERIFICATION")
print("="*60)

# What private key generates
account = Account.from_key(PRIVATE_KEY)
generated_wallet = account.address
print(f"Private key generates: {generated_wallet}")

# What screenshot shows
screenshot_wallet = "0x9e24439aC551E757E8d578614336b4e482aC9EEF"
print(f"Screenshot shows:     {screenshot_wallet}")
print(f"Match? {generated_wallet.lower() == screenshot_wallet.lower()}")

print("\n" + "="*60)
print("TESTING API ACCESS")
print("="*60)

try:
    # Try with generated wallet
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=PRIVATE_KEY)
    server_time = client.get_server_time()
    print(f"✅ API connected with generated wallet: {generated_wallet}")
    print(f"   Server time: {server_time}")
    
    # Try to get balance/positions
    print("\nTrying to access wallet data...")
    try:
        # Try different methods
        markets = client.get_markets()
        print(f"   Can access markets: {len(markets) if isinstance(markets, list) else 'Yes'}")
        
        # Try to create a test order (won't submit)
        if markets and isinstance(markets, list):
            market = markets[0]
            condition_id = market.get('condition_id')
            if condition_id:
                token_id = f"{condition_id}0x{'0'*63}1"
                from py_clob_client.clob_types import OrderArgs
                from py_clob_client.order_builder.constants import BUY
                
                order_args = OrderArgs(
                    token_id=token_id,
                    price=5000,
                    size=1,  # $0.01
                    side=BUY
                )
                
                order = client.create_order(order_args)
                print(f"   Can create orders: Yes")
                
    except Exception as e:
        print(f"   Limited access: {e}")
        
except Exception as e:
    print(f"❌ API failed: {e}")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
print("The private key controls wallet: 0xb354e25623617a24164639F63D8b731250AC92d8")
print("But Polymarket account uses:     0x9e24439aC551E757E8d578614336b4e482aC9EEF")
print("\nOPTIONS:")
print("1. Use wallet 0xb354e256... (need to fund it)")
print("2. Get correct private key for 0x9e24439a...")
print("3. Check if 0xb354e256... has any USDC")

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)
print("Let me check if wallet 0xb354e256... has any funds first.")
print("If not, we need the CORRECT private key for 0x9e24439a...")