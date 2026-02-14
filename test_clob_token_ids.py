#!/usr/bin/env python3
"""
Test CLOB token IDs
"""

import requests
import json
import ast

# Read market data
with open('market_full.json', 'r') as f:
    market = json.load(f)

print("="*60)
print("TESTING CLOB TOKEN IDs")
print("="*60)

# Parse clobTokenIds (it's a string representation of a list)
clob_token_ids_str = market.get('clobTokenIds', '[]')
clob_token_ids = ast.literal_eval(clob_token_ids_str)

print(f"Market: {market.get('question')[:50]}...")
print(f"Outcomes: {market.get('outcomes')}")
print(f"CLOB Token IDs: {clob_token_ids}")

# Test each token ID
for i, token_id in enumerate(clob_token_ids):
    print(f"\nTesting token ID {i+1}: {token_id}")
    
    clob_url = f"https://clob.polymarket.com/orderbook?token_id={token_id}"
    clob_response = requests.get(clob_url, timeout=10)
    
    if clob_response.status_code == 200:
        orderbook = clob_response.json()
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])
        
        print(f"  SUCCESS! Order book found")
        print(f"  Bids: {len(bids)}, Asks: {len(asks)}")
        
        if bids:
            best_bid = bids[0]
            print(f"  Best bid: {best_bid.get('price')} @ {best_bid.get('size')}")
        
        if asks:
            best_ask = asks[0]
            print(f"  Best ask: {best_ask.get('price')} @ {best_ask.get('size')}")
        
        # Map to outcome
        outcomes_str = market.get('outcomes', '[]')
        outcomes = ast.literal_eval(outcomes_str)
        
        if i < len(outcomes):
            print(f"  This is the '{outcomes[i]}' outcome")
            
            # Save mapping
            mapping = {
                "market_id": market.get('id'),
                "question": market.get('question'),
                "outcome": outcomes[i],
                "token_id": token_id,
                "best_bid": bids[0].get('price') if bids else None,
                "best_ask": asks[0].get('price') if asks else None
            }
            
            filename = f"token_mapping_{market.get('id')}_{outcomes[i]}.json"
            with open(filename, 'w') as f:
                json.dump(mapping, f, indent=2)
            print(f"  Saved to: {filename}")
            
    else:
        print(f"  Error: {clob_response.status_code}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Token IDs are DECIMAL numbers, not hex!")
print(f"Format: token_id = decimal number from clobTokenIds")
print(f"Example: 101676997363687199724245607342877036148401850938023978421879460310389391082353")
print("="*60)