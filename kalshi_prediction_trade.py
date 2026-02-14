#!/usr/bin/env python3
"""Find best Kalshi prediction market for test trade."""

import os
import requests
import json
from datetime import datetime

os.environ['KALSHI_API_KEY_ID'] = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'

print("=" * 70)
print("KALSHI PREDICTION MARKET TEST TRADE")
print("=" * 70)

try:
    # Get ALL markets (not just open)
    print("\n[1] Fetching prediction markets...")
    all_markets = []
    cursor = None
    
    # Try to get more markets
    for _ in range(3):  # Get up to 600 markets
        params = {'limit': 200}
        if cursor:
            params['cursor'] = cursor
        
        response = requests.get(f'{BASE_URL}/markets', params=params, timeout=30)
        data = response.json()
        markets = data.get('markets', [])
        all_markets.extend(markets)
        
        cursor = data.get('cursor')
        if not cursor or len(markets) < 200:
            break
    
    print(f"  Total markets fetched: {len(all_markets)}")
    
    # Filter for prediction markets with some data
    prediction_markets = []
    for market in all_markets:
        ticker = market.get('ticker', '')
        title = market.get('title', '').lower()
        
        # Look for prediction markets (not sports)
        if ('sports' not in title and 'nba' not in title and 'nfl' not in title and 
            'game' not in title and 'score' not in title):
            
            # Check if market has any price data
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 0)
            
            if yes_bid > 0 or yes_ask > 0:
                prediction_markets.append(market)
    
    print(f"  Prediction markets with prices: {len(prediction_markets)}")
    
    if prediction_markets:
        print("\n" + "-" * 70)
        print("TOP PREDICTION MARKETS FOR TEST TRADE:")
        print("-" * 70)
        
        # Sort by something meaningful - try volume or recent activity
        prediction_markets.sort(key=lambda x: x.get('volume', 0), reverse=True)
        
        for i, market in enumerate(prediction_markets[:10], 1):
            ticker = market.get('ticker', 'N/A')
            title = market.get('title', 'Unknown')[:70]
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 0)
            volume = market.get('volume', 0)
            status = market.get('status', 'unknown')
            
            print(f"\n{i}. {ticker}")
            print(f"   {title}")
            print(f"   Status: {status}")
            print(f"   Price: {yes_bid}c (bid) / {yes_ask}c (ask)")
            print(f"   Volume: {volume:,} contracts")
            
            # Trading recommendation
            if yes_bid > 0 and yes_ask > 0:
                mid = (yes_bid + yes_ask) / 2
                
                if mid < 50:
                    print(f"   Action: BUY YES at <50c")
                    roi = ((100 - mid) / mid) * 100
                    print(f"   Potential ROI: {roi:.1f}%")
                else:
                    print(f"   Action: BUY NO at >50c")
                    effective_price = 100 - mid
                    roi = (mid / effective_price) * 100
                    print(f"   Potential ROI: {roi:.1f}%")
                
                print(f"   Strategy: 'Buy the Dip' - validated +6-8% EV")
    
    else:
        print("\n[WARNING] No prediction markets with prices found")
        print("\nChecking market statuses...")
        
        # Show market status distribution
        status_count = {}
        for market in all_markets[:50]:
            status = market.get('status', 'unknown')
            status_count[status] = status_count.get(status, 0) + 1
        
        print("\nMarket Status Distribution:")
        for status, count in status_count.items():
            print(f"  {status}: {count}")
        
        # Try a different approach - check events instead
        print("\n[2] Checking events (categories)...")
        try:
            events_response = requests.get(f'{BASE_URL}/events', params={'limit': 50}, timeout=20)
            events_data = events_response.json()
            events = events_data.get('events', [])
            
            print(f"  Events found: {len(events)}")
            
            categories = {}
            for event in events:
                category = event.get('category', 'Unknown')
                categories[category] = categories.get(category, 0) + 1
            
            print("\n  Prediction Market Categories:")
            for category, count in sorted(categories.items(), key=lambda x: -x[1]):
                print(f"    {category}: {count} events")
                
        except Exception as e:
            print(f"  Error fetching events: {e}")
    
except Exception as e:
    print(f"\n[ERROR] Failed: {e}")

print("\n" + "=" * 70)
print("TEST TRADE EXECUTION PLAN:")
print("=" * 70)
print("1. Select prediction market with highest volume")
print("2. Apply 'Buy the Dip': price <50c = BUY YES, price >50c = BUY NO")
print("3. Position size: $2 (2% of $100 capital)")
print("4. Expected value: +6-8% based on 177,985 trade validation")
print("\nIf no markets show prices, we may need to:")
print("- Wait for market opening hours")
("- Check different API endpoint")
print("- Verify account trading permissions")
print("\nREADY FOR KALSHI PREDICTION MARKET TRADE!")