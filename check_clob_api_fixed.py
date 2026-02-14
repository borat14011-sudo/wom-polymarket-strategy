#!/usr/bin/env python3
"""
Check CLOB API - fixed
"""

import requests
import json

clob_base = "https://clob.polymarket.com"

print("="*60)
print("CHECKING CLOB API")
print("="*60)

# Get markets
markets_url = f"{clob_base}/markets"
response = requests.get(markets_url, timeout=10)

if response.status_code == 200:
    markets = response.json()
    print(f"Response type: {type(markets)}")
    
    if isinstance(markets, dict):
        print(f"Dict keys: {list(markets.keys())}")
        
        # Check if there's a 'markets' key
        if 'markets' in markets:
            market_list = markets['markets']
            print(f"Found {len(market_list)} markets")
            
            if market_list:
                market = market_list[0]
                print(f"\nFirst market:")
                print(f"  ID: {market.get('id')}")
                print(f"  Question: {market.get('question', 'Unknown')[:50]}...")
                
                # Check for token IDs
                if 'tokens' in market:
                    tokens = market['tokens']
                    print(f"\nTokens found: {len(tokens)}")
                    
                    for i, token in enumerate(tokens[:2]):
                        token_id = token.get('id')
                        outcome = token.get('outcome')
                        print(f"\nToken {i+1}:")
                        print(f"  ID: {token_id}")
                        print(f"  Outcome: {outcome}")
                        
                        # Try order book
                        orderbook_url = f"{clob_base}/orderbook?token_id={token_id}"
                        ob_response = requests.get(orderbook_url, timeout=5)
                        
                        if ob_response.status_code == 200:
                            orderbook = ob_response.json()
                            bids = orderbook.get('bids', [])
                            asks = orderbook.get('asks', [])
                            print(f"  SUCCESS! Bids: {len(bids)}, Asks: {len(asks)}")
                            
                            if bids:
                                print(f"  Best bid: {bids[0].get('price')}")
                            if asks:
                                print(f"  Best ask: {asks[0].get('price')}")
                        else:
                            print(f"  Error: {ob_response.status_code}")
                
                # Save sample
                with open('clob_market_fixed.json', 'w') as f:
                    json.dump(market, f, indent=2)
                print(f"\nSample saved to: clob_market_fixed.json")
                
        else:
            print(f"No 'markets' key in response")
            print(f"Full response keys: {list(markets.keys())}")
            
    else:
        print(f"Unexpected response type: {type(markets)}")
        
else:
    print(f"Error: {response.status_code}")

print("\n" + "="*60)
print("TRYING TOKEN ID FORMATS")
print("="*60)

# Try different token ID formats for our market
market_id = "517310"

# Get market from Gamma API
gamma_url = f"https://gamma-api.polymarket.com/markets/{market_id}"
response = requests.get(gamma_url, timeout=10)

if response.status_code == 200:
    market = response.json()
    
    # Get clobTokenIds
    import ast
    clob_token_ids_str = market.get('clobTokenIds', '[]')
    clob_token_ids = ast.literal_eval(clob_token_ids_str)
    
    print(f"\nMarket: {market.get('question')[:50]}...")
    print(f"CLOB Token IDs: {clob_token_ids}")
    
    # Try each token ID with different formats
    for i, token_decimal in enumerate(clob_token_ids):
        print(f"\nToken {i+1} (decimal): {token_decimal}")
        
        # Format 1: Decimal as string
        orderbook_url = f"{clob_base}/orderbook?token_id={token_decimal}"
        response = requests.get(orderbook_url, timeout=5)
        print(f"  Decimal string: {response.status_code}")
        
        # Format 2: Hex with 0x
        token_hex = hex(int(token_decimal))
        orderbook_url = f"{clob_base}/orderbook?token_id={token_hex}"
        response = requests.get(orderbook_url, timeout=5)
        print(f"  Hex with 0x: {response.status_code}")
        
        # Format 3: Hex without 0x
        token_hex_no_prefix = token_hex[2:]
        orderbook_url = f"{clob_base}/orderbook?token_id={token_hex_no_prefix}"
        response = requests.get(orderbook_url, timeout=5)
        print(f"  Hex without 0x: {response.status_code}")
        
        # Format 4: Padded hex (64 chars)
        padded_hex = token_hex_no_prefix.zfill(64)
        orderbook_url = f"{clob_base}/orderbook?token_id={padded_hex}"
        response = requests.get(orderbook_url, timeout=5)
        print(f"  Padded hex (64): {response.status_code}")