import json

with open('live_bets_output.json', 'r') as f:
    data = json.load(f)

for market in data['top_markets']:
    if 'collect less than $100b' in market['question']:
        print('Market Found:')
        print(f"Question: {market['question']}")
        print(f"Condition ID: {market['condition_id']}")
        print(f"Slug: {market['slug']}")
        print(f"Volume: ${market['volume']:,.2f}")
        print(f"Best Bid: {market.get('best_bid', 'N/A')}")
        print(f"Best Ask: {market.get('best_ask', 'N/A')}")
        print(f"Outcome Prices: {market.get('outcome_prices', 'N/A')}")
        print(f"Token IDs: {market.get('token_ids', 'N/A')}")
        break