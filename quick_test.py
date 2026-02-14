#!/usr/bin/env python3

import os
os.chdir('polymarket_bot')

from dotenv import load_dotenv
load_dotenv()

PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
FUNDER_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print(f"Private key: {PRIVATE_KEY[:20]}...")
print(f"Wallet address: {FUNDER_ADDRESS}")

from eth_account import Account
acc = Account.from_key(PRIVATE_KEY)
print(f"Derived address: {acc.address}")

if acc.address.lower() == FUNDER_ADDRESS.lower():
    print("MATCH! Can trade with Wallet A")
else:
    print("MISMATCH! Private key is for different wallet")
    print(f"  Expected: {FUNDER_ADDRESS}")
    print(f"  Got: {acc.address}")