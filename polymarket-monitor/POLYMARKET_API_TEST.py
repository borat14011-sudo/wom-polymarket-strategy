# POLYMARKET_API_TEST.py - Live API Access Verification
# Testing all Polymarket API endpoints for live data access

import requests
import json
from datetime import datetime

def test_gamma_api():
    """Test Gamma API for market data"""
    print("="*60)
    print("TESTING GAMMA API")
    print("="*60)
    
    try:
        response = requests.get('https://gamma-api.polymarket.com/markets', timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            markets = response.json()
            print(f"Markets Retrieved: {len(markets)}")
            print()
            
            # Look for Musk/Elon markets
            musk_markets = []
            for market in markets:
                question = market.get('question', '').lower()
                if any(term in question for term in ['musk', 'elon', 'tweet']):
                    musk_markets.append(market)
            
            print(f"Musk-related markets in current batch: {len(musk_markets)}")
            for m in musk_markets[:5]:  # Show first 5
                print(f"  - {m.get('question', 'N/A')[:50]}")
                print(f"    End Date: {m.get('endDate', 'N/A')}")
                print(f"    Volume: ${m.get('volume', 0):,.0f}")
                print()
            
            return markets
        else:
            print(f"ERROR: Status code {response.status_code}")
            return []
            
    except Exception as e:
        print(f"ERROR: {e}")
        return []

def test_clob_api():
    """Test CLOB API for order book data"""
    print("="*60)
    print("TESTING CLOB API")
    print("="*60)
    
    try:
        response = requests.get('https://clob.polymarket.com/markets', timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            print(f"Markets Retrieved: {len(markets)}")
            print()
            
            return markets
        else:
            print(f"ERROR: Status code {response.status_code}")
            return []
            
    except Exception as e:
        print(f"ERROR: {e}")
        return []

def test_timeseries_api():
    """Test Timeseries API for historical prices"""
    print("="*60)
    print("TESTING TIMESERIES API")
    print("="*60)
    
    # Test with a known market ID
    test_market_id = "0xa69729ae3d9838ec5754e0f74bf57dedd5ddbecd9e31b15a04f48f081168ba00"
    
    try:
        url = f'https://clob.polymarket.com/prices-history'
        params = {
            'market': test_market_id,
            'interval': '1h'
        }
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Data points: {len(data)}")
            print()
            return data
        else:
            print(f"ERROR: Status code {response.status_code}")
            return []
            
    except Exception as e:
        print(f"ERROR: {e}")
        return []

def search_all_musk_markets():
    """Comprehensive search for all Musk-related markets"""
    print("="*60)
    print("COMPREHENSIVE MUSK MARKET SEARCH")
    print("="*60)
    print(f"Search Time: {datetime.now()}")
    print()
    
    all_musk_markets = []
    
    # Get all markets from Gamma API
    try:
        response = requests.get('https://gamma-api.polymarket.com/markets?active=true&closed=false', timeout=15)
        if response.status_code == 200:
            markets = response.json()
            print(f"Total Active Markets: {len(markets)}")
            print()
            
            # Search for Musk markets
            search_terms = ['musk', 'elon', 'tweet', 'twitter', 'x.com', 'spacex', 'tesla']
            
            for market in markets:
                question = market.get('question', '').lower()
                description = market.get('description', '').lower()
                
                if any(term in question or term in description for term in search_terms):
                    all_musk_markets.append(market)
            
            print(f"Musk-related Markets Found: {len(all_musk_markets)}")
            print()
            
            # Display detailed info for each
            for i, market in enumerate(all_musk_markets, 1):
                print(f"{i}. {market.get('question', 'N/A')}")
                print(f"   End Date: {market.get('endDate', 'N/A')}")
                print(f"   Volume: ${market.get('volume', 0):,.0f}")
                print(f"   Liquidity: ${market.get('liquidity', 0):,.0f}")
                
                # Get current prices if available
                outcomes = market.get('outcomes', [])
                prices = market.get('outcomePrices', [])
                if outcomes and prices and len(outcomes) == len(prices):
                    print(f"   Current Odds:")
                    for outcome, price in zip(outcomes, prices):
                        print(f"     - {outcome}: {float(price)*100:.1f}%")
                print()
                
    except Exception as e:
        print(f"ERROR: {e}")
    
    return all_musk_markets

def main():
    """Run all API tests"""
    print("\n" + "="*60)
    print("POLYMARKET API LIVE ACCESS VERIFICATION")
    print("="*60)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Test all APIs
    gamma_markets = test_gamma_api()
    print()
    
    clob_markets = test_clob_api()
    print()
    
    timeseries_data = test_timeseries_api()
    print()
    
    # Comprehensive Musk search
    musk_markets = search_all_musk_markets()
    print()
    
    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Gamma API: {'✅ WORKING' if gamma_markets else '❌ FAILED'}")
    print(f"CLOB API: {'✅ WORKING' if clob_markets else '❌ FAILED'}")
    print(f"Timeseries API: {'✅ WORKING' if timeseries_data else '❌ FAILED'}")
    print(f"Musk Markets Found: {len(musk_markets)}")
    print()
    
    if musk_markets:
        print("🎯 RECOMMENDATION: Deploy trades on identified Musk markets")
    else:
        print("⚠️  No active Musk markets found - continue monitoring")
    
    return {
        'gamma': gamma_markets,
        'clob': clob_markets,
        'timeseries': timeseries_data,
        'musk_markets': musk_markets
    }

if __name__ == "__main__":
    results = main()