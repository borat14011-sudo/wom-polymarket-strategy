import json

with open('markets_snapshot_20260207_221914.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

markets = data['markets']
print(f"Total markets: {len(markets)}")

closed = [m for m in markets if m.get('closed')]
print(f"Closed markets: {len(closed)}")

with_winner = [m for m in closed if m.get('outcome_winner')]
print(f"With outcome_winner: {len(with_winner)}")

# Check what fields are available
if closed:
    sample = closed[0]
    print("\nSample closed market:")
    for key in sample.keys():
        print(f"  {key}: {sample[key]}")
    
# Check if we can infer outcomes
print("\nChecking for outcome inference...")
for m in closed[:10]:
    print(f"\nMarket: {m['question'][:50]}")
    print(f"  closed: {m.get('closed')}")
    print(f"  outcome_winner: {m.get('outcome_winner')}")
    print(f"  last_trade_price: {m.get('last_trade_price')}")
    print(f"  outcome_prices: {m.get('outcome_prices')}")
    print(f"  outcomes: {m.get('outcomes')}")
