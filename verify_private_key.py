#!/usr/bin/env python3
"""
Verify which wallet this private key corresponds to
"""

from eth_account import Account

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("="*60)
print("VERIFYING PRIVATE KEY")
print("="*60)
print(f"Private key: {PRIVATE_KEY}")

# Derive wallet address
account = Account.from_key(PRIVATE_KEY)
wallet_address = account.address

print(f"Derived wallet address: {wallet_address}")

WALLET_A = "0x9e24439aC551E757E8d578614336b4e482aC9EEF"
WALLET_B = "0xb354e25623617a24164639F63D8b731250AC92d8"

print("\n" + "="*60)
print("COMPARISON")
print("="*60)
print(f"Wallet A (has $10.41): {WALLET_A}")
print(f"Wallet B (private key): {WALLET_B}")
print(f"This private key gives: {wallet_address}")

print("\n" + "="*60)
print("RESULT")
print("="*60)
if wallet_address.lower() == WALLET_B.lower():
    print("✅ This is the private key for WALLET B")
    print("   - We already have this private key")
    print("   - Wallet B has $0 balance")
    print("   - Needs $10 funding")
elif wallet_address.lower() == WALLET_A.lower():
    print("✅ This is the private key for WALLET A")
    print("   - PERFECT! We can trade with $10.41")
    print("   - Update configuration immediately")
    print("   - Start trading NOW")
else:
    print("❓ This is a DIFFERENT wallet")
    print(f"   Address: {wallet_address}")
    print("   Need to check balance")

print("\n" + "="*60)
print("NEXT STEP")
print("="*60)
print("Let me check the actual derived address...")