#!/usr/bin/env python3
"""
REAL BACKTESTER #3: Price-Based Pattern Analysis (v2 - with error handling)
Analyzes 17,324 markets for profitable price patterns
"""

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import traceback

# Load data
print("Loading backtest dataset...", flush=True)
with open(r'C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json', 'r') as f:
    markets = json.load(f)

print(f"Loaded {len(markets)} markets", flush=True)

# Examine data structure
if markets:
    sample = markets[0]
    print(f"\nSample market keys: {list(sample.keys())}", flush=True)
    print(f"Question: {sample.get('question', 'N/A')[:80]}", flush=True)
    print(f"Price history entries: {len(sample.get('price_history', []))}", flush=True)
    if sample.get('price_history'):
        print(f"Sample price entry: {sample['price_history'][0]}", flush=True)

# TRANSACTION COSTS
FEE_RATE = 0.04  # 4% fee
SLIPPAGE = 0.015  # 1.5% average slippage
TOTAL_COST = FEE_RATE + SLIPPAGE  # 5.5% total per round trip

class Trade:
    def __init__(self, market_id, question, entry_price, entry_time, signal_type):
        self.market_id = market_id
        self.question = question
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.signal_type = signal_type
        self.exit_price = None
        self.exit_time = None
        self.pnl = None
        self.outcome = None
        
    def close(self, exit_price, exit_time, outcome=None):
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.outcome = outcome
        
        # Calculate PnL including transaction costs
        if self.signal_type in ['buy_dip', 'buy_breakout', 'buy_longshot']:
            # Long position
            gross_return = (exit_price - self.entry_price) / self.entry_price
            self.pnl = gross_return - TOTAL_COST
        else:  # sell/fade signals
            # Short position (or selling)
            gross_return = (self.entry_price - exit_price) / self.entry_price
            self.pnl = gross_return - TOTAL_COST
            
        return self.pnl

def parse_timestamp(ts):
    """Parse various timestamp formats"""
    try:
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts)
        elif isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts.replace('Z', '+00:00'))
            except:
                try:
                    return datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%fZ')
                except:
                    return None
        return None
    except:
        return None

