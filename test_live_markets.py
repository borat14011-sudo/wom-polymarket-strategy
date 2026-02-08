#!/usr/bin/env python3
"""
Test Polymarket API endpoints for live market data access
"""
import requests
import json

def test_polymarket_apis():
    """Test basic Polymarket API endpoints without authentication"""
    endpoints = [
        'https://gamma-api.polymarket.com/markets',
        'https://clob.polymarket.com/markets',
        'https://data-api.polymarket.com/markets'
    ]
    
    print('Testing Polymarket API endpoints for live market access...')
    print('=' * 60)
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            print(f'{endpoint}: Status {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f'  SUCCESS: Found {len(data)} markets')
                    print(f'  Sample market: {data[0].get("question", "No question field")[:100]}...')
                    print(f'  Market ID: {data[0].get("id", "No ID")}')
                    return endpoint, data  # Return successful endpoint
                elif isinstance(data, dict):
                    print(f'  Response keys: {list(data.keys())}')
            else:
                print(f'  Error: {response.text[:200]}')
                
        except Exception as e:
            print(f'  Failed: {e}')
        print()
    
    return None, None

if __name__ == "__main__":
    successful_endpoint, market_data = test_polymarket_apis()
    
    if successful_endpoint and market_data:
        print("SUCCESS: LIVE MARKET ACCESS CONFIRMED!")
        print(f"Best endpoint: {successful_endpoint}")
        print(f"Total markets available: {len(market_data)}")
        
        # Show some live market examples
        print("\nLIVE MARKET EXAMPLES:")
        for i, market in enumerate(market_data[:3]):
            print(f"{i+1}. {market.get('question', 'No question')[:80]}...")
            volume = market.get('volume', 0)
            if isinstance(volume, (int, float)):
                print(f"   Volume: ${volume:,.0f}")
            else:
                print(f"   Volume: {volume}")
            print(f"   End Date: {market.get('endDate', 'N/A')}")
            print()
    else:
        print("ERROR: No live market access available with current endpoints")