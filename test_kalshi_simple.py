import requests
import json

API_KEY = "63d25fe0-e138-4d22-9024-0ba4857f7604"

# Test different endpoints
endpoints = [
    "https://trading-api.kalshi.com/trade-api/v2/markets",
    "https://api.kalshi.com/trade-api/v2/markets",
    "https://api.kalshi.co/trade-api/v2/markets",
    "https://api.kalshi.io/trade-api/v2/markets",
    "https://kalshi.com/api/v1/markets",
    "https://www.kalshi.com/api/v1/markets",
]

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}

print("Testing Kalshi API endpoints...")
print("=" * 60)

for url in endpoints:
    print(f"\nTrying: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS! Found {len(data.get('markets', []))} markets")
            if data.get('markets'):
                print(f"First market: {data['markets'][0].get('title', 'No title')}")
            break
        elif response.status_code == 401:
            print("Authentication failed")
        elif response.status_code == 404:
            print("Endpoint not found")
        else:
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("Connection failed (domain doesn't exist)")
    except Exception as e:
        print(f"Error: {str(e)[:100]}")

print("\n" + "=" * 60)
print("If all fail, API might need different authentication method.")
print("Check docs.kalshi.com for correct API usage.")