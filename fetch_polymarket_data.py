#!/usr/bin/env python3
"""
Fetch historical Polymarket trader data and Polysights alerts
"""
import requests
import json
from datetime import datetime, timedelta
import csv

# Try to fetch top traders historical data
def fetch_top_traders():
    """Fetch top traders from Polymarket"""
    try:
        # Try different API endpoints
        endpoints = [
            "https://data-api.polymarket.com/users/top",
            "https://gamma-api.polymarket.com/users",
            "https://clob.polymarket.com/users/top"
        ]
        
        for endpoint in endpoints:
            try:
                print(f"Trying: {endpoint}")
                response = requests.get(endpoint, timeout=10)
                if response.status_code == 200:
                    print(f"Success! Status: {response.status_code}")
                    print(f"Response: {response.text[:500]}")
                    return response.json()
                else:
                    print(f"Failed: {response.status_code} - {response.text[:200]}")
            except Exception as e:
                print(f"Error with {endpoint}: {e}")
                
    except Exception as e:
        print(f"Error fetching traders: {e}")
    return None

# Try to fetch historical trades
def fetch_historical_trades():
    """Fetch historical trades"""
    try:
        # Calculate date range (2 years back)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)  # 2 years
        
        print(f"\nFetching trades from {start_date} to {end_date}")
        
        # Try CLOB API
        url = "https://clob.polymarket.com/trades"
        params = {
            "limit": 1000,
            "after": int(start_date.timestamp()),
            "before": int(end_date.timestamp())
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"Trades API Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            return response.json()
            
    except Exception as e:
        print(f"Error fetching trades: {e}")
    return None

# Try to fetch Polysights data
def fetch_polysights_data():
    """Attempt to fetch Polysights historical alerts"""
    print("\n=== Polysights Data Fetch ===")
    print("Note: Polysights data requires Twitter/X API access or web scraping")
    print("Twitter/X historical data requires authentication and paid API access")
    print("Current capabilities: LIMITED - would require:")
    print("  1. Twitter API v2 credentials (paid)")
    print("  2. Web scraping with browser automation")
    print("  3. Or manual data collection from @polysights feed")
    
    # We cannot access this without proper API keys
    return {
        "status": "UNAVAILABLE",
        "reason": "Twitter API requires authentication",
        "theoretical_accuracy": "85% (claimed)",
        "source": "Polysights (@polysights on X/Twitter)"
    }

if __name__ == "__main__":
    print("=" * 60)
    print("POLYMARKET HISTORICAL DATA COLLECTION")
    print("=" * 60)
    
    # Fetch traders
    print("\n1. Fetching Top Traders...")
    traders = fetch_top_traders()
    
    # Fetch trades
    print("\n2. Fetching Historical Trades...")
    trades = fetch_historical_trades()
    
    # Polysights
    print("\n3. Checking Polysights Availability...")
    polysights = fetch_polysights_data()
    
    # Summary
    print("\n" + "=" * 60)
    print("DATA AVAILABILITY SUMMARY")
    print("=" * 60)
    print(f"Top Traders: {'✓ Available' if traders else '✗ Not Available'}")
    print(f"Historical Trades: {'✓ Available' if trades else '✗ Not Available'}")
    print(f"Polysights Alerts: ✗ Not Available (requires Twitter API)")
    print("\nSaving results...")
    
    # Save what we got
    with open('data_fetch_results.json', 'w') as f:
        json.dump({
            "traders": traders,
            "trades": trades,
            "polysights": polysights,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print("Results saved to: data_fetch_results.json")
