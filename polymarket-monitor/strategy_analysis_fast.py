#!/usr/bin/env python3
"""
STRATEGY OPTIMIZATION SCIENTIST - FAST VERSION
Deep analysis of strategy edge vs data artifacts (optimized)
"""
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import statistics
import random

DATA_DIR = Path("historical-data-scraper/data")
OUTPUT_DIR = Path("backtest-results")

print("\n" + "="*80)
print("STRATEGY OPTIMIZATION SCIENTIST - EDGE ANALYSIS (FAST)")
print("="*80 + "\n")

# Load dataset
print("Loading dataset...")
with open(DATA_DIR / "backtest_dataset_v1.json") as f:
    dataset = json.load(f)
print(f"[OK] {len(dataset):,} markets loaded")

# Sample for faster analysis (use 30% of data)
SAMPLE_SIZE = min(5000, len(dataset))
print(f"Sampling {SAMPLE_SIZE:,} markets for analysis...\n")
dataset_sample = random.sample(dataset, SAMPLE_SIZE)

# ============================================================================
# ANALYSIS 1: WHY DOES TREND FILTER WIN 95%?
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 1: TREND FILTER - WHY 95% WIN RATE?")
print("="*80 + "\n")

def analyze_trend_filter_mechanics(markets):
    """Deep dive into WHY trend filter wins"""
    
    trend_continued = []
    trend_reversed = []
    entry_prices = []
    entry_to_outcome = []
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 30:
            continue
        
        final_price = prices[-1].get('p', 0)
        
        # Skip ambiguous
        if not (final_price > 0.95 or final_price < 0.05):
            continue
        
        outcome = 'Yes' if final_price > 0.95 else 'No'
        
        # Find trend signals
        max_entry_idx = len(prices) - 10
        
        for i in range(5, max_entry_idx):
            current = prices[i].get('p', 0)
            prev_1 = prices[i-1].get('p', 0)
            prev_2 = prices[i-2].get('p', 0)
            prev_3 = prices[i-3].get('p', 0)
            
            # Trend detected
            if current > prev_1 > prev_2 > prev_3:
                entry_price = current
                exit_idx = len(prices) - 5
                exit_price = prices[exit_idx].get('p', 0)
                
                # Did trend continue?
                price_change = exit_price - entry_price
                
                if price_change > 0:
                    trend_continued.append(price_change)
                else:
                    trend_reversed.append(price_change)
                
                entry_prices.append(entry_price)
                entry_to_outcome.append({
                    'entry': entry_price,
                    'outcome_yes': outcome == 'Yes',
                    'price_rose': price_change > 0
                })
                
                break  # One per market
    
    # Analysis
    total_trends = len(trend_continued) + len(trend_reversed)
    continuation_rate = len(trend_continued) / total_trends * 100 if total_trends > 0 else 0
    
    print(f"TREND BEHAVIOR ANALYSIS")
    print(f"Total trend signals detected: {total_trends:,}")
    print(f"Trends that CONTINUED: {len(trend_continued):,} ({continuation_rate:.1f}%)")
    print(f"Trends that REVERSED: {len(trend_reversed):,} ({100-continuation_rate:.1f}%)")
    print()
    
    if trend_continued:
        avg_continuation = statistics.mean(trend_continued)
        print(f"Avg continuation gain: {avg_continuation:+.4f}")
    
    if trend_reversed:
        avg_reversal = statistics.mean(trend_reversed)
        print(f"Avg reversal loss: {avg_reversal:+.4f}")
    
    print()
    
    # KEY INSIGHT: Entry price distribution
    print(f"ENTRY PRICE DISTRIBUTION (critical insight)")
    print(f"Mean entry price: {statistics.mean(entry_prices):.3f}")
    print(f"Median entry price: {statistics.median(entry_prices):.3f}")
    print(f"Entry < 0.1: {len([p for p in entry_prices if p < 0.1]):,} trades ({len([p for p in entry_prices if p < 0.1])/len(entry_prices)*100:.1f}%)")
    print(f"Entry 0.1-0.3: {len([p for p in entry_prices if 0.1 <= p < 0.3]):,} trades")
    print(f"Entry 0.3-0.5: {len([p for p in entry_prices if 0.3 <= p < 0.5]):,} trades")
    print(f"Entry 0.5-0.7: {len([p for p in entry_prices if 0.5 <= p < 0.7]):,} trades")
    print(f"Entry > 0.7: {len([p for p in entry_prices if p >= 0.7]):,} trades")
    
    # SMOKING GUN: Correlation between uptrend and YES outcome
    uptrends_on_yes_markets = sum(1 for x in entry_to_outcome if x['outcome_yes'] and x['price_rose'])
    uptrends_on_no_markets = sum(1 for x in entry_to_outcome if not x['outcome_yes'] and x['price_rose'])
    print()
    print(f"CRITICAL INSIGHT - Trend alignment with outcomes:")
    print(f"  Uptrends that occurred on YES markets: {uptrends_on_yes_markets} / {len([x for x in entry_to_outcome if x['outcome_yes']])}")
    print(f"  Uptrends that occurred on NO markets: {uptrends_on_no_markets} / {len([x for x in entry_to_outcome if not x['outcome_yes']])}")
    
    yes_market_uptrend_rate = uptrends_on_yes_markets / len([x for x in entry_to_outcome if x['outcome_yes']]) * 100 if len([x for x in entry_to_outcome if x['outcome_yes']]) > 0 else 0
    print(f"  Rate: {yes_market_uptrend_rate:.1f}% of YES markets show uptrends that continue")
    print()
    
    return {
        'continuation_rate': continuation_rate,
        'entry_prices': entry_prices,
        'yes_market_alignment': yes_market_uptrend_rate
    }

