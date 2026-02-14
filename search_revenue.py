import json
import re

with open('polymarket_resolved_markets.json', 'r', encoding='utf-8-sig') as f:
    resolved = json.load(f)

print(f"Total resolved markets: {len(resolved)}")

# Find all markets with revenue or tariff
keywords = ['revenue', 'tariff', 'fy2025', 'fy2026', 'fiscal year']
for kw in keywords:
    matches = [m for m in resolved if kw in m['question'].lower()]
    print(f"{kw}: {len(matches)}")
    for m in matches[:3]:
        print(f"  {m['question']} -> {m['winner']}")

# Let's also look for any market with year pattern
year_pattern = r'202[0-9]'
year_matches = []
for m in resolved:
    if re.search(year_pattern, m['question']):
        year_matches.append(m)
print(f"\nMarkets with year: {len(year_matches)}")
for m in year_matches[:5]:
    print(f"  {m['question']}")