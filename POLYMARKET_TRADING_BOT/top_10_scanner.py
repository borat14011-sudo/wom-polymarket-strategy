#!/usr/bin/env python3
"""
POLYMARKET TOP 10 BETTING OPPORTUNITIES
Analyzes all active markets and ranks best bets
"""

import requests
import json
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

print("=" * 80)
print("POLYMARKET TOP 10 BETTING OPPORTUNITIES")
print(f"Scan Time: {datetime.now()}")
print("=" * 80)

# Get all active markets
response = requests.get(
    f"{GAMMA_API}/markets",
    params={"active": "true", "closed": "false", "limit": 500},
    timeout=30
)
markets = response.json()
print(f"\nTotal Active Markets: {len(markets)}")

# Filter and score opportunities
opportunities = []

for market in markets:
    try:
        volume = float(market.get('volume', 0))
        if volume < 100000:  # Minimum $100k volume
            continue
            
        best_bid = float(market.get('bestBid', 0))
        best_ask = float(market.get('bestAsk', 0))
        spread = best_ask - best_bid if best_ask > 0 and best_bid > 0 else 1
        
        question = market.get('question', '').lower()
        volume_24h = float(market.get('volume24hr', 0))
        liquidity = float(market.get('liquidity', 0))
        
        # Parse prices
        prices = []
        try:
            prices = [float(p) for p in json.loads(market.get('outcomePrices', '[]'))]
        except:
            pass
        
        # SCORING SYSTEM
        score = 0
        reasons = []
        recommendation = None
        bet_side = None
        
        # === STRATEGY 1: HIGH VOLUME LIQUIDITY ===
        if volume > 1000000:
            score += 2
            reasons.append("High volume")
        if liquidity > 100000:
            score += 1
            reasons.append("Good liquidity")
            
        # === STRATEGY 2: TIGHT SPREAD ===
        if spread < 0.01:
            score += 2
            reasons.append("Tight spread")
        elif spread < 0.05:
            score += 1
            reasons.append("Fair spread")
            
        # === STRATEGY 3: POLITICAL FADE (Trump/Elon) ===
        if 'trump' in question:
            # High YES prices on Trump = fade opportunity
            if best_ask > 0.85:
                score += 3
                reasons.append(f"Trump hype fade - YES at {best_ask:.0%}")
                recommendation = "BET NO"
                bet_side = "NO"
            elif best_bid < 0.15:
                score += 1
                reasons.append(f"Trump oversold - NO at {best_bid:.0%}")
                
        # === STRATEGY 4: ELON HYPE FADE ===
        if any(x in question for x in ['elon', 'musk', 'doge']):
            if best_ask > 0.80:
                score += 4
                reasons.append(f"Elon hype peak - YES at {best_ask:.0%}")
                recommendation = "BET NO"
                bet_side = "NO"
                
        # === STRATEGY 5: LONG-TERM TIME BIAS (BTC/MSTR) ===
        if any(x in question for x in ['bitcoin', 'btc', 'microstrategy', 'mstr']):
            # Long dated = time decay favors NO
            end_date = market.get('endDate', '')
            if '2025-12' in end_date or '2026' in end_date:
                if best_ask > 0.70:
                    score += 3
                    reasons.append(f"BTC long-term - time bias vs {best_ask:.0%} YES")
                    recommendation = "BET NO"
                    bet_side = "NO"
                    
        # === STRATEGY 6: EXTREME PRICES ===
        if best_ask > 0.95:
            score += 2
            reasons.append(f"Extreme YES price {best_ask:.0%}")
            if not recommendation:
                recommendation = "FADE - BET NO"
                bet_side = "NO"
        if best_bid < 0.05:
            score += 1
            reasons.append(f"Extreme NO price {best_bid:.0%}")
            
        # === STRATEGY 7: HIGH 24H ACTIVITY ===
        if volume_24h > 500000:
            score += 1
            reasons.append(f"Hot market - ${volume_24h:,.0f} 24h vol")
            
        # === STRATEGY 8: ENTERTAINMENT/GAMING FADES ===
        if any(x in question for x in ['gta', 'jesus', 'ceasefire']):
            if best_ask > 0.50:
                score += 1
                reasons.append("Entertainment speculation")
                if best_ask > 0.80 and not recommendation:
                    recommendation = "FADE - BET NO"
                    bet_side = "NO"
        
        # Must have a recommendation to be included
        if recommendation and score >= 5:
            opportunities.append({
                'question': market.get('question', 'Unknown'),
                'slug': market.get('marketSlug', market.get('slug', '')),
                'condition_id': market.get('conditionId', ''),
                'volume': volume,
                'volume_24h': volume_24h,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'spread': spread,
                'prices': prices,
                'score': score,
                'reasons': reasons,
                'recommendation': recommendation,
                'bet_side': bet_side,
                'end_date': market.get('endDate', 'Unknown')[:10],
                'token_ids': json.loads(market.get('clobTokenIds', '[]'))
            })
            
    except Exception as e:
        continue

# Sort by score descending
opportunities.sort(key=lambda x: x['score'], reverse=True)

print(f"High-Conviction Opportunities: {len(opportunities)}\n")

# Display TOP 10
print("=" * 80)
print("TOP 10 RECOMMENDED BETS (Ranked by Conviction)")
print("=" * 80)

for i, opp in enumerate(opportunities[:10], 1):
    print(f"\n{'='*80}")
    print(f"#{i} | CONVICTION: {opp['score']}/10")
    print(f"{'='*80}")
    print(f"Market: {opp['question']}")
    print(f"Action: {opp['recommendation']}")
    print(f"\nPrices:")
    print(f"  YES Ask: {opp['best_ask']:.3f}¢ | NO Bid: {opp['best_bid']:.3f}¢")
    print(f"  Spread: {opp['spread']:.3f}¢")
    if opp['prices']:
        print(f"  Implied: YES {opp['prices'][0]:.3f} | NO {opp['prices'][1]:.3f}")
    print(f"\nVolume: ${opp['volume']:,.0f} | 24h: ${opp['volume_24h']:,.0f}")
    print(f"Ends: {opp['end_date']}")
    print(f"\nWhy:")
    for reason in opp['reasons']:
        print(f"  • {reason}")
    print(f"\nLink: https://polymarket.com/event/{opp['slug']}")

# Also show ALL active markets summary
print("\n" + "=" * 80)
print("ALL ACTIVE MARKETS WITH TRADABLE VOLUME (>$100K)")
print("=" * 80)

all_active = []
for market in markets:
    try:
        volume = float(market.get('volume', 0))
        if volume >= 100000:
            best_bid = float(market.get('bestBid', 0))
            best_ask = float(market.get('bestAsk', 0))
            all_active.append({
                'question': market.get('question', 'Unknown'),
                'volume': volume,
                'bid': best_bid,
                'ask': best_ask,
                'slug': market.get('marketSlug', '')
            })
    except:
        continue

all_active.sort(key=lambda x: x['volume'], reverse=True)

for i, m in enumerate(all_active, 1):
    print(f"\n{i}. {m['question'][:65]}...")
    print(f"   Vol: ${m['volume']:,.0f} | Bid: {m['bid']:.3f} | Ask: {m['ask']:.3f}")

# Save to file
output = {
    'timestamp': datetime.now().isoformat(),
    'top_10_opportunities': opportunities[:10],
    'all_active_markets': all_active,
    'total_active': len(all_active)
}

with open('top_10_bets.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\n{'='*80}")
print("Saved to: top_10_bets.json")
print(f"Total markets analyzed: {len(all_active)}")
print("="*80)
