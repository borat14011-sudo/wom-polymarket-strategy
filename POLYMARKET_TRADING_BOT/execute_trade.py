#!/usr/bin/env python3
"""
Execute MSTR Trade via Polymarket API
Uses FIXED authentication
"""

import os
import sys
from dotenv import load_dotenv
from polymarket_api_client_fixed import PolymarketAPIClient

# Load credentials
load_dotenv('.env.api')

API_KEY = os.getenv('POLYMARKET_API_KEY')
API_SECRET = os.getenv('POLYMARKET_API_SECRET')
PASSPHRASE = os.getenv('POLYMARKET_PASSPHRASE')
WALLET_ADDRESS = os.getenv('POLY_WALLET_ADDRESS')

print("=" * 60)
print("EXECUTING MSTR TRADE")
print("=" * 60)

# Initialize client
client = PolymarketAPIClient(API_KEY, API_SECRET, PASSPHRASE, WALLET_ADDRESS)

# Test connection first
print("\nTesting API connection...")
try:
    balance = client.get_balance()
    print(f"[OK] Connected! Balance: {balance}")
except Exception as e:
    print(f"[FAIL] Connection failed: {e}")
    sys.exit(1)

# Get MSTR market
print("\nGetting MSTR market...")
try:
    # Try to find the market
    markets = client.get_markets()
    print(f"[OK] Found {len(markets)} markets")
    
    # Look for MSTR market
    mstr_market = None
    for market in markets:
        if 'microstrategy' in market.get('name', '').lower() or '500k' in market.get('name', '').lower():
            mstr_market = market
            break
    
    if mstr_market:
        print(f"[OK] MSTR Market: {mstr_market.get('name')}")
        print(f"  Condition ID: {mstr_market.get('condition_id')}")
    else:
        print("[FAIL] MSTR market not found in list")
        
except Exception as e:
    print(f"[FAIL] Market fetch failed: {e}")

print("\n" + "=" * 60)
print("Ready to place order:")
print("  Market: MSTR 500K BTC Dec 31")
print("  Side: NO")
print("  Price: 0.835")
print("  Size: $8.00")
print("=" * 60)

# UNCOMMENT TO EXECUTE REAL TRADE:
# try:
#     result = client.place_order(
#         market_id="microstrategy-500k-btc-dec-31",
#         side="NO",
#         price=0.835,
#         size=8.00
#     )
#     print("\n[TRADE EXECUTED!]")
#     print(f"Order ID: {result.get('orderId')}")
#     print(f"Status: {result.get('status')}")
# except Exception as e:
#     print(f"\n[FAIL] Trade failed: {e}")

print("\n[DRY RUN - Edit script to execute real trade]")
print("=" * 60)
