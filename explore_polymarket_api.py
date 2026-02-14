#!/usr/bin/env python3
"""
Explore Polymarket API for trading endpoints
"""

import requests
import json

print("="*60)
print("EXPLORING POLYMARKET API")
print("="*60)

# Test different endpoints
endpoints = [
    ("Events", "https://gamma-api.polymarket.com/events?closed=false&limit=1"),
    ("Markets", "https://gamma-api.polymarket.com/markets?limit=1&closed=false"),
    ("Market Details", "https://gamma-api.polymarket.com/markets/517310"),
    ("CLOB Orderbook", "https://clob.polymarket.com/orderbook?token_id=101676997363687199724245607342877036148401850938023978421879460310389391082353"),
    ("CLOB Time", "https://clob.polymarket.com/time"),
    ("Gamma Health", "https://gamma-api.polymarket.com/health"),
]

for name, url in endpoints:
    try:
        response = requests.get(url, timeout=5)
        print(f"\n{name}:")
        print(f"  URL: {url[:80]}...")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if name == "CLOB Orderbook":
                    bids = data.get('bids', [])
                    asks = data.get('asks', [])
                    print(f"  Bids: {len(bids)}, Asks: {len(asks)}")
                elif name == "Market Details":
                    question = data.get('question', '')[:50]
                    print(f"  Question: {question}...")
                else:
                    print(f"  Response: {str(data)[:100]}...")
            except:
                print(f"  Response: {response.text[:100]}...")
        else:
            print(f"  Error: {response.text[:100]}")
    except Exception as e:
        print(f"\n{name}: Error - {e}")

# Check if there's a swap/AMM endpoint
print("\n" + "="*60)
print("CHECKING FOR SWAP/AMM ENDPOINTS")
print("="*60)

# Try to find AMM router
# Based on Polymarket docs, there might be a swap endpoint
market_id = "517310"

# Check market liquidity
market_url = f"https://gamma-api.polymarket.com/markets/{market_id}"
response = requests.get(market_url, timeout=5)

if response.status_code == 200:
    market = response.json()
    question = market.get('question', '')[:50]
    liquidity = market.get('liquidity', 0)
    volume24h = market.get('volume24h', 0)
    outcome_prices = market.get('outcomePrices', [])
    
    print(f"\nMarket: {question}...")
    print(f"Liquidity: ${liquidity:,.2f}")
    print(f"24h Volume: ${volume24h:,.2f}")
    print(f"Outcome Prices: {outcome_prices}")
    
    # Check if it's AMM
    amm_info = market.get('amm', {})
    if amm_info:
        print(f"AMM Info: {amm_info}")
    else:
        print(f"No AMM info found")
        
    # Check for swap endpoint
    swap_url = f"https://gamma-api.polymarket.com/markets/{market_id}/swap"
    swap_response = requests.get(swap_url, timeout=5)
    print(f"\nSwap endpoint ({swap_url[:80]}...): {swap_response.status_code}")
    
    # Check for quote endpoint
    quote_url = f"https://gamma-api.polymarket.com/markets/{market_id}/quote"
    quote_response = requests.get(quote_url, timeout=5)
    print(f"Quote endpoint ({quote_url[:80]}...): {quote_response.status_code}")

print("\n" + "="*60)
print("KEY FINDINGS")
print("="*60)
print("1. Gamma API works (events, markets, health)")
print("2. CLOB API works (time endpoint)")
print("3. CLOB Orderbook returns 404 (token_id format issue)")
print("4. Need to find correct trading endpoint")
print("="*60)