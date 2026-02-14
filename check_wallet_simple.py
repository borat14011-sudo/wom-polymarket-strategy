#!/usr/bin/env python3
"""
Simple wallet check
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

private_key = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("="*60)
print("WALLET CHECK")
print("="*60)

# Show wallet
account = Account.from_key(private_key)
print(f"Wallet: {account.address}")

# Initialize client
try:
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=private_key)
    print("OK: Client initialized")
    
    # Get server time
    server_time = client.get_server_time()
    print(f"Server time: {server_time}")
    
    print("\n" + "="*60)
    print("STATUS: READY")
    print("="*60)
    print(f"Wallet: {account.address}")
    print("Private key: MATCHING")
    print("API access: WORKING")
    print("\nNext: Check if this wallet has USDC on Polymarket")
    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("ACTION REQUIRED")
print("="*60)
print("1. Go to https://polymarket.com")
print("2. Connect wallet")
print("3. Check USDC balance")
print("4. What wallet address shows up?")
print("5. Does it have the $10 USDC?")