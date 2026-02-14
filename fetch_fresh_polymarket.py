#!/usr/bin/env python3
"""
Fetch fresh Polymarket data
"""

import json
import requests
from datetime import datetime, timezone

def fetch_polymarket_markets():
    """Fetch fresh Polymarket data"""
    url = "https://gamma-api.polymarket.com/markets"
    params = {
        "limit": 200,
        "closed": "false"
    }
    
    print(f"Fetching fresh data from: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Save the data
        output = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "markets": data,
            "summary": {
                "total_markets": len(data),
                "source_url": url,
                "params": params
            }
        }
        
        with open('polymarket_fresh.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] Successfully fetched {len(data)} markets")
        print(f"Saved to: polymarket_fresh.json")
        
        # Also update the latest file
        with open('polymarket_latest.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"Updated: polymarket_latest.json")
        
        return data
        
    except Exception as e:
        print(f"[ERROR] Error fetching data: {e}")
        return None

def main():
    print("="*60)
    print("FETCH FRESH POLYMARKET DATA")
    print("="*60)
    
    markets = fetch_polymarket_markets()
    
    if markets:
        print("\nSample of first 3 markets:")
        print("-"*40)
        for i, market in enumerate(markets[:3]):
            print(f"\n{i+1}. {market.get('question', 'N/A')[:80]}...")
            print(f"   Prices: {market.get('outcomePrices', [])}")
            print(f"   Volume: ${float(market.get('volume', 0)):,.2f}")
            print(f"   Slug: {market.get('slug', 'N/A')}")
    else:
        print("\nFailed to fetch data. Check internet connection or API status.")

if __name__ == "__main__":
    main()