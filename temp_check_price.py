import requests

# Fetch event data
url = "https://gamma-api.polymarket.com/events/us-strikes-iran-by"
resp = requests.get(url)
data = resp.json()

# Find the February 13 market
for market in data.get('markets', []):
    question = market.get('question', '')
    if 'February 13' in question:
        # outcomePrices[0] is "Yes" probability
        yes_price = float(market['outcomePrices'][0]) * 100
        print(f"Market: {question}")
        print(f"Current Price: {yes_price:.1f}%")
        print(f"Entry Price: 12.0%")
        
        # P/L calculation
        position_size = 4.20
        entry_price = 12.0
        pl = (yes_price - entry_price) * position_size / entry_price
        print(f"P/L: ${pl:.2f} ({(yes_price - entry_price):.1f}%)")
        break
