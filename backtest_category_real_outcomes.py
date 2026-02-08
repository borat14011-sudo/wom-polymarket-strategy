#!/usr/bin/env python3
"""
Real Category Backtest - Using Actual Resolved Market Outcomes
Validates the 93.5% politics / 87.5% crypto "strategy fit" claims
"""

import json
import csv
from collections import defaultdict
from typing import Dict, List, Tuple

# Strategy parameters
MIN_RVR = 2.5  # Minimum risk/reward ratio
MIN_ROC = 0.10  # Minimum return on capital (10%)

# Category keywords
CATEGORIES = {
    'POLITICS': [
        'election', 'senate', 'house', 'president', 'governor', 'congress',
        'democrat', 'republican', 'political', 'vote', 'poll', 'biden', 'trump'
    ],
    'CRYPTO': [
        'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
        'blockchain', 'token', 'defi', 'nft', 'solana', 'cardano'
    ],
    'SPORTS': [
        'nba', 'nfl', 'mlb', 'nhl', 'soccer', 'football', 'basketball',
        'baseball', 'hockey', 'champion', 'super bowl', 'world series',
        'finals', 'playoff', 'game', 'match', 'team', 'player'
    ],
    'AI/TECH': [
        'ai', 'artificial intelligence', 'gpt', 'chatgpt', 'openai',
        'tech', 'technology', 'software', 'apple', 'google', 'microsoft',
        'meta', 'amazon', 'tesla'
    ],
    'WORLD/EVENTS': [
        'war', 'ukraine', 'russia', 'china', 'nato', 'conflict',
        'pandemic', 'covid', 'climate', 'disaster', 'weather'
    ]
}

def categorize_market(question: str, description: str = "") -> str:
    """Categorize a market based on keywords"""
    text = f"{question} {description}".lower()
    
    category_scores = defaultdict(int)
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in text:
                category_scores[category] += 1
    
    if not category_scores:
        return 'OTHER'
    
    return max(category_scores.items(), key=lambda x: x[1])[0]

def calculate_entry_signal(price: float) -> Tuple[bool, float, float]:
    """
    Calculate if market meets entry criteria
    Returns: (qualifies, rvr, roc)
    """
    if price <= 0 or price >= 1:
        return False, 0, 0
    
    # Calculate potential return if we bet on this outcome
    rvr = (1 - price) / price
    roc = (1 - price) / price
    
    qualifies = rvr >= MIN_RVR and roc >= MIN_ROC
    return qualifies, rvr, roc

def analyze_market_trade(market: dict) -> dict:
    """
    Analyze if we would have entered this market and if we would have won
    """
    question = market.get('question', '')
    description = market.get('description', '')
    outcomes = market.get('outcomes', '').split('|')
    final_prices_str = market.get('final_prices', '')
    winner = market.get('winner', '')
    
    if not final_prices_str or not winner:
        return None
    
    # Parse final prices
    try:
        final_prices = [float(p) for p in final_prices_str.split('|')]
    except:
        return None
    
    if len(outcomes) != len(final_prices):
        return None
    
    category = categorize_market(question, description)
    
    # Simulate entry decision for each outcome
    trades = []
    for outcome, final_price in zip(outcomes, final_prices):
        # We'd look at the FINAL price (what the market settled at)
        # In reality we'd enter earlier, but this simulates "did this outcome have value?"
        qualifies, rvr, roc = calculate_entry_signal(final_price)
        
        if qualifies:
            won = (outcome == winner and final_price == 1.0) or (outcome != winner and final_price == 0.0)
            trades.append({
                'category': category,
                'market_id': market.get('market_id'),
                'question': question,
                'outcome': outcome,
                'final_price': final_price,
                'rvr': rvr,
                'roc': roc,
                'winner': winner,
                'won': won,
                'volume': float(market.get('volume_num', 0))
            })
    
    return trades

