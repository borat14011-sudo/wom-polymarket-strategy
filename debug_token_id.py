#!/usr/bin/env python3
"""
Debug token_id issue
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('polymarket_bot/.env')

# Get a market
gamma_url = "https://gamma-api.polymarket.com/markets?limit=5&closed=false"
response = requests.get(gamma_url, timeout=10)

if response.status_code == 200:
    markets = response.json()
    
    print("="*60)
    print("DEBUGGING TOKEN_ID FORMAT")
    print("="*60)
    
    for i, market in enumerate(markets):
        market_id = market.get('id')
        question = market.get('question', 'Unknown')[:60]
        condition_id = market.get('conditionId')
        
        print(f"\nMarket {i+1}: {market_id}")
        print(f"Question: {question}...")
        print(f"Condition ID: {condition_id}")
        
        # Check outcomes
        outcomes = market.get('outcomes', [])
        print(f"Outcomes: {len(outcomes)}")
        
        for j, outcome in enumerate(outcomes):
            # Handle both string and dict outcomes
            if isinstance(outcome, dict):
                outcome_name = outcome.get('name', 'Unknown')
                outcome_id = outcome.get('id')
                token_id = outcome.get('tokenId')
            else:
                outcome_name = str(outcome)
                outcome_id = str(j)
                token_id = None
            
            print(f"  Outcome {j+1}: {outcome_name}")
            print(f"    Outcome ID: {outcome_id}")
            print(f"    Token ID: {token_id}")
            
            # Try to derive token_id
            if condition_id and outcome_id and token_id:
                derived_token_id = condition_id + outcome_id.zfill(2)
                print(f"    Derived: {derived_token_id}")
                print(f"    Match: {'YES' if derived_token_id == token_id else 'NO'}")
        
        # Check if market has order book
        print(f"\n  Checking order book...")
        clob_url = f"https://clob.polymarket.com/orderbook?token_id={token_id}"
        clob_response = requests.get(clob_url, timeout=10)
        
        if clob_response.status_code == 200:
            orderbook = clob_response.json()
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            print(f"    Bids: {len(bids)}, Asks: {len(asks)}")
            
            if bids:
                print(f"    Best bid: {bids[0].get('price')}")
            if asks:
                print(f"    Best ask: {asks[0].get('price')}")
        else:
            print(f"    Orderbook error: {clob_response.status_code}")
        
        print("-"*40)
        
    # Save market data
    with open('market_debug.json', 'w') as f:
        json.dump(markets, f, indent=2)
    print(f"\nSaved to: market_debug.json")
    
else:
    print(f"ERROR: Gamma API failed: {response.status_code}")