trend_stats = analyze_trend_filter_mechanics(dataset_sample)

# ============================================================================
# ANALYSIS 2: DATA ARTIFACTS - THE SMOKING GUN
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 2: DATA ARTIFACT DETECTION")
print("="*80 + "\n")

def detect_artifacts(markets):
    """Check if strategy exploits data peculiarities"""
    
    exits_near_final = []
    low_volatility_count = 0
    high_volatility_count = 0
    entry_timing = {'early': 0, 'mid': 0, 'late': 0}
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 30:
            continue
        
        final_price = prices[-1].get('p', 0)
        if not (final_price > 0.95 or final_price < 0.05):
            continue
        
        # Check for trend
        max_entry_idx = len(prices) - 10
        for i in range(5, max_entry_idx):
            current = prices[i].get('p', 0)
            prev_1 = prices[i-1].get('p', 0)
            prev_2 = prices[i-2].get('p', 0)
            prev_3 = prices[i-3].get('p', 0)
            
            if current > prev_1 > prev_2 > prev_3:
                entry_idx = i
                exit_idx = len(prices) - 5
                
                # ARTIFACT 1: How close is exit to final?
                exit_price = prices[exit_idx].get('p', 0)
                price_change_after_exit = final_price - exit_price
                exits_near_final.append(abs(price_change_after_exit))
                
                # ARTIFACT 2: Volatility after entry
                prices_after_entry = [prices[j].get('p', 0) for j in range(entry_idx, min(exit_idx, entry_idx + 20))]
                if len(prices_after_entry) > 2:
                    volatility = statistics.stdev(prices_after_entry)
                    if volatility < 0.05:
                        low_volatility_count += 1
                    else:
                        high_volatility_count += 1
                
                # ARTIFACT 3: When do trends appear?
                position_in_market = i / len(prices)
                if position_in_market < 0.2:
                    entry_timing['early'] += 1
                elif position_in_market < 0.5:
                    entry_timing['mid'] += 1
                else:
                    entry_timing['late'] += 1
                
                break
    
    print(f"ARTIFACT DETECTION RESULTS")
    print()
    print(f"Exit proximity to final price:")
    if exits_near_final:
        avg_diff = statistics.mean(exits_near_final)
        median_diff = statistics.median(exits_near_final)
        print(f"  Avg difference: {avg_diff:.4f}")
        print(f"  Median difference: {median_diff:.4f}")
        print(f"  VERDICT: {'SUSPICIOUS - Very close!' if avg_diff < 0.02 else 'Reasonable'}")
    print()
    
    total_vol = low_volatility_count + high_volatility_count
    if total_vol > 0:
        low_vol_pct = low_volatility_count / total_vol * 100
        print(f"Post-trend volatility:")
        print(f"  Low volatility: {low_volatility_count:,} ({low_vol_pct:.1f}%)")
        print(f"  High volatility: {high_volatility_count:,}")
        print(f"  VERDICT: {'Trends occur in stable markets' if low_vol_pct > 60 else 'Mixed volatility'}")
    print()
    
    print(f"Entry timing distribution:")
    total_timing = sum(entry_timing.values())
    for phase, count in entry_timing.items():
        pct = count / total_timing * 100 if total_timing > 0 else 0
        print(f"  {phase.capitalize()}: {count:,} ({pct:.1f}%)")
    print()
    
    return {
        'avg_exit_proximity': statistics.mean(exits_near_final) if exits_near_final else 0,
        'entry_timing': entry_timing
    }

