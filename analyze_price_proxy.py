#!/usr/bin/env python3
"""
PRICE-AS-PROXY VALIDATOR
Analyzes whether final prices are reliable outcome proxies for Polymarket markets
"""

import json
import random
from collections import defaultdict
from datetime import datetime

# Load dataset
print("Loading dataset...")
with open('polymarket-monitor/historical-data-scraper/data/backtest_dataset_v1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

markets = data if isinstance(data, list) else data.get('markets', [])
total_markets = len(markets)
print(f"Total markets: {total_markets:,}")

# Analyze final prices and outcomes
decisive_threshold_high = 0.95
decisive_threshold_low = 0.05

decisive_yes = []  # >0.95
decisive_no = []   # <0.05
indecisive = []    # between 0.05 and 0.95
no_price_history = []

for market in markets:
    price_history = market.get('price_history', [])
    
    if not price_history:
        no_price_history.append(market)
        continue
    
    # Get final price (last entry in price history)
    final_price = price_history[-1].get('p')
    market['final_price'] = final_price  # Add for convenience
    
    if final_price is None:
        no_price_history.append(market)
    elif final_price > decisive_threshold_high:
        decisive_yes.append(market)
    elif final_price < decisive_threshold_low:
        decisive_no.append(market)
    else:
        indecisive.append(market)

# Statistics
total_decisive = len(decisive_yes) + len(decisive_no)
pct_decisive = (total_decisive / total_markets * 100) if total_markets > 0 else 0
pct_decisive_yes = (len(decisive_yes) / total_markets * 100) if total_markets > 0 else 0
pct_decisive_no = (len(decisive_no) / total_markets * 100) if total_markets > 0 else 0
pct_indecisive = (len(indecisive) / total_markets * 100) if total_markets > 0 else 0
pct_no_price = (len(no_price_history) / total_markets * 100) if total_markets > 0 else 0

print("\n" + "="*70)
print("FINAL PRICE DISTRIBUTION")
print("="*70)
print(f"Decisive YES (>0.95):     {len(decisive_yes):,} ({pct_decisive_yes:.2f}%)")
print(f"Decisive NO (<0.05):      {len(decisive_no):,} ({pct_decisive_no:.2f}%)")
print(f"TOTAL DECISIVE:           {total_decisive:,} ({pct_decisive:.2f}%)")
print(f"Indecisive (0.05-0.95):   {len(indecisive):,} ({pct_indecisive:.2f}%)")
print(f"No price history:         {len(no_price_history):,} ({pct_no_price:.2f}%)")

# Outcome analysis for decisive markets
outcomes_known = 0
outcomes_unknown = 0
for market in decisive_yes + decisive_no:
    if market.get('outcome') is not None:
        outcomes_known += 1
    else:
        outcomes_unknown += 1

print(f"\nOf {total_decisive:,} decisive markets:")
print(f"  With known outcome: {outcomes_known:,} ({outcomes_known/total_decisive*100:.2f}%)")
print(f"  Without outcome:    {outcomes_unknown:,} ({outcomes_unknown/total_decisive*100:.2f}%)")

# Select 20 random decisive markets for manual verification
verification_sample = []
if len(decisive_yes) >= 10 and len(decisive_no) >= 10:
    verification_sample = random.sample(decisive_yes, 10) + random.sample(decisive_no, 10)
elif total_decisive >= 20:
    verification_sample = random.sample(decisive_yes + decisive_no, 20)
else:
    verification_sample = decisive_yes + decisive_no

print("\n" + "="*70)
print("RANDOM SAMPLE FOR MANUAL VERIFICATION (20 markets)")
print("="*70)

verification_data = []
for i, market in enumerate(verification_sample[:20], 1):
    market_id = market.get('market_id', 'unknown')
    event_id = market.get('event_id', 'unknown')
    question = market.get('question', 'No question')
    final_price = market.get('final_price', 'N/A')
    outcome = market.get('outcome')
    
    # Polymarket URL - try different formats
    url = f"https://polymarket.com/event/{event_id}"
    
    predicted = 'YES' if final_price > 0.95 else 'NO'
    
    verification_data.append({
        'event_id': event_id,
        'market_id': market_id,
        'question': question,
        'final_price': final_price,
        'predicted_outcome': predicted,
        'actual_outcome': outcome,
        'url': url
    })
    
    outcome_str = f"Actual: {outcome}" if outcome else "Actual: UNKNOWN"
    print(f"\n{i}. {question[:70]}")
    print(f"   Final Price: {final_price:.4f} -> Predicted: {predicted}")
    print(f"   {outcome_str}")
    print(f"   URL: {url}")

# Save verification sample to file
with open('verification_sample.json', 'w', encoding='utf-8') as f:
    json.dump(verification_data, f, indent=2)
print(f"\n[OK] Verification sample saved to verification_sample.json")

# Price distribution analysis
print("\n" + "="*70)
print("DETAILED PRICE DISTRIBUTION")
print("="*70)

price_buckets = defaultdict(int)
for market in markets:
    price_history = market.get('price_history', [])
    if price_history:
        final_price = price_history[-1].get('p')
        if final_price is not None:
            bucket = int(final_price * 10) / 10  # Round to nearest 0.1
            price_buckets[bucket] += 1

for bucket in sorted(price_buckets.keys()):
    count = price_buckets[bucket]
    pct = (count / total_markets * 100)
    bar = "#" * min(int(pct), 50)
    print(f"{bucket:.1f}-{bucket+0.1:.1f}: {count:5,} ({pct:5.2f}%) {bar}")

# Summary statistics
print("\n" + "="*70)
print("SUMMARY & RECOMMENDATIONS")
print("="*70)
print(f"Usable markets (decisive): {total_decisive:,} / {total_markets:,} ({pct_decisive:.2f}%)")
print(f"\nTheory: Markets >0.95 = YES won, <0.05 = NO won")
print(f"Finding: {pct_decisive:.1f}% of markets have decisive final prices")
print(f"\nNext step: Manually verify the 20 markets above on Polymarket")
print(f"Expected: If price-as-proxy works, predicted outcomes should match actual")
print(f"\nNote: Confidence interval calculation requires manual verification results.")
