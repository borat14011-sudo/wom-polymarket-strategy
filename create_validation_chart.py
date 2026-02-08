#!/usr/bin/env python3
"""Create visualization of backtest validation results"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Results data
strategies = ['MUSK_FADE', 'WEATHER_FADE', 'ALTCOIN_FADE', 'CRYPTO_FAV', 'BTC_TIME']
expected = [97.1, 93.9, 92.3, 61.9, 58.9]
actual = [87.2, 85.1, 61.1, 53.2, 58.8]
trades = [39, 3809, 432, 1818, 7641]

# Create figure with 2 subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Expected vs Actual Win Rates
x = np.arange(len(strategies))
width = 0.35

bars1 = ax1.bar(x - width/2, expected, width, label='Expected', color='#2E7D32', alpha=0.8)
bars2 = ax1.bar(x + width/2, actual, width, label='Actual', color='#1976D2', alpha=0.8)

ax1.set_xlabel('Strategy', fontsize=12, fontweight='bold')
ax1.set_ylabel('Win Rate (%)', fontsize=12, fontweight='bold')
ax1.set_title('Strategy Performance: Expected vs Actual', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(strategies, rotation=45, ha='right')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)
ax1.axhline(y=55, color='red', linestyle='--', alpha=0.5, label='Profitability Threshold')

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

# Plot 2: Trade Count (log scale)
colors = ['#4CAF50' if a >= 55 else '#F44336' for a in actual]
bars3 = ax2.bar(strategies, trades, color=colors, alpha=0.8)

ax2.set_xlabel('Strategy', fontsize=12, fontweight='bold')
ax2.set_ylabel('Number of Trades (log scale)', fontsize=12, fontweight='bold')
ax2.set_title('Sample Size by Strategy', fontsize=14, fontweight='bold')
ax2.set_yscale('log')
ax2.set_xticklabels(strategies, rotation=45, ha='right')
ax2.grid(axis='y', alpha=0.3)

# Add value labels
for i, (bar, count) in enumerate(zip(bars3, trades)):
    ax2.text(i, count, f'{count:,}', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('backtest_validation_chart.png', dpi=150, bbox_inches='tight')
print("Chart saved: backtest_validation_chart.png")

# Create detailed comparison table
print("\n" + "="*80)
print("DETAILED COMPARISON")
print("="*80)
print(f"{'Strategy':<20} {'Expected':>10} {'Actual':>10} {'Diff':>8} {'Trades':>8} {'Status':<12}")
print("-"*80)

for i, strat in enumerate(strategies):
    diff = actual[i] - expected[i]
    if abs(diff) < 5:
        status = "VALIDATED"
    elif actual[i] >= 55:
        status = "PROFITABLE"
    else:
        status = "FAILED"
    
    print(f"{strat:<20} {expected[i]:>9.1f}% {actual[i]:>9.1f}% {diff:>+7.1f}% {trades[i]:>8,} {status:<12}")

print("\n" + "="*80)
print("KEY INSIGHTS")
print("="*80)
print("1. BTC_TIME_BIAS: PERFECTLY VALIDATED (58.8% vs 58.9% expected, 7,641 trades)")
print("2. MUSK_FADE: High win rate (87.2%) but small sample (39 trades)")
print("3. WEATHER_FADE: Excellent performance (85.1% on 3,809 trades)")
print("4. ALTCOIN_FADE: Win rate dropped from 92.3% to 61.1% - strategy needs refinement")
print("5. CRYPTO_FAVORITE: Failed profitability threshold (53.2% < 55%)")
print("\nOVERALL: 4/5 strategies profitable, 1/5 validated within 5%")