artifacts = detect_artifacts(dataset_sample)

# ============================================================================
# ANALYSIS 3: PARAMETER SENSITIVITY
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 3: PARAMETER SENSITIVITY TESTING")
print("="*80 + "\n")

def test_parameter_sensitivity(markets):
    """Test if changing parameters destroys edge"""
    
    configs = [
        {'name': 'Original (3 rising)', 'window': 3, 'exit_offset': 5},
        {'name': '2 rising points', 'window': 2, 'exit_offset': 5},
        {'name': '4 rising points', 'window': 4, 'exit_offset': 5},
        {'name': 'Exit 10 before', 'window': 3, 'exit_offset': 10},
        {'name': 'Exit 15 before', 'window': 3, 'exit_offset': 15},
        {'name': 'Exit 20 before', 'window': 3, 'exit_offset': 20},
    ]
    
    results = []
    
    for config in configs:
        trades = []
        
        for market in markets:
            if not market.get('closed'):
                continue
            
            prices = market.get('price_history', [])
            if len(prices) < 30:
                continue
            
            final_price = prices[-1].get('p', 0)
            if not (final_price > 0.95 or final_price < 0.05):
                continue
            
            outcome = 'Yes' if final_price > 0.95 else 'No'
            
            window = config['window']
            max_entry_idx = len(prices) - config['exit_offset'] - 5
            
            if max_entry_idx < window + 2:
                continue
            
            for i in range(window + 2, max_entry_idx):
                # Check trend
                trend_detected = True
                for j in range(window):
                    if i-j < 0 or i-j-1 < 0:
                        trend_detected = False
                        break
                    if prices[i-j].get('p', 0) <= prices[i-j-1].get('p', 0):
                        trend_detected = False
                        break
                
                if trend_detected:
                    entry_price = prices[i].get('p', 0)
                    exit_idx = len(prices) - config['exit_offset']
                    if exit_idx >= len(prices):
                        break
                    exit_price = prices[exit_idx].get('p', 0)
                    
                    if outcome == 'Yes':
                        pnl = exit_price - entry_price
                    else:
                        pnl = -(exit_price - entry_price)
                    
                    trades.append(pnl > 0)
                    break
        
        total = len(trades)
        wins = sum(trades)
        win_rate = wins / total * 100 if total > 0 else 0
        
        results.append({
            'config': config['name'],
            'trades': total,
            'win_rate': win_rate
        })
        
        print(f"{config['name']:20s} | {total:>5,} trades | {win_rate:>5.1f}% win")
    
    print()
    print(f"SENSITIVITY VERDICT:")
    if results:
        baseline = results[0]['win_rate']
        variations = [r['win_rate'] for r in results[1:]]
        if variations:
            avg_variation = statistics.mean(variations)
            
            if max(variations) - min(variations) < 5:
                print(f"  ROBUST - Win rate stays {min(variations):.1f}%-{max(variations):.1f}% across parameters")
            elif baseline - avg_variation > 10:
                print(f"  FRAGILE - Original config is {baseline - avg_variation:.1f}% better than variations")
                print(f"  WARNING: This suggests overfitting to specific parameters!")
            else:
                print(f"  MODERATE - Some sensitivity but edge persists")
    
    print()
    
    return results

