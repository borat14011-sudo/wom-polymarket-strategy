#!/usr/bin/env python3
"""
Check market structure from Gamma API
"""

import requests
import json

def check_market():
    """Check market structure"""
    url = "https://gamma-api.polymarket.com/events?closed=false&limit=1"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        events = response.json()
        if events:
            event = events[0]
            print(f"Event ID: {event['id']}")
            print(f"Title: {event['title']}")
            
            markets = event.get('markets', [])
            print(f"\nNumber of markets: {len(markets)}")
            
            if markets:
                market = markets[0]
                print(f"\nMarket ID: {market['id']}")
                print(f"Question: {market['question']}")
                
                tokens = market.get('tokens', [])
                print(f"\nNumber of tokens: {len(tokens)}")
                
                for token in tokens:
                    print(f"\nToken:")
                    print(f"  ID: {token['id']}")
                    print(f"  Outcome: {token['outcome']}")
                    print(f"  Price: {token.get('price', 'N/A')}")
                
                return market
    
    return None

def main():
    """Main function"""
    print("Checking market structure...")
    market = check_market()
    
    if market:
        print("\n" + "="*50)
        print("Market structure confirmed!")
        print("Use token IDs for CLOB API, not market IDs")
        print("="*50)

if __name__ == "__main__":
    main()