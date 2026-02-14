import json

# Check active markets
with open('active-markets.json', 'r') as f:
    data = json.load(f)

markets = data.get('markets', [])
print("=== CARDI B MARKETS IN ACTIVE-MARKETS.JSON ===")
found = False
for m in markets:
    question = m.get('question', '').lower()
    if 'cardi' in question:
        found = True
        print(f"ID: {m.get('id')}")
        print(f"Question: {m.get('question')}")
        print(f"Closed: {m.get('closed')}")
        print(f"Archived: {m.get('archived')}")
        print(f"Outcome Prices: {m.get('outcomePrices')}")
        print(f"End Date: {m.get('endDate')}")
        print(f"---")

if not found:
    print("No Cardi B markets found in active-markets.json")
