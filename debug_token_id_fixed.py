#!/usr/bin/env python3
"""
Debug token_id issue - fixed
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('polymarket_bot/.env')

# Get a market
gamma_url = "https://gamma-api.polymarket.com/markets?limit=3&closed=false"
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
        
        # Outcomes are strings like "YES", "NO", etc.
        for j, outcome_name in enumerate(outcomes):
            # Token ID formula: condition_id + outcome_index (01, 02, etc.)
            outcome_index = str(j + 1).zfill(2)
            token_id = condition_id + outcome_index
            
            print(f"  Outcome {j+1}: {outcome_name}")
            print(f"    Index: {outcome_index}")
            print(f"    Token ID: {token_id}")
            
            # Check order book
            clob_url = f"https://clob.polymarket.com/orderbook?token_id={token_id}"
            clob_response = requests.get(clob_url, timeout=10)
            
            if clob_response.status_code == 200:
                orderbook = clob_response.json()
                bids = orderbook.get('bids', [])
                asks = orderbook.get('asks', [])
                
                if bids or asks:
                    print(f"    Orderbook: {len(bids)} bids, {len(asks)} asks")
                    if bids:
                        print(f"    Best bid: {bids[0].get('price')}")
                    if asks:
                        print(f"    Best ask: {asks[0].get('price')}")
                else:
                    print(f"    No orders")
            else:
                print(f"    Orderbook error: {clob_response.status_code}")
        
        print("-"*40)
        
    # Save market data
    with open('market_debug_fixed.json', 'w') as f:
        json.dump(markets, f, indent=2)
    print(f"\nSaved to: market_debug_fixed.json")
    
else:
    print(f"ERROR: Gamma API failed: {response.status_code}")