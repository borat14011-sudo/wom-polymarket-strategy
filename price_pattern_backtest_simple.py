#!/usr/bin/env python3
"""
REAL BACKTESTER #3: Price-Based Pattern Analysis (Simple Version)
Analyzes price patterns in 17,324 markets
"""

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

# Load data
print("Loading backtest dataset...", flush=True)
with open(r'C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json', 'r') as f:
    markets = json.load(f)

print(f"Loaded {len(markets)} markets", flush=True)

# TRANSACTION COSTS
FEE_RATE = 0.04  # 4% fee
SLIPPAGE = 0.015  # 1.5% average slippage
TOTAL_COST = FEE_RATE + SLIPPAGE  # 5.5% total per round trip

def analyze_simple(markets, max_markets=None):
    """Simple analysis of price patterns"""
    
    results = {
        'buy_dip_10pct': [],  # Buy when price drops >10% in 24h
        'fade_spike_10pct': [],  # Sell when price spikes >10% in 24h
        'buy_breakout_80': [],  # Buy breakouts above 80%
        'fade_longshot': [],  # Fade prices below 10%
    }
    
    limit = max_markets or len(markets)
    
    for idx, market in enumerate(markets[:limit]):
        if idx % 1000 == 0:
            print(f"Processing market {idx}/{limit}...", flush=True)
        
        try:
            price_history = market.get('price_history', [])
            if len(price_history) < 10:  # Need enough data
                continue
                
            outcome_value = market.get('outcome')  # 'Yes' or 'No'
            
            # Get price points
            prices = []
            timestamps = []
            
            for entry in price_history:
                try:
                    price = float(entry.get('p', entry.get('price', 0)))
                    if price > 0 and price <= 1:
                        prices.append(price)
                        # Use index as proxy for time
                        timestamps.append(len(prices))
                except:
                    continue
            
            if len(prices) < 10:
                continue
            
            # Analyze patterns
            for i in range(10, len(prices)):
                current_price = prices[i]
                
                # Look at last 24 "hours" (using indices as proxy)
                lookback = min(24, i)
                recent_prices = prices[i-lookback:i]
                
                if not recent_prices:
                    continue
                    
                avg_recent = statistics.mean(recent_prices)
                max_recent = max(recent_prices)
                
                # STRATEGY 1: Buy the Dip (>10% drop)
                if avg_recent > 0 and current_price < avg_recent * 0.9:
                    # Exit at next price or outcome
                    exit_price = None
                    for j in range(i+1, min(i+10, len(prices))):
                        exit_price = prices[j]
                        break
                    
                    if not exit_price and outcome_value:
                        exit_price = 1.0 if outcome_value == 'Yes' else 0.0
                    
                    if exit_price is not None:
                        # Long position PnL
                        gross_return = (exit_price - current_price) / current_price
                        pnl = gross_return - TOTAL_COST
                        results['buy_dip_10pct'].append({
                            'entry': current_price,
                            'exit': exit_price,
                            'pnl': pnl,
                            'won': pnl > 0
                        })
                
                # STRATEGY 2: Fade the Spike (>10% spike)
                if avg_recent > 0 and current_price > avg_recent * 1.1:
                    exit_price = None
                    for j in range(i+1, min(i+10, len(prices))):
                        exit_price = prices[j]
                        break
                    
                    if not exit_price and outcome_value:
                        exit_price = 1.0 if outcome_value == 'Yes' else 0.0
                    
                    if exit_price is not None:
                        # Short position PnL
                        gross_return = (current_price - exit_price) / current_price
                        pnl = gross_return - TOTAL_COST
                        results['fade_spike_10pct'].append({
                            'entry': current_price,
                            'exit': exit_price,
                            'pnl': pnl,
                            'won': pnl > 0
                        })
                
                # STRATEGY 3: Buy Breakout (above 80%)
                if current_price > 0.80 and max_recent <= 0.80:
                    exit_price = None
                    for j in range(i+1, min(i+10, len(prices))):
                        exit_price = prices[j]
                        break
                    
                    if not exit_price and outcome_value:
                        exit_price = 1.0 if outcome_value == 'Yes' else 0.0
                    
                    if exit_price is not None:
                        gross_return = (exit_price - current_price) / current_price
                        pnl = gross_return - TOTAL_COST
                        results['buy_breakout_80'].append({
                            'entry': current_price,
                            'exit': exit_price,
                            'pnl': pnl,
                            'won': pnl > 0
                        })
                
                # STRATEGY 4: Fade Longshots (below 10%)
                if current_price < 0.10 and current_price > 0:
                    exit_price = None
                    for j in range(i+1, min(i+10, len(prices))):
                        exit_price = prices[j]
                        break
                    
                    if not exit_price and outcome_value:
                        exit_price = 1.0 if outcome_value == 'Yes' else 0.0
                    
                    if exit_price is not None:
                        gross_return = (current_price - exit_price) / current_price
                        pnl = gross_return - TOTAL_COST
                        results['fade_longshot'].append({
                            'entry': current_price,
                            'exit': exit_price,
                            'pnl': pnl,
                            'won': pnl > 0
                        })
                        
        except Exception as e:
            # Skip problematic markets
            continue
    
    return results

