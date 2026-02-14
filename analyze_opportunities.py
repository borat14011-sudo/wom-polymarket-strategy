#!/usr/bin/env python3
"""
Polymarket Opportunity Analyzer
Identifies high-EV trading opportunities based on slippage-aware analysis
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import math

# Constants
SLIPPAGE_RATES = {
    'low': 0.005,      # 0.5% for very liquid markets
    'medium': 0.015,   # 1.5% for normal markets
    'high': 0.03,      # 3% for illiquid markets
}

FEES = {
    'polymarket': 0.02,  # 2% on winnings
    'withdrawal': 0.005, # 0.5% withdrawal fee
}

MIN_VOLUME = 500000  # $500K minimum
PRICE_RANGES = [(0.08, 0.20), (0.80, 0.92)]  # Target price ranges
MAX_DAYS = 90  # Maximum days to resolution

def calculate_slippage(volume: float, liquidity: float, order_size: float = 1000) -> float:
    """Estimate slippage based on market liquidity"""
    if volume > 5000000 and liquidity > 50000:
        return SLIPPAGE_RATES['low']
    elif volume > 1000000 and liquidity > 10000:
        return SLIPPAGE_RATES['medium']
    else:
        return SLIPPAGE_RATES['high']

def calculate_ev(market: Dict, slippage: float) -> Dict[str, Any]:
    """
    Calculate expected value for a market after slippage and fees
    Returns EV analysis for both YES and NO outcomes
    """
    prices = json.loads(market['outcomePrices'])
    outcomes = json.loads(market['outcomes'])
    
    results = {}
    for i, (outcome, price_str) in enumerate(zip(outcomes, prices)):
        price = float(price_str)
        
        # Apply slippage to execution price
        if price < 0.5:
            # Buying YES - pay more
            execution_price = min(price * (1 + slippage), 0.99)
        else:
            # Buying NO - pay less
            execution_price = max(price * (1 - slippage), 0.01)
        
        # Calculate potential profit/loss
        if outcome == "Yes":
            potential_win = (1 - execution_price) * (1 - FEES['polymarket'])
            potential_loss = execution_price
        else:
            potential_win = (1 - execution_price) * (1 - FEES['polymarket'])
            potential_loss = execution_price
        
        # Simple Kelly-style edge calculation
        if price < 0.5:
            # Undervalued scenario
            edge = (1 - price) / price - 1 if price > 0 else 0
        else:
            # Overvalued scenario (betting against)
            edge = price / (1 - price) - 1 if price < 1 else 0
        
        # Apply total cost factor
        total_cost_factor = 1 + FEES['withdrawal']
        
        results[outcome] = {
            'market_price': price,
            'execution_price': execution_price,
            'potential_win': potential_win,
            'potential_loss': potential_loss,
            'edge': edge,
            'ev_percent': edge * 100 if edge > 0 else 0,
        }
    
    return results

def days_to_resolution(end_date: str) -> int:
    """Calculate days until market resolution"""
    try:
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        now = datetime.now().replace(tzinfo=end.tzinfo)
        return (end - now).days
    except:
        return 365  # Default to far future if parsing fails

def score_opportunity(market: Dict, ev_analysis: Dict) -> float:
    """
    Score an opportunity based on multiple factors
    Returns a score from 0-100
    """
    score = 0
    
    # Volume score (0-25 points)
    volume = market.get('volumeNum', 0)
    if volume > 5000000:
        score += 25
    elif volume > 2000000:
        score += 20
    elif volume > 1000000:
        score += 15
    elif volume > 500000:
        score += 10
    else:
        score += 5
    
    # Liquidity score (0-20 points)
    liquidity = market.get('liquidityNum', 0)
    if liquidity > 100000:
        score += 20
    elif liquidity > 50000:
        score += 15
    elif liquidity > 10000:
        score += 10
    else:
        score += 5
    
    # Time score - markets resolving sooner are better for capital turnover (0-25 points)
    days = days_to_resolution(market.get('endDate', ''))
    if days < 30:
        score += 25
    elif days < 60:
        score += 20
    elif days < 90:
        score += 15
    elif days < 180:
        score += 10
    else:
        score += 5
    
    # EV score (0-30 points)
    max_ev = max([v.get('ev_percent', 0) for v in ev_analysis.values()])
    if max_ev > 50:
        score += 30
    elif max_ev > 30:
        score += 25
    elif max_ev > 20:
        score += 20
    elif max_ev > 10:
        score += 15
    elif max_ev > 5:
        score += 10
    else:
        score += max_ev
    
    return score

def is_in_target_range(price: float) -> bool:
    """Check if price is in our target ranges (avoiding slippage extremes)"""
    for low, high in PRICE_RANGES:
        if low <= price <= high:
            return True
    return False

def analyze_markets(data: Dict) -> List[Dict]:
    """Analyze all markets and return sorted opportunities"""
    opportunities = []
    
    for market in data.get('markets', []):
        # Basic filters
        volume = market.get('volumeNum', 0)
        if volume < MIN_VOLUME:
            continue
        
        days = days_to_resolution(market.get('endDate', ''))
        if days > MAX_DAYS:
            continue
        
        # Check if any outcome is in target price range
        prices = json.loads(market['outcomePrices'])
        outcomes = json.loads(market['outcomes'])
        
        target_outcome = None
        for outcome, price_str in zip(outcomes, prices):
            price = float(price_str)
            if is_in_target_range(price):
                target_outcome = outcome
                target_price = price
                break
        
        if not target_outcome:
            continue
        
        # Calculate slippage and EV
        liquidity = market.get('liquidityNum', 0)
        slippage = calculate_slippage(volume, liquidity)
        ev_analysis = calculate_ev(market, slippage)
        
        # Check if any outcome has >5% EV
        has_positive_ev = any(
            v.get('ev_percent', 0) > 5 for v in ev_analysis.values()
        )
        
        if not has_positive_ev:
            continue
        
        # Score the opportunity
        score = score_opportunity(market, ev_analysis)
        
        opportunities.append({
            'market': market,
            'ev_analysis': ev_analysis,
            'score': score,
            'days_to_resolution': days,
            'target_outcome': target_outcome,
            'target_price': target_price,
            'slippage': slippage,
        })
    
    # Sort by score descending
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    return opportunities

def generate_thesis(opp: Dict) -> str:
    """Generate a trading thesis for an opportunity"""
    market = opp['market']
    ev = opp['ev_analysis']
    
    thesis = f"""
