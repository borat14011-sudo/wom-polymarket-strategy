import requests
import json
from datetime import datetime, timedelta

print("=== Exploring date filtering for Feb 2024 - Feb 2026 ===\n")

# Test different date parameters
params_to_test = [
    {"limit": 5, "active": "false"},
    {"limit": 5, "closed": "true"},
    {"limit": 5, "end_date_min": "2024-02-01"},
    {"limit": 5, "start_date_min": "2024-02-01"},
]

for params in params_to_test:
    try:
        response = requests.get("https://gamma-api.polymarket.com/markets", params=params, timeout=10)
        print(f"Testing params: {params}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            markets = response.json()
            print(f"Markets returned: {len(markets)}")
            if markets:
                m = markets[0]
                print(f"  Sample: {m.get('question', 'N/A')[:80]}")
                print(f"  Created: {m.get('createdAt', 'N/A')}")
                print(f"  End Date: {m.get('endDate', 'N/A')}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")

# Try to get recent markets
print("\n=== Getting recent markets (2024+) ===")
try:
    # Get all markets, will need to filter client-side
    offset = 0
    limit = 100
    markets_2024_plus = []
    
    target_start = datetime(2024, 2, 1)
    
    for page in range(3):  # Just test 3 pages
        response = requests.get(
            "https://gamma-api.polymarket.com/markets",
            params={"limit": limit, "offset": offset, "closed": "true"},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Error fetching page {page}: {response.status_code}")
            break
            
        markets = response.json()
        if not markets:
            break
            
        for m in markets:
            created = m.get('createdAt')
            if created:
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                if created_dt >= target_start:
                    markets_2024_plus.append({
                        'id': m.get('id'),
                        'question': m.get('question', '')[:60],
                        'created': created,
                        'endDate': m.get('endDate'),
                        'category': m.get('category'),
                        'volume': m.get('volumeNum', 0),
                        'clobTokenIds': m.get('clobTokenIds')
                    })
        
        offset += limit
        print(f"Processed page {page+1}, found {len(markets_2024_plus)} markets from Feb 2024+")
    
    print(f"\nTotal markets found from Feb 2024+: {len(markets_2024_plus)}")
    if markets_2024_plus:
        print("\nSample markets:")
        for m in markets_2024_plus[:3]:
            print(f"  - {m['question']} (created: {m['created'][:10]})")

except Exception as e:
    print(f"Error: {e}")

# Test CLOB price history endpoint
print("\n=== Testing CLOB price history ===")
try:
    # Get a recent market with clobTokenIds
    response = requests.get("https://gamma-api.polymarket.com/markets?limit=50")
    markets = response.json()
    
    for market in markets:
        clob_ids = market.get('clobTokenIds')
        if clob_ids and clob_ids != '[]':
            try:
                token_ids = json.loads(clob_ids)
                if token_ids:
                    token_id = token_ids[0]
                    print(f"\nTesting market: {market.get('question', '')[:60]}")
                    print(f"Token ID: {token_id}")
                    
                    # Try different CLOB endpoints
                    endpoints = [
                        f"https://clob.polymarket.com/prices-history?market={token_id}",
                        f"https://clob.polymarket.com/prices-history?token_id={token_id}",
                        f"https://data-api.polymarket.com/prices/{token_id}",
                    ]
                    
                    for url in endpoints:
                        try:
                            resp = requests.get(url, timeout=5)
                            print(f"  {url.split('polymarket.com')[1][:40]}: {resp.status_code}")
                            if resp.status_code == 200:
                                data = resp.json()
                                print(f"    Response keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
                                print(f"    Data sample: {str(data)[:200]}")
                        except Exception as e:
                            print(f"    Error: {e}")
                    
                    break  # Only test one market
            except:
                continue

except Exception as e:
    print(f"Error: {e}")
