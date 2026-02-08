# CHECK_MARKET_FORMAT.py - Debug market data format
import requests

r = requests.get('https://gamma-api.polymarket.com/markets?active=true&closed=false', timeout=15)
markets = r.json()

print("Checking market data format for Musk/Elon/DOGE markets")
print("="*60)

for market in markets:
    q = market.get('question', '').lower()
    if 'musk' in q or 'elon' in q or 'doge' in q:
        print(f"Question: {market.get('question')}")
        prices = market.get('outcomePrices', [])
        print(f"Raw Prices: {prices}")
        print(f"Type: {type(prices)}")
        
        if isinstance(prices, list) and len(prices) == 2:
            try:
                yes = float(prices[0])
                no = float(prices[1])
                print(f"YES: {yes:.4f} ({yes*100:.2f}%)")
                print(f"NO: {no:.4f} ({no*100:.2f}%)")
                is_extreme = yes >= 0.90 or yes <= 0.10
                print(f"Is Extreme: {is_extreme}")
                if is_extreme:
                    print(">>> EXTREME PROBABILITY DETECTED!")
            except Exception as e:
                print(f"Error: {e}")
        print("-"*60)