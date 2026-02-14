import json

with open('active-markets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for market in data:
    if market['id'] == '537486':
        print(f"ID: {market['id']}")
        print(f"Question: {market['question']}")
        
        # Parse the outcomePrices string
        prices_str = market['outcomePrices']
        if isinstance(prices_str, str):
            prices = json.loads(prices_str.replace("'", '"'))
        else:
            prices = prices_str
            
        print(f"YES Price: {float(prices[0]) * 100:.1f}%")
        print(f"NO Price: {float(prices[1]) * 100:.1f}%")
        print(f"Volume: ${float(market['volume']):,.2f}")
        print(f"Liquidity: ${float(market['liquidity']):,.2f}")
        print(f"End Date: {market['endDate']}")
        print(f"Description: {market['description'][:200]}...")
        print("-" * 80)
        break