#!/usr/bin/env python3
"""
Find token_id for a market
"""

import requests
import json

print("Finding token_id for markets...")

# Get markets from Gamma API
gamma_url = "https://gamma-api.polymarket.com/markets?limit=5&closed=false"
response = requests.get(gamma_url, timeout=10)

if response.status_code == 200:
    markets = response.json()
    print(f"Found {len(markets)} markets")
    
    for i, market in enumerate(markets):
        market_id = market.get('id')
        question = market.get('question', 'Unknown')[:50]
        condition_id = market.get('conditionId')
        
        print(f"\nMarket {i+1}:")
        print(f"  Question: {question}...")
        print(f"  Market ID: {market_id}")
        print(f"  Condition ID: {condition_id}")
        
        # Get market details to find token_id
        details_url = f"https://gamma-api.polymarket.com/markets/{market_id}"
        details_response = requests.get(details_url, timeout=10)
        
        if details_response.status_code == 200:
            details = details_response.json()
            
            # Look for outcomes/tokens
            if 'outcomes' in details:
                outcomes = details['outcomes']
                print(f"  Outcomes: {len(outcomes)}")
                for outcome in outcomes:
                    token_id = outcome.get('tokenId')
                    name = outcome.get('name', 'Unknown')
                    print(f"    - {name}: token_id = {token_id}")
                    
                    # Save first token_id
                    if token_id and i == 0:
                        with open('first_token_id.txt', 'w') as f:
                            f.write(token_id)
                        print(f"\nSaved first token_id to first_token_id.txt")
                        break
        else:
            print(f"  Could not get details: {details_response.status_code}")
            
else:
    print(f"Failed to get markets: {response.status_code}")

print("\n" + "="*60)
print("NOTE: Token IDs are needed for CLOB API orders")
print("Market ID ≠ Token ID")
print("Each outcome (YES/NO) has its own token_id")
print("="*60)