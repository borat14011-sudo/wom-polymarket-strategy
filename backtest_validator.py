#!/usr/bin/env python3
"""
BACKTEST VALIDATOR - Validate 5 strategies on resolved markets
Tests strategies from MEMORY.md against real market outcomes
"""

import json
import sys
from datetime import datetime
from collections import defaultdict

# Strategy definitions from MEMORY.md
STRATEGIES = {
    "MUSK_FADE_EXTREMES": {
        "expected_winrate": 97.1,
        "description": "Bet NO on Elon Musk tweet count extremes (0-19 OR 200+)",
        "keywords": ["musk", "elon", "tweet", "twitter", "x.com"],
        "condition": lambda m: ("tweet" in m['question'].lower() and 
                                 any(extreme in m['question'].lower() for extreme in 
                                     ['0-19', '200+', '0-10', '250+', 'less than 20', 'more than 200']))
    },
    
    "WEATHER_FADE_LONGSHOTS": {
        "expected_winrate": 93.9,
        "description": "Bet NO on weather predictions with <30% probability",
        "keywords": ["temperature", "weather", "degrees", "celsius", "fahrenheit", "rain", "snow"],
        "condition": lambda m: any(w in m['question'].lower() for w in 
                                   ['temperature', 'weather', 'degrees', 'rain', 'snow', 'celsius', 'fahrenheit'])
    },
    
    "ALTCOIN_FADE_HIGH": {
        "expected_winrate": 92.3,
        "description": "Bet NO when altcoin reach $X markets hit >70%",
        "keywords": ["eth", "ethereum", "sol", "solana", "xrp", "ada", "doge", "altcoin", "reach"],
        "condition": lambda m: (any(coin in m['question'].lower() for coin in 
                                    ['eth', 'ethereum', 'sol', 'solana', 'xrp', 'cardano', 'doge']) and
                                'reach' in m['question'].lower())
    },
    
    "CRYPTO_FAVORITE_FADE": {
        "expected_winrate": 61.9,
        "description": "Bet NO on BTC directional predictions",
        "keywords": ["bitcoin", "btc"],
        "condition": lambda m: any(w in m['question'].lower() for w in ['bitcoin', 'btc']) and 
                                any(d in m['question'].lower() for d in ['above', 'below', 'reach', 'hit'])
    },
    
    "BTC_TIME_BIAS": {
        "expected_winrate": 58.9,
        "description": "Bitcoin time-of-day directional betting",
        "keywords": ["bitcoin", "btc"],
        "condition": lambda m: any(w in m['question'].lower() for w in ['bitcoin', 'btc'])
    }
}