def analyze_price_patterns(markets):
    """Analyze various price-based trading patterns"""
    
    results = {
        'buy_dip_10pct': [],  # Buy when price drops >10% in 24h
        'fade_spike_10pct': [],  # Sell when price spikes >10% in 24h
        'buy_breakout_80': [],  # Buy breakouts above 80%
        'fade_longshot': [],  # Fade prices below 10%
    }
    
    processed = 0
    skipped = 0
    errors = 0
    
    for market in markets:
        processed += 1
        if processed % 1000 == 0:
            print(f"Processed {processed}/{len(markets)} markets... (errors: {errors})", flush=True)
        
        try:
            price_history = market.get('price_history', [])
            if len(price_history) < 2:
                skipped += 1
                continue
                
            market_id = market.get('id', market.get('market_id', 'unknown'))
            question = market.get('question', 'Unknown')
            outcome_value = market.get('outcome')  # Final outcome: 'Yes' or 'No'
            
            # Sort by timestamp
            sorted_history = sorted(price_history, key=lambda x: parse_timestamp(x.get('t', x.get('timestamp', 0))) or datetime.min)
            
            # Analyze each price point
            for i in range(1, len(sorted_history)):
                try:
                    current = sorted_history[i]
                    previous_24h = []
                    
                    current_time = parse_timestamp(current.get('t', current.get('timestamp')))
                    current_price = float(current.get('p', current.get('price', 0)))
                    
                    if not current_time or current_price == 0:
                        continue
                    
                    # Get prices from last 24 hours
                    for j in range(max(0, i-50), i):  # Look back up to 50 entries
                        prev = sorted_history[j]
                        prev_time = parse_timestamp(prev.get('t', prev.get('timestamp')))
                        if prev_time and (current_time - prev_time).total_seconds() <= 86400:
                            prev_price = float(prev.get('p', prev.get('price', 0)))
                            if prev_price > 0:
                                previous_24h.append(prev_price)
                    
                    if not previous_24h:
                        continue
                        
                    avg_24h = statistics.mean(previous_24h)
                    max_24h = max(previous_24h)
                    min_24h = min(previous_24h)
                    
                    # STRATEGY 1: Buy the Dip (>10% drop in 24h)
                    if avg_24h > 0 and current_price < avg_24h * 0.9:
                        pct_drop = (avg_24h - current_price) / avg_24h
                        
                        # Find exit: sell after hold period or at market close
                        exit_price = None
                        for k in range(i+1, min(i+20, len(sorted_history))):  # Hold up to 20 periods
                            exit_price = float(sorted_history[k].get('p', sorted_history[k].get('price', 0)))
                            if exit_price > 0:
                                break
                        
                        if not exit_price and outcome_value:
                            # Use outcome as exit
                            exit_price = 1.0 if outcome_value == 'Yes' else 0.0
                        
                        if exit_price is not None and exit_price >= 0:
                            trade = Trade(market_id, question, current_price, current_time, 'buy_dip')
                            pnl = trade.close(exit_price, None, outcome_value)
                            results['buy_dip_10pct'].append({
                                'entry': current_price,
                                'exit': exit_price,
                                'pnl': pnl,
                                'drop_pct': pct_drop,
                                'won': pnl > 0
                            })
                    
                    # STRATEGY 2: Fade the Spike (>10% spike in 24h)
                    if avg_24h > 0 and current_price > avg_24h * 1.1:
                        pct_spike = (current_price - avg_24h) / avg_24h
                        
                        # Find exit
                        exit_price = None
                        for k in range(i+1, min(i+20, len(sorted_history))):
                            exit_price = float(sorted_history[k].get('p', sorted_history[k].get('price', 0)))
                            if exit_price > 0:
                                break
                        
                        if not exit_price and outcome_value:
                            exit_price = 1.0 if outcome_value == 'Yes' else 0.0
                        
                        if exit_price is not None and exit_price >= 0:
                            trade = Trade(market_id, question, current_price, current_time, 'fade_spike')
                            pnl = trade.close(exit_price, None, outcome_value)
                            results['fade_spike_10pct'].append({
                                'entry': current_price,
                                'exit': exit_price,
                                'pnl': pnl,
                                'spike_pct': pct_spike,
                                'won': pnl > 0
                            })
                    
                    # STRATEGY 3: Buy Breakout (price breaks above 80%)
                    if current_price > 0.80 and max_24h <= 0.80:
                        # Price just broke above 80%
                        exit_price = None
                        for k in range(i+1, min(i+20, len(sorted_history))):
                            exit_price = float(sorted_history[k].get('p', sorted_history[k].get('price', 0)))
                            if exit_price > 0:
                                break
                        
                        if not exit_price and outcome_value:
                            exit_price = 1.0 if outcome_value == 'Yes' else 0.0
                        
                        if exit_price is not None and exit_price >= 0:
                            trade = Trade(market_id, question, current_price, current_time, 'buy_breakout')
                            pnl = trade.close(exit_price, None, outcome_value)
                            results['buy_breakout_80'].append({
                                'entry': current_price,
                                'exit': exit_price,
                                'pnl': pnl,
                                'won': pnl > 0
                            })
                    
                    # STRATEGY 4: Fade Longshots (price below 10%)
                    if current_price < 0.10 and current_price > 0:
                        # Bet against longshots
                        exit_price = None
                        for k in range(i+1, min(i+20, len(sorted_history))):
                            exit_price = float(sorted_history[k].get('p', sorted_history[k].get('price', 0)))
                            if exit_price > 0:
                                break
                        
                        if not exit_price and outcome_value:
                            exit_price = 1.0 if outcome_value == 'Yes' else 0.0
                        
                        if exit_price is not None and exit_price >= 0:
                            trade = Trade(market_id, question, current_price, current_time, 'fade_longshot')
                            pnl = trade.close(exit_price, None, outcome_value)
                            results['fade_longshot'].append({
                                'entry': current_price,
                                'exit': exit_price,
                                'pnl': pnl,
                                'won': pnl > 0
                            })
                except Exception as e:
                    errors += 1
                    if errors <= 5:
                        print(f"Error processing price point: {e}", flush=True)
                    continue
                    
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"Error processing market {processed}: {e}", flush=True)
            continue
    
    print(f"\nProcessed {processed} markets, skipped {skipped} (insufficient data), errors: {errors}", flush=True)
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

