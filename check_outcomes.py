#!/usr/bin/env python3
import json
from collections import Counter

data = json.load(open('polymarket-monitor/historical-data-scraper/data/backtest_dataset_v1.json'))

total = len(data)
with_outcome = sum(1 for m in data if m.get('outcome') is not None)
without_outcome = total - with_outcome

print(f"Total markets: {total}")
print(f"Markets with outcome: {with_outcome}")
print(f"Markets without outcome: {without_outcome}")
print(f"Percentage resolved: {with_outcome/total*100:.1f}%")

# Check outcome values
outcomes = Counter()
for m in data:
    if m.get('outcome') is not None:
        outcomes[m['outcome']] += 1

print(f"\nOutcome distribution:")
for outcome, count in outcomes.most_common():
    print(f"  {outcome}: {count}")

# Show a few examples with outcomes
print(f"\nSample resolved markets:")
for m in data:
    if m.get('outcome') is not None:
        print(f"\nQuestion: {m['question']}")
        print(f"Outcome: {m['outcome']}")
        print(f"Start: {m['start_date']}")
        print(f"End: {m['end_date']}")
        print(f"Closed: {m['closed']}")
        if m.get('price_history'):
            prices = [p['p'] for p in m['price_history']]
            print(f"Price range: {min(prices):.4f} - {max(prices):.4f}")
        break
