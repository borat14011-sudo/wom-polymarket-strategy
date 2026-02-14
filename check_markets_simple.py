import json

with open('live_bets_output.json', 'r') as f:
    data = json.load(f)

print('Total markets:', len(data.get('top_markets', [])))
print('\nMarkets with NO < 20% (Longshot candidates):')
count = 0
for i, m in enumerate(data['top_markets']):
    question = m.get('question', '')
    prices = m.get('outcome_prices', [])
    if len(prices) == 2:
        yes_price = prices[0]
        no_price = prices[1]
        if no_price < 0.20:  # NO price < 20%
            count += 1
            print(f'{count}. {question[:80]}')
            print(f'   NO: {no_price:.3f} ({no_price*100:.1f}%) | Volume: ${m.get("volume", 0):,.0f}')
            print()