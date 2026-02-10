import requests
import json
import os

# Set encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Get markets with prices
def get_market_by_keyword(keywords):
    url = 'https://gamma-api.polymarket.com/events'
    params = {'active': 'true', 'closed': 'false', 'limit': 200}
    resp = requests.get(url, params=params, timeout=15)
    events = resp.json()
    
    matches = []
    for event in events:
        title = event.get('title', '').lower()
        if all(k in title for k in keywords):
            matches.append(event)
    return matches

# Specific markets we track
markets_to_check = [
    ('Trump deport less than 250000', ['trump', 'deport', '250']),
    ('Trump deport 750000 or more', ['trump', 'deport', '750']),
    ('Elon DOGE cut less than 50B', ['elon', '50b']),
    ('Elon DOGE cut more than 250B', ['elon', '250b']),
    ('MicroStrategy 500K BTC', ['microstrategy', '500k']),
]

print("=== HIGH-CONVICTION MARKET PRICES ===\n")

for name, keywords in markets_to_check:
    try:
        events = get_market_by_keyword(keywords)
        if events:
            event = events[0]
            print(f"MARKET: {name}")
            print(f"  Title: {event.get('title', 'N/A')}")
            print(f"  Volume 24h: ${float(event.get('volume24hr', 0) or 0):,.0f}")
            print(f"  Liquidity: ${float(event.get('liquidity', 0) or 0):,.0f}")
            
            # Get market prices if available
            markets = event.get('markets', [])
            if markets:
                for m in markets:
                    outcome = m.get('outcome', 'N/A')
                    price = float(m.get('price', 0) or 0) * 100
                    print(f"  {outcome}: {price:.1f}c")
            print()
        else:
            print(f"NOT FOUND: {name}\n")
    except Exception as e:
        print(f"ERROR: {name} - {e}\n")

print("=== MARKET HEALTH CHECK ===")
print("Comparing to 11:31 AM baseline...")
