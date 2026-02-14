import json
import math
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

def load_markets():
    """Load markets from active-markets.json"""
    try:
        with open('active-markets.json', 'r', encoding='utf-8') as f:
            markets = json.load(f)
        return markets
    except Exception as e:
        print(f"Error loading markets: {e}")
        return []

def calculate_ev(yes_price: float, strategy: str) -> float:
    """
    Calculate expected value for $1 bet
    Simplified: EV = (probability_win * payout) - (probability_loss * cost)
    """
    if strategy == "buy_dip":
        # Buying YES when price < 0.30
        # Pay p to win $1, probability of winning = true_prob
        # Assuming true probability is higher than market price
        # Conservative estimate: true_prob = 0.5 (fair value)
        # EV = 0.5*(1-p)/p - 0.5
        if yes_price > 0:
            return (0.5 * (1 - yes_price) / yes_price) - 0.5
        return 0
    
    elif strategy == "hype_fade":
        # Buying NO when YES price > 0.70
        # Pay (1-p) to win $1 if NO wins
        # Assuming true probability of NO is higher than market price
        # Conservative: true_prob_NO = 0.5
        # EV = 0.5*(1/(1-p)) - 0.5
        no_price = 1 - yes_price
        if no_price > 0:
            return (0.5 * (1 / no_price)) - 0.5
        return 0
    
    elif strategy == "near_certainty":
        # Buying YES when price 0.90-0.98
        # High probability events, paying premium for certainty
        # If true probability is 0.95, EV = 0.95*(1-p)/p - 0.05
        true_prob = 0.95  # Conservative estimate for near-certain events
        if yes_price > 0:
            return (true_prob * (1 - yes_price) / yes_price) - (1 - true_prob)
        return 0
    
    return 0

def get_hype_score(question: str, volume: float) -> float:
    """Calculate hype score for a market"""
    question_lower = question.lower()
    
    hype_keywords = {
        'elon': 3.0, 'musk': 3.0, 'tesla': 2.5, 'trump': 2.5, 'biden': 2.0,
        'win': 1.5, 'will': 1.0, 'hype': 2.0, 'news': 1.5, 'rumor': 2.0,
        'spike': 2.0, 'breakthrough': 2.0, 'announcement': 1.5,
        'twitter': 2.0, 'x.com': 2.0, 'social media': 1.5
    }
    
    score = 0
    for keyword, weight in hype_keywords.items():
        if keyword in question_lower:
            score += weight
    
    # Volume bonus
    if volume > 100000:
        score += 2.0
    elif volume > 10000:
        score += 1.0
    
    return score

def get_certainty_score(question: str, volume: float, yes_price: float) -> float:
    """Calculate certainty score for near-certainty strategy"""
    question_lower = question.lower()
    
    certainty_keywords = {
        'incumbent': 3.0, 'favorite': 2.5, 'leading': 2.0, 'ahead': 2.0,
        'likely': 2.0, 'expected': 2.0, 'probable': 2.0, 'clear': 1.5,
        'obvious': 2.0, 'almost certain': 3.0, 'guaranteed': 3.0,
        'sure': 2.5, 'definite': 3.0
    }
    
    score = 0
    for keyword, weight in certainty_keywords.items():
        if keyword in question_lower:
            score += weight
    
    # Volume indicates consensus
    if volume > 50000:
        score += 2.0
    elif volume > 10000:
        score += 1.0
    
    # Price proximity to 1.0
    score += (yes_price - 0.9) * 10  # 0 at 0.9, 1 at 1.0
    
    return score

def analyze_market(market: Dict) -> List[Dict]:
    """Analyze a single market for all 3 strategies"""
    strategies = []
    
    # Get market details
    question = market.get('question', '')
    market_id = market.get('id', '')
    outcomes = market.get('outcomes', [])
    prices = market.get('outcomePrices', [])
    volume = float(market.get('volume', 0))
    liquidity = float(market.get('liquidity', 0))
    
    if len(prices) < 2 or len(outcomes) < 2:
        return strategies
    
    # Parse prices
    try:
        yes_price = float(prices[0]) if outcomes[0] == 'Yes' else float(prices[1])
        no_price = float(prices[1]) if outcomes[1] == 'No' else float(prices[0])
    except (ValueError, IndexError):
        return strategies
    
    # Check if it's a binary market (prices sum to ~1)
    if abs(yes_price + no_price - 1) > 0.05:
        return strategies
    
    # Strategy 1: Buy the Dip (price < 30c)
    if yes_price < 0.30:
        ev = calculate_ev(yes_price, "buy_dip")
        strategies.append({
            'market_id': market_id,
            'question': question,
            'strategy': 'buy_dip',
            'yes_price': yes_price,
            'no_price': no_price,
            'expected_value': ev,
            'volume': volume,
            'liquidity': liquidity,
            'action': f'BUY YES at {yes_price:.3f}',
            'edge_percentage': (0.5 - yes_price) * 200,
            'score': (0.3 - yes_price) * 10 + min(volume / 10000, 5)  # Lower price + higher volume = better
        })
    
    # Strategy 2: Hype Fade (price > 70c + hype indicators)
    if yes_price > 0.70:
        hype_score = get_hype_score(question, volume)
        if hype_score >= 2.0:  # Minimum hype threshold
            ev = calculate_ev(yes_price, "hype_fade")
            strategies.append({
                'market_id': market_id,
                'question': question,
                'strategy': 'hype_fade',
                'yes_price': yes_price,
                'no_price': no_price,
                'expected_value': ev,
                'volume': volume,
                'liquidity': liquidity,
                'action': f'BUY NO at {no_price:.3f}',
                'edge_percentage': (yes_price - 0.5) * 200,
                'hype_score': hype_score,
                'score': hype_score + (yes_price - 0.7) * 5 + min(volume / 10000, 5)
            })
    
    # Strategy 3: Near Certainty (price 90-98c + high probability)
    if 0.90 <= yes_price <= 0.98:
        certainty_score = get_certainty_score(question, volume, yes_price)
        if certainty_score >= 3.0:  # Minimum certainty threshold
            ev = calculate_ev(yes_price, "near_certainty")
            strategies.append({
                'market_id': market_id,
                'question': question,
                'strategy': 'near_certainty',
                'yes_price': yes_price,
                'no_price': no_price,
                'expected_value': ev,
                'volume': volume,
                'liquidity': liquidity,
                'action': f'BUY YES at {yes_price:.3f}',
                'edge_percentage': (0.5 - yes_price) * 200,
                'certainty_score': certainty_score,
                'score': certainty_score + min(volume / 50000, 5)
            })
    
    return strategies

