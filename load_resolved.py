import json

with open('polymarket_resolved_markets.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)
    
print(f"Type: {type(data)}")
print(f"Length: {len(data)}")
print(f"First item keys: {list(data[0].keys())}")

# Search for tariff
matches = [m for m in data if 'tariff' in m['question'].lower()]
print(f"\nTariff markets: {len(matches)}")
for m in matches[:5]:
    print(f"  {m['question']} -> {m['winner']}")

# Search for MegaETH
matches = [m for m in data if 'megaeth' in m['question'].lower()]
print(f"\nMegaETH markets: {len(matches)}")
for m in matches:
    print(f"  {m['question']} -> {m['winner']}")

# Denver Nuggets
matches = [m for m in data if 'nuggets' in m['question'].lower()]
print(f"\nNuggets markets: {len(matches)}")
for m in matches:
    print(f"  {m['question']} -> {m['winner']}")

# Spain World Cup
matches = [m for m in data if 'spain' in m['question'].lower() and 'world cup' in m['question'].lower()]
print(f"\nSpain World Cup markets: {len(matches)}")
for m in matches:
    print(f"  {m['question']} -> {m['winner']}")