import json
import sys
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
import math

def load_markets():
    """Load markets from latest data"""
    try:
        with open('polymarket_latest.json', 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        return data.get('markets', [])
    except Exception as e:
        print(f"Error loading markets: {e}")
        return []

def calculate_expected_value(yes_price: float, no_price: float, strategy: str) -> float:
    """
    Calculate expected value for a trade
    Assumes we bet $1 and outcomes are binary
    """
    if strategy == "buy_dip":
        # Buying YES when price < 0.30
        # Expected value = (probability_win * payout) - (probability_loss * cost)
        # If we buy YES at price p, we pay p, get $1 if YES wins
        # EV = (1-p)*1 - p*1 = 1 - 2p
        return 1 - 2*yes_price
    
    elif strategy == "hype_fade":
        # Buying NO when YES price > 0.70 (betting against hype)
        # If we buy NO at price (1-yes_price), we pay (1-yes_price), get $1 if NO wins
        # EV = yes_price*1 - (1-yes_price)*1 = 2*yes_price - 1
        return 2*yes_price - 1
    
    elif strategy == "near_certainty":
        # Buying YES when price 0.90-0.98 (high probability)
        # EV = (1-p)*1 - p*1 = 1 - 2p
        return 1 - 2*yes_price
    
    return 0

def analyze_market(market: Dict) -> List[Dict]:
    """Analyze a single market for all 3 strategies"""
    strategies = []
    
    # Get market details
    question = market.get('question', '')
    market_id = market.get('id', '')
    outcomes = market.get('outcomes', [])
    prices = market.get('outcomePrices', [])
    volume = market.get('volumeNum', 0)
    liquidity = market.get('liquidityNum', 0)
    
    if len(prices) < 2 or len(outcomes) < 2:
        return strategies
    
    # Parse prices
    try:
        yes_price = float(prices[0]) if outcomes[0] == 'Yes' else float(prices[1])
        no_price = float(prices[1]) if outcomes[1] == 'No' else float(prices[0])
    except (ValueError, IndexError):
        return strategies
    
    # Check if it's a binary market (prices sum to ~1)
    if abs(yes_price + no_price - 1) > 0.1:
        return strategies
    
    # Strategy 1: Buy the Dip (price < 30c)
    if yes_price < 0.30:
        ev = calculate_expected_value(yes_price, no_price, "buy_dip")
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
            'edge_percentage': (0.5 - yes_price) * 200  # Percentage edge
        })
    
    # Strategy 2: Hype Fade (price > 70c + hype indicators)
    if yes_price > 0.70:
        # Check for hype indicators
        hype_keywords = ['elon', 'musk', 'tesla', 'trump', 'biden', 'win', 'will', 'hype', 'news', 'rumor', 'spike']
        question_lower = question.lower()
        has_hype = any(keyword in question_lower for keyword in hype_keywords)
        
        # Also check volume spike (if we had historical data)
        if has_hype:
            ev = calculate_expected_value(yes_price, no_price, "hype_fade")
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
                'edge_percentage': (yes_price - 0.5) * 200  # Percentage edge
            })
    
    # Strategy 3: Near Certainty (price 90-98c + high probability)
    if 0.90 <= yes_price <= 0.98:
        # Check for high probability events
        high_prob_keywords = ['incumbent', 'favorite', 'leading', 'ahead', 'likely', 'expected', 'probable']
        question_lower = question.lower()
        has_high_prob = any(keyword in question_lower for keyword in high_prob_keywords)
        
        if has_high_prob or volume > 10000:  # High volume suggests consensus
            ev = calculate_expected_value(yes_price, no_price, "near_certainty")
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
                'edge_percentage': (0.5 - yes_price) * 200  # Negative edge means we're paying for certainty
            })
    
    return strategies

def main():
    print("Loading markets...")
    markets = load_markets()
    print(f"Total markets loaded: {len(markets)}")
    
    # Filter active markets
    active_markets = [m for m in markets if m.get('active', False)]
    print(f"Active markets: {len(active_markets)}")
    
    # Analyze all markets
    all_strategies = []
    for market in active_markets:
        strategies = analyze_market(market)
        all_strategies.extend(strategies)
    
    print(f"\nTotal strategy matches found: {len(all_strategies)}")
    
    # Group by strategy
    by_strategy = {}
    for s in all_strategies:
        strat = s['strategy']
        if strat not in by_strategy:
            by_strategy[strrat] = []
        by_strategy[strat].append(s)
    
    print("\nStrategy breakdown:")
    for strat, matches in by_strategy.items():
        print(f"  {strat}: {len(matches)} matches")
    
    # Sort by expected value (descending)
    all_strategies.sort(key=lambda x: x['expected_value'], reverse=True)
    
    # Take top 15
    top_15 = all_strategies[:15]
    
    print("\n" + "="*80)
    print("TOP 15 STRATEGY MATCHES (Ranked by Expected Value)")
    print("="*80)
    
    for i, strat in enumerate(top_15, 1):
        print(f"\n{i}. {strat['strategy'].upper()}")
        print(f"   Question: {strat['question'][:80]}...")
        print(f"   Market ID: {strat['market_id']}")
        print(f"   Prices: YES={strat['yes_price']:.3f}, NO={strat['no_price']:.3f}")
        print(f"   Action: {strat['action']}")
        print(f"   Expected Value: {strat['expected_value']:.3f} (Edge: {strat['edge_percentage']:.1f}%)")
        print(f"   Volume: ${strat['volume']:,.0f}, Liquidity: ${strat['liquidity']:,.0f}")
    
    # Save results
    with open('strategy_applications.json', 'w') as f:
        json.dump({
            'analysis_date': datetime.now(timezone.utc).isoformat(),
            'total_markets_analyzed': len(active_markets),
            'total_strategy_matches': len(all_strategies),
            'top_15_matches': top_15
        }, f, indent=2)
    
    print(f"\nResults saved to strategy_applications.json")

if __name__ == "__main__":
    main()