#!/usr/bin/env python3
"""
Inspect the backtest dataset structure
"""

import json

def main():
    print("Loading backtest dataset...")
    with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
        data = json.load(f)
    
    print(f"Total markets: {len(data):,}")
    
    # Count closed markets with outcomes
    closed = [m for m in data if m.get('closed') and m.get('outcome')]
    print(f"Closed markets with outcomes: {len(closed):,}")
    print(f"Percentage: {len(closed)/len(data)*100:.1f}%")
    
    # Check outcome distribution
    outcomes = {}
    for m in closed:
        outcome = m.get('outcome')
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
    
    print(f"\nOutcome distribution:")
    for outcome, count in outcomes.items():
        print(f"  {outcome}: {count:,} ({count/len(closed)*100:.1f}%)")
    
    # Check first closed market
    if closed:
        print(f"\nFirst closed market sample:")
        m = closed[0]
        question = m.get('question', 'N/A')
        print(f"  Question: {question[:100]}...")
        print(f"  Outcome: {m.get('outcome')}")
        print(f"  Volume: {m.get('volume')}")
        print(f"  Price history length: {len(m.get('price_history', []))}")
        
        if m.get('price_history'):
            first = m['price_history'][0]
            last = m['price_history'][-1]
            print(f"  First price: {first.get('p', first.get('price'))} at {first.get('t')}")
            print(f"  Last price: {last.get('p', last.get('price'))} at {last.get('t')}")
            
            # Calculate profit if YES outcome
            if m['outcome'] == 'YES':
                profit = float(last.get('p', last.get('price', 0))) - float(first.get('p', first.get('price', 0)))
            else:
                profit = float(first.get('p', first.get('price', 0))) - float(last.get('p', last.get('price', 0)))
            print(f"  Profit (before costs): {profit:.4f}")
    
    # Check data quality
    print(f"\nData quality check:")
    print(f"Markets with price_history: {len([m for m in closed if m.get('price_history')]):,}")
    print(f"Markets with start_date: {len([m for m in closed if m.get('start_date')]):,}")
    print(f"Markets with end_date: {len([m for m in closed if m.get('end_date')]):,}")
    print(f"Markets with volume: {len([m for m in closed if m.get('volume')]):,}")
    
    # Check if we have enough data for analysis
    if len(closed) >= 100:
        print(f"\n✅ SUFFICIENT DATA: {len(closed):,} closed markets available for pattern analysis")
    else:
        print(f"\n❌ INSUFFICIENT DATA: Only {len(closed):,} closed markets - need at least 100 for reliable analysis")

if __name__ == '__main__':
    main()
