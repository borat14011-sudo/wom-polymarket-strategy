import json

with open('active-markets.json', 'r', encoding='utf-8') as f:
    markets = json.load(f)

print(f"Total markets: {len(markets)}")

price_distribution = {
    '<0.1': 0, '0.1-0.2': 0, '0.2-0.3': 0, '0.3-0.4': 0,
    '0.4-0.5': 0, '0.5-0.6': 0, '0.6-0.7': 0, '0.7-0.8': 0,
    '0.8-0.9': 0, '0.9-1.0': 0
}

for market in markets:
    question = market.get('question', '')
    outcomes = market.get('outcomes', [])
    prices = market.get('outcomePrices', [])
    
    if len(prices) >= 2 and len(outcomes) >= 2:
        try:
            yes_price = float(prices[0]) if outcomes[0] == 'Yes' else float(prices[1])
            
            if yes_price < 0.1:
                price_distribution['<0.1'] += 1
            elif yes_price < 0.2:
                price_distribution['0.1-0.2'] += 1
            elif yes_price < 0.3:
                price_distribution['0.2-0.3'] += 1
            elif yes_price < 0.4:
                price_distribution['0.3-0.4'] += 1
            elif yes_price < 0.5:
                price_distribution['0.4-0.5'] += 1
            elif yes_price < 0.6:
                price_distribution['0.5-0.6'] += 1
            elif yes_price < 0.7:
                price_distribution['0.6-0.7'] += 1
            elif yes_price < 0.8:
                price_distribution['0.7-0.8'] += 1
            elif yes_price < 0.9:
                price_distribution['0.8-0.9'] += 1
            else:
                price_distribution['0.9-1.0'] += 1
                
        except:
            pass

print("\nPrice Distribution:")
for range_name, count in price_distribution.items():
    print(f"  {range_name}: {count}")

print("\nMarkets with YES price < 0.3:")
for market in markets:
    question = market.get('question', '')
    outcomes = market.get('outcomes', [])
    prices = market.get('outcomePrices', [])
    
    if len(prices) >= 2 and len(outcomes) >= 2:
        try:
            yes_price = float(prices[0]) if outcomes[0] == 'Yes' else float(prices[1])
            if yes_price < 0.3:
                print(f"  {yes_price:.3f}: {question[:80]}...")
        except:
            pass

print("\nMarkets with YES price > 0.7:")
for market in markets:
    question = market.get('question', '')
    outcomes = market.get('outcomes', [])
    prices = market.get('outcomePrices', [])
    
    if len(prices) >= 2 and len(outcomes) >= 2:
        try:
            yes_price = float(prices[0]) if outcomes[0] == 'Yes' else float(prices[1])
            if yes_price > 0.7:
                print(f"  {yes_price:.3f}: {question[:80]}...")
        except:
            pass