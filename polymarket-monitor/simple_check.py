#!/usr/bin/env python3
"""
Simple check of backtest dataset
"""

import json

def main():
    # Load data
    with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
        data = json.load(f)
    
    print(f'Loaded {len(data)} markets')
    print('='*60)
    
    # Count outcomes
    outcomes = {}
    for market in data:
        outcome = market.get('outcome', 'missing')
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
    
    print('Outcome distribution:')
    for outcome, count in outcomes.items():
        print(f'  {outcome}: {count} markets ({count/len(data)*100:.1f}%)')
    
    # Find resolved markets
    print('\nLooking for resolved markets...')
    resolved_markets = []
    for market in data:
        outcome = market.get('outcome')
        if outcome in ['YES', 'NO']:
            resolved_markets.append(market)
    
    print(f'Found {len(resolved_markets)} resolved markets')
    
    if resolved_markets:
        print('\nSample resolved market:')
        market = resolved_markets[0]
        print(f'  Question: {market["question"][:80]}...')
        print(f'  Outcome: {market["outcome"]}')
        
        if 'price_history' in market and market['price_history']:
            prices = market['price_history']
            first_p = None
            last_p = None
            for price in prices:
                p_val = price.get('p')
                if p_val is not None:
                    if first_p is None:
                        first_p = p_val
                    last_p = p_val
            
            if first_p is not None and last_p is not None:
                print(f'  First price: {first_p}')
                print(f'  Last price: {last_p}')
                
                if market['outcome'] == 'YES':
                    profit = last_p - first_p
                else:
                    profit = first_p - last_p
                
                print(f'  Profit: {profit:.4f}')
                print(f'  Edge after 4% costs: {profit - 0.04:.4f}')

if __name__ == '__main__':
    main()