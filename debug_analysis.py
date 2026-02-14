import json
import requests
from datetime import datetime, timezone

def fetch_markets():
    """Fetch active markets from Polymarket API"""
    url = "https://gamma-api.polymarket.com/markets?limit=100&closed=false"
    response = requests.get(url)
    return response.json()

def main():
    print("Fetching Polymarket data...")
    markets = fetch_markets()
    
    print(f"Found {len(markets)} active markets")
    
    # Let's examine the first few markets
    for i, market in enumerate(markets[:5]):
        print(f"\n=== Market {i+1} ===")
        print(f"Question: {market.get('question')}")
        print(f"OutcomePrices: {market.get('outcomePrices')}")
        print(f"Best Bid: {market.get('bestBid')}")
        print(f"Best Ask: {market.get('bestAsk')}")
        print(f"Volume 24h: {market.get('volume24hr')}")
        print(f"Liquidity: {market.get('liquidityNum')}")
        
        # Parse outcome prices
        outcome_prices_str = market.get('outcomePrices', '["0", "0"]')
        try:
            outcome_prices = outcome_prices_str.strip('[]"').replace('"', '').split(',')
            yes_price = float(outcome_prices[0].strip())
            no_price = float(outcome_prices[1].strip())
            print(f"Parsed YES: {yes_price}, NO: {no_price}")
            
            # Check if in our range
            if 0.08 <= yes_price <= 0.92:
                print(f"✓ Price in range (8-92%)")
            else:
                print(f"✗ Price out of range: {yes_price*100:.1f}%")
                
            # Check volume
            volume = market.get('volume24hr', 0)
            if volume > 1000:
                print(f"✓ Volume sufficient: ${volume:,.0f}")
            else:
                print(f"✗ Volume insufficient: ${volume:,.0f}")
                
        except Exception as e:
            print(f"Error parsing: {e}")

if __name__ == "__main__":
    main()