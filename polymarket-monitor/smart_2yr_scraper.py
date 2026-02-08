#!/usr/bin/env python3
"""
Smart 2-Year Scraper - Skip old markets using binary search approach
"""
import requests
import json
import time
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("historical-data-scraper/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

GAMMA_API = "https://gamma-api.polymarket.com"
START_DATE = datetime(2024, 2, 1, tzinfo=timezone.utc)

print(f"\n{'='*70}")
print(f"SMART 2-YEAR SCRAPER")
print(f"Strategy: Binary search for Feb 2024 start point")
print(f"{'='*70}\n")

# Step 1: Find where Feb 2024 markets start
print("STEP 1: Finding Feb 2024 start offset...")

def check_offset(offset, retries=3):
    """Check if markets at this offset are from Feb 2024+"""
    for attempt in range(retries):
        try:
            r = requests.get(f"{GAMMA_API}/markets", 
                            params={'limit': 10, 'closed': True, 'offset': offset},
                            timeout=30)
            if r.status_code != 200:
                return None
            markets = r.json()
            if not markets:
                return None
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return None
    
    # Count how many are from Feb 2024+
    count = 0
    for m in markets:
        start = m.get('startDate')
        if start:
            try:
                dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                if dt >= START_DATE:
                    count += 1
            except:
                pass
    return count

# Binary search to find start
low = 0
high = 100000  # Assume max 100K closed markets
best_offset = None

print(f"  Searching range 0-100,000...")
while low < high:
    mid = (low + high) // 2
    count = check_offset(mid)
    
    if count is None:
        high = mid - 1
        continue
    
    print(f"    Offset {mid}: {count}/10 markets from Feb 2024+")
    
    if count > 0:
        best_offset = mid
        high = mid - 1  # Try earlier
    else:
        low = mid + 1
    
    time.sleep(0.2)

if best_offset:
    print(f"\n[FOUND] Feb 2024 markets start around offset {best_offset}")
else:
    print(f"\n[NOT FOUND] Using active markets only")
    best_offset = 0

# Step 2: Fetch from that point forward
print(f"\nSTEP 2: Fetching markets from offset {best_offset}...")

all_markets = []
offset = best_offset
limit = 100

while True:
    print(f"  Batch {(offset-best_offset)//limit + 1} (offset={offset})...")
    
    try:
        r = requests.get(f"{GAMMA_API}/markets",
                        params={'limit': limit, 'closed': True, 'offset': offset},
                        timeout=30)
        
        if r.status_code != 200 or not r.json():
            break
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"    [ERROR] Connection failed: {e}, retrying in 5s...")
        time.sleep(5)
        continue
    
    markets = r.json()
    
    # Filter by date
    filtered = []
    for m in markets:
        start = m.get('startDate')
        if start:
            try:
                dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                if dt >= START_DATE:
                    filtered.append(m)
            except:
                pass
    
    all_markets.extend(filtered)
    print(f"    Got {len(markets)} markets, {len(filtered)} from Feb 2024+, total: {len(all_markets)}")
    
    # If we got 0 matches in this batch, we might be past the range
    if len(filtered) == 0 and offset > best_offset + 5000:
        print(f"    No matches in batch, stopping")
        break
    
    if len(markets) < limit:
        break
    
    offset += limit
    time.sleep(0.3)

# Also get active markets
print(f"\nSTEP 3: Fetching ACTIVE markets...")
offset = 0
while True:
    print(f"  Batch {offset//limit + 1} (offset={offset})...")
    
    try:
        r = requests.get(f"{GAMMA_API}/markets",
                        params={'limit': limit, 'closed': False, 'offset': offset},
                        timeout=30)
        
        if r.status_code != 200 or not r.json():
            break
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"    [ERROR] Connection failed: {e}, retrying in 5s...")
        time.sleep(5)
        continue
    
    markets = r.json()
    
    filtered = []
    for m in markets:
        start = m.get('startDate')
        if start:
            try:
                dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                if dt >= START_DATE:
                    filtered.append(m)
            except:
                pass
    
    all_markets.extend(filtered)
    print(f"    Got {len(markets)} markets, {len(filtered)} from Feb 2024+, total: {len(all_markets)}")
    
    if len(markets) < limit:
        break
    
    offset += limit
    time.sleep(0.3)

# Save
with open(DATA_DIR / "markets_2yr_list.json", 'w') as f:
    json.dump(all_markets, f)

print(f"\n{'='*70}")
print(f"MARKET COLLECTION COMPLETE")
print(f"{'='*70}")
print(f"Total markets from Feb 2024+: {len(all_markets):,}")
print(f"Saved to: {DATA_DIR / 'markets_2yr_list.json'}")
print(f"{'='*70}\n")

print("Ready for price history fetching!")
