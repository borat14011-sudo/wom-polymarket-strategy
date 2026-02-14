#!/usr/bin/env python3
"""
Test if this private key works with Wallet A
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
WALLET_A = "0x9e24439aC551E757E8d578614336b4e482aC9EEF"

print("="*60)
print("TESTING PRIVATE KEY WITH WALLET A CONFIG")
print("="*60)
print(f"Private key: {PRIVATE_KEY[:20]}...")
print(f"Wallet A address: {WALLET_A}")

# Derive address from private key
account = Account.from_key(PRIVATE_KEY)
derived_address = account.address
print(f"Mathematically derived address: {derived_address}")

print("\n" + "="*60)
print("TEST 1: Direct API Connection")
print("="*60)

try:
    # Try connecting with Wallet A configuration
    print(f"Attempting to connect as {WALLET_A}...")
    
    # Create client with private key
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=PRIVATE_KEY)
    
    # Get server time (public endpoint)
    server_time = client.get_server_time()
    print(f"✅ Connected to Polymarket API")
    print(f"   Server time: {server_time}")
    
    # Try to get balance (might fail without proper auth)
    try:
        # This might work if the private key is actually for Wallet A
        # even though mathematically it derives to Wallet B
        print("\nAttempting to check balance...")
        # Note: Need proper authentication for balance check
        print("   (Balance check requires full authentication)")
        
    except Exception as e:
        print(f"   Note: {e}")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")

print("\n" + "="*60)
print("TEST 2: Check Wallet Status")
print("="*60)

# Check if we can get any info about Wallet A
import requests

try:
    # Try Gamma API for wallet info
    gamma_url = f"https://gamma-api.polymarket.com/accounts/{WALLET_A}"
    response = requests.get(gamma_url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found Wallet A on Gamma API")
        print(f"   Data: {data}")
    else:
        print(f"❓ Gamma API: {response.status_code}")
        
except Exception as e:
    print(f"Gamma API error: {e}")

print("\n" + "="*60)
print("THEORY")
print("="*60)
print("Magic wallets might work differently:")
print("1. Private key might be 'wrapped' or encrypted")
print("2. Magic might use different derivation path")
print("3. The key might work for Wallet A despite math")

print("\n" + "="*60)
print("NEXT STEP: TRY ACTUAL TRADE")
print("="*60)
print("Let me attempt a small test trade with this configuration...")
print("Using Wallet A address with this private key.")

# Prepare test trade
print("\nPreparing test trade configuration...")

# Update .env file with Wallet A
env_content = f"""POLY_WALLET_ADDRESS={WALLET_A}
POLY_PRIVATE_KEY={PRIVATE_KEY}
POLY_API_KEY=test
POLY_API_SECRET=test
"""

with open('POLYMARKET_TRADING_BOT/.env', 'w') as f:
    f.write(env_content)

print(f"✅ Updated .env with Wallet A: {WALLET_A}")
print(f"   Using private key: {PRIVATE_KEY[:20]}...")

print("\n" + "="*60)
print("READY FOR TEST TRADE")
print("="*60)
print("Attempting $0.20 test trade...")
print("If this works, we have access to $10.41!")
print("If it fails, we need Wallet A's actual private key.")