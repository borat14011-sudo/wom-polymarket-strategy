import json
import csv
import re
from datetime import datetime
from collections import defaultdict
import statistics

# ============================================
# DATA LOADING
# ============================================

print("="*80)
print("DATA-DRIVEN VALIDATION ENGINE")
print("Validating Grade A Trading Strategies with REAL Historical Data")
print("="*80)

# Load Polymarket resolved markets
print("\n[LOADING] Loading polymarket_resolved_markets.json...")
with open('polymarket_resolved_markets.json', 'r', encoding='utf-8-sig') as f:
    markets_data = json.load(f)
print(f"[OK] Loaded {len(markets_data)} resolved markets")

# Load backtest results
print("\n[LOADING] Loading backtest_results.csv...")
backtest_data = []
with open('backtest_results.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row['pnl'] = float(row['pnl'])
        row['roi'] = float(row['roi'])
        row['entry_price'] = float(row['entry_price'])
        row['exit_price'] = float(row['exit_price'])
        backtest_data.append(row)
print(f"[OK] Loaded {len(backtest_data)} backtest trades")

# ============================================
# TASK 1: IDENTIFY MUSK MARKETS
# ============================================

print("\n" + "="*80)
print("TASK 1: MUSK-RELATED MARKETS ANALYSIS")
print("="*80)

musk_keywords = ['musk', 'elon', 'tesla', 'twitter', 'x.com', 'doge', 'dogecoin']
musk_markets = []

for market in markets_data:
    question = market.get('question', '').lower()
    event_title = market.get('event_title', '').lower()
    description = market.get('description', '').lower()
    
    text_to_search = f"{question} {event_title} {description}"
    
    if any(keyword in text_to_search for keyword in musk_keywords):
        musk_markets.append({
            'market_id': market.get('market_id'),
            'question': market.get('question'),
            'event_title': market.get('event_title'),
            'winner': market.get('winner'),
            'volume_usd': float(market.get('volume_usd', 0)),
            'final_prices': market.get('final_prices'),
            'created_time': market.get('created_time'),
            'closed': market.get('closed')
        })

print(f"\n[SEARCH] Found {len(musk_markets)} Musk-related markets")

# Analyze Musk markets fade strategy (bet NO on all)
musk_no_wins = 0
musk_total_volume = 0
musk_results = []

for market in musk_markets:
    winner = market['winner']
    volume = market['volume_usd']
    musk_total_volume += volume
    
    # If we bet NO and winner is NO, we win
    if winner == 'No':
        musk_no_wins += 1
        result = 'WIN (NO won)'
    else:
        result = 'LOSS (YES won)'
    
    musk_results.append({
        'market_id': market['market_id'],
        'question': market['question'],
        'winner': winner,
        'volume': volume,
        'result': result
    })

musk_total = len(musk_markets)
musk_win_rate = (musk_no_wins / musk_total * 100) if musk_total > 0 else 0

print(f"\n[RESULTS] MUSK FADE STRATEGY RESULTS:")
print(f"   Total Markets: {musk_total}")
print(f"   NO wins (fade success): {musk_no_wins}")
print(f"   YES wins (fade failure): {musk_total - musk_no_wins}")
print(f"   ACTUAL Win Rate: {musk_win_rate:.2f}%")
print(f"   Total Volume: ${musk_total_volume:,.2f}")

# Save detailed Musk analysis
with open('MUSK_MARKETS_ANALYSIS.md', 'w', encoding='utf-8') as f:
    f.write("# MUSK-RELATED MARKETS ANALYSIS\n\n")
    f.write("## Summary\n\n")
    f.write(f"- **Total Musk Markets Found:** {musk_total}\n")
    f.write(f"- **NO Wins (Fade Success):** {musk_no_wins}\n")
    f.write(f"- **YES Wins (Fade Failure):** {musk_total - musk_no_wins}\n")
    f.write(f"- **ACTUAL Fade Win Rate:** {musk_win_rate:.2f}%\n")
    f.write(f"- **Total Volume:** ${musk_total_volume:,.2f}\n\n")
    f.write("## Detailed Market List\n\n")
    f.write("| Market ID | Question | Winner | Volume ($) | Fade Result |\n")
    f.write("|-----------|----------|--------|------------|-------------|\n")
    for r in musk_results:
        q = r['question'][:60] + "..." if len(r['question']) > 60 else r['question']
        f.write(f"| {r['market_id']} | {q} | {r['winner']} | {r['volume']:,.2f} | {r['result']} |\n")

print("[OK] Saved MUSK_MARKETS_ANALYSIS.md")

# ============================================
# TASK 2: IDENTIFY "WILL" PREDICTION MARKETS
# ============================================

print("\n" + "="*80)
print("TASK 2: 'WILL' PREDICTION MARKETS ANALYSIS")
print("="*80)

will_markets = []

for market in markets_data:
    question = market.get('question', '').strip()
    
    # Check if question starts with "Will"
    if question.lower().startswith('will'):
        will_markets.append({
            'market_id': market.get('market_id'),
            'question': market.get('question'),
            'event_title': market.get('event_title'),
            'winner': market.get('winner'),
            'volume_usd': float(market.get('volume_usd', 0)),
            'final_prices': market.get('final_prices'),
            'created_time': market.get('created_time'),
            'closed': market.get('closed')
        })

print(f"\n[SEARCH] Found {len(will_markets)} 'Will' prediction markets")

# Analyze Will markets fade strategy (bet NO on all)
will_no_wins = 0
will_total_volume = 0
will_results = []

for market in will_markets:
    winner = market['winner']
    volume = market['volume_usd']
    will_total_volume += volume
    
    # If we bet NO and winner is NO, we win
    if winner == 'No':
        will_no_wins += 1
        result = 'WIN (NO won)'
    else:
        result = 'LOSS (YES won)'
    
    will_results.append({
        'market_id': market['market_id'],
        'question': market['question'],
        'winner': winner,
        'volume': volume,
        'result': result
    })

will_total = len(will_markets)
will_win_rate = (will_no_wins / will_total * 100) if will_total > 0 else 0

print(f"\n[RESULTS] WILL PREDICTION FADE STRATEGY RESULTS:")
print(f"   Total Markets: {will_total}")
print(f"   NO wins (fade success): {will_no_wins}")
print(f"   YES wins (fade failure): {will_total - will_no_wins}")
print(f"   ACTUAL Win Rate: {will_win_rate:.2f}%")
print(f"   Total Volume: ${will_total_volume:,.2f}")

# Save detailed Will analysis
with open('WILL_MARKETS_ANALYSIS.md', 'w', encoding='utf-8') as f:
    f.write("# 'WILL' PREDICTION MARKETS ANALYSIS\n\n")
    f.write("## Summary\n\n")
    f.write(f"- **Total 'Will' Markets Found:** {will_total}\n")
    f.write(f"- **NO Wins (Fade Success):** {will_no_wins}\n")
    f.write(f"- **YES Wins (Fade Failure):** {will_total - will_no_wins}\n")
    f.write(f"- **ACTUAL Fade Win Rate:** {will_win_rate:.2f}%\n")
    f.write(f"- **Total Volume:** ${will_total_volume:,.2f}\n\n")
    f.write("## Detailed Market List (First 100)\n\n")
    f.write("| Market ID | Question | Winner | Volume ($) | Fade Result |\n")
    f.write("|-----------|----------|--------|------------|-------------|\n")
    for r in will_results[:100]:  # Limit to first 100 for readability
        q = r['question'][:60] + "..." if len(r['question']) > 60 else r['question']
        f.write(f"| {r['market_id']} | {q} | {r['winner']} | {r['volume']:,.2f} | {r['result']} |\n")
    if len(will_results) > 100:
        f.write(f"\n... and {len(will_results) - 100} more markets\n")

print("[OK] Saved WILL_MARKETS_ANALYSIS.md")

# ============================================
# TASK 3: ANALYZE BACKTEST RESULTS
# ============================================

print("\n" + "="*80)
print("TASK 3: BACKTEST RESULTS ANALYSIS")
print("="*80)

# Group by strategy
strategies = defaultdict(list)
for trade in backtest_data:
    strategies[trade['strategy']].append(trade)

print(f"\n[ANALYSIS] Found {len(strategies)} strategies in backtest data:")
for strategy, trades in strategies.items():
    print(f"   - {strategy}: {len(trades)} trades")

# Calculate aggregate statistics
total_trades = len(backtest_data)
winning_trades = [t for t in backtest_data if t['pnl'] > 0]
losing_trades = [t for t in backtest_data if t['pnl'] <= 0]

win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0

pnl_values = [t['pnl'] for t in backtest_data]
total_pnl = sum(pnl_values)
avg_pnl = statistics.mean(pnl_values) if pnl_values else 0

roi_values = [t['roi'] for t in backtest_data]
avg_roi = statistics.mean(roi_values) if roi_values else 0
total_roi = sum(roi_values)

# Calculate Sharpe ratio (simplified, assuming risk-free rate = 0)
if len(roi_values) > 1:
    roi_std = statistics.stdev(roi_values)
    sharpe_ratio = (avg_roi / roi_std) * (252 ** 0.5) if roi_std > 0 else 0  # Annualized
else:
    sharpe_ratio = 0

# Calculate maximum drawdown
cumulative_pnl = []
running_total = 0
for t in backtest_data:
    running_total += t['pnl']
    cumulative_pnl.append(running_total)

peak = 0
max_drawdown = 0
for pnl in cumulative_pnl:
    if pnl > peak:
        peak = pnl
    drawdown = peak - pnl
    if drawdown > max_drawdown:
        max_drawdown = drawdown

# Calculate profit factor
gross_profits = sum(t['pnl'] for t in winning_trades)
gross_losses = abs(sum(t['pnl'] for t in losing_trades))
profit_factor = gross_profits / gross_losses if gross_losses > 0 else float('inf')

# Analyze consecutive losses
consecutive_losses = 0
max_consecutive_losses = 0
for t in backtest_data:
    if t['pnl'] <= 0:
        consecutive_losses += 1
        max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
    else:
        consecutive_losses = 0

print(f"\n[RESULTS] AGGREGATE BACKTEST STATISTICS:")
print(f"   Total Trades: {total_trades}")
print(f"   Winning Trades: {len(winning_trades)}")
print(f"   Losing Trades: {len(losing_trades)}")
print(f"   Win Rate: {win_rate:.2f}%")
print(f"   Total P&L: ${total_pnl:,.4f}")
print(f"   Average P&L per Trade: ${avg_pnl:.4f}")
print(f"   Average ROI: {avg_roi:.4f}")
print(f"   Total ROI: {total_roi:.4f}")
print(f"   Sharpe Ratio: {sharpe_ratio:.4f}")
print(f"   Maximum Drawdown: ${max_drawdown:,.4f}")
print(f"   Profit Factor: {profit_factor:.4f}")
print(f"   Maximum Consecutive Losses: {max_consecutive_losses}")

# Check for losing periods
losing_periods = []
in_losing_period = False
period_start = None
for i, t in enumerate(backtest_data):
    if t['pnl'] <= 0:
        if not in_losing_period:
            in_losing_period = True
            period_start = i
    else:
        if in_losing_period:
            losing_periods.append((period_start, i-1))
            in_losing_period = False

if in_losing_period:
    losing_periods.append((period_start, len(backtest_data)-1))

print(f"\n[RESULTS] LOSING PERIODS:")
print(f"   Number of losing periods: {len(losing_periods)}")

# Save backtest report
with open('REAL_BACKTEST_REPORT.md', 'w', encoding='utf-8') as f:
    f.write("# REAL BACKTEST REPORT\n\n")
    f.write("## Aggregate Statistics\n\n")
    f.write(f"| Metric | Value |\n")
    f.write(f"|--------|-------|\n")
    f.write(f"| Total Trades | {total_trades} |\n")
    f.write(f"| Winning Trades | {len(winning_trades)} |\n")
    f.write(f"| Losing Trades | {len(losing_trades)} |\n")
    f.write(f"| Win Rate | {win_rate:.2f}% |\n")
    f.write(f"| Total P&L | ${total_pnl:,.4f} |\n")
    f.write(f"| Average P&L per Trade | ${avg_pnl:.4f} |\n")
    f.write(f"| Average ROI | {avg_roi:.4f} |\n")
    f.write(f"| Total ROI | {total_roi:.4f} |\n")
    f.write(f"| Sharpe Ratio | {sharpe_ratio:.4f} |\n")
    f.write(f"| Maximum Drawdown | ${max_drawdown:,.4f} |\n")
    f.write(f"| Profit Factor | {profit_factor:.4f} |\n")
    f.write(f"| Maximum Consecutive Losses | {max_consecutive_losses} |\n\n")
    
    f.write("## Strategy Breakdown\n\n")
    f.write("| Strategy | Trades | Win Rate | Avg P&L |\n")
    f.write("|----------|--------|----------|---------|\n")
    for strategy, trades in strategies.items():
        s_wins = len([t for t in trades if t['pnl'] > 0])
        s_win_rate = s_wins / len(trades) * 100
        s_avg_pnl = statistics.mean([t['pnl'] for t in trades])
        f.write(f"| {strategy} | {len(trades)} | {s_win_rate:.2f}% | ${s_avg_pnl:.4f} |\n")

print("[OK] Saved REAL_BACKTEST_REPORT.md")

# ============================================
# TASK 4: CROSS-VALIDATION
# ============================================

print("\n" + "="*80)
print("TASK 4: CROSS-VALIDATION")
print("="*80)

claimed_musk_win_rate = 84.9
claimed_will_win_rate = 76.7

musk_diff = abs(musk_win_rate - claimed_musk_win_rate)
will_diff = abs(will_win_rate - claimed_will_win_rate)

print(f"\n[VALIDATION] CLAIMED vs ACTUAL WIN RATES:")
print(f"\n   MUSK HYPE FADE:")
print(f"   - Claimed: {claimed_musk_win_rate}%")
print(f"   - Actual: {musk_win_rate:.2f}%")
print(f"   - Difference: {musk_diff:.2f}%")
print(f"   - Within 5%: {'[YES]' if musk_diff <= 5 else '[NO]'}")

print(f"\n   WILL PREDICTION FADE:")
print(f"   - Claimed: {claimed_will_win_rate}%")
print(f"   - Actual: {will_win_rate:.2f}%")
print(f"   - Difference: {will_diff:.2f}%")
print(f"   - Within 5%: {'[YES]' if will_diff <= 5 else '[NO]'}")

# Save cross-validation report
with open('CROSS_VALIDATION.md', 'w', encoding='utf-8') as f:
    f.write("# CROSS-VALIDATION REPORT\n\n")
    f.write("## Claimed vs Actual Win Rates\n\n")
    f.write("### MUSK HYPE FADE Strategy\n\n")
    f.write(f"| Metric | Value |\n")
    f.write(f"|--------|-------|\n")
    f.write(f"| Claimed Win Rate | {claimed_musk_win_rate}% |\n")
    f.write(f"| Actual Win Rate | {musk_win_rate:.2f}% |\n")
    f.write(f"| Difference | {musk_diff:.2f}% |\n")
    f.write(f"| Within 5% Threshold | {'[YES]' if musk_diff <= 5 else '[NO]'} |\n\n")
    
    f.write("### WILL PREDICTION FADE Strategy\n\n")
    f.write(f"| Metric | Value |\n")
    f.write(f"|--------|-------|\n")
    f.write(f"| Claimed Win Rate | {claimed_will_win_rate}% |\n")
    f.write(f"| Actual Win Rate | {will_win_rate:.2f}% |\n")
    f.write(f"| Difference | {will_diff:.2f}% |\n")
    f.write(f"| Within 5% Threshold | {'[YES]' if will_diff <= 5 else '[NO]'} |\n\n")
    
    f.write("## Verdict\n\n")
    if musk_diff <= 5 and will_diff <= 5:
        f.write("[VALIDATED] Both strategies are within 5% of claimed win rates.\n")
    else:
        f.write("[NOT VALIDATED] One or both strategies exceed 5% difference from claimed rates.\n")

print("[OK] Saved CROSS_VALIDATION.md")

# ============================================
# TASK 5: IRONCLAD ASSESSMENT
# ============================================

print("\n" + "="*80)
print("TASK 5: IRONCLAD ASSESSMENT")
print("="*80)

# Calculate profitability after fees (5% fee assumption)
fee_rate = 0.05
fees_paid = total_pnl * fee_rate if total_pnl > 0 else 0
profit_after_fees = total_pnl - fees_paid
is_profitable_after_fees = profit_after_fees > 0

# Check consistency (win rate stability across time)
# Split trades into halves
half_point = total_trades // 2
first_half = backtest_data[:half_point]
second_half = backtest_data[half_point:]

first_half_wins = len([t for t in first_half if t['pnl'] > 0])
second_half_wins = len([t for t in second_half if t['pnl'] > 0])

first_half_win_rate = first_half_wins / len(first_half) * 100 if first_half else 0
second_half_win_rate = second_half_wins / len(second_half) * 100 if second_half else 0

consistency = abs(first_half_win_rate - second_half_win_rate) < 10

# Risk-adjusted returns
sharpe_acceptable = sharpe_ratio > 1.0

print(f"\n[ASSESSMENT] DETAILED ASSESSMENT:")
print(f"\n   1. PROFITABLE AFTER FEES (5% fee)?")
print(f"      - Total P&L: ${total_pnl:,.4f}")
print(f"      - Fees (5%): ${fees_paid:,.4f}")
print(f"      - Profit After Fees: ${profit_after_fees:,.4f}")
print(f"      - Verdict: {'[YES]' if is_profitable_after_fees else '[NO]'}")

print(f"\n   2. PERFORMANCE CONSISTENT?")
print(f"      - First Half Win Rate: {first_half_win_rate:.2f}%")
print(f"      - Second Half Win Rate: {second_half_win_rate:.2f}%")
print(f"      - Difference: {abs(first_half_win_rate - second_half_win_rate):.2f}%")
print(f"      - Verdict: {'[YES]' if consistency else '[NO]'}")

print(f"\n   3. LOSING PERIODS?")
print(f"      - Number of losing periods: {len(losing_periods)}")
print(f"      - Verdict: {'[YES - Losing periods exist]' if losing_periods else '[NO - No losing periods]'}")

print(f"\n   4. MAXIMUM CONSECUTIVE LOSSES?")
print(f"      - Maximum: {max_consecutive_losses} consecutive losses")
print(f"      - Verdict: {'[HIGH]' if max_consecutive_losses > 10 else '[ACCEPTABLE]'}")

print(f"\n   5. RISK-ADJUSTED RETURNS (Sharpe > 1.0)?")
print(f"      - Sharpe Ratio: {sharpe_ratio:.4f}")
print(f"      - Verdict: {'[YES]' if sharpe_acceptable else '[NO]'}")

# Save final verdict
with open('FINAL_IRONCLAD_VERDICT.md', 'w', encoding='utf-8') as f:
    f.write("# FINAL IRONCLAD VERDICT\n\n")
    f.write("## Data-Driven Assessment of Grade A Strategies\n\n")
    f.write("### Executive Summary\n\n")
    f.write("Based on rigorous analysis of REAL historical data:\n\n")
    
    f.write("#### Musk Hype Fade Strategy\n\n")
    f.write(f"- **Markets Analyzed:** {musk_total}\n")
    f.write(f"- **Actual Win Rate:** {musk_win_rate:.2f}%\n")
    f.write(f"- **Claimed Win Rate:** {claimed_musk_win_rate}%\n")
    f.write(f"- **Validation:** {'[VALIDATED]' if musk_diff <= 5 else '[NOT VALIDATED]'}\n\n")
    
    f.write("#### Will Prediction Fade Strategy\n\n")
    f.write(f"- **Markets Analyzed:** {will_total}\n")
    f.write(f"- **Actual Win Rate:** {will_win_rate:.2f}%\n")
    f.write(f"- **Claimed Win Rate:** {claimed_will_win_rate}%\n")
    f.write(f"- **Validation:** {'[VALIDATED]' if will_diff <= 5 else '[NOT VALIDATED]'}\n\n")
    
    f.write("### Backtest Performance Analysis\n\n")
    f.write(f"| Metric | Value | Status |\n")
    f.write(f"|--------|-------|--------|\n")
    f.write(f"| Profitable After Fees | ${profit_after_fees:,.4f} | {'[PASS]' if is_profitable_after_fees else '[FAIL]'} |\n")
    f.write(f"| Consistent Performance | {abs(first_half_win_rate - second_half_win_rate):.2f}% diff | {'[PASS]' if consistency else '[FAIL]'} |\n")
    f.write(f"| Losing Periods | {len(losing_periods)} periods | {'[PASS]' if not losing_periods else '[WARNING]'} |\n")
    f.write(f"| Max Consecutive Losses | {max_consecutive_losses} | {'[PASS]' if max_consecutive_losses <= 10 else '[WARNING]'} |\n")
    f.write(f"| Sharpe Ratio | {sharpe_ratio:.4f} | {'[PASS]' if sharpe_acceptable else '[FAIL]'} |\n\n")
    
    f.write("### Final Verdict\n\n")
    
    # Count pass/fail
    checks_passed = sum([
        is_profitable_after_fees,
        consistency,
        not losing_periods or len(losing_periods) < 5,
        max_consecutive_losses <= 10,
        sharpe_acceptable
    ])
    
    f.write(f"**Validation Score: {checks_passed}/5**\n\n")
    
    if checks_passed >= 4 and musk_diff <= 5 and will_diff <= 5:
        f.write("[GRADE A CONFIRMED] Strategies are validated by real data.\n\n")
    elif checks_passed >= 3:
        f.write("[GRADE B] Strategies show promise but have some concerns.\n\n")
    else:
        f.write("[GRADE C/FAIL] Strategies do not meet validation criteria.\n\n")
    
    f.write("### Key Findings\n\n")
    f.write("1. **Data Quality:** Analysis based on " + str(len(markets_data)) + " resolved markets and " + str(len(backtest_data)) + " backtest trades.\n")
    f.write("2. **Win Rate Accuracy:** " + ("Claimed win rates are accurate within 5%" if musk_diff <= 5 and will_diff <= 5 else "Claimed win rates differ significantly from actual data") + ".\n")
    f.write("3. **Profitability:** " + ("Strategies remain profitable after 5% fees" if is_profitable_after_fees else "Strategies may not be profitable after fees") + ".\n")
    f.write("4. **Risk Profile:** Sharpe ratio of " + f"{sharpe_ratio:.4f} indicates " + ("good risk-adjusted returns" if sharpe_acceptable else "poor risk-adjusted returns") + ".\n\n")
    
    f.write("---\n\n")
    f.write("*This assessment is based solely on the provided data files. No simulated or fabricated data was used.*\n")

print("[OK] Saved FINAL_IRONCLAD_VERDICT.md")

print("\n" + "="*80)
print("VALIDATION COMPLETE")
print("="*80)
print("\n[OUTPUT] Generated Files:")
print("   1. MUSK_MARKETS_ANALYSIS.md")
print("   2. WILL_MARKETS_ANALYSIS.md")
print("   3. REAL_BACKTEST_REPORT.md")
print("   4. CROSS_VALIDATION.md")
print("   5. FINAL_IRONCLAD_VERDICT.md")
