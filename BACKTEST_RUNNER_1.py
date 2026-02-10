#!/usr/bin/env python3
"""
BACKTEST RUNNER 1 - Comprehensive Strategy Backtest
Tests ALL strategies against real historical resolved market data from RESOLVED_DATA_FIXED.json
"""

import json
import sys
from datetime import datetime
from collections import defaultdict

# Fee structure: 4% trading fee + 1% slippage = 5% total
TRADING_FEE = 0.04
SLIPPAGE = 0.01
TOTAL_COST = TRADING_FEE + SLIPPAGE

# ALL STRATEGIES TO TEST
STRATEGIES = {
    # === FADE STRATEGIES ===
    "MUSK_HYPE_FADE": {
        "claimed_winrate": 88.0,
        "description": "Bet NO on any Musk-related market",
        "condition": lambda m: any(kw in m['question'].lower() for kw in ["musk", "elon", "tesla"])
    },
    
    "TECH_HYPE_FADE": {
        "claimed_winrate": 78.2,
        "description": "Bet NO on tech company predictions",
        "condition": lambda m: any(kw in m['question'].lower() for kw in 
                                   ["apple", "google", "meta", "microsoft", "amazon", "nvidia", 
                                    "openai", "deepseek", "iphone", "android", "windows", "chatgpt", "gpt"])
    },
    
    "MICRO_MARKET_FADE": {
        "claimed_winrate": 77.2,
        "description": "Bet NO on markets with volume under $5,000",
        "condition": lambda m: m.get('volume_usd', 0) < 5000
    },
    
    "WILL_PREDICTION_FADE": {
        "claimed_winrate": 75.8,
        "description": "Bet NO on markets starting with 'Will'",
        "condition": lambda m: m['question'].strip().lower().startswith("will ")
    },
    
    "CONSENSUS_FADE": {
        "claimed_winrate": 75.1,
        "description": "Bet NO when high volume indicates consensus",
        "condition": lambda m: m.get('volume_usd', 0) > 50000
    },
    
    "CELEBRITY_FADE": {
        "claimed_winrate": 76.2,
        "description": "Bet NO on celebrity-related markets",
        "condition": lambda m: any(kw in m['question'].lower() for kw in 
                                   ["trump", "biden", "taylor swift", "kanye", "kardashian", 
                                    "oscar", "grammy", "emmy", "beyonce", "drake", "celebrity"])
    },
    
    "COMPLEX_QUESTION_FADE": {
        "claimed_winrate": 71.4,
        "description": "Bet NO on complex questions (>100 chars or contains 'and'/'or')",
        "condition": lambda m: len(m['question']) > 100 or ' and ' in m['question'].lower() or ' or ' in m['question'].lower()
    },
    
    "CRYPTO_HYPE_FADE": {
        "claimed_winrate": 66.0,
        "description": "Bet NO on crypto price predictions",
        "condition": lambda m: any(kw in m['question'].lower() for kw in 
                                   ["bitcoin", "btc", "ethereum", "eth", "crypto", "solana", "sol", 
                                    "xrp", "ripple", "doge", "cardano", "ada", "blockchain", "coinbase"])
    },
    
    # === ADDITIONAL STRATEGIES ===
    "POLITICAL_FADE": {
        "claimed_winrate": 72.0,
        "description": "Bet NO on political prediction markets",
        "condition": lambda m: any(kw in m['question'].lower() for kw in 
                                   ["election", "vote", "senate", "congress", "president", "democrat", "republican", "poll"])
    },
    
    "SPORTS_FADE": {
        "claimed_winrate": 68.0,
        "description": "Bet NO on sports outcome predictions",
        "condition": lambda m: any(kw in m['question'].lower() for kw in 
                                   ["super bowl", "nba", "nfl", "mlb", "championship", "win the", "defeat"])
    },
    
    "HIGH_VOLUME_FADE": {
        "claimed_winrate": 70.0,
        "description": "Bet NO on high volume markets (>$100K)",
        "condition": lambda m: m.get('volume_usd', 0) > 100000
    },
    
    "EXTREME_HIGH_FADE": {
        "claimed_winrate": 90.0,
        "description": "Bet NO when YES price >90% (extreme confidence)",
        "condition": lambda m: m.get('final_yes_price', 0) > 0.9
    },
    
    "EXTREME_LOW_FADE": {
        "claimed_winrate": 85.0,
        "description": "Bet YES when YES price <10% (extreme underdog)",
        "condition": lambda m: m.get('final_yes_price', 0) < 0.1,
        "side": "YES"
    },
    
    "FIFTY_FIFTY_FADE": {
        "claimed_winrate": 55.0,
        "description": "Bet NO on 40-60% probability markets (coin flip)",
        "condition": lambda m: 0.4 <= m.get('final_yes_price', 0.5) <= 0.6
    },
    
    "QUESTION_WORD_FADE": {
        "claimed_winrate": 73.0,
        "description": "Bet NO on questions with 'Can', 'Will', 'Does'",
        "condition": lambda m: any(m['question'].lower().startswith(w) for w in ["can ", "will ", "does ", "is ", "are "])
    },
    
    "LONG_QUESTION_FADE": {
        "claimed_winrate": 69.0,
        "description": "Bet NO on very long questions (>150 chars)",
        "condition": lambda m: len(m['question']) > 150
    },
    
    "US_MARKETS_FADE": {
        "claimed_winrate": 71.0,
        "description": "Bet NO on US-specific markets",
        "condition": lambda m: any(kw in m['question'].lower() for kw in 
                                   ["us ", "u.s.", "united states", "america", "american", "usa"])
    },
    
    "FAVORITE_WINS": {
        "claimed_winrate": 95.0,
        "description": "Bet on favorite (>50% initial price) - validates market efficiency",
        "condition": lambda m: m.get('initial_price', 0.5) > 0.5,
        "side": "FAVORITE"
    },
    
    "UNDERDOG_FADE": {
        "claimed_winrate": 60.0,
        "description": "Bet NO on underdog markets (<40% initial price)",
        "condition": lambda m: m.get('initial_price', 0.5) < 0.4
    },
}