def load_markets(filepath):
    """Load market snapshot"""
    print(f"Loading markets from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total = data['summary']['total_markets']
    closed = data['summary']['closed_markets']
    print(f"Total markets: {total:,}")
    print(f"Closed markets: {closed:,}")
    
    return data['markets']

def is_resolved(market):
    """Check if market is resolved with outcome"""
    if not market.get('closed'):
        return False
    
    # Check if we have outcome_prices that indicate resolution
    outcome_prices = market.get('outcome_prices')
    if outcome_prices and len(outcome_prices) == 2:
        # If one price is 1 and other is 0, it's resolved
        return (outcome_prices[0] in [0, 1] and outcome_prices[1] in [0, 1] and
                outcome_prices[0] != outcome_prices[1])
    
    return False

def matches_strategy(market, strategy_name):
    """Check if market matches strategy criteria"""
    strategy = STRATEGIES[strategy_name]
    question = market.get('question', '').lower()
    
    # Check keywords first
    if not any(kw in question for kw in strategy['keywords']):
        return False
    
    # Apply specific condition
    try:
        m = {'question': market.get('question', '')}
        return strategy['condition'](m)
    except:
        return False

def simulate_trade(market, bet_side='NO'):
    """
    Simulate betting NO on a market
    Returns: (won, profit, market_info)
    """
    outcome_prices = market.get('outcome_prices', [])
    
    if len(outcome_prices) != 2:
        return False, 0, None
    
    # outcome_prices: [Yes_price, No_price]
    # If [1, 0] = Yes won, if [0, 1] = No won
    yes_won = outcome_prices[0] == 1
    no_won = outcome_prices[1] == 1
    
    # Determine if our bet won
    if bet_side == 'NO':
        won = no_won
        outcome_str = "No" if no_won else "Yes"
    else:
        won = yes_won
        outcome_str = "Yes" if yes_won else "No"
    
    # Simple profit calculation (assuming equal stakes)
    # In reality we'd need historical prices, but for win rate we just need win/loss
    profit = 1.0 if won else -1.0
    
    return won, profit, {
        'id': market.get('id'),
        'question': market.get('question', '')[:100],
        'outcome': outcome_str,
        'won': won
    }

def backtest_strategy(markets, strategy_name):
    """Backtest a single strategy"""
    print(f"\n{'='*80}")
    print(f"BACKTESTING: {strategy_name}")
    print(f"Expected Win Rate: {STRATEGIES[strategy_name]['expected_winrate']:.1f}%")
    print(f"{'='*80}")
    
    matching_markets = []
    wins = 0
    losses = 0
    total_profit = 0
    sample_trades = []
    
    for market in markets:
        if not is_resolved(market):
            continue
            
        if matches_strategy(market, strategy_name):
            won, profit, trade_info = simulate_trade(market, 'NO')
            matching_markets.append(market)
            
            if won:
                wins += 1
            else:
                losses += 1
            
            total_profit += profit
            
            # Save sample trades (first 3 wins, first 3 losses)
            if (won and len([t for t in sample_trades if t['won']]) < 3) or \
               (not won and len([t for t in sample_trades if not t['won']]) < 3):
                sample_trades.append(trade_info)
    
    total_trades = wins + losses
    actual_winrate = (wins / total_trades * 100) if total_trades > 0 else 0
    expected_winrate = STRATEGIES[strategy_name]['expected_winrate']
    difference = actual_winrate - expected_winrate
    
    # Determine status
    if total_trades == 0:
        status = "NO DATA"
    elif abs(difference) < 5:
        status = "VALIDATED"
    elif actual_winrate > 55:
        status = "PROFITABLE"
    else:
        status = "FAILED"
    
    result = {
        'strategy': strategy_name,
        'expected': expected_winrate,
        'actual': actual_winrate,
        'difference': difference,
        'status': status,
        'total_trades': total_trades,
        'wins': wins,
        'losses': losses,
        'total_profit': total_profit,
        'sample_trades': sample_trades
    }
    
    print(f"\nTotal Matching Markets: {total_trades}")
    print(f"Wins: {wins} | Losses: {losses}")
    print(f"Actual Win Rate: {actual_winrate:.1f}%")
    print(f"Expected Win Rate: {expected_winrate:.1f}%")
    print(f"Difference: {difference:+.1f}%")
    print(f"Status: {status}")
    
    return result

def generate_report(results, output_file):
    """Generate markdown report"""
    
    report = f"""# BACKTEST VALIDATION RESULTS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

Validated 5 trading strategies against {results[0].get('total_markets_scanned', 0):,} resolved Polymarket markets.

## Results Table

| Strategy | Expected | Actual | Difference | Trades | Status |
|----------|----------|--------|------------|--------|--------|
"""
    
    for r in results:
        report += f"| {r['strategy']} | {r['expected']:.1f}% | {r['actual']:.1f}% | {r['difference']:+.1f}% | {r['total_trades']} | {r['status']} |\n"
    
    report += "\n## Detailed Results\n\n"
    
    for r in results:
        report += f"""### {r['strategy']}

**Description:** {STRATEGIES[r['strategy']]['description']}

**Performance:**
- Expected Win Rate: {r['expected']:.1f}%
- Actual Win Rate: {r['actual']:.1f}%
- Difference: {r['difference']:+.1f}%
- Total Trades: {r['total_trades']}
- Wins: {r['wins']} | Losses: {r['losses']}
- Total P/L: ${r['total_profit']:+.2f}
- **Status: {r['status']}**

**Sample Trades:**
"""
        
        if r['sample_trades']:
            for i, trade in enumerate(r['sample_trades'][:6], 1):
                result_str = "WIN" if trade['won'] else "LOSS"
                report += f"{i}. [{result_str}] {trade['question'][:80]}... (Outcome: {trade['outcome']})\n"
        else:
            report += "No trades found.\n"
        
        report += "\n---\n\n"
    
    # Overall recommendation
    validated = sum(1 for r in results if "VALIDATED" in r['status'])
    profitable = sum(1 for r in results if r['actual'] > 55)
    
    report += f"""## Overall Recommendation

- **Validated Strategies:** {validated}/5
- **Profitable Strategies (>55% win rate):** {profitable}/5

"""
    
    if validated >= 3:
        report += "**RECOMMENDATION: VALIDATED** - Majority of strategies performed as expected.\n\n"
    elif profitable >= 3:
        report += "**RECOMMENDATION: NEEDS TUNING** - Strategies are profitable but differ from expectations.\n\n"
    else:
        report += "**RECOMMENDATION: FAILED** - Strategies did not validate on historical data.\n\n"
    
    report += """## Important Notes

1. **Data Limitations:** Backtests use resolved markets but lack historical price data for precise entry timing
2. **Transaction Costs:** Not modeled in this validation (typically 2-5%)
3. **Sample Size:** Some strategies have limited matching markets
4. **Forward Testing:** Real-world results may vary - paper trading recommended

## Next Steps

1. For validated strategies: Begin paper trading with real-time data
2. For failed strategies: Refine criteria or abandon
3. Build historical price database for more accurate backtesting
4. Monitor win rates in live trading and adjust

---
*Generated by backtest_validator.py*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[OK] Report saved to {output_file}")

def main():
    print("BACKTEST VALIDATOR - Strategy Validation System")
    print("=" * 80)
    
    # Load data
    markets = load_markets('markets_snapshot_20260207_221914.json')
    
    # Filter to resolved markets only
    resolved_markets = [m for m in markets if is_resolved(m)]
    print(f"\nResolved markets with outcomes: {len(resolved_markets):,}")
    
    # Backtest each strategy
    results = []
    for strategy_name in STRATEGIES.keys():
        result = backtest_strategy(resolved_markets, strategy_name)
        result['total_markets_scanned'] = len(resolved_markets)
        results.append(result)
    
    # Generate report
    print("\n" + "=" * 80)
    print("GENERATING REPORT...")
    print("=" * 80)
    
    generate_report(results, 'BACKTEST_VALIDATION_RESULTS.md')
    
    # Print summary
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print("\nQuick Summary:")
    for r in results:
        print(f"  {r['strategy']}: {r['actual']:.1f}% win rate ({r['total_trades']} trades) - {r['status']}")

if __name__ == "__main__":
    main()
