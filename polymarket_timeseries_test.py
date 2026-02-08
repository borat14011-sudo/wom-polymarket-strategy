#!/usr/bin/env python3
"""
Polymarket Timeseries API Validation Script
Tests historical price data API and validates data quality
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import sys

CLOB_BASE = "https://clob.polymarket.com"

def fetch_price_history(token_id, interval="1w", fidelity=60, start_ts=None, end_ts=None):
    """
    Fetch price history for a token
    
    Args:
        token_id: CLOB token ID
        interval: Time interval (1m, 1h, 6h, 1d, 1w, max)
        fidelity: Resolution in minutes
        start_ts: Start timestamp (Unix)
        end_ts: End timestamp (Unix)
    """
    url = f"{CLOB_BASE}/prices-history"
    params = {
        "market": token_id,
        "fidelity": fidelity
    }
    
    if start_ts and end_ts:
        params["startTs"] = start_ts
        params["endTs"] = end_ts
    else:
        params["interval"] = interval
    
    print(f"Fetching {url} with params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'List response'}")
            return data
        else:
            print(f"Error: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def analyze_data_quality(data, token_id, description=""):
    """Analyze price history data for quality issues"""
    
    if not data:
        return {"error": "No data received"}
    
    # Handle different response formats
    if isinstance(data, dict) and 'history' in data:
        history = data['history']
    elif isinstance(data, list):
        history = data
    else:
        return {"error": f"Unexpected data format: {type(data)}"}
    
    if not history:
        return {"error": "Empty history"}
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(history)
    
    # Check structure
    if 't' not in df.columns or 'p' not in df.columns:
        return {"error": f"Missing expected columns. Found: {list(df.columns)}"}
    
    # Convert timestamps
    df['timestamp'] = pd.to_datetime(df['t'], unit='s')
    df['price'] = df['p'].astype(float)
    
    # Calculate metrics
    analysis = {
        "token_id": token_id,
        "description": description,
        "total_points": len(df),
        "start_time": df['timestamp'].min().isoformat(),
        "end_time": df['timestamp'].max().isoformat(),
        "duration_hours": (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600,
        "price_range": [float(df['price'].min()), float(df['price'].max())],
        "price_mean": float(df['price'].mean()),
        "missing_data_gaps": 0,  # Will calculate below
        "data_sample": df.head(5).to_dict('records')
    }
    
    # Check for time gaps
    df_sorted = df.sort_values('timestamp')
    time_diffs = df_sorted['timestamp'].diff()
    median_diff = time_diffs.median()
    large_gaps = time_diffs[time_diffs > median_diff * 3]
    analysis["missing_data_gaps"] = len(large_gaps)
    analysis["median_interval_seconds"] = median_diff.total_seconds() if pd.notna(median_diff) else None
    
    return analysis, df

def test_api_endpoint():
    """Test 1: Basic API functionality with known markets"""
    
    print("\n" + "="*80)
    print("TEST 1: API ENDPOINT VALIDATION")
    print("="*80)
    
    # Test with a known market - let's try to get recent markets first
    # We'll use a well-known market token ID
    # For now, let's try a dummy ID to see the error format
    
    test_tokens = [
        # We need real token IDs - let me fetch from markets API first
    ]
    
    # First, get some real token IDs from the markets API
    print("\nFetching active markets to get real token IDs...")
    markets_url = f"{CLOB_BASE}/markets"
    try:
        resp = requests.get(markets_url, timeout=30)
        if resp.status_code == 200:
            markets = resp.json()
            print(f"Found {len(markets)} markets")
            
            # Get first 5 active markets with good volume
            test_markets = []
            for market in markets[:20]:  # Check first 20
                if 'tokens' in market and market.get('active', False):
                    # Get the YES token (usually index 0)
                    if len(market['tokens']) > 0:
                        token = market['tokens'][0]
                        test_markets.append({
                            'token_id': token['token_id'],
                            'outcome': token.get('outcome', 'Unknown'),
                            'question': market.get('question', 'Unknown')[:80]
                        })
                        
                        if len(test_markets) >= 5:
                            break
            
            print(f"\nSelected {len(test_markets)} markets for testing:")
            for i, m in enumerate(test_markets, 1):
                print(f"{i}. {m['outcome']}: {m['question']}")
            
            return test_markets
        else:
            print(f"Failed to fetch markets: {resp.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return []

def test_data_quality(test_markets):
    """Test 2: Validate data quality across multiple markets"""
    
    print("\n" + "="*80)
    print("TEST 2: DATA QUALITY VALIDATION")
    print("="*80)
    
    results = []
    
    for market in test_markets:
        token_id = market['token_id']
        description = f"{market['outcome']}: {market['question']}"
        
        print(f"\n--- Testing: {description}")
        
        # Test different fidelity settings
        for fidelity in [60, 360, 1440]:  # 1h, 6h, 1d
            print(f"\nFidelity: {fidelity} minutes")
            data = fetch_price_history(token_id, interval="1w", fidelity=fidelity)
            
            if data:
                analysis, df = analyze_data_quality(data, token_id, description)
                analysis['fidelity'] = fidelity
                results.append(analysis)
                
                print(f"✓ Points: {analysis['total_points']}")
                print(f"✓ Duration: {analysis['duration_hours']:.1f} hours")
                print(f"✓ Price range: {analysis['price_range']}")
                print(f"✓ Gaps detected: {analysis['missing_data_gaps']}")
            else:
                print(f"✗ Failed to fetch data")
            
            time.sleep(1)  # Rate limit courtesy
    
    return results

def main():
    """Run all tests and generate report"""
    
    print("POLYMARKET TIMESERIES API VALIDATION")
    print("Starting tests...")
    
    # Test 1: Get real market token IDs
    test_markets = test_api_endpoint()
    
    if not test_markets:
        print("\n❌ CRITICAL: Could not fetch test markets. Aborting.")
        sys.exit(1)
    
    # Test 2: Validate data quality
    quality_results = test_data_quality(test_markets)
    
    # Save results
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)
    
    with open('api_test_results.json', 'w') as f:
        json.dump({
            'test_markets': test_markets,
            'quality_results': quality_results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print("✓ Saved to api_test_results.json")
    
    # Generate summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if quality_results:
        print(f"✓ API is functional")
        print(f"✓ Tested {len(test_markets)} markets")
        print(f"✓ Retrieved {len(quality_results)} datasets")
        
        avg_points = sum(r['total_points'] for r in quality_results) / len(quality_results)
        print(f"✓ Average data points per dataset: {avg_points:.0f}")
        
        total_gaps = sum(r['missing_data_gaps'] for r in quality_results)
        print(f"⚠ Total data gaps detected: {total_gaps}")
    else:
        print("❌ No data retrieved - API may not be working")
    
    return test_markets, quality_results

if __name__ == "__main__":
    test_markets, results = main()
