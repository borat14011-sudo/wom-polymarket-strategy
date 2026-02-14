#!/usr/bin/env python3
"""
Simple trade test with correct token_id
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
print("SIMPLE TRADE TEST")
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
        
        # For YES/NO markets, outcomes are ["YES", "NO"]
        if "YES" in outcomes and "NO" in outcomes:
            yes_index = outcomes.index("YES") + 1
            no_index = outcomes.index("NO") + 1
            
            yes_token_id = condition_id + str(yes_index).zfill(2)
            no_token_id = condition_id + str(no_index).zfill(2)
            
            print(f"\nYES token ID: {yes_token_id}")
            print(f"NO token ID: {no_token_id}")
            
            # Check order book for YES
            print(f"\nChecking YES order book...")
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
                
                with open('trade_data.json', 'w') as f:
                    json.dump(trade_data, f, indent=2)
                print(f"\nSaved trade data to: trade_data.json")
                
            else:
                print(f"Orderbook error: {clob_response.status_code}")
                
        else:
            print(f"Not a YES/NO market")
            
    else:
        print(f"No markets returned")
else:
    print(f"Gamma API error: {response.status_code}")

print("\n" + "="*60)
print("READY FOR TRADING")
print("="*60)