"""
Simple Polymarket API Monitor - No Browser Needed
Monitors paper position on "US strikes Iran by February 13" market
"""

import requests
import json
from datetime import datetime

# Configuration
GAMMA_API = "https://gamma-api.polymarket.com"
ENTRY_PRICE = 0.12  # 12% entry
POSITION_SIZE = 4.20  # $4.20 paper position
STOP_LOSS = 0.106  # 10.6% stop-loss trigger

def get_iran_markets():
    """Fetch all Iran strike markets from Polymarket"""
    try:
        # Search for Iran markets
        url = f"{GAMMA_API}/markets"
        params = {
            'limit': 200,
            'active': True,
            'closed': False
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        markets = response.json()
        
        # Filter for Iran markets
        iran_markets = []
        for market in markets:
            title = market.get('question', '').lower()
            if 'iran' in title and 'strike' in title:
                iran_markets.append({
                    'id': market.get('id'),
                    'title': market.get('question'),
                    'yes_price': float(market.get('outcomePrices', ['0', '0'])[0]),
                    'no_price': float(market.get('outcomePrices', ['0', '0'])[1]),
                    'volume_24h': float(market.get('volume24hr', 0)),
                    'end_date': market.get('endDate', '')
                })
        
        return iran_markets
    
    except Exception as e:
        print(f"ERROR: Failed to fetch markets: {e}")
        return []

def find_feb13_market(iran_markets):
    """Find the February 13 market specifically"""
    for market in iran_markets:
        if 'february 13' in market['title'].lower() or 'feb 13' in market['title'].lower():
            return market
    
    # If not found by title, find closest by end date
    for market in iran_markets:
        if '2026-02-13' in market['end_date']:
            return market
    
    return None

def calculate_pnl(current_price, entry_price, position_size):
    """Calculate P&L for position"""
    price_change_pct = ((current_price - entry_price) / entry_price) * 100
    pnl_dollars = ((current_price - entry_price) / entry_price) * position_size
    return price_change_pct, pnl_dollars

def format_price(price):
    """Format price as percentage"""
    return f"{price*100:.1f}%"

def main():
    print("=" * 60)
    print("POLYMARKET API MONITOR")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S CST')}")
    print()
    
    # Fetch markets
    print("Fetching Iran strike markets...")
    iran_markets = get_iran_markets()
    
    if not iran_markets:
        print("ERROR: No Iran markets found!")
        return
    
    print(f"Found {len(iran_markets)} Iran strike markets")
    print()
    
    # Find Feb 13 market
    feb13_market = find_feb13_market(iran_markets)
    
    if not feb13_market:
        print("ERROR: Could not find February 13 market!")
        print("\nAvailable Iran markets:")
        for m in iran_markets:
            print(f"  - {m['title']} ({format_price(m['yes_price'])})")
        return
    
    # Display position status
    current_price = feb13_market['yes_price']
    price_change_pct, pnl_dollars = calculate_pnl(current_price, ENTRY_PRICE, POSITION_SIZE)
    
    print("PAPER POSITION STATUS")
    print("-" * 60)
    print(f"Market: {feb13_market['title']}")
    print(f"Entry Price: {format_price(ENTRY_PRICE)}")
    print(f"Current Price: {format_price(current_price)}")
    print(f"Position Size: ${POSITION_SIZE:.2f} (paper)")
    print(f"Price Change: {price_change_pct:+.1f}%")
    print(f"P&L: ${pnl_dollars:+.2f} ({price_change_pct:+.1f}%)")
    print(f"Stop-Loss: {format_price(STOP_LOSS)}")
    
    # Check stop-loss
    if current_price <= STOP_LOSS:
        print("\n*** STOP-LOSS TRIGGERED ***")
        print(f"Current price ({format_price(current_price)}) <= Stop ({format_price(STOP_LOSS)})")
    
    print()
    print("MARKET DATA")
    print("-" * 60)
    print(f"Volume (24h): ${feb13_market['volume_24h']:,.0f}")
    print(f"Bid/Ask: {format_price(current_price - 0.01)} / {format_price(current_price + 0.01)}")
    print(f"Resolution Date: {feb13_market['end_date']}")
    print()
    
    # Show all Iran markets for context
    print("ALL IRAN STRIKE MARKETS")
    print("-" * 60)
    for market in sorted(iran_markets, key=lambda x: x['yes_price']):
        indicator = " <-- OUR POSITION" if market['id'] == feb13_market['id'] else ""
        print(f"{format_price(market['yes_price']):>6} - {market['title'][:50]}{indicator}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
