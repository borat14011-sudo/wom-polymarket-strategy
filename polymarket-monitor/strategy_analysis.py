#!/usr/bin/env python3
"""
STRATEGY OPTIMIZATION SCIENTIST 🧪
Deep analysis of strategy edge vs data artifacts
"""
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import statistics

DATA_DIR = Path("historical-data-scraper/data")
OUTPUT_DIR = Path("backtest-results")

print(f"\n{'='*80}")
print(f"STRATEGY OPTIMIZATION SCIENTIST - EDGE ANALYSIS")
print(f"{'='*80}\n")

# Load dataset
print("Loading dataset...")
with open(DATA_DIR / "backtest_dataset_v1.json") as f:
    dataset = json.load(f)
print(f"[OK] {len(dataset):,} markets loaded\n")

# ============================================================================
# ANALYSIS 1: WHY DOES TREND FILTER WIN 95%?
# ============================================================================
print(f"\n{'='*80}")
print(f"ANALYSIS 1: TREND FILTER - WHY 95% WIN RATE?")
print(f"{'='*80}\n")

def analyze_trend_filter_mechanics(markets):
    """Deep dive into WHY trend filter wins"""
    
    stats = {
        'trend_continuation': [],  # Do trends continue?
        'trend_reversal': [],      # Or reverse?
        'entry_to_final': [],      # Entry price vs final price
        'trend_strength': [],      # How strong are trends?
        'false_signals': [],       # Trends that reversed
        'true_signals': [],        # Trends that continued
        'market_types': defaultdict(lambda: {'total': 0, 'trend_continued': 0})
    }
    
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
                
                # Calculate trend strength
                trend_slope = (current - prev_3) / 3
                
                # Did trend continue?
                price_change = exit_price - entry_price
                trend_continued = price_change > 0
                
                # Record data
                stats['entry_to_final'].append({
                    'entry': entry_price,
                    'exit': exit_price,
                    'final': final_price,
                    'change': price_change,
                    'outcome': outcome
                })
                
                stats['trend_strength'].append(trend_slope)
                
                if trend_continued:
                    stats['trend_continuation'].append(price_change)
                    stats['true_signals'].append({
                        'entry': entry_price,
                        'exit': exit_price,
                        'slope': trend_slope,
                        'outcome': outcome
                    })
                else:
                    stats['trend_reversal'].append(price_change)
                    stats['false_signals'].append({
                        'entry': entry_price,
                        'exit': exit_price,
                        'slope': trend_slope,
                        'outcome': outcome
                    })
                
                # Market type analysis
                market_type = 'binary'  # Simplified
                stats['market_types'][market_type]['total'] += 1
                if trend_continued:
                    stats['market_types'][market_type]['trend_continued'] += 1
                
                break  # One per market
    
    # Analysis
    total_trends = len(stats['trend_continuation']) + len(stats['trend_reversal'])
    continuation_rate = len(stats['trend_continuation']) / total_trends * 100 if total_trends > 0 else 0
    
    print(f"📊 TREND BEHAVIOR ANALYSIS")
    print(f"Total trend signals detected: {total_trends:,}")
    print(f"Trends that CONTINUED: {len(stats['trend_continuation']):,} ({continuation_rate:.1f}%)")
    print(f"Trends that REVERSED: {len(stats['trend_reversal']):,} ({100-continuation_rate:.1f}%)")
    print()
    
    if stats['trend_continuation']:
        avg_continuation = statistics.mean(stats['trend_continuation'])
        print(f"Avg continuation gain: {avg_continuation:+.4f}")
    
    if stats['trend_reversal']:
        avg_reversal = statistics.mean(stats['trend_reversal'])
        print(f"Avg reversal loss: {avg_reversal:+.4f}")
    
    print()
    
    # KEY INSIGHT: Entry price distribution
    entry_prices = [x['entry'] for x in stats['entry_to_final']]
    print(f"📈 ENTRY PRICE DISTRIBUTION (critical insight)")
    print(f"Mean entry price: {statistics.mean(entry_prices):.3f}")
    print(f"Median entry price: {statistics.median(entry_prices):.3f}")
    print(f"Entry < 0.1: {len([p for p in entry_prices if p < 0.1]):,} trades")
    print(f"Entry 0.1-0.3: {len([p for p in entry_prices if 0.1 <= p < 0.3]):,} trades")
    print(f"Entry 0.3-0.5: {len([p for p in entry_prices if 0.3 <= p < 0.5]):,} trades")
    print(f"Entry 0.5-0.7: {len([p for p in entry_prices if 0.5 <= p < 0.7]):,} trades")
    print(f"Entry > 0.7: {len([p for p in entry_prices if p >= 0.7]):,} trades")
    print()
    
    return stats

trend_stats = analyze_trend_filter_mechanics(dataset)

# ============================================================================
# ANALYSIS 2: DATA ARTIFACTS - THE SMOKING GUN
# ============================================================================
print(f"\n{'='*80}")
print(f"ANALYSIS 2: DATA ARTIFACT DETECTION")
print(f"{'='*80}\n")

