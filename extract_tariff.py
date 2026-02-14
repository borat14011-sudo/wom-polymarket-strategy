import json
import sys

with open('active-markets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

markets = data['markets']
tariff_markets = []
for m in markets:
    if 'collect' in m['question'].lower() and ('revenue' in m['question'].lower() or 'tariff' in m['question'].lower()):
        tariff_markets.append(m)
        print(f"ID: {m['id']}")
        print(f"Question: {m['question']}")
        print(f"OutcomePrices: {m['outcomePrices']}")
        print(f"Liquidity: {m['liquidityNum']}")
        print(f"Volume: {m['volumeNum']}")
        print(f"EndDate: {m['endDate']}")
        print("---")

# Compute implied probabilities
print("\nImplied probabilities (YES):")
for m in tariff_markets:
    try:
        prices = json.loads(m['outcomePrices'].replace("'", '"'))
        yes_price = float(prices[0])
        print(f"{m['question']}: {yes_price*100:.2f}%")
    except:
        pass