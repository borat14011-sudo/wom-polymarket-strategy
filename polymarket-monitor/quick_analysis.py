#!/usr/bin/env python3
"""
Quick analysis of backtest dataset
"""

import json
import statistics

def main():
    # Load data
    with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
        data = json.load(f)
    
    print(f'Loaded {len(data)} markets')
    print('='*60)
    
    # Analyze first 10 markets in detail
    print('Analyzing first 10 markets:')
    print('-'*60)
    
    profits = []
    
    for i, market in enumerate(data[:10]):
        print(f'\nMarket {i+1}: {market["question"][:80]}...')
        print(f'  Outcome: {market.get("outcome", "N/A")}')
        
        if 'price_history' not in market:
            print('  No price history')
            continue
        
        prices = market['price_history']
        print(f'  Price history entries: {len(prices)}')
        
        if len(prices) < 2:
            print('  Not enough price data')
            continue
        
        # Show first and last prices
        first_price = None
        last_price = None
        
        for price in prices:
            p_val = price.get('p')
            if p_val is not None:
                if first_price is None:
                    first_price = p_val
                last_price = p_val
        
        if first_price is None or last_price is None:
            print('  No valid prices found')
            continue
        
        print(f'  First price: {first_price}')
        print(f'  Last price: {last_price}')
        
        # Calculate profit
        outcome = market.get('outcome')
        if outcome == 'YES':
            profit = last_price - first_price
            print(f'  Profit (YES): {profit:.4f}')
        elif outcome == 'NO':
            profit = first_price - last_price
            print(f'  Profit (NO): {profit:.4f}')
        else:
            print(f'  Unknown outcome: {outcome}')
            continue
        
        profits.append(profit)
    
    print('\n' + '='*60)
    print('SUMMARY:')
    print(f'Markets analyzed: 10')
    print(f'Valid profit calculations: {len(profits)}')
    
    if profits:
        avg_profit = statistics.mean(profits)
        win_rate = len([p for p in profits if p > 0]) / len(profits)
        edge_after_costs = avg_profit - 0.04
        
        print(f'\nAverage profit: ${avg_profit:.4f}')
        print(f'Win rate: {win_rate:.1%}')
        print(f'Edge after 4% costs: ${edge_after_costs:.4f} ({edge_after_costs*100:.2f}%)')

if __name__ == '__main__':
    main()