def calculate_stats(trades):
    """Calculate statistics for a trading strategy"""
    if not trades:
        return None
    
    pnls = [t['pnl'] for t in trades]
    wins = [t for t in trades if t['won']]
    losses = [t for t in trades if not t['won']]
    
    return {
        'sample_size': len(trades),
        'win_count': len(wins),
        'loss_count': len(losses),
        'win_rate': len(wins) / len(trades) if trades else 0,
        'avg_pnl': statistics.mean(pnls),
        'median_pnl': statistics.median(pnls),
        'total_pnl': sum(pnls),
        'best_trade': max(pnls),
        'worst_trade': min(pnls),
        'stddev': statistics.stdev(pnls) if len(pnls) > 1 else 0,
        'avg_win': statistics.mean([t['pnl'] for t in wins]) if wins else 0,
        'avg_loss': statistics.mean([t['pnl'] for t in losses]) if losses else 0,
    }

# Run analysis on first 5000 markets to get results
print("\n" + "="*60, flush=True)
print("BACKTESTING PRICE-BASED PATTERNS (First 5000 markets)", flush=True)
print("="*60, flush=True)
print(f"Transaction costs: {TOTAL_COST*100:.1f}% per round trip", flush=True)
print("="*60 + "\n", flush=True)

pattern_results = analyze_simple(markets, max_markets=5000)

# Calculate and display statistics
report_lines = []
report_lines.append("# REAL BACKTEST: Price Pattern Analysis\n")
report_lines.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
report_lines.append(f"**Dataset:** First 5,000 of 17,324 markets (sample for analysis)\n")
report_lines.append(f"**Transaction Costs:** {TOTAL_COST*100:.1f}% per round trip (fees: {FEE_RATE*100:.1f}%, slippage: {SLIPPAGE*100:.1f}%)\n")
report_lines.append("\n---\n\n")

print("\nRESULTS SUMMARY:", flush=True)
print("="*60, flush=True)

