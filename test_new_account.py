import os
import json
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY
import requests

# NEW ACCOUNT CREDENTIALS
PRIVATE_KEY = "0x6000219032e3356c3ea88fee049fd87dd3e964ea6492efa1fe5cecbd8f0923a9"
FUNDER_ADDRESS = "0x165B25471cB352954fb43229A6D9e07f8dF61BAe"

HOST = "https://clob.polymarket.com"

print("="*60)
print("TESTING NEW POLYMARKET ACCOUNT")
print("="*60)
print(f"Funder: {FUNDER_ADDRESS}")

print("\n1. Creating client (POLY_PROXY)...")
client = ClobClient(
    HOST, 
    key=PRIVATE_KEY, 
    chain_id=137, 
    signature_type=1,  # POLY_PROXY for Magic Link
    funder=FUNDER_ADDRESS
)

print("2. Deriving API credentials...")
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)
print(f"   API Key: {creds.api_key[:20]}...")

print("\n3. Testing connection...")
print(f"   Server time: {client.get_server_time()}")

print("\n4. Getting market...")
r = requests.get("https://gamma-api.polymarket.com/markets?limit=1&closed=false", timeout=10)
market = r.json()[0]
token_id = json.loads(market.get('clobTokenIds', '[]'))[0]
print(f"   Market: {market.get('question', '')[:50]}...")
print(f"   Token: {token_id[:30]}...")

print("\n5. Placing $0.01 test order...")
try:
    order = client.create_order(OrderArgs(price=0.01, size=1.0, side=BUY, token_id=token_id))
    print("   Order signed!")
    result = client.post_order(order)
    print(f"\n{'='*60}")
    print("SUCCESS! ORDER PLACED!")
    print(f"{'='*60}")
    print(f"Result: {result}")
except Exception as e:
    print(f"\nFailed: {e}")

print("\nDone!")
