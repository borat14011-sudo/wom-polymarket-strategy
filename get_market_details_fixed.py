#!/usr/bin/env python3
"""
Get details for GTA VI market
"""

import requests
import json

print("Searching for GTA VI market...")

url = 'https://gamma-api.polymarket.com/markets'
params = {'active': 'true', 'closed': 'false', 'limit': 20}
response = requests.get(url, params=params)
markets = response.json()

found = False
for market in markets:
    question = market.get('question', '').lower()
    if 'gta vi' in question and 'released before june 2026' in question:
        print('[OK] Found GTA VI market:')
        print(f'  Condition ID: {market["conditionId"]}')
        print(f'  Question: {market["question"]}')
        volume = float(market.get("volume", 0))
        print(f'  Volume: ${volume:,.0f}')
        print(f'  YES price: {market.get("yesPrice", 0)}')
        print(f'  NO price: {market.get("noPrice", 0)}')
        print(f'  Slug: {market.get("slug", "")}')
        
        # Save for trade script
        market_info = {
            'condition_id': market['conditionId'],
            'question': market['question'],
            'volume': market.get('volume', 0),
            'yes_price': market.get('yesPrice', 0),
            'no_price': market.get('noPrice', 0),
            'slug': market.get('slug', '')
        }
        
        with open('gta_market_info.json', 'w') as f:
            json.dump(market_info, f, indent=2)
        
        print('\n[OK] Market info saved to gta_market_info.json')
        found = True
        break

if not found:
    print('[WARN] GTA VI market not found, showing first 3 markets:')
    for i, market in enumerate(markets[:3]):
        print(f'\n{i+1}. {market["question"][:80]}...')
        print(f'   Condition ID: {market["conditionId"]}')
        print(f'   Volume: ${market.get("volume", 0):,.0f}')
        print(f'   YES price: {market.get("yesPrice", 0)}')
        print(f'   NO price: {market.get("noPrice", 0)}')