def load_resolved_data(filepath):
    """Load RESOLVED_DATA_FIXED.json"""
    print(f"Loading resolved markets from {filepath}...")
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    markets = data.get('market_details', [])
    metadata = {
        'total_analyzed': data.get('total_markets_analyzed', 0),
        'date_range': data.get('date_range', {})
    }
    
    print(f"Total markets loaded: {len(markets):,}")
    print(f"From analysis of: {metadata['total_analyzed']:,} total markets")
    
    return markets

def simulate_trade(market, bet_side='NO'):
    """
    Simulate a trade with realistic fees
    Returns: (won, net_profit)
    """
    final_outcome = market.get('final_outcome', '')
    final_yes_price = market.get('final_yes_price', 0)
    final_no_price = market.get('final_no_price', 0)
    initial_price = market.get('initial_price', 0.5)
    
    # Determine if we won based on bet side
    if bet_side == 'NO':
        won = final_outcome == 'NO'
        entry_price = 1 - initial_price  # NO price is inverse of YES
    elif bet_side == 'YES':
        won = final_outcome == 'YES'
        entry_price = initial_price
    else:  # FAVORITE - bet on the side with >50% probability
        if initial_price > 0.5:
            won = final_outcome == 'YES'
            entry_price = initial_price
        else:
            won = final_outcome == 'NO'
            entry_price = 1 - initial_price
    
    # Profit calculation
    stake = 100.0
    
    if won:
        # Winner gets $100 / entry_price
        if entry_price > 0:
            gross_profit = stake / entry_price - stake
        else:
            gross_profit = 0  # Edge case: free money
        fees = stake * TOTAL_COST
        net_profit = gross_profit - fees
    else:
        gross_profit = -stake
        fees = stake * TRADING_FEE
        net_profit = -stake - fees
    
    return won, net_profit

