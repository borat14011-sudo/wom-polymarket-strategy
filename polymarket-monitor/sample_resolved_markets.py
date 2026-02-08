"""
Sample resolved markets to understand what data we have
"""
import json
import re

with open('historical-data-scraper/data/polymarket_complete.json', 'r') as f:
    events = json.load(f)

print(f"Total events: {len(events)}")

# Get closed events
closed_events = [e for e in events if e.get('closed')]
print(f"Closed events: {len(closed_events)}")

# Extract markets
resolved_markets = []
for event in closed_events:
    for market in event.get('markets', []):
        outcome_prices = market.get('outcome_prices')
        if outcome_prices and "1" in outcome_prices:
            resolved_markets.append(market)

print(f"Resolved markets: {len(resolved_markets)}")

# Find Musk markets
print(f"\n[MUSK MARKETS]")
musk_markets = [m for m in resolved_markets if 'musk' in m.get('question', '').lower()]
print(f"Total Musk markets: {len(musk_markets)}")

if musk_markets:
    print(f"\nSamples (first 5):")
    for m in musk_markets[:5]:
        q = m.get('question')
        outcome_prices = m.get('outcome_prices', [])
        price_histories = m.get('price_histories', {})
        
        yes_won = outcome_prices[0] == "1" if len(outcome_prices) > 0 else None
        has_prices = len(price_histories) > 0
        
        print(f"\n  Question: {q[:70]}")
        print(f"  Outcome: {'YES' if yes_won else 'NO'}")
        print(f"  Has price history: {has_prices}")
        
        if has_prices:
            # Show price history structure
            token_id = list(price_histories.keys())[0]
            prices = price_histories[token_id]
            print(f"  Price snapshots: {len(prices)}")
            if prices:
                print(f"  First price: {prices[0]}")

# Find crypto markets
print(f"\n[CRYPTO MARKETS]")
crypto_keywords = ['bitcoin', 'btc', 'solana', 'xrp', 'ethereum']
crypto_markets = []

for m in resolved_markets:
    q = m.get('question', '').lower()
    if any(kw in q for kw in crypto_keywords):
        crypto_markets.append(m)

print(f"Total crypto markets: {len(crypto_markets)}")

if crypto_markets:
    print(f"\nSamples (first 3):")
    for m in crypto_markets[:3]:
        q = m.get('question')
        outcome_prices = m.get('outcome_prices', [])
        price_histories = m.get('price_histories', {})
        
        yes_won = outcome_prices[0] == "1" if len(outcome_prices) > 0 else None
        has_prices = len(price_histories) > 0
        
        print(f"\n  Question: {q[:70]}")
        print(f"  Outcome: {'YES' if yes_won else 'NO'}")
        print(f"  Has price history: {has_prices}")

# Check how many have price history
with_prices = sum(1 for m in resolved_markets if len(m.get('price_histories', {})) > 0)
print(f"\n[PRICE HISTORY]")
print(f"  Resolved markets: {len(resolved_markets)}")
print(f"  With price history: {with_prices} ({with_prices/len(resolved_markets)*100:.1f}%)")
print(f"  Without: {len(resolved_markets) - with_prices}")
