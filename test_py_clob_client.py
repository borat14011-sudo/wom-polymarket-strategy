#!/usr/bin/env python3
"""
Test py_clob_client authentication and balance
"""
import sys
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("Testing py_clob_client")
print("="*60)

# Initialize wallet
account = Account.from_key(PRIVATE_KEY)
print(f"Wallet address: {account.address}")

# Initialize CLOB client
client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=POLYGON,
    key=account.key,
    signature_type=0,
    funder=account.address
)

print("Client initialized.")

# Test public endpoint
print("\n1. Testing public endpoint (server time)...")
try:
    # There's no direct server time method, but we can try get_markets
    markets = client.get_markets()
    print(f"   Success: got {len(markets.get('data', []))} markets")
except Exception as e:
    print(f"   Error: {e}")

# Test authenticated endpoint (balance)
print("\n2. Testing authenticated endpoint (balance)...")
try:
    # Try to get balances
    balances = client.get_balances()
    print(f"   Success: {balances}")
except Exception as e:
    print(f"   Error: {e}")

# Test orders
print("\n3. Testing orders endpoint...")
try:
    orders = client.get_orders()
    print(f"   Success: {len(orders)} orders")
except Exception as e:
    print(f"   Error: {e}")

# Test token allowance
print("\n4. Testing token allowance...")
try:
    # Use a sample token ID (need a valid token)
    # Let's get a token ID from a market
    import requests
    resp = requests.get("https://gamma-api.polymarket.com/events?closed=false&limit=1", timeout=10)
    if resp.status_code == 200:
        events = resp.json()
        if events and events[0].get('markets'):
            market = events[0]['markets'][0]
            condition_id = market['conditionId']
            token_id = condition_id + "0100000000000000000000000000000000000000000000000000000000000000"
            print(f"   Using token: {token_id[:20]}...")
            allowance = client.get_balance_allowance(asset_type="COLLATERAL", token_id=token_id)
            print(f"   Allowance: {allowance}")
except Exception as e:
    print(f"   Error: {e}")

print("\nDone.")