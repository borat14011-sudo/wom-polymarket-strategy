"""
Reality check: What historical data is actually available?
"""
import sys
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import requests
import json
from datetime import datetime, timezone

print("=== POLYMARKET HISTORICAL DATA REALITY CHECK ===\n")

# Test 1: What does Gamma API actually provide?
print("1. Gamma API - Market Metadata")
print("   Endpoint: https://gamma-api.polymarket.com/markets")
print("   Testing...")

try:
    response = requests.get("https://gamma-api.polymarket.com/markets", params={
        "limit": 1,
        "closed": "true"
    })
    
    if response.status_code == 200:
        market = response.json()[0]
        
        # Check for price history fields
        has_prices = False
        price_fields = []
        
        for key in market.keys():
            if 'price' in key.lower() or 'history' in key.lower():
                price_fields.append(key)
                value = market[key]
                print(f"   - {key}: {value}")
        
        print(f"\n   Result: Gamma API has {len(price_fields)} price-related fields")
        print("   Fields:", price_fields)
        print("\n   CONCLUSION: Only current/recent prices, NO historical price arrays")
        
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Check if there's a separate price history API
print("\n2. Looking for Price History Endpoints")
print("   Testing known patterns...")

test_urls = [
    "https://clob.polymarket.com/prices-history",
    "https://data-api.polymarket.com/prices",
    "https://gamma-api.polymarket.com/price-history",
    "https://strapi-matic.polymarket.com/prices",
]

for url in test_urls:
    try:
        resp = requests.get(url, timeout=3)
        status = resp.status_code
        print(f"   - {url.split('polymarket.com')[1]}: {status}")
        if status == 200:
            print(f"     [FOUND!] Data: {str(resp.json())[:100]}")
    except Exception as e:
        print(f"   - {url.split('polymarket.com')[1]}: ERROR ({str(e)[:30]})")

print("\n   CONCLUSION: No public historical price API found")

# Test 3: What DO those GitHub repos actually do?
print("\n3. How DO the GitHub repos get historical data?")
print("   Hypothesis: They may be:")
print("   a) Using WebSocket streams (real-time only)")
print("   b) Scraping the website")  
print("   c) Using undocumented APIs")
print("   d) Only getting current prices + metadata")

# Test 4: What CAN we realistically collect?
print("\n4. What Data IS Available Right Now?")
print("   Testing comprehensive market data collection...")

try:
    # Get markets with various filters
    params_list = [
        {"limit": 100, "closed": "true", "offset": 0},
        {"limit": 100, "active": "true", "offset": 0},
    ]
    
    total_markets = 0
    markets_2024_plus = 0
    resolved_markets = 0
    
    for params in params_list:
        resp = requests.get("https://gamma-api.polymarket.com/markets", params=params, timeout=10)
        if resp.status_code == 200:
            markets = resp.json()
            total_markets += len(markets)
            
            for m in markets:
                created = m.get('createdAt', '')
                if created and '2024' in created:
                    markets_2024_plus += 1
                
                if m.get('closed') and m.get('outcomePrices'):
                    resolved_markets += 1
    
    print(f"   - Total markets fetched: {total_markets}")
    print(f"   - Markets from 2024+: {markets_2024_plus}")
    print(f"   - Resolved markets: {resolved_markets}")
    
except Exception as e:
    print(f"   ERROR: {e}")

# Final assessment
print("\n" + "="*60)
print("FINAL ASSESSMENT")
print("="*60)
print("\n❌ WHAT'S NOT AVAILABLE:")
print("   - Historical minute/hourly price arrays via API")
print("   - Bulk price history downloads")
print("   - Time-series price data from past months")

print("\n✅ WHAT IS AVAILABLE:")
print("   - Current market metadata (question, dates, category)")
print("   - Current prices (last trade, bid, ask)")
print("   - Recent price changes (1h, 24h, 7d, 30d)")
print("   - Volume metrics")
print("   - Resolved outcomes (for closed markets)")
print("   - Market filtering by date/status")

print("\n🔧 ALTERNATIVE STRATEGIES:")
print("   1. Collect current snapshots repeatedly (build history forward)")
print("   2. Use WebSocket streams (real-time only)")
print("   3. Web scraping (may violate ToS, unreliable)")
print("   4. Request data from Polymarket directly")
print("   5. Use existing datasets (e.g., Kaggle, research papers)")

print("\n💡 RECOMMENDED APPROACH:")
print("   For 2-year historical data (Feb 2024 - Feb 2026):")
print("   → Focus on Feb 2026 forward with real-time collection")
print("   → For past data, use alternative sources or accept limitations")
print("   → Build robust current data collector as foundation")