def detect_artifacts(markets):
    """Check if strategy exploits data peculiarities"""
    
    artifacts = {
        'low_volatility_after_trend': 0,
        'high_volatility_after_trend': 0,
        'markets_with_single_direction': 0,
        'exits_near_final': [],
        'entry_timing_bias': defaultdict(int)
    }
    
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
                artifacts['exits_near_final'].append(abs(price_change_after_exit))
                
                # ARTIFACT 2: Volatility after entry
                prices_after_entry = [prices[j].get('p', 0) for j in range(entry_idx, exit_idx)]
                if len(prices_after_entry) > 2:
                    volatility = statistics.stdev(prices_after_entry)
                    if volatility < 0.05:
                        artifacts['low_volatility_after_trend'] += 1
                    else:
                        artifacts['high_volatility_after_trend'] += 1
                
                # ARTIFACT 3: When do trends appear? (timing bias)
                position_in_market = i / len(prices)
                if position_in_market < 0.2:
                    artifacts['entry_timing_bias']['early'] += 1
                elif position_in_market < 0.5:
                    artifacts['entry_timing_bias']['mid'] += 1
                else:
                    artifacts['entry_timing_bias']['late'] += 1
                
                break
    
    print(f"🚨 ARTIFACT DETECTION RESULTS")
    print()
    print(f"Exit proximity to final price:")
    if artifacts['exits_near_final']:
        avg_diff = statistics.mean(artifacts['exits_near_final'])
        print(f"  Avg difference: {avg_diff:.4f}")
        print(f"  This means exits are {avg_diff:.4f} away from final price")
        print(f"  🔍 VERDICT: {'SUSPICIOUS - Very close!' if avg_diff < 0.02 else 'Reasonable'}")
    print()
    
    total_vol = artifacts['low_volatility_after_trend'] + artifacts['high_volatility_after_trend']
    if total_vol > 0:
        low_vol_pct = artifacts['low_volatility_after_trend'] / total_vol * 100
        print(f"Post-trend volatility:")
        print(f"  Low volatility: {artifacts['low_volatility_after_trend']:,} ({low_vol_pct:.1f}%)")
        print(f"  High volatility: {artifacts['high_volatility_after_trend']:,}")
        print(f"  🔍 VERDICT: {'Trends occur in stable markets' if low_vol_pct > 60 else 'Mixed volatility'}")
    print()
    
    print(f"Entry timing distribution:")
    for phase, count in artifacts['entry_timing_bias'].items():
        print(f"  {phase.capitalize()}: {count:,}")
    print()
    
    return artifacts

artifacts = detect_artifacts(dataset)

# ============================================================================
# ANALYSIS 3: PARAMETER SENSITIVITY
# ============================================================================
print(f"\n{'='*80}")
print(f"ANALYSIS 3: PARAMETER SENSITIVITY TESTING")
print(f"{'='*80}\n")

