import requests
import json
import sys

def fetch_all_markets():
    api_key = "14a525cf-42d7-4746-8e36-30a8d9c17c96"
    base_url = "https://api.kalshi.com/trade-api/v2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    all_markets = []
    cursor = None
    limit = 100
    
    try:
        while True:
            url = f"{base_url}/markets?limit={limit}"
            if cursor:
                url += f"&cursor={cursor}"
            
            print(f"Fetching markets with cursor: {cursor}")
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.text)
                break
                
            data = response.json()
            markets = data.get("markets", [])
            all_markets.extend(markets)
            
            cursor = data.get("cursor")
            if not cursor or len(markets) < limit:
                break
                
        print(f"Total markets fetched: {len(all_markets)}")
        return all_markets
        
    except Exception as e:
        print(f"Exception: {e}")
        return None

if __name__ == "__main__":
    markets = fetch_all_markets()
    if markets:
        with open("markets.json", "w") as f:
            json.dump(markets, f, indent=2)
        print("Markets saved to markets.json")
        
        # Print first few markets for verification
        print("\nFirst 3 markets:")
        for i, market in enumerate(markets[:3]):
            print(f"{i+1}. {market.get('ticker')}: {market.get('title')}")
            print(f"   Yes: {market.get('yes_price')}, No: {market.get('no_price')}")
            print()