def backtest_strategy(markets, strategy_name):
    """Backtest a single strategy against all resolved markets"""
    strategy = STRATEGIES[strategy_name]
    
    wins = 0
    losses = 0
    net_profit = 0
    matching_count = 0
    
    bet_side = strategy.get('side', 'NO')
    
    for market in markets:
        try:
            if strategy['condition'](market):
                matching_count += 1
                won, np = simulate_trade(market, bet_side)
                
                if won:
                    wins += 1
                else:
                    losses += 1
                
                net_profit += np
        except Exception as e:
            continue
    
    total_trades = wins + losses
    actual_winrate = (wins / total_trades * 100) if total_trades > 0 else 0
    claimed_winrate = strategy['claimed_winrate']
    difference = actual_winrate - claimed_winrate
    
    # Calculate ROI
    total_staked = total_trades * 100
    roi_pct = (net_profit / total_staked * 100) if total_staked > 0 else 0
    
    # Determine status
    if total_trades == 0:
        status = "NO DATA"
        status_emoji = "[--]"
    elif total_trades < 10:
        status = "INSUFFICIENT SAMPLE"
        status_emoji = "[LOW]"
    elif actual_winrate >= claimed_winrate * 0.95:
        status = "VALIDATED"
        status_emoji = "[OK]"
    elif actual_winrate >= 55:
        status = "PROFITABLE"
        status_emoji = "[WIN]"
    elif actual_winrate >= 50:
        status = "MARGINAL"
        status_emoji = "[MEH]"
    else:
        status = "FAILED"
        status_emoji = "[FAIL]"
    
    return {
        'strategy': strategy_name,
        'description': strategy['description'],
        'claimed': claimed_winrate,
        'actual': actual_winrate,
        'difference': difference,
        'wins': wins,
        'losses': losses,
        'total_trades': total_trades,
        'matching_count': matching_count,
        'net_profit': net_profit,
        'roi_pct': roi_pct,
        'status': status,
        'status_emoji': status_emoji
    }

