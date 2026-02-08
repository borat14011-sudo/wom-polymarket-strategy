"""
Backtest all strategies on REAL resolved markets
This will be our true validation
"""
import json
import re
from collections import defaultdict

# Our proven strategies
STRATEGIES = {
    'MUSK_FADE_EXTREMES': {
        'match': lambda q: bool(re.search(r'musk.*tweet', q, re.I)),
        'condition': lambda q: check_tweet_extreme(q),
        'direction': 'NO',
        'expected_win': 97.1
    },
    'WEATHER_FADE_LONGSHOTS': {
        'match': lambda q: bool(re.search(r'\btemperature\b|\bweather\b', q, re.I)),
        'condition': lambda q: True,  # Will check price < 0.30
        'direction': 'NO',
        'expected_win': 93.9
    },
    'ALTCOIN_FADE_HIGH': {
        'match': lambda q: bool(re.search(r'\bsolana\b|\bxrp\b|\bcardano\b', q, re.I)),
        'condition': lambda q: True,  # Will check price > 0.70
        'direction': 'NO',
        'expected_win': 92.3
    },
    'CRYPTO_FAVORITE_FADE': {
        'match': lambda q: bool(re.search(r'\bbitcoin\b.*\$\d+', q, re.I)),
        'condition': lambda q: True,  # Will check price > 0.70
        'direction': 'NO',
        'expected_win': 61.9
    },
    'BTC_TIME_BIAS': {
        'match': lambda q: bool(re.search(r'\bbitcoin\s+up\s+or\s+down\b', q, re.I)),
        'condition': lambda q: True,
        'direction': 'VARIES',
        'expected_win': 58.9
    }
}

def check_tweet_extreme(question):
    """Check if Musk tweet range is extreme"""
    match = re.search(r'(\d+)-(\d+)\s+tweets', question, re.I)
    if not match:
        return False
    
    low = int(match.group(1))
    high = int(match.group(2))
    
    return low < 40 or high > 200

def get_price_info(market):
    """Extract price information from market"""
    # Check for price_histories (dict with token_id keys)
    price_histories = market.get('price_histories', {})
    
    if price_histories:
        # Get first token's price history
        token_ids = market.get('clob_token_ids', [])
        if token_ids:
            token_id = token_ids[0]  # YES token usually first
            prices = price_histories.get(token_id, [])
            
            if prices and len(prices) > 0:
                # prices format: list of {'t': timestamp, 'p': price}
                price_values = [p['p'] for p in prices if isinstance(p, dict) and 'p' in p]
                
                if price_values:
                    initial = price_values[0]
                    max_price = max(price_values)
                    final = price_values[-1]
                    return initial, max_price, final
    
    # Fallback: try old format
    prices = market.get('price_history', market.get('prices', []))
    
    if not prices:
        return None, None, None
    
    # Extract price values
    price_values = []
    for p in prices:
        if isinstance(p, dict):
            if 'p' in p:
                price_values.append(p['p'])
            elif 'price' in p:
                price_values.append(p['price'])
        elif isinstance(p, (int, float)):
            price_values.append(p)
    
    if not price_values:
        return None, None, None
    
    initial = price_values[0]
    max_price = max(price_values)
    final = price_values[-1]
    
    return initial, max_price, final

def check_outcome(market, direction):
    """Check if bet won using outcome_prices"""
    outcome_prices = market.get('outcome_prices')
    
    if not outcome_prices or len(outcome_prices) < 2:
        return None  # Not resolved
    
    # outcome_prices format: ["1", "0"] means YES won, NO lost
    # ["0", "1"] means YES lost, NO won
    
    yes_won = outcome_prices[0] == "1"
    no_won = outcome_prices[1] == "1"
    
    if direction == 'NO':
        return no_won
    elif direction == 'YES':
        return yes_won
    
    return None

