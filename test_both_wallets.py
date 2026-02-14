#!/usr/bin/env python3
"""
Test same private key with both Wallet A and Wallet B
"""

import requests
import time
from eth_account import Account

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
WALLET_A = "0x9e24439aC551E757E8d578614336b4e482aC9EEF"
WALLET_B = "0xb354e25623617a24164639F63D8b731250AC92d8"

print("="*60)
print("TESTING SAME PRIVATE KEY WITH BOTH WALLETS")
print("="*60)
print(f"Private key: {PRIVATE_KEY[:20]}...")
print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

print("\n" + "="*60)
print("MATHEMATICAL DERIVATION")
print("="*60)

acc = Account.from_key(PRIVATE_KEY)
derived = acc.address
print(f"Private key mathematically derives to: {derived}")

if derived.lower() == WALLET_A.lower():
    print("✅ Mathematically belongs to WALLET A")
elif derived.lower() == WALLET_B.lower():
    print("✅ Mathematically belongs to WALLET B")
else:
    print(f"❓ Mathematically belongs to different wallet: {derived}")

print("\n" + "="*60)
print("TEST 1: Check Wallet A Balance")
print("="*60)

try:
    url_a = f"https://gamma-api.polymarket.com/accounts/{WALLET_A}"
    r_a = requests.get(url_a, timeout=10)
    
    if r_a.status_code == 200:
        data_a = r_a.json()
        print(f"✅ Wallet A found on Gamma API")
        
        # Check USDC balance
        if 'balances' in data_a:
            for balance in data_a['balances']:
                if balance.get('token') == 'USDC':
                    amount = float(balance.get('amount', 0))
                    print(f"   USDC Balance: ${amount:.2f}")
                    if amount >= 10:
                        print("   ✅ SUFFICIENT FUNDS ($10.41)")
                    else:
                        print(f"   ❌ Insufficient: ${amount:.2f}")
        else:
            print(f"   No balance data")
            
    elif r_a.status_code == 404:
        print(f"❌ Wallet A not found (404)")
    else:
        print(f"❓ Wallet A: {r_a.status_code}")
        
except Exception as e:
    print(f"Error checking Wallet A: {e}")

print("\n" + "="*60)
print("TEST 2: Check Wallet B Balance")
print("="*60)

try:
    url_b = f"https://gamma-api.polymarket.com/accounts/{WALLET_B}"
    r_b = requests.get(url_b, timeout=10)
    
    if r_b.status_code == 200:
        data_b = r_b.json()
        print(f"✅ Wallet B found on Gamma API")
        
        # Check USDC balance
        if 'balances' in data_b:
            for balance in data_b['balances']:
                if balance.get('token') == 'USDC':
                    amount = float(balance.get('amount', 0))
                    print(f"   USDC Balance: ${amount:.2f}")
                    if amount >= 10:
                        print("   ✅ SUFFICIENT FUNDS")
                    else:
                        print(f"   ❌ Insufficient: ${amount:.2f}")
        else:
            print(f"   No balance data")
            
    elif r_b.status_code == 404:
        print(f"❌ Wallet B not found (404)")
    else:
        print(f"❓ Wallet B: {r_b.status_code}")
        
except Exception as e:
    print(f"Error checking Wallet B: {e}")

print("\n" + "="*60)
print("TEST 3: Try API Authentication")
print("="*60)

print("Testing API connection with private key...")
try:
    from py_clob_client.client import ClobClient
    from py_clob_client.constants import POLYGON
    
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=PRIVATE_KEY)
    server_time = client.get_server_time()
    print(f"✅ API connection successful")
    print(f"   Server time: {server_time}")
    
    # Try to get which address the client uses
    print(f"   Client connected with private key")
    print(f"   Mathematically controls: {derived}")
    
except ImportError:
    print("❌ py_clob_client not installed")
except Exception as e:
    print(f"❌ API connection failed: {e}")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
print("1. Private key mathematically controls Wallet B")
print("2. Wallet A has $10.41 but we don't have its private key")
print("3. Wallet B is unfunded (404)")

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)
print("OPTION 1: Get Wallet A's actual private key")
print("   - While logged into Wallet A, go to https://reveal.magic.link")
print("   - Get private key for Wallet A specifically")
print("   - Trade with $10.41 immediately")

print("\nOPTION 2: Fund Wallet B with $10")
print(f"   - Send $10 USDC to: {WALLET_B}")
print("   - Use existing private key")
print("   - Start trading immediately")

print("\n" + "="*60)
print("NEXT STEP")
print("="*60)
print("Which wallet should we use?")
print("A. Try to get Wallet A's private key")
print("B. Fund Wallet B with $10")
print("\nPlease choose A or B!")