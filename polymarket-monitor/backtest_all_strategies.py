"""
Backtest ALL event-driven strategies on 17K historical markets
Real data, real outcomes, real validation
"""
import json
import re
from collections import defaultdict

# All proven strategies
STRATEGIES = {
    'MUSK_FADE_EXTREMES': {
        'category_pattern': r'\bmusk\b.*tweet',
        'condition': lambda q, prices: check_tweet_range(q, '<40 or >200'),
        'direction': 'NO',
        'expected_win_rate': 0.971
    },
    'WEATHER_FADE_LONGSHOTS': {
        'category_pattern': r'\btemperature\b|\bdegrees\b|\bweather\b',
        'condition': lambda q, prices: get_initial_price(prices) < 0.30,
        'direction': 'NO',
        'expected_win_rate': 0.939
    },
    'ALTCOIN_FADE_HIGH': {
        'category_pattern': r'\bsolana\b|\bxrp\b|\bcardano\b',
        'condition': lambda q, prices: get_initial_price(prices) > 0.70,
        'direction': 'NO',
        'expected_win_rate': 0.923
    },
    'CRYPTO_FAVORITE_FADE': {
        'category_pattern': r'\bbitcoin\b.*\$\d+',
        'condition': lambda q, prices: get_initial_price(prices) > 0.70,
        'direction': 'NO',
        'expected_win_rate': 0.619
    },
    'BTC_TIME_BIAS': {
        'category_pattern': r'\bbitcoin\s+up\s+or\s+down\b',
        'condition': lambda q, prices: check_time_bias(q),
        'direction': 'VARIES',
        'expected_win_rate': 0.589
    }
}

def get_initial_price(prices):
    """Extract initial price from price history"""
    if not prices:
        return 0.5
    
    if isinstance(prices[0], dict) and 'p' in prices[0]:
        return prices[0]['p']
    elif isinstance(prices[0], (int, float)):
        return prices[0]
    
    return 0.5

def check_tweet_range(question, criteria):
    """Check if Musk tweet market is in extreme range"""
    match = re.search(r'(\d+)-(\d+)\s+tweets', question, re.I)
    if not match:
        return False
    
    low = int(match.group(1))
    high = int(match.group(2))
    
    return low < 40 or high > 200

def check_time_bias(question):
    """Check if BTC up/down has time bias (simplified)"""
    # For now, just return False (we'd need timestamp analysis)
    return False

def check_outcome(outcome, direction):
    """Check if bet won"""
    if direction == 'NO':
        return outcome in ['NO', 'No', 'no', False, 'false', 0, 'False']
    elif direction == 'YES':
        return outcome in ['YES', 'Yes', 'yes', True, 'true', 1, 'True']
    
    return False

def main():
    print("="*80)
    print("[BACKTEST] All Strategies on 17K Historical Markets")
    print("="*80)
    
    # Load dataset
    print("\n[LOAD] backtest_dataset_v1.json (this may take 30-60 seconds)...")
    
    with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
        markets = json.load(f)
    
    print(f"[OK] Loaded {len(markets)} markets")
    
    # Backtest each strategy
    results = {}
    
    for strategy_name, params in STRATEGIES.items():
        print(f"\n{'='*80}")
        print(f"[STRATEGY] {strategy_name}")
        print(f"  Expected win rate: {params['expected_win_rate']*100:.1f}%")
        print('='*80)
        
        matches = 0
        trades = []
        
        # Find markets matching this strategy
        for market in markets:
            question = market.get('question', '')
            
            # Check category pattern
            if not re.search(params['category_pattern'], question, re.I):
                continue
            
            matches += 1
            
            # Check strategy condition
            prices = market.get('price_history', [])
            
            try:
                if params['condition'](question, prices):
                    # This is a trade!
                    outcome = market.get('outcome')
                    direction = params['direction']
                    
                    if outcome is not None:
                        won = check_outcome(outcome, direction)
                        trades.append({
                            'question': question,
                            'outcome': outcome,
                            'won': won
                        })
            except:
                pass  # Skip markets with bad data
        
        # Calculate results
        total_trades = len(trades)
        wins = sum(1 for t in trades if t['won'])
        losses = total_trades - wins
        
        actual_win_rate = wins / total_trades if total_trades > 0 else 0
        
        print(f"\n[RESULTS]")
        print(f"  Markets matched: {matches}")
        print(f"  Trades taken: {total_trades}")
        print(f"  Wins: {wins}")
        print(f"  Losses: {losses}")
        print(f"  Actual win rate: {actual_win_rate*100:.1f}%")
        print(f"  Expected: {params['expected_win_rate']*100:.1f}%")
        
        diff = actual_win_rate - params['expected_win_rate']
        if total_trades >= 10:
            if abs(diff) < 0.10:
                print(f"  STATUS: VALIDATED ✓ (within 10%)")
            elif diff > 0:
                print(f"  STATUS: OUTPERFORMED ({diff*100:+.1f}%)")
            else:
                print(f"  STATUS: UNDERPERFORMED ({diff*100:+.1f}%)")
        else:
            print(f"  STATUS: TOO FEW TRADES (need >=10)")
        
        # Show sample trades
        if trades:
            print(f"\n  Sample trades:")
            for t in trades[:3]:
                result = "WIN" if t['won'] else "LOSS"
                print(f"    [{result}] {t['question'][:65]}")
        
        results[strategy_name] = {
            'matches': matches,
            'trades': total_trades,
            'wins': wins,
            'actual_win_rate': actual_win_rate,
            'expected_win_rate': params['expected_win_rate']
        }
    
    # Final summary
    print(f"\n{'='*80}")
    print("[OVERALL SUMMARY]")
    print('='*80)
    
    total_validated = 0
    total_strategies = len(STRATEGIES)
    
    for name, res in results.items():
        if res['trades'] >= 10:
            diff = abs(res['actual_win_rate'] - res['expected_win_rate'])
            if diff < 0.10:
                total_validated += 1
                status = "✓"
            else:
                status = "✗"
        else:
            status = "?"
        
        print(f"  {status} {name:30} {res['actual_win_rate']*100:5.1f}% ({res['trades']:3} trades)")
    
    print(f"\n  Strategies validated: {total_validated}/{total_strategies}")
    
    if total_validated >= total_strategies * 0.6:
        print(f"\n  OVERALL STATUS: STRONG VALIDATION ✓✓✓")
    elif total_validated >= total_strategies * 0.4:
        print(f"\n  OVERALL STATUS: PARTIAL VALIDATION ✓")
    else:
        print(f"\n  OVERALL STATUS: NEEDS MORE RESEARCH")

if __name__ == "__main__":
    main()
