#!/usr/bin/env python3
"""
Find actual trading opportunities from Polymarket data
Looking for markets with clear edges based on common sense
"""

import json
import re
from datetime import datetime, timezone

def load_markets():
    """Load latest Polymarket data"""
    with open('polymarket_fresh.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('markets', [])

def parse_price(price_str):
    """Parse price string to float"""
    try:
        return float(price_str)
    except:
        return 0.0

def analyze_market(market):
    """Analyze a single market for trading opportunities"""
    question = market.get('question', '')
    slug = market.get('slug', '')
    outcome_prices = market.get('outcomePrices', [])
    
    if not outcome_prices or len(outcome_prices) < 2:
        return None
    
    yes_price = parse_price(outcome_prices[0])
    no_price = parse_price(outcome_prices[1]) if len(outcome_prices) > 1 else 1.0 - yes_price
    volume = float(market.get('volume', '0'))
    liquidity = float(market.get('liquidity', '0'))
    end_date = market.get('endDate', '')
    
    opportunities = []
    
    # Strategy 1: Trump deportation markets (from our memory)
    if 'trump' in question.lower() and 'deport' in question.lower():
        # These are active political markets
        if 'less than 250,000' in question.lower():
            # Current price: YES at 5.4% (0.054)
            # This seems VERY low given Trump's rhetoric
            # Even with implementation challenges, >5% seems likely
            true_prob_estimate = 0.20  # 20% chance
            edge = true_prob_estimate - yes_price
            if edge > 0.05:  # 5% edge
                opportunities.append({
                    'type': 'TRUMP_DEPORTATION',
                    'action': 'BUY YES',
                    'edge': edge,
                    'edge_percent': (edge / yes_price) * 100 if yes_price > 0 else 0 if yes_price > 0 else 0,
                    'reason': 'Trump deportation <250k at 5.4% seems underpriced given rhetoric'
                })
        
        elif '250,000-500,000' in question.lower():
            # Current price: YES at 88% (0.88)
            # This seems high - 250-500k is a huge number
            true_prob_estimate = 0.60  # 60% chance
            edge = (1 - true_prob_estimate) - no_price  # Edge on NO
            if edge > 0.05:
                opportunities.append({
                    'type': 'TRUMP_DEPORTATION_HYPE_FADE',
                    'action': 'BUY NO',
                    'edge': edge,
                    'edge_percent': (edge / no_price) * 100 if no_price > 0 else 0 if no_price > 0 else 0,
                    'reason': 'Trump deportation 250-500k at 88% seems overhyped'
                })
    
    # Strategy 2: Sports championships (often overpriced favorites)
    sports_keywords = ['nba', 'nfl', 'mlb', 'nhl', 'championship', 'finals', 'super bowl']
    if any(keyword in question.lower() for keyword in sports_keywords):
        # Sports favorites are often overpriced
        if yes_price > 0.85:  # Heavy favorite
            true_prob_estimate = 0.70  # Even favorites rarely >70%
            edge = (1 - true_prob_estimate) - no_price
            if edge > 0.05:
                opportunities.append({
                    'type': 'SPORTS_HYPE_FADE',
                    'action': 'BUY NO',
                    'edge': edge,
                    'edge_percent': (edge / no_price) * 100 if no_price > 0 else 0,
                    'reason': f'Sports favorite at {yes_price*100:.1f}% likely overpriced'
                })
        elif yes_price < 0.20:  # Big underdog
            true_prob_estimate = 0.10  # Still some chance
            edge = true_prob_estimate - yes_price
            if edge > 0.02:  # Smaller edge for longshots
                opportunities.append({
                    'type': 'SPORTS_LONGSHOT',
                    'action': 'BUY YES',
                    'edge': edge,
                    'edge_percent': (edge / yes_price) * 100 if yes_price > 0 else 0,
                    'reason': f'Sports underdog at {yes_price*100:.1f}% may have value'
                })
    
    # Strategy 3: Political markets (often mispriced)
    political_keywords = ['election', 'nomination', 'president', 'senate', 'house', 'democrat', 'republican']
    if any(keyword in question.lower() for keyword in political_keywords):
        # Political markets often have public misperceptions
        if yes_price > 0.90:  # Near-certain political outcome
            true_prob_estimate = 0.80  # Politics is unpredictable
            edge = (1 - true_prob_estimate) - no_price
            if edge > 0.03:
                opportunities.append({
                    'type': 'POLITICAL_HYPE_FADE',
                    'action': 'BUY NO',
                    'edge': edge,
                    'edge_percent': (edge / no_price) * 100 if no_price > 0 else 0,
                    'reason': f'Political certainty at {yes_price*100:.1f}% likely overconfident'
                })
    
    # Strategy 4: Crypto/tech markets
    crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'elon', 'musk']
    if any(keyword in question.lower() for keyword in crypto_keywords):
        # Crypto markets are volatile and often overreact
        if yes_price > 0.85:
            true_prob_estimate = 0.70
            edge = (1 - true_prob_estimate) - no_price
            if edge > 0.05:
                opportunities.append({
                    'type': 'CRYPTO_HYPE_FADE',
                    'action': 'BUY NO',
                    'edge': edge,
                    'edge_percent': (edge / no_price) * 100 if no_price > 0 else 0,
                    'reason': f'Crypto certainty at {yes_price*100:.1f}% likely overhyped'
                })
    
    # If we found opportunities, return the best one
    if opportunities:
        # Sort by edge percentage
        opportunities.sort(key=lambda x: x['edge_percent'], reverse=True)
        best = opportunities[0]
        
        return {
            'question': question,
            'slug': slug,
            'yes_price': yes_price,
            'no_price': no_price,
            'volume': volume,
            'liquidity': liquidity,
            'end_date': end_date,
            'type': best['type'],
            'action': best['action'],
            'edge': best['edge'],
            'edge_percent': best['edge_percent'],
            'reason': best['reason']
        }
    
    return None

