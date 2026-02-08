#!/usr/bin/env python3
"""
Test CLOB API for current markets and prices
"""
import requests
import json

def test_clob_api():
    """Test the CLOB API for market data"""
    try:
        # Test CLOB markets endpoint
        url = "https://clob.polymarket.com/markets"
        response = requests.get(url, timeout=10)
        
        print(f"CLOB API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response structure: {list(data.keys())}")
            
            if 'data' in data:
                markets = data['data']
                print(f"Found {len(markets)} markets in CLOB data")
                
                # Show some current markets
                print("\nCLOB MARKET EXAMPLES:")
                print("=" * 50)
                
                for i, market in enumerate(markets[:5]):
                    if 'question' in market:
                        print(f"{i+1}. {market['question'][:80]}...")
                    elif 'title' in market:
                        print(f"{i+1}. {market['title'][:80]}...")
                    
                    # Show available fields
                    print(f"   Available fields: {list(market.keys())}")
                    
                    # Show volume if available
                    if 'volume' in market:
                        print(f"   Volume: {market['volume']}")
                    if 'clobTokenIds' in market:
                        print(f"   CLOB Tokens: {len(market['clobTokenIds'])}")
                    
                    print()
                
                return markets
            else:
                print("No 'data' field in response")
                return None
        else:
            print(f"Error: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"CLOB API test failed: {e}")
        return None

def search_current_events(markets):
    """Search for current event markets"""
    current_keywords = [
        'trump', 'biden', '2025', '2026', 'super bowl', 'chiefs', 'eagles',
        'musk', 'tesla', 'bitcoin', 'crypto', 'election', 'president'
    ]
    
    print("SEARCHING FOR CURRENT EVENT MARKETS:")
    print("=" * 50)
    
    found_markets = []
    
    for market in markets:
        text = ""
        if 'question' in market:
            text = market['question'].lower()
        elif 'title' in market:
            text = market['title'].lower()
        
        for keyword in current_keywords:
            if keyword in text:
                found_markets.append(market)
                print(f"Found '{keyword}' market:")
                print(f"  {text[:100]}...")
                print(f"  Fields: {list(market.keys())}")
                print()
                break
    
    return found_markets

if __name__ == "__main__":
    print("Testing CLOB API for current market data...")
    print("=" * 60)
    
    markets = test_clob_api()
    
    if markets:
        current_markets = search_current_events(markets)
        print(f"\nFound {len(current_markets)} current event markets")
        
        # Test if we can get more details
        if markets and 'clobTokenIds' in markets[0]:
            print("\nCLOB Token IDs available - can potentially get order book data")
    else:
        print("No CLOB market data available")