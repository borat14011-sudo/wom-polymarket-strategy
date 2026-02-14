#!/usr/bin/env python3
"""
Verify Wallet B setup
"""

from eth_account import Account

WALLET_B = "0xb354e25623617a24164639F63D8b731250AC92d8"
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("WALLET B SETUP VERIFICATION")
print("="*60)

# Verify key derivation
acc = Account.from_key(PRIVATE_KEY)
derived = acc.address

print(f"Private key: {PRIVATE_KEY[:20]}...")
print(f"Derived address: {derived}")
print(f"Expected address: {WALLET_B}")

if derived.lower() == WALLET_B.lower():
    print("SUCCESS: Private key matches Wallet B")
else:
    print("ERROR: Private key does not match Wallet B")
    exit(1)

print("\n" + "="*60)
print("CONFIGURATION STATUS")
print("="*60)

# Check config files
import os

configs = [
    ("polymarket_bot/.env", "POLYMARKET_FUNDER_ADDRESS"),
    ("POLYMARKET_TRADING_BOT/.env", "POLY_WALLET_ADDRESS"),
]

for file_path, key in configs:
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
            if WALLET_B in content:
                print(f"OK: {file_path} contains Wallet B")
            else:
                print(f"WARNING: {file_path} may not have Wallet B")
    else:
        print(f"MISSING: {file_path}")

print("\n" + "="*60)
print("READY FOR FUNDING")
print("="*60)
print(f"Send $10 USDC to: {WALLET_B}")
print("Network: Polygon")
print("Token: USDC")
print("\nOnce funded, trading begins immediately!")