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
        # Remove brackets and quotes, split by comma
        if price_str.startswith('[') and price_str.endswith(']'):
            # It's a JSON array string
            prices_list = json.loads(price_str)
            return [float(p) for p in prices_list]
        else:
            # Try to parse as comma-separated
            parts = price_str.strip('[]').split(',')
            return [float(p.strip().strip('"')) for p in parts if p.strip()]
    except:
        return []

def calculate_ev(yes_price: float, strategy: str) -> float:
    """
    Calculate expected value for $1 bet
    """
    if strategy == "buy_dip":
        # Buying YES when price < 0.30
        # Simple EV calculation: (1 - yes_price) / yes_price - 1
        if yes_price > 0:
            return (1 - yes_price) / yes_price - 1
        return 0
    
    elif strategy == "hype_fade":
        # Buying NO when YES price > 0.70
        no_price = 1 - yes_price
        if no_price > 0:
            return yes_price / no_price - 1
        return 0
    
    elif strategy == "near_certainty":
        # Buying YES when price 0.90-0.98
        # Assuming 95% true probability
        true_prob = 0.95
        if yes_price > 0:
            return (true_prob * (1 - yes_price) / yes_price) - (1 - true_prob)
        return 0
    
    return 0

def analyze_market(market: Dict) -> List[Dict]:
    """Analyze a single market for all 3 strategies"""
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
            'score': (0.3 - yes_price) * 10 + min(volume / 10000, 5)
        })
    
    # Strategy 2: Hype Fade (price > 70c)
    if yes_price > 0.70:
        # Simple hype check
        question_lower = question.lower()
        hype_words = ['elon', 'musk', 'tesla', 'trump', 'biden', 'win', 'hype', 'news', 'rumor', 'spike']
        has_hype = any(word in question_lower for word in hype_words)
        
        if has_hype or volume > 50000:  # High volume can indicate hype
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
                'score': (yes_price - 0.7) * 5 + min(volume / 10000, 5)
            })
    
    # Strategy 3: Near Certainty (price 90-98c)
    if 0.90 <= yes_price <= 0.98:
        # Check for high probability indicators
        question_lower = question.lower()
        certainty_words = ['incumbent', 'favorite', 'leading', 'ahead', 'likely', 'expected']
        has_certainty = any(word in question_lower for word in certainty_words)
        
        if has_certainty or volume > 100000:  # High volume indicates consensus
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
                'score': (yes_price - 0.9) * 10 + min(volume / 50000, 5)
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
        print("\nNo strategy matches found. Checking price distribution...")
        price_counts = {'<0.3': 0, '0.3-0.7': 0, '>0.7': 0, '0.9-0.98': 0}
        
        for market in markets:
            outcomes_str = market.get('outcomes', '[]')
            prices_str = market.get('outcomePrices', '[]')
            
            try:
                outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
                prices = parse_prices(prices_str) if isinstance(prices_str, str) else prices_str
                
                if len(prices) >= 2 and len(outcomes) >= 2:
                    yes_price = prices[0] if outcomes[0] == 'Yes' else prices[1]
                    
                    if yes_price < 0.3:
                        price_counts['<0.3'] += 1
                    elif yes_price < 0.7:
                        price_counts['0.3-0.7'] += 1
                    elif yes_price < 0.9:
                        price_counts['>0.7'] += 1
                    elif yes_price <= 0.98:
                        price_counts['0.9-0.98'] += 1
            except:
                continue
        
        print("\nPrice distribution of binary markets:")
        for range_name, count in price_counts.items():
            print(f"  {range_name}: {count}")
        
        # Show examples
        print("\nExamples of markets in each range:")
        for market in markets[:10]:
            question = market.get('question', '')[:60]
            outcomes_str = market.get('outcomes', '[]')
            prices_str = market.get('outcomePrices', '[]')
            
            try:
                outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
                prices = parse_prices(prices_str) if isinstance(prices_str, str) else prices_str
                
                if len(prices) >= 2 and len(outcomes) >= 2:
                    yes_price = prices[0] if outcomes[0] == 'Yes' else prices[1]
                    print(f"  {yes_price:.3f}: {question}...")
            except:
                continue
        
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
        print(f"   Question: {strat['question'][:100]}...")
        print(f"   Market ID: {strat['market_id']}")
        print(f"   Prices: YES={strat['yes_price']:.3f}, NO={strat['no_price']:.3f}")
        print(f"   Action: {strat['action']}")
        print(f"   Expected Value: {strat['expected_value']:.3f}")
        print(f"   Edge: {strat['edge_percentage']:.1f}%")
        print(f"   Volume: ${strat['volume']:,.0f}")
    
    # Save results
    results = {
        'analysis_date': datetime.now(timezone.utc).isoformat(),
        'total_markets_analyzed': len(markets),
        'total_strategy_matches': len(all_strategies),
        'strategy_breakdown': {k: len(v) for k, v in by_strategy.items()},
        'top_15_matches': top_15
    }
    
    with open('strategy_applications_final.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to strategy_applications_final.json")

if __name__ == "__main__":
    main()