# Run the analysis
print("\n" + "="*60, flush=True)
print("BACKTESTING PRICE-BASED PATTERNS", flush=True)
print("="*60, flush=True)
print(f"Transaction costs: {TOTAL_COST*100:.1f}% per round trip", flush=True)
print(f"  - Fees: {FEE_RATE*100:.1f}%", flush=True)
print(f"  - Slippage: {SLIPPAGE*100:.1f}%", flush=True)
print("="*60 + "\n", flush=True)

pattern_results = analyze_price_patterns(markets)

# Calculate and display statistics
report_lines = []
report_lines.append("# REAL BACKTEST: Price Pattern Analysis\n")
report_lines.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
report_lines.append(f"**Dataset:** 17,324 markets with historical price data\n")
report_lines.append(f"**Transaction Costs:** {TOTAL_COST*100:.1f}% per round trip (fees: {FEE_RATE*100:.1f}%, slippage: {SLIPPAGE*100:.1f}%)\n")
report_lines.append("\n---\n\n")

print("\nRESULTS SUMMARY:", flush=True)
print("="*60, flush=True)

for strategy_name, trades in pattern_results.items():
    stats = calculate_stats(trades)
    
    if stats:
        print(f"\n{strategy_name.upper().replace('_', ' ')}", flush=True)
        print("-" * 40, flush=True)
        print(f"Sample Size: {stats['sample_size']:,}", flush=True)
        print(f"Win Rate: {stats['win_rate']*100:.1f}%", flush=True)
        print(f"Average PnL: {stats['avg_pnl']*100:.2f}%", flush=True)
        print(f"Median PnL: {stats['median_pnl']*100:.2f}%", flush=True)
        print(f"Total PnL: {stats['total_pnl']*100:.1f}%", flush=True)
        print(f"Expected Value: {stats['avg_pnl']*100:.2f}% per trade", flush=True)
        print(f"Best Trade: +{stats['best_trade']*100:.1f}%", flush=True)
        print(f"Worst Trade: {stats['worst_trade']*100:.1f}%", flush=True)
        print(f"Std Dev: {stats['stddev']*100:.1f}%", flush=True)
        print(f"Avg Win: +{stats['avg_win']*100:.1f}%", flush=True)
        print(f"Avg Loss: {stats['avg_loss']*100:.1f}%", flush=True)
        
        # Add to report
        report_lines.append(f"## {strategy_name.upper().replace('_', ' ')}\n\n")
        report_lines.append(f"**Sample Size:** {stats['sample_size']:,} trades\n\n")
        report_lines.append(f"**Performance Metrics:**\n")
        report_lines.append(f"- Win Rate: **{stats['win_rate']*100:.1f}%** ({stats['win_count']:,} wins, {stats['loss_count']:,} losses)\n")
        report_lines.append(f"- Expected Value: **{stats['avg_pnl']*100:.2f}%** per trade\n")
        report_lines.append(f"- Median Return: {stats['median_pnl']*100:.2f}%\n")
        report_lines.append(f"- Total Return: {stats['total_pnl']*100:.1f}%\n")
        report_lines.append(f"- Best Trade: +{stats['best_trade']*100:.1f}%\n")
        report_lines.append(f"- Worst Trade: {stats['worst_trade']*100:.1f}%\n")
        report_lines.append(f"- Standard Deviation: {stats['stddev']*100:.1f}%\n")
        report_lines.append(f"- Average Win: +{stats['avg_win']*100:.1f}%\n")
        report_lines.append(f"- Average Loss: {stats['avg_loss']*100:.1f}%\n")
        
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

