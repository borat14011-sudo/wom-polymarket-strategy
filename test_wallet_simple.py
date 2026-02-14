#!/usr/bin/env python3
"""
Test wallet connectivity and API access for Polymarket
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.constants import POLYGON
import requests

# Wallet configuration
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
WALLET_ADDRESS = "0xb354e25623617a24164639F63D8b731250AC92d8"

def test_wallet():
    """Test wallet connectivity"""
    print("Testing wallet connectivity...")
    
    try:
        # Create account from private key
        account = Account.from_key(PRIVATE_KEY)
        print(f"Wallet address: {account.address}")
        print(f"Expected address: {WALLET_ADDRESS}")
        
        if account.address.lower() == WALLET_ADDRESS.lower():
            print("Wallet address matches!")
        else:
            print("Wallet address mismatch!")
            return False
            
        return True
        
    except Exception as e:
        print(f"Wallet error: {e}")
        return False

def test_api_connection():
    """Test CLOB API connection"""
    print("\nTesting CLOB API connection...")
    
    try:
        # Initialize client
        client = ClobClient(
            host="https://clob.polymarket.com",
            chain_id=POLYGON,
            key=Account.from_key(PRIVATE_KEY).key,
            signature_type=0,
            funder=WALLET_ADDRESS
        )
        
        # Get API credentials
        creds = client.create_or_derive_api_creds()
        print(f"API credentials obtained:")
        print(f"  API Key: {creds.api_key}")
        print(f"  API Secret: {creds.api_secret[:10]}...")
        print(f"  API Passphrase: {creds.api_passphrase[:10]}...")
        
        # Test a simple API call - get order book for a known market
        # First get a market ID from Gamma API
        gamma_url = "https://gamma-api.polymarket.com/events?closed=false&limit=1"
        gamma_resp = requests.get(gamma_url, timeout=5)
        if gamma_resp.status_code == 200:
            events = gamma_resp.json()
            if events and isinstance(events, list) and len(events) > 0:
                event = events[0]
                markets = event.get('markets', [])
                if markets:
                    market_id = markets[0]['id']
                    print(f"Using market ID for test: {market_id}")
                
                # Try to get order book
                try:
                    order_book = client.get_order_book(market_id)
                    print(f"Retrieved order book for market {market_id}")
                except Exception as e:
                    print(f"Could not get order book (may need auth): {e}")
        else:
            print("Could not fetch market ID from Gamma API")
        
        return True
        
    except Exception as e:
        print(f"API connection error: {e}")
        return False

def test_gamma_api():
    """Test Gamma API (market data)"""
    print("\nTesting Gamma API (market data)...")
    
    try:
        url = "https://gamma-api.polymarket.com/events?closed=false&limit=5"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            events = response.json()
            print(f"Retrieved {len(events)} events")
            
            # Show first event
            if events:
                event = events[0]
                print(f"Sample event: {event.get('title', 'No title')[:50]}...")
                print(f"Markets: {len(event.get('markets', []))}")
                
            return True
        else:
            print(f"Gamma API error: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Gamma API error: {e}")
        return False

def test_small_market():
    """Find a small market for testing"""
    print("\nFinding small test market...")
    
    try:
        url = "https://gamma-api.polymarket.com/events?closed=false&limit=20"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            events = response.json()
            
            for event in events:
                for market in event.get('markets', []):
                    if market.get('active') and market.get('volume24h', 0) < 1000:
                        tokens = market.get('tokens', [])
                        if len(tokens) >= 2:
                            print(f"Found test market:")
                            print(f"ID: {market['id']}")
                            print(f"Question: {market['question'][:60]}...")
                            print(f"Volume (24h): ${market.get('volume24h', 0)}")
                            print(f"Tokens: {[t['outcome'] for t in tokens]}")
                            return market
            
            print("No suitable small market found")
            return None
            
    except Exception as e:
        print(f"Error finding market: {e}")
        return None

def main():
    """Run all tests"""
    print("="*50)
    print("POLYMARKET WALLET & API TEST SUITE")
    print("="*50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Wallet connectivity
    if test_wallet():
        tests_passed += 1
    
    # Test 2: CLOB API connection
    if test_api_connection():
        tests_passed += 1
    
    # Test 3: Gamma API
    if test_gamma_api():
        tests_passed += 1
    
    # Test 4: Find test market
    test_market = test_small_market()
    if test_market:
        tests_passed += 1
    
    print("\n" + "="*50)
    print(f"TEST RESULTS: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("ALL TESTS PASSED! Ready for trading.")
        print(f"\nRecommended test market:")
        print(f"ID: {test_market['id']}")
        print(f"Question: {test_market['question'][:80]}...")
    else:
        print("Some tests failed. Check configuration.")
    
    print("="*50)

if __name__ == "__main__":
    main()