def generate_report(results, output_file):
    """Generate comprehensive report"""
    
    validated = sum(1 for r in results if r['status'] == 'VALIDATED')
    profitable = sum(1 for r in results if r['actual'] >= 55 and r['total_trades'] >= 10)
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    total_trades = sum(r['total_trades'] for r in results)
    total_net_pl = sum(r['net_profit'] for r in results)
    
    report = f"""# BACKTEST RUNNER 1 - FINAL REPORT
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Dataset:** RESOLVED_DATA_FIXED.json (500 Real Resolved Markets)  
**Fee Structure:** {TRADING_FEE*100:.0f}% trading fee + {SLIPPAGE*100:.0f}% slippage  
**Position Size:** $100 per trade

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Total Strategies Tested** | {len(results)} |
| **Validated (>=95% of claim)** | {validated} |
| **Profitable (>=55% win rate)** | {profitable} |
| **Failed (<50% win rate)** | {failed} |
| **Total Trades Simulated** | {total_trades:,} |
| **Combined Net P/L** | ${total_net_pl:+,.2f} |

---

## SURVIVING STRATEGIES (Actual Win Rate >= 55%)

"""
    
    surviving = [r for r in results if r['actual'] >= 55 and r['total_trades'] >= 10]
    surviving.sort(key=lambda x: x['actual'], reverse=True)
    
    if surviving:
        for i, r in enumerate(surviving, 1):
            report += f"""### {i}. {r['strategy']} [{r['status_emoji']}]
- **Actual Win Rate:** {r['actual']:.1f}% (Claimed: {r['claimed']:.1f}%)
- **Trades:** {r['total_trades']:,} ({r['wins']:,}W / {r['losses']:,}L)
- **Net P/L:** ${r['net_profit']:+,.2f} (ROI: {r['roi_pct']:+.1f}%)
- **Description:** {r['description']}

"""
    else:
        report += "**No strategies survived the 55% win rate threshold.**\n\n"
    
    report += """---

## ALL RESULTS (Ranked by Actual Win Rate)

| Rank | Strategy | Claimed | Actual | Diff | Trades | Net P/L | Status |
|------|----------|---------|--------|------|--------|---------|--------|
"""
    
    sorted_results = sorted(results, key=lambda x: x['actual'], reverse=True)
    for i, r in enumerate(sorted_results, 1):
        report += f"| {i} | {r['strategy'][:25]} | {r['claimed']:.1f}% | {r['actual']:.1f}% | {r['difference']:+.1f}% | {r['total_trades']:,} | ${r['net_profit']:+.0f} | {r['status_emoji']} {r['status']} |\n"
    
    report += f"""
---

## FAILED STRATEGIES (< 50% Win Rate)

"""
    
    failed_strategies = [r for r in results if r['actual'] < 50 and r['total_trades'] >= 10]
    if failed_strategies:
        for r in failed_strategies:
            report += f"- **{r['strategy']}**: {r['actual']:.1f}% win rate ({r['total_trades']:,} trades)\n"
    else:
        report += "None - all strategies with sufficient sample size achieved >=50% win rate.\n"
    
    report += f"""
---

## DETAILED BREAKDOWN

"""
    
    for r in sorted_results:
        report += f"""### {r['strategy']} [{r['status_emoji']}]

**Description:** {r['description']}

**Performance:**
- Claimed Win Rate: {r['claimed']:.1f}%
- Actual Win Rate: {r['actual']:.1f}%
- Difference: {r['difference']:+.1f}%
- Sample Size: {r['total_trades']:,} trades ({r['wins']:,}W / {r['losses']:,}L)

**Financial:**
- Net P/L: ${r['net_profit']:+,.2f}
- ROI: {r['roi_pct']:+.2f}%

**Verdict:** {r['status']}

---

"""
    
    report += f"""## FINAL VERDICT

### Strategies That SURVIVED (>=55% win rate, >=10 trades):
"""
    
    if surviving:
        for r in surviving:
            report += f"- [OK] **{r['strategy']}** - {r['actual']:.1f}% win rate\n"
    else:
        report += "- [FAIL] No strategies met the survival criteria\n"
    
    report += f"""
### Key Findings:
1. **{validated}/{len(results)}** strategies performed within 5% of claimed win rates
2. **{profitable}/{len(results)}** strategies are profitable (>=55% win rate)
3. **{failed}/{len(results)}** strategies failed (<50% win rate)
4. Combined portfolio P/L across all strategies: ${total_net_pl:+,.2f}

### Recommendations:
"""
    
    if surviving:
        report += """- Focus on the top 3-5 validated strategies
- Start with small position sizing (1-2% of bankroll)
- Monitor for edge degradation over time
- Combine multiple strategies for diversification
"""
    else:
        report += """- No strategies passed validation in this dataset
- Consider refining strategy criteria
- Need larger sample size for statistical significance
- May require different market conditions
"""
    
    report += f"""
---
*Report generated by BACKTEST RUNNER 1*
*Real historical data from RESOLVED_DATA_FIXED.json (500 markets)*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {output_file}")

def main():
    print("="*100)
    print("BACKTEST RUNNER 1 - ALL STRATEGIES BACKTEST")
    print("="*100)
    print(f"Fee Structure: {TRADING_FEE*100:.0f}% trading fee + {SLIPPAGE*100:.0f}% slippage")
    print("="*100)
    
    # Load data
    markets = load_resolved_data('RESOLVED_DATA_FIXED.json')
    
    if not markets:
        print("ERROR: No markets loaded!")
        return
    
    print(f"\nTesting {len(STRATEGIES)} strategies against {len(markets)} resolved markets...")
    print("="*100)
    
    # Backtest each strategy
    results = []
    for i, strategy_name in enumerate(STRATEGIES.keys(), 1):
        print(f"\n[{i}/{len(STRATEGIES)}] Testing {strategy_name}...")
        result = backtest_strategy(markets, strategy_name)
        results.append(result)
        
        print(f"  Matching markets: {result['matching_count']:,}")
        print(f"  Resolved trades: {result['total_trades']:,}")
        print(f"  Win rate: {result['actual']:.1f}% (claimed: {result['claimed']:.1f}%)")
        print(f"  Net P/L: ${result['net_profit']:+.2f}")
        print(f"  Status: {result['status_emoji']} {result['status']}")
    
    # Generate report
    print("\n" + "="*100)
    print("GENERATING FINAL REPORT...")
    print("="*100)
    
    generate_report(results, 'BACKTEST_RUNNER_1_RESULTS.md')
    
    # Summary
    print("\n" + "="*100)
    print("FINAL SUMMARY")
    print("="*100)
    
    surviving = [r for r in results if r['actual'] >= 55 and r['total_trades'] >= 10]
    validated = sum(1 for r in results if r['status'] == 'VALIDATED')
    total_trades = sum(r['total_trades'] for r in results)
    
    print(f"\nTotal Strategies Tested: {len(results)}")
    print(f"Validated (within 5% of claim): {validated}")
    print(f"Surviving (>=55% win rate): {len(surviving)}")
    print(f"Total Trades Simulated: {total_trades:,}")
    print(f"Combined Net P/L: ${sum(r['net_profit'] for r in results):+,.2f}")
    
    print("\n" + "="*100)
    print("SURVIVING STRATEGIES (Actual Win Rate >= 55%):")
    print("="*100)
    
    if surviving:
        for r in surviving:
            print(f"[OK] {r['strategy']}: {r['actual']:.1f}% win rate ({r['total_trades']:,} trades)")
    else:
        print("[FAIL] No strategies met the survival threshold")
    
    print("\n" + "="*100)
    print("BACKTEST COMPLETE")
    print("="*100)
    print("\nFull report: BACKTEST_RUNNER_1_RESULTS.md")

if __name__ == "__main__":
    main()
