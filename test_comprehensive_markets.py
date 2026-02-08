#!/usr/bin/env python3
"""
Test current Polymarket markets with different API approaches
"""
import requests
import json
from datetime import datetime

def test_all_market_endpoints():
    """Test various Polymarket API endpoints"""
    
    # Different approaches to get markets
    endpoints_to_test = [
        # Basic markets endpoint
        ("https://gamma-api.polymarket.com/markets", {}),
        # Markets with simple limit
        ("https://gamma-api.polymarket.com/markets", {"limit": 20}),
        # Markets with different sorting
        ("https://gamma-api.polymarket.com/markets", {"limit": 20, "sort": "created"}),
        # Try clob API
        ("https://clob.polymarket.com/markets", {}),
        # Try conditional token API
        ("https://gamma-api.polymarket.com/conditional-tokens", {})
    ]
    
    print("Testing multiple Polymarket API approaches...")
    print("=" * 60)
    
    working_endpoints = []
    
    for url, params in endpoints_to_test:
        try:
            print(f"Testing: {url}")
            if params:
                print(f"  Params: {params}")
                
            response = requests.get(url, params=params, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"  SUCCESS: Found {len(data)} items")
                    if len(data) > 0:
                        sample = data[0]
                        if 'question' in sample:
                            print(f"  Sample: {sample['question'][:60]}...")
                        elif 'title' in sample:
                            print(f"  Sample: {sample['title'][:60]}...")
                        else:
                            print(f"  Available keys: {list(sample.keys())}")
                    working_endpoints.append((url, params, data))
                elif isinstance(data, dict):
                    print(f"  Dict response keys: {list(data.keys())}")
                    if 'markets' in data:
                        print(f"  Markets found: {len(data['markets'])}")
                        working_endpoints.append((url, params, data['markets']))
            else:
                print(f"  Error: {response.text[:150]}")
                
        except Exception as e:
            print(f"  Failed: {e}")
        print()
    
    return working_endpoints

def check_for_superbowl_markets(markets):
    """Look for Super Bowl related markets"""
    print("Searching for Super Bowl markets...")
    superbowl_keywords = ['super bowl', 'superbowl', 'chiefs', 'eagles', 'patrick mahomes', 'jalen hurts']
    
    superbowl_markets = []
    for market in markets:
        question = market.get('question', '').lower()
        for keyword in superbowl_keywords:
            if keyword in question:
                superbowl_markets.append(market)
                break
    
    if superbowl_markets:
        print(f"Found {len(superbowl_markets)} Super Bowl related markets:")
        for i, market in enumerate(superbowl_markets[:3]):
            print(f"{i+1}. {market.get('question', 'No question')}")
            print(f"   Volume: {market.get('volume', 'N/A')}")
    else:
        print("No Super Bowl markets found in current data")
    
    return superbowl_markets

if __name__ == "__main__":
    working_endpoints = test_all_market_endpoints()
    
    if working_endpoints:
        print("=" * 60)
        print("SUMMARY: Working API endpoints found!")
        for url, params, data in working_endpoints:
            print(f"SUCCESS: {url} - {len(data)} markets")
        
        # Use the first working endpoint to search for Super Bowl markets
        if working_endpoints:
            url, params, markets = working_endpoints[0]
            check_for_superbowl_markets(markets)
    else:
        print("No working endpoints found")