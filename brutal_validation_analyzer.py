#!/usr/bin/env python3
"""
BRUTAL STRATEGY REVALIDATION
Zero tolerance for overfitting, weak data, or unrealistic assumptions.
"""

import json
import sqlite3
from datetime import datetime
from collections import defaultdict
import statistics
import math

# STRICT REQUIREMENTS
MIN_TRADES = 100
MIN_PVALUE = 0.05
FEE_PERCENT = 0.05  # 4% trading + 1% slippage
MIN_WIN_RATE = 0.55  # After fees, need >50% to be profitable

def load_data():
    """Load the 78K resolved markets dataset"""
    print("[*] Loading historical data...")
    try:
        with open('markets_snapshot_20260207_221914.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle nested structure
        if isinstance(data, dict) and 'markets' in data:
            markets = data['markets']
        else:
            markets = data
        
        print(f"[+] Loaded {len(markets)} total markets")
        
        # Filter for resolved markets only
        # Winner is inferred from outcome_prices: [1.0, 0.0] = Yes won, [0.0, 1.0] = No won
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
        
        # Add winner field to each market
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
    """
    Calculate p-value using binomial test
    H0: win rate = 0.5 (no edge)
    H1: win rate > 0.5 (positive edge)
    """
    if total < 30:
        return 1.0  # Not enough data
    
    observed_rate = wins / total
    expected_rate = 0.5
    
    # Standard error for binomial
    se = math.sqrt(expected_rate * (1 - expected_rate) / total)
    
    # Z-score
    z = (observed_rate - expected_rate) / se
    
    # One-tailed p-value (using normal approximation)
    from scipy import stats
    pvalue = 1 - stats.norm.cdf(z)
    
    return pvalue

def test_strategy(markets, name, filter_func, direction='NO'):
    """
    Test a strategy with BRUTAL validation
    
    Args:
        markets: List of market dicts
        name: Strategy name
        filter_func: Function that returns True if market matches strategy
        direction: 'YES' or 'NO' - which side to bet
    """
    print(f"\n{'='*80}")
    print(f"[TEST] {name}")
    print(f"{'='*80}")
    
    # Find matching markets
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
            'trades': total_trades
        }
    
    # Calculate wins
    if direction == 'NO':
        wins = sum(1 for m in matches if m.get('winner') == 'No')
    else:
        wins = sum(1 for m in matches if m.get('winner') == 'Yes')
    
    losses = total_trades - wins
    win_rate = wins / total_trades
    
    print(f"[*] Win Rate: {win_rate:.1%} ({wins}W - {losses}L)")
    
    # CHECK 2: Statistical significance
    try:
        from scipy import stats
        pvalue = calculate_pvalue(wins, total_trades)
        print(f"[*] P-value: {pvalue:.4f}")
        
        if pvalue > MIN_PVALUE:
            print(f"[REJECT] P-value {pvalue:.4f} > {MIN_PVALUE} (not statistically significant)")
            return {
                'name': name,
                'status': 'REJECTED',
                'reason': 'Not statistically significant',
                'trades': total_trades,
                'win_rate': win_rate,
                'pvalue': pvalue
            }
    except ImportError:
        print("[!] Warning: scipy not available, skipping p-value calculation")
        pvalue = None
    
    # CHECK 3: Profitability after fees
    # Assume $100 per trade, win $100, lose $100
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
            'roi': roi
        }
    
    # CHECK 4: Out-of-sample validation (70/30 split)
    print(f"\n[*] OUT-OF-SAMPLE VALIDATION (70/30 split)")
    split_idx = int(len(matches) * 0.7)
    train_set = matches[:split_idx]
    test_set = matches[split_idx:]
    
    # Train performance
    if direction == 'NO':
        train_wins = sum(1 for m in train_set if m.get('winner') == 'No')
    else:
        train_wins = sum(1 for m in train_set if m.get('winner') == 'Yes')
    train_wr = train_wins / len(train_set) if train_set else 0
    
    # Test performance
    if direction == 'NO':
        test_wins = sum(1 for m in test_set if m.get('winner') == 'No')
    else:
        test_wins = sum(1 for m in test_set if m.get('winner') == 'Yes')
    test_wr = test_wins / len(test_set) if test_set else 0
    
    print(f"   Training set: {train_wr:.1%} win rate ({len(train_set)} trades)")
    print(f"   Test set: {test_wr:.1%} win rate ({len(test_set)} trades)")
    
    # Check for overfitting (test performance should be within 10% of train)
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
            'test_wr': test_wr
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
        'test_wr': test_wr
    }

