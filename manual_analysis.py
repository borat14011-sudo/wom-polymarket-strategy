import json
from datetime import datetime, timezone
import math

# Sample data from the web_fetch response
# Let me analyze the deportation markets we saw

markets_data = [
    {
        "id": "517310",
        "question": "Will Trump deport less than 250,000?",
        "outcomePrices": '["0.0545", "0.9455"]',
        "volume24hr": 13558.463149000005,
        "liquidityNum": 11383.30748,
        "endDate": "2025-12-31T12:00:00Z",
        "bestBid": 0.051,
        "bestAsk": 0.058
    },
    {
        "id": "517311", 
        "question": "Will Trump deport 250,000-500,000 people?",
        "outcomePrices": '["0.8905", "0.1095"]',
        "volume24hr": 1307782.493223,
        "liquidityNum": 7354.08533,
        "endDate": "2025-12-31T12:00:00Z",
        "bestBid": 0.873,
        "bestAsk": 0.908
    },
    {
        "id": "517313",
        "question": "Will Trump deport 500,000-750,000 people?",
        "outcomePrices": '["0.0225", "0.9775"]',
        "volume24hr": 7803.025673,
        "liquidityNum": 5247.52478,
        "endDate": "2025-12-31T12:00:00Z",
        "bestBid": 0.02,
        "bestAsk": 0.025
    }
]

def parse_outcome_prices(outcome_prices_str):
    """Parse outcome prices string"""
    try:
        outcome_prices = outcome_prices_str.strip('[]"').replace('"', '').split(',')
        yes_price = float(outcome_prices[0].strip())
        no_price = float(outcome_prices[1].strip())
        return yes_price, no_price
    except:
        return 0.5, 0.5

def calculate_days_until_resolution(end_date_str):
    """Calculate days until resolution"""
    if not end_date_str:
        return None
    
    try:
        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        delta = end_date - now
        return max(0, delta.days)
    except:
        return None

def calculate_expected_value(yes_price, no_price, days_until_resolution, true_probability=0.5):
    """
    Calculate expected value after 4% transaction costs + 1% slippage
    """
    # Use mid-price for calculation
    mid_price = yes_price
    
    # Apply 1% slippage (worst-case execution)
    execution_price = mid_price * 1.01 if mid_price < 0.5 else mid_price * 0.99
    
    # Calculate payout if correct (1 - execution_price after costs)
    gross_payout = 1 - execution_price
    net_payout = gross_payout * 0.98 * 0.98  # Apply both entry and exit fees
    
    # Calculate expected value
    expected_value = (true_probability * net_payout) - ((1 - true_probability) * execution_price * 1.02)
    
    # Annualize if we have days until resolution
    if days_until_resolution and days_until_resolution > 0:
        annualized = ((1 + expected_value) ** (365 / days_until_resolution)) - 1
    else:
        annualized = None
    
    return expected_value * 100, annualized * 100 if annualized else None

def analyze_market(market):
    """Analyze a single market"""
    question = market.get('question', '')
    yes_price, no_price = parse_outcome_prices(market.get('outcomePrices', '["0.5", "0.5"]'))
    volume_24hr = market.get('volume24hr', 0)
    liquidity = market.get('liquidityNum', 0)
    end_date = market.get('endDate')
    
    days_until_resolution = calculate_days_until_resolution(end_date)
    
    # For demonstration, let's assume different true probabilities based on context
    # For deportation markets, we might have different views
    
    print(f"\n=== {question} ===")
    print(f"YES Price: {yes_price*100:.2f}% | NO Price: {no_price*100:.2f}%")
    print(f"24h Volume: ${volume_24hr:,.0f}")
    print(f"Liquidity: ${liquidity:,.0f}")
    print(f"Days to resolution: {days_until_resolution}")
    
    # Check basic filters
    in_price_range = 0.08 <= yes_price <= 0.92
    sufficient_volume = volume_24hr > 1000
    
    print(f"Price in range (8-92%): {'YES' if in_price_range else 'NO'} ({yes_price*100:.1f}%)")
    print(f"Volume > $1000/day: {'YES' if sufficient_volume else 'NO'} (${volume_24hr:,.0f})")
    
    if in_price_range and sufficient_volume:
        # Calculate EV with different true probability assumptions
        # For deportation markets, we might have an edge if we think market is wrong
        
        # Example: If we think <250k has 20% true probability (vs 5.45% market)
        true_prob = 0.20  # Our estimate
        ev, ann = calculate_expected_value(yes_price, no_price, days_until_resolution, true_prob)
        
        print(f"\nWith true probability estimate of {true_prob*100:.0f}%:")
        print(f"Expected Value: {ev:.2f}%")
        if ann:
            print(f"Annualized Return: {ann:.2f}%")
        
        if ev > 3:
            print("MEETS CRITERIA: EV > 3%")
        else:
            print("FAILS: EV <= 3%")
    
    return in_price_range and sufficient_volume

def main():
    print("Analyzing deportation markets...")
    
    opportunities = []
    for market in markets_data:
        if analyze_market(market):
            opportunities.append(market.get('question'))
    
    print(f"\n=== SUMMARY ===")
    print(f"Markets analyzed: {len(markets_data)}")
    print(f"Markets passing basic filters: {len(opportunities)}")
    
    if opportunities:
        print("\nPotential opportunities (need EV analysis):")
        for opp in opportunities:
            print(f"  - {opp}")

if __name__ == "__main__":
    main()