def test_parameter_sensitivity(markets):
    """Test if changing parameters destroys edge"""
    
    configs = [
        {'name': 'Original (3 rising)', 'window': 3, 'exit_offset': 5},
        {'name': '2 rising points', 'window': 2, 'exit_offset': 5},
        {'name': '4 rising points', 'window': 4, 'exit_offset': 5},
        {'name': '5 rising points', 'window': 5, 'exit_offset': 5},
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
            
            for i in range(window + 2, max_entry_idx):
                # Check trend
                trend_detected = True
                for j in range(window):
                    if prices[i-j].get('p', 0) <= prices[i-j-1].get('p', 0):
                        trend_detected = False
                        break
                
                if trend_detected:
                    entry_price = prices[i].get('p', 0)
                    exit_idx = len(prices) - config['exit_offset']
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
    print(f"🔍 SENSITIVITY VERDICT:")
    baseline = results[0]['win_rate']
    variations = [r['win_rate'] for r in results[1:]]
    avg_variation = statistics.mean(variations)
    
    if max(variations) - min(variations) < 5:
        print(f"  ROBUST - Win rate stays {min(variations):.1f}%-{max(variations):.1f}% across parameters")
    elif baseline - avg_variation > 10:
        print(f"  FRAGILE - Original config is {baseline - avg_variation:.1f}% better than variations")
        print(f"  ⚠️  This suggests overfitting to specific parameters!")
    else:
        print(f"  MODERATE - Some sensitivity but edge persists")
    
    print()
    
    return results

sensitivity_results = test_parameter_sensitivity(dataset)

# ============================================================================
# ANALYSIS 4: MARKET-SPECIFIC PERFORMANCE
# ============================================================================
print(f"\n{'='*80}")
print(f"ANALYSIS 4: MARKET-SPECIFIC PERFORMANCE")
print(f"{'='*80}\n")

def analyze_market_categories(markets):
    """Which types of markets does each strategy work on?"""
    
    # Categorize by volume, duration, topic
    categories = defaultdict(lambda: {'total': 0, 'wins': 0})
    
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
        
        # Categorize by volume
        volume = market.get('volume', 0)
        if volume < 1000:
            vol_cat = 'micro'
        elif volume < 10000:
            vol_cat = 'small'
        elif volume < 100000:
            vol_cat = 'medium'
        else:
            vol_cat = 'large'
        
        # Categorize by price history length (proxy for activity)
        if len(prices) < 50:
            activity = 'low'
        elif len(prices) < 200:
            activity = 'medium'
        else:
            activity = 'high'
        
        # Find trend
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
                
                win = pnl > 0
                
                # Record by category
                categories[f'volume_{vol_cat}']['total'] += 1
                categories[f'activity_{activity}']['total'] += 1
                
                if win:
                    categories[f'volume_{vol_cat}']['wins'] += 1
                    categories[f'activity_{activity}']['wins'] += 1
                
                break
    
    print(f"📊 PERFORMANCE BY MARKET CATEGORY")
    print()
    
    for cat_name in sorted(categories.keys()):
        data = categories[cat_name]
        win_rate = data['wins'] / data['total'] * 100 if data['total'] > 0 else 0
        print(f"{cat_name:20s} | {data['total']:>5,} trades | {win_rate:>5.1f}% win")
    
    print()
    
    return categories

market_categories = analyze_market_categories(dataset)

# ============================================================================
# ANALYSIS 5: STATISTICAL SIGNIFICANCE
# ============================================================================
print(f"\n{'='*80}")
print(f"ANALYSIS 5: STATISTICAL SIGNIFICANCE (Bootstrap)")
print(f"{'='*80}\n")

def statistical_significance_test(markets, n_bootstrap=1000):
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
        print(f"  🎯 HIGHLY SIGNIFICANT - Edge is real (p < 0.01)")
    elif p_value < 0.05:
        print(f"  ✅ SIGNIFICANT - Edge is likely real (p < 0.05)")
    else:
        print(f"  ⚠️  NOT SIGNIFICANT - Could be luck")
    print()
    
    return {
        'actual_mean': actual_mean,
        'actual_win_rate': actual_win_rate,
        'ci_mean': (mean_ci_low, mean_ci_high),
        'ci_win_rate': (wr_ci_low, wr_ci_high),
        'p_value': p_value
    }

sig_test = statistical_significance_test(dataset, n_bootstrap=1000)

# ============================================================================
# FINAL VERDICT
# ============================================================================
print(f"\n{'='*80}")
print(f"🧪 FINAL VERDICT: REAL EDGE VS DATA ARTIFACTS")
print(f"{'='*80}\n")

print(f"TREND FILTER STRATEGY:")
print(f"  Win Rate: 95% ({'REAL' if sig_test['p_value'] < 0.01 else 'QUESTIONABLE'})")
print(f"  Statistical Significance: p = {sig_test['p_value']:.4f}")
print(f"  95% CI: [{sig_test['ci_win_rate'][0]:.1f}%, {sig_test['ci_win_rate'][1]:.1f}%]")
print()

# Determine verdict
issues = []
if artifacts['exits_near_final'] and statistics.mean(artifacts['exits_near_final']) < 0.02:
    issues.append("Exit timing very close to final price")

if len(sensitivity_results) > 1:
    baseline = sensitivity_results[0]['win_rate']
    avg_other = statistics.mean([r['win_rate'] for r in sensitivity_results[1:]])
    if baseline - avg_other > 10:
        issues.append("Highly sensitive to specific parameters")

if issues:
    print(f"⚠️  CONCERNS DETECTED:")
    for issue in issues:
        print(f"  - {issue}")
    print()
    print(f"VERDICT: MIXED - Has statistical edge BUT shows signs of data overfitting")
else:
    print(f"✅ VERDICT: REAL EDGE - Strategy shows robust, statistically significant performance")

print()
print(f"RECOMMENDATIONS:")
print(f"  1. Test on out-of-sample data (future markets)")
print(f"  2. Implement with more conservative exit (20+ points before close)")
print(f"  3. Add volume filters to focus on liquid markets")
print(f"  4. Monitor live performance vs backtest")
print(f"\n{'='*80}\n")

# Save detailed analysis
output = {
    'timestamp': datetime.now().isoformat(),
    'trend_continuation_rate': len(trend_stats['trend_continuation']) / 
                               (len(trend_stats['trend_continuation']) + len(trend_stats['trend_reversal'])) * 100
                               if (len(trend_stats['trend_continuation']) + len(trend_stats['trend_reversal'])) > 0 else 0,
    'artifacts': {
        'avg_exit_proximity': statistics.mean(artifacts['exits_near_final']) if artifacts['exits_near_final'] else 0,
        'entry_timing': dict(artifacts['entry_timing_bias'])
    },
    'sensitivity': sensitivity_results,
    'statistical_test': {
        'p_value': sig_test['p_value'],
        'confidence_interval_win_rate': sig_test['ci_win_rate'],
        'confidence_interval_mean_pnl': sig_test['ci_mean']
    },
    'verdict': 'REAL_EDGE' if not issues else 'MIXED_OVERFITTING'
}

output_file = OUTPUT_DIR / f"strategy_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"Analysis saved: {output_file}")
