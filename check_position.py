import requests
import json

# Fetch more markets
response = requests.get('https://gamma-api.polymarket.com/markets', params={'limit': 200, 'closed': False})
markets = response.json()

# Find all Iran markets
iran_markets = [m for m in markets if 'iran' in m.get('question', '').lower()]

print(f"Found {len(iran_markets)} Iran-related markets:")
print()

for market in iran_markets[:10]:
    # Parse outcomePrices (it's a JSON string)
    prices_str = market.get('outcomePrices', '[]')
    if isinstance(prices_str, str):
        prices = json.loads(prices_str)
    else:
        prices = prices_str
    
    yes_price = float(prices[0]) if prices else 0
    question = market['question']
    end_date = market.get('endDate', 'Unknown')
    
    print(f"Q: {question}")
    print(f"   YES: {yes_price*100:.1f}% | End: {end_date}")
    
    # Check if this is our Feb 13 position
    if 'february 13' in question.lower() or 'feb 13' in question.lower() or '2026-02-13' in end_date:
        print(f"   >>> THIS IS OUR POSITION! <<<")
        entry = 0.12
        position_size = 4.20
        pnl = ((yes_price - entry) / entry) * position_size
        pnl_pct = ((yes_price - entry) / entry) * 100
        print(f"   Entry: 12% | Current: {yes_price*100:.1f}%")
        print(f"   P&L: ${pnl:.2f} ({pnl_pct:.1f}%)")
        print(f"   Paper balance: ${100 + pnl:.2f}")
    print()
