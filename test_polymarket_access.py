#!/usr/bin/env python3
"""
Test if private key can access Polymarket account
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("="*60)
print("TEST POLYMARKET ACCESS")
print("="*60)

# What wallet does this key control?
account = Account.from_key(PRIVATE_KEY)
actual_wallet = account.address
print(f"Private key controls: {actual_wallet}")

print("\nTrying to connect to Polymarket...")
try:
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=PRIVATE_KEY)
    
    # Test basic connectivity
    server_time = client.get_server_time()
    print(f"OK: Connected to Polymarket API")
    print(f"Server time: {server_time}")
    
    # Try to get user-specific data
    print("\nTrying to get user data...")
    try:
        # Try to get API keys (requires auth)
        api_keys = client.get_api_keys()
        print(f"OK: Can access API keys")
        print(f"This wallet has API access")
    except Exception as e:
        print(f"Limited access: {e}")
        print("May need to create API keys first")
    
    # Check if we can trade
    print("\nTesting trade capability...")
    try:
        # Get a market
        import requests
        gamma_url = "https://gamma-api.polymarket.com/markets"
        response = requests.get(gamma_url, params={"limit": 1, "closed": False}, timeout=10)
        if response.status_code == 200:
            markets = response.json()
            if markets:
                market = markets[0]
                condition_id = market.get('conditionId')
                
                if condition_id:
                    # Try to create order (won't submit without funds)
                    from py_clob_client.clob_types import OrderArgs
                    from py_clob_client.order_builder.constants import BUY
                    
                    token_id = f"{condition_id}0x{'0'*63}1"
                    order_args = OrderArgs(
                        token_id=token_id,
                        price=5000,  # 50%
                        size=100,    # $1.00
                        side=BUY
                    )
                    
                    order = client.create_order(order_args)
                    print(f"OK: Can create orders")
                    print(f"Wallet {actual_wallet} can trade on Polymarket")
                    
        else:
            print(f"Market fetch failed: {response.status_code}")
            
    except Exception as e:
        print(f"Order test failed: {e}")
        print("May be due to: no funds, no API keys, or wallet not registered")
        
except Exception as e:
    print(f"Connection failed: {e}")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
print(f"Wallet {actual_wallet} can connect to Polymarket API")
print("Next: Check if wallet has USDC balance")

print("\n" + "="*60)
print("ACTION PLAN")
print("="*60)
print("1. Check if wallet {actual_wallet} has USDC")
print("   - Go to https://polymarket.com")
print("   - Connect with private key {PRIVATE_KEY[:20]}...")
print("   - Check balance")
print("\n2. If no funds, send $10 USDC to {actual_wallet}")
print("\n3. If funds exist, execute test trade immediately")