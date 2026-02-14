import json

with open('active-markets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for market in data:
    if 'tariff' in market['question'].lower() or '200' in market['question']:
        print(f"ID: {market['id']}")
        print(f"Question: {market['question']}")
        print(f"YES Price: {market['outcomePrices'][0]}")
        print(f"NO Price: {market['outcomePrices'][1]}")
        print(f"Volume: ${float(market['volume']):,.2f}")
        print(f"Liquidity: ${float(market['liquidity']):,.2f}")
        print(f"End Date: {market['endDate']}")
        print("-" * 80)