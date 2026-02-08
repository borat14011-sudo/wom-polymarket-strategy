#!/usr/bin/env python3
"""
Search for current 2025 markets specifically
"""
import requests
import json
from datetime import datetime

def get_current_2025_markets():
    """Get markets for 2025"""
    try:
        # Get CLOB markets
        url = "https://clob.polymarket.com/markets"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            all_markets = data.get('data', [])
            
            print(f"Total markets in database: {len(all_markets)}")
            
            # Search for 2025 markets
            markets_2025 = []
            current_markets = []
            
            for market in all_markets:
                question = market.get('question', '').lower()
                end_date = market.get('end_date_iso', '')
                
                # Check for 2025 in question or end date
                if '2025' in question or '2025' in end_date:
                    markets_2025.append(market)
                
                # Also check for current/recent markets
                current_keywords = [
                    'trump 2024', 'biden 2024', 'election 2024', 'musk', 'tesla',
                    'bitcoin 2024', 'crypto 2024', 'super bowl 2025', 'super bowl lix'
                ]
                
                for keyword in current_keywords:
                    if keyword in question:
                        current_markets.append(market)
                        break
            
            print(f"\n2025 MARKETS FOUND: {len(markets_2025)}")
            print("=" * 50)
            
            for i, market in enumerate(markets_2025[:10]):
                print(f"{i+1}. {market.get('question', 'No question')}")
                print(f"   End Date: {market.get('end_date_iso', 'N/A')}")
                print(f"   Status: Active={market.get('active', 'N/A')}, Closed={market.get('closed', 'N/A')}")
                print()
            
            print(f"\nCURRENT EVENT MARKETS: {len(current_markets)}")
            print("=" * 50)
            
            for i, market in enumerate(current_markets[:10]):
                print(f"{i+1}. {market.get('question', 'No question')}")
                print(f"   End Date: {market.get('end_date_iso', 'N/A')}")
                print()
            
            return markets_2025, current_markets
            
    except Exception as e:
        print(f"Failed to fetch markets: {e}")
        return [], []

def test_price_api():
    """Test if we can get current prices"""
    try:
        # Test getting prices for a market
        # First, get a sample market
        url = "https://clob.polymarket.com/markets"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('data', [])
            
            if markets:
                # Get first market and check if it has tokens
                first_market = markets[0]
                if 'tokens' in first_market and first_market['tokens']:
                    token_id = first_market['tokens'][0].get('token_id')
                    if token_id:
                        print(f"Testing price API for token: {token_id}")
                        
                        # Try to get price
                        price_url = f"https://clob.polymarket.com/prices/{token_id}"
                        price_response = requests.get(price_url, timeout=10)
                        
                        print(f"Price API status: {price_response.status_code}")
                        if price_response.status_code == 200:
                            price_data = price_response.json()
                            print(f"Price data: {price_data}")
                            return True
                        else:
                            print(f"Price API error: {price_response.text[:100]}")
                            
    except Exception as e:
        print(f"Price API test failed: {e}")
    
    return False

if __name__ == "__main__":
    print("Searching for current 2025 markets...")
    print("=" * 60)
    
    markets_2025, current_markets = get_current_2025_markets()
    
    print(f"\nSUMMARY:")
    print(f"2025 Markets: {len(markets_2025)}")
    print(f"Current Events: {len(current_markets)}")
    
    print("\nTesting price API access...")
    has_prices = test_price_api()
    print(f"Price API access: {'YES' if has_prices else 'NO'}")