sensitivity_results = test_parameter_sensitivity(dataset_sample)

# ============================================================================
# ANALYSIS 4: STATISTICAL SIGNIFICANCE
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 4: STATISTICAL SIGNIFICANCE (Bootstrap)")
print("="*80 + "\n")

def statistical_significance_test(markets, n_bootstrap=500):
    """Test if results are statistically significant vs random"""
    
    # Collect all trades
    trades = []
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 30:
            continue
        
        final_price = prices[-1].get('p', 0)
        if not (final_price > 0.95 or final_price < 0.05):
            continue
        
        outcome = 'Yes' if final_price > 0.95 else 'No'
        
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
                
                if outcome == 'Yes':
                    pnl = exit_price - entry_price
                else:
                    pnl = -(exit_price - entry_price)
                
                trades.append(pnl)
                break
    
    if not trades:
        print("No trades found!")
        return {}
    
    actual_mean = statistics.mean(trades)
    actual_win_rate = len([t for t in trades if t > 0]) / len(trades) * 100
    
    print(f"Actual Performance:")
    print(f"  Trades: {len(trades):,}")
    print(f"  Win Rate: {actual_win_rate:.2f}%")
    print(f"  Mean P&L: {actual_mean:+.4f}")
    print()
    
    # Bootstrap resampling
    print(f"Running {n_bootstrap:,} bootstrap samples...")
    bootstrap_means = []
    bootstrap_win_rates = []
    
    for _ in range(n_bootstrap):
        sample = np.random.choice(trades, size=len(trades), replace=True)
        bootstrap_means.append(np.mean(sample))
        bootstrap_win_rates.append(sum(1 for t in sample if t > 0) / len(sample) * 100)
    
    # Calculate confidence intervals
    mean_ci_low = np.percentile(bootstrap_means, 2.5)
    mean_ci_high = np.percentile(bootstrap_means, 97.5)
    wr_ci_low = np.percentile(bootstrap_win_rates, 2.5)
    wr_ci_high = np.percentile(bootstrap_win_rates, 97.5)
    
    print(f"95% Confidence Intervals (Bootstrap):")
    print(f"  Mean P&L: [{mean_ci_low:+.4f}, {mean_ci_high:+.4f}]")
    print(f"  Win Rate: [{wr_ci_low:.2f}%, {wr_ci_high:.2f}%]")
    print()
    
    # Compare to random (50% win rate)
    random_better_count = sum(1 for wr in bootstrap_win_rates if wr < 50)
    p_value = random_better_count / n_bootstrap
    
    print(f"Statistical Test vs Random (50% baseline):")
    print(f"  P-value: {p_value:.4f}")
    if p_value < 0.01:
        print(f"  HIGHLY SIGNIFICANT - Edge is real (p < 0.01)")
    elif p_value < 0.05:
        print(f"  SIGNIFICANT - Edge is likely real (p < 0.05)")
    else:
        print(f"  NOT SIGNIFICANT - Could be luck")
    print()
    
    return {
        'actual_mean': actual_mean,
        'actual_win_rate': actual_win_rate,
        'ci_mean': (mean_ci_low, mean_ci_high),
        'ci_win_rate': (wr_ci_low, wr_ci_high),
        'p_value': p_value
    }

sig_test = statistical_significance_test(dataset_sample, n_bootstrap=500)

