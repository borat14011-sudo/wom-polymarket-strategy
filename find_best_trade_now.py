#!/usr/bin/env python3
"""
Find best trade opportunities from latest Polymarket data
Based on Wom's preferred strategies:
1. Near-certainties not priced in (95%+ true prob at 70-85% price)
2. Hype fade (bet NO on spike-driven markets)
"""

import json
import os
from datetime import datetime, timezone

def load_markets():
    """Load latest Polymarket data"""
    with open('polymarket_latest.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('markets', [])

def parse_price(price_str):
    """Parse price string to float"""
    try:
        return float(price_str)
    except:
        return 0.0

def analyze_markets(markets):
    """Analyze markets for best opportunities"""
    opportunities = []
    
    for market in markets:
        try:
            # Extract key data
            question = market.get('question', '')
            slug = market.get('slug', '')
            outcome_prices = market.get('outcomePrices', [])
            
            if not outcome_prices or len(outcome_prices) < 2:
                continue
                
            # Parse YES price (first element)
            yes_price = parse_price(outcome_prices[0])
            no_price = parse_price(outcome_prices[1]) if len(outcome_prices) > 1 else 1.0 - yes_price
            
            volume = float(market.get('volume', '0'))
            liquidity = float(market.get('liquidity', '0'))
            end_date = market.get('endDate', '')
            
            # Strategy 1: Near-certainties not priced in
            # Look for YES prices in 70-85% range where true probability is likely >95%
            if 0.70 <= yes_price <= 0.85:
                # Calculate edge assuming 95% true probability
                true_prob = 0.95
                expected_value = (true_prob * 1.0) - yes_price
                edge_percentage = (expected_value / yes_price) * 100
                
                if edge_percentage > 10:  # At least 10% edge
                    opportunities.append({
                        'type': 'NEAR_CERTAINTY',
                        'question': question,
                        'slug': slug,
                        'yes_price': yes_price,
                        'no_price': no_price,
                        'edge_percentage': edge_percentage,
                        'expected_value': expected_value,
                        'volume': volume,
                        'liquidity': liquidity,
                        'end_date': end_date,
                        'action': 'BUY YES',
                        'reason': f'95% true probability vs {yes_price*100:.1f}% price = {edge_percentage:.1f}% edge'
                    })
            
            # Strategy 2: Hype fade (bet NO on overhyped markets)
            # Look for YES prices >85% where market is overconfident
            if yes_price > 0.85:
                # Assume true probability is lower (hype fade)
                true_prob = 0.70  # Conservative estimate
                expected_value = ((1 - true_prob) * 1.0) - no_price
                edge_percentage = (expected_value / no_price) * 100
                
                if edge_percentage > 15:  # Higher threshold for hype fade
                    opportunities.append({
                        'type': 'HYPE_FADE',
                        'question': question,
                        'slug': slug,
                        'yes_price': yes_price,
                        'no_price': no_price,
                        'edge_percentage': edge_percentage,
                        'expected_value': expected_value,
                        'volume': volume,
                        'liquidity': liquidity,
                        'end_date': end_date,
                        'action': 'BUY NO',
                        'reason': f'Hype fade: Market at {yes_price*100:.1f}% YES, likely overconfident. {edge_percentage:.1f}% edge on NO'
                    })
                    
            # Strategy 3: Longshots (bet YES on underpriced markets)
            # Look for YES prices <30% where true probability is higher
            if yes_price < 0.30:
                # Assume true probability is higher
                true_prob = 0.50  # Conservative estimate
                expected_value = (true_prob * 1.0) - yes_price
                edge_percentage = (expected_value / yes_price) * 100
                
                if edge_percentage > 50:  # High threshold for longshots
                    opportunities.append({
                        'type': 'LONGSHOT',
                        'question': question,
                        'slug': slug,
                        'yes_price': yes_price,
                        'no_price': no_price,
                        'edge_percentage': edge_percentage,
                        'expected_value': expected_value,
                        'volume': volume,
                        'liquidity': liquidity,
                        'end_date': end_date,
                        'action': 'BUY YES',
                        'reason': f'Longshot: Market at {yes_price*100:.1f}% YES, likely underpriced. {edge_percentage:.1f}% edge'
                    })
                    
        except Exception as e:
            continue
    
    # Sort by edge percentage (highest first)
    opportunities.sort(key=lambda x: x['edge_percentage'], reverse=True)
    return opportunities

def main():
    print("="*80)
    print("POLYMARKET TRADE OPPORTUNITY SCANNER")
    print("="*80)
    print(f"Scan time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # Load markets
    print("Loading latest Polymarket data...")
    markets = load_markets()
    print(f"Loaded {len(markets)} markets")
    
    if len(markets) < 5:
        print(f"⚠️ Warning: Only {len(markets)} markets loaded. Data may be stale.")
        print("Consider fetching fresh data from: https://gamma-api.polymarket.com/markets?limit=200&closed=false")
    
    # Analyze opportunities
    print("\nAnalyzing for best trade opportunities...")
    opportunities = analyze_markets(markets)
    
    print(f"\nFound {len(opportunities)} potential opportunities")
    print("-"*80)
    
    # Display top 10 opportunities
    for i, opp in enumerate(opportunities[:10]):
        print(f"\n{i+1}. [{opp['type']}] {opp['action']}")
        print(f"   Question: {opp['question'][:100]}...")
        print(f"   Price: YES={opp['yes_price']*100:.1f}% | NO={opp['no_price']*100:.1f}%")
        print(f"   Edge: {opp['edge_percentage']:.1f}% | Expected Value: {opp['expected_value']:.3f}")
        print(f"   Volume: ${opp['volume']:,.2f} | Liquidity: ${opp['liquidity']:,.2f}")
        print(f"   End Date: {opp['end_date']}")
        print(f"   Reason: {opp['reason']}")
        print(f"   URL: https://polymarket.com/event/{opp['slug']}")
        print("-"*80)
    
    # Save to file
    output_file = 'best_trade_opportunities.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(opportunities[:20], f, indent=2, ensure_ascii=False)
    
    print(f"\nTop {min(20, len(opportunities))} opportunities saved to {output_file}")
    
    # Recommendations
    if opportunities:
        print("\n🎯 RECOMMENDED TRADE:")
        best = opportunities[0]
        print(f"   Action: {best['action']} on '{best['question'][:80]}...'")
        print(f"   Edge: {best['edge_percentage']:.1f}%")
        print(f"   Position Size: $2.50 (0.5% of $500 capital, 25% of $10 testing capital)")
        print(f"   Expected Return: ${2.50 * best['expected_value']:.2f}")
        print(f"   Trade URL: https://polymarket.com/event/{best['slug']}")
    else:
        print("\n[WARNING] No strong opportunities found. Consider manual review of markets.")

if __name__ == "__main__":
    main()