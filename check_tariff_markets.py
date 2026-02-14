#!/usr/bin/env python3
"""Check Kalshi for tariff and stimulus markets."""

import os
import requests
import json

os.environ['KALSHI_API_KEY_ID'] = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'

print("=" * 70)
print("KALSHI TARIFF & STIMULUS MARKETS CHECK")
print("=" * 70)

try:
    # Search for tariff/stimulus markets
    print("\n[1] Searching for tariff/stimulus markets...")
    
    # Get all markets
    all_markets = []
    cursor = None
    
    for _ in range(2):
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
    
    print(f"  Total markets scanned: {len(all_markets)}")
    
    # Search for tariff/stimulus keywords
    tariff_markets = []
    keywords = ['tariff', 'stimulus', 'check', 'revenue', 'trump', 'biden', 'tax', 'payment']
    
    for market in all_markets:
        title = market.get('title', '').lower()
        ticker = market.get('ticker', '').lower()
        
        if any(keyword in title for keyword in keywords) or any(keyword in ticker for keyword in keywords):
            tariff_markets.append(market)
    
    print(f"\n[2] Tariff/Stimulus Markets Found: {len(tariff_markets)}")
    
    if tariff_markets:
        print("\n" + "-" * 70)
        print("TARIFF/STIMULUS MARKETS:")
        print("-" * 70)
        
        for i, market in enumerate(tariff_markets, 1):
            ticker = market.get('ticker', 'N/A')
            title = market.get('title', 'Unknown')
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 0)
            volume = market.get('volume', 0)
            status = market.get('status', 'unknown')
            
            print(f"\n{i}. {ticker}")
            print(f"   {title}")
            print(f"   Status: {status}")
            print(f"   Price: {yes_bid}c (bid) / {yes_ask}c (ask)")
            print(f"   Volume: {volume:,} contracts")
            
            # Trading analysis
            if yes_bid > 0 and yes_ask > 0:
                mid = (yes_bid + yes_ask) / 2
                
                # Hype Fade analysis for stimulus checks
                if 'stimulus' in title.lower() or 'check' in title.lower():
                    print(f"   Strategy: HYPE FADE - Bet NO")
                    print(f"   Market price: {mid}c")
                    print(f"   Our estimate: ~5c (95% chance NO)")
                    print(f"   Edge: {mid - 5:.1f} percentage points")
                    
                    if mid > 20:
                        print(f"   Action: STRONG SELL (Bet NO)")
                        roi_if_no = (mid / (100 - mid)) * 100
                        print(f"   ROI if correct: {roi_if_no:.1f}%")
                    else:
                        print(f"   Action: Wait for price spike >30c")
                
                # Tariff revenue analysis
                elif 'tariff' in title.lower() and 'revenue' in title.lower():
                    print(f"   Strategy: Near-Certainty")
                    print(f"   Market price: {mid}c")
                    print(f"   Our estimate: ~35c (from Polymarket analysis)")
                    
                    if mid < 30:
                        print(f"   Action: BUY YES (undervalued)")
                        roi_if_yes = ((100 - mid) / mid) * 100
                        print(f"   ROI if correct: {roi_if_yes:.1f}%")
                    else:
                        print(f"   Action: Neutral (fairly priced)")
    
    else:
        print("\n[INFO] No tariff/stimulus markets found in current API data")
        print("\nChecking events for tariff categories...")
        
        try:
            events_response = requests.get(f'{BASE_URL}/events', params={'limit': 100}, timeout=20)
            events_data = events_response.json()
            events = events_data.get('events', [])
            
            # Look for political/economic events
            political_events = []
            for event in events:
                category = event.get('category', '')
                title = event.get('title', '').lower()
                
                if 'politics' in category.lower() or 'economics' in category.lower() or 'policy' in category.lower():
                    political_events.append(event)
            
            print(f"\nPolitical/Economic Events: {len(political_events)}")
            for i, event in enumerate(political_events[:5], 1):
                event_title = event.get('title', 'Unknown')[:80]
                category = event.get('category', 'Unknown')
                print(f"{i}. {category}: {event_title}...")
                
        except Exception as e:
            print(f"  Error checking events: {e}")
    
    # Check if we need to search Polymarket instead
    print("\n" + "-" * 70)
    print("MEMORY CHECK - From our analysis:")
    print("-" * 70)
    print("1. Tariff $200-500B revenue market: YES at 11% (Polymarket)")
    print("2. Stimulus checks market: NO at ~32% (Hype Fade)")
    print("3. These might be on Polymarket, not Kalshi")
    
    print("\n[3] Recommendation:")
    print("- If tariff/stimulus markets exist on Kalshi: Execute Hype Fade")
    print("- If not on Kalshi: Use college basketball market for test trade")
    print("- Or: Check Polymarket for ready-to-go tariff trade")
    
except Exception as e:
    print(f"\n[ERROR] Failed: {e}")

print("\n" + "=" * 70)
print("ACTION PLAN:")
print("=" * 70)
print("1. Check Kalshi website for 'tariff stimulus checks' market")
print("2. If exists: Bet NO at >30c price (Hype Fade)")
print("3. If not: Use college basketball market for Kalshi test trade")
print("4. Polymarket tariff trade still available (400% ROI)")
print("\nWhat's your preference?")