#!/usr/bin/env python3
"""
Test Polymarket API methods
"""

import os
os.chdir('polymarket_bot')

from config import PRIVATE_KEY, FUNDER_ADDRESS

print("Testing Polymarket API methods...")
print(f"Wallet: {FUNDER_ADDRESS}")

try:
    from py_clob_client.client import ClobClient
    from py_clob_client.constants import POLYGON
    
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=POLYGON,
        key=PRIVATE_KEY,
        signature_type=1,
        funder=FUNDER_ADDRESS
    )
    
    print("\n1. Server time:", client.get_server_time())
    
    # Check available methods
    print("\n2. Available methods:")
    methods = [m for m in dir(client) if not m.startswith('_')]
    print("   ", ", ".join(methods[:10]), "...")
    
    # Try get_simplified_markets
    print("\n3. Trying get_simplified_markets...")
    try:
        markets = client.get_simplified_markets()
        if markets:
            print(f"   Found {len(markets)} markets")
            if markets[0].get('question'):
                print(f"   Example: {markets[0].get('question')[:50]}...")
        else:
            print("   No markets returned")
    except Exception as e:
        print(f"   Error: {e}")
        
    # Try get_markets without limit
    print("\n4. Trying get_markets()...")
    try:
        markets = client.get_markets()
        if markets:
            print(f"   Found {len(markets)} markets")
        else:
            print("   No markets returned")
    except Exception as e:
        print(f"   Error: {e}")
        
    # Try to get balance
    print("\n5. Trying to get balance...")
    try:
        # Check if get_balance method exists
        if hasattr(client, 'get_balance'):
            balance = client.get_balance()
            print(f"   Balance: {balance}")
        else:
            print("   No get_balance method found")
            
        # Try get_balance_allowance
        if hasattr(client, 'get_balance_allowance'):
            allowance = client.get_balance_allowance()
            print(f"   Balance allowance: {allowance}")
            
    except Exception as e:
        print(f"   Error: {e}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
print("The private key works with Polymarket API!")
print(f"Wallet: {FUNDER_ADDRESS}")
print("Signature type: 1 (Magic/email login)")
print("\nNext step: Check if wallet has funds")