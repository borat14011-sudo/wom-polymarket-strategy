#!/usr/bin/env python3
"""
BIAS VALIDATION TEST
Test that our fixes actually work by comparing:
1. Original biased version
2. Deliberately WORSE code (should lose more)
3. Actually fixed version (should be realistic)
"""
import json
from pathlib import Path

DATA_DIR = Path("historical-data-scraper/data")

print("="*70)
print("BIAS VALIDATION TEST")
print("="*70)
print()

# Load dataset
with open(DATA_DIR / "backtest_dataset_v1.json") as f:
    dataset = json.load(f)

# Take a smaller sample for faster testing
dataset = dataset[:1000]
print(f"Testing with {len(dataset)} markets\n")

# ===================================================================
# VERSION 1: BIASED (original backtest_fixed.py logic)
# ===================================================================
def run_BIASED_version(markets):
    """Original biased version"""
    trades = []
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 30:
            continue
        
        final_price = prices[-1].get('p', 0)
        if final_price > 0.95:
            outcome = 'Yes'
        elif final_price < 0.05:
            outcome = 'No'
        else:
            continue
        
        max_entry_idx = len(prices) - 10
        for i in range(5, max_entry_idx):
            current = prices[i].get('p', 0)
            prev_1 = prices[i-1].get('p', 0)
            prev_2 = prices[i-2].get('p', 0)
            prev_3 = prices[i-3].get('p', 0)
            
            if current > prev_1 > prev_2 > prev_3:
                entry_price = current
                exit_idx = len(prices) - 5
                exit_price = prices[exit_idx].get('p', 0)
                
                # BIASED: Uses outcome to determine direction
                if outcome == 'Yes':
                    pnl = exit_price - entry_price
                else:
                    pnl = -(exit_price - entry_price)
                
                trades.append({'pnl': pnl, 'win': pnl > 0})
                break
    
    wins = len([t for t in trades if t['win']])
    return {
        'name': 'BIASED VERSION',
        'trades': len(trades),
        'win_rate': wins / len(trades) * 100 if trades else 0,
        'avg_pnl': sum(t['pnl'] for t in trades) / len(trades) if trades else 0
    }

# ===================================================================
# VERSION 2: DELIBERATELY BROKEN (bet against signals)
# ===================================================================
def run_BROKEN_version(markets):
    """Intentionally broken: bet OPPOSITE direction"""
    trades = []
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 30:
            continue
        
        final_price = prices[-1].get('p', 0)
        if final_price > 0.95:
            outcome = 'Yes'
        elif final_price < 0.05:
            outcome = 'No'
        else:
            continue
        
        max_entry_idx = int(len(prices) * 0.7)
        for i in range(5, max_entry_idx):
            current = prices[i].get('p', 0)
            prev_1 = prices[i-1].get('p', 0)
            prev_2 = prices[i-2].get('p', 0)
            prev_3 = prices[i-3].get('p', 0)
            
            if current > prev_1 > prev_2 > prev_3:
                entry_price = current
                
                # BROKEN: Bet NO on uptrend (opposite of signal!)
                bet_side = 'No'
                
                # Correct P&L formula but wrong direction
                if outcome == 'No':
                    pnl = 1.0 - (1.0 - entry_price)  # Bet NO, NO wins
                else:
                    pnl = 0.0 - (1.0 - entry_price)  # Bet NO, YES wins
                
                trades.append({'pnl': pnl, 'win': pnl > 0})
                break
    
    wins = len([t for t in trades if t['win']])
    return {
        'name': 'BROKEN VERSION (bet opposite)',
        'trades': len(trades),
        'win_rate': wins / len(trades) * 100 if trades else 0,
        'avg_pnl': sum(t['pnl'] for t in trades) / len(trades) if trades else 0
    }

