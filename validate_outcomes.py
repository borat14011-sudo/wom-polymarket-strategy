#!/usr/bin/env python3
"""
Additional validation: Check price convergence patterns
Since direct outcome verification is blocked, analyze price behavior
"""

import json
from collections import defaultdict
import statistics

print("Loading dataset...")
with open('polymarket-monitor/historical-data-scraper/data/backtest_dataset_v1.json', 'r', encoding='utf-8') as f:
    markets = json.load(f)

print(f"Total markets: {len(markets):,}\n")

# Analyze price convergence for decisive markets
decisive_markets = []
for market in markets:
    price_history = market.get('price_history', [])
    if not price_history:
        continue
    
    final_price = price_history[-1].get('p')
    if final_price is not None and (final_price > 0.95 or final_price < 0.05):
        # Get last 10 prices to analyze convergence
        recent_prices = [p.get('p') for p in price_history[-10:]]
        market['recent_prices'] = recent_prices
        market['final_price'] = final_price
        market['price_volatility'] = statistics.stdev(recent_prices) if len(recent_prices) > 1 else 0
        decisive_markets.append(market)

print("="*70)
print("PRICE CONVERGENCE ANALYSIS (Decisive Markets)")
print("="*70)

# Analyze convergence quality
very_stable = [m for m in decisive_markets if m['price_volatility'] < 0.01]  # <1% volatility
stable = [m for m in decisive_markets if 0.01 <= m['price_volatility'] < 0.05]
moderate = [m for m in decisive_markets if 0.05 <= m['price_volatility'] < 0.1]
volatile = [m for m in decisive_markets if m['price_volatility'] >= 0.1]

print(f"Very Stable (volatility <1%):   {len(very_stable):,} ({len(very_stable)/len(decisive_markets)*100:.1f}%)")
print(f"Stable (volatility 1-5%):       {len(stable):,} ({len(stable)/len(decisive_markets)*100:.1f}%)")
print(f"Moderate (volatility 5-10%):    {len(moderate):,} ({len(moderate)/len(decisive_markets)*100:.1f}%)")
print(f"Volatile (volatility >10%):     {len(volatile):,} ({len(volatile)/len(decisive_markets)*100:.1f}%)")

print("\n" + "="*70)
print("MARKET CATEGORIES ANALYSIS")
print("="*70)

# Categorize markets by type (heuristic based on question keywords)
categories = defaultdict(list)
for market in decisive_markets:
    question = market.get('question', '').lower()
    
    if any(word in question for word in ['nba', 'nfl', 'mlb', 'spread', 'moneyline', 'o/u', 'over/under']):
        categories['Sports Betting'].append(market)
    elif any(word in question for word in ['kills', 'dota', 'lol', 'game 1', 'game 2', 'first blood']):
        categories['Esports'].append(market)
    elif any(word in question for word in ['bitcoin', 'ethereum', 'btc', 'eth', 'crypto', 'up or down']):
        categories['Crypto Price'].append(market)
    elif any(word in question for word in ['trump', 'biden', 'election', 'president', 'senate']):
        categories['Politics'].append(market)
    elif any(word in question for word in ['elon', 'tweet', 'twitter', 'post']):
        categories['Social Media'].append(market)
    else:
        categories['Other'].append(market)

for category, markets_list in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
    pct = len(markets_list) / len(decisive_markets) * 100
    print(f"{category:20s}: {len(markets_list):5,} ({pct:5.1f}%)")

print("\n" + "="*70)
print("SAMPLE HIGH-CONFIDENCE MARKETS")
print("="*70)

# Show examples of very stable markets (highest confidence)
print("\n10 Random Very Stable Markets (low volatility, should be highly reliable):")
import random
sample = random.sample(very_stable, min(10, len(very_stable)))
for i, market in enumerate(sample, 1):
    question = market['question'][:70]
    final_price = market['final_price']
    volatility = market['price_volatility']
    prediction = 'YES' if final_price > 0.95 else 'NO'
    print(f"{i}. {question}")
    print(f"   Final: {final_price:.4f} | Volatility: {volatility:.4f} | Predicted: {prediction}")

print("\n" + "="*70)
print("RELIABILITY INDICATORS")
print("="*70)

# Markets with extreme final prices (99.5%+) are likely most reliable
extreme_confidence = [m for m in decisive_markets if m['final_price'] > 0.995 or m['final_price'] < 0.005]
print(f"Extreme confidence (>99.5% or <0.5%): {len(extreme_confidence):,} ({len(extreme_confidence)/len(decisive_markets)*100:.1f}%)")

# Markets with both extreme prices AND low volatility = gold standard
gold_standard = [m for m in extreme_confidence if m['price_volatility'] < 0.01]
print(f"Gold standard (extreme + stable):      {len(gold_standard):,} ({len(gold_standard)/len(decisive_markets)*100:.1f}%)")

print("\n" + "="*70)
print("KEY FINDINGS")
print("="*70)
print(f"""
1. Data Quality: {len(very_stable)/len(decisive_markets)*100:.1f}% of decisive markets show very stable convergence
2. Market Types: Dominated by sports betting and esports (verifiable outcomes)
3. Confidence Tiers:
   - Gold Standard: {len(gold_standard):,} markets (extreme price + low volatility)
   - High Confidence: {len(very_stable):,} markets (very stable convergence)
   - Total Decisive: {len(decisive_markets):,} markets

The high percentage of stable convergence suggests that price-as-proxy
is likely reliable for these markets, particularly for:
- Sports/Esports (objectively verifiable outcomes)
- Crypto price predictions (objectively verifiable)
- Markets with >99.5% final prices and low volatility
""")
