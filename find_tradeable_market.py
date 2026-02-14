#!/usr/bin/env python3
"""
Find a market that's actually tradeable on CLOB
"""

import requests
import json

print("Finding tradeable markets on CLOB...")

# Get CLOB markets
url = "https://clob.polymarket.com/markets"
response = requests.get(url, timeout=10)
data = response.json()

markets = data.get('data', [])
print(f"Found {len(markets)} markets on CLOB")

# Find markets with outcomes and token IDs
tradeable_markets = []
for market in markets:
    condition_id = market.get('conditionId', '')
    question = market.get('question', 'Unknown')
    outcomes = market.get('outcomes', [])
    
    if len(outcomes) >= 2:  # Need YES and NO outcomes
        token_ids = [outcome.get('tokenId', '') for outcome in outcomes]
        if all(token_ids):  # All token IDs exist
            tradeable_markets.append({
                'condition_id': condition_id,
                'question': question,
                'outcomes': outcomes,
                'token_ids': token_ids
            })

print(f"\nFound {len(tradeable_markets)} tradeable markets with token IDs")

# Show available markets
for i, market in enumerate(tradeable_markets[:5]):
    print(f"\n{i+1}. {market['question'][:60]}...")
    print(f"   Condition ID: {market['condition_id'][:20]}...")
    for j, outcome in enumerate(market['outcomes']):
        print(f"   {outcome.get('name', f'Outcome {j}')}: {outcome.get('tokenId', '')[:20]}...")

# If we found tradeable markets, pick one for test trade
if tradeable_markets:
    print("\n" + "="*60)
    print("RECOMMENDED FOR TEST TRADE:")
    test_market = tradeable_markets[0]
    print(f"Market: {test_market['question'][:80]}...")
    print(f"Condition ID: {test_market['condition_id']}")
    print(f"YES Token: {test_market['token_ids'][0][:20]}...")
    print(f"NO Token: {test_market['token_ids'][1][:20]}...")
    
    # Save for test trade script
    market_info = {
        'condition_id': test_market['condition_id'],
        'question': test_market['question'],
        'yes_token': test_market['token_ids'][0],
        'no_token': test_market['token_ids'][1]
    }
    
    with open('clob_market_for_test.json', 'w') as f:
        json.dump(market_info, f, indent=2)
    
    print("\nMarket info saved to clob_market_for_test.json")
else:
    print("\nNo tradeable markets found with token IDs")