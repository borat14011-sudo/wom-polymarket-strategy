"""Test CLOB prices-history API with correct parameters"""
import sys
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import requests
import json
from datetime import datetime, timezone

print("=== Testing CLOB prices-history API (CORRECT METHOD) ===\n")

# Step 1: Get a market with token IDs
print("1. Fetching a sample market...")
response = requests.get("https://gamma-api.polymarket.com/markets", params={
    "limit": 20,
    "closed": "true"
})

markets = response.json()
print(f"   Got {len(markets)} markets")

# Find one with token IDs
test_market = None
for market in markets:
    clob_ids = market.get('clobTokenIds', '[]')
    if clob_ids and clob_ids != '[]':
        try:
            token_ids = json.loads(clob_ids)
            if token_ids and len(token_ids) > 0:
                test_market = market
                break
        except:
            continue

if not test_market:
    print("   ERROR: No markets with token IDs found")
    sys.exit(1)

print(f"   Testing with: {test_market.get('question', 'Unknown')[:60]}")

# Step 2: Extract token ID and date range
token_ids = json.loads(test_market.get('clobTokenIds', '[]'))
token_id = token_ids[0] if token_ids else None

if not token_id:
    print("   ERROR: No token ID")
    sys.exit(1)

print(f"   Token ID: {token_id}")

# Get market date range
start_date_str = test_market.get('startDate') or test_market.get('createdAt')
end_date_str = test_market.get('endDate') or test_market.get('closedTime')

print(f"   Market dates: {start_date_str} to {end_date_str}")

# Convert to timestamps
try:
    start_dt = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
    
    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())
    
    print(f"   Timestamps: {start_ts} to {end_ts}")
except Exception as e:
    print(f"   ERROR parsing dates: {e}")
    # Use a fixed recent range instead
    end_ts = int(datetime.now(timezone.utc).timestamp())
    start_ts = end_ts - (7 * 24 * 60 * 60)  # 7 days ago
    print(f"   Using fallback: {start_ts} to {end_ts}")

# Step 3: Test CLOB prices-history API
print("\n2. Testing CLOB prices-history API...")

url = "https://clob.polymarket.com/prices-history"
params = {
    'market': token_id,
    'startTs': start_ts,
    'endTs': end_ts,
    'fidelity': 60  # 60-minute intervals
}

print(f"   URL: {url}")
print(f"   Params: {json.dumps(params, indent=6)}")

try:
    response = requests.get(url, params=params, timeout=10)
    print(f"\n   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   [SUCCESS!] Got price history data")
        
        # Check structure
        if isinstance(data, dict):
            print(f"   Response keys: {list(data.keys())}")
            history = data.get('history', [])
        else:
            history = data
        
        print(f"   Price points: {len(history)}")
        
        if history:
            print(f"\n   Sample data points:")
            for i, point in enumerate(history[:5]):
                print(f"     {i+1}. {point}")
            
            if len(history) > 5:
                print(f"     ... ({len(history) - 5} more points)")
        
        # Calculate what we can get
        total_points = len(history)
        if total_points > 0:
            time_span_days = (end_ts - start_ts) / (24 * 60 * 60)
            points_per_day = total_points / time_span_days if time_span_days > 0 else 0
            
            print(f"\n   Analysis:")
            print(f"     Time span: {time_span_days:.1f} days")
            print(f"     Data points: {total_points}")
            print(f"     Points/day: {points_per_day:.1f}")
            print(f"     Fidelity: {60} minutes ({60/60:.1f} hour)")
    else:
        print(f"   [FAILED] Status: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Step 4: Test with different fidelities
print("\n3. Testing different fidelities...")

fidelities = [5, 15, 60, 360]  # 5min, 15min, 1hr, 6hr

for fidelity in fidelities:
    params['fidelity'] = fidelity
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            history = data.get('history', []) if isinstance(data, dict) else data
            print(f"   Fidelity {fidelity:3d} min: {len(history):4d} points")
        else:
            print(f"   Fidelity {fidelity:3d} min: FAILED ({resp.status_code})")
    except Exception as e:
        print(f"   Fidelity {fidelity:3d} min: ERROR ({str(e)[:30]})")

print("\n" + "="*70)
print("CONCLUSION:")
print("="*70)
if response.status_code == 200 and total_points > 0:
    print("[SUCCESS] Historical price data IS available via CLOB API!")
    print("We CAN build the 2-year historical collector!")
else:
    print("[PARTIAL] API exists but may have limitations for old markets")
    print("Need to test with more recent, active markets")
