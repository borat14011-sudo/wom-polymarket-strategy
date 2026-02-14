import os
import json
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY
import requests
from eth_account import Account

# NEW private key from Wom
NEW_PRIVATE_KEY = "0x6000219032e3356c3ea88fee049fd87dd3e964ea6492efa1fe5cecbd8f0923a9"

# Derive wallet address from private key
account = Account.from_key(NEW_PRIVATE_KEY)
wallet_address = account.address
print(f"Wallet address: {wallet_address}")

HOST = "https://clob.polymarket.com"

print("\n1. Creating client with NEW key...")
# Try with signature_type=0 (EOA) first since this might be a fresh wallet
client = ClobClient(
    HOST, 
    key=NEW_PRIVATE_KEY, 
    chain_id=137, 
    signature_type=0,  # EOA - direct wallet
    funder=wallet_address
)

print("2. Deriving API credentials...")
try:
    client.set_api_creds(client.create_or_derive_api_creds())
    print("   Credentials derived!")
except Exception as e:
    print(f"   Error: {e}")
    # Try POLY_PROXY
    print("\n   Trying POLY_PROXY instead...")
    client = ClobClient(
        HOST, 
        key=NEW_PRIVATE_KEY, 
        chain_id=137, 
        signature_type=1,  # POLY_PROXY
        funder=wallet_address
    )
    client.set_api_creds(client.create_or_derive_api_creds())
    print("   Credentials derived with POLY_PROXY!")

print("\n3. Testing server...")
try:
    print(f"   Server time: {client.get_server_time()}")
except Exception as e:
    print(f"   Error: {e}")

print("\n4. Getting market...")
r = requests.get("https://gamma-api.polymarket.com/markets?limit=1&closed=false", timeout=10)
market = r.json()[0]
token_id = json.loads(market.get('clobTokenIds', '[]'))[0]
print(f"   Market: {market.get('question', '')[:40]}...")
print(f"   Token: {token_id[:30]}...")

print("\n5. Placing $0.01 test order...")
try:
    order = client.create_order(OrderArgs(price=0.01, size=1.0, side=BUY, token_id=token_id))
    result = client.post_order(order)
    print(f"\n*** SUCCESS! ***")
    print(f"Result: {result}")
except Exception as e:
    print(f"\nFailed: {e}")

print("\nDone!")
