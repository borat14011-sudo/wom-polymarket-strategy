#!/usr/bin/env python3
"""
Check wallet balance via Polymarket API
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

# Test both wallet possibilities
wallets_to_check = [
    ("0xb354e25623617a24164639F63D8b731250AC92d8", "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"),
    # We don't have private key for the other wallet
]

print("="*60)
print("WALLET BALANCE CHECK")
print("="*60)

for wallet_address, private_key in wallets_to_check:
    print(f"\nChecking wallet: {wallet_address}")
    print(f"Private key: {private_key[:20]}...")
    
    # Verify match
    account = Account.from_key(private_key)
    if account.address.lower() != wallet_address.lower():
        print(f"WARNING: Private key generates {account.address}, not {wallet_address}")
        continue
    
    try:
        # Initialize client
        client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=private_key)
        
        # Try to get positions/balance
        print("Trying to get positions...")
        
        # Method 1: Try get_positions
        try:
            positions = client.get_positions()
            print(f"Positions: {positions}")
        except Exception as e:
            print(f"get_positions failed: {e}")
        
        # Method 2: Try get_balance (if method exists)
        try:
            # Check available methods
            if hasattr(client, 'get_balance'):
                balance = client.get_balance()
                print(f"Balance: {balance}")
        except Exception as e:
            print(f"get_balance failed: {e}")
            
        # Method 3: Try to create a small order to see if we have funds
        print("\nTrying to create test order...")
        try:
            # Get a market
            markets = client.get_markets(limit=1)
            if markets:
                market = markets[0]
                condition_id = market.get('conditionId')
                
                if condition_id:
                    # Create YES token ID
                    token_id = condition_id + "0x" + "0" * 63 + "1"
                    
                    # Try to create order (won't submit)
                    from py_clob_client.order_builder.constants import BUY
                    
                    order = client.create_order(
                        token_id=token_id,
                        price="100",  # 1.00 = 100%
                        size="1",     # 1 share = $0.01
                        side=BUY,
                        fee_rate_bps="0"
                    )
                    
                    print(f"Test order created (not submitted)")
                    print(f"This suggests wallet can trade")
                    
        except Exception as e:
            print(f"Order creation test failed: {e}")
            
    except Exception as e:
        print(f"Client initialization failed: {e}")

print("\n" + "="*60)
print("MANUAL CHECK REQUIRED")
print("="*60)
print("The API doesn't show balance directly.")
print("")
print("PLEASE DO THIS:")
print("1. Go to https://polymarket.com")
print("2. Connect wallet")
print("3. Check USDC balance manually")
print("4. Send screenshot showing:")
print("   - Wallet address")
print("   - USDC balance")
print("   - Any positions")
print("")
print("This is the FINAL step before trading!")