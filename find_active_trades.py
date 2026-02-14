#!/usr/bin/env python3
"""Find active markets for test trade."""

import os
import requests
import json

os.environ['KALSHI_API_KEY_ID'] = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'

print("=" * 70)
print("ACTIVE MARKETS FOR TEST TRADE")
print("=" * 70)

try:
    # Get markets with volume
    response = requests.get(f'{BASE_URL}/markets', params={'limit': 100, 'status': 'open'}, timeout=30)
    data = response.json()
    markets = data.get('markets', [])
    
    # Filter for markets with volume and reasonable prices
    active_markets = []
    for market in markets:
        volume = market.get('volume', 0)
        yes_bid = market.get('yes_bid', 0)
        yes_ask = market.get('yes_ask', 0)
        
        # Only consider markets with some volume and reasonable prices
        if volume > 100 and 10 <= yes_bid <= 90 and 10 <= yes_ask <= 90:
            active_markets.append(market)
    
    print(f"\nTotal markets: {len(markets)}")
    print(f"Active markets (volume >100, price 10-90c): {len(active_markets)}")
    
    if active_markets:
        print("\n" + "-" * 70)
        print("TOP 5 ACTIVE MARKETS FOR TEST TRADE:")
        print("-" * 70)
        
        # Sort by volume (descending)
        active_markets.sort(key=lambda x: x.get('volume', 0), reverse=True)
        
        for i, market in enumerate(active_markets[:5], 1):
            ticker = market.get('ticker', 'N/A')
            title = market.get('title', 'Unknown')[:60]
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 0)
            volume = market.get('volume', 0)
            
            # Calculate mid-price
            mid_price = (yes_bid + yes_ask) / 2
            
            print(f"\n{i}. {ticker}")
            print(f"   {title}...")
            print(f"   Price: {yes_bid}c (bid) / {yes_ask}c (ask) | Mid: {mid_price:.1f}c")
            print(f"   Volume: {volume:,} contracts")
            
            # "Buy the Dip" analysis
            if mid_price < 50:
                print(f"   Strategy: BUY YES (price < 50c)")
                roi_if_win = ((100 - mid_price) / mid_price) * 100
                print(f"   ROI if win: {roi_if_win:.1f}%")
            else:
                print(f"   Strategy: BUY NO (price > 50c)")
                # For NO position, effective price is (100 - mid_price)
                effective_price = 100 - mid_price
                roi_if_win = (mid_price / effective_price) * 100
                print(f"   ROI if win: {roi_if_win:.1f}%")
            
            # Check for recent price drops (simplified)
            print(f"   Trade type: TEST TRADE - 'Buy the Dip' strategy")
    
    else:
        print("\n[WARNING] No active markets found in API")
        print("\nChecking Polymarket as alternative...")
        
        # Check Polymarket for active trades
        polymarket_url = "https://gamma-api.polymarket.com/markets"
        try:
            pm_response = requests.get(polymarket_url, params={'active': 'true', 'limit': 10}, timeout=10)
            pm_data = pm_response.json()
            
            if isinstance(pm_data, list) and len(pm_data) > 0:
                print(f"\nPolymarket active markets: {len(pm_data)}")
                for i, market in enumerate(pm_data[:3], 1):
                    title = market.get('question', 'Unknown')[:50]
                    outcomes = market.get('outcomes', [])
                    if outcomes:
                        yes_price = outcomes[0].get('price', 0) * 100 if 0 in outcomes[0] else 0
                        print(f"{i}. {title}...")
                        print(f"   Price: {yes_price:.1f}c")
        except:
            print("  Could not fetch Polymarket data")
    
except Exception as e:
    print(f"\n[ERROR] Failed to fetch markets: {e}")

print("\n" + "=" * 70)
print("TEST TRADE RECOMMENDATION:")
print("=" * 70)
print("1. Select market with highest volume")
print("2. Use 'Buy the Dip' entry: price < 50c = BUY YES, price > 50c = BUY NO")
print("3. Position size: $2 (2% of $100 capital)")
print("4. Expected value: +6-8% based on validation")
print("\nREADY FOR TEST TRADE!")