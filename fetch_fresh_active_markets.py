#!/usr/bin/env python3
"""Fetch fresh OPEN markets from Polymarket"""
import requests
import json
from datetime import datetime

url = 'https://gamma-api.polymarket.com/markets'
params = {
    'limit': 200,
    'closed': False  # This gets actually open markets!
}

print("Fetching OPEN markets from Polymarket...")
response = requests.get(url, params=params, timeout=15)
print(f'API Status: {response.status_code}')

if response.status_code == 200:
    markets = response.json()
    print(f'Fetched {len(markets)} OPEN markets')
    
    # Add metadata
    data = {
        'fetch_timestamp': datetime.now().isoformat(),
        'count': len(markets),
        'markets': markets
    }
    
    # Save to file
    with open('active-markets.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f'\nSaved {len(markets)} open markets to active-markets.json')
    
    # Show sample
    print("\n--- TOP 10 OPEN MARKETS ---")
    # Sort by volume
    sorted_markets = sorted(markets, key=lambda x: float(x.get('volume', 0)), reverse=True)
    for m in sorted_markets[:10]:
        question = m.get('question', 'N/A')
        volume = float(m.get('volume', 0))
        end_date = m.get('endDate', 'N/A')[:10]
        prices = m.get('outcomePrices', '[]')
        print(f"\n- {question[:60]}...")
        print(f"  Volume: ${volume:,.0f} | Ends: {end_date} | Prices: {prices}")
else:
    print(f'Error: {response.text[:200]}')
