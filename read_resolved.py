import json

with open('polymarket_resolved_markets.json', 'r', encoding='utf-8-sig') as f:
    # Read first 5 lines
    for i in range(5):
        line = f.readline()
        if not line:
            break
        obj = json.loads(line.strip())
        print(f"Line {i}: {obj['question'][:100]}...")

# Now count total lines
print("\nCounting total lines...")
count = 0
with open('polymarket_resolved_markets.json', 'r', encoding='utf-8-sig') as f:
    for line in f:
        count += 1
print(f"Total lines: {count}")

# Search for tariff in all lines
print("\nSearching for tariff...")
matches = []
with open('polymarket_resolved_markets.json', 'r', encoding='utf-8-sig') as f:
    for line in f:
        obj = json.loads(line.strip())
        if 'tariff' in obj['question'].lower():
            matches.append(obj)
print(f"Found {len(matches)} tariff markets")
for m in matches:
    print(f"  {m['question']} -> {m['winner']}")