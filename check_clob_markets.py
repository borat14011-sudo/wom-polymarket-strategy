#!/usr/bin/env python3
"""
Check what markets are actually available on CLOB
"""

import requests
import json

print("Checking CLOB markets...")

# Try to get markets from CLOB API
try:
    # CLOB markets endpoint
    url = "https://clob.polymarket.com/markets"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        markets = response.json()
        print(f"Found {len(markets)} markets on CLOB")
        
        # Show first 5
        for i, market in enumerate(markets[:5]):
            print(f"\n{i+1}. {market.get('question', 'Unknown')[:60]}...")
            print(f"   Condition ID: {market.get('conditionId', '')[:20]}...")
            print(f"   Active: {market.get('active', False)}")
            print(f"   Closed: {market.get('closed', False)}")
    else:
        print(f"CLOB API returned HTTP {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"Error checking CLOB: {e}")

print("\n" + "="*60)
print("Checking Gamma API for comparison...")

# Check Gamma API
try:
    url = "https://gamma-api.polymarket.com/markets"
    params = {"active": "true", "closed": "false", "limit": 5}
    response = requests.get(url, params=params, timeout=10)
    
    if response.status_code == 200:
        markets = response.json()
        print(f"Found {len(markets)} active markets on Gamma API")
        
        for i, market in enumerate(markets[:3]):
            print(f"\n{i+1}. {market.get('question', 'Unknown')[:60]}...")
            print(f"   Condition ID: {market.get('conditionId', '')[:20]}...")
            print(f"   Volume: ${market.get('volume', 0):,.0f}")
            
except Exception as e:
    print(f"Error checking Gamma: {e}")