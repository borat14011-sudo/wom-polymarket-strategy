#!/usr/bin/env python3
"""
Kalshi Actual Working API Test
Based on discovered endpoints from previous tests
"""

import requests
import json
import time
import sys

def test_endpoint(url, name, headers=None, params=None):
    """Test a single API endpoint."""
    print(f"\nTesting {name}:")
    print(f"  URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ SUCCESS!")
            
            # Try to extract useful information
            if 'markets' in data:
                markets = data['markets']
                print(f"  Found {len(markets)} markets")
                if markets:
                    m = markets[0]
                    print(f"  Sample market: {m.get('ticker', 'N/A')} - {m.get('title', 'N/A')[:50]}...")
                    print(f"    Yes: {m.get('yes_price', 'N/A')}, No: {m.get('no_price', 'N/A')}")
            
            elif 'events' in data:
                events = data['events']
                print(f"  Found {len(events)} events")
                if events:
                    e = events[0]
                    print(f"  Sample event: {e.get('ticker', 'N/A')} - {e.get('title', 'N/A')[:50]}...")
            
            elif 'series' in data:
                series = data['series']
                print(f"  Found {len(series)} series")
            
            else:
                print(f"  Response keys: {list(data.keys())}")
                print(f"  Response sample: {json.dumps(data, indent=2)[:300]}...")
                
            return True, data
            
        elif response.status_code == 401:
            print(f"  ⚠️  Requires authentication")
            print(f"  Response: {response.text[:200]}")
            return False, None
            
        elif response.status_code == 403:
            print(f"  ❌ Forbidden (may need different endpoint)")
            return False, None
            
        elif response.status_code == 404:
            print(f"  ❌ Not found")
            return False, None
            
        else:
            print(f"  ❌ Unexpected status")
            print(f"  Response: {response.text[:200]}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"  ❌ Timeout")
        return False, None
    except requests.exceptions.ConnectionError as e:
        print(f"  ❌ Connection error: {e}")
        return False, None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False, None

def main():
    print("=" * 70)
    print("KALSHI API ACTUAL WORKING TEST")
    print("Based on discovered endpoints from investigation")
    print("=" * 70)
    
    # Test with known working API key from previous tests
    api_key = "14a525cf-42d7-4746-8e36-30a8d9c17c96"
    
    # Test cases based on what we found works
    test_cases = [
        {
            "name": "Public Markets API",
            "url": "https://api.kalshi.com/v1/markets",
            "headers": None,
            "params": {"limit": 5}
        },
        {
            "name": "Public Events API", 
            "url": "https://api.kalshi.com/v1/events",
            "headers": None,
            "params": {"limit": 5}
        },
        {
            "name": "Trading API with Key",
            "url": "https://trading-api.kalshi.com/trade-api/v2/events",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "params": None
        },
        {
            "name": "Elections API",
            "url": "https://api.elections.kalshi.com/v1/markets",
            "headers": None,
            "params": {"limit": 5}
        }
    ]
    
    results = []
    
    for test in test_cases:
        success, data = test_endpoint(
            test["url"], 
            test["name"],
            headers=test["headers"],
            params=test["params"]
        )
        results.append({
            "name": test["name"],
            "url": test["url"],
            "success": success,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        if success and data:
            # Save successful responses for analysis
            filename = f"kalshi_{test['name'].lower().replace(' ', '_')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"  Saved to: {filename}")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {result['name']}")
    
    # API Domain Analysis
    print("\n" + "=" * 70)
    print("API DOMAIN ANALYSIS")
    print("=" * 70)
    
    domains = {}
    for result in results:
        if result["url"].startswith("https://"):
            domain = result["url"].split("//")[1].split("/")[0]
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(result["name"])
    
    print(f"Found {len(domains)} unique API domains:")
    for domain, tests in domains.items():
        print(f"\n  {domain}:")
        for test in tests:
            print(f"    - {test}")
    
    # Check if domains are different from api.kalshi.com
    api_kalshi_com = "api.kalshi.com"
    different_domains = [d for d in domains.keys() if d != api_kalshi_com]
    
    print(f"\nDomains different from {api_kalshi_com}: {len(different_domains)}")
    for domain in different_domains:
        print(f"  - {domain}")
    
    # Authentication test simulation
    print("\n" + "=" * 70)
    print("AUTHENTICATION STATUS")
    print("=" * 70)
    
    # Try login simulation
    print("\nAuthentication simulation with provided credentials:")
    print(f"Email: Borat14011@gmail.com")
    print(f"Password: {'*' * len('Montenegro@')}")
    
    print("\n⚠️  Note: Actual authentication requires:")
    print("  1. Valid Kalshi account")
    print("  2. API key from Kalshi dashboard")
    print("  3. Proper authentication endpoint (likely POST /login)")
    
    # Based on our tests, what works?
    print("\n" + "=" * 70)
    print("WHAT WORKS BASED ON TESTS")
    print("=" * 70)
    
    working_endpoints = [r for r in results if r["success"]]
    if working_endpoints:
        print(f"\n✅ Working endpoints ({len(working_endpoints)}):")
        for endpoint in working_endpoints:
            print(f"  - {endpoint['name']}: {endpoint['url']}")
    else:
        print("\n❌ No endpoints working with current configuration")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS FOR FULL API ACCESS")
    print("=" * 70)
    
    print("""
1. Get proper API credentials:
   - Log into Kalshi account
   - Navigate to API settings
   - Generate API key
   - Note: May require account verification

2. Use correct authentication method:
   - Likely Bearer token authentication
   - Token from login endpoint or API key

3. Test endpoints in this order:
   a) Public endpoints (no auth needed)
   b) Trading endpoints with API key
   c) Order placement with small amounts

4. Implement proper error handling:
   - Rate limiting
   - Authentication refresh
   - Network retries
""")
    
    # Save comprehensive results
    final_results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_results": results,
        "domains_analyzed": domains,
        "different_from_api_kalshi_com": different_domains,
        "working_endpoints": [r["name"] for r in results if r["success"]]
    }
    
    with open("kalshi_comprehensive_results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\nDetailed results saved to: kalshi_comprehensive_results.json")
    print("\n" + "=" * 70)
    
    return 0 if passed > 0 else 1

if __name__ == "__main__":
    sys.exit(main())