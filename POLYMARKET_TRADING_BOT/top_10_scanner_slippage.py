#!/usr/bin/env python3
"""
POLYMARKET TOP 10 BETTING OPPORTUNITIES - WITH 3% SLIPPAGE
Only shows bets that are profitable after transaction costs
"""

import requests
import json
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com"
SLIPPAGE = 0.03  # 3% transaction cost

print("=" * 80)
print("POLYMARKET TOP 10 - ACCOUNTING FOR 3% SLIPPAGE")
print(f"Scan Time: {datetime.now()}")
print(f"Transaction Cost: {SLIPPAGE:.1%}")
print("=" * 80)

# Get all active markets
response = requests.get(
    f"{GAMMA_API}/markets",
    params={"active": "true", "closed": "false", "limit": 500},
    timeout=30
)
markets = response.json()
print(f"\nTotal Active Markets: {len(markets)}")

opportunities = []

for market in markets:
    try:
        volume = float(market.get('volume', 0))
        if volume < 100000:
            continue
            
        best_bid = float(market.get('bestBid', 0))
        best_ask = float(market.get('bestAsk', 0))
        spread = best_ask - best_bid if best_ask > 0 and best_bid > 0 else 1
        
        question = market.get('question', '')
        question_lower = question.lower()
        volume_24h = float(market.get('volume24hr', 0))
        liquidity = float(market.get('liquidity', 0))
        
        # Parse outcome prices
        yes_price = None
        no_price = None
        try:
            prices = json.loads(market.get('outcomePrices', '[]'))
            if len(prices) >= 2:
                yes_price = float(prices[0])
                no_price = float(prices[1])
        except:
            pass
        
        if yes_price is None:
            yes_price = best_ask
        if no_price is None:
            no_price = 1.0 - yes_price
        
        # Calculate REAL costs after slippage
        # If betting YES, you pay yes_price + slippage
        # If betting NO, you pay no_price + slippage
        yes_cost = yes_price + SLIPPAGE
        no_cost = no_price + SLIPPAGE
        
        # Profit if win $1
        yes_profit = 1.0 - yes_cost
        no_profit = 1.0 - no_cost
        
        # ROI after slippage
        yes_roi = yes_profit / yes_cost if yes_cost > 0 else -1
        no_roi = no_profit / no_cost if no_cost > 0 else -1
        
        score = 0
        reasons = []
        recommendation = None
        bet_side = None
        entry_cost = None
        net_profit = None
        net_roi = None
        
        # === STRATEGY: ONLY BET WHERE EDGE > SLIPPAGE ===
        
        # High volume = liquid
        if volume > 1000000:
            score += 1
            reasons.append(f"High volume ${volume:,.0f}")
        
        # Tight spread
        if spread < 0.01:
            score += 1
            reasons.append("Tight spread")
        
        # === POLITICAL FADES (Trump/Elon) ===
        if 'trump' in question_lower:
            if yes_price > 0.90 and no_cost < 0.85:  # Must be profitable after fees
                score += 3
                reasons.append(f"Trump YES at {yes_price:.1%} - fade after {SLIPPAGE:.0%} fees")
                recommendation = "BET NO"
                bet_side = "NO"
                entry_cost = no_cost
                net_profit = no_profit
                net_roi = no_roi
            elif no_price > 0.90 and yes_cost < 0.85:
                score += 2
                reasons.append(f"Trump NO overpriced")
                recommendation = "BET YES"
                bet_side = "YES"
                entry_cost = yes_cost
                net_profit = yes_profit
                net_roi = yes_roi
                
        # === ELON FADES ===
        if any(x in question_lower for x in ['elon', 'musk', 'doge']):
            if yes_price > 0.80 and no_cost < 0.80:
                score += 3
                reasons.append(f"Elon YES {yes_price:.1%} - fade, net profit {no_profit:.1%}")
                recommendation = "BET NO"
                bet_side = "NO"
                entry_cost = no_cost
                net_profit = no_profit
                net_roi = no_roi
            elif no_price > 0.95 and yes_cost < 0.80:  # Must have real edge
                score += 2
                reasons.append(f"Elon NO {no_price:.1%} - possible YES value")
                recommendation = "BET YES"
                bet_side = "YES"
                entry_cost = yes_cost
                net_profit = yes_profit
                net_roi = yes_roi
                
        # === BTC LONG-TERM TIME BIAS ===
        if any(x in question_lower for x in ['bitcoin', 'btc', 'microstrategy', 'mstr']):
            end_date = market.get('endDate', '')
            if '2025-12' in end_date or '2026' in end_date:
                if yes_price > 0.70 and no_cost < 0.80:
                    score += 3
                    reasons.append(f"BTC long-dated YES {yes_price:.1%} - time decay")
                    recommendation = "BET NO"
                    bet_side = "NO"
                    entry_cost = no_cost
                    net_profit = no_profit
                    net_roi = no_roi
                    
        # === EXTREME PRICES - ONLY IF PROFITABLE ===
        if yes_price > 0.95 and no_cost < 0.90:
            score += 2
            reasons.append(f"Extreme YES {yes_price:.1%}")
            if not recommendation and no_roi > 0.10:  # At least 10% profit after fees
                recommendation = "FADE - BET NO"
                bet_side = "NO"
                entry_cost = no_cost
                net_profit = no_profit
                net_roi = no_roi
                
        if no_price > 0.95 and yes_cost < 0.90:
            score += 2
            reasons.append(f"Extreme NO {no_price:.1%}")
            if not recommendation and yes_roi > 0.10:
                recommendation = "FADE - BET YES"
                bet_side = "YES"
                entry_cost = yes_cost
                net_profit = yes_profit
                net_roi = yes_roi
        
        # Hot market
        if volume_24h > 500000:
            score += 1
            reasons.append(f"Hot ${volume_24h:,.0f} 24h")
        
        # Only include if profitable after slippage
        if recommendation and score >= 5 and net_roi and net_roi > 0.05:
            opportunities.append({
                'question': question,
                'slug': market.get('marketSlug', market.get('slug', '')),
                'condition_id': market.get('conditionId', ''),
                'volume': volume,
                'volume_24h': volume_24h,
                'yes_price': yes_price,
                'no_price': no_price,
                'yes_cost': yes_cost,
                'no_cost': no_cost,
                'spread': spread,
                'score': score,
                'reasons': reasons,
                'recommendation': recommendation,
                'bet_side': bet_side,
                'entry_cost': entry_cost,
                'net_profit': net_profit,
                'net_roi': net_roi,
                'end_date': market.get('endDate', 'Unknown')[:10],
                'token_ids': json.loads(market.get('clobTokenIds', '[]'))
            })
            
    except Exception as e:
        continue

