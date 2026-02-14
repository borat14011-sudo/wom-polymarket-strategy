#!/usr/bin/env python3
"""
Extract token info from CLOB response
"""

import json

# Read the response
with open('clob_response_bytes.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*60)
print("EXTRACTING TOKEN INFO")
print("="*60)

# Get first few markets
markets = data.get('data', [])[:5]

for i, market in enumerate(markets):
    print(f"\nMarket {i+1}:")
    print(f"  Condition ID: {market.get('condition_id')}")
    print(f"  Question ID: {market.get('question_id')}")
    print(f"  Active: {market.get('active')}")
    print(f"  Accepting orders: {market.get('accepting_orders')}")
    
    # Check for tokens
    if 'tokens' in market:
        tokens = market['tokens']
        print(f"  Tokens: {len(tokens)}")
        
        for j, token in enumerate(tokens[:2]):  # First 2 tokens
            token_id = token.get('id')
            outcome = token.get('outcome')
            print(f"\n  Token {j+1}:")
            print(f"    ID: {token_id}")
            print(f"    Outcome: {outcome}")
            
            # Test this token ID
            import requests
            clob_base = "https://clob.polymarket.com"
            orderbook_url = f"{clob_base}/orderbook?token_id={token_id}"
            
            try:
                response = requests.get(orderbook_url, timeout=5)
                if response.status_code == 200:
                    orderbook = response.json()
                    bids = orderbook.get('bids', [])
                    asks = orderbook.get('asks', [])
                    
                    print(f"    ✅ Order book found!")
                    print(f"    Bids: {len(bids)}, Asks: {len(asks)}")
                    
                    if bids:
                        print(f"    Best bid: {bids[0].get('price')}")
                    if asks:
                        print(f"    Best ask: {asks[0].get('price')}")
                    
                    # Save this working token
                    token_info = {
                        "market_condition_id": market.get('condition_id'),
                        "token_id": token_id,
                        "outcome": outcome,
                        "best_bid": bids[0].get('price') if bids else None,
                        "best_ask": asks[0].get('price') if asks else None
                    }
                    
                    with open('working_token_found.json', 'w') as f:
                        json.dump(token_info, f, indent=2)
                    print(f"\n    Saved to: working_token_found.json")
                    
                    # Stop after first success
                    print("\n" + "="*60)
                    print("FOUND WORKING TOKEN ID!")
                    print("="*60)
                    print(f"Token ID: {token_id}")
                    print(f"Outcome: {outcome}")
                    print("="*60)
                    
                    exit(0)  # Exit after finding working token
                    
                else:
                    print(f"    ❌ Order book error: {response.status_code}")
                    
            except Exception as e:
                print(f"    Error: {e}")
    
    print("-"*40)

print("\n" + "="*60)
print("NO WORKING TOKEN FOUND IN FIRST 5 MARKETS")
print("="*60)