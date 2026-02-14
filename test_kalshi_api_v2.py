import requests
import json

api_key = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

# Test the new Kalshi Elections API
try:
    # Try to get events from elections API
    print("Testing Kalshi Elections API...")
    response = requests.get('https://api.elections.kalshi.com/v1/events', headers=headers)
    print(f'Status Code: {response.status_code}')
    print(f'Response Headers: {dict(response.headers)}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Number of events: {len(data.get("events", []))}')
        print('First event sample:')
        if data.get('events'):
            event = data['events'][0]
            print(f"  Event ID: {event.get('id')}")
            print(f"  Title: {event.get('title')}")
            print(f"  Status: {event.get('status')}")
            print(f"  Category: {event.get('category')}")
            print(f"  Markets Count: {len(event.get('markets', []))}")
    else:
        print(f'Error: {response.text}')
        
    # Try to get markets directly
    print("\n\nTrying to get markets directly...")
    response = requests.get('https://api.elections.kalshi.com/v1/markets', headers=headers, params={'limit': 10})
    print(f'Markets Status Code: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Number of markets: {len(data.get("markets", []))}')
        if data.get('markets'):
            market = data['markets'][0]
            print(f"  Market ID: {market.get('id')}")
            print(f"  Ticker: {market.get('ticker')}")
            print(f"  Title: {market.get('title')}")
            print(f"  Yes Price: {market.get('yes_price')}")
            print(f"  No Price: {market.get('no_price')}")
            print(f"  Volume: {market.get('volume')}")
            print(f"  Status: {market.get('status')}")
            print(f"  Resolution: {market.get('resolution')}")
            print(f"  Close Date: {market.get('close_date')}")
except Exception as e:
    print(f'Exception: {e}')
    import traceback
    traceback.print_exc()