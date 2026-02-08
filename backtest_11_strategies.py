#!/usr/bin/env python3
"""
BACKTEST ALL 11 STRATEGIES
Tests all strategies from NEW_STRATEGY_PROPOSALS.md on 70K+ resolved markets
Validates claimed win rates with realistic fees and slippage
"""

import json
import sys
from datetime import datetime
from collections import defaultdict
import re

# Fee structure: 4% trading fee + 1% slippage = 5% total
TRADING_FEE = 0.04
SLIPPAGE = 0.01
TOTAL_COST = TRADING_FEE + SLIPPAGE  # 5%

# Strategy definitions from NEW_STRATEGY_PROPOSALS.md
STRATEGIES = {
    "MUSK_HYPE_FADE": {
        "claimed_winrate": 88.0,
        "description": "Bet NO on any Musk-related market",
        "keywords": ["musk", "elon", "tesla"],
        "condition": lambda m: any(kw in m['question'].lower() for kw in ["musk", "elon", "tesla"])
    },
    
    "TECH_HYPE_FADE": {
        "claimed_winrate": 78.2,
        "description": "Bet NO on tech company predictions",
        "keywords": ["apple", "google", "meta", "microsoft", "amazon", "nvidia", "openai", "deepseek", "iphone", "launch"],
        "condition": lambda m: any(kw in m['question'].lower() for kw in 
                                   ["apple", "google", "meta", "microsoft", "amazon", "nvidia", 
                                    "openai", "deepseek", "iphone", "android", "windows", "chatgpt", "gpt"])
    },
    
    "MICRO_MARKET_FADE": {
        "claimed_winrate": 77.2,
        "description": "Bet NO on markets with volume under $5,000",
        "keywords": [],  # Volume-based, not keyword
        "condition": lambda m: m.get('volume', 0) < 5000
    },
    
    "WILL_PREDICTION_FADE": {
        "claimed_winrate": 75.8,
        "description": "Bet NO on markets starting with 'Will'",
        "keywords": ["will"],
        "condition": lambda m: m['question'].strip().lower().startswith("will ")
    },
    
    "CONSENSUS_FADE": {
        "claimed_winrate": 75.1,
        "description": "Bet NO when early consensus forms (needs historical price data - using proxy)",
        "keywords": [],  # Price-based - we'll use a proxy
        "condition": lambda m: True  # We'll filter differently since we lack historical prices
    },
    
    "CELEBRITY_FADE": {
        "claimed_winrate": 76.2,
        "description": "Bet NO on celebrity-related markets",
        "keywords": ["trump", "biden", "taylor swift", "kanye", "kardashian", "celebrity", 
                     "oscar", "grammys", "emmy", "beyonce", "drake", "lebron"],
        "condition": lambda m: any(kw in m['question'].lower() for kw in 
                                   ["trump", "biden", "taylor swift", "kanye", "kardashian", 
                                    "oscar", "grammy", "emmy", "beyonce", "drake", "celebrity"])
    },
    
    "LATE_NIGHT_FADE": {
        "claimed_winrate": 74.1,
        "description": "Bet NO on markets created late at night (proxy: check creation time)",
        "keywords": [],  # Time-based
        "condition": lambda m: is_late_night_creation(m)
    },
    
    "COMPLEX_QUESTION_FADE": {
        "claimed_winrate": 71.4,
        "description": "Bet NO on complex questions (>100 chars or contains 'and'/'or')",
        "keywords": [],  # Length-based
        "condition": lambda m: len(m['question']) > 100 or ' and ' in m['question'].lower() or ' or ' in m['question'].lower()
    },
    
    "WEEKEND_FADE": {
        "claimed_winrate": 71.2,
        "description": "Bet NO on markets created on weekends",
        "keywords": [],  # Time-based
        "condition": lambda m: is_weekend_creation(m)
    },
    
    "SHORT_DURATION_FADE": {
        "claimed_winrate": 71.1,
        "description": "Bet NO on markets with <7 day duration",
        "keywords": [],  # Duration-based
        "condition": lambda m: is_short_duration(m)
    },
    
    "CRYPTO_HYPE_FADE": {
        "claimed_winrate": 66.0,
        "description": "Bet NO on crypto price predictions",
        "keywords": ["bitcoin", "btc", "ethereum", "eth", "crypto", "solana", "sol", 
                     "xrp", "doge", "ada", "cardano", "blockchain"],
        "condition": lambda m: any(kw in m['question'].lower() for kw in 
                                   ["bitcoin", "btc", "ethereum", "eth", "crypto", "solana", "sol", 
                                    "xrp", "ripple", "doge", "cardano", "ada", "blockchain", "coinbase"])
    }
}

