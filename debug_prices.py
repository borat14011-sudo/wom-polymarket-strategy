import json

with open('active-markets.json', 'r', encoding='utf-8') as f:
    markets = json.load(f)

print('Checking first 5 markets:')
for i, market in enumerate(markets[:5]):
    print(f'\nMarket {i}:')
    print(f'  Question: {market.get("question", "N/A")[:60]}...')
    print(f'  Outcomes: {market.get("outcomes", [])}')
    print(f'  Prices: {market.get("outcomePrices", [])}')
    print(f'  Type of prices: {type(market.get("outcomePrices", []))}')
    if market.get('outcomePrices'):
        print(f'  First price type: {type(market["outcomePrices"][0])}')
        print(f'  First price value: {market["outcomePrices"][0]}')
        print(f'  Float conversion: {float(market["outcomePrices"][0])}')