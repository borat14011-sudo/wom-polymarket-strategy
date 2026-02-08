import json

data = json.load(open(r'C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json'))

print(f"Total markets: {len(data)}")

# Check closed status
closed_true = sum(1 for m in data if m.get('closed') == True)
closed_false = sum(1 for m in data if m.get('closed') == False)
print(f"Closed=True: {closed_true}, Closed=False: {closed_false}")

# Check outcome values
with_outcome = [m for m in data if m.get('outcome') is not None]
print(f"With outcome: {len(with_outcome)}")

# For backtesting, we can simulate outcomes based on final price
# If final price > 0.9, assume YES won
# If final price < 0.1, assume NO won
can_backtest = 0
for m in data:
    ph = m.get('price_history', [])
    if len(ph) >= 10:
        final_price = ph[-1]['p']
        if final_price > 0.9 or final_price < 0.1:
            can_backtest += 1

print(f"Markets with clear outcome (price >0.9 or <0.1): {can_backtest}")

# Sample some markets
print("\n--- Sample Markets ---")
for m in data[:3]:
    ph = m.get('price_history', [])
    print(f"Q: {m['question'][:70]}...")
    print(f"  volume: ${m.get('volume',0):,.0f}")
    print(f"  closed: {m.get('closed')}, outcome: {m.get('outcome')}")
    if ph:
        print(f"  price: start={ph[0]['p']:.4f}, end={ph[-1]['p']:.4f}, points={len(ph)}")
    print()
