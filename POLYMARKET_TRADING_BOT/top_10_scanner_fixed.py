#!/usr/bin/env python3
"""
POLYMARKET TOP 10 BETTING OPPORTUNITIES - FIXED VERSION
Accurately displays YES/NO prices and betting recommendations
"""

import requests
import json
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

print("=" * 80)
print("POLYMARKET TOP 10 BETTING OPPORTUNITIES (FIXED)")
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
        
        question = market.get('question', '')
        question_lower = question.lower()
        volume_24h = float(market.get('volume24hr', 0))
        liquidity = float(market.get('liquidity', 0))
        
        # Parse outcome prices - index 0 is YES, index 1 is NO
        yes_price = None
        no_price = None
        try:
            prices = json.loads(market.get('outcomePrices', '[]'))
            if len(prices) >= 2:
                yes_price = float(prices[0])
                no_price = float(prices[1])
        except:
            pass
        
        # Use outcome prices if available, otherwise use bestBid/bestAsk
        if yes_price is None:
            yes_price = best_ask
        if no_price is None:
            no_price = 1.0 - yes_price  # Estimate
        
        # SCORING SYSTEM
        score = 0
        reasons = []
        recommendation = None
        bet_side = None
        entry_price = None
        potential_profit = None
        
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
        if 'trump' in question_lower:
            # High YES prices on Trump = fade opportunity
            if yes_price > 0.85:
                score += 3
                reasons.append(f"Trump YES overpriced at {yes_price:.1%}")
                recommendation = "BET NO"
                bet_side = "NO"
                entry_price = no_price
                potential_profit = yes_price  # If NO wins, you win the YES price
            elif no_price > 0.85:
                score += 1
                reasons.append(f"Trump NO overpriced at {no_price:.1%}")
                
        # === STRATEGY 4: ELON HYPE FADE ===
        if any(x in question_lower for x in ['elon', 'musk', 'doge']):
            if yes_price > 0.80:
                score += 4
                reasons.append(f"Elon YES overpriced at {yes_price:.1%}")
                recommendation = "BET NO"
                bet_side = "NO"
                entry_price = no_price
                potential_profit = yes_price
            elif no_price > 0.80:
                score += 2
                reasons.append(f"Elon NO overpriced at {no_price:.1%}")
                recommendation = "BET YES"
                bet_side = "YES"
                entry_price = yes_price
                potential_profit = no_price
                
        # === STRATEGY 5: LONG-TERM TIME BIAS (BTC/MSTR) ===
        if any(x in question_lower for x in ['bitcoin', 'btc', 'microstrategy', 'mstr']):
            end_date = market.get('endDate', '')
            if '2025-12' in end_date or '2026' in end_date:
                if yes_price > 0.70:
                    score += 3
                    reasons.append(f"BTC long-term YES at {yes_price:.1%} - time decay")
                    recommendation = "BET NO"
                    bet_side = "NO"
                    entry_price = no_price
                    potential_profit = yes_price
                    
        # === STRATEGY 6: EXTREME PRICES ===
        if yes_price > 0.95:
            score += 2
            reasons.append(f"Extreme YES price {yes_price:.1%}")
            if not recommendation:
                recommendation = "FADE - BET NO"
                bet_side = "NO"
                entry_price = no_price
                potential_profit = yes_price
        if no_price > 0.95:
            score += 2
            reasons.append(f"Extreme NO price {no_price:.1%}")
            if not recommendation:
                recommendation = "FADE - BET YES"
                bet_side = "YES"
                entry_price = yes_price
                potential_profit = no_price
            
        # === STRATEGY 7: HIGH 24H ACTIVITY ===
        if volume_24h > 500000:
            score += 1
            reasons.append(f"Hot market - ${volume_24h:,.0f} 24h vol")
            
        # === STRATEGY 8: ENTERTAINMENT/GAMING FADES ===
        if any(x in question_lower for x in ['gta', 'jesus', 'ceasefire']):
            if yes_price > 0.50:
                score += 1
                reasons.append("Entertainment speculation")
                if yes_price > 0.80 and not recommendation:
                    recommendation = "FADE - BET NO"
                    bet_side = "NO"
                    entry_price = no_price
                    potential_profit = yes_price
        
        # Must have a recommendation to be included
        if recommendation and score >= 5:
            opportunities.append({
                'question': question,
                'slug': market.get('marketSlug', market.get('slug', '')),
                'condition_id': market.get('conditionId', ''),
                'volume': volume,
                'volume_24h': volume_24h,
                'yes_price': yes_price,
                'no_price': no_price,
                'spread': spread,
                'score': score,
                'reasons': reasons,
                'recommendation': recommendation,
                'bet_side': bet_side,
                'entry_price': entry_price,
                'potential_profit': potential_profit,
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
    print(f"\nCURRENT PRICES:")
    print(f"  YES: {opp['yes_price']:.3f}¢ (${opp['yes_price']:.2f})")
    print(f"  NO:  {opp['no_price']:.3f}¢ (${opp['no_price']:.2f})")
    print(f"  Spread: {opp['spread']:.3f}¢")
    print(f"\nRECOMMENDATION: {opp['recommendation']}")
    print(f"  Entry Price: {opp['entry_price']:.3f}¢")
    print(f"  If Correct, Win: {opp['potential_profit']:.3f}¢ (+{(opp['potential_profit']/opp['entry_price']*100):.0f}%)")
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
            yes_p = None
            no_p = None
            try:
                prices = json.loads(market.get('outcomePrices', '[]'))
                if len(prices) >= 2:
                    yes_p = float(prices[0])
                    no_p = float(prices[1])
            except:
                pass
            
            if yes_p is None:
                yes_p = float(market.get('bestAsk', 0))
            if no_p is None:
                no_p = 1.0 - yes_p
                
            all_active.append({
                'question': market.get('question', 'Unknown'),
                'volume': volume,
                'yes': yes_p,
                'no': no_p,
                'slug': market.get('marketSlug', '')
            })
    except:
        continue

all_active.sort(key=lambda x: x['volume'], reverse=True)

for i, m in enumerate(all_active[:50], 1):  # Show top 50
    print(f"\n{i}. {m['question'][:65]}...")
    print(f"   Vol: ${m['volume']:,.0f} | YES: {m['yes']:.3f} | NO: {m['no']:.3f}")

# Save to file
output = {
    'timestamp': datetime.now().isoformat(),
    'top_10_opportunities': opportunities[:10],
    'all_active_markets': all_active[:100],
    'total_active': len(all_active)
}

with open('top_10_bets_fixed.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\n{'='*80}")
print("Saved to: top_10_bets_fixed.json")
print(f"Total markets analyzed: {len(all_active)}")
print("="*80)
