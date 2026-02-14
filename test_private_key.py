#!/usr/bin/env python3
"""
Test if private key matches wallet address
"""

from eth_account import Account

# Private key from test_trade_execution.py
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

# Wallet address from .env.api
WALLET_ADDRESS = "0x32684d1162eF8A6E13213A67269271734182E667"

print("Testing private key...")
try:
    account = Account.from_key(PRIVATE_KEY)
    derived_address = account.address
    print(f"Private key derives to address: {derived_address}")
    print(f"Target wallet address: {WALLET_ADDRESS}")
    
    if derived_address.lower() == WALLET_ADDRESS.lower():
        print("[MATCH] Private key matches wallet address!")
    else:
        print("[NO MATCH] Private key does not match wallet address")
        print(f"Difference: {derived_address} != {WALLET_ADDRESS}")
        
except Exception as e:
    print(f"[ERROR] Failed to derive address: {e}")