def is_late_night_creation(market):
    """Check if market was created between 10 PM - 6 AM"""
    try:
        created = datetime.fromisoformat(market['created_at'].replace('Z', '+00:00'))
        hour = created.hour
        return hour >= 22 or hour < 6  # 10 PM - 6 AM
    except:
        return False

def is_weekend_creation(market):
    """Check if market was created on Saturday or Sunday"""
    try:
        created = datetime.fromisoformat(market['created_at'].replace('Z', '+00:00'))
        return created.weekday() >= 5  # 5 = Saturday, 6 = Sunday
    except:
        return False

def is_short_duration(market):
    """Check if market duration is less than 7 days"""
    try:
        created = datetime.fromisoformat(market['created_at'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(market['end_date'].replace('Z', '+00:00'))
        duration = (end - created).days
        return duration < 7
    except:
        return False

def load_markets(filepath):
    """Load market snapshot"""
    print(f"Loading markets from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total = data['summary']['total_markets']
    closed = data['summary']['closed_markets']
    print(f"Total markets: {total:,}")
    print(f"Closed markets: {closed:,}")
    
    return data['markets'], total, closed

def is_resolved(market):
    """Check if market is resolved with clear outcome"""
    if not market.get('closed'):
        return False
    
    outcome_prices = market.get('outcome_prices')
    if outcome_prices and len(outcome_prices) == 2:
        # If one price is 1 and other is 0, it's resolved
        return (outcome_prices[0] in [0, 1] and outcome_prices[1] in [0, 1] and
                outcome_prices[0] != outcome_prices[1])
    
    return False

def matches_strategy(market, strategy_name):
    """Check if market matches strategy criteria"""
    strategy = STRATEGIES[strategy_name]
    
    # Special handling for CONSENSUS_FADE (skip for now - needs historical prices)
    if strategy_name == "CONSENSUS_FADE":
        # Use high volume as proxy for consensus (imperfect but better than nothing)
        return market.get('volume', 0) > 50000
    
    try:
        return strategy['condition'](market)
    except Exception as e:
        return False

def simulate_trade(market, bet_side='NO'):
    """
    Simulate betting NO on a market with realistic fees
    
    Fees:
    - 4% trading fee (charged on entry)
    - 1% slippage (price impact)
    
    Returns: (won, gross_profit, net_profit, fees_paid, market_info)
    """
    outcome_prices = market.get('outcome_prices', [])
    
    if len(outcome_prices) != 2:
        return False, 0, 0, 0, None
    
    # Determine outcome: [1, 0] = Yes won, [0, 1] = No won
    yes_won = outcome_prices[0] == 1
    no_won = outcome_prices[1] == 1
    
    # For NO bet
    won = no_won
    outcome_str = "No" if no_won else "Yes"
    
    # Profit calculation with fees
    # Assume we bet $100 on NO at average price of 0.60 (typical for NO bets)
    stake = 100.0
    entry_price = 0.60  # Average NO price
    
    if won:
        # Win: Get $100 / 0.60 = $166.67 payout
        # Gross profit = payout - stake = $66.67
        gross_profit = stake / entry_price - stake
        
        # Fees: 4% of stake + 1% slippage
        fees = stake * TOTAL_COST
        net_profit = gross_profit - fees
    else:
        # Loss: Lose entire stake
        gross_profit = -stake
        fees = stake * TRADING_FEE  # Only entry fee charged (no exit)
        net_profit = -stake - fees
    
    return won, gross_profit, net_profit, fees, {
        'id': market.get('id'),
        'question': market.get('question', '')[:100],
        'outcome': outcome_str,
        'won': won,
        'volume': market.get('volume', 0)
    }

def backtest_strategy(markets, strategy_name, total_markets, closed_markets):
    """Backtest a single strategy"""
    print(f"\n{'='*100}")
    print(f"BACKTESTING: {strategy_name}")
    print(f"Claimed Win Rate: {STRATEGIES[strategy_name]['claimed_winrate']:.1f}%")
    print(f"{'='*100}")
    
    wins = 0
    losses = 0
    gross_profit = 0
    net_profit = 0
    total_fees = 0
    sample_trades = []
    
    matching_count = 0
    
    for market in markets:
        if not is_resolved(market):
            continue
            
        if matches_strategy(market, strategy_name):
            matching_count += 1
            won, gp, np, fees, trade_info = simulate_trade(market, 'NO')
            
            if won:
                wins += 1
            else:
                losses += 1
            
            gross_profit += gp
            net_profit += np
            total_fees += fees
            
            # Save sample trades (first 3 wins, first 3 losses)
            if (won and len([t for t in sample_trades if t['won']]) < 3) or \
               (not won and len([t for t in sample_trades if not t['won']]) < 3):
                sample_trades.append(trade_info)
    
    total_trades = wins + losses
    actual_winrate = (wins / total_trades * 100) if total_trades > 0 else 0
    claimed_winrate = STRATEGIES[strategy_name]['claimed_winrate']
    difference = actual_winrate - claimed_winrate
    edge_degradation = -difference  # Positive = worse than claimed
    
    # Calculate ROI
    total_staked = total_trades * 100  # $100 per trade
    roi_pct = (net_profit / total_staked * 100) if total_staked > 0 else 0
    
    # Determine status
    if total_trades == 0:
        status = "NO DATA"
        status_emoji = "❌"
    elif total_trades < 20:
        status = "INSUFFICIENT SAMPLE"
        status_emoji = "⚠️"
    elif actual_winrate >= claimed_winrate * 0.95:  # Within 5% of claim
        status = "VALIDATED"
        status_emoji = "✅"
    elif actual_winrate >= 55:  # Still profitable after fees
        status = "PROFITABLE (Degraded)"
        status_emoji = "⚠️"
    elif actual_winrate >= 50:
        status = "MARGINAL"
        status_emoji = "⚠️"
    else:
        status = "FAILED"
        status_emoji = "❌"
    
    result = {
        'strategy': strategy_name,
        'claimed': claimed_winrate,
        'actual': actual_winrate,
        'difference': difference,
        'edge_degradation': edge_degradation,
        'status': status,
        'status_emoji': status_emoji,
        'total_trades': total_trades,
        'wins': wins,
        'losses': losses,
        'gross_profit': gross_profit,
        'net_profit': net_profit,
        'total_fees': total_fees,
        'roi_pct': roi_pct,
        'sample_trades': sample_trades,
        'total_markets': total_markets,
        'closed_markets': closed_markets
    }
    
    print(f"\nMatching Markets: {matching_count:,}")
    print(f"Resolved Trades: {total_trades:,}")
    print(f"Wins: {wins:,} | Losses: {losses:,}")
    print(f"Actual Win Rate: {actual_winrate:.1f}%")
    print(f"Claimed Win Rate: {claimed_winrate:.1f}%")
    print(f"Difference: {difference:+.1f}%")
    print(f"Edge Degradation: {edge_degradation:+.1f}%")
    print(f"Gross P/L: ${gross_profit:+,.2f}")
    print(f"Fees Paid: ${total_fees:,.2f}")
    print(f"Net P/L: ${net_profit:+,.2f}")
    print(f"ROI: {roi_pct:+.2f}%")
    print(f"Status: {status}")
    
    return result

def generate_report(results, output_file):
    """Generate comprehensive markdown report"""
    
    # Get metadata from first result
    total_markets = results[0]['total_markets']
    closed_markets = results[0]['closed_markets']
    
    report = f"""# BACKTEST VALIDATION: ALL 11 STRATEGIES
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Dataset:** {total_markets:,} total markets, {closed_markets:,} resolved markets  
**Fee Structure:** 4% trading fee + 1% slippage = 5% total cost  
**Position Size:** $100 per trade (standardized)

---

## 🎯 EXECUTIVE SUMMARY

Validated all 11 strategies from NEW_STRATEGY_PROPOSALS.md against real historical data.

### Quick Stats

| Metric | Value |
|--------|-------|
| **Strategies Tested** | 11 |
| **Validated (≥95% of claim)** | {sum(1 for r in results if '✅' in r['status'])} |
| **Profitable (≥55% win rate)** | {sum(1 for r in results if r['actual'] >= 55)} |
| **Failed (<50% win rate)** | {sum(1 for r in results if r['actual'] < 50)} |
| **Total Trades Simulated** | {sum(r['total_trades'] for r in results):,} |
| **Combined Net P/L** | ${sum(r['net_profit'] for r in results):+,.2f} |

---

## 📊 RESULTS TABLE

| # | Strategy | Claimed | Actual | Diff | Trades | Net P/L | ROI | Status |
|---|----------|---------|--------|------|--------|---------|-----|--------|
"""
    
    for i, r in enumerate(results, 1):
        report += f"| {i} | {r['strategy']} | {r['claimed']:.1f}% | {r['actual']:.1f}% | {r['difference']:+.1f}% | {r['total_trades']:,} | ${r['net_profit']:+,.0f} | {r['roi_pct']:+.1f}% | {r['status_emoji']} {r['status']} |\n"
    
    report += "\n---\n\n## 📈 DETAILED RESULTS\n\n"
    
    for i, r in enumerate(results, 1):
        report += f"""### {i}. {r['strategy']} {r['status_emoji']} {r['status']}

**Description:** {STRATEGIES[r['strategy']]['description']}

**Performance Metrics:**
- **Claimed Win Rate:** {r['claimed']:.1f}%
- **Actual Win Rate:** {r['actual']:.1f}%
- **Difference:** {r['difference']:+.1f}% ({r['edge_degradation']:+.1f}% edge degradation)
- **Sample Size:** {r['total_trades']:,} trades
- **Win/Loss Record:** {r['wins']:,}W - {r['losses']:,}L

**Financial Results:**
- **Gross P/L:** ${r['gross_profit']:+,.2f}
- **Total Fees:** ${r['total_fees']:,.2f} (@ 5% per trade)
- **Net P/L:** ${r['net_profit']:+,.2f}
- **ROI:** {r['roi_pct']:+.2f}%
- **Avg P/L per Trade:** ${r['net_profit']/r['total_trades'] if r['total_trades'] > 0 else 0:+.2f}

**Sample Trades:**
"""
        
        if r['sample_trades']:
            for j, trade in enumerate(r['sample_trades'][:6], 1):
                result_str = "✅ WIN" if trade['won'] else "❌ LOSS"
                report += f"{j}. [{result_str}] {trade['question'][:80]}... (Outcome: {trade['outcome']}, Vol: ${trade['volume']:,.0f})\n"
        else:
            report += "No trades matched this strategy.\n"
        
        # Add interpretation
        if r['total_trades'] == 0:
            interpretation = "**⚠️ CRITICAL:** No trades matched this strategy. Criteria may be too restrictive or keywords need adjustment."
        elif r['total_trades'] < 20:
            interpretation = f"**⚠️ WARNING:** Sample size ({r['total_trades']}) is too small for statistical significance. Needs ≥50 trades for validation."
        elif r['actual'] >= r['claimed'] * 0.95:
            interpretation = f"**✅ VALIDATED:** Strategy performs as expected. Actual win rate within 5% of claim. {'Profitable after fees.' if r['net_profit'] > 0 else 'Unprofitable after fees - review position sizing.'}"
        elif r['actual'] >= 55:
            interpretation = f"**⚠️ DEGRADED BUT VIABLE:** Win rate is {abs(r['difference']):.1f}% below claim, but still profitable at {r['actual']:.1f}%. Edge degradation may be due to market evolution or data differences."
        elif r['actual'] >= 50:
            interpretation = f"**⚠️ MARGINAL:** Win rate around 50% means strategy breaks even before fees and loses money after fees. Not recommended for live trading."
        else:
            interpretation = f"**❌ FAILED:** Win rate {r['actual']:.1f}% is below 50%. Strategy loses money. Do not trade."
        
        report += f"\n{interpretation}\n\n---\n\n"
    
    # Overall recommendation
    validated = sum(1 for r in results if r['status'] == 'VALIDATED')
    profitable = sum(1 for r in results if r['actual'] >= 55 and r['total_trades'] >= 20)
    total_net_pl = sum(r['net_profit'] for r in results)
    
    report += f"""## 🎯 OVERALL ASSESSMENT

### Summary
- **Validated Strategies:** {validated}/11 (performed within 5% of claimed win rate)
- **Profitable Strategies:** {profitable}/11 (≥55% win rate, sufficient sample)
- **Combined Net P/L:** ${total_net_pl:+,.2f}
- **Average ROI Across All:** {sum(r['roi_pct'] for r in results)/len(results):.2f}%

### Recommendations

"""
    
    if validated >= 6:
        report += """**✅ STRONG VALIDATION**

Majority of strategies validated successfully. The systematic NO bias in Polymarket is confirmed by real data.

**Action Items:**
1. **Paper trade** the top 3-5 validated strategies for 30 days
2. Focus on strategies with:
   - Win rate ≥70%
   - Sample size ≥100 trades
   - Positive net P/L after fees
3. **Avoid** strategies with insufficient sample or failed validation
4. Monitor for market adaptation (edge may erode over time)

"""
    elif profitable >= 6:
        report += """**⚠️ MIXED RESULTS**

Strategies are profitable but show edge degradation vs claims. This could indicate:
1. Market conditions changed between proposal and backtest
2. Different data filtering/interpretation
3. Natural variance in win rates

**Action Items:**
1. **Recalibrate** claimed win rates based on actual results
2. **Paper trade** only strategies with ≥60% actual win rate
3. **Double position size** requirements (use 2-3% bankroll instead of 5%)
4. Track live performance closely for 60 days before scaling

"""
    else:
        report += """**❌ VALIDATION FAILED**

Majority of strategies did not meet profitability thresholds. Possible reasons:
1. Systematic bias exists but is smaller than claimed
2. Data quality issues (missing historical prices, incomplete markets)
3. Overfitting in original analysis
4. Market has adapted to these patterns

**Action Items:**
1. **DO NOT TRADE** these strategies with real money
2. Investigate data discrepancies
3. Re-analyze with different data sources
4. Consider alternative strategy approaches

"""
    
    # Top performers
    top_3 = sorted(results, key=lambda x: x['actual'], reverse=True)[:3]
    report += f"""### 🏆 Top 3 Performers (by Win Rate)

"""
    for i, r in enumerate(top_3, 1):
        report += f"{i}. **{r['strategy']}** - {r['actual']:.1f}% win rate ({r['total_trades']:,} trades, ${r['net_profit']:+,.0f} P/L)\n"
    
    # Worst performers
    bottom_3 = sorted(results, key=lambda x: x['actual'])[:3]
    report += f"""
### ⚠️ Bottom 3 Performers (by Win Rate)

"""
    for i, r in enumerate(bottom_3, 1):
        report += f"{i}. **{r['strategy']}** - {r['actual']:.1f}% win rate ({r['total_trades']:,} trades, ${r['net_profit']:+,.0f} P/L)\n"
    
    report += """
---

## 📝 IMPORTANT NOTES

### Limitations of This Backtest

1. **No Historical Prices:** Used simplified entry assumptions (60¢ NO price). Real entries vary.
2. **Slippage Estimate:** 1% is conservative; actual may be 0.5-2% depending on liquidity.
3. **Fee Structure:** Polymarket's actual fees may vary (market maker rebates, promotions).
4. **Survivorship Bias:** Dataset may exclude certain market types.
5. **Look-Ahead Bias:** Some strategies (CONSENSUS_FADE) require real-time price data we don't have.

### What This Backtest DOES Tell Us

✅ **Win rate accuracy** - Did YES or NO win?  
✅ **Sample size** - How often do these patterns appear?  
✅ **Relative performance** - Which strategies work best?  
✅ **Fee impact** - How much do costs eat into profits?

### What This Backtest DOESN'T Tell Us

❌ **Optimal entry timing** - When exactly to place bets  
❌ **Price evolution** - How markets moved over time  
❌ **Liquidity constraints** - Whether you can actually get filled  
❌ **Market adaptation** - How strategies perform going forward

---

## 🚀 NEXT STEPS

### Immediate Actions
1. Review detailed results for each strategy
2. Identify top 3-5 performers for paper trading
3. Build real-time market scanner for pattern detection
4. Set up tracking spreadsheet for live validation

### 30-Day Paper Trading Plan
1. **Week 1:** Track all 11 strategies, record every match
2. **Week 2:** Focus on top 5, refine entry criteria
3. **Week 3:** Test position sizing (1%, 2%, 3% of bankroll)
4. **Week 4:** Final validation, prepare for live trading

### Live Trading Checklist
- [ ] Validated win rate ≥60% in paper trading
- [ ] Sample size ≥30 paper trades
- [ ] Positive net P/L after estimated fees
- [ ] Clear entry/exit rules documented
- [ ] Position sizing strategy defined (recommend 2% max)
- [ ] Stop-loss rules in place (max 20% portfolio drawdown)

---

*Backtest completed by backtest_11_strategies.py*  
*Dataset: markets_snapshot_20260207_221914.json*  
*Analysis date: {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to {output_file}")

def main():
    print("="*100)
    print("BACKTEST VALIDATOR: ALL 11 STRATEGIES FROM NEW_STRATEGY_PROPOSALS.md")
    print("="*100)
    print(f"Fee Structure: {TRADING_FEE*100:.0f}% trading fee + {SLIPPAGE*100:.0f}% slippage = {TOTAL_COST*100:.0f}% total")
    print("="*100)
    
    # Load data
    markets, total_markets, closed_markets = load_markets('markets_snapshot_20260207_221914.json')
    
    # Filter to resolved markets only
    print("\nFiltering to resolved markets...")
    resolved_markets = [m for m in markets if is_resolved(m)]
    print(f"Resolved markets with clear outcomes: {len(resolved_markets):,}")
    
    # Backtest each strategy
    results = []
    for i, strategy_name in enumerate(STRATEGIES.keys(), 1):
        print(f"\n[{i}/11] Testing {strategy_name}...")
        result = backtest_strategy(resolved_markets, strategy_name, total_markets, closed_markets)
        results.append(result)
    
    # Generate report
    print("\n" + "="*100)
    print("GENERATING COMPREHENSIVE REPORT...")
    print("="*100)
    
    generate_report(results, 'BACKTEST_11_STRATEGIES.md')
    
    # Print summary
    print("\n" + "="*100)
    print("BACKTEST COMPLETE - SUMMARY")
    print("="*100)
    
    validated = sum(1 for r in results if r['status'] == 'VALIDATED')
    profitable = sum(1 for r in results if r['actual'] >= 55 and r['total_trades'] >= 20)
    total_trades = sum(r['total_trades'] for r in results)
    total_net_pl = sum(r['net_profit'] for r in results)
    
    print(f"\nValidated Strategies: {validated}/11")
    print(f"Profitable Strategies (>=55% WR): {profitable}/11")
    print(f"Total Trades Simulated: {total_trades:,}")
    print(f"Combined Net P/L: ${total_net_pl:+,.2f}")
    print(f"\nFull report: BACKTEST_11_STRATEGIES.md")
    
    # Print quick results table
    print("\n" + "="*100)
    print("QUICK RESULTS")
    print("="*100)
    print(f"{'Strategy':<30} {'Claimed':<10} {'Actual':<10} {'Diff':<10} {'Trades':<10} {'Status':<20}")
    print("-"*100)
    for r in sorted(results, key=lambda x: x['actual'], reverse=True):
        print(f"{r['strategy']:<30} {r['claimed']:>6.1f}%   {r['actual']:>6.1f}%   {r['difference']:>+6.1f}%   {r['total_trades']:>6,}    {r['status']:<20}")
    
    print("\n" + "="*100)
    print("BACKTEST COMPLETE")
    print("="*100)

if __name__ == "__main__":
    main()