def main():
    print("Loading resolved markets data...")
    
    # Load resolved markets
    with open('polymarket_resolved_markets.json', 'r', encoding='utf-8') as f:
        markets = json.load(f)
    
    print(f"Loaded {len(markets)} resolved markets")
    
    # Analyze all markets
    all_trades = []
    for market in markets:
        trades = analyze_market_trade(market)
        if trades:
            all_trades.extend(trades)
    
    print(f"Found {len(all_trades)} qualifying trades across all markets")
    
    # Group by category
    category_stats = defaultdict(lambda: {
        'total_trades': 0,
        'winning_trades': 0,
        'total_volume': 0,
        'winning_volume': 0,
        'trades': []
    })
    
    for trade in all_trades:
        cat = trade['category']
        category_stats[cat]['total_trades'] += 1
        category_stats[cat]['total_volume'] += trade['volume']
        category_stats[cat]['trades'].append(trade)
        
        if trade['won']:
            category_stats[cat]['winning_trades'] += 1
            category_stats[cat]['winning_volume'] += trade['volume']
    
    # Calculate win rates
    results = []
    for category in sorted(category_stats.keys()):
        stats = category_stats[category]
        total = stats['total_trades']
        wins = stats['winning_trades']
        win_rate = (wins / total * 100) if total > 0 else 0
        
        results.append({
            'category': category,
            'total_trades': total,
            'winning_trades': wins,
            'losing_trades': total - wins,
            'win_rate': win_rate,
            'total_volume': stats['total_volume'],
            'avg_volume_per_trade': stats['total_volume'] / total if total > 0 else 0
        })
    
    # Sort by win rate
    results.sort(key=lambda x: x['win_rate'], reverse=True)
    
    # Print results
    print("\n" + "="*80)
    print("REAL CATEGORY BACKTEST RESULTS")
    print("="*80)
    print(f"\nStrategy: RVR >= {MIN_RVR}x, ROC >= {MIN_ROC*100}%")
    print(f"Data: {len(markets)} resolved Polymarket markets\n")
    
    print(f"{'Category':<20} {'Trades':<10} {'Wins':<10} {'Losses':<10} {'Win Rate':<15}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['category']:<20} "
              f"{result['total_trades']:<10} "
              f"{result['winning_trades']:<10} "
              f"{result['losing_trades']:<10} "
              f"{result['win_rate']:.1f}%")
    
    print("\n" + "="*80)
    print("VALIDATION OF CLAIMS")
    print("="*80)
    
    # Find politics and crypto results
    politics = next((r for r in results if r['category'] == 'POLITICS'), None)
    crypto = next((r for r in results if r['category'] == 'CRYPTO'), None)
    
    print(f"\nCLAIM: Politics = 93.5% 'strategy fit'")
    if politics:
        print(f"REALITY: Politics = {politics['win_rate']:.1f}% WIN RATE ({politics['winning_trades']}/{politics['total_trades']} trades)")
        print(f"NOTE: Original 93.5% was % of markets meeting ENTRY criteria, not win rate!")
    else:
        print("REALITY: No politics trades found")
    
    print(f"\nCLAIM: Crypto = 87.5% 'strategy fit'")
    if crypto:
        print(f"REALITY: Crypto = {crypto['win_rate']:.1f}% WIN RATE ({crypto['winning_trades']}/{crypto['total_trades']} trades)")
        print(f"NOTE: Original 87.5% was % of markets meeting ENTRY criteria, not win rate!")
    else:
        print("REALITY: No crypto trades found")
    
    print("\n" + "="*80)
    print("KEY INSIGHT")
    print("="*80)
    print("\nThe original analysis measured 'strategy fit' = % of markets meeting entry criteria")
    print("This analysis measures ACTUAL WIN RATE = % of qualifying trades that won")
    print("\nThese are VERY different metrics!")
    print("- Strategy fit: Can we enter this market? (yes/no)")
    print("- Win rate: Did we profit from this trade? (win/loss)")
    
    # Save detailed results
    output = {
        'summary': results,
        'all_trades': all_trades,
        'parameters': {
            'min_rvr': MIN_RVR,
            'min_roc': MIN_ROC,
            'total_markets': len(markets),
            'total_qualifying_trades': len(all_trades)
        }
    }
    
    with open('category_real_backtest_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nDetailed results saved to: category_real_backtest_results.json")
    
    return results

if __name__ == '__main__':
    main()
