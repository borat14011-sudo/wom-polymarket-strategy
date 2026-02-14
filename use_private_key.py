#!/usr/bin/env python3
"""
How to use the private key with Polymarket
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('polymarket_bot/.env')

PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
WALLET_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print("="*60)
print("HOW TO USE THE PRIVATE KEY WITH POLYMARKET")
print("="*60)
print(f"Private key: {PRIVATE_KEY[:20]}...")
print(f"Wallet address: {WALLET_ADDRESS}")

print("\n" + "="*60)
print("METHOD 1: Direct API Authentication (EIP-712)")
print("="*60)

print("""
The private key can be used directly with Polymarket's CLOB API
using EIP-712 signatures. This is what the py-clob-client does.

Steps:
1. Import the private key into a wallet (MetaMask, etc.)
2. Use it to sign EIP-712 typed data messages
3. Send signed messages to Polymarket API

Example code:
```
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=POLYGON,
    key=PRIVATE_KEY,
    signature_type=1,  # Magic/email login
    funder=WALLET_ADDRESS
)
```
""")

print("\n" + "="*60)
print("METHOD 2: Manual Wallet Connection")
print("="*60)

print("""
To use the private key manually:

1. Install MetaMask browser extension
2. Click "Import Account"
3. Paste the private key: """ + PRIVATE_KEY[:20] + """...
4. Connect to https://polymarket.com
5. The wallet will appear with any balance

This is the easiest way to check if the wallet has funds.
""")

print("\n" + "="*60)
print("METHOD 3: Magic.link Email Login")
print("="*60)

print("""
The private key might be from Magic.link email login.

If you logged into Polymarket with email (Magic.link), then:
1. Go to https://reveal.magic.link/polymarket
2. Log in with the same email
3. It will show the private key
4. That's the key you gave me

This key controls the wallet that Polymarket created for your email.
""")

print("\n" + "="*60)
print("CRITICAL: CHECK WALLET BALANCE")
print("="*60)

print("""
Before we can trade, we need to know:

1. Does this wallet have funds?
2. If not, which wallet has the $10.41?

ACTION REQUIRED:
1. Import the private key into MetaMask
2. Connect to https://polymarket.com
3. Check the USDC balance
4. Tell me the balance

OR

1. Log into Polymarket with your email
2. Check which wallet appears
3. Check the balance
4. Get that wallet's private key from https://reveal.magic.link
""")

print("\n" + "="*60)
print("NEXT STEP")
print("="*60)
print("Please try METHOD 2 (MetaMask import) and tell me:")
print("1. Which wallet address appears?")
print("2. What's the USDC balance?")
print("\nThis will solve everything in 2 minutes!")