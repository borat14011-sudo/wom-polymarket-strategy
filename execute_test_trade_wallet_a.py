#!/usr/bin/env python3
"""
Execute test trade with Wallet A configuration
"""

import os
import sys
from pathlib import Path

# Add polymarket_bot to path
sys.path.append(str(Path(__file__).parent / 'polymarket_bot'))

from authentication import PolymarketAuthenticator
from trade_executor import TradeExecutor

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
WALLET_A = "0x9e24439aC551E757E8d578614336b4e482aC9EEF"

print("="*60)
print("EXECUTE TEST TRADE - WALLET A")
print("="*60)
print(f"Using Wallet: {WALLET_A}")
print(f"Private key: {PRIVATE_KEY[:20]}...")

print("\n" + "="*60)
print("STEP 1: Create Authenticator")
print("="*60)

try:
    # Create authenticator with Wallet A address
    auth = PolymarketAuthenticator(
        wallet_address=WALLET_A,
        private_key=PRIVATE_KEY
    )
    print("SUCCESS: Authenticator created")
    
    # Get authentication headers
    headers = auth.get_auth_headers()
    print(f"Auth headers generated: {list(headers.keys())}")
    
except Exception as e:
    print(f"FAILED to create authenticator: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("STEP 2: Create Trade Executor")
print("="*60)

try:
    executor = TradeExecutor(auth)
    print("SUCCESS: Trade executor created")
    
    # Check balance
    print("\nChecking balance...")
    balance = executor.get_balance()
    print(f"Balance: {balance}")
    
except Exception as e:
    print(f"FAILED to create executor: {e}")
    print("Trying alternative approach...")

print("\n" + "="*60)
print("STEP 3: Try Direct Trade")
print("="*60)

# Find a test market
print("Looking for test market...")
try:
    import requests
    
    # Get active markets
    markets_url = "https://gamma-api.polymarket.com/markets?limit=10"
    response = requests.get(markets_url)
    
    if response.status_code == 200:
        markets = response.json()
        print(f"Found {len(markets)} markets")
        
        # Find a small market for testing
        test_market = None
        for market in markets:
            if market.get('volume_24h', 0) > 1000:  # Some volume
                test_market = market
                break
        
        if test_market:
            print(f"Test market: {test_market['question']}")
            print(f"Market ID: {test_market['id']}")
            
            # Try to place a tiny order
            print("\nAttempting test order...")
            # This will likely fail due to authentication mismatch
            # but worth trying
            
        else:
            print("No suitable test market found")
            
    else:
        print(f"Failed to get markets: {response.status_code}")
        
except Exception as e:
    print(f"Market search failed: {e}")

print("\n" + "="*60)
print("ANALYSIS")
print("="*60)
print("The private key mathematically belongs to Wallet B.")
print("But Magic wallets might work differently.")

print("\nTwo possibilities:")
print("1. Magic uses different key derivation")
print("   - This key might actually work for Wallet A")
print("   - Need to test with actual trade")

print("2. Need Wallet A's actual private key")
print("   - Get from reveal.magic.link WHILE logged into Wallet A")
print("   - Or use different authentication method")

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)
print("Let me try one more thing: check if we can use")
print("Magic session authentication instead of private key.")

print("\n" + "="*60)
print("NEXT STEP")
print("="*60)
print("Trying Magic session extraction...")