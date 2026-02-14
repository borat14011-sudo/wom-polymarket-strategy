import json
import sys

with open('active-markets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

markets = data.get('markets', [])
# Sort by volumeNum descending
markets.sort(key=lambda m: m.get('volumeNum', 0), reverse=True)
top20 = markets[:20]

# Print as formatted summary
for i, m in enumerate(top20, 1):
    print(f"{i}. {m.get('question', 'N/A')}")
    print(f"   ID: {m.get('id')}, Volume: ${m.get('volumeNum', 0):,.2f}, Liquidity: ${m.get('liquidityNum', 0):,.2f}, End: {m.get('endDateIso', 'N/A')}")
    print(f"   Yes price: {m.get('outcomePrices', ['?'])[0] if isinstance(m.get('outcomePrices'), list) else '?'}")
    print()