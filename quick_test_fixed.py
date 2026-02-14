#!/usr/bin/env python3

import os
from pathlib import Path

# Change to polymarket_bot directory
os.chdir('polymarket_bot')

from dotenv import load_dotenv
load_dotenv()

PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
FUNDER_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print(f"Private key loaded: {PRIVATE_KEY is not None}")
print(f"Wallet address loaded: {FUNDER_ADDRESS is not None}")

if PRIVATE_KEY:
    print(f"Private key: {PRIVATE_KEY[:20]}...")
    
if FUNDER_ADDRESS:
    print(f"Wallet address: {FUNDER_ADDRESS}")

if PRIVATE_KEY and FUNDER_ADDRESS:
    from eth_account import Account
    try:
        acc = Account.from_key(PRIVATE_KEY)
        print(f"Derived address: {acc.address}")
        
        if acc.address.lower() == FUNDER_ADDRESS.lower():
            print("MATCH! Can trade with Wallet A")
        else:
            print("MISMATCH! Private key is for different wallet")
            print(f"  Expected: {FUNDER_ADDRESS}")
            print(f"  Got: {acc.address}")
    except Exception as e:
        print(f"Error deriving address: {e}")