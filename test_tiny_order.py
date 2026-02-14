#!/usr/bin/env python3
"""
Test placing a tiny order using derived credentials
"""
import sys
import requests
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import OrderArgs, BalanceAllowanceParams, AssetType
from py_clob_client.order_builder.constants import BUY, SELL

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("Testing Tiny Order Placement")
print("="*60)

# Wallet
account = Account.from_key(PRIVATE_KEY)
wallet_address = account.address
print(f"Wallet: {wallet_address}")

# Initialize L1 client
client_l1 = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=POLYGON,
    key=account.key,
    signature_type=0,
    funder=wallet_address
)

# Derive API credentials
print("\nDeriving API credentials...")
creds = client_l1.create_or_derive_api_creds()
print(f"API Key: {creds.api_key[:10]}...")

# Initialize L2 client with creds
client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=POLYGON,
    key=account.key,
    creds=creds,
    signature_type=0,
    funder=wallet_address
)
print("L2 client ready.")

# Get USDC balance
print("\nChecking USDC balance...")
try:
    params = BalanceAllowanceParams(
        asset_type=AssetType.COLLATERAL,
        signature_type=0
    )
    balance = client.get_balance_allowance(params)
    print(f"Balance: {balance}")
except Exception as e:
    print(f"Could not get balance: {e}")
    # continue anyway

# Pick a market with good liquidity
print("\nFetching a liquid market...")
try:
    resp = requests.get("https://gamma-api.polymarket.com/events?closed=false&limit=5", timeout=10)
    if resp.status_code == 200:
        events = resp.json()
        market = None
        for ev in events:
            for mkt in ev.get('markets', []):
                if mkt.get('volume24h', 0) > 10000:  # decent volume
                    market = mkt
                    break
            if market:
                break
        if market:
            condition_id = market['conditionId']
            print(f"Selected market: {market['question'][:80]}...")
            print(f"Condition ID: {condition_id}")
            # Get token IDs - they are in clobTokenIds field
            clob_token_ids = market.get('clobTokenIds')
            if clob_token_ids:
                token_ids = clob_token_ids
                print(f"Token IDs: {token_ids}")
                # For binary markets, first token is YES, second is NO
                yes_token = token_ids[0]
                no_token = token_ids[1]
                print(f"YES token: {yes_token[:20]}...")
                print(f"NO token: {no_token[:20]}...")
            else:
                # Fallback: derive token IDs manually
                yes_token = condition_id + "0100000000000000000000000000000000000000000000000000000000000000"
                no_token = condition_id + "0000000000000000000000000000000000000000000000000000000000000000"
                print(f"Derived YES token: {yes_token[:20]}...")
        else:
            print("No suitable market found.")
            sys.exit(1)
    else:
        print(f"Gamma API error: {resp.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"Market fetch error: {e}")
    sys.exit(1)

# Prepare tiny order: BUY YES at 1 cent (1% probability), size 1 share = $0.01 cost
print("\nPreparing tiny order...")
token_id = yes_token
price = 0.01  # 1 cent
size = 1.0    # 1 share
side = BUY
fee_rate_bps = 0  # no fee

order_args = OrderArgs(
    token_id=token_id,
    price=price,
    size=size,
    side=side,
    fee_rate_bps=fee_rate_bps
)

print(f"Order args: token={token_id[:20]}..., price={price}, size={size}, side={side}")

# Create and post order
print("\nAttempting to create and post order...")
try:
    result = client.create_and_post_order(order_args)
    print(f"SUCCESS! Order result: {result}")
except Exception as e:
    print(f"Order failed: {e}")
    import traceback
    traceback.print_exc()
    # Try just creating order and posting separately
    print("\nTrying create_order then post_order...")
    try:
        order = client.create_order(order_args)
        print(f"Created order: {order}")
        post_result = client.post_order(order)
        print(f"Posted order result: {post_result}")
    except Exception as e2:
        print(f"Also failed: {e2}")

print("\nDone.")