def main():
    print("Loading markets...")
    markets = load_markets()
    print(f"Total markets loaded: {len(markets)}")
    
    # Analyze all markets
    all_strategies = []
    for i, market in enumerate(markets):
        strategies = analyze_market(market)
        all_strategies.extend(strategies)
        
        if i % 20 == 0 and i > 0:
            print(f"  Analyzed {i} markets...")
    
    print(f"\nTotal strategy matches found: {len(all_strategies)}")
    
    # Group by strategy
    by_strategy = {}
    for s in all_strategies:
        strat = s['strategy']
        if strat not in by_strategy:
            by_strategy[strat] = []
        by_strategy[strat].append(s)
    
    print("\nStrategy breakdown:")
    for strat, matches in by_strategy.items():
        avg_ev = sum(m['expected_value'] for m in matches) / len(matches) if matches else 0
        print(f"  {strat}: {len(matches)} matches (avg EV: {avg_ev:.3f})")
    
    # Sort by score (descending)
    all_strategies.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Take top 15
    top_15 = all_strategies[:15]
    
    print("\n" + "="*100)
    print("TOP 15 STRATEGY MATCHES (Ranked by Composite Score)")
    print("="*100)
    
    for i, strat in enumerate(top_15, 1):
        print(f"\n{i}. {strat['strategy'].upper()} (Score: {strat.get('score', 0):.1f})")
        print(f"   Question: {strat['question'][:100]}...")
        print(f"   Market ID: {strat['market_id']}")
        print(f"   Prices: YES={strat['yes_price']:.3f}, NO={strat['no_price']:.3f}")
        print(f"   Action: {strat['action']}")
        print(f"   Expected Value: {strat['expected_value']:.3f}")
        print(f"   Edge: {strat['edge_percentage']:.1f}%")
        print(f"   Volume: ${strat['volume']:,.0f}")
        
        if 'hype_score' in strat:
            print(f"   Hype Score: {strat['hype_score']:.1f}")
        if 'certainty_score' in strat:
            print(f"   Certainty Score: {strat['certainty_score']:.1f}")
    
    # Also show top 5 by expected value
    print("\n" + "="*100)
    print("TOP 5 BY EXPECTED VALUE")
    print("="*100)
    
    by_ev = sorted(all_strategies, key=lambda x: x['expected_value'], reverse=True)[:5]
    for i, strat in enumerate(by_ev, 1):
        print(f"\n{i}. {strat['strategy'].upper()} (EV: {strat['expected_value']:.3f})")
        print(f"   Question: {strat['question'][:80]}...")
        print(f"   Action: {strat['action']}")
        print(f"   Edge: {strat['edge_percentage']:.1f}%")
    
    # Save results
    results = {
        'analysis_date': datetime.now(timezone.utc).isoformat(),
        'total_markets_analyzed': len(markets),
        'total_strategy_matches': len(all_strategies),
        'strategy_breakdown': {k: len(v) for k, v in by_strategy.items()},
        'top_15_matches': top_15,
        'top_5_by_ev': by_ev
    }
    
    with open('strategy_applications_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to strategy_applications_results.json")
    
    # Generate summary report
    with open('strategy_applications_summary.md', 'w') as f:
        f.write(f"# Strategy Application Results\n")
        f.write(f"**Analysis Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n")
        f.write(f"**Markets Analyzed:** {len(markets)}\n")
        f.write(f"**Strategy Matches Found:** {len(all_strategies)}\n\n")
        
        f.write("## Strategy Breakdown\n")
        for strat, matches in by_strategy.items():
            avg_ev = sum(m['expected_value'] for m in matches) / len(matches) if matches else 0
            f.write(f"- **{strat}:** {len(matches)} matches (Average EV: {avg_ev:.3f})\n")
        
        f.write("\n## Top 15 Opportunities\n")
        f.write("| Rank | Strategy | Question | Price | Action | EV | Edge |\n")
        f.write("|------|----------|----------|-------|--------|----|------|\n")
        
        for i, strat in enumerate(top_15, 1):
            question_short = strat['question'][:60].replace('|', '') + '...'
            f.write(f"| {i} | {strat['strategy']} | {question_short} | {strat['yes_price']:.3f} | {strat['action']} | {strat['expected_value']:.3f} | {strat['edge_percentage']:.1f}% |\n")
    
    print(f"Summary report saved to strategy_applications_summary.md")

if __name__ == "__main__":
    main()