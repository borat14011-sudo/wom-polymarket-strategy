#!/usr/bin/env python3
"""Scan Kalshi for NBA games tonight."""

import os
import requests
import json
from datetime import datetime, timedelta

# Set credentials
os.environ['KALSHI_API_KEY_ID'] = '14a525cf-42d7-4746-8e36-30a8d9c17c96'

BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'
API_KEY_ID = os.environ['KALSHI_API_KEY_ID']

print("=" * 70)
print("KALSHI NBA GAMES SCANNER - Feb 13, 2026")
print("=" * 70)

# Get all markets
try:
    print("\n[1] Fetching all markets...")
    response = requests.get(f'{BASE_URL}/markets', params={'limit': 200, 'status': 'open'}, timeout=30)
    data = response.json()
    markets = data.get('markets', [])
    print(f"  Found {len(markets)} open markets")
    
    # Filter for NBA games
    nba_keywords = ['NBA', 'Lakers', 'Warriors', 'Celtics', 'Bucks', 'Nuggets', 'Knicks', 'Mavericks']
    nba_markets = []
    
    for market in markets:
        title = market.get('title', '').lower()
        ticker = market.get('ticker', '').upper()
        
        # Check for NBA keywords
        if any(keyword.lower() in title for keyword in nba_keywords) or any(keyword in ticker for keyword in nba_keywords):
            nba_markets.append(market)
    
    print(f"\n[2] NBA Games Found: {len(nba_markets)}")
    
    if nba_markets:
        print("\n" + "-" * 70)
        print("NBA GAMES AVAILABLE FOR TRADING:")
        print("-" * 70)
        
        for i, market in enumerate(nba_markets[:10], 1):  # Show top 10
            ticker = market.get('ticker', 'N/A')
            title = market.get('title', 'Unknown')[:60]
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 0)
            volume = market.get('volume', 0)
            
            # Calculate mid-price
            mid_price = (yes_bid + yes_ask) / 2 if yes_bid and yes_ask else 0
            
            print(f"\n{i}. {ticker}")
            print(f"   {title}...")
            print(f"   Price: {yes_bid}c (bid) / {yes_ask}c (ask) | Mid: {mid_price:.1f}c")
            print(f"   Volume: {volume:,} contracts")
            
            # Calculate potential ROI
            if mid_price > 0:
                roi_if_win = ((100 - mid_price) / mid_price) * 100
                print(f"   ROI if win: {roi_if_win:.1f}%")
    else:
        print("\n[WARNING] No NBA games found in current market data")
        print("\nChecking all sports markets...")
        
        # Show all sports markets
        sports_markets = []
        for market in markets:
            title = market.get('title', '').lower()
            if 'basketball' in title or 'nba' in title or 'ncaa' in title:
                sports_markets.append(market)
        
        print(f"\nSports/Basketball Markets: {len(sports_markets)}")
        for i, market in enumerate(sports_markets[:5], 1):
            ticker = market.get('ticker', 'N/A')
            title = market.get('title', 'Unknown')[:50]
            print(f"{i}. {ticker}: {title}...")
    
    # Check for any markets resolving today/tomorrow
    print("\n" + "-" * 70)
    print("MARKETS RESOLVING SOON:")
    print("-" * 70)
    
    soon_markets = []
    for market in markets:
        close_time = market.get('close_time')
        if close_time:
            # Parse timestamp (assuming ISO format)
            try:
                close_date = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                days_until = (close_date - datetime.utcnow()).days
                
                if days_until <= 7:  # Next 7 days
                    soon_markets.append((market, days_until))
            except:
                pass
    
    print(f"\nMarkets resolving in next 7 days: {len(soon_markets)}")
    
    for market, days in sorted(soon_markets, key=lambda x: x[1])[:5]:
        ticker = market.get('ticker', 'N/A')
        title = market.get('title', 'Unknown')[:50]
        yes_bid = market.get('yes_bid', 0)
        yes_ask = market.get('yes_ask', 0)
        
        print(f"\n• {ticker}")
        print(f"  {title}...")
        print(f"  Resolves in: {days} days")
        print(f"  Price: {yes_bid}c / {yes_ask}c")
        
        # Calculate annualized IRR
        if yes_bid > 0 and days > 0:
            mid = (yes_bid + yes_ask) / 2
            roi = (100 - mid) / mid
            annual_irr = (1 + roi) ** (365 / days) - 1
            print(f"  Annualized IRR: {annual_irr:.1%}")

except Exception as e:
    print(f"\n[ERROR] Failed to fetch markets: {e}")

print("\n" + "=" * 70)
print("RECOMMENDED ACTION:")
print("=" * 70)
print("1. If NBA games found: Use 'Buy the Dip' strategy")
print("2. Target prices: 30-70¢ range for best risk/reward")
print("3. Position size: $2-5 per trade (2-5% of $100 capital)")
print("4. Focus on markets with volume >10,000 contracts")
print("\nREADY TO EXECUTE TRADES! 🚀")