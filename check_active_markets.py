import requests
import json
from datetime import datetime, timezone

api_key = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
headers = {'Authorization': f'Bearer {api_key}'}
base_url = "https://api.elections.kalshi.com/trade-api/v2"

# Get more markets with different parameters
print("Testing different API parameters...")

# Try to get markets with volume
params = {
    'limit': 50,
    'status': 'active',
    'order_by': 'volume',
    'order_dir': 'desc'
}

response = requests.get(f"{base_url}/markets", headers=headers, params=params, timeout=30)
data = response.json()

markets = data.get('markets', [])
print(f"\nGot {len(markets)} markets ordered by volume")

if markets:
    # Find markets with non-zero volume
    markets_with_volume = [m for m in markets if m.get('volume', 0) > 0]
    print(f"Markets with volume > 0: {len(markets_with_volume)}")
    
    if markets_with_volume:
        print("\n=== Top 5 Markets by Volume ===")
        for i, market in enumerate(markets_with_volume[:5]):
            print(f"\n{i+1}. {market.get('title', 'No title')[:80]}...")
            print(f"   Ticker: {market.get('ticker')}")
            print(f"   Volume: {market.get('volume', 0):,}")
            print(f"   Status: {market.get('status')}")
            
            yes_ask = market.get('yes_ask')
            yes_bid = market.get('yes_bid')
            no_ask = market.get('no_ask')
            no_bid = market.get('no_bid')
            
            if yes_ask is not None and yes_bid is not None:
                print(f"   Yes: Bid={yes_bid}¢, Ask={yes_ask}¢")
            if no_ask is not None and no_bid is not None:
                print(f"   No: Bid={no_bid}¢, Ask={no_ask}¢")
            
            close_time = market.get('close_time')
            if close_time:
                try:
                    close_date = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                    today = datetime.now(timezone.utc).replace(tzinfo=None)
                    days_to_close = (close_date - today).days
                    print(f"   Close: {close_date.strftime('%Y-%m-%d')} ({days_to_close} days)")
                except:
                    print(f"   Close: {close_time}")
    
    # Check market categories
    print("\n=== Market Categories ===")
    categories = {}
    for market in markets:
        # Try to infer category from ticker
        ticker = market.get('ticker', '')
        if 'KXELON' in ticker:
            cat = 'Elon Musk'
        elif 'KXNEWPOPE' in ticker:
            cat = 'Pope'
        elif 'KXMVE' in ticker:
            cat = 'Sports Multi-Game'
        elif 'KX' in ticker:
            cat = 'Other KX'
        else:
            cat = 'Unknown'
        
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count} markets")
    
    # Check price ranges for markets with bids/asks
    print("\n=== Price Analysis ===")
    markets_with_prices = []
    for market in markets:
        yes_bid = market.get('yes_bid')
        yes_ask = market.get('yes_ask')
        if yes_bid is not None and yes_ask is not None and yes_bid > 0:
            markets_with_prices.append(market)
    
    print(f"Markets with yes bids > 0: {len(markets_with_prices)}")
    
    if markets_with_prices:
        # Sort by mid price
        for market in sorted(markets_with_prices, key=lambda m: m.get('yes_bid', 0), reverse=True)[:5]:
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 0)
            mid_price = (yes_bid + yes_ask) / 2 if yes_ask > yes_bid else yes_bid
            
            print(f"\n  {market.get('title', 'No title')[:60]}...")
            print(f"    Yes: Bid={yes_bid}¢, Ask={yes_ask}¢, Mid={mid_price:.1f}¢")
            print(f"    Volume: {market.get('volume', 0):,}")

# Also try events endpoint
print("\n\n=== Testing Events Endpoint ===")
response = requests.get(f"{base_url}/events?limit=10", headers=headers, timeout=30)
events_data = response.json()
events = events_data.get('events', [])

print(f"Got {len(events)} events")

if events:
    for i, event in enumerate(events[:3]):
        print(f"\n{i+1}. {event.get('title', 'No title')}")
        print(f"   Ticker: {event.get('event_ticker')}")
        print(f"   Category: {event.get('category')}")
        print(f"   Status: {event.get('status')}")
        
        # Get markets for this event
        event_ticker = event.get('event_ticker')
        if event_ticker:
            markets_response = requests.get(
                f"{base_url}/markets", 
                headers=headers, 
                params={'event_ticker': event_ticker, 'limit': 5},
                timeout=30
            )
            event_markets = markets_response.json().get('markets', [])
            print(f"   Markets: {len(event_markets)}")
            
            for market in event_markets[:2]:
                print(f"     - {market.get('title', 'No title')[:50]}...")
                print(f"       Volume: {market.get('volume', 0):,}, Yes bid: {market.get('yes_bid', 'N/A')}¢")