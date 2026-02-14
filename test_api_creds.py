#!/usr/bin/env python3
"""
Test obtaining API credentials via py_clob_client
"""
import sys
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("Testing API credential derivation")
print("="*60)

account = Account.from_key(PRIVATE_KEY)
print(f"Wallet address: {account.address}")

# Initialize client with signer only (L1)
client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=POLYGON,
    key=account.key,
    signature_type=0,
    funder=account.address
)

print("Client initialized (L1).")

# Create or derive API credentials
print("\nDeriving API credentials...")
try:
    creds = client.create_or_derive_api_creds()
    print(f"Credentials: {creds}")
    # creds should have api_key, secret, passphrase
    api_key = creds.api_key
    secret = creds.secret
    passphrase = creds.passphrase
    print(f"API Key: {api_key}")
    print(f"Secret: {secret[:10]}...")
    print(f"Passphrase: {passphrase[:10]}...")
except Exception as e:
    print(f"Error deriving creds: {e}")
    sys.exit(1)

# Now reinitialize client with full credentials (L2)
print("\nRe-initializing client with API credentials (L2)...")
try:
    client_l2 = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=POLYGON,
        key=account.key,
        api_creds=creds,
        signature_type=0,
        funder=account.address
    )
    print("L2 client initialized.")
    
    # Test authenticated endpoint
    print("\nTesting balance allowance...")
    # Need a token ID, but we can try with asset_type="COLLATERAL"
    # According to py_clob_client source, get_balance_allowance expects token_id param
    # Let's get a token ID from a market
    import requests
    resp = requests.get("https://gamma-api.polymarket.com/events?closed=false&limit=1", timeout=10)
    if resp.status_code == 200:
        events = resp.json()
        if events and events[0].get('markets'):
            market = events[0]['markets'][0]
            condition_id = market['conditionId']
            token_id = condition_id + "0100000000000000000000000000000000000000000000000000000000000000"
            print(f"Using token: {token_id[:20]}...")
            allowance = client_l2.get_balance_allowance(token_id=token_id)
            print(f"Balance allowance: {allowance}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\nDone.")