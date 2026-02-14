#!/usr/bin/env python3
"""
Polymarket Opportunity Scanner
Scans all markets for +EV trading opportunities
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re

# Constants
FEE_RATE = 0.02  # 2% Polymarket fee
MIN_VOLUME = 500000  # $500K minimum volume
TARGET_PRICE_LOW = (0.08, 0.20)  # 8-20%
TARGET_PRICE_HIGH = (0.80, 0.92)  # 80-92%
MAX_DAYS_TO_RESOLUTION = 90  # Prefer markets ending within 90 days

def parse_price(price_str: str) -> float:
    """Parse price string to float"""
    try:
        return float(price_str)
    except:
        return 0.0

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse ISO date string"""
    try:
        # Handle various date formats
        date_str = date_str.replace('Z', '+00:00')
        if '.' in date_str:
            date_str = date_str.split('.')[0] + '+00:00'
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        try:
            return datetime.strptime(date_str[:10], '%Y-%m-%d')
        except:
            return None

def days_to_resolution(end_date: datetime) -> int:
    """Calculate days until resolution"""
    now = datetime.now()
    if end_date.tzinfo:
        from datetime import timezone
        now = now.replace(tzinfo=timezone.utc)
    delta = end_date - now
    return max(0, delta.days)

def is_in_target_range(price: float) -> bool:
    """Check if price is in target range (avoiding slippage extremes)"""
    low_min, low_max = TARGET_PRICE_LOW
    high_min, high_max = TARGET_PRICE_HIGH
    return (low_min <= price <= low_max) or (high_min <= price <= high_max)

def calculate_slippage(spread: float, liquidity: float) -> float:
    """Estimate slippage based on spread and liquidity"""
    # Base slippage is half the spread
    base_slippage = spread / 2
    
    # Liquidity adjustment - lower liquidity = higher slippage
    if liquidity < 10000:
        liquidity_factor = 2.0
    elif liquidity < 50000:
        liquidity_factor = 1.5
    elif liquidity < 100000:
        liquidity_factor = 1.2
    else:
        liquidity_factor = 1.0
    
    return base_slippage * liquidity_factor

