#!/usr/bin/env python3
"""
Mimic browser requests to Polymarket
"""

import requests
import json
import time

print("="*60)
print("MIMIC BROWSER TRADING")
print("="*60)

# Step 1: Get market data like browser does
market_id = "517310"
url = f"https://gamma-api.polymarket.com/markets/{market_id}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://polymarket.com/",
}

response = requests.get(url, headers=headers, timeout=10)

if response.status_code == 200:
    market = response.json()
    question = market.get('question', '')[:50]
    condition_id = market.get('conditionId')
    
    print(f"Market: {question}")
    print(f"Condition ID: {condition_id}")
    
    # Parse outcomes
    outcomes_str = market.get('outcomes', '[]')
    try:
        outcomes = json.loads(outcomes_str)
        print(f"Outcomes: {outcomes}")
    except:
        print(f"Outcomes parse failed: {outcomes_str}")
        outcomes = []
    
    # Check for AMM data
    print(f"\nChecking for AMM data...")
    
    # Look for swap/AMM endpoints
    # Based on Polymarket website inspection
    
    # Try to get swap quote
    swap_url = f"https://gamma-api.polymarket.com/markets/{market_id}/swap/quote"
    
    swap_params = {
        "amount": "0.01",  # $0.01
        "side": "buy",  # buy YES
        "outcomeIndex": 0  # YES outcome
    }
    
    swap_response = requests.get(swap_url, params=swap_params, headers=headers, timeout=5)
    print(f"Swap quote status: {swap_response.status_code}")
    
    if swap_response.status_code == 200:
        quote = swap_response.json()
        print(f"Swap quote: {quote}")
    else:
        print(f"No swap quote endpoint")
    
    # Try different endpoints
    endpoints = [
        f"https://gamma-api.polymarket.com/markets/{market_id}/amm",
        f"https://gamma-api.polymarket.com/markets/{market_id}/pool",
        f"https://gamma-api.polymarket.com/markets/{market_id}/liquidity",
    ]
    
    for endpoint in endpoints:
        ep_response = requests.get(endpoint, headers=headers, timeout=5)
        print(f"{endpoint}: {ep_response.status_code}")
    
    # Step 2: Check if there's a GraphQL API
    print(f"\nChecking GraphQL API...")
    
    graphql_url = "https://gamma-api.polymarket.com/graphql"
    
    # Try to get market query
    graphql_query = {
        "query": """
        query GetMarket($id: ID!) {
            market(id: $id) {
                id
                question
                volume24h
                liquidity
                outcomes
                clobTokenIds
            }
        }
        """,
        "variables": {"id": market_id}
    }
    
    graphql_response = requests.post(graphql_url, json=graphql_query, headers=headers, timeout=5)
    print(f"GraphQL status: {graphql_response.status_code}")
    
    if graphql_response.status_code == 200:
        graphql_data = graphql_response.json()
        print(f"GraphQL data: {json.dumps(graphql_data, indent=2)[:200]}...")
    
    # Step 3: Check wallet endpoints
    print(f"\nChecking wallet endpoints...")
    
    # Try to get wallet balance (might need auth)
    wallet_url = "https://gamma-api.polymarket.com/wallet/balance"
    wallet_response = requests.get(wallet_url, headers=headers, timeout=5)
    print(f"Wallet balance status: {wallet_response.status_code}")
    
    # Step 4: Look for trading endpoints
    print(f"\nLooking for trading endpoints...")
    
    # Based on Polymarket docs, trading might be through:
    # 1. CLOB API (not working)
    # 2. AMM swap (might work)
    # 3. Website only
    
    # Try to find AMM router address
    print(f"\nSearching for AMM contract...")
    
    # Check if there's a known AMM router
    # Polymarket uses 0x... for AMM
    
    # Let me check the website JavaScript
    print(f"\nTo find actual trading endpoints:")
    print(f"1. Open Chrome DevTools (F12)")
    print(f"2. Go to Network tab")
    print(f"3. Go to polymarket.com")
    print(f"4. Make a trade")
    print(f"5. See what API calls are made")
    
else:
    print(f"API error: {response.status_code}")

print("\n" + "="*60)
print("IMMEDIATE ACTION NEEDED")
print("="*60)
print("Since API trading is complex, I need YOU to:")
print("\n1. Go to: https://polymarket.com")
print("2. Open DevTools (F12)")
print("3. Go to Network tab")
print("4. Make a $0.01 trade")
print("5. Send me the API calls you see")
print("\nOR simpler:")
print("1. Just make the $0.01 trade manually")
print("2. Tell me if it works")
print("="*60)