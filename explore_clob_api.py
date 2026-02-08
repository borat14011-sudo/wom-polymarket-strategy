import requests
import json
from datetime import datetime, timezone
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

print("=== Finding correct CLOB/price history API ===\n")

# Get a recent, active market
response = requests.get("https://gamma-api.polymarket.com/markets", params={
    "limit": 20,
    "active": "true"
})

markets = response.json()
print(f"Fetched {len(markets)} active markets\n")

# Try different API endpoints for price history
for market in markets[:5]:
    question = market.get('question', '')[:60]
    condition_id = market.get('conditionId', '')
    clob_ids = market.get('clobTokenIds', '[]')
    
    print(f"Market: {question}")
    print(f"Condition ID: {condition_id}")
    print(f"CLOB Token IDs: {clob_ids[:100]}")
    
    # Parse token IDs
    try:
        token_ids = json.loads(clob_ids) if clob_ids else []
    except:
        token_ids = []
    
    if token_ids:
        token_id = token_ids[0]
        
        # Try various endpoints
        endpoints_to_try = [
            ("Gamma Events", f"https://gamma-api.polymarket.com/events?id={market.get('id')}"),
            ("Gamma Market", f"https://gamma-api.polymarket.com/markets/{market.get('id')}"),
            ("CLOB Market", f"https://clob.polymarket.com/markets/{condition_id}"),
            ("CLOB Prices", f"https://clob.polymarket.com/prices/{token_id}"),
            ("Data API", f"https://data-api.polymarket.com/markets/{condition_id}"),
            ("Strapi", f"https://strapi-matic.polymarket.com/markets?id={market.get('id')}"),
        ]
        
        for name, url in endpoints_to_try:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"  [OK] {name}: {resp.status_code}")
                    if isinstance(data, dict):
                        print(f"    Keys: {list(data.keys())[:10]}")
                    elif isinstance(data, list) and len(data) > 0:
                        print(f"    List with {len(data)} items, first keys: {list(data[0].keys())[:10] if isinstance(data[0], dict) else 'N/A'}")
                else:
                    print(f"  [FAIL] {name}: {resp.status_code}")
            except Exception as e:
                print(f"  [ERROR] {name}: {str(e)[:50]}")
        
        print()
        break  # Only test first market with token IDs

# Try to find price history in market details
print("\n=== Checking if market detail has price history ===")
try:
    market_id = markets[0].get('id')
    resp = requests.get(f"https://gamma-api.polymarket.com/markets/{market_id}")
    if resp.status_code == 200:
        market_detail = resp.json()
        print("Market detail keys:")
        print(json.dumps(list(market_detail.keys()), indent=2))
        
        # Check for any price-related fields
        price_fields = [k for k in market_detail.keys() if 'price' in k.lower() or 'history' in k.lower()]
        print(f"\nPrice-related fields: {price_fields}")
except Exception as e:
    print(f"Error: {e}")

# Check if there's documentation or alternative endpoints
print("\n=== Trying Polymarket subgraph (The Graph) ===")
try:
    # Polymarket uses The Graph for historical data
    subgraph_url = "https://api.thegraph.com/subgraphs/name/polymarket/matic-markets-5"
    
    query = """
    {
      markets(first: 1, orderBy: creationTimestamp, orderDirection: desc) {
        id
        question
        outcomes
        volume
        liquidity
        creationTimestamp
      }
    }
    """
    
    resp = requests.post(subgraph_url, json={"query": query}, timeout=10)
    print(f"Subgraph status: {resp.status_code}")
    if resp.status_code == 200:
        print("[OK] The Graph API works!")
        data = resp.json()
        print(json.dumps(data, indent=2)[:500])
except Exception as e:
    print(f"Subgraph error: {e}")

# Try alternative data endpoints
print("\n=== Checking GitHub scrapers ===")
print("Will check:")
print("1. apoideas/polymarket-historical-data")
print("2. benjiminii/polymarket-scrape")
