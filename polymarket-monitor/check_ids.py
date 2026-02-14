import json
import csv

# Load backtest data
data = json.load(open(r'C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json'))

# Get sample market IDs from backtest
print('Sample backtest market IDs:')
for m in data[:5]:
    mid = m.get('market_id')
    q = m.get('question', '')[:60]
    print(f'  ID: {mid} - {q}')

# Load resolved CSV
print('\nSample resolved market IDs:')
with open(r'C:\Users\Borat\.openclaw\workspace\polymarket_resolved_markets.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 5:
            break
        mid = row.get('market_id')
        q = row.get('question', '')[:60]
        winner = row.get('winner', '')
        print(f'  ID: {mid} - {q} | Winner: {winner}')

# Try to match by question text
print('\nTrying to match by question text...')
backtest_questions = {m.get('question', '').lower().strip(): m for m in data}
matches = 0

with open(r'C:\Users\Borat\.openclaw\workspace\polymarket_resolved_markets.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        q = row.get('question', '').lower().strip()
        if q in backtest_questions:
            matches += 1
            
print(f'Question text matches: {matches}')

# Check if closed markets might have outcomes we can infer
print('\nAnalyzing closed markets...')
closed = [m for m in data if m.get('closed') == True]
print(f'Closed markets: {len(closed)}')

# Check final prices of closed markets
final_price_1 = 0
final_price_0 = 0
for m in closed:
    ph = m.get('price_history', [])
    if ph:
        final = ph[-1].get('p', 0.5)
        if final >= 0.95:
            final_price_1 += 1
        elif final <= 0.05:
            final_price_0 += 1

print(f'Closed with final price >= 0.95 (likely YES): {final_price_1}')
print(f'Closed with final price <= 0.05 (likely NO): {final_price_0}')
print(f'These are our pseudo-resolved markets!')