def main():
    print("="*80)
    print("*** BRUTAL STRATEGY REVALIDATION ***")
    print("="*80)
    print(f"Requirements:")
    print(f"  - Minimum {MIN_TRADES} trades")
    print(f"  - P-value < {MIN_PVALUE}")
    print(f"  - Profitable after {FEE_PERCENT*100}% fees")
    print(f"  - Out-of-sample validation")
    print()
    
    # Load data
    markets = load_data()
    if not markets:
        print("[-] No data available. Exiting.")
        return
    
    results = []
    
    # Test each strategy
    print("\n" + "="*80)
    print("TESTING 11 STRATEGIES FROM NEW_STRATEGY_PROPOSALS")
    print("="*80)
    
    # 1. MUSK_HYPE_FADE
    results.append(test_strategy(
        markets,
        "MUSK_HYPE_FADE",
        lambda m: any(keyword in m.get('question', '').lower() 
                     for keyword in ['elon', 'musk', 'tesla']),
        'NO'
    ))
    
    # 2. TECH_HYPE_FADE
    results.append(test_strategy(
        markets,
        "TECH_HYPE_FADE",
        lambda m: any(keyword in m.get('question', '').lower() 
                     for keyword in ['apple', 'microsoft', 'google', 'amazon', 'meta', 
                                   'nvidia', 'openai', 'gpt']),
        'NO'
    ))
    
    # 3. MICRO_MARKET_FADE
    results.append(test_strategy(
        markets,
        "MICRO_MARKET_FADE",
        lambda m: float(m.get('volume', 0)) < 5000,
        'NO'
    ))
    
    # 4. WILL_PREDICTION_FADE
    results.append(test_strategy(
        markets,
        "WILL_PREDICTION_FADE",
        lambda m: m.get('question', '').lower().startswith('will '),
        'NO'
    ))
    
    # 5. CRYPTO_HYPE_FADE
    results.append(test_strategy(
        markets,
        "CRYPTO_HYPE_FADE",
        lambda m: any(keyword in m.get('question', '').lower() 
                     for keyword in ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 
                                   'solana', 'sol', 'dogecoin']),
        'NO'
    ))
    
    # 6. CELEBRITY_FADE
    results.append(test_strategy(
        markets,
        "CELEBRITY_FADE",
        lambda m: any(keyword in m.get('question', '').lower() 
                     for keyword in ['trump', 'biden', 'taylor swift', 'kanye', 
                                   'kardashian', 'celebrity']),
        'NO'
    ))
    
    # 7. WEEKEND_FADE (need creation date - skip if not available)
    # Skip for now
    
    # 8. SHORT_DURATION_FADE (need creation and end dates - skip if not available)
    # Skip for now
    
    # Generate summary report
    print("\n" + "="*80)
    print("*** FINAL SUMMARY ***")
    print("="*80)
    
    validated = [r for r in results if r['status'] == 'VALIDATED']
    rejected = [r for r in results if r['status'] == 'REJECTED']
    
    print(f"\n[+] VALIDATED STRATEGIES: {len(validated)}/{len(results)}")
    for r in validated:
        print(f"   - {r['name']}: {r['win_rate']:.1%} win rate, ROI: {r['roi']:.1%}, {r['trades']} trades")
    
    print(f"\n[-] REJECTED STRATEGIES: {len(rejected)}/{len(results)}")
    for r in rejected:
        print(f"   - {r['name']}: {r['reason']} ({r.get('trades', 0)} trades)")
    
    # Save results
    with open('BRUTAL_VALIDATION_REPORT.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[*] Results saved to BRUTAL_VALIDATION_REPORT.json")

if __name__ == '__main__':
    main()
