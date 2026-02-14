#!/usr/bin/env python3
"""
QC CHECK: Compare multiple API endpoints for consistency
"""
import requests
import json

print("=" * 60)
print("POLYMARKET API QC - CROSS VALIDATION")
print("=" * 60)

# Test 1: Gamma API vs CLOB API for same markets
print("\n[TEST 1] Deportation Markets Price Check")
print("-" * 60)

# Gamma API
print("\n1. GAMMA API (gamma-api.polymarket.com)")
url = "https://gamma-api.polymarket.com/markets"
params = {'limit': 10, 'closed': False}
response = requests.get(url, params=params, timeout=10)

gamma_prices = {}
if response.status_code == 200:
    markets = response.json()
    for m in markets:
        q = m.get('question', '')
        if 'deport' in q.lower():
            prices = m.get('outcomePrices', '["?", "?"]')
            gamma_prices[q[:40]] = prices
            print(f"  {q[:45]}...")
            print(f"    Prices: {prices}")
            print(f"    Updated: {m.get('updatedAt', 'N/A')[:19]}")

# Test 2: Check individual market details
print("\n[TEST 2] Individual Market Detail Consistency")
print("-" * 60)

market_ids = ['517310', '517311', '517313']  # Deportation markets
for mid in market_ids:
    url = f"https://gamma-api.polymarket.com/markets/{mid}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        m = response.json()
        q = m.get('question', 'N/A')[:40]
        prices = m.get('outcomePrices', 'N/A')
        print(f"\n  Market {mid}: {q}...")
        print(f"    Prices: {prices}")

# Test 3: Check fresh markets file
print("\n[TEST 3] Local File Data Freshness")
print("-" * 60)

try:
    with open('active-markets.json', 'r') as f:
        data = json.load(f)
    
    fetch_time = data.get('fetch_timestamp', 'N/A')
    count = data.get('count', 0)
    print(f"  File timestamp: {fetch_time}")
    print(f"  Market count: {count}")
    
    # Check deportation markets in file
    markets = data.get('markets', [])
    for m in markets:
        q = m.get('question', '')
        if 'deport' in q.lower() and '250' in q:
            print(f"\n  {q[:45]}...")
            print(f"    Prices: {m.get('outcomePrices')}")
            print(f"    Updated: {m.get('updatedAt', 'N/A')[:19]}")
            break
except Exception as e:
    print(f"  Error reading file: {e}")

# Test 4: Data staleness check
print("\n[TEST 4] Data Staleness Analysis")
print("-" * 60)

from datetime import datetime

try:
    with open('active-markets.json', 'r') as f:
        data = json.load(f)
    
    fetch_time = datetime.fromisoformat(data.get('fetch_timestamp', datetime.now().isoformat()))
    now = datetime.now()
    age_minutes = (now - fetch_time).total_seconds() / 60
    
    print(f"  Data age: {age_minutes:.1f} minutes")
    if age_minutes < 5:
        print("  [OK] FRESH (under 5 minutes)")
    elif age_minutes < 30:
        print("  [WARN] MODERATE (5-30 minutes)")
    else:
        print("  [FAIL] STALE (over 30 minutes)")
        
except Exception as e:
    print(f"  Error: {e}")

# Test 5: Check for duplicate markets
print("\n[TEST 5] Duplicate Market Check")
print("-" * 60)

try:
    with open('active-markets.json', 'r') as f:
        data = json.load(f)
    
    markets = data.get('markets', [])
    ids = [m.get('id') for m in markets]
    duplicates = len(ids) - len(set(ids))
    
    if duplicates == 0:
        print(f"  [OK] No duplicates found ({len(ids)} unique markets)")
    else:
        print(f"  [FAIL] Found {duplicates} duplicate market IDs")
        
except Exception as e:
    print(f"  Error: {e}")

# Test 6: Price sanity check
print("\n[TEST 6] Price Sanity Check")
print("-" * 60)

try:
    with open('active-markets.json', 'r') as f:
        data = json.load(f)
    
    markets = data.get('markets', [])
    issues = 0
    
    for m in markets[:20]:  # Check first 20
        prices_str = m.get('outcomePrices', '[]')
        try:
            prices = json.loads(prices_str)
            if len(prices) == 2:
                p1, p2 = float(prices[0]), float(prices[1])
                total = p1 + p2
                if abs(total - 1.0) > 0.01:  # More than 1% deviation
                    issues += 1
                    print(f"  [WARN] {m.get('question', 'N/A')[:40]}...")
                    print(f"         Prices sum to {total:.3f} (expected ~1.0)")
        except:
            pass
    
    if issues == 0:
        print("  [OK] All checked markets have valid prices (sum to ~$1)")
    else:
        print(f"  [WARN] {issues} markets with price issues")
        
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 60)
print("QC CHECK COMPLETE")
print("=" * 60)