opportunities.sort(key=lambda x: x['net_roi'], reverse=True)

print(f"Profitable Opportunities (after {SLIPPAGE:.0%} fees): {len(opportunities)}\n")

print("=" * 80)
print("TOP 10 BETS - PROFITABLE AFTER 3% SLIPPAGE")
print("=" * 80)

for i, opp in enumerate(opportunities[:10], 1):
    print(f"\n{'='*80}")
    print(f"#{i} | CONVICTION: {opp['score']}/10 | NET ROI: {opp['net_roi']:+.1%}")
    print(f"{'='*80}")
    print(f"Market: {opp['question']}")
    print(f"\nMARKET PRICES:")
    print(f"  YES: {opp['yes_price']:.3f}¢ (${opp['yes_price']:.2f})")
    print(f"  NO:  {opp['no_price']:.3f}¢ (${opp['no_price']:.2f})")
    print(f"\nAFTER {SLIPPAGE:.0%} SLIPPAGE:")
    if opp['bet_side'] == 'YES':
        print(f"  Cost to enter: {opp['yes_cost']:.3f}¢ (was {opp['yes_price']:.3f}¢)")
    else:
        print(f"  Cost to enter: {opp['no_cost']:.3f}¢ (was {opp['no_price']:.3f}¢)")
    print(f"\nRECOMMENDATION: {opp['recommendation']}")
    print(f"  Net Profit if Win: ${opp['net_profit']:.3f}")
    print(f"  Net ROI: {opp['net_roi']:+.1%}")
    print(f"\nVolume: ${opp['volume']:,.0f} | 24h: ${opp['volume_24h']:,.0f}")
    print(f"Ends: {opp['end_date']}")
    print(f"\nWhy:")
    for reason in opp['reasons']:
        print(f"  • {reason}")
    print(f"\nLink: https://polymarket.com/event/{opp['slug']}")

# Also show what we EXCLUDED
print("\n" + "=" * 80)
print("EXCLUDED BETS (Not Profitable After 3% Fees)")
print("=" * 80)

excluded = []
for market in markets[:100]:  # Check first 100
    try:
        volume = float(market.get('volume', 0))
        if volume < 100000:
            continue
            
        prices = json.loads(market.get('outcomePrices', '[]'))
        if len(prices) >= 2:
            yes_p = float(prices[0])
            no_p = float(prices[1])
            
            # Would have been a recommendation but fees kill it
            if yes_p < 0.05 or no_p < 0.05:
                side = "YES" if yes_p < 0.05 else "NO"
                price = yes_p if yes_p < 0.05 else no_p
                cost = price + SLIPPAGE
                
                if cost > 0.95:  # Not profitable
                    excluded.append({
                        'q': market.get('question', '')[:50],
                        'side': side,
                        'price': price,
                        'cost': cost,
                        'profit': 1 - cost
                    })
    except:
        continue

excluded.sort(key=lambda x: x['price'])

print("\nThese look tempting but 3% fees make them unprofitable:")
for e in excluded[:10]:
    status = "❌ LOSS" if e['profit'] < 0 else "⚠️ THIN"
    print(f"  {status} {e['side']} @ {e['price']:.1%} → costs {e['cost']:.1%} → profit ${e['profit']:.2f}")
    print(f"       {e['q']}...")

print(f"\n{'='*80}")
print(f"SUMMARY: {len(opportunities)} profitable bets found")
print(f"File saved: top_10_bets_slippage.json")
print("="*80)

# Save
output = {
    'timestamp': datetime.now().isoformat(),
    'slippage': SLIPPAGE,
    'profitable_bets': opportunities[:10],
    'excluded_count': len(excluded)
}

with open('top_10_bets_slippage.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)