# Key findings and recommendations
report_lines.append("## KEY FINDINGS\n\n")

# Find best strategy
best_strategy = None
best_ev = float('-inf')
for strategy_name, trades in pattern_results.items():
    stats = calculate_stats(trades)
    if stats and stats['avg_pnl'] > best_ev and stats['sample_size'] >= 10:
        best_ev = stats['avg_pnl']
        best_strategy = (strategy_name, stats)

if best_strategy:
    name, stats = best_strategy
    report_lines.append(f"### Best Strategy: {name.upper().replace('_', ' ')}\n\n")
    report_lines.append(f"- Expected value: **{stats['avg_pnl']*100:.2f}%** per trade\n")
    report_lines.append(f"- Win rate: {stats['win_rate']*100:.1f}%\n")
    report_lines.append(f"- Sample size: {stats['sample_size']:,} trades\n\n")

report_lines.append("### Transaction Cost Impact\n\n")
report_lines.append(f"With {TOTAL_COST*100:.1f}% total costs per round trip, strategies need:\n")
report_lines.append(f"- **>{TOTAL_COST*100:.1f}% average price movement** to break even\n")
report_lines.append(f"- **High win rate** (>55%) or large average wins to overcome costs\n\n")

report_lines.append("### Pattern Analysis Summary\n\n")
profitable_count = sum(1 for strategy_name, trades in pattern_results.items() 
                       if calculate_stats(trades) and calculate_stats(trades)['avg_pnl'] > 0)
report_lines.append(f"- Profitable strategies: {profitable_count}/4\n")
report_lines.append(f"- Total trades analyzed: {sum(len(trades) for trades in pattern_results.values()):,}\n\n")

report_lines.append("## RECOMMENDATIONS\n\n")
report_lines.append("Based on this backtest of 17,324 real markets:\n\n")

for strategy_name, trades in pattern_results.items():
    stats = calculate_stats(trades)
    if stats and stats['sample_size'] >= 10:
        if stats['avg_pnl'] > 0.02:  # >2% EV
            report_lines.append(f"✅ **{strategy_name.upper().replace('_', ' ')}**: RECOMMENDED\n")
            report_lines.append(f"   - Trade when signals appear ({stats['sample_size']:,} historical opportunities)\n")
            report_lines.append(f"   - Expected edge: {stats['avg_pnl']*100:.2f}% per trade\n\n")
        elif stats['avg_pnl'] > 0:
            report_lines.append(f"⚠️ **{strategy_name.upper().replace('_', ' ')}**: MARGINAL\n")
            report_lines.append(f"   - Slightly positive but edge is small\n")
            report_lines.append(f"   - Expected edge: {stats['avg_pnl']*100:.2f}% per trade\n\n")
        else:
            report_lines.append(f"❌ **{strategy_name.upper().replace('_', ' ')}**: AVOID\n")
            report_lines.append(f"   - Negative expected value ({stats['avg_pnl']*100:.2f}%)\n")
            report_lines.append(f"   - Transaction costs eat all profits\n\n")

report_lines.append("\n---\n\n")
report_lines.append("*Backtest completed using real historical data from 17,324 Polymarket markets*\n")

# Write report
report_path = r'C:\Users\Borat\.openclaw\workspace\real_backtest_price_patterns.md'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(''.join(report_lines))

print(f"\n{'='*60}", flush=True)
print(f"Report saved to: {report_path}", flush=True)
print(f"{'='*60}", flush=True)
