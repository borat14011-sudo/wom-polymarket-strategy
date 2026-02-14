"""
API TRADE TEST - Simulated Trading Logic
Since DNS is broken, we'll test the trading logic locally
"""

import json
import math
from datetime import datetime

# Load top 10 bets
with open('top_10_kalshi_bets.json', 'r') as f:
    top_bets = json.load(f)

# Trading parameters
CAPITAL = 100  # $100
RISK_PER_TRADE = 0.02  # 2% per trade
MIN_TRADE_SIZE = 1  # Minimum $1 per trade

def calculate_kelly_position(price, ev_percentage, win_prob=0.115):
    """
    Calculate Kelly-optimal position size
    price: price in cents (e.g., 7.5 for 7.5¢)
    ev_percentage: expected value percentage (e.g., 43.4)
    win_prob: strategy win probability (11.5% for Buy the Dip)
    """
    # Convert to decimal
    price_decimal = price / 100
    
    # Kelly formula: f* = (p × b - q) / b
    # where b = (1/price - 1) for binary options
    b = (1 / price_decimal) - 1  # payout ratio
    p = win_prob  # win probability
    q = 1 - p  # loss probability
    
    kelly_fraction = (p * b - q) / b
    
    # Fractional Kelly (1/3 for conservative)
    fractional_kelly = kelly_fraction / 3
    
    # Cap at 2% risk
    fractional_kelly = min(fractional_kelly, RISK_PER_TRADE)
    
    # Calculate position size
    position_size = CAPITAL * fractional_kelly
    
    # Ensure minimum trade size
    position_size = max(position_size, MIN_TRADE_SIZE)
    
    return round(position_size, 2)

def simulate_trades():
    """Simulate trading the top 3 bets"""
    print("=== API TRADE TEST SIMULATION ===")
    print(f"Capital: ${CAPITAL}")
    print(f"Risk per trade: {RISK_PER_TRADE*100}%")
    print()
    
    top_3 = top_bets[:3]
    
    total_invested = 0
    trades = []
    
    for i, bet in enumerate(top_3, 1):
        ticker = bet.get('ticker', 'Unknown')
        title = bet.get('title', 'Unknown')[:50]
        price = bet.get('price_cents', 0) or 7.5  # Default if 0
        ev = bet.get('expected_value_percentage', 0) or 43.4
        
        # Calculate position size
        position = calculate_kelly_position(price, ev)
        
        # Calculate contracts (each contract = $1)
        contracts = int(position)
        
        trades.append({
            'rank': i,
            'ticker': ticker,
            'title': title,
            'price_cents': price,
            'ev_percentage': ev,
            'position_size': position,
            'contracts': contracts
        })
        
        total_invested += position
    
    # Display results
    print("TOP 3 TRADES TO EXECUTE:")
    print("-" * 80)
    
    for trade in trades:
        print(f"{trade['rank']}. {trade['ticker']}")
        print(f"   {trade['title']}...")
        print(f"   Price: {trade['price_cents']}¢ | EV: {trade['ev_percentage']}%")
        print(f"   Position: ${trade['position_size']} ({trade['contracts']} contracts)")
        print(f"   Kelly Allocation: {trade['position_size']/CAPITAL*100:.1f}% of capital")
        print()
    
    print("-" * 80)
    print(f"TOTAL INVESTMENT: ${total_invested:.2f}")
    print(f"REMAINING CAPITAL: ${CAPITAL - total_invested:.2f}")
    print(f"PERCENTAGE DEPLOYED: {total_invested/CAPITAL*100:.1f}%")
    
    # Generate API call examples
    print("\n=== SAMPLE API CALLS ===")
    print("If API worked, you would send:")
    
    for trade in trades:
        print(f"\nTrade {trade['rank']} ({trade['ticker']}):")
        print(f"  POST https://trading-api.kalshi.com/trade-api/v2/orders")
        print(f"  Headers: Authorization: Bearer YOUR_API_KEY")
        print(f"  Body: {{")
        print(f"    \"ticker\": \"{trade['ticker']}\",")
        print(f"    \"side\": \"yes\",")
        print(f"    \"action\": \"buy\",")
        print(f"    \"count\": {trade['contracts']},")
        print(f"    \"type\": \"limit\",")
        print(f"    \"price\": {trade['price_cents']}")
        print(f"  }}")
    
    return trades

if __name__ == "__main__":
    # Load the actual top 10 bets file
    try:
        with open('top_10_kalshi_bets.json', 'r') as f:
            top_bets = json.load(f)
        simulate_trades()
    except FileNotFoundError:
        print("Error: top_10_kalshi_bets.json not found")
        print("Creating sample data for testing...")
        
        # Create sample data
        sample_bets = [
            {
                "ticker": "KXNEXTISRAELPM-45JAN01-YGAL",
                "title": "Yoav Gallant - Next Israeli Prime Minister",
                "price_cents": 7.5,
                "expected_value_percentage": 43.4
            },
            {
                "ticker": "KXMEDIARELEASEPRISONBREAK-30JAN01-26JUL01",
                "title": "New Season of Prison Break Released by 2030",
                "price_cents": 9.0,
                "expected_value_percentage": 43.0
            },
            {
                "ticker": "KXRAMPBREX-40-BREX",
                "title": "Ramp vs Brex IPO Race - Brex IPOs First",
                "price_cents": 1.5,
                "expected_value_percentage": 41.2
            }
        ]
        
        top_bets = sample_bets
        simulate_trades()