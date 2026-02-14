import json
import pandas as pd

print("Searching for tariff-related markets...")
# Search resolved markets
with open('polymarket_resolved_markets.json', 'r', encoding='utf-8-sig') as f:
    resolved = json.load(f)

tariff_markets = []
for m in resolved:
    if 'tariff' in m['question'].lower():
        tariff_markets.append(m)
        
print(f"Found {len(tariff_markets)} tariff markets in resolved")
for m in tariff_markets[:5]:
    print(f"  ID: {m['market_id']}, Question: {m['question']}, Winner: {m['winner']}")

# Search active markets
with open('active-markets.json', 'r', encoding='utf-8') as f:
    active_data = json.load(f)

active_tariff = []
for m in active_data['markets']:
    if 'tariff' in m['question'].lower():
        active_tariff.append(m)

print(f"\nFound {len(active_tariff)} tariff markets in active")
for m in active_tariff[:5]:
    print(f"  ID: {m['id']}, Question: {m['question'][:100]}...")

# Search for MegaETH, Denver Nuggets, Spain World Cup
print("\n=== Searching for specified strategies ===")
strategies = [
    ('MegaETH', 'megacth'),
    ('Denver Nuggets', 'nuggets'),
    ('Spain World Cup', 'spain')
]

for keyword, alt in strategies:
    found = []
    for m in resolved:
        if keyword.lower() in m['question'].lower() or alt.lower() in m['question'].lower():
            found.append(m)
    print(f"{keyword}: {len(found)} markets")
    for m in found[:3]:
        print(f"  {m['question']} -> {m['winner']}")