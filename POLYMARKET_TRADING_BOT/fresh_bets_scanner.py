#!/usr/bin/env python3
"""
Fresh Bet Scanner - Find 10 New Opportunities
"""

import requests
import json
from datetime import datetime

base_url = "https://gamma-api.polymarket.com"

print("=" * 70)
print("FRESH BET SCANNER - Top 10 Opportunities")
print("=" * 70)
print(f"Scan Time: {datetime.now()}\n")

# Get active markets
try:
    response = requests.get(
        f"{base_url}/markets",
        params={
            "active": True,
            "closed": False,
            "limit": 200
        },
        timeout=30
    )
    markets = response.json()
    print(f"Markets Analyzed: {len(markets)}\n")
    
except Exception as e:
    print(f"Error: {e}")
    markets = []

opportunities = []

for market in markets:
    try:
        question = market.get('question', '').lower()
        volume = float(market.get('volume', 0))
        best_bid = float(market.get('bestBid', 0))
        best_ask = float(market.get('bestAsk', 0))
        
        if volume < 50000:  # Skip low volume
            continue
            
        score = 0
        reasons = []
        
        # High volume = liquid
        if volume > 500000:
            score += 2
            reasons.append(f"High volume: ${volume:,.0f}")
        elif volume > 100000:
            score += 1
            reasons.append(f"Good volume: ${volume:,.0f}")
        
        # Tight spread
        if best_ask > 0 and best_bid > 0:
            spread = best_ask - best_bid
            if spread < 0.02:
                score += 2
                reasons.append("Tight spread")
            elif spread < 0.05:
                score += 1
                reasons.append("Moderate spread")
        
        # Strategy matches
        if 'trump' in question or 'biden' in question:
            score += 2
            reasons.append("Political - fade opportunity")
        
        if 'elon' in question or 'musk' in question or 'twitter' in question:
            score += 3
            reasons.append("Elon hype - strong fade")
        
        if 'bitcoin' in question or 'btc' in question or 'crypto' in question:
            score += 1
            reasons.append("Crypto market")
        
        if 'microstrategy' in question or 'mstr' in question:
            score += 2
            reasons.append("MSTR time bias")
        
        # Fade opportunities (high YES prices)
        if best_ask > 0.95:
            score += 2
            reasons.append(f"High YES price ({best_ask:.0%}) - fade candidate")
        
        if best_bid < 0.10:
            score += 1
            reasons.append(f"Low NO price ({best_bid:.0%}) - value?")
        
        if score >= 4:
            opportunities.append({
                'market': market,
                'score': score,
                'reasons': reasons
            })
            
    except Exception as e:
        continue

# Sort by score
opportunities.sort(key=lambda x: x['score'], reverse=True)

print(f"Found {len(opportunities)} opportunities (score >= 4)\n")
print("=" * 70)
print("TOP 10 FRESH BETS")
print("=" * 70)

for i, opp in enumerate(opportunities[:10], 1):
    market = opp['market']
    question = market.get('question', 'Unknown')[:70]
    volume = float(market.get('volume', 0))
    best_bid = float(market.get('bestBid', 0))
    best_ask = float(market.get('bestAsk', 0))
    end_date = market.get('endDate', 'Unknown')[:10]
    slug = market.get('marketSlug', market.get('slug', ''))
    
    print(f"\n{i}. {question}...")
    print(f"   Score: {opp['score']}/10 | Volume: ${volume:,.0f}")
    print(f"   Prices: Bid {best_bid:.2f}¢ / Ask {best_ask:.2f}¢")
    print(f"   Ends: {end_date}")
    print(f"   Why:")
    for reason in opp['reasons']:
        print(f"     • {reason}")
    if slug:
        print(f"   Link: https://polymarket.com/event/{slug}")
    print(f"   {'='*70}")

# Save to file
with open('FRESH_BETS_TOP10.json', 'w') as f:
    json.dump(opportunities[:10], f, indent=2)

print(f"\n✅ Saved top 10 to FRESH_BETS_TOP10.json")
