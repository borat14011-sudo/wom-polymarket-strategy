#!/usr/bin/env python3
"""
Check py-clob-client usage
"""

import requests
import json

# Let me check what the actual Polymarket website uses
# Look at network requests when trading

print("="*60)
print("CHECKING ACTUAL POLYMARKET API USAGE")
print("="*60)

# Try to get order book from a different endpoint
# Based on Polymarket's actual API usage

# Try the CLOB API directly
clob_base = "https://clob.polymarket.com"

# Get markets from CLOB API
markets_url = f"{clob_base}/markets"
response = requests.get(markets_url, timeout=10)

if response.status_code == 200:
    markets = response.json()
    print(f"Found {len(markets)} markets from CLOB API")
    
    # Look at first market
    if markets:
        market = markets[0]
        print(f"\nFirst market:")
        print(f"  ID: {market.get('id')}")
        print(f"  Question: {market.get('question', 'Unknown')[:50]}...")
        
        # Check for token IDs
        print(f"\nKeys in market:")
        for key in market.keys():
            print(f"  {key}")
            
        # Check if there's a tokens field
        if 'tokens' in market:
            tokens = market['tokens']
            print(f"\nTokens: {tokens}")
            
            # Try order book with token ID from tokens
            for token in tokens:
                token_id = token.get('id')
                if token_id:
                    print(f"\nTrying token ID: {token_id}")
                    
                    orderbook_url = f"{clob_base}/orderbook?token_id={token_id}"
                    ob_response = requests.get(orderbook_url, timeout=5)
                    
                    if ob_response.status_code == 200:
                        orderbook = ob_response.json()
                        print(f"  SUCCESS! Bids: {len(orderbook.get('bids', []))}, Asks: {len(orderbook.get('asks', []))}")
                        break
                    else:
                        print(f"  Error: {ob_response.status_code}")
        
        # Save sample market
        with open('clob_market_sample.json', 'w') as f:
            json.dump(market, f, indent=2)
        print(f"\nSample market saved to: clob_market_sample.json")
        
else:
    print(f"CLOB markets API error: {response.status_code}")

# Try another approach - look at network tab pattern
print(f"\n" + "="*60)
print("TRYING DIFFERENT FORMATS")
print("="*60)

# The token IDs might need to be in a specific format
# Let me check if they need to be converted to hex

token_decimal = "101676997363687199724245607342877036148401850938023978421879460310389391082353"

# Convert decimal to hex
token_hex = hex(int(token_decimal))
print(f"Decimal: {token_decimal}")
print(f"Hex: {token_hex}")

# Try with hex
orderbook_url = f"{clob_base}/orderbook?token_id={token_hex}"
response = requests.get(orderbook_url, timeout=5)
print(f"\nTrying hex {token_hex}: {response.status_code}")

# Try without 0x prefix
token_hex_no_prefix = token_hex[2:]
orderbook_url = f"{clob_base}/orderbook?token_id={token_hex_no_prefix}"
response = requests.get(orderbook_url, timeout=5)
print(f"Trying hex without prefix {token_hex_no_prefix[:20]}...: {response.status_code}")

# Try the other token
token2_decimal = "4153292802911610701832309484716814274802943278345248636922528170020319407796"
token2_hex = hex(int(token2_decimal))
print(f"\nToken 2 Hex: {token2_hex}")

orderbook_url = f"{clob_base}/orderbook?token_id={token2_hex}"
response = requests.get(orderbook_url, timeout=5)
print(f"Trying token 2 hex: {response.status_code}")