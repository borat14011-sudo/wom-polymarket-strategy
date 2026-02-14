#!/usr/bin/env python3
"""
Refined Polymarket Opportunity Analyzer
Focuses on realistic high-EV opportunities with proper risk assessment
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Constants - Realistic parameters
SLIPPAGE_FACTORS = {
    'tight_spread': 0.005,    # 0.5% - bid/ask within 1%
    'normal': 0.015,          # 1.5% - normal market
    'wide_spread': 0.03,      # 3% - wide spreads
}

POLYMARKET_FEE = 0.02  # 2% fee on winnings
WITHDRAWAL_FEE = 0.005  # 0.5% withdrawal

def parse_price(price_str):
    """Parse price string to float"""
    try:
        return float(price_str)
    except:
        return 0.0

def days_to_resolution(end_date_str: str) -> int:
    """Calculate days until market resolution"""
    try:
        end = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        now = datetime.now(end.tzinfo)
        return (end - now).days
    except:
        return 999

def estimate_slippage(market: Dict) -> float:
    """Estimate slippage based on spread and liquidity"""
    spread = market.get('spread', 0.01)
    liquidity = market.get('liquidityNum', 0)
    volume = market.get('volumeNum', 0)
    
    # Tight spread = low slippage
    if spread < 0.01 and liquidity > 20000:
        return SLIPPAGE_FACTORS['tight_spread']
    elif spread < 0.03 and liquidity > 5000:
        return SLIPPAGE_FACTORS['normal']
    else:
        return SLIPPAGE_FACTORS['wide_spread']

def calculate_expected_value(price: float, true_prob: float) -> float:
    """
    Calculate expected value percentage
    If we buy at 'price' and true probability is 'true_prob'
    """
    if price <= 0 or price >= 1:
        return 0
    
    # EV = (True Prob * (1 - Price) - (1 - True Prob) * Price) / Price
    # Simplified: (True Prob - Price) / Price
    edge = (true_prob - price) / price
    return edge * 100

def analyze_opportunity(market: Dict) -> Optional[Dict]:
    """Analyze a single market for opportunity"""
    
    # Basic filters
    volume = market.get('volumeNum', 0)
    if volume < 500000:  # $500K minimum
        return None
    
    days = days_to_resolution(market.get('endDate', ''))
    if days < 0:  # Already passed
        return None
    
    prices = json.loads(market['outcomePrices'])
    outcomes = json.loads(market['outcomes'])
    
    # Look for prices in target ranges
    opportunities = []
    
    for outcome, price_str in zip(outcomes, prices):
        price = parse_price(price_str)
        
        # Target range 1: 8-20% (undervalued longshots)
        # Target range 2: 80-92% (overvalued favorites to bet against)
        is_target = (0.08 <= price <= 0.20) or (0.80 <= price <= 0.92)
        
        if not is_target:
            continue
        
        slippage = estimate_slippage(market)
        
        # Estimate realistic execution price
        if price < 0.5:
            exec_price = min(price * (1 + slippage), 0.99)
        else:
            exec_price = max(price * (1 - slippage), 0.01)
        
        # For scoring, we need to estimate "edge"
        # This is where the thesis comes in - what's the true probability?
        # For now, we'll flag markets that meet criteria for manual review
        
        opportunities.append({
            'outcome': outcome,
            'price': price,
            'exec_price': exec_price,
            'slippage': slippage,
            'days': days,
            'volume': volume,
            'liquidity': market.get('liquidityNum', 0),
            'spread': market.get('spread', 0),
            'market_id': market['id'],
            'slug': market['slug'],
            'question': market['question'],
            'best_bid': market.get('bestBid'),
            'best_ask': market.get('bestAsk'),
            'volume_24h': market.get('volume24hr', 0),
            'description': market.get('description', '')[:200],
        })
    
    return opportunities[0] if opportunities else None

def score_opportunity(opp: Dict) -> int:
    """Score an opportunity on 0-100 scale"""
    score = 0
    
    # Volume score (0-25)
    vol = opp['volume']
    if vol > 5000000: score += 25
    elif vol > 2000000: score += 20
    elif vol > 1000000: score += 15
    elif vol > 500000: score += 10
    
    # Liquidity score (0-20)
    liq = opp['liquidity']
    if liq > 50000: score += 20
    elif liq > 20000: score += 15
    elif liq > 10000: score += 10
    elif liq > 5000: score += 5
    
    # Time score (0-25) - sooner is better for capital turnover
    days = opp['days']
    if days < 30: score += 25
    elif days < 60: score += 20
    elif days < 90: score += 15
    elif days < 180: score += 10
    else: score += 5
    
    # Price range score (0-20)
    price = opp['price']
    if 0.10 <= price <= 0.18 or 0.82 <= price <= 0.90:
        score += 20  # Sweet spot
    elif 0.08 <= price <= 0.20 or 0.80 <= price <= 0.92:
        score += 15  # Acceptable
    
    # Spread score (0-10)
    spread = opp['spread']
    if spread < 0.01: score += 10
    elif spread < 0.02: score += 7
    elif spread < 0.03: score += 5
    elif spread < 0.05: score += 3
    
    return score

def main():
    # Load data
    with open('active-markets.json', 'r') as f:
        data = json.load(f)
    
    print(f"Analyzing {len(data['markets'])} markets...")
    print(f"Timestamp: {data.get('fetch_timestamp', 'unknown')}\n")
    
    opportunities = []
    
    for market in data['markets']:
        opp = analyze_opportunity(market)
        if opp:
            opp['score'] = score_opportunity(opp)
            opportunities.append(opp)
    
    # Sort by score
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"Found {len(opportunities)} opportunities in target price ranges")
    print("="*80)
    
    # Display top 15
    for i, opp in enumerate(opportunities[:15], 1):
        print(f"\n{i}. Score: {opp['score']}/100")
        print(f"   {opp['question'][:70]}...")
        print(f"   Outcome: {opp['outcome']} @ {opp['price']:.2%}")
        print(f"   Exec: ~{opp['exec_price']:.2%} (slippage: {opp['slippage']:.1%})")
        print(f"   Vol: ${opp['volume']:,.0f} | Liq: ${opp['liquidity']:,.0f}")
        print(f"   Days: {opp['days']} | Spread: {opp['spread']:.2%}")
        print(f"   24h Vol: ${opp['volume_24h']:,.0f}")
    
    # Save detailed results
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_markets': len(data['markets']),
        'opportunities_found': len(opportunities),
        'top_opportunities': opportunities[:20]
    }
    
    with open('refined-opportunities.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n\nSaved to refined-opportunities.json")
    return opportunities

if __name__ == '__main__':
    main()
