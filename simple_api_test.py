#!/usr/bin/env python3
"""
Simple API test - find working token_id
"""

import requests
import json

print("="*60)
print("FINDING WORKING TOKEN_ID")
print("="*60)

# Get markets from CLOB API
clob_base = "https://clob.polymarket.com"
markets_url = f"{clob_base}/markets"

try:
    response = requests.get(markets_url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, dict) and 'markets' in data:
            markets = data['markets']
            print(f"Found {len(markets)} markets")
            
            # Find first market with tokens
            for market in markets:
                if 'tokens' in market and market['tokens']:
                    tokens = market['tokens']
                    
                    print(f"\nMarket: {market.get('question', 'Unknown')[:50]}...")
                    print(f"Tokens: {len(tokens)}")
                    
                    # Try first token
                    token = tokens[0]
                    token_id = token.get('id')
                    outcome = token.get('outcome')
                    
                    print(f"Token ID: {token_id}")
                    print(f"Outcome: {outcome}")
                    
                    # Test order book
                    orderbook_url = f"{clob_base}/orderbook?token_id={token_id}"
                    ob_response = requests.get(orderbook_url, timeout=5)
                    
                    if ob_response.status_code == 200:
                        orderbook = ob_response.json()
                        bids = orderbook.get('bids', [])
                        asks = orderbook.get('asks', [])
                        
                        print(f"\n✅ SUCCESS! Order book found!")
                        print(f"Bids: {len(bids)}, Asks: {len(asks)}")
                        
                        if bids:
                            print(f"Best bid: {bids[0].get('price')} @ {bids[0].get('size')}")
                        if asks:
                            print(f"Best ask: {asks[0].get('price')} @ {asks[0].get('size')}")
                        
                        # Save token info
                        token_info = {
                            "market_id": market.get('id'),
                            "question": market.get('question'),
                            "token_id": token_id,
                            "outcome": outcome,
                            "best_bid": bids[0].get('price') if bids else None,
                            "best_ask": asks[0].get('price') if asks else None
                        }
                        
                        with open('working_token.json', 'w') as f:
                            json.dump(token_info, f, indent=2)
                        print(f"\nSaved to: working_token.json")
                        
                        break  # Found working token
                    else:
                        print(f"❌ Order book error: {ob_response.status_code}")
                        
        else:
            print(f"Unexpected response format")
    else:
        print(f"API error: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("NEXT")
print("="*60)
print("If we found a working token_id, we can test trading")
print("="*60)