"""
Backtest the 6 BTC signals on REAL historical data
Match markets to price history and validate strategy
"""
import json
import sqlite3
from datetime import datetime

def load_backtest_dataset():
    """Load the main backtest dataset"""
    print("[LOAD] backtest_dataset_v1.json")
    
    with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
        data = json.load(f)
    
    print(f"  Type: {type(data)}")
    
    if isinstance(data, list):
        print(f"  Markets: {len(data)}")
        if data:
            print(f"  Sample keys: {list(data[0].keys())}")
            print(f"  Sample question: {data[0].get('question', 'N/A')[:80]}")
        return data
    else:
        print(f"  Unexpected format")
        return []

def find_btc_markets_in_dataset(dataset):
    """Find our 6 BTC signals in the historical dataset"""
    
    btc_targets = ['$200,000', '$150,000', '$190,000', '$180,000', '$160,000', '$170,000']
    
    print("\n[SEARCH] Looking for BTC price target markets...")
    
    matches = []
    
    for market in dataset:
        question = market.get('question', '')
        
        # Check if it matches our BTC targets
        for target in btc_targets:
            if target in question and 'Bitcoin' in question and 'December 31, 2026' in question:
                matches.append(market)
                print(f"  Found: {question[:70]}")
                break
    
    print(f"\n[RESULT] Found {len(matches)}/{len(btc_targets)} matches")
    return matches

def analyze_price_history(market):
    """Analyze a market's price history for strategy validation"""
    question = market.get('question', 'Unknown')
    prices = market.get('prices', [])
    
    if not prices:
        print(f"\n[MARKET] {question[:70]}")
        print(f"  No price history available")
        return None
    
    print(f"\n[MARKET] {question[:70]}")
    print(f"  Price snapshots: {len(prices)}")
    
    # Extract price values
    price_values = []
    for p in prices:
        if isinstance(p, dict) and 'p' in p:
            price_values.append(p['p'])
        elif isinstance(p, (int, float)):
            price_values.append(p)
    
    if not price_values:
        print(f"  No valid prices found")
        return None
    
    # Calculate stats
    initial_price = price_values[0]
    max_price = max(price_values)
    min_price = min(price_values)
    final_price = price_values[-1]
    
    # Check if ever >70% (strategy trigger)
    over_70_count = sum(1 for p in price_values if p > 0.70)
    
    print(f"  Initial: {initial_price:.3f}")
    print(f"  Max: {max_price:.3f}")
    print(f"  Min: {min_price:.3f}")
    print(f"  Final: {final_price:.3f}")
    print(f"  Times >70%: {over_70_count}/{len(price_values)}")
    
    # Strategy check: CRYPTO_FAVORITE_FADE
    # Entry: price > 0.70
    # Direction: NO (bet it won't happen)
    
    if max_price > 0.70:
        print(f"  STRATEGY TRIGGER: YES (reached {max_price:.3f})")
        
        # Check outcome
        outcome = market.get('outcome', market.get('resolved', 'Unknown'))
        print(f"  Outcome: {outcome}")
        
        # Did strategy win?
        if outcome in ['NO', 'No', 'no', False, 'false', 0]:
            print(f"  Result: WIN (bet NO, market resolved NO)")
            return 'WIN'
        elif outcome in ['YES', 'Yes', 'yes', True, 'true', 1]:
            print(f"  Result: LOSS (bet NO, market resolved YES)")
            return 'LOSS'
        else:
            print(f"  Result: UNKNOWN (market not resolved yet)")
            return 'PENDING'
    else:
        print(f"  STRATEGY TRIGGER: NO (never reached 70%)")
        return 'NO_ENTRY'

def main():
    print("="*80)
    print("[BACKTEST] BTC Signals on Real Historical Data")
    print("="*80)
    
    # Load dataset
    dataset = load_backtest_dataset()
    
    if not dataset:
        print("[ERROR] No data loaded")
        return
    
    # Find our 6 BTC markets
    btc_markets = find_btc_markets_in_dataset(dataset)
    
    if not btc_markets:
        print("\n[INFO] Markets not found in historical dataset")
        print("[NOTE] They might be too recent (after data collection)")
        return
    
    # Backtest each market
    print("\n" + "="*80)
    print("[BACKTEST RESULTS]")
    print("="*80)
    
    results = {'WIN': 0, 'LOSS': 0, 'PENDING': 0, 'NO_ENTRY': 0}
    
    for market in btc_markets:
        result = analyze_price_history(market)
        if result:
            results[result] += 1
    
    # Summary
    print("\n" + "="*80)
    print("[SUMMARY]")
    print("="*80)
    
    total_trades = results['WIN'] + results['LOSS']
    
    print(f"  Markets analyzed: {len(btc_markets)}")
    print(f"  Strategy triggered: {results['WIN'] + results['LOSS'] + results['PENDING']}")
    print(f"  No entry (never >70%): {results['NO_ENTRY']}")
    print(f"\n  Trades taken: {total_trades}")
    print(f"  Wins: {results['WIN']}")
    print(f"  Losses: {results['LOSS']}")
    print(f"  Pending: {results['PENDING']}")
    
    if total_trades > 0:
        win_rate = results['WIN'] / total_trades * 100
        print(f"\n  WIN RATE: {win_rate:.1f}%")
        print(f"  Expected (CRYPTO_FAVORITE_FADE): 61.9%")
        
        if win_rate >= 55:
            print(f"\n  STATUS: VALIDATED ✓")
        else:
            print(f"\n  STATUS: UNDERPERFORMED")

if __name__ == "__main__":
    main()