def main():
    print("="*80)
    print("[BACKTEST] All Strategies on Resolved Markets")
    print("="*80)
    
    # Load resolved markets (from extract script)
    print("\n[LOAD] polymarket_complete.json (30-60 seconds)...")
    
    with open('historical-data-scraper/data/polymarket_complete.json', 'r') as f:
        events = json.load(f)
    
    print(f"[OK] Loaded {len(events)} events")
    
    # Flatten markets
    print("\n[FLATTEN] Extracting markets...")
    resolved_markets = []
    
    for event in events:
        if not event.get('closed'):
            continue
        
        for market in event.get('markets', []):
            # Check if resolved using outcome_prices
            outcome_prices = market.get('outcome_prices')
            if outcome_prices and len(outcome_prices) >= 2:
                if "1" in outcome_prices:  # Market resolved
                    resolved_markets.append(market)
    
    print(f"[OK] Found {len(resolved_markets)} resolved markets")
    
    # Backtest each strategy
    print("\n" + "="*80)
    print("[BACKTESTING]")
    print("="*80)
    
    results = {}
    
    for strategy_name, params in STRATEGIES.items():
        print(f"\n[STRATEGY] {strategy_name}")
        print(f"  Expected win rate: {params['expected_win']:.1f}%")
        
        trades = []
        
        for market in resolved_markets:
            # Get question
            question = market.get('question', market.get('title', ''))
            
            # Check if matches strategy category
            if not params['match'](question):
                continue
            
            # Check strategy condition
            if not params['condition'](question):
                continue
            
            # Get price info
            initial, max_price, final = get_price_info(market)
            
            if initial is None:
                continue  # No price data
            
            # Strategy-specific entry logic
            enter_trade = False
            
            if strategy_name == 'MUSK_FADE_EXTREMES':
                enter_trade = True  # Always enter if extreme range
            elif strategy_name in ['WEATHER_FADE_LONGSHOTS']:
                enter_trade = initial < 0.30  # Enter if longshot
            elif strategy_name in ['ALTCOIN_FADE_HIGH', 'CRYPTO_FAVORITE_FADE']:
                enter_trade = max_price > 0.70  # Enter if ever >70%
            elif strategy_name == 'BTC_TIME_BIAS':
                enter_trade = True  # Simplified for now
            
            if not enter_trade:
                continue
            
            # Check outcome
            won = check_outcome(market, params['direction'])
            
            if won is not None:
                trades.append({
                    'question': question,
                    'outcome': market.get('outcome'),
                    'initial_price': initial,
                    'max_price': max_price,
                    'won': won
                })
        
        # Calculate results
        total = len(trades)
        wins = sum(1 for t in trades if t['won'])
        losses = total - wins
        
        actual_win_rate = wins / total * 100 if total > 0 else 0
        expected = params['expected_win']
        diff = actual_win_rate - expected
        
        print(f"\n  Trades: {total}")
        print(f"  Wins: {wins}")
        print(f"  Losses: {losses}")
        print(f"  Actual win rate: {actual_win_rate:.1f}%")
        print(f"  Expected: {expected:.1f}%")
        print(f"  Difference: {diff:+.1f}%")
        
        if total >= 10:
            if abs(diff) <= 10:
                print(f"  STATUS: ✓ VALIDATED (within 10%)")
            elif diff > 0:
                print(f"  STATUS: ✓✓ OUTPERFORMED")
            else:
                print(f"  STATUS: ✗ UNDERPERFORMED")
        else:
            print(f"  STATUS: ? TOO FEW TRADES")
        
        # Show samples
        if trades:
            print(f"\n  Sample trades:")
            for t in trades[:3]:
                result = "WIN" if t['won'] else "LOSS"
                print(f"    [{result}] {t['question'][:60]}")
                print(f"           Initial: {t['initial_price']:.3f}, Max: {t['max_price']:.3f}")
        
        results[strategy_name] = {
            'trades': total,
            'wins': wins,
            'actual_win_rate': actual_win_rate,
            'expected_win_rate': expected,
            'validated': total >= 10 and abs(diff) <= 10
        }
    
    # Final summary
    print(f"\n{'='*80}")
    print("[FINAL SUMMARY]")
    print('='*80)
    
    validated_count = sum(1 for r in results.values() if r['validated'])
    
    for name, res in results.items():
        status = "✓" if res['validated'] else ("?" if res['trades'] < 10 else "✗")
        print(f"  {status} {name:30} {res['actual_win_rate']:5.1f}% ({res['trades']:4} trades)")
    
    print(f"\n  Strategies validated: {validated_count}/{len(STRATEGIES)}")
    
    if validated_count >= 3:
        print(f"\n  OVERALL: ✓✓✓ STRONG VALIDATION")
    elif validated_count >= 2:
        print(f"\n  OVERALL: ✓ PARTIAL VALIDATION")
    else:
        print(f"\n  OVERALL: NEEDS MORE DATA")

if __name__ == "__main__":
    main()
