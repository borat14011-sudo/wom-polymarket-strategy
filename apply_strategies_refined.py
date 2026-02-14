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

def parse_prices(price_str: str) -> List[float]:
    """Parse price string that contains JSON array"""
    try:
        if isinstance(price_str, list):
            return [float(p) for p in price_str]
        elif price_str.startswith('[') and price_str.endswith(']'):
            prices_list = json.loads(price_str)
            return [float(p) for p in prices_list]
        else:
            parts = str(price_str).strip('[]').split(',')
            return [float(p.strip().strip('"')) for p in parts if p.strip()]
    except:
        return []

def calculate_ev(yes_price: float, strategy: str) -> float:
    """
    Calculate expected value for $1 bet
    More realistic EV calculation
    """
    if strategy == "buy_dip":
        # Buying YES when price < 0.30
        # Assume true probability is 2x market price (conservative)
        true_prob = min(yes_price * 2, 0.5)  # Cap at 50%
        if yes_price > 0:
            return (true_prob * (1 - yes_price) / yes_price) - (1 - true_prob)
        return 0
    
    elif strategy == "hype_fade":
        # Buying NO when YES price > 0.70
        # Assume true probability of NO is 40% (conservative)
        true_prob_no = 0.4
        no_price = 1 - yes_price
        if no_price > 0:
            return (true_prob_no * (1 / no_price)) - (1 - true_prob_no)
        return 0
    
    elif strategy == "near_certainty":
        # Buying YES when price 0.90-0.98
        # Assume true probability is 97%
        true_prob = 0.97
        if yes_price > 0:
            return (true_prob * (1 - yes_price) / yes_price) - (1 - true_prob)
        return 0
    
    return 0

def analyze_market(market: Dict) -> List[Dict]:
    """Analyze a single market for all 3 strategies with better filtering"""
    strategies = []
    
    # Get market details
    question = market.get('question', '')
    market_id = market.get('id', '')
    outcomes_str = market.get('outcomes', '[]')
    prices_str = market.get('outcomePrices', '[]')
    
    # Parse outcomes and prices
    try:
        outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
        prices = parse_prices(prices_str) if isinstance(prices_str, str) else prices_str
        
        if not isinstance(prices, list):
            prices = parse_prices(str(prices_str))
    except:
        return strategies
    
    if len(prices) < 2 or len(outcomes) < 2:
        return strategies
    
    # Get volume and liquidity
    volume = float(market.get('volume', 0))
    liquidity = float(market.get('liquidity', 0))
    
    # Determine YES price
    yes_price = prices[0] if outcomes[0] == 'Yes' else prices[1]
    no_price = prices[1] if outcomes[1] == 'No' else prices[0]
    
    # Check if it's a binary market (prices sum to ~1)
    if abs(yes_price + no_price - 1) > 0.05:
        return strategies
    
    # Skip extreme low probability events (<1%)
    if yes_price < 0.01:
        return strategies
    
    # Strategy 1: Buy the Dip (price 5c-30c)
    if 0.05 <= yes_price < 0.30:
        # Additional filter: volume > $10,000 for liquidity
        if volume > 10000:
            ev = calculate_ev(yes_price, "buy_dip")
            # Calculate score: lower price + higher volume = better
            price_score = (0.3 - yes_price) * 20  # 0 at 30c, 5 at 5c
            volume_score = min(math.log10(max(volume, 1)) - 3, 5)  # 0 at $1k, 5 at $100M
            score = price_score + volume_score
            
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
                'score': score
            })
    
    # Strategy 2: Hype Fade (price > 70c)
    if yes_price > 0.70:
        # Check for genuine hype
        question_lower = question.lower()
        hype_words = ['elon', 'musk', 'tesla', 'trump', 'biden', 'hype', 'rumor', 'spike', 'breakthrough']
        has_hype = any(word in question_lower for word in hype_words)
        
        # Also check for volume spike (would need historical data)
        if has_hype and volume > 50000:
            ev = calculate_ev(yes_price, "hype_fade")
            # Calculate score: higher price + higher volume = better fade opportunity
            price_score = (yes_price - 0.7) * 10  # 0 at 70c, 3 at 100c
            volume_score = min(math.log10(max(volume, 1)) - 3, 5)
            score = price_score + volume_score
            
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
                'score': score
            })
    
    # Strategy 3: Near Certainty (price 90-98c)
    if 0.90 <= yes_price <= 0.98:
        # Check for genuine high probability events
        question_lower = question.lower()
        certainty_words = ['incumbent', 'favorite', 'leading', 'ahead', 'likely', 'expected', 'probable']
        has_certainty = any(word in question_lower for word in certainty_words)
        
        # High volume indicates consensus
        if (has_certainty or volume > 100000) and volume > 50000:
            ev = calculate_ev(yes_price, "near_certainty")
            # Calculate score: higher price + higher volume = better
            price_score = (yes_price - 0.9) * 20  # 0 at 90c, 1.6 at 98c
            volume_score = min(math.log10(max(volume, 1)) - 3, 5)
            score = price_score + volume_score
            
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
                'score': score
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
    
    if not all_strategies:
        print("No strategy matches found with refined criteria.")
        return
    
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
        print(f"   Question: {strat['question'][:80]}...")
        print(f"   Market ID: {strat['market_id']}")
        print(f"   Prices: YES={strat['yes_price']:.3f}, NO={strat['no_price']:.3f}")
        print(f"   Action: {strat['action']}")
        print(f"   Expected Value: {strat['expected_value']:.3f}")
        print(f"   Edge: {strat['edge_percentage']:.1f}%")
        print(f"   Volume: ${strat['volume']:,.0f}")
        print(f"   Liquidity: ${strat['liquidity']:,.0f}")
    
    # Also show top 5 by expected value
    print("\n" + "="*100)
    print("TOP 5 BY EXPECTED VALUE")
    print("="*100)
    
    by_ev = sorted(all_strategies, key=lambda x: x['expected_value'], reverse=True)[:5]
    for i, strat in enumerate(by_ev, 1):
        print(f"\n{i}. {strat['strategy'].upper()} (EV: {strat['expected_value']:.3f})")
        print(f"   Question: {strat['question'][:60]}...")
        print(f"   Action: {strat['action']}")
        print(f"   Edge: {strat['edge_percentage']:.1f}%")
        print(f"   Volume: ${strat['volume']:,.0f}")
    
    # Save results
    results = {
        'analysis_date': datetime.now(timezone.utc).isoformat(),
        'total_markets_analyzed': len(markets),
        'total_strategy_matches': len(all_strategies),
        'strategy_breakdown': {k: len(v) for k, v in by_strategy.items()},
        'top_15_matches': top_15,
        'top_5_by_ev': by_ev
    }
    
    with open('strategy_applications_refined.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to strategy_applications_refined.json")

if __name__ == "__main__":
    main()