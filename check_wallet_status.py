#!/usr/bin/env python3
"""
Check wallet status and balances
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
import requests

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("="*60)
print("WALLET STATUS CHECK")
print("="*60)

# Initialize wallet
print("\n1. Initializing wallet...")
account = Account.from_key(PRIVATE_KEY)
print(f"   Address: {account.address}")

# Initialize CLOB client
print("\n2. Initializing CLOB client...")
client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=POLYGON,
    key=account.key,
    signature_type=0,
    funder=account.address
)

# Try to get positions
print("\n3. Checking positions...")
try:
    # Note: This might require authentication
    positions = client.get_user_positions(account.address)
    if positions:
        print(f"   Found {len(positions)} positions")
        for pos in positions[:3]:  # Show first 3
            print(f"   - {pos}")
    else:
        print("   No positions found")
except Exception as e:
    print(f"   Could not fetch positions: {e}")

# Check Polymarket website for wallet (simulated)
print("\n4. Checking Polymarket portfolio...")
print(f"   Visit: https://polymarket.com/account/{account.address}")
print(f"   Or login with: Borat14011@gmail.com")

# Check recent activity via API
print("\n5. Checking recent trades...")
try:
    url = f"https://data-api.polymarket.com/trades?user={account.address}&limit=5"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        trades = response.json()
        print(f"   Found {len(trades)} recent trades")
        for trade in trades[:3]:
            print(f"   - {trade.get('side', '')} ${trade.get('amount', 0)}")
    else:
        print(f"   No recent trades found (HTTP {response.status_code})")
except Exception as e:
    print(f"   Could not fetch trades: {e}")

print("\n" + "="*60)
print("READY FOR TEST TRADE")
print("="*60)
print("\nWallet is configured and ready.")
print(f"Private key: {PRIVATE_KEY[:20]}...")
print(f"Address: {account.address}")
print("\nProceed with $0.20 test trade when ready.")