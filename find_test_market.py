#!/usr/bin/env python3
"""
Find a test market with token IDs for Polymarket API testing
"""

import requests

def find_test_market():
    """Find a small market with token IDs"""
    print("Searching for test market...")
    
    try:
        url = "https://gamma-api.polymarket.com/events?closed=false&limit=20"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            events = response.json()
            
            for event in events:
                for market in event.get('markets', []):
                    if market.get('active'):
                        tokens = market.get('tokens', [])
                        if len(tokens) >= 2:
                            print(f"\nMarket found:")
                            print(f"  Market ID: {market['id']}")
                            print(f"  Question: {market['question'][:80]}...")
                            print(f"  Volume (24h): ${market.get('volume24h', 0)}")
                            print(f"  Liquidity: ${market.get('liquidity', 0)}")
                            
                            for token in tokens:
                                print(f"  Token: {token['outcome']} -> ID: {token['id']}")
                            
                            # Return first market with tokens
                            return market
            
            print("No suitable market found")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """Main function"""
    print("="*50)
    print("FIND TEST MARKET FOR POLYMARKET API")
    print("="*50)
    
    market = find_test_market()
    
    if market:
        print("\n" + "="*50)
        print("SUCCESS! Use this market for testing:")
        print(f"Market ID: {market['id']}")
        print(f"Question: {market['question']}")
        
        tokens = market.get('tokens', [])
        for token in tokens:
            print(f"{token['outcome']} Token ID: {token['id']}")
        
        print("\nFor API testing, use token IDs (not market ID)")
        print("="*50)
    else:
        print("\nNo suitable market found")

if __name__ == "__main__":
    main()