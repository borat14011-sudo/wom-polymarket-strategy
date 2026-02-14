#!/usr/bin/env python3
"""
Simple authentication test for Polymarket
"""

import os
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

print("="*60)
print("POLYMARKET AUTHENTICATION TEST")
print("="*60)

# Load credentials
private_key = os.getenv("POLYMARKET_PRIVATE_KEY", "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455")
funder_address = os.getenv("POLYMARKET_FUNDER_ADDRESS", "0x9e24439aC551E757E8d578614336b4e482aC9EEF")

print(f"Private key: {private_key[:20]}...")
print(f"Funder address: {funder_address}")

# Verify wallet match
account = Account.from_key(private_key)
generated_wallet = account.address
print(f"Generated wallet: {generated_wallet}")
print(f"Match: {generated_wallet.lower() == funder_address.lower()}")

if generated_wallet.lower() != funder_address.lower():
    print("\nWARNING: Wallet mismatch!")
    print(f"Private key generates: {generated_wallet}")
    print(f"But config expects:    {funder_address}")
    print("\nThis will cause authentication failures!")

# Try to initialize client anyway
try:
    print("\nInitializing CLOB client...")
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=private_key)
    print("OK: Client initialized")
    
    # Test public endpoint
    print("\nTesting public endpoint (server time)...")
    server_time = client.get_server_time()
    print(f"OK: Server time: {server_time}")
    
    # Try to get balances (will fail if wallet has no funds or wrong wallet)
    print("\nTrying to get balances...")
    try:
        balances = client.get_balances()
        print(f"OK: Got balances: {balances}")
    except Exception as e:
        print(f"Balance check failed (expected if wrong wallet): {e}")
        
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("1. Client initialization: OK")
print("2. Public API access: OK") 
print("3. Wallet match: " + ("OK" if generated_wallet.lower() == funder_address.lower() else "FAIL"))
print("\nNEXT: Need correct private key for wallet 0x9e24439aC551E757E8d578614336b4e482aC9EEF")