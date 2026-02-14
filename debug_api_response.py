import requests
import json

api_key = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

# Get raw response
response = requests.get('https://api.elections.kalshi.com/v1/events', headers=headers, params={'limit': 5})
print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")

# Save raw response
data = response.json()
with open('raw_kalshi_response.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\nSaved raw response to raw_kalshi_response.json")

# Let's examine the first event structure
if data.get('events'):
    first_event = data['events'][0]
    print(f"\nFirst event keys: {list(first_event.keys())}")
    
    if 'markets' in first_event and first_event['markets']:
        first_market = first_event['markets'][0]
        print(f"\nFirst market keys: {list(first_market.keys())}")
        print(f"\nFirst market data:")
        for key, value in first_market.items():
            print(f"  {key}: {value}")