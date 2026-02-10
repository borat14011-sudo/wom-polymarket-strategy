#!/usr/bin/env python3
"""
Quick Elon Market Scanner
Finds Elon-related prediction markets
"""

import requests
import json

# Search terms for Elon markets
search_terms = ['elon', 'musk', 'twitter', 'tweet', 'x.com', 'dogecoin', 'doge']

base_url = "https://gamma-api.polymarket.com"

print("=" * 60)
print("ELON MUSK MARKET SCANNER")
print("=" * 60)

all_markets = []

for term in search_terms:
    try:
        response = requests.get(
            f"{base_url}/markets",
            params={
                "active": True,
                "closed": False,
                "search": term,
                "limit": 50
            },
            timeout=30
        )
        
        markets = response.json()
        print(f"\n[Search: '{term}'] Found {len(markets)} markets")
        
        for market in markets:
            question = market.get('question', '').lower()
            # Filter for Elon-specific
            if any(x in question for x in ['elon', 'musk', 'twitter', 'tweet', 'x.com']):
                all_markets.append(market)
                
    except Exception as e:
        print(f"Error searching '{term}': {e}")

# Remove duplicates
seen = set()
unique_markets = []
for m in all_markets:
    mid = m.get('id', m.get('conditionId', ''))
    if mid and mid not in seen:
        seen.add(mid)
        unique_markets.append(m)

print(f"\n{'='*60}")
print(f"FOUND {len(unique_markets)} UNIQUE ELON MARKETS")
print(f"{'='*60}\n")

# Sort by volume
unique_markets.sort(key=lambda x: float(x.get('volume', 0)), reverse=True)

# Display top markets
for i, market in enumerate(unique_markets[:15], 1):
    question = market.get('question', 'Unknown')
    volume = float(market.get('volume', 0))
    best_bid = float(market.get('bestBid', 0))
    best_ask = float(market.get('bestAsk', 0))
    end_date = market.get('endDate', 'Unknown')[:10]
    
    print(f"{i}. {question[:70]}")
    print(f"   Volume: ${volume:,.0f} | Bid: {best_bid:.2f}¢ | Ask: {best_ask:.2f}¢")
    print(f"   Ends: {end_date}")
    
    slug = market.get('marketSlug', market.get('slug', ''))
    if slug:
        print(f"   Link: https://polymarket.com/event/{slug}")
    print()

# Save to file
with open('ELON_MARKETS_FOUND.json', 'w') as f:
    json.dump(unique_markets, f, indent=2)

print(f"Saved {len(unique_markets)} markets to ELON_MARKETS_FOUND.json")
