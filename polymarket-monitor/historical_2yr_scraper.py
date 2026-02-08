#!/usr/bin/env python3
"""
2-Year Historical Data Scraper
Fetches Polymarket data from Feb 2024 - Feb 2026 with 4 prices per day

Modified from historical_scraper.py to pull complete price histories
instead of just current snapshots.
"""
import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("historical-data-scraper/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# Date range (timezone-aware to match API dates)
from datetime import timezone
START_DATE = datetime(2024, 2, 1, tzinfo=timezone.utc)
END_DATE = datetime(2026, 2, 7, tzinfo=timezone.utc)

print(f"\n{'='*70}")
print(f"2-YEAR HISTORICAL DATA SCRAPER")
print(f"Date Range: {START_DATE.date()} to {END_DATE.date()}")
print(f"{'='*70}\n")

# ============================================================
# STEP 1: Fetch All Markets from Feb 2024+
# ============================================================
def fetch_all_markets():
    """Fetch all markets (active + closed) from Feb 2024 onwards"""
    print("STEP 1: Fetching all markets from Feb 2024+...")
    
    all_markets = []
    
    # Fetch closed markets first
    print("\n  Fetching CLOSED markets...")
    offset = 0
    limit = 100
    
    while True:
        print(f"    Batch {offset//limit + 1} (offset={offset})...")
        
        try:
            response = requests.get(
                f"{GAMMA_API}/markets",
                params={
                    'limit': limit,
                    'offset': offset,
                    'closed': True
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"    [ERROR] API returned {response.status_code}")
                break
            
            markets = response.json()
            if not markets:
                break
            
            # Filter by date
            filtered = []
            for m in markets:
                start_date = m.get('startDate')
                if start_date:
                    try:
                        dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        if dt >= START_DATE:
                            filtered.append(m)
                    except:
                        pass
            
            all_markets.extend(filtered)
            print(f"      Got {len(markets)} markets, {len(filtered)} after date filter")
            
            if len(markets) < limit:
                break
            
            offset += limit
            time.sleep(0.3)
            
        except Exception as e:
            print(f"    [ERROR] {e}")
            break
    
    print(f"  Closed markets: {len(all_markets):,}")
    
    # Now fetch active markets
    print("\n  Fetching ACTIVE markets...")
    offset = 0
    
    while True:
        print(f"    Batch {offset//limit + 1} (offset={offset})...")
        
        try:
            response = requests.get(
                f"{GAMMA_API}/markets",
                params={
                    'limit': limit,
                    'offset': offset,
                    'closed': False
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"  [ERROR] API returned {response.status_code}")
                break
            
            markets = response.json()
            if not markets:
                break
            
            # Filter by date
            filtered = []
            for m in markets:
                start_date = m.get('startDate')
                if start_date:
                    try:
                        dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        if dt >= START_DATE:
                            filtered.append(m)
                    except:
                        pass
            
            all_markets.extend(filtered)
            print(f"    Got {len(markets)} markets, {len(filtered)} after date filter")
            
            # If we got fewer than limit, we're done
            if len(markets) < limit:
                break
            
            offset += limit
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            break
    
    print(f"\n[COMPLETE] Fetched {len(all_markets):,} markets from {START_DATE.date()}+\n")
    
    # Save raw market list
    with open(DATA_DIR / "markets_2yr_list.json", 'w') as f:
        json.dump(all_markets, f)
    
    return all_markets

# ============================================================
# STEP 2: Fetch Price Histories for Each Market
# ============================================================
def fetch_price_history(token_id):
    """Fetch full price history for a token from CLOB API"""
    try:
        url = f"{CLOB_API}/prices-history"
        params = {
            'market': token_id,
            'interval': 'max',
            'fidelity': 1  # Get all available data
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('history', [])
        else:
            return None
            
    except Exception as e:
        return None

def downsample_to_4_per_day(prices):
    """Downsample hourly prices to 4 per day (00:00, 06:00, 12:00, 18:00 UTC)"""
    if not prices:
        return []
    
    # Group by date
    by_date = {}
    for p in prices:
        timestamp = p.get('t', 0)
        if not timestamp:
            continue
        
        dt = datetime.fromtimestamp(timestamp)
        date_key = dt.date()
        
        if date_key not in by_date:
            by_date[date_key] = []
        by_date[date_key].append(p)
    
    # For each date, pick closest to 00:00, 06:00, 12:00, 18:00
    result = []
    target_hours = [0, 6, 12, 18]
    
    for date, day_prices in sorted(by_date.items()):
        for target_hour in target_hours:
            # Find closest price to target hour
            target_time = datetime.combine(date, datetime.min.time()).replace(hour=target_hour)
            target_ts = target_time.timestamp()
            
            closest = min(
                day_prices,
                key=lambda p: abs(p.get('t', 0) - target_ts)
            )
            
            result.append({
                't': target_ts,  # Normalized to target hour
                'p': closest.get('p', 0),
                'original_t': closest.get('t', 0)  # Keep original for reference
            })
    
    return result

def fetch_all_price_histories(markets):
    """Fetch and downsample price histories for all markets"""
    print("STEP 2: Fetching price histories...")
    print(f"  Total markets: {len(markets):,}")
    print(f"  Downsampling to 4 prices/day\n")
    
    results = []
    success_count = 0
    fail_count = 0
    
    for i, market in enumerate(markets):
        if i % 100 == 0 and i > 0:
            print(f"  Progress: {i:,}/{len(markets):,} ({i/len(markets)*100:.1f}%) | "
                  f"Success: {success_count} | Failed: {fail_count}")
        
        market_id = market.get('id')
        tokens = market.get('clobTokenIds', [])
        
        if not tokens:
            fail_count += 1
            continue
        
        # Get price history for first token (YES side)
        token_id = tokens[0]
        prices = fetch_price_history(token_id)
        
        if prices and len(prices) > 0:
            # Downsample to 4/day
            downsampled = downsample_to_4_per_day(prices)
            
            results.append({
                'market_id': market_id,
                'question': market.get('question'),
                'token_id': token_id,
                'start_date': market.get('startDate'),
                'end_date': market.get('endDate'),
                'closed': market.get('closed', False),
                'outcome': market.get('outcome'),
                'volume': market.get('volume', 0),
                'prices_4d': downsampled,  # 4 per day
                'original_points': len(prices)
            })
            success_count += 1
        else:
            fail_count += 1
        
        # Rate limiting
        time.sleep(0.1)
        
        # Save checkpoint every 1000
        if (i + 1) % 1000 == 0:
            checkpoint_file = DATA_DIR / f"prices_2yr_checkpoint_{i+1}.json"
            with open(checkpoint_file, 'w') as f:
                json.dump(results, f)
            print(f"    [CHECKPOINT] Saved at {i+1} markets")
    
    print(f"\n[COMPLETE] Price histories fetched!")
    print(f"  Total: {len(results):,}")
    print(f"  Success: {success_count}")
    print(f"  Failed: {fail_count}\n")
    
    # Save final
    with open(DATA_DIR / "prices_2yr_complete.json", 'w') as f:
        json.dump(results, f)
    
    return results

# ============================================================
# STEP 3: Build Analysis-Ready Dataset
# ============================================================
def build_analysis_dataset(market_data):
    """Convert to analysis-ready format"""
    print("STEP 3: Building analysis dataset...")
    
    # Filter to markets with sufficient data
    valid = [m for m in market_data if len(m.get('prices_4d', [])) >= 20]
    
    print(f"  Markets with 20+ price points: {len(valid):,}")
    
    # Add statistics
    for m in valid:
        prices = [p['p'] for p in m['prices_4d']]
        m['stats'] = {
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': sum(prices) / len(prices),
            'volatility': max(prices) - min(prices),
            'data_points': len(prices)
        }
    
    # Save
    with open(DATA_DIR / "analysis_dataset_2yr.json", 'w') as f:
        json.dump(valid, f)
    
    print(f"[COMPLETE] Analysis dataset ready: {len(valid):,} markets\n")
    
    return valid

# ============================================================
# MAIN
# ============================================================
def main():
    start_time = time.time()
    
    # Step 1: Fetch all markets
    markets = fetch_all_markets()
    
    if not markets:
        print("[ERROR] No markets fetched. Exiting.")
        return
    
    # Step 2: Fetch price histories
    market_data = fetch_all_price_histories(markets)
    
    # Step 3: Build analysis dataset
    analysis_ready = build_analysis_dataset(market_data)
    
    # Summary
    elapsed = time.time() - start_time
    print(f"{'='*70}")
    print(f"SCRAPE COMPLETE")
    print(f"{'='*70}")
    print(f"Time: {elapsed/60:.1f} minutes")
    print(f"Markets with price data: {len(analysis_ready):,}")
    print(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"Sampling: 4 prices/day")
    print(f"Output: {DATA_DIR / 'analysis_dataset_2yr.json'}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
