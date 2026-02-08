import requests
import json

# Fetch all markets
r = requests.get('https://gamma-api.polymarket.com/markets')
markets = r.json()

# Find markets with "US" and related to Feb 13
target_markets = [m for m in markets if ('US' in m.get('question', '') or 'strike' in m.get('question', '').lower()) and 'February 13' in m.get('question', '')]

if target_markets:
    for m in target_markets[:3]:
        print(f"Question: {m.get('question')}")
        print(f"Prices: {m.get('outcome_prices')}")
        print(f"Volume 24h: ${m.get('volume_24hr', 0):,.0f}")
        print("---")
else:
    # Try broader search
    print("Searching all active markets...")
    active = [m for m in markets if m.get('active') == True]
    print(f"Total active markets: {len(active)}")
    
    # Check if Iran market might be closed/resolved
    print("\nSearching closed markets with 'Iran' or 'strike'...")
    closed = [m for m in markets if 'Iran' in m.get('question', '') or 'strike' in m.get('question', '').lower()]
    for m in closed[:5]:
        print(f"Question: {m.get('question')}")
        print(f"Active: {m.get('active')}")
        print(f"Closed: {m.get('closed', 'unknown')}")
        print("---")
