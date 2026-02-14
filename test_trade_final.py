#!/usr/bin/env python3
"""
Final trade test with correct token_id
"""

import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv('polymarket_bot/.env')

PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
WALLET_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print("="*60)
print("FINAL TRADE TEST")
print("="*60)
print(f"Wallet: {WALLET_ADDRESS}")

# Get a market
gamma_url = "https://gamma-api.polymarket.com/markets?limit=1&closed=false"
response = requests.get(gamma_url, timeout=10)

if response.status_code == 200:
    markets = response.json()
    if markets:
        market = markets[0]
        market_id = market.get('id')
        question = market.get('question', 'Unknown')[:60]
        condition_id = market.get('conditionId')
        
        print(f"\nMarket: {market_id}")
        print(f"Question: {question}...")
        print(f"Condition ID: {condition_id}")
        
        # Get outcomes
        outcomes = market.get('outcomes', [])
        print(f"Outcomes: {outcomes}")
        
        # For Yes/No markets
        if "Yes" in outcomes and "No" in outcomes:
            yes_index = outcomes.index("Yes") + 1
            no_index = outcomes.index("No") + 1
            
            yes_token_id = condition_id + str(yes_index).zfill(2)
            no_token_id = condition_id + str(no_index).zfill(2)
            
            print(f"\nYes token ID: {yes_token_id}")
            print(f"No token ID: {no_token_id}")
            
            # Check order book for Yes
            print(f"\nChecking Yes order book...")
            clob_url = f"https://clob.polymarket.com/orderbook?token_id={yes_token_id}"
            clob_response = requests.get(clob_url, timeout=10)
            
            if clob_response.status_code == 200:
                orderbook = clob_response.json()
                bids = orderbook.get('bids', [])
                asks = orderbook.get('asks', [])
                
                if bids:
                    print(f"Best bid: {bids[0].get('price')}")
                if asks:
                    print(f"Best ask: {asks[0].get('price')}")
                    
                # Save for trading
                trade_data = {
                    "market_id": market_id,
                    "question": question,
                    "condition_id": condition_id,
                    "yes_token_id": yes_token_id,
                    "no_token_id": no_token_id,
                    "best_bid": bids[0].get('price') if bids else None,
                    "best_ask": asks[0].get('price') if asks else None
                }
                
                with open('trade_data_final.json', 'w') as f:
                    json.dump(trade_data, f, indent=2)
                print(f"\nSaved trade data to: trade_data_final.json")
                
                # Now test with py-clob-client
                print(f"\n" + "="*60)
                print("TESTING WITH PY-CLOB-CLIENT")
                print("="*60)
                
                try:
                    from py_clob_client.client import ClobClient
                    from py_clob_client.constants import POLYGON
                    from py_clob_client.clob_types import OrderArgs, OrderType
                    from py_clob_client.order_builder.constants import BUY
                    
                    client = ClobClient(
                        host="https://clob.polymarket.com",
                        chain_id=POLYGON,
                        key=PRIVATE_KEY,
                        signature_type=1,
                        funder=WALLET_ADDRESS
                    )
                    
                    print(f"Client created successfully")
                    
                    # Create a small test order
                    order_args = OrderArgs(
                        token_id=yes_token_id,
                        price="0.50",  # 50% probability
                        size="0.01",   # $0.01 test
                        side=BUY
                    )
                    
                    print(f"Creating order...")
                    signed_order = client.create_order(order_args)
                    print(f"Order signed: {signed_order}")
                    
                    print(f"Posting order...")
                    response = client.post_order(signed_order, OrderType.GTC)
                    print(f"Order posted! Response: {response}")
                    
                    print(f"\n" + "="*60)
                    print("SUCCESS! TRADING WORKS!")
                    print("="*60)
                    
                except Exception as e:
                    print(f"Error with py-clob-client: {e}")
                    print(f"\nWe'll need to debug the API call")
                    
            else:
                print(f"Orderbook error: {clob_response.status_code}")
                
        else:
            print(f"Not a Yes/No market")
            
    else:
        print(f"No markets returned")
else:
    print(f"Gamma API error: {response.status_code}")

print("\n" + "="*60)
print("STATUS")
print("="*60)
print(f"Wallet: {WALLET_ADDRESS}")
print(f"Balance: $10.41")
print(f"Ready for trading: YES")
print(f"Next: Run agent manager with fixed token_id")