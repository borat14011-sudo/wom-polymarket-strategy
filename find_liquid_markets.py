#!/usr/bin/env python3
"""
Find liquid markets for test trading
"""

import json

def main():
    print("="*60)
    print("FINDING LIQUID MARKETS FOR TEST TRADING")
    print("="*60)
    
    try:
        with open('active-markets.json', 'r') as f:
            data = json.load(f)
        
        # Find markets with volume > 1000
        markets_with_volume = []
        markets_data = data.get('markets', [])
        
        for market in markets_data:
            volume = market.get('volume24h', 0)
            if volume > 1000:
                markets_with_volume.append({
                    'conditionId': market['conditionId'],
                    'question': market.get('question', 'Unknown'),
                    'volume24h': volume,
                    'yesPrice': market.get('yesPrice', 0),
                    'noPrice': market.get('noPrice', 0),
                    'slug': market.get('slug', '')
                })
        
        print(f'\nFound {len(markets_with_volume)} markets with >$1000 volume')
        print('\nTop 10 markets by volume:')
        print('-'*80)
        
        for i, m in enumerate(sorted(markets_with_volume, key=lambda x: x['volume24h'], reverse=True)[:10]):
            print(f'{i+1}. {m["question"][:80]}...')
            print(f'   Condition ID: {m["conditionId"][:20]}...')
            print(f'   Volume: ${m["volume24h"]:,.0f}')
            print(f'   YES Price: {m["yesPrice"]:.3f} | NO Price: {m["noPrice"]:.3f}')
            print(f'   Slug: {m["slug"]}')
            print()
            
        # Also find markets in the 8-20% or 80-92% range (good for longshots/favorites)
        print('\n' + '='*60)
        print('MARKETS IN OPTIMAL PRICE RANGES (avoiding slippage extremes)')
        print('='*60)
        
        optimal_markets = []
        for m in markets_with_volume:
            yes_price = m['yesPrice']
            no_price = m['noPrice']
            
            # Check if YES is in longshot range (8-20%) or NO is in favorite range (80-92%)
            if 0.08 <= yes_price <= 0.20 or 0.80 <= no_price <= 0.92:
                optimal_markets.append(m)
        
        print(f'\nFound {len(optimal_markets)} markets in optimal price ranges')
        print('\nTop 5 optimal markets:')
        print('-'*80)
        
        for i, m in enumerate(sorted(optimal_markets, key=lambda x: x['volume24h'], reverse=True)[:5]):
            yes_price = m['yesPrice']
            no_price = m['noPrice']
            range_type = "LONGSHOT (YES 8-20%)" if 0.08 <= yes_price <= 0.20 else "FAVORITE (NO 80-92%)"
            
            print(f'{i+1}. {m["question"][:80]}...')
            print(f'   Type: {range_type}')
            print(f'   Condition ID: {m["conditionId"][:20]}...')
            print(f'   Volume: ${m["volume24h"]:,.0f}')
            print(f'   YES: {yes_price:.3f} | NO: {no_price:.3f}')
            print()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()