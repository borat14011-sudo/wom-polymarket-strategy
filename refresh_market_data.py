#!/usr/bin/env python3
"""
POLYMARKET DATA REFRESH SCRIPT
Automatically refreshes active-markets.json when data becomes stale
"""
import requests
import json
import time
from datetime import datetime, timezone

def refresh_market_data():
    """Refresh the active-markets.json file with latest data"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting market data refresh...")
    
    try:
        # Fetch fresh data from Gamma API
        url = "https://gamma-api.polymarket.com/markets"
        params = {
            'limit': 50,
            'closed': False
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            markets = response.json()
            
            # Create the data structure
            data = {
                "fetch_timestamp": datetime.now(timezone.utc).isoformat(),
                "count": len(markets),
                "markets": markets
            }
            
            # Save to file
            with open('active-markets.json', 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"SUCCESS: Refreshed {len(markets)} markets")
            print(f"TIMESTAMP: {data['fetch_timestamp']}")
            return True
        else:
            print(f"ERROR: API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: During refresh: {e}")
        return False

def check_and_refresh():
    """Check if refresh is needed and perform it"""
    try:
        # Check current file age
        with open('active-markets.json', 'r') as f:
            data = json.load(f)
        
        fetch_time = datetime.fromisoformat(data.get('fetch_timestamp', datetime.now().isoformat()))
        now = datetime.now(timezone.utc)
        age_minutes = (now - fetch_time.replace(tzinfo=timezone.utc)).total_seconds() / 60
        
        print(f"Current data age: {age_minutes:.1f} minutes")
        
        if age_minutes > 30:
            print("Data is stale - refreshing...")
            return refresh_market_data()
        else:
            print("Data is fresh - no refresh needed")
            return True
            
    except Exception as e:
        print(f"Error checking file: {e}")
        print("Attempting refresh...")
        return refresh_market_data()

if __name__ == "__main__":
    print("=== POLYMARKET DATA REFRESH ===")
    success = check_and_refresh()
    
    if success:
        print("SUCCESS: Refresh completed")
    else:
        print("ERROR: Refresh failed")
        exit(1)