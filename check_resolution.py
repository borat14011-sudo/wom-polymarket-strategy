import requests

# Try to find if there's a resolved outcome
# Check the market events/history
market_id = "555793"

# Try different endpoints to find resolution data
endpoints = [
    f"https://gamma-api.polymarket.com/markets/{market_id}",
    f"https://clob.polymarket.com/markets/{market_id}",
]

for url in endpoints:
    print(f"\nTrying: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Keys: {list(data.keys())[:15]}")
            if 'outcome' in data and data['outcome']:
                print(f"OUTCOME: {data['outcome']}")
            if 'resolved' in data:
                print(f"RESOLVED: {data['resolved']}")
            if 'resolutionData' in data:
                print(f"RESOLUTION DATA: {data['resolutionData']}")
    except Exception as e:
        print(f"Error: {e}")
