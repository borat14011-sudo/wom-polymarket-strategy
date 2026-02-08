"""
Extract resolved markets from polymarket_complete.json
Events have nested markets - need to flatten
"""
import json

print("[EXTRACT] Resolved markets from polymarket_complete.json")

filepath = 'historical-data-scraper/data/polymarket_complete.json'

print("\n[LOAD] Loading 488 MB file (30-60 seconds)...")

with open(filepath, 'r') as f:
    events = json.load(f)

print(f"[OK] Loaded {len(events)} events")

# Flatten: extract all markets from all events
print("\n[FLATTEN] Extracting markets from events...")

all_markets = []
resolved_markets = []

for event in events:
    event_markets = event.get('markets', [])
    
    for market in event_markets:
        # Add event context to market
        market['event_closed'] = event.get('closed', False)
        market['event_volume'] = event.get('volume', 0)
        
        all_markets.append(market)
        
        # Check if resolved
        if market.get('closed') or market.get('outcome') is not None:
            resolved_markets.append(market)

print(f"\n[RESULT]")
print(f"  Total markets: {len(all_markets)}")
print(f"  Resolved: {len(resolved_markets)} ({len(resolved_markets)/len(all_markets)*100:.1f}%)")

# Check structure of resolved markets
if resolved_markets:
    print(f"\n[SAMPLE] Resolved market structure:")
    sample = resolved_markets[0]
    print(f"  Keys: {list(sample.keys())}")
    print(f"  Question: {sample.get('question', sample.get('title', 'N/A'))[:80]}")
    print(f"  Outcome: {sample.get('outcome')}")
    print(f"  Closed: {sample.get('closed')}")
    
    # Check if price history exists
    has_prices = 'price_history' in sample or 'prices' in sample
    print(f"  Has price history: {has_prices}")

# Find Musk resolved markets
print(f"\n[MUSK] Checking resolved Musk markets...")
musk_resolved = [m for m in resolved_markets if 'musk' in str(m.get('question', m.get('title', ''))).lower()]

print(f"  Found {len(musk_resolved)} resolved Musk markets")

if musk_resolved:
    print(f"\n  Samples:")
    for m in musk_resolved[:5]:
        q = m.get('question', m.get('title', 'Unknown'))
        outcome = m.get('outcome')
        print(f"    [{outcome}] {q[:70]}")

# Find crypto resolved markets
print(f"\n[CRYPTO] Checking resolved crypto markets...")
crypto_keywords = ['bitcoin', 'btc', 'solana', 'xrp', 'ethereum', 'eth']
crypto_resolved = []

for m in resolved_markets:
    q = str(m.get('question', m.get('title', ''))).lower()
    if any(kw in q for kw in crypto_keywords):
        crypto_resolved.append(m)

print(f"  Found {len(crypto_resolved)} resolved crypto markets")

if crypto_resolved:
    print(f"\n  Samples:")
    for m in crypto_resolved[:5]:
        q = m.get('question', m.get('title', 'Unknown'))
        outcome = m.get('outcome')
        print(f"    [{outcome}] {q[:70]}")

print(f"\n[SUMMARY]")
print(f"  We have {len(resolved_markets)} resolved markets to backtest!")
print(f"  This is REAL historical data with actual outcomes")
print(f"  Can validate all 5 strategies on this data")