# {market['question'][:60]}...

**Market ID:** {market['id']} | **Slug:** {market['slug']}

## Key Metrics
- **Current Price:** {opp['target_outcome']} at {opp['target_price']:.2%}
- **Volume:** ${market['volumeNum']:,.0f}
- **Liquidity:** ${market['liquidityNum']:,.0f}
- **Days to Resolution:** {opp['days_to_resolution']}
- **Score:** {opp['score']}/100

## EV Analysis
"""
    for outcome, analysis in ev.items():
        thesis += f"""
### {outcome}
- Market Price: {analysis['market_price']:.4f}
- Est. Execution: {analysis['execution_price']:.4f}
- Potential Win: ${analysis['potential_win']:.2f} per $1
- Edge: {analysis['ev_percent']:.1f}%
"""
    
    thesis += f"""
## Thesis
[To be filled with detailed catalyst analysis]

## Risks
- Execution slippage estimated at {opp['slippage']:.1%}
- Resolution uncertainty
- Market volatility

## Recommended Action
[Buy/Sell recommendation with sizing]
"""
    
    return thesis

def main():
    # Load market data
    with open('active-markets.json', 'r') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data.get('markets', []))} markets")
    print(f"Timestamp: {data.get('fetch_timestamp', 'unknown')}")
    print("="*80)
    
    # Analyze markets
    opportunities = analyze_markets(data)
    
    print(f"\nFound {len(opportunities)} high-EV opportunities")
    print("="*80)
    
    # Print top 10
    print("\n## TOP 10 OPPORTUNITIES:\n")
    for i, opp in enumerate(opportunities[:10], 1):
        market = opp['market']
        print(f"{i}. Score {opp['score']}/100 | {market['question'][:50]}...")
        print(f"   Price: {opp['target_outcome']} @ {opp['target_price']:.2%} | "
              f"Vol: ${market['volumeNum']:,.0f} | "
              f"Days: {opp['days_to_resolution']}")
        best_ev = max([v.get('ev_percent', 0) for v in opp['ev_analysis'].values()])
        print(f"   Best Edge: {best_ev:.1f}% | Slippage: {opp['slippage']:.1%}")
        print()
    
    # Generate detailed theses for top 3
    top_3 = opportunities[:3]
    
    print("\n" + "="*80)
    print("## DETAILED THESES FOR TOP 3 OPPORTUNITIES")
    print("="*80)
    
    for i, opp in enumerate(top_3, 1):
        print(f"\n{'='*80}")
        print(f"## OPPORTUNITY #{i}")
        print(f"{'='*80}")
        print(generate_thesis(opp))
    
    # Save results
    results = {
        'analysis_timestamp': datetime.now().isoformat(),
        'total_markets': len(data.get('markets', [])),
        'opportunities_found': len(opportunities),
        'top_opportunities': [
            {
                'rank': i+1,
                'score': opp['score'],
                'market_id': opp['market']['id'],
                'question': opp['market']['question'],
                'slug': opp['market']['slug'],
                'target_outcome': opp['target_outcome'],
                'target_price': opp['target_price'],
                'volume': opp['market']['volumeNum'],
                'liquidity': opp['market']['liquidityNum'],
                'days_to_resolution': opp['days_to_resolution'],
                'ev_analysis': opp['ev_analysis'],
                'slippage': opp['slippage'],
            }
            for i, opp in enumerate(opportunities[:20])
        ]
    }
    
    with open('opportunity-analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nFull analysis saved to opportunity-analysis.json")
    
    return opportunities

if __name__ == '__main__':
    opportunities = main()
