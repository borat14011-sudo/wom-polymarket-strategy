#!/usr/bin/env python3

import os

# Read .env file manually
env_path = 'polymarket_bot/.env'
with open(env_path, 'r') as f:
    lines = f.readlines()

# Parse key-value pairs
env_vars = {}
for line in lines:
    line = line.strip()
    if line and not line.startswith('#'):
        if '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()

PRIVATE_KEY = env_vars.get('POLYMARKET_PRIVATE_KEY')
FUNDER_ADDRESS = env_vars.get('POLYMARKET_FUNDER_ADDRESS')

print(f"Private key: {PRIVATE_KEY[:20]}..." if PRIVATE_KEY else "No private key")
print(f"Wallet address: {FUNDER_ADDRESS}" if FUNDER_ADDRESS else "No wallet address")

if PRIVATE_KEY and FUNDER_ADDRESS:
    from eth_account import Account
    acc = Account.from_key(PRIVATE_KEY)
    derived = acc.address
    
    print(f"\nDerived address: {derived}")
    print(f"Expected address: {FUNDER_ADDRESS}")
    
    if derived.lower() == FUNDER_ADDRESS.lower():
        print("\n✅ MATCH! This private key belongs to Wallet A")
        print("   We can trade with $10.41 immediately!")
    else:
        print(f"\n❌ MISMATCH! Private key belongs to different wallet")
        print(f"   It controls: {derived}")
        print(f"   Not: {FUNDER_ADDRESS}")
        
        # Check if it's Wallet B
        WALLET_B = "0xb354e25623617a24164639F63D8b731250AC92d8"
        if derived.lower() == WALLET_B.lower():
            print(f"\n   This is Wallet B (we already have this private key)")
            print(f"   Wallet B has $0 balance, needs $10 funding")