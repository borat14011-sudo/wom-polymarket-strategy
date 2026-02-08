import requests
import csv
from datetime import datetime
import json
import time

def fetch_resolved_markets_january_2026():
    """Fetch all resolved Polymarket markets from January 2026"""
    
    base_url = "https://gamma-api.polymarket.com/markets"
    all_markets = []
    offset = 0
    limit = 100
    
    # January 2026 date range
    jan_start = datetime(2026, 1, 1)
    jan_end = datetime(2026, 2, 1)
    
    print("Fetching resolved markets from January 2026...")
    
    while True:
        params = {
            "closed": "true",
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            markets = response.json()
            
            if not markets:
                print(f"No more markets found at offset {offset}")
                break
            
            print(f"Fetched {len(markets)} markets at offset {offset}")
            
            # Filter for January 2026 resolved markets
            for market in markets:
                if market.get("closedTime"):
                    try:
                        # Parse closedTime - it's in format "2020-11-02 16:31:01+00"
                        closed_time_str = market["closedTime"]
                        # Handle different formats
                        if '+' in closed_time_str:
                            closed_time_str = closed_time_str.split('+')[0]
                        if '.' in closed_time_str:
                            closed_time_str = closed_time_str.split('.')[0]
                        
                        closed_time = datetime.strptime(closed_time_str.strip(), "%Y-%m-%d %H:%M:%S")
                        
                        if jan_start <= closed_time < jan_end:
                            all_markets.append(market)
                            print(f"  ✓ Found January 2026 market: {market.get('question', 'Unknown')[:60]}...")
                    except Exception as e:
                        # If we can't parse the date, skip it
                        continue
            
            # If we've gone past February 2026, we can stop
            # Check if the newest market in this batch is before January 2026
            if markets:
                try:
                    newest_closed = None
                    for m in markets:
                        if m.get("closedTime"):
                            ct_str = m["closedTime"].split('+')[0].split('.')[0].strip()
                            ct = datetime.strptime(ct_str, "%Y-%m-%d %H:%M:%S")
                            if newest_closed is None or ct > newest_closed:
                                newest_closed = ct
                    
                    # If we're getting markets older than December 2025, we can stop
                    if newest_closed and newest_closed < datetime(2025, 12, 1):
                        print(f"Reached markets before December 2025, stopping...")
                        break
                except:
                    pass
            
            offset += limit
            time.sleep(0.5)  # Be nice to the API
            
        except Exception as e:
            print(f"Error fetching markets at offset {offset}: {e}")
            break
    
    return all_markets

def extract_outcome_from_market(market):
    """Extract the outcome/resolution of a market"""
    # Try to get outcome from various fields
    outcomes_str = market.get("outcomes", "[]")
    try:
        outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
    except:
        outcomes = []
    
    prices_str = market.get("outcomePrices", "[]")
    try:
        prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
    except:
        prices = []
    
    # If we have outcomes and prices, find the winning outcome
    if outcomes and prices and len(outcomes) == len(prices):
        try:
            # Convert prices to float and find the highest
            price_floats = [float(p) for p in prices]
            max_price = max(price_floats)
            if max_price > 0.9:  # If price is very high, likely the winner
                winner_idx = price_floats.index(max_price)
                return outcomes[winner_idx]
        except:
            pass
    
    # Otherwise return a descriptive outcome
    return "Resolved (outcome TBD)"

def save_to_csv(markets, filename="jan_2026_resolved.csv"):
    """Save markets to CSV file"""
    
    if not markets:
        print("No markets found for January 2026!")
        return
    
    print(f"\nSaving {len(markets)} markets to {filename}...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['question', 'outcome', 'category', 'resolution_date', 'volume']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for market in markets:
            # Extract data
            question = market.get("question", "Unknown")
            category = market.get("category", "Unknown")
            volume = market.get("volume", "0")
            closed_time = market.get("closedTime", "Unknown")
            outcome = extract_outcome_from_market(market)
            
            # Parse resolution date
            resolution_date = closed_time
            try:
                if closed_time and closed_time != "Unknown":
                    ct_str = closed_time.split('+')[0].split('.')[0].strip()
                    dt = datetime.strptime(ct_str, "%Y-%m-%d %H:%M:%S")
                    resolution_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
            
            writer.writerow({
                'question': question,
                'outcome': outcome,
                'category': category,
                'resolution_date': resolution_date,
                'volume': volume
            })
    
    print(f"✓ Successfully saved {len(markets)} markets to {filename}")

if __name__ == "__main__":
    markets = fetch_resolved_markets_january_2026()
    print(f"\nTotal markets found in January 2026: {len(markets)}")
    save_to_csv(markets)
