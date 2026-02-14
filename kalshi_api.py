import requests
import json

api_key = "14a525cf-42d7-4746-8e36-30a8d9c17c96"
headers = {
    "Authorization": f"Bearer {api_key}"
}

# Try different API endpoints
endpoints = [
    "https://api.kalshi.com/v1/markets",
    "https://api.kalshi.com/trade-api/v2/markets",
    "https://api.kalshi.com/trade-api/v1/markets"
]

for endpoint in endpoints:
    print(f"Trying endpoint: {endpoint}")
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            data = response.json()
            print(f"Number of markets: {len(data.get('markets', []))}")
            # Print first market as sample
            if data.get('markets'):
                print("\nSample market:")
                print(json.dumps(data['markets'][0], indent=2))
            break
        else:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)