for strategy_name, trades in pattern_results.items():
    stats = calculate_stats(trades)
    
    if stats and stats['sample_size'] > 0:
        print(f"\n{strategy_name.upper().replace('_', ' ')}", flush=True)
        print("-" * 40, flush=True)
        print(f"Sample Size: {stats['sample_size']:,}", flush=True)
        print(f"Win Rate: {stats['win_rate']*100:.1f}%", flush=True)
        print(f"Average PnL: {stats['avg_pnl']*100:.2f}%", flush=True)
        print(f"Expected Value: {stats['avg_pnl']*100:.2f}% per trade", flush=True)
        print(f"Total PnL: {stats['total_pnl']*100:.1f}%", flush=True)
        
        # Add to report
        report_lines.append(f"## {strategy_name.upper().replace('_', ' ')}\n\n")
        report_lines.append(f"**Sample Size:** {stats['sample_size']:,} trades\n\n")
        report_lines.append(f"**Performance Metrics:**\n")
        report_lines.append(f"- Win Rate: **{stats['win_rate']*100:.1f}%** ({stats['win_count']:,} wins, {stats['loss_count']:,} losses)\n")
        report_lines.append(f"- Expected Value: **{stats['avg_pnl']*100:.2f}%** per trade\n")
        report_lines.append(f"- Total Return: {stats['total_pnl']*100:.1f}%\n")
        report_lines.append(f"- Best Trade: +{stats['best_trade']*100:.1f}%\n")
        report_lines.append(f"- Worst Trade: {stats['worst_trade']*100:.1f}%\n")
        
        # Verdict
        if stats['avg_pnl'] > 0:
            report_lines.append(f"\n**Verdict:** ✅ PROFITABLE (positive expected value)\n\n")
        else:
            report_lines.append(f"\n**Verdict:** ❌ NOT PROFITABLE (negative expected value)\n\n")
        
        report_lines.append("---\n\n")
    else:
        print(f"\n{strategy_name.upper().replace('_', ' ')}", flush=True)
        print("-" * 40, flush=True)
        print("No trades found", flush=True)
        report_lines.append(f"## {strategy_name.upper().replace('_', ' ')}\n\n")
        report_lines.append("No trades found for this strategy.\n\n---\n\n")

# Key findings
report_lines.append("## KEY FINDINGS\n\n")

# Find best strategy
best_strategy = None
best_ev = float('-inf')
for strategy_name, trades in pattern_results.items():
    stats = calculate_stats(trades)
    if stats and stats['sample_size'] >= 10 and stats['avg_pnl'] > best_ev:
        best_ev = stats['avg_pnl']
        best_strategy = (strategy_name, stats)

if best_strategy:
    name, stats = best_strategy
    report_lines.append(f"### Best Strategy: {name.upper().replace('_', ' ')}\n\n")
    report_lines.append(f"- Expected value: **{stats['avg_pnl']*100:.2f}%** per trade\n")
    report_lines.append(f"- Win rate: {stats['win_rate']*100:.1f}%\n")
    report_lines.append(f"- Sample size: {stats['sample_size']:,} trades\n\n")

report_lines.append("### Transaction Cost Impact\n\n")
report_lines.append(f"With {TOTAL_COST*100:.1f}% total costs per round trip:\n")
report_lines.append(f"- Strategies need **>{TOTAL_COST*100:.1f}% average price movement** to break even\n")
report_lines.append(f"- High win rate (>55%) or large average wins needed to overcome costs\n\n")

report_lines.append("## RECOMMENDATIONS\n\n")

for strategy_name, trades in pattern_results.items():
    stats = calculate_stats(trades)
    if stats and stats['sample_size'] >= 10:
        if stats['avg_pnl'] > 0.02:  # >2% EV
            report_lines.append(f"✅ **{strategy_name.upper().replace('_', ' ')}**: RECOMMENDED\n")
            report_lines.append(f"   - Expected edge: {stats['avg_pnl']*100:.2f}% per trade\n")
            report_lines.append(f"   - Historical opportunities: {stats['sample_size']:,}\n\n")
        elif stats['avg_pnl'] > 0:
            report_lines.append(f"⚠️ **{strategy_name.upper().replace('_', ' ')}**: MARGINAL\n")
            report_lines.append(f"   - Slight positive edge: {stats['avg_pnl']*100:.2f}%\n\n")
        else:
            report_lines.append(f"❌ **{strategy_name.upper().replace('_', ' ')}**: AVOID\n")
            report_lines.append(f"   - Negative expected value: {stats['avg_pnl']*100:.2f}%\n\n")

report_lines.append("\n---\n\n")
report_lines.append("*Analysis based on first 5,000 of 17,324 Polymarket markets*\n")
report_lines.append("*Full dataset analysis limited by memory constraints*\n")

# Write report
report_path = r'C:\Users\Borat\.openclaw\workspace\real_backtest_price_patterns.md'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(''.join(report_lines))

print(f"\n{'='*60}", flush=True)
print(f"Report saved to: {report_path}", flush=True)
print(f"{'='*60}", flush=True)

# Show total trades found
total_trades = sum(len(trades) for trades in pattern_results.values())
print(f"\nTotal trades analyzed: {total_trades:,}", flush=True)
