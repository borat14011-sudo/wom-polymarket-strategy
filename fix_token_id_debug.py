#!/usr/bin/env python3
"""
Fix token_id debug - parse outcomes correctly
"""

import requests
import json

print("="*60)
print("FIXED TOKEN_ID DEBUG")
print("="*60)

# Get market 517310
market_url = "https://gamma-api.polymarket.com/markets/517310"
response = requests.get(market_url, timeout=10)

if response.status_code == 200:
    market = response.json()
    
    market_id = market.get('id')
    question = market.get('question', 'Unknown')
    condition_id = market.get('conditionId')
    
    print(f"Market: {question}")
    print(f"ID: {market_id}")
    print(f"Condition ID: {condition_id}")
    
    # Parse outcomes correctly
    outcomes_str = market.get('outcomes', '[]')
    try:
        outcomes = json.loads(outcomes_str)
        print(f"Outcomes (parsed): {outcomes}")
        print(f"Outcomes type: {type(outcomes)}")
    except:
        print(f"Failed to parse outcomes: {outcomes_str}")
        outcomes = []
    
    # Check clobTokenIds
    clob_token_ids_str = market.get('clobTokenIds', '[]')
    try:
        clob_token_ids = json.loads(clob_token_ids_str)
        print(f"\nCLOB Token IDs: {clob_token_ids}")
        print(f"Count: {len(clob_token_ids)}")
        
        if clob_token_ids:
            # Test each token ID
            for i, token_id in enumerate(clob_token_ids):
                print(f"\nToken {i+1}: {token_id}")
                print(f"  Type: {type(token_id)}")
                print(f"  Length: {len(str(token_id))}")
                
                # Try decimal
                orderbook_url = f"https://clob.polymarket.com/orderbook?token_id={token_id}"
                ob_response = requests.get(orderbook_url, timeout=5)
                print(f"  Decimal orderbook: {ob_response.status_code}")
                
                # Try hex
                try:
                    token_hex = hex(int(token_id))
                    orderbook_url_hex = f"https://clob.polymarket.com/orderbook?token_id={token_hex}"
                    ob_response_hex = requests.get(orderbook_url_hex, timeout=5)
                    print(f"  Hex orderbook: {ob_response_hex.status_code}")
                except:
                    print(f"  Hex conversion failed")
                
                # Try with 0x prefix
                orderbook_url_0x = f"https://clob.polymarket.com/orderbook?token_id=0x{token_id}"
                ob_response_0x = requests.get(orderbook_url_0x, timeout=5)
                print(f"  0x+decimal orderbook: {ob_response_0x.status_code}")
                
    except Exception as e:
        print(f"Failed to parse clobTokenIds: {e}")
        print(f"Raw: {clob_token_ids_str}")
    
    # Check other fields
    print(f"\nOther fields:")
    print(f"enableOrderBook: {market.get('enableOrderBook')}")
    print(f"volume24h: {market.get('volume24h')}")
    print(f"liquidity: {market.get('liquidity')}")
    
else:
    print(f"API error: {response.status_code}")

print("\n" + "="*60)
print("KEY INSIGHT")
print("="*60)
print("The token_id might be correct but the market doesn't have")
print("an order book yet (new market). We might need to:")
print("1. Wait for order book to be created")
print("2. Use AMM trading instead")
print("3. Trade on website (always works)")
print("="*60)