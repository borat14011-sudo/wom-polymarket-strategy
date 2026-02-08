"""
Identify Resolved Markets (Oct 2025 - Feb 2026)
Queries Polymarket API to find all markets that resolved in this timeframe
"""

import requests
import json
from datetime import datetime, timezone
import time

# Date range for resolved markets
START_DATE = datetime(2025, 10, 1, tzinfo=timezone.utc)
END_DATE = datetime(2026, 2, 28, 23, 59, 59, tzinfo=timezone.utc)

def get_resolved_markets():
    """
    Query Polymarket Gamma API for resolved markets
    """
    all_markets = []
    
    # Try Gamma API endpoint for markets
    gamma_url = "https://gamma-api.polymarket.com/markets"
    
    print(f"🔍 Querying Polymarket Gamma API for resolved markets...")
    print(f"📅 Date range: {START_DATE.date()} to {END_DATE.date()}")
    
    try:
        # Query with filters for closed/resolved markets
        params = {
            'closed': 'true',
            'active': 'false',
            '_limit': 1000,  # Get large batch
            '_sort': '-volume'  # Sort by volume descending
        }
        
        response = requests.get(gamma_url, params=params, timeout=30)
        response.raise_for_status()
        markets_data = response.json()
        
        print(f"📥 Fetched {len(markets_data)} closed markets")
        
        # Filter by resolution date
        resolved_markets = []
        for market in markets_data:
            # Check if market resolved in our date range
            closed_time = market.get('closedTime') or market.get('endDate')
            if closed_time:
                try:
                    # Parse various date formats
                    if 'T' in closed_time:
                        closed_dt = datetime.fromisoformat(closed_time.replace('Z', '+00:00'))
                    else:
                        closed_dt = datetime.strptime(closed_time, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                    
                    if START_DATE <= closed_dt <= END_DATE:
                        resolved_markets.append({
                            'id': market.get('id'),
                            'market_id': market.get('conditionId'),
                            'question': market.get('question'),
                            'slug': market.get('slug'),
                            'closed_time': closed_time,
                            'volume': market.get('volume', 0),
                            'category': market.get('category', 'Unknown')
                        })
                except Exception as e:
                    print(f"⚠️ Could not parse date for market {market.get('id')}: {e}")
        
        print(f"✅ Found {len(resolved_markets)} resolved markets in date range")
        return resolved_markets
        
    except Exception as e:
        print(f"❌ Error querying Gamma API: {e}")
        return []

def save_market_list(markets, filename='resolved_markets_oct2025_feb2026.json'):
    """Save market list to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(markets, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(markets)} markets to {filename}")

def print_summary(markets):
    """Print summary statistics"""
    if not markets:
        print("No markets found.")
        return
    
    total_volume = sum(float(m.get('volume', 0)) for m in markets)
    categories = {}
    for m in markets:
        cat = m.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total markets: {len(markets)}")
    print(f"Total volume: ${total_volume:,.2f}")
    print(f"\nTop 10 by volume:")
    sorted_markets = sorted(markets, key=lambda x: float(x.get('volume', 0)), reverse=True)
    for i, market in enumerate(sorted_markets[:10], 1):
        print(f"  {i}. {market['question'][:60]}...")
        print(f"     Volume: ${float(market.get('volume', 0)):,.2f}")
    
    print(f"\nCategories:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")

if __name__ == "__main__":
    # Try to fetch from API
    markets = get_resolved_markets()
    
    if markets:
        save_market_list(markets)
        print_summary(markets)
        
        # Also create a simple CSV for quick reference
        import csv
        with open('resolved_markets_simple.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['market_id', 'slug', 'question', 'closed_time', 'volume'])
            writer.writeheader()
            writer.writerows(markets)
        print(f"💾 Also saved to resolved_markets_simple.csv")
    else:
        print("\n⚠️ No markets found via API. Checking existing data files...")
        # Check if we have local market data we can filter
        try:
            with open('markets.json', 'r', encoding='utf-8') as f:
                local_markets = json.load(f)
            print(f"📂 Found {len(local_markets)} markets in local markets.json")
            print("Note: These appear to be old markets (2020-2021). Need to fetch recent data.")
        except FileNotFoundError:
            print("No local markets.json found.")
