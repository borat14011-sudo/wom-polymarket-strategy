#!/usr/bin/env python3
"""
Proper token_id debugging
"""

import requests
import json

# Get market details
market_id = "517310"
url = f"https://gamma-api.polymarket.com/markets/{market_id}"
response = requests.get(url, timeout=10)

if response.status_code == 200:
    market = response.json()
    
    print("="*60)
    print("MARKET DETAILS")
    print("="*60)
    
    print(f"ID: {market.get('id')}")
    print(f"Question: {market.get('question')}")
    print(f"Condition ID: {market.get('conditionId')}")
    
    # Check all fields
    print(f"\nAll keys:")
    for key in market.keys():
        print(f"  {key}")
    
    # Check outcomes structure
    outcomes = market.get('outcomes', [])
    print(f"\nOutcomes type: {type(outcomes)}")
    print(f"Outcomes: {outcomes}")
    
    # Check if there's a different field for token IDs
    if 'tokens' in market:
        print(f"\nTokens: {market['tokens']}")
    
    # Try to find token IDs in the market data
    print(f"\nSearching for token IDs...")
    import re
    
    market_str = json.dumps(market)
    token_pattern = r'0x[a-fA-F0-9]{64}'
    all_hex = re.findall(token_pattern, market_str)
    
    print(f"Found {len(all_hex)} hex strings:")
    for i, hex_str in enumerate(all_hex[:10]):
        print(f"  {i+1}: {hex_str}")
    
    # Save full market data
    with open('market_full.json', 'w') as f:
        json.dump(market, f, indent=2)
    print(f"\nFull market data saved to: market_full.json")
    
    # Try the CLOB API with different endpoints
    print(f"\n" + "="*60)
    print("TESTING CLOB ENDPOINTS")
    print("="*60)
    
    # Try to get order book for condition ID
    condition_id = market.get('conditionId')
    if condition_id:
        # Try different token_id formats
        test_formats = [
            condition_id + '01',
            condition_id + '02',
            condition_id + '03',
            condition_id + '10',
            condition_id + '20',
            condition_id + '30',
        ]
        
        for token_id in test_formats:
            clob_url = f"https://clob.polymarket.com/orderbook?token_id={token_id}"
            clob_response = requests.get(clob_url, timeout=5)
            
            if clob_response.status_code == 200:
                orderbook = clob_response.json()
                bids = orderbook.get('bids', [])
                asks = orderbook.get('asks', [])
                
                print(f"\nToken ID {token_id[-2:]}: SUCCESS!")
                print(f"  Bids: {len(bids)}, Asks: {len(asks)}")
                if bids:
                    print(f"  Best bid: {bids[0].get('price')}")
                if asks:
                    print(f"  Best ask: {asks[0].get('price')}")
            else:
                print(f"Token ID {token_id[-2:]}: {clob_response.status_code}")
    
else:
    print(f"Error: {response.status_code}")