# ============================================================================
# FINAL VERDICT
# ============================================================================
print("\n" + "="*80)
print("FINAL VERDICT: REAL EDGE VS DATA ARTIFACTS")
print("="*80 + "\n")

if sig_test:
    print(f"TREND FILTER STRATEGY:")
    print(f"  Win Rate: ~95% ({'REAL' if sig_test.get('p_value', 1) < 0.01 else 'QUESTIONABLE'})")
    print(f"  Statistical Significance: p = {sig_test.get('p_value', 'N/A'):.4f}" if 'p_value' in sig_test else "")
    print(f"  95% CI: [{sig_test.get('ci_win_rate', [0,0])[0]:.1f}%, {sig_test.get('ci_win_rate', [0,0])[1]:.1f}%]" if 'ci_win_rate' in sig_test else "")
    print()
    
    # Determine verdict
    issues = []
    if artifacts['avg_exit_proximity'] < 0.02:
        issues.append("Exit timing very close to final price (avg {:.4f})".format(artifacts['avg_exit_proximity']))
    
    if sensitivity_results and len(sensitivity_results) > 1:
        baseline = sensitivity_results[0]['win_rate']
        avg_other = statistics.mean([r['win_rate'] for r in sensitivity_results[1:] if r['trades'] > 0])
        if baseline - avg_other > 15:
            issues.append("Highly sensitive to specific parameters ({:.1f}% drop)".format(baseline - avg_other))
    
    if trend_stats.get('yes_market_alignment', 0) > 90:
        issues.append("Uptrends overwhelmingly occur on YES-outcome markets")
    
    print(f"KEY FINDINGS:")
    print(f"  1. Trend continuation rate: {trend_stats.get('continuation_rate', 0):.1f}%")
    print(f"  2. Average exit proximity to final: {artifacts['avg_exit_proximity']:.4f}")
    print(f"  3. Entry price median: {statistics.median(trend_stats.get('entry_prices', [0.5])):.3f}")
    print()
    
    if issues:
        print(f"CONCERNS DETECTED:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print()
        print(f"VERDICT: MIXED - Has statistical edge BUT shows signs of data overfitting/artifacts")
        print()
        print(f"THE STRATEGY LIKELY EXPLOITS:")
        print(f"  - Markets where trends are self-reinforcing (YES markets)")
        print(f"  - Exit timing close enough to resolution to capture final price movement")
        print(f"  - Low entry prices that have high upside potential")
    else:
        print(f"VERDICT: REAL EDGE - Strategy shows robust, statistically significant performance")
    
    print()
    print(f"RECOMMENDATIONS:")
    print(f"  1. Test on out-of-sample data (future markets, not in this dataset)")
    print(f"  2. Implement with more conservative exit (20+ points before close)")
    print(f"  3. Add volume filters to focus on liquid markets (> $10k volume)")
    print(f"  4. Consider entry price filters (avoid extremes < 0.05 or > 0.95)")
    print(f"  5. Monitor live performance vs backtest - expect degradation")
    print(f"  6. Test with realistic fees and slippage")

print(f"\n" + "="*80 + "\n")

# Save detailed analysis
if sig_test:
    output = {
        'timestamp': datetime.now().isoformat(),
        'sample_size': SAMPLE_SIZE,
        'trend_continuation_rate': trend_stats.get('continuation_rate', 0),
        'artifacts': {
            'avg_exit_proximity': artifacts['avg_exit_proximity'],
            'entry_timing': artifacts['entry_timing']
        },
        'sensitivity': sensitivity_results,
        'statistical_test': {
            'p_value': sig_test.get('p_value', 1),
            'confidence_interval_win_rate': sig_test.get('ci_win_rate', [0, 0]),
            'confidence_interval_mean_pnl': sig_test.get('ci_mean', [0, 0])
        },
        'verdict': 'MIXED_OVERFITTING' if issues else 'REAL_EDGE',
        'concerns': issues
    }
    
    output_file = OUTPUT_DIR / f"strategy_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Analysis saved: {output_file}")
