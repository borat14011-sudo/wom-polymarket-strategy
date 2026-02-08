#!/usr/bin/env python3
"""
Clean test for current Polymarket market access
"""
import requests
import json

def clean_test_markets():
    """Clean test of market APIs"""
    print("CLEAN TEST: Polymarket API Access")
    print("=" * 50)
    
    # Test 1: Basic markets endpoint
    try:
        response = requests.get("https://gamma-api.polymarket.com/markets", timeout=10)
        print(f"Gamma API /markets: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Markets returned: {len(data)}")
            if data:
                print(f"  Sample: {data[0].get('question', 'No question')[:60]}...")
        print()
    except Exception as e:
        print(f"  Error: {e}")
        print()
    
    # Test 2: CLOB markets endpoint  
    try:
        response = requests.get("https://clob.polymarket.com/markets", timeout=10)
        print(f"CLOB API /markets: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Response keys: {list(data.keys())}")
            markets = data.get('data', [])
            print(f"  Markets returned: {len(markets)}")
            if markets:
                print(f"  Sample: {markets[0].get('question', markets[0].get('title', 'No text'))[:60]}...")
                print(f"  Market has tokens: {'tokens' in markets[0]}")
        print()
    except Exception as e:
        print(f"  Error: {e}")
        print()
    
    # Test 3: Try to get current Super Bowl markets
    try:
        response = requests.get("https://clob.polymarket.com/markets", timeout=10)
        if response.status_code == 200:
            data = response.json()
            markets = data.get('data', [])
            
            # Search for current events
            current_found = []
            keywords = ['super bowl', 'trump', 'biden', 'musk', '2025', '2024']
            
            for market in markets[:100]:  # Check first 100
                question = market.get('question', market.get('title', '')).lower()
                for keyword in keywords:
                    if keyword in question:
                        current_found.append(market)
                        break
            
            print(f"Current event markets found: {len(current_found)}")
            for i, market in enumerate(current_found[:5]):
                text = market.get('question', market.get('title', 'No text'))
                print(f"  {i+1}. {text[:70]}...")
            print()
            
    except Exception as e:
        print(f"Current events search error: {e}")
        print()

def test_order_book_access():
    """Test if we can access order book data"""
    print("TESTING ORDER BOOK ACCESS:")
    print("-" * 30)
    
    try:
        # Get a market with tokens
        response = requests.get("https://clob.polymarket.com/markets", timeout=10)
        if response.status_code == 200:
            data = response.json()
            markets = data.get('data', [])
            
            # Find market with tokens
            for market in markets[:10]:
                if 'tokens' in market and market['tokens']:
                    token = market['tokens'][0]
                    token_id = token.get('token_id')
                    if token_id:
                        print(f"Testing token: {token_id[:20]}...")
                        
                        # Test order book endpoint
                        ob_url = f"https://clob.polymarket.com/orderbook/{token_id}"
                        ob_response = requests.get(ob_url, timeout=10)
                        print(f"Order book API status: {ob_response.status_code}")
                        
                        if ob_response.status_code == 200:
                            print("SUCCESS: Order book data available!")
                            ob_data = ob_response.json()
                            print(f"Order book keys: {list(ob_data.keys())}")
                        else:
                            print(f"Order book error: {ob_response.text[:100]}")
                        
                        return
            
            print("No markets with tokens found")
    except Exception as e:
        print(f"Order book test error: {e}")

if __name__ == "__main__":
    clean_test_markets()
    test_order_book_access()