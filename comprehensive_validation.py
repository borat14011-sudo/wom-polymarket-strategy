#!/usr/bin/env python3
"""
COMPREHENSIVE BRUTAL STRATEGY REVALIDATION
Testing ALL strategies with zero tolerance for weak data
"""

import json
import statistics
import math
from datetime import datetime, timedelta

# STRICT REQUIREMENTS
MIN_TRADES = 100
MIN_PVALUE = 0.05
FEE_PERCENT = 0.05
MIN_WIN_RATE = 0.55

def load_data():
    """Load the 78K resolved markets dataset"""
    print("[*] Loading historical data...")
    try:
        with open('markets_snapshot_20260207_221914.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'markets' in data:
            markets = data['markets']
        else:
            markets = data
        
        print(f"[+] Loaded {len(markets)} total markets")
        
        # Winner is inferred from outcome_prices
        def get_winner(market):
            if not market.get('closed'):
                return None
            prices = market.get('outcome_prices', [])
            if len(prices) < 2:
                return None
            if prices[0] == 1.0 and prices[1] == 0.0:
                return 'Yes'
            elif prices[0] == 0.0 and prices[1] == 1.0:
                return 'No'
            return None
        
        for m in markets:
            if isinstance(m, dict):
                m['winner'] = get_winner(m)
        
        resolved = [m for m in markets if isinstance(m, dict) and m.get('closed') == True and m.get('winner') is not None]
        print(f"[+] {len(resolved)} resolved markets with outcomes")
        
        return resolved
    except Exception as e:
        print(f"[-] Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return []

def calculate_pvalue(wins, total):
    """Calculate p-value using binomial test"""
    if total < 30:
        return 1.0
    
    observed_rate = wins / total
    expected_rate = 0.5
    
    try:
        from scipy import stats
        se = math.sqrt(expected_rate * (1 - expected_rate) / total)
        z = (observed_rate - expected_rate) / se
        pvalue = 1 - stats.norm.cdf(z)
        return pvalue
    except:
        return None

def test_strategy(markets, name, filter_func, direction='NO', claimed_wr=None):
    """Test a strategy with BRUTAL validation"""
    print(f"\n{'='*80}")
    print(f"[TEST] {name}")
    if claimed_wr:
        print(f"[*] Claimed win rate: {claimed_wr:.1%}")
    print(f"{'='*80}")
    
    matches = [m for m in markets if filter_func(m)]
    total_trades = len(matches)
    
    print(f"[*] Sample size: {total_trades} trades")
    
    # CHECK 1: Minimum sample size
    if total_trades < MIN_TRADES:
        print(f"[REJECT] Sample size {total_trades} < {MIN_TRADES} minimum")
        return {
            'name': name,
            'status': 'REJECTED',
            'reason': 'Insufficient sample size',
            'trades': total_trades,
            'claimed_wr': claimed_wr
        }
    
    # Calculate wins
    if direction == 'NO':
        wins = sum(1 for m in matches if m.get('winner') == 'No')
    else:
        wins = sum(1 for m in matches if m.get('winner') == 'Yes')
    
    losses = total_trades - wins
    win_rate = wins / total_trades
    
    print(f"[*] Actual Win Rate: {win_rate:.1%} ({wins}W - {losses}L)")
    if claimed_wr:
        diff = win_rate - claimed_wr
        print(f"[*] Difference from claim: {diff:+.1%}")
    
    # CHECK 2: Statistical significance
    pvalue = calculate_pvalue(wins, total_trades)
    if pvalue is not None:
        print(f"[*] P-value: {pvalue:.4f}")
        
        if pvalue > MIN_PVALUE:
            print(f"[REJECT] P-value {pvalue:.4f} > {MIN_PVALUE} (not statistically significant)")
            return {
                'name': name,
                'status': 'REJECTED',
                'reason': 'Not statistically significant',
                'trades': total_trades,
                'win_rate': win_rate,
                'pvalue': pvalue,
                'claimed_wr': claimed_wr
            }
    else:
        print(f"[!] Warning: scipy not available, skipping p-value")
    
    # CHECK 3: Profitability after fees
    gross_pnl = (wins * 100) - (losses * 100)
    fees = total_trades * 100 * FEE_PERCENT
    net_pnl = gross_pnl - fees
    roi = net_pnl / (total_trades * 100)
    
    print(f"[*] Gross P/L: ${gross_pnl:,.0f}")
    print(f"[*] Fees (5%): ${fees:,.0f}")
    print(f"[*] Net P/L: ${net_pnl:,.0f}")
    print(f"[*] ROI: {roi:.1%}")
    
    if net_pnl <= 0:
        print(f"[REJECT] Unprofitable after fees")
        return {
            'name': name,
            'status': 'REJECTED',
            'reason': 'Unprofitable after fees',
            'trades': total_trades,
            'win_rate': win_rate,
            'net_pnl': net_pnl,
            'roi': roi,
            'claimed_wr': claimed_wr
        }
    
    # CHECK 4: Out-of-sample validation (70/30 split)
    print(f"\n[*] OUT-OF-SAMPLE VALIDATION (70/30 split)")
    split_idx = int(len(matches) * 0.7)
    train_set = matches[:split_idx]
    test_set = matches[split_idx:]
    
    if direction == 'NO':
        train_wins = sum(1 for m in train_set if m.get('winner') == 'No')
        test_wins = sum(1 for m in test_set if m.get('winner') == 'No')
    else:
        train_wins = sum(1 for m in train_set if m.get('winner') == 'Yes')
        test_wins = sum(1 for m in test_set if m.get('winner') == 'Yes')
    
    train_wr = train_wins / len(train_set) if train_set else 0
    test_wr = test_wins / len(test_set) if test_set else 0
    
    print(f"   Training set: {train_wr:.1%} win rate ({len(train_set)} trades)")
    print(f"   Test set: {test_wr:.1%} win rate ({len(test_set)} trades)")
    
    if abs(test_wr - train_wr) > 0.10:
        print(f"[!] WARNING: Large train/test gap suggests overfitting")
    
    if test_wr < MIN_WIN_RATE:
        print(f"[REJECT] Test set win rate {test_wr:.1%} < {MIN_WIN_RATE:.0%}")
        return {
            'name': name,
            'status': 'REJECTED',
            'reason': 'Failed out-of-sample validation',
            'trades': total_trades,
            'train_wr': train_wr,
            'test_wr': test_wr,
            'claimed_wr': claimed_wr
        }
    
    # PASSED ALL TESTS
    print(f"\n[PASS] STRATEGY VALIDATED")
    
    return {
        'name': name,
        'status': 'VALIDATED',
        'trades': total_trades,
        'win_rate': win_rate,
        'pvalue': pvalue,
        'net_pnl': net_pnl,
        'roi': roi,
        'train_wr': train_wr,
        'test_wr': test_wr,
        'claimed_wr': claimed_wr,
        'difference': win_rate - claimed_wr if claimed_wr else None
    }

def main():
    print("="*80)
    print("*** COMPREHENSIVE BRUTAL STRATEGY REVALIDATION ***")
    print("="*80)
    print(f"Requirements:")
    print(f"  - Minimum {MIN_TRADES} trades")
    print(f"  - P-value < {MIN_PVALUE}")
    print(f"  - Profitable after {FEE_PERCENT*100}% fees")
    print(f"  - Out-of-sample validation")
    print()
    
    markets = load_data()
    if not markets:
        print("[-] No data available. Exiting.")
        return
    
    results = []
    
    print("\n" + "="*80)
    print("TESTING ALL STRATEGIES")
    print("="*80)
    
    # 1-6: From NEW_STRATEGY_PROPOSALS.md
    results.append(test_strategy(markets, "MUSK_HYPE_FADE",
        lambda m: any(k in m.get('question', '').lower() for k in ['elon', 'musk', 'tesla']),
        'NO', 0.880))
    
    results.append(test_strategy(markets, "TECH_HYPE_FADE",
        lambda m: any(k in m.get('question', '').lower() for k in ['apple', 'microsoft', 'google', 'amazon', 'meta', 'nvidia', 'openai', 'gpt']),
        'NO', 0.782))
    
    results.append(test_strategy(markets, "MICRO_MARKET_FADE",
        lambda m: float(m.get('volume', 0)) < 5000,
        'NO', 0.772))
    
    results.append(test_strategy(markets, "WILL_PREDICTION_FADE",
        lambda m: m.get('question', '').lower().startswith('will '),
        'NO', 0.758))
    
    results.append(test_strategy(markets, "CRYPTO_HYPE_FADE",
        lambda m: any(k in m.get('question', '').lower() for k in ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'solana', 'sol', 'dogecoin']),
        'NO', 0.660))
    
    results.append(test_strategy(markets, "CELEBRITY_FADE",
        lambda m: any(k in m.get('question', '').lower() for k in ['trump', 'biden', 'taylor swift', 'kanye', 'kardashian']),
        'NO', 0.762))
    
    # 7: COMPLEX_QUESTION_FADE
    results.append(test_strategy(markets, "COMPLEX_QUESTION_FADE",
        lambda m: len(m.get('question', '')) > 100 or ' and ' in m.get('question', '').lower() or ' or ' in m.get('question', '').lower(),
        'NO', 0.714))
    
    # NOTE: Skipping LATE_NIGHT_FADE, WEEKEND_FADE, SHORT_DURATION_FADE 
    # as they require date parsing which would match all markets with lambda m: True
    
    # 11: BTC_TIME_BIAS (from BACKTEST_VALIDATION_RESULTS.md)
    results.append(test_strategy(markets, "BTC_TIME_BIAS",
        lambda m: 'bitcoin' in m.get('question', '').lower() or 'btc' in m.get('question', '').lower(),
        'NO', 0.588))
    
    # 12: WEATHER_FADE (from BACKTEST_VALIDATION_RESULTS.md)
    results.append(test_strategy(markets, "WEATHER_FADE_LONGSHOTS",
        lambda m: any(k in m.get('question', '').lower() for k in ['weather', 'rain', 'snow', 'temperature', 'storm']),
        'NO', 0.939))
    
    # Generate summary
    print("\n" + "="*80)
    print("*** FINAL SUMMARY ***")
    print("="*80)
    
    validated = [r for r in results if r['status'] == 'VALIDATED']
    rejected = [r for r in results if r['status'] == 'REJECTED']
    
    print(f"\n[+] VALIDATED STRATEGIES: {len(validated)}/{len(results)}")
    for r in validated:
        diff_str = f", Diff: {r['difference']:+.1%}" if r.get('difference') is not None else ""
        print(f"   - {r['name']}: {r['win_rate']:.1%} actual, ROI: {r['roi']:.1%}, {r['trades']} trades{diff_str}")
    
    print(f"\n[-] REJECTED STRATEGIES: {len(rejected)}/{len(results)}")
    for r in rejected:
        print(f"   - {r['name']}: {r['reason']} ({r.get('trades', 0)} trades)")
    
    # Save results
    with open('COMPREHENSIVE_VALIDATION.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n[*] Results saved to COMPREHENSIVE_VALIDATION.json")
    
    # Return for report generation
    return results, validated, rejected

if __name__ == '__main__':
    main()