def main():
    print("="*80)
    print("POLYMARKET ACTUAL OPPORTUNITY FINDER")
    print("="*80)
    print(f"Scan time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # Load markets
    print("Loading fresh Polymarket data...")
    markets = load_markets()
    print(f"Loaded {len(markets)} markets")
    
    # Analyze each market
    print("\nAnalyzing for trading opportunities...")
    opportunities = []
    
    for market in markets:
        opp = analyze_market(market)
        if opp:
            opportunities.append(opp)
    
    print(f"\nFound {len(opportunities)} potential opportunities")
    print("-"*80)
    
    # Sort by edge percentage
    opportunities.sort(key=lambda x: x['edge_percent'], reverse=True)
    
    # Display top opportunities
    for i, opp in enumerate(opportunities[:10]):
        print(f"\n{i+1}. [{opp['type']}] {opp['action']}")
        print(f"   Question: {opp['question'][:100]}...")
        print(f"   Price: YES={opp['yes_price']*100:.1f}% | NO={opp['no_price']*100:.1f}%")
        print(f"   Edge: {opp['edge_percent']:.1f}% | Absolute Edge: {opp['edge']:.3f}")
        print(f"   Volume: ${opp['volume']:,.2f} | Liquidity: ${opp['liquidity']:,.2f}")
        print(f"   End Date: {opp['end_date']}")
        print(f"   Reason: {opp['reason']}")
        print(f"   URL: https://polymarket.com/event/{opp['slug']}")
        print("-"*80)
    
    # Save to file
    output_file = 'actual_opportunities.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(opportunities[:20], f, indent=2, ensure_ascii=False)
    
    print(f"\nTop {min(20, len(opportunities))} opportunities saved to {output_file}")
    
    # Recommendations
    if opportunities:
        print("\n🎯 TOP RECOMMENDED TRADE:")
        best = opportunities[0]
        print(f"   Action: {best['action']} on '{best['question'][:80]}...'")
        print(f"   Edge: {best['edge_percent']:.1f}%")
        
        # Position sizing
        capital = 100  # $100 total capital
        test_capital = 10  # $10 testing capital
        position_size = min(2.50, test_capital * 0.25)  # 0.5% of total, 25% of test
        
        print(f"   Position Size: ${position_size:.2f}")
        print(f"   Expected Return: ${position_size * best['edge']:.2f}")
        print(f"   Expected ROI: {(best['edge'] / (best['yes_price'] if best['action'] == 'BUY YES' else best['no_price'])) * 100:.1f}%")
        print(f"   Trade URL: https://polymarket.com/event/{best['slug']}")
        
        # Create trade plan
        trade_plan = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'market_question': best['question'],
            'market_slug': best['slug'],
            'action': best['action'],
            'yes_price': best['yes_price'],
            'no_price': best['no_price'],
            'position_size': position_size,
            'edge_percent': best['edge_percent'],
            'reason': best['reason'],
            'expected_return': position_size * best['edge'],
            'trade_url': f"https://polymarket.com/event/{best['slug']}",
            'status': 'READY_TO_EXECUTE'
        }
        
        with open('trade_plan_now.json', 'w', encoding='utf-8') as f:
            json.dump(trade_plan, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Trade plan saved to: trade_plan_now.json")
        
    else:
        print("\n[WARNING] No opportunities found. Consider:")
        print("  1. Manual review of top volume markets")
        print("  2. Checking Kalshi for sports/economic markets")
        print("  3. Waiting for new market catalysts")

if __name__ == "__main__":
    main()