#!/usr/bin/env python3
"""
Test current active Polymarket markets
"""
import requests
import json

def get_active_markets():
    """Get currently active markets from Polymarket"""
    try:
        # Test gamma API for active markets
        url = "https://gamma-api.polymarket.com/markets"
        params = {
            'limit': 50,
            'active': True,
            'sort': 'volume',
            'order': 'desc'
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"Active markets API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} markets")
            
            # Show current active markets
            print("\nCURRENT ACTIVE MARKETS:")
            print("=" * 50)
            
            for i, market in enumerate(data[:5]):
                question = market.get('question', 'No question')
                volume = market.get('volume', 0)
                end_date = market.get('endDate', 'N/A')
                market_id = market.get('id', 'N/A')
                
                print(f"{i+1}. {question[:80]}...")
                print(f"   Market ID: {market_id}")
                print(f"   Volume: {volume}")
                print(f"   End Date: {end_date}")
                print()
                
            return data
        else:
            print(f"Error: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"Failed to fetch active markets: {e}")
        return None

def test_market_details(market_id):
    """Test getting detailed market data"""
    try:
        url = f"https://gamma-api.polymarket.com/markets/{market_id}"
        response = requests.get(url, timeout=10)
        
        print(f"Market details API status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Available fields: {list(data.keys())}")
            return data
        else:
            print(f"Error: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"Failed to fetch market details: {e}")
        return None

if __name__ == "__main__":
    print("Testing live Polymarket market access...")
    print("=" * 60)
    
    # Get active markets
    markets = get_active_markets()
    
    if markets and len(markets) > 0:
        # Test detailed data for first market
        first_market_id = markets[0].get('id')
        if first_market_id:
            print(f"Testing detailed data for market ID: {first_market_id}")
            details = test_market_details(first_market_id)
            
            if details:
                print("\nDETAILED MARKET DATA AVAILABLE!")
                print("Key fields for trading:")
                for key in ['question', 'endDate', 'volume', 'liquidity', 'outcomes', 'prices']:
                    if key in details:
                        print(f"  {key}: {details[key]}")
    else:
        print("No active markets found or API access limited")