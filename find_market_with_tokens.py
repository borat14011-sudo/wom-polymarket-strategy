#!/usr/bin/env python3
"""
Find a market with tokens for API testing
"""

import requests
import json

def find_market_with_tokens():
    """Find a market with tokens"""
    print("Searching for market with tokens...")
    
    url = "https://gamma-api.polymarket.com/events?closed=false&limit=50"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        events = response.json()
        
        for i, event in enumerate(events):
            markets = event.get('markets', [])
            
            for market in markets:
                tokens = market.get('tokens', [])
                
                if len(tokens) >= 2:
                    print(f"\nFound market with {len(tokens)} tokens:")
                    print(f"Event: {event['title'][:60]}...")
                    print(f"Market ID: {market['id']}")
                    print(f"Question: {market['question'][:80]}...")
                    
                    for token in tokens:
                        print(f"  {token['outcome']}: ID={token['id']}, Price={token.get('price', 'N/A')}")
                    
                    return market
            
            if i >= 10:  # Check first 10 events only
                break
    
    print("\nNo market with tokens found in first 10 events")
    return None

def main():
    """Main function"""
    print("="*50)
    print("FIND MARKET WITH TOKENS FOR CLOB API")
    print("="*50)
    
    market = find_market_with_tokens()
    
    if market:
        print("\n" + "="*50)
        print("SUCCESS! Use this market for testing:")
        print(f"Market: {market['question']}")
        
        tokens = market.get('tokens', [])
        for token in tokens:
            print(f"{token['outcome']} Token ID: {token['id']}")
        
        print("\nFor CLOB API testing:")
        print(f"Use token ID {tokens[0]['id']} for YES")
        print(f"Use token ID {tokens[1]['id']} for NO")
        print("="*50)

if __name__ == "__main__":
    main()