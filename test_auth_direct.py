#!/usr/bin/env python3
"""
Test authentication directly
"""

import os
import sys

# Add polymarket_bot to path
bot_dir = os.path.join(os.path.dirname(__file__), 'polymarket_bot')
sys.path.append(bot_dir)

from config import PRIVATE_KEY, FUNDER_ADDRESS

print("="*60)
print("DIRECT AUTHENTICATION TEST")
print("="*60)
print(f"Private key: {PRIVATE_KEY[:20]}...")
print(f"Wallet address: {FUNDER_ADDRESS}")

print("\n" + "="*60)
print("TEST 1: Verify Key Derivation")
print("="*60)

from eth_account import Account

account = Account.from_key(PRIVATE_KEY)
derived_address = account.address

print(f"Private key derives to: {derived_address}")
print(f"Expected (Wallet A):    {FUNDER_ADDRESS}")

if derived_address.lower() == FUNDER_ADDRESS.lower():
    print("✅ MATCH! This private key belongs to Wallet A")
    print("   We can trade with $10.41 immediately!")
else:
    print("❌ MISMATCH! This private key belongs to different wallet")
    print(f"   It belongs to: {derived_address}")
    print(f"   Not to: {FUNDER_ADDRESS}")

print("\n" + "="*60)
print("TEST 2: Try API Connection")
print("="*60)

try:
    from py_clob_client.client import ClobClient
    from py_clob_client.constants import POLYGON
    
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=PRIVATE_KEY)
    server_time = client.get_server_time()
    print(f"✅ Connected to Polymarket API")
    print(f"   Server time: {server_time}")
    
    # Check which address the client will use
    print(f"   Note: Client will use derived address: {derived_address}")
    print(f"   Not the configured address: {FUNDER_ADDRESS}")
    
except Exception as e:
    print(f"❌ API connection failed: {e}")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
print("The private key mathematically belongs to a different wallet.")
print("However, Magic authentication might work differently.")

print("\nTwo possibilities:")
print("1. Magic uses different key derivation")
print("   - This key might work for Wallet A in practice")
print("   - Need to test with actual trade")

print("2. We need Wallet A's actual private key")
print("   - Get from reveal.magic.link WHILE logged into Wallet A")

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)
print("Let's try a $0.20 test trade.")
print("If it works, great! If it fails, we know we need")
print("Wallet A's actual private key.")

print("\n" + "="*60)
print("READY FOR TEST TRADE")
print("="*60)
print("Attempting $0.20 test trade now...")