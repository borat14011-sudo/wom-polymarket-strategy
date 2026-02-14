import os
import json
from dotenv import load_dotenv
load_dotenv('polymarket_bot/.env')

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY
import requests

HOST = "https://clob.polymarket.com"
PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
FUNDER_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print("Creating client...")
client = ClobClient(HOST, key=PRIVATE_KEY, chain_id=137, signature_type=1, funder=FUNDER_ADDRESS)
client.set_api_creds(client.create_or_derive_api_creds())
print("Client ready!")

# Get token
r = requests.get("https://gamma-api.polymarket.com/markets?limit=1&closed=false", timeout=10)
token_id = json.loads(r.json()[0].get('clobTokenIds', '[]'))[0]
print(f"Token: {token_id[:30]}...")

# Place order
print("Placing order...")
try:
    order = client.create_order(OrderArgs(price=0.01, size=1.0, side=BUY, token_id=token_id))
    result = client.post_order(order)
    print(f"SUCCESS! Result: {result}")
except Exception as e:
    print(f"FAILED: {e}")
