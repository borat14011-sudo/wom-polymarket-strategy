#!/usr/bin/env python3
"""
Test market scanner with lower volume threshold
"""

import sys
import os
sys.path.append('polymarket_bot')

from market_scanner import MarketScanner

print("Testing market scanner with $100 volume threshold...")
scanner = MarketScanner(min_daily_volume=100, scan_limit=50)

opportunities = scanner.scan_opportunities()

if opportunities:
    print(f"\nFound {len(opportunities)} opportunities:")
    for i, opp in enumerate(opportunities[:5]):  # Show top 5
        print(f"\n{i+1}. {opp.question[:80]}...")
        print(f"   Condition ID: {opp.condition_id[:20]}...")
        print(f"   24h Volume: ${opp.volume_24h:,.2f}")
        print(f"   Liquidity Score: {opp.liquidity_score:.2f}")
        if opp.midpoint:
            print(f"   Midpoint Price: {opp.midpoint:.2%}")
else:
    print("\nNo opportunities found even with $100 threshold.")
    print("\nChecking raw market data...")
    
    # Try to fetch raw markets
    import requests
    try:
        response = requests.get("https://gamma-api.polymarket.com/markets", 
                              params={"limit": 20, "closed": False}, 
                              timeout=30)
        markets = response.json()
        print(f"Raw markets fetched: {len(markets)}")
        
        # Show volume distribution
        volumes = [m.get('volume24h', 0) for m in markets]
        print(f"Volume stats: min=${min(volumes):.2f}, max=${max(volumes):.2f}, avg=${sum(volumes)/len(volumes):.2f}")
        
        # Show markets with any volume
        markets_with_volume = [m for m in markets if m.get('volume24h', 0) > 0]
        print(f"Markets with volume > 0: {len(markets_with_volume)}")
        
        for m in markets_with_volume[:3]:
            print(f"\n- {m.get('question', 'No question')[:60]}...")
            print(f"  Volume: ${m.get('volume24h', 0):.2f}")
            print(f"  ID: {m.get('id', 'No ID')}")
            
    except Exception as e:
        print(f"Error fetching markets: {e}")