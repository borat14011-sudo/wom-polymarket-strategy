#!/usr/bin/env python3
"""
Time-to-Resolution Filter Implementation
Add this to your existing trading system to filter markets by resolution timeframe

Based on backtest findings:
- <3 days: 66.7% win rate, +$4.17 expectancy
- 3-7 days: 50.0% win rate, +$0.83 expectancy  
- >7 days: AVOID (negative expectancy)
"""

import requests
from datetime import datetime, timedelta
from typing import Tuple, Optional

GAMMA_API = "https://gamma-api.polymarket.com"


def get_market_end_date(market_id: str) -> Optional[datetime]:
    """
    Fetch market endDate from Gamma API
    
    Args:
        market_id: Polymarket market ID
    
    Returns:
        datetime object of market end date, or None if error
    """
    try:
        url = f"{GAMMA_API}/markets/{market_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Try to get endDate from various possible fields
            end_date_str = data.get('endDate') or data.get('end_date') or data.get('closesAt')
            
            if end_date_str:
                # Parse ISO format timestamp
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                return end_date
            else:
                print(f"Warning: No endDate found for market {market_id}")
                return None
        else:
            print(f"Error fetching market {market_id}: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None


def calculate_days_to_resolution(market_id: str) -> Optional[float]:
    """
    Calculate days from now until market resolution
    
    Args:
        market_id: Polymarket market ID
    
    Returns:
        Days to resolution as float, or None if error
    """
    end_date = get_market_end_date(market_id)
    
    if end_date is None:
        return None
    
    now = datetime.now(end_date.tzinfo)  # Match timezone
    delta = end_date - now
    days = delta.total_seconds() / (24 * 3600)
    
    return max(0, days)  # Don't return negative days


def should_trade_market(market_id: str, min_confidence: float = 0.0) -> Tuple[bool, float, str]:
    """
    Determine if market should be traded based on time-to-resolution
    
    Args:
        market_id: Polymarket market ID
        min_confidence: Minimum signal confidence to consider
    
    Returns:
        (should_trade, position_size_multiplier, reason)
        
    Examples:
        (True, 1.0, "High priority: <3 days")
        (True, 0.5, "Selective: 3-7 days")
        (False, 0.0, "Avoid: >7 days")
    """
    days = calculate_days_to_resolution(market_id)
    
    if days is None:
        return False, 0.0, "Error: Could not fetch market data"
    
    # Apply time-based filter based on backtest results
    if days < 3:
        # High priority: 66.7% win rate, $4.17 expectancy
        return True, 1.0, f"✅ HIGH PRIORITY: {days:.1f} days (66.7% win rate)"
    
    elif days < 7:
        # Selective: 50% win rate, $0.83 expectancy
        # Only trade if confidence is higher
        if min_confidence >= 70:  # Require higher confidence
            return True, 0.5, f"⚠️ SELECTIVE: {days:.1f} days (50% win rate, reduced size)"
        else:
            return False, 0.0, f"⚠️ SKIP: {days:.1f} days (need 70+ confidence for medium-term)"
    
    elif days < 30:
        # Avoid: 33.3% win rate, -$2.42 expectancy
        return False, 0.0, f"❌ AVOID: {days:.1f} days (negative expectancy)"
    
    else:
        # Definitely avoid: 16.7% win rate, -$8.58 expectancy
        return False, 0.0, f"🚫 NEVER TRADE: {days:.1f} days (83% reversal rate)"


def calculate_adjusted_confidence(market_id: str, base_confidence: float) -> float:
    """
    Adjust signal confidence based on time-to-resolution
    
    Shorter timeframes = higher confidence multiplier
    Longer timeframes = reduced confidence
    
    Args:
        market_id: Polymarket market ID
        base_confidence: Base signal confidence (0-100)
    
    Returns:
        Adjusted confidence score
    """
    days = calculate_days_to_resolution(market_id)
    
    if days is None:
        return base_confidence
    
    # Apply time-based confidence multipliers based on backtest
    if days < 3:
        # Strong performance, boost confidence
        multiplier = 1.2  # +20% confidence
    elif days < 7:
        # Moderate performance, slight boost
        multiplier = 1.0  # No change
    elif days < 30:
        # Poor performance, reduce confidence
        multiplier = 0.7  # -30% confidence
    else:
        # Terrible performance, heavily reduce
        multiplier = 0.3  # -70% confidence
    
    adjusted = base_confidence * multiplier
    return min(100, adjusted)  # Cap at 100


def get_position_size(market_id: str, base_size: float, bankroll: float) -> float:
    """
    Calculate position size based on time-to-resolution
    
    Args:
        market_id: Polymarket market ID
        base_size: Base position size in USDC
        bankroll: Total bankroll in USDC
    
    Returns:
        Recommended position size in USDC
    """
    days = calculate_days_to_resolution(market_id)
    
    if days is None:
        return 0.0
    
    # Position sizing based on backtest results
    if days < 3:
        # Full size for highest edge
        max_pct = 0.12  # 12% of bankroll
        multiplier = 1.0
    elif days < 7:
        # Half size for moderate edge
        max_pct = 0.06  # 6% of bankroll
        multiplier = 0.5
    else:
        # No position for negative expectancy
        return 0.0
    
    max_position = bankroll * max_pct
    recommended = min(base_size * multiplier, max_position)
    
    return recommended


# Example usage and integration
def example_integration():
    """Example of how to integrate into existing trading system"""
    
    print("=" * 60)
    print("TIME-TO-RESOLUTION FILTER - EXAMPLE INTEGRATION")
    print("=" * 60)
    print()
    
    # Example market IDs (replace with real ones)
    test_markets = [
        {"id": "btc-today", "signal_confidence": 75},
        {"id": "election-next-week", "signal_confidence": 80},
        {"id": "yearly-prediction", "signal_confidence": 85},
    ]
    
    bankroll = 1000.0  # $1000 example bankroll
    
    for market in test_markets:
        market_id = market['id']
        base_confidence = market['signal_confidence']
        
        print(f"Market: {market_id}")
        print(f"Base Confidence: {base_confidence}%")
        
        # Get time to resolution
        days = calculate_days_to_resolution(market_id)
        print(f"Days to Resolution: {days:.1f}")
        
        # Check if should trade
        should_trade, size_mult, reason = should_trade_market(market_id, base_confidence)
        print(f"Should Trade: {should_trade}")
        print(f"Reason: {reason}")
        
        if should_trade:
            # Calculate adjusted confidence
            adj_confidence = calculate_adjusted_confidence(market_id, base_confidence)
            print(f"Adjusted Confidence: {adj_confidence:.1f}%")
            
            # Calculate position size
            base_size = 100.0  # $100 base position
            position = get_position_size(market_id, base_size, bankroll)
            print(f"Position Size: ${position:.2f}")
        
        print("-" * 60)
        print()


def add_to_existing_signal_evaluator():
    """
    Pseudo-code showing how to add to existing signal evaluation
    """
    code_example = '''
    # In your existing signal evaluator:
    
    def evaluate_signal(market_id, signal_data):
        """Enhanced signal evaluation with time filter"""
        
        # Your existing signal logic
        base_confidence = calculate_base_confidence(signal_data)
        
        # ADD THIS: Time-to-resolution filter
        should_trade, size_mult, reason = should_trade_market(market_id, base_confidence)
        
        if not should_trade:
            logger.info(f"Skipping {market_id}: {reason}")
            return None  # Don't trade this market
        
        # Adjust confidence based on time horizon
        adjusted_confidence = calculate_adjusted_confidence(market_id, base_confidence)
        
        # Calculate position size with time consideration
        position_size = get_position_size(market_id, base_size, bankroll) * size_mult
        
        return {
            'market_id': market_id,
            'confidence': adjusted_confidence,
            'position_size': position_size,
            'time_category': reason,
            'trade': True
        }
    '''
    
    print("INTEGRATION CODE EXAMPLE:")
    print("=" * 60)
    print(code_example)


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║  TIME-TO-RESOLUTION FILTER IMPLEMENTATION                  ║
║                                                            ║
║  Based on backtest results:                                ║
║  • <3 days: 66.7% win rate, +$4.17 expectancy             ║
║  • 3-7 days: 50.0% win rate, +$0.83 expectancy            ║
║  • >7 days: AVOID (negative expectancy)                   ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("\nFunctions available:")
    print("  • get_market_end_date(market_id)")
    print("  • calculate_days_to_resolution(market_id)")
    print("  • should_trade_market(market_id, min_confidence)")
    print("  • calculate_adjusted_confidence(market_id, base_confidence)")
    print("  • get_position_size(market_id, base_size, bankroll)")
    print()
    
    # Show integration example
    add_to_existing_signal_evaluator()
