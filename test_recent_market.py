"""Test with a more recent market and shorter intervals"""
import sys
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import requests
import json
from datetime import datetime, timezone, timedelta

print("=== Testing CLOB API with Recent Markets ===\n")

# Get recent active markets (more likely to have data)
print("1. Fetching recent active markets...")
response = requests.get("https://gamma-api.polymarket.com/markets", params={
    "limit": 50,
    "active": "true"
})

markets = response.json()
print(f"   Got {len(markets)} active markets")

# Find one created recently with token IDs
test_market = None
for market in markets:
    clob_ids = market.get('clobTokenIds', '[]')
    created = market.get('createdAt', '')
    
    if clob_ids and clob_ids != '[]' and '2024' in created or '2025' in created or '2026' in created:
        try:
            token_ids = json.loads(clob_ids)
            if token_ids and len(token_ids) > 0:
                test_market = market
                break
        except:
            continue

if not test_market:
    print("   No recent markets found, using any market...")
    for market in markets:
        clob_ids = market.get('clobTokenIds', '[]')
        if clob_ids and clob_ids != '[]':
            try:
                token_ids = json.loads(clob_ids)
                if token_ids:
                    test_market = market
                    break
            except:
                continue

if not test_market:
    print("   ERROR: No suitable markets found")
    sys.exit(1)

print(f"   Testing: {test_market.get('question', 'Unknown')[:70]}")
print(f"   Created: {test_market.get('createdAt')}")
print(f"   End Date: {test_market.get('endDate')}")

# Get token ID
token_ids = json.loads(test_market.get('clobTokenIds', '[]'))
token_id = token_ids[0]
print(f"   Token ID: {token_id}")

# Test various time ranges
print("\n2. Testing different time ranges...")

test_cases = [
    ("Last 24 hours", 1),
    ("Last 3 days", 3),
    ("Last 7 days", 7),
    ("Last 14 days", 14),
    ("Last 30 days", 30),
]

url = "https://clob.polymarket.com/prices-history"

for label, days_back in test_cases:
    end_ts = int(datetime.now(timezone.utc).timestamp())
    start_ts = end_ts - (days_back * 24 * 60 * 60)
    
    params = {
        'market': token_id,
        'startTs': start_ts,
        'endTs': end_ts,
        'fidelity': 60  # 60 minutes
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            history = data.get('history', []) if isinstance(data, dict) else data
            print(f"   {label:15s}: [OK] {len(history):4d} points")
            
            if history and label == "Last 7 days":
                # Show sample data for 7-day test
                print(f"      Sample points:")
                for point in history[:3]:
                    print(f"        {point}")
        else:
            error_msg = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text
            print(f"   {label:15s}: [FAIL] {resp.status_code} - {str(error_msg)[:60]}")
    except Exception as e:
        print(f"   {label:15s}: [ERROR] {str(e)[:50]}")

# Test maximum interval that works
print("\n3. Finding maximum interval that works...")
print("   Binary search for max days...")

low, high = 1, 730  # 1 day to 2 years
max_working_days = 0

while low <= high:
    mid = (low + high) // 2
    end_ts = int(datetime.now(timezone.utc).timestamp())
    start_ts = end_ts - (mid * 24 * 60 * 60)
    
    params = {
        'market': token_id,
        'startTs': start_ts,
        'endTs': end_ts,
        'fidelity': 360  # Use 6-hour intervals for longer periods
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            max_working_days = mid
            low = mid + 1
            print(f"   {mid:3d} days: OK", end='\r', flush=True)
        else:
            high = mid - 1
    except:
        high = mid - 1

print(f"\n   Maximum working interval: ~{max_working_days} days")

print("\n" + "="*70)
print("ASSESSMENT:")
print("="*70)
if max_working_days > 0:
    print(f"[PARTIAL SUCCESS] Can get up to ~{max_working_days} days of history")
    print(f"This means:")
    if max_working_days >= 730:
        print("  [OK] Can get 2 years of data!")
    elif max_working_days >= 365:
        print("  [OK] Can get 1 year, need to fetch 2-year data in chunks")
    elif max_working_days >= 30:
        print("  [LIMITED] Can get ~1 month at a time, need many API calls")
    else:
        print("  [VERY LIMITED] Can only get recent data")
    
    print(f"\nFor 2-year collection (730 days):")
    chunks_needed = (730 // max_working_days) + 1 if max_working_days > 0 else float('inf')
    print(f"  - Need ~{chunks_needed:.0f} API calls per market per token")
    print(f"  - For 10K markets × 2 tokens = {20000 * chunks_needed:.0f} API calls")
    print(f"  - At 1 req/sec = {(20000 * chunks_needed / 3600):.1f} hours")
else:
    print("[FAILED] Cannot retrieve any historical data")
