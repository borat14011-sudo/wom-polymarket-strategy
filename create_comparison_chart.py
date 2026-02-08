#!/usr/bin/env python3
"""
Generate visual comparison between original and event-based backtests
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Set2")

# Original backtest results (from FINAL_BACKTEST_REPORT.md)
original = {
    'Trend Filter': {'sharpe': 2.56, 'win_rate': 57.3, 'trades': 356, 'pnl': 23.79},
    'NO-Side Bias': {'sharpe': 2.55, 'win_rate': 11.3, 'trades': 257, 'pnl': 2.74},
    'Expert Fade': {'sharpe': 1.99, 'win_rate': 14.0, 'trades': 477, 'pnl': 17.57},
    'Whale Copy': {'sharpe': 3.13, 'win_rate': 82.0, 'trades': 405, 'pnl': 33.84},
    'News Mean Reversion': {'sharpe': 1.88, 'win_rate': 57.0, 'trades': 395, 'pnl': 4.82},
}

# Event-based backtest results
event_based = {
    'Trend Filter': {'sharpe': -10.03, 'win_rate': 31.0, 'trades': 58, 'pnl': -2544.13},
    'NO-Side Bias': {'sharpe': -44.87, 'win_rate': 3.2, 'trades': 31, 'pnl': -1038.17},
    'Expert Fade': {'sharpe': -27.81, 'win_rate': 7.7, 'trades': 39, 'pnl': -1354.92},
    'Whale Copy': {'sharpe': -9.39, 'win_rate': 36.5, 'trades': 85, 'pnl': -3870.68},
    'News Mean Reversion': {'sharpe': -9.64, 'win_rate': 30.8, 'trades': 26, 'pnl': -1538.17},
}

# Create figure with subplots
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

strategies = list(original.keys())

# 1. Sharpe Ratio Comparison
ax1 = fig.add_subplot(gs[0, :2])
x = np.arange(len(strategies))
width = 0.35

sharpe_orig = [original[s]['sharpe'] for s in strategies]
sharpe_event = [event_based[s]['sharpe'] for s in strategies]

bars1 = ax1.bar(x - width/2, sharpe_orig, width, label='Original (No Costs)', 
               color='steelblue', alpha=0.8)
bars2 = ax1.bar(x + width/2, sharpe_event, width, label='Event-Based (Realistic)', 
               color='coral', alpha=0.8)

ax1.axhline(y=0, color='red', linestyle='--', linewidth=2, alpha=0.5)
ax1.set_xlabel('Strategy', fontsize=14, fontweight='bold')
ax1.set_ylabel('Sharpe Ratio', fontsize=14, fontweight='bold')
ax1.set_title('Sharpe Ratio Comparison: Original vs. Event-Based', 
             fontsize=16, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(strategies, rotation=45, ha='right')
ax1.legend(fontsize=12)
ax1.grid(True, alpha=0.3)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom' if height > 0 else 'top', 
                fontsize=9, fontweight='bold')

# 2. Win Rate Comparison
ax2 = fig.add_subplot(gs[1, :2])
win_orig = [original[s]['win_rate'] for s in strategies]
win_event = [event_based[s]['win_rate'] for s in strategies]

bars1 = ax2.bar(x - width/2, win_orig, width, label='Original', 
               color='green', alpha=0.7)
bars2 = ax2.bar(x + width/2, win_event, width, label='Event-Based', 
               color='red', alpha=0.7)

ax2.axhline(y=50, color='orange', linestyle='--', linewidth=2, alpha=0.5, 
           label='50% Breakeven')
ax2.set_xlabel('Strategy', fontsize=14, fontweight='bold')
ax2.set_ylabel('Win Rate (%)', fontsize=14, fontweight='bold')
ax2.set_title('Win Rate Comparison', fontsize=16, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(strategies, rotation=45, ha='right')
ax2.legend(fontsize=12)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 100)

# 3. Total P&L Comparison
ax3 = fig.add_subplot(gs[2, :2])
pnl_orig = [original[s]['pnl'] for s in strategies]
pnl_event = [event_based[s]['pnl'] for s in strategies]

bars1 = ax3.bar(x - width/2, pnl_orig, width, label='Original', 
               color='steelblue', alpha=0.8)
bars2 = ax3.bar(x + width/2, pnl_event, width, label='Event-Based', 
               color='coral', alpha=0.8)

ax3.axhline(y=0, color='red', linestyle='--', linewidth=2, alpha=0.5)
ax3.set_xlabel('Strategy', fontsize=14, fontweight='bold')
ax3.set_ylabel('Total P&L ($)', fontsize=14, fontweight='bold')
ax3.set_title('Total P&L Comparison', fontsize=16, fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(strategies, rotation=45, ha='right')
ax3.legend(fontsize=12)
ax3.grid(True, alpha=0.3)

# 4. Summary Stats Box
ax4 = fig.add_subplot(gs[0, 2])
ax4.axis('off')

summary_text = """SUMMARY STATISTICS

