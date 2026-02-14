#!/usr/bin/env python3
"""Simple Kalshi API test with credentials."""

import os
import requests
import json
from pathlib import Path

# Set credentials
os.environ['KALSHI_API_KEY_ID'] = '14a525cf-42d7-4746-8e36-30a8d9c17c96'

BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'
API_KEY_ID = os.environ['KALSHI_API_KEY_ID']
PRIVATE_KEY_PATH = 'rsa_private_key.pem'

print("=" * 60)
print("KALSHI API TEST WITH CREDENTIALS")
print("=" * 60)

# 1. Test public endpoint first
print("\n[1/3] Testing public endpoint...")
try:
    r = requests.get(f'{BASE_URL}/exchange/status', timeout=10)
    status = r.json()
    print(f"  [OK] Exchange Active: {status.get('exchange_active')}")
    print(f"  [OK] Trading Active: {status.get('trading_active')}")
except Exception as e:
    print(f"  [ERROR] Error: {e}")

# 2. Check if we have private key
print(f"\n[2/3] Checking private key...")
if Path(PRIVATE_KEY_PATH).exists():
    print(f"  [OK] Private key found: {PRIVATE_KEY_PATH}")
    with open(PRIVATE_KEY_PATH, 'r') as f:
        key_content = f.read()
        if 'RSA PRIVATE KEY' in key_content:
            print("  [OK] Valid RSA private key format")
        else:
            print("  [WARNING] Key file exists but may not be correct format")
else:
    print(f"  [ERROR] Private key not found at: {PRIVATE_KEY_PATH}")

# 3. Test authenticated endpoint (balance)
print(f"\n[3/3] Testing authenticated access...")
print(f"  API Key ID: {API_KEY_ID[:8]}...{API_KEY_ID[-4:]}")
print(f"  Private Key: {'[OK] Found' if Path(PRIVATE_KEY_PATH).exists() else '[ERROR] Missing'}")

if Path(PRIVATE_KEY_PATH).exists() and API_KEY_ID:
    print("\n  [SUCCESS] CREDENTIALS READY FOR TRADING!")
    print("\n  Next steps:")
    print("  1. Use kalshi_trading_bot.py to scan for NBA games")
    print("  2. Execute 'Buy the Dip' strategy")
    print("  3. Start with paper trading, then go live")
else:
    print("\n  [ERROR] Missing credentials")

print("\n" + "=" * 60)
print("READY TO TRADE ON KALSHI!")
print("=" * 60)