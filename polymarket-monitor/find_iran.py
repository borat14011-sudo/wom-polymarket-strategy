import requests

# Try different API endpoints
print("Testing Polymarket Gamma API endpoints...")
print("=" * 60)

# Try with search query
try:
    response = requests.get(
        'https://gamma-api.polymarket.com/markets',
        params={'q': 'iran', 'limit': 50},
        timeout=10
    )
    print(f"\n1. Search 'iran': Status {response.status_code}")
    if response.ok:
        markets = response.json()
        print(f"   Found {len(markets)} results")
        for m in markets[:5]:
            print(f"   - {m.get('question', 'Unknown')[:60]}")
except Exception as e:
    print(f"   ERROR: {e}")

# Try getting all active markets with higher limit
try:
    response = requests.get(
        'https://gamma-api.polymarket.com/markets',
        params={'active': 'true', 'limit': 200},
        timeout=10
    )
    print(f"\n2. Active markets (limit 200): Status {response.status_code}")
    if response.ok:
        markets = response.json()
        print(f"   Found {len(markets)} total markets")
        
        # Search for Iran in results
        iran_markets = [m for m in markets if 'iran' in m.get('question', '').lower()]
        print(f"   Iran markets found: {len(iran_markets)}")
        for m in iran_markets[:10]:
            print(f"   - {m.get('question')}")
except Exception as e:
    print(f"   ERROR: {e}")

# Try the CLOB API instead
try:
    response = requests.get(
        'https://clob.polymarket.com/markets',
        params={'active': 'true'},
        timeout=10
    )
    print(f"\n3. CLOB API: Status {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   Response type: {type(data)}")
        if isinstance(data, list):
            print(f"   Found {len(data)} markets")
        else:
            print(f"   Response keys: {data.keys() if hasattr(data, 'keys') else 'N/A'}")
except Exception as e:
    print(f"   ERROR: {e}")

print("=" * 60)
