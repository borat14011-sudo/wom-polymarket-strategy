#!/usr/bin/env python3
"""
Minimal Polymarket API test
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.constants import POLYGON
import requests

# Wallet
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
WALLET_ADDRESS = "0xb354e25623617a24164639F63D8b731250AC92d8"

def main():
    print("Minimal Polymarket API Test")
    print("="*50)
    
    # 1. Initialize wallet
    account = Account.from_key(PRIVATE_KEY)
    print(f"Wallet: {account.address}")
    
    # 2. Initialize CLOB client
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=POLYGON,
        key=account.key,
        signature_type=0,
        funder=account.address
    )
    
    # 3. Get API credentials
    creds = client.create_or_derive_api_creds()
    print(f"API Key: {creds.api_key}")
    
    # 4. Get a market to test with
    gamma_url = "https://gamma-api.polymarket.com/events?closed=false&limit=5"
    response = requests.get(gamma_url, timeout=10)
    
    if response.status_code != 200:
        print("Failed to get markets")
        return
    
    events = response.json()
    if not events:
        print("No events found")
        return
    
    # Find first market with conditionId
    test_market = None
    test_condition_id = None
    
    for event in events:
        markets = event.get('markets', [])
        for market in markets:
            condition_id = market.get('conditionId')
            if condition_id:
                test_market = market
                test_condition_id = condition_id
                break
        if test_market:
            break
    
    if not test_market:
        print("No market with conditionId found")
        return
    
    print(f"\nTest Market:")
    print(f"  ID: {test_market['id']}")
    print(f"  Question: {test_market['question'][:60]}...")
    print(f"  Condition ID: {test_condition_id}")
    
    # 5. Try to get order book using conditionId
    try:
        print(f"\nTrying to get order book for conditionId: {test_condition_id}")
        order_book = client.get_order_book(test_condition_id)
        print(f"Order book retrieved!")
        print(f"  Bids: {len(order_book.get('bids', []))}")
        print(f"  Asks: {len(order_book.get('asks', []))}")
    except Exception as e:
        print(f"Failed to get order book: {e}")
        
        # Maybe we need the token ID instead
        # Let me check if there's a tokens endpoint
        print("\nTrying tokens endpoint...")
        tokens_url = f"https://gamma-api.polymarket.com/markets/{test_market['id']}/tokens"
        tokens_resp = requests.get(tokens_url, timeout=5)
        
        if tokens_resp.status_code == 200:
            tokens = tokens_resp.json()
            print(f"Tokens found: {len(tokens)}")
            for token in tokens:
                print(f"  {token.get('outcome')}: ID={token.get('id')}")
                
            if tokens and len(tokens) >= 2:
                # Try with first token ID
                token_id = tokens[0]['id']
                print(f"\nTrying order book with token ID: {token_id}")
                try:
                    order_book = client.get_order_book(token_id)
                    print(f"Success with token ID!")
                except Exception as e2:
                    print(f"Failed with token ID too: {e2}")
        else:
            print(f"Tokens endpoint failed: {tokens_resp.status_code}")
    
    print("\n" + "="*50)
    print("Test complete")

if __name__ == "__main__":
    main()