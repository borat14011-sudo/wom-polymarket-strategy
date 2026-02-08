"""
Check how many markets are resolved vs pending
Find tradeable opportunities in resolved markets
"""
import json

print("[LOAD] backtest_dataset_v1.json...")

with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
    markets = json.load(f)

print(f"[OK] {len(markets)} markets loaded\n")

# Count resolved vs pending
resolved_count = 0
pending_count = 0
resolved_yes = 0
resolved_no = 0

for m in markets:
    outcome = m.get('outcome')
    
    if outcome is None:
        pending_count += 1
    else:
        resolved_count += 1
        if outcome in ['YES', 'Yes', 'yes', True, 'true', 1, 'True']:
            resolved_yes += 1
        elif outcome in ['NO', 'No', 'no', False, 'false', 0, 'False']:
            resolved_no += 1

print("[RESOLUTION STATUS]")
print(f"  Total markets: {len(markets)}")
print(f"  Resolved: {resolved_count} ({resolved_count/len(markets)*100:.1f}%)")
print(f"    YES: {resolved_yes}")
print(f"    NO: {resolved_no}")
print(f"  Pending: {pending_count} ({pending_count/len(markets)*100:.1f}%)")

# Find Musk markets that are resolved
print("\n[MUSK MARKETS]")
musk_markets = [m for m in markets if 'musk' in m.get('question', '').lower()]
musk_resolved = [m for m in musk_markets if m.get('outcome') is not None]

print(f"  Total Musk markets: {len(musk_markets)}")
print(f"  Resolved: {len(musk_resolved)}")

if musk_resolved:
    print(f"\n  Sample resolved Musk markets:")
    for m in musk_resolved[:5]:
        outcome = m.get('outcome')
        prices = m.get('price_history', [])
        initial_p = prices[0]['p'] if prices else 0
        max_p = max([p['p'] for p in prices]) if prices else 0
        
        print(f"    [{outcome}] {m['question'][:70]}")
        print(f"          Initial: {initial_p:.3f}, Max: {max_p:.3f}")

# Find high-confidence crypto markets (initial price >0.70)
print("\n[HIGH-CONFIDENCE CRYPTO]")
crypto_keywords = ['bitcoin', 'btc', 'solana', 'xrp', 'cardano', 'ethereum', 'eth']
high_conf_crypto = []

for m in markets:
    question = m.get('question', '').lower()
    
    # Check if crypto market
    if not any(kw in question for kw in crypto_keywords):
        continue
    
    # Check if resolved
    if m.get('outcome') is None:
        continue
    
    # Check price history
    prices = m.get('price_history', [])
    if not prices:
        continue
    
    initial_price = prices[0]['p']
    max_price = max([p['p'] for p in prices])
    
    # Check if ever >0.70 (strategy trigger)
    if max_price > 0.70:
        high_conf_crypto.append({
            'question': m['question'],
            'outcome': m.get('outcome'),
            'initial': initial_price,
            'max': max_price,
            'num_prices': len(prices)
        })

print(f"  Found {len(high_conf_crypto)} resolved crypto markets with price >70%")

if high_conf_crypto:
    print(f"\n  Top 10:")
    for i, m in enumerate(high_conf_crypto[:10], 1):
        result = "WIN" if m['outcome'] in ['NO', 'No', 'no', False, 'false', 0, 'False'] else "LOSS"
        print(f"    {i}. [{result}] {m['question'][:60]}")
        print(f"       Initial: {m['initial']:.3f}, Max: {m['max']:.3f}")

print(f"\n[DONE]")
