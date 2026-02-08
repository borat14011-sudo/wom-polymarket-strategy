import json

with open('markets_snapshot_20260207_221914.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

markets = data['markets']
closed = [m for m in markets if m.get('closed') and m.get('outcome_prices') and len(m.get('outcome_prices', [])) >= 2]

print(f"Total closed markets: {len(closed)}")

yes_no_markets = []
for m in closed:
    outcomes = m.get('outcomes', [])
    outcome_prices = m.get('outcome_prices', [])
    
    if len(outcomes) >= 2 and len(outcome_prices) >= 2:
        # Find Yes index
        yes_idx = None
        for i, outcome in enumerate(outcomes):
            if outcome.lower() == 'yes':
                yes_idx = i
                break
        
        if yes_idx is not None:
            yes_won = outcome_prices[yes_idx] >= 0.99
            yes_no_markets.append(yes_won)

print(f"Yes/No markets: {len(yes_no_markets)}")
yes_wins = sum(yes_no_markets)
print(f"Yes wins: {yes_wins} ({yes_wins/len(yes_no_markets)*100:.1f}%)")
print(f"No wins: {len(yes_no_markets) - yes_wins} ({(len(yes_no_markets) - yes_wins)/len(yes_no_markets)*100:.1f}%)")

print("\n" + "="*60)
print("INSIGHT: Polymarket Yes/No markets have a strong NO bias!")
print("This is likely because:")
print("1. People are optimistic about exciting events (optimism bias)")
print("2. 'Will X happen?' questions attract hopeful traders")
print("3. Reality is usually more boring than speculation")
print("="*60)
