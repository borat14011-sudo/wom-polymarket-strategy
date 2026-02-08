"""
Find patterns where YES wins MORE than the baseline 23.7%
These would be contrarian opportunities
"""

import json
from collections import defaultdict

with open('markets_snapshot_20260207_221914.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

markets = data['markets']

def extract_yes_won(m):
    outcomes = m.get('outcomes', [])
    outcome_prices = m.get('outcome_prices', [])
    
    if len(outcomes) >= 2 and len(outcome_prices) >= 2:
        yes_idx = None
        for i, outcome in enumerate(outcomes):
            if outcome.lower() == 'yes':
                yes_idx = i
                break
        
        if yes_idx is not None:
            return outcome_prices[yes_idx] >= 0.99
    return None

# Closed Yes/No markets with >$1K volume
tradeable = []
for m in markets:
    if not m.get('closed'):
        continue
    if m.get('volume', 0) < 1000:
        continue
    yes_won = extract_yes_won(m)
    if yes_won is not None:
        tradeable.append(m)

print(f"Tradeable Yes/No markets: {len(tradeable)}")

# Look for patterns where Yes wins MORE than 30% (above baseline 23.7%)
patterns_to_test = []

# Time-based patterns where Yes WINS
import re
from datetime import datetime

for m in tradeable:
    question = m.get('question', '').lower()
    
    # Pattern: "Above" or "Over" in question (threshold markets)
    if 'above' in question or 'over' in question or 'higher than' in question:
        m['pattern'] = 'THRESHOLD_ABOVE'
    # Pattern: "Below" or "Under"  
    elif 'below' in question or 'under' in question or 'less than' in question or 'lower than' in question:
        m['pattern'] = 'THRESHOLD_BELOW'
    # Pattern: Questions with numbers/statistics
    elif re.search(r'\d{3,}', question):
        m['pattern'] = 'NUMERIC_THRESHOLD'
    # Pattern: Sports/gambling markets
    elif any(w in question for w in ['nfl', 'nba', 'mlb', 'fifa', 'super bowl', 'world cup']):
        m['pattern'] = 'SPORTS_MAJOR'
    # Pattern: Markets about negative events
    elif any(w in question for w in ['impeach', 'arrest', 'resign', 'die', 'crash', 'war', 'attack']):
        m['pattern'] = 'NEGATIVE_EVENT'
    else:
        m['pattern'] = 'OTHER'

# Calculate Yes win rates by pattern
pattern_stats = defaultdict(lambda: {'yes_wins': 0, 'total': 0, 'examples': []})

for m in tradeable:
    pattern = m.get('pattern', 'OTHER')
    yes_won = extract_yes_won(m)
    
    pattern_stats[pattern]['total'] += 1
    if yes_won:
        pattern_stats[pattern]['yes_wins'] += 1
    
    if len(pattern_stats[pattern]['examples']) < 5:
        pattern_stats[pattern]['examples'].append(m.get('question', ''))

print("\nPATTERNS WHERE YES WINS MORE THAN BASELINE (23.7%):")
print("="*80)

sorted_patterns = sorted(pattern_stats.items(), key=lambda x: x[1]['yes_wins']/x[1]['total'] if x[1]['total'] > 20 else 0, reverse=True)

for pattern, stats in sorted_patterns:
    if stats['total'] < 20:
        continue
    
    yes_rate = stats['yes_wins'] / stats['total']
    
    if yes_rate > 0.30:  # Above baseline + some margin
        print(f"\n{pattern}:")
        print(f"  Yes Win Rate: {yes_rate:.1%}")
        print(f"  Sample Size: {stats['total']}")
        print(f"  Strategy: BET YES (counter to general trend)")
        print(f"  Examples:")
        for ex in stats['examples'][:3]:
            print(f"    - {ex}")