ORIGINAL BACKTEST:
• Total Trades: 2,014
• Avg Sharpe: 2.02
• Total P&L: +$82.76
• Final Return: +3.3%

EVENT-BASED BACKTEST:
• Total Trades: 239
• Avg Sharpe: -20.35
• Total P&L: -$10,346
• Final Return: -98.0%

DISCREPANCY:
• -88% fewer trades
• -22.37 Sharpe difference
• -$10,429 P&L difference
• -101.3% return difference
"""

ax4.text(0.1, 0.95, summary_text, transform=ax4.transAxes,
        fontsize=11, verticalalignment='top', family='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 5. Cost Breakdown
ax5 = fig.add_subplot(gs[1, 2])
ax5.axis('off')

cost_text = """COST IMPACT

Avg Costs Per Trade:
━━━━━━━━━━━━━━━━━━━
Platform Fees: 4.0%
  (2% entry + 2% exit)

Slippage: 0.5-1.5%
  (varies by size)

TOTAL: ~5% per trade
━━━━━━━━━━━━━━━━━━━

With 5% costs, you need:
• 75%+ win rate, OR
• 8%+ edge per trade

None of these strategies
have sufficient edge!
"""

ax5.text(0.1, 0.95, cost_text, transform=ax5.transAxes,
        fontsize=10, verticalalignment='top', family='monospace',
        bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.3))

# 6. Conclusion
ax6 = fig.add_subplot(gs[2, 2])
ax6.axis('off')

conclusion_text = """⚠️ CONCLUSION

The original backtest was
OVERLY OPTIMISTIC due to:

❌ No slippage modeling
❌ No fee modeling
❌ No liquidity limits
❌ Fixed position sizing

The event-based backtest
shows REALISTIC results:

✓ All strategies unprofitable
✓ Costs destroy edges
✓ Kelly sizing prevents
  overtrading

RECOMMENDATION:
Do NOT trade these strategies
without major improvements!
"""

ax6.text(0.1, 0.95, conclusion_text, transform=ax6.transAxes,
        fontsize=11, verticalalignment='top', family='monospace',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))

# Overall title
fig.suptitle('BACKTEST COMPARISON: Original vs. Event-Based (Realistic Costs)', 
            fontsize=20, fontweight='bold', y=0.995)

# Save
plt.tight_layout()
plt.savefig('backtest_comparison_chart.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: backtest_comparison_chart.png")

# Create a second chart showing cost breakdown
fig2, axes = plt.subplots(1, 2, figsize=(16, 6))

# Cost components
strategies_short = ['Trend', 'NO-Side', 'Expert', 'Whale', 'News']
slippage = [71.24, 5.03, 9.57, 111.09, 32.21]
fees = [227.23, 41.22, 60.96, 363.27, 87.23]

x2 = np.arange(len(strategies_short))

# Stacked bar chart
axes[0].bar(x2, slippage, label='Slippage', color='orange', alpha=0.8)
axes[0].bar(x2, fees, bottom=slippage, label='Fees', color='red', alpha=0.8)
axes[0].set_xlabel('Strategy', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Total Cost ($)', fontsize=12, fontweight='bold')
axes[0].set_title('Cost Breakdown by Strategy', fontsize=14, fontweight='bold')
axes[0].set_xticks(x2)
axes[0].set_xticklabels(strategies_short, rotation=45, ha='right')
axes[0].legend(fontsize=11)
axes[0].grid(True, alpha=0.3, axis='y')

# Cost as % of gross P&L
slippage_pct = [1.38, 0.49, 0.63, 1.44, 1.54]
fee_pct = [4.0, 4.0, 4.0, 4.0, 4.0]  # Fixed 2% + 2%

axes[1].bar(x2, slippage_pct, label='Slippage %', color='orange', alpha=0.8)
axes[1].bar(x2, fee_pct, bottom=slippage_pct, label='Fees %', color='red', alpha=0.8)
axes[1].axhline(y=5, color='green', linestyle='--', linewidth=2, 
               label='5% Total Cost Threshold')
axes[1].set_xlabel('Strategy', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Cost (%)', fontsize=12, fontweight='bold')
axes[1].set_title('Cost as % of Position', fontsize=14, fontweight='bold')
axes[1].set_xticks(x2)
axes[1].set_xticklabels(strategies_short, rotation=45, ha='right')
axes[1].legend(fontsize=11)
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('cost_breakdown_chart.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: cost_breakdown_chart.png")

print("\n[OK] Visualization complete!")