def calculate_ev(market: Dict) -> Dict[str, Any]:
    """Calculate expected value for a market"""
    outcomes = market.get('outcomes', '[]')
    prices_str = market.get('outcomePrices', '[]')
    
    # Parse outcomes and prices
    try:
        if isinstance(outcomes, str):
            outcomes = json.loads(outcomes)
        if isinstance(prices_str, str):
            prices = json.loads(prices_str)
        else:
            prices = prices_str
    except:
        return None
    
    if len(outcomes) != 2 or len(prices) != 2:
        return None  # Only binary markets
    
    yes_price = parse_price(prices[0])
    no_price = parse_price(prices[1])
    
    # Get market metrics
    volume = market.get('volumeNum', 0) or market.get('volume', 0)
    liquidity = market.get('liquidityNum', 0) or market.get('liquidity', 0)
    spread = market.get('spread', 0.01)
    
    # Calculate days to resolution
    end_date_str = market.get('endDate', '')
    end_date = parse_date(end_date_str)
    days = days_to_resolution(end_date) if end_date else 365
    
    # Skip if doesn't meet criteria
    if volume < MIN_VOLUME:
        return None
    
    if days > MAX_DAYS_TO_RESOLUTION * 2:  # Allow some flexibility
        return None
    
    # Check if either side is in target range
    yes_in_range = is_in_target_range(yes_price)
    no_in_range = is_in_target_range(no_price)
    
    if not yes_in_range and not no_in_range:
        return None
    
    # Calculate slippage
    slippage = calculate_slippage(spread, liquidity)
    
    # Determine which side to analyze
    if yes_in_range and yes_price <= 0.20:
        # Buying YES at low price (longshot)
        entry_price = yes_price + slippage
        potential_return = (1 - entry_price) / entry_price
        win_prob_implied = yes_price
        
        # For longshots, true prob often > implied (market overprices favorites)
        # Estimate edge: assume true prob is ~1.5x implied for 8-20% range
        true_prob_estimate = min(win_prob_implied * 1.5, 0.35)
        
        ev = (true_prob_estimate * (1 - entry_price) * (1 - FEE_RATE)) - ((1 - true_prob_estimate) * entry_price)
        
        side = "YES"
        price = yes_price
        
    elif yes_in_range and yes_price >= 0.80:
        # Buying YES at high price (favorite)
        entry_price = yes_price + slippage
        potential_return = (1 - entry_price) / entry_price
        win_prob_implied = yes_price
        
        # For favorites, true prob often > implied
        true_prob_estimate = min(win_prob_implied * 1.05, 0.98)
        
        ev = (true_prob_estimate * (1 - entry_price) * (1 - FEE_RATE)) - ((1 - true_prob_estimate) * entry_price)
        
        side = "YES"
        price = yes_price
        
    elif no_in_range and no_price <= 0.20:
        # Buying NO at low price
        entry_price = no_price + slippage
        potential_return = (1 - entry_price) / entry_price
        win_prob_implied = no_price
        
        true_prob_estimate = min(win_prob_implied * 1.5, 0.35)
        
        ev = (true_prob_estimate * (1 - entry_price) * (1 - FEE_RATE)) - ((1 - true_prob_estimate) * entry_price)
        
        side = "NO"
        price = no_price
        
    else:  # no_in_range and no_price >= 0.80
        # Buying NO at high price
        entry_price = no_price + slippage
        potential_return = (1 - entry_price) / entry_price
        win_prob_implied = no_price
        
        true_prob_estimate = min(win_prob_implied * 1.05, 0.98)
        
        ev = (true_prob_estimate * (1 - entry_price) * (1 - FEE_RATE)) - ((1 - true_prob_estimate) * entry_price)
        
        side = "NO"
        price = no_price
    
    # Calculate EV percentage
    ev_percent = (ev / entry_price) * 100 if entry_price > 0 else 0
    
    # Scoring
    volume_score = min(25, (volume / 1000000) * 10)  # 0-25 based on volume
    liquidity_score = min(20, (liquidity / 100000) * 10)  # 0-20 based on liquidity
    time_score = max(0, 25 - (days / 90) * 25) if days <= 90 else max(0, 25 - (days / 365) * 15)
    
    # Price range score - sweet spot is 10-15% or 85-90%
    if 0.10 <= price <= 0.15 or 0.85 <= price <= 0.90:
        price_score = 20
    elif 0.08 <= price <= 0.20 or 0.80 <= price <= 0.92:
        price_score = 15
    else:
        price_score = 10
    
    spread_score = max(0, 10 - (spread * 100))  # Tighter spread = higher score
    
    total_score = volume_score + liquidity_score + time_score + price_score + spread_score + (ev_percent if ev_percent > 0 else 0)
    
    return {
        'id': market.get('id'),
        'question': market.get('question'),
        'slug': market.get('slug'),
        'side': side,
        'price': price,
        'entry_price': entry_price,
        'volume': volume,
        'liquidity': liquidity,
        'spread': spread,
        'days_to_resolution': days,
        'ev': ev,
        'ev_percent': ev_percent,
        'potential_return': potential_return,
        'slippage': slippage,
        'score': total_score,
        'end_date': end_date_str,
        'description': market.get('description', '')[:200]
    }

def main():
    # Load markets
    with open('active-markets.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    markets = data.get('markets', [])
    print(f"Loaded {len(markets)} markets")
    
    # Calculate EV for all markets
    opportunities = []
    for market in markets:
        result = calculate_ev(market)
        if result and result['ev_percent'] > 5:  # >5% EV threshold
            opportunities.append(result)
    
    print(f"Found {len(opportunities)} opportunities with >5% EV")
    
    # Sort by multiple criteria: EV%, then score, then days to resolution
    opportunities.sort(key=lambda x: (-x['ev_percent'], -x['score'], x['days_to_resolution']))
    
    # Display top 10
    print("\n" + "="*80)
    print("TOP OPPORTUNITIES")
    print("="*80)
    
    for i, opp in enumerate(opportunities[:10], 1):
        print(f"\n#{i}: {opp['question']}")
        print(f"  Side: {opp['side']} @ {opp['price']:.2%} (entry: {opp['entry_price']:.2%})")
        print(f"  EV: {opp['ev_percent']:.1f}% | Score: {opp['score']:.0f}")
        print(f"  Volume: ${opp['volume']:,.0f} | Liquidity: ${opp['liquidity']:,.0f}")
        print(f"  Days to resolution: {opp['days_to_resolution']}")
        print(f"  Potential return: {opp['potential_return']:.1f}x")
        print(f"  Slippage estimate: {opp['slippage']:.2%}")
    
    # Save detailed results
    with open('scan-results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_markets': len(markets),
            'opportunities_found': len(opportunities),
            'top_opportunities': opportunities[:10]
        }, f, indent=2, default=str)
    
    print(f"\n\nResults saved to scan-results.json")
    
    return opportunities[:3]  # Return top 3

if __name__ == '__main__':
    top_3 = main()