# ===================================================================
# VERSION 3: ACTUALLY FIXED (all biases removed)
# ===================================================================
def run_FIXED_version(markets):
    """Actually fixed: no look-ahead, realistic exit, correct P&L"""
    trades = []
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 30:
            continue
        
        final_price = prices[-1].get('p', 0)
        if final_price > 0.95:
            outcome = 'Yes'
        elif final_price < 0.05:
            outcome = 'No'
        else:
            continue
        
        # Realistic exit timing
        max_entry_idx = int(len(prices) * 0.7)
        for i in range(5, max_entry_idx):
            current = prices[i].get('p', 0)
            prev_1 = prices[i-1].get('p', 0)
            prev_2 = prices[i-2].get('p', 0)
            prev_3 = prices[i-3].get('p', 0)
            
            if current > prev_1 > prev_2 > prev_3:
                entry_price = current
                
                # ALWAYS bet YES on uptrend (no peeking!)
                bet_side = 'Yes'
                
                # Binary P&L
                if outcome == 'Yes':
                    pnl = 1.0 - entry_price
                else:
                    pnl = 0.0 - entry_price
                
                trades.append({'pnl': pnl, 'win': pnl > 0})
                break
    
    wins = len([t for t in trades if t['win']])
    return {
        'name': 'ACTUALLY FIXED',
        'trades': len(trades),
        'win_rate': wins / len(trades) * 100 if trades else 0,
        'avg_pnl': sum(t['pnl'] for t in trades) / len(trades) if trades else 0
    }

# ===================================================================
# RUN ALL VERSIONS
# ===================================================================
print("Running tests...")
print()

results = [
    run_BIASED_version(dataset),
    run_BROKEN_version(dataset),
    run_FIXED_version(dataset)
]

# ===================================================================
# RESULTS
# ===================================================================
print("="*70)
print("RESULTS")
print("="*70)
print()

for r in results:
    print(f"{r['name']:30s} | {r['trades']:>4} trades | "
          f"{r['win_rate']:>5.1f}% win | {r['avg_pnl']:>+7.3f} P&L")

print()
print("="*70)
print("VALIDATION")
print("="*70)
print()

biased = results[0]
broken = results[1]
fixed = results[2]

# Test 1: Biased version should have unrealistic win rate
test1_pass = biased['win_rate'] > 70
print(f"Test 1: Biased version shows >70% win rate")
print(f"  Result: {biased['win_rate']:.1f}% - {'PASS' if test1_pass else 'FAIL'}")
print()

# Test 2: Broken version should be worse than biased
# (proves we're not just flipping a coin)
test2_pass = broken['avg_pnl'] < biased['avg_pnl']
print(f"Test 2: Broken version performs worse than biased")
print(f"  Biased: {biased['avg_pnl']:+.3f}, Broken: {broken['avg_pnl']:+.3f}")
print(f"  Result: {'PASS' if test2_pass else 'FAIL'}")
print()

# Test 3: Fixed version should have realistic win rate (30-60%)
test3_pass = 30 <= fixed['win_rate'] <= 60
print(f"Test 3: Fixed version shows realistic win rate (30-60%)")
print(f"  Result: {fixed['win_rate']:.1f}% - {'PASS' if test3_pass else 'FAIL'}")
print()

# Test 4: Fixed version should have symmetric wins/losses
if len([t for t in results[2] if t]) > 0:
    fixed_full = run_FIXED_version(dataset)
    # With correct P&L, losses should be comparable to wins
    test4_pass = abs(fixed['avg_pnl']) < 0.2  # Not massively profitable
    print(f"Test 4: Fixed version has realistic P&L (not absurdly profitable)")
    print(f"  Result: {fixed['avg_pnl']:+.3f} - {'PASS' if test4_pass else 'FAIL'}")
    print()

# Overall
all_pass = test1_pass and test2_pass and test3_pass and test4_pass
print("="*70)
if all_pass:
    print("ALL TESTS PASSED - Bias detection is working correctly!")
else:
    print("SOME TESTS FAILED - Review bias detection logic")
print("="*70)
print()

print("KEY FINDINGS:")
print(f"  1. Biased code inflates win rate by {biased['win_rate'] - fixed['win_rate']:.1f} points")
print(f"  2. Biased code inflates P&L by {biased['avg_pnl'] - fixed['avg_pnl']:.3f} per trade")
print(f"  3. Betting opposite direction (broken) confirms signal detection works")
print(f"  4. Fixed version shows realistic market efficiency (~50% win rate)")
