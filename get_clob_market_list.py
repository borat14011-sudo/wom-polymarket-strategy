#!/usr/bin/env python3
"""
Get list of markets available on CLOB
"""

import requests
import json

print("Fetching CLOB markets...")

try:
    url = "https://clob.polymarket.com/markets"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        markets = response.json()
        print(f"Total CLOB markets: {len(markets)}")
        print("\n" + "="*60)
        
        for i, market in enumerate(markets):
            question = market.get('question', 'Unknown')
            condition_id = market.get('conditionId', '')
            active = market.get('active', False)
            closed = market.get('closed', False)
            
            print(f"{i+1}. {question[:80]}...")
            print(f"   Condition ID: {condition_id}")
            print(f"   Active: {active}, Closed: {closed}")
            
            # Check if we can get token IDs
            if 'outcomes' in market:
                for j, outcome in enumerate(market['outcomes']):
                    if 'tokenId' in outcome:
                        print(f"   Outcome {j} token: {outcome['tokenId'][:20]}...")
            
            print()
            
    else:
        print(f"Error: HTTP {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")