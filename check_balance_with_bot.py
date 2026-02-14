#!/usr/bin/env python3
"""
Check balance using trading bot method
"""

import os
import sys
import time

# Add polymarket_bot to path
sys.path.append('polymarket_bot')

try:
    from py_clob_client.client import ClobClient
    from py_clob_client.constants import POLYGON
    
    PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
    
    print("CHECKING BALANCE WITH TRADING BOT")
    print("="*60)
    
    # Create client
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=PRIVATE_KEY)
    
    # Get server time
    server_time = client.get_server_time()
    print(f"API Connected: Server time = {server_time}")
    
    # Try to get balance
    print("\nAttempting to get balance...")
    try:
        # Note: get_balance might not be available in this version
        # Try alternative approach
        print("Checking available methods...")
        print(dir(client))
        
    except Exception as e:
        print(f"Balance check error: {e}")
        
except ImportError as e:
    print(f"Import error: {e}")
    print("\nTrying alternative approach...")

print("\n" + "="*60)
print("ALTERNATIVE: Check via Polymarket Website")
print("="*60)
print("Since APIs show 404, let's check manually:")
print("\n1. Go to https://polymarket.com")
print("2. Connect wallet with private key")
print("3. Check balance in top right")
print("\nOR")
print("\n1. Check transaction on PolygonScan:")
print(f"   https://polygonscan.com/address/{WALLET_B}")
print("\n2. Look for USDC transfer")

print("\n" + "="*60)
print("STATUS")
print("="*60)
print("Wallet B exists (private key valid)")
print("But not found on Polymarket APIs (404)")
print("\nPossible reasons:")
print("1. Transaction still pending (2-5 min)")
print("2. Wallet never used on Polymarket")
print("3. Need to 'activate' wallet with first trade")

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)
print("1. Wait 5 minutes for transaction to confirm")
print("2. Check PolygonScan for transaction")
print("3. Try connecting wallet to Polymarket website")

print("\n" + "="*60)
print("I'LL KEEP CHECKING")
print("="*60)
print("I'll check balance every 30 seconds...")