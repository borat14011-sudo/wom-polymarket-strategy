#!/usr/bin/env python3
"""
Simple trade finder - look at actual Polymarket data and find best trade
"""

import json
from datetime import datetime, timezone

print("="*80)
print("SIMPLE POLYMARKET TRADE FINDER")
print("="*80)
print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
print()

# Load fresh data
with open('polymarket_fresh.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

markets = data.get('markets', [])
print(f"Loaded {len(markets)} markets")
print()

# Look at first few markets to understand structure
print("First 5 markets:")
print("-"*40)
for i, market in enumerate(markets[:5]):
    print(f"\n{i+1}. {market.get('question', 'N/A')}")
    print(f"   Prices: {market.get('outcomePrices', [])}")
    print(f"   Volume: ${float(market.get('volume', 0)):,.2f}")
    print(f"   Slug: {market.get('slug', 'N/A')}")
    print(f"   End Date: {market.get('endDate', 'N/A')}")

print("\n" + "="*80)
print("ANALYZING FOR BEST TRADE OPPORTUNITY")
print("="*80)

# Based on our memory and Wom's preferences, let's look for:
# 1. Near-certainties not priced in (95%+ true prob at 70-85% price)
# 2. Hype fade (bet NO on spike-driven markets)

best_trades = []

for market in markets:
    question = market.get('question', '').lower()
    prices = market.get('outcomePrices', [])
    
    if not prices or len(prices) < 2:
        continue
    
    try:
        yes_price = float(prices[0])
        no_price = float(prices[1]) if len(prices) > 1 else 1.0 - yes_price
        
        volume = float(market.get('volume', 0))
        slug = market.get('slug', '')
        end_date = market.get('endDate', '')
        
        # Skip markets with very low volume
        if volume < 1000:
            continue
            
        # Strategy 1: Trump deportation markets (from our memory)
        if 'trump' in question and 'deport' in question:
            if 'less than 250,000' in question:
                # YES at 5.4% seems very low
                # Even with challenges, probability is likely >20%
                true_prob = 0.20  # Conservative estimate
                edge = true_prob - yes_price
                if edge > 0.05:
                    best_trades.append({
                        'question': market.get('question', ''),
                        'slug': slug,
                        'action': 'BUY YES',
                        'yes_price': yes_price,
                        'no_price': no_price,
                        'edge': edge,
                        'edge_percent': (edge / yes_price) * 100 if yes_price > 0 else 0,
                        'volume': volume,
                        'end_date': end_date,
                        'reason': 'Trump deportation <250k at 5.4% - likely underpriced given rhetoric',
                        'type': 'TRUMP_DEPORTATION_UNDERPRICED'
                    })
            
            elif '250,000-500,000' in question:
                # YES at 88% seems very high for such a large number
                true_prob = 0.60  # Conservative estimate
                edge = (1 - true_prob) - no_price  # Edge on NO
                if edge > 0.05:
                    best_trades.append({
                        'question': market.get('question', ''),
                        'slug': slug,
                        'action': 'BUY NO',
                        'yes_price': yes_price,
                        'no_price': no_price,
                        'edge': edge,
                        'edge_percent': (edge / no_price) * 100 if no_price > 0 else 0,
                        'volume': volume,
                        'end_date': end_date,
                        'reason': 'Trump deportation 250-500k at 88% - likely overhyped',
                        'type': 'TRUMP_DEPORTATION_OVERHYPED'
                    })
        
        # Strategy 2: Sports favorites (often overpriced)
        sports_teams = ['lakers', 'celtics', 'warriors', 'bulls', 'yankees', 'dodgers']
        if any(team in question for team in sports_teams):
            if yes_price > 0.80:
                true_prob = 0.65  # Even good teams lose
                edge = (1 - true_prob) - no_price
                if edge > 0.05:
                    best_trades.append({
                        'question': market.get('question', ''),
                        'slug': slug,
                        'action': 'BUY NO',
                        'yes_price': yes_price,
                        'no_price': no_price,
                        'edge': edge,
                        'edge_percent': (edge / no_price) * 100 if no_price > 0 else 0,
                        'volume': volume,
                        'end_date': end_date,
                        'reason': f'Sports favorite at {yes_price*100:.1f}% - likely overpriced',
                        'type': 'SPORTS_HYPE_FADE'
                    })
        
        # Strategy 3: Political certainties (often overconfident)
        if 'election' in question or 'nomination' in question:
            if yes_price > 0.90:
                true_prob = 0.75  # Politics is unpredictable
                edge = (1 - true_prob) - no_price
                if edge > 0.03:
                    best_trades.append({
                        'question': market.get('question', ''),
                        'slug': slug,
                        'action': 'BUY NO',
                        'yes_price': yes_price,
                        'no_price': no_price,
                        'edge': edge,
                        'edge_percent': (edge / no_price) * 100 if no_price > 0 else 0,
                        'volume': volume,
                        'end_date': end_date,
                        'reason': f'Political certainty at {yes_price*100:.1f}% - likely overconfident',
                        'type': 'POLITICAL_HYPE_FADE'
                    })
                    
    except Exception as e:
        continue

# Sort by edge percentage
best_trades.sort(key=lambda x: x.get('edge_percent', 0), reverse=True)

print(f"\nFound {len(best_trades)} potential trades")
print("-"*80)

if best_trades:
    # Show top 5
    for i, trade in enumerate(best_trades[:5]):
        print(f"\n{i+1}. [{trade['type']}] {trade['action']}")
        print(f"   Question: {trade['question'][:80]}...")
        print(f"   Price: YES={trade['yes_price']*100:.1f}% | NO={trade['no_price']*100:.1f}%")
        print(f"   Edge: {trade['edge_percent']:.1f}% | Absolute Edge: {trade['edge']:.3f}")
        print(f"   Volume: ${trade['volume']:,.2f}")
        print(f"   End Date: {trade['end_date']}")
        print(f"   Reason: {trade['reason']}")
        print(f"   URL: https://polymarket.com/event/{trade['slug']}")
        print("-"*80)
    
    # Select the best trade
    best = best_trades[0]
    
    print("\n" + "="*80)
    print("RECOMMENDED TRADE")
    print("="*80)
    print(f"ACTION: {best['action']}")
    print(f"MARKET: {best['question']}")
    print(f"CURRENT PRICE: YES={best['yes_price']*100:.1f}% | NO={best['no_price']*100:.1f}%")
    print(f"EDGE: {best['edge_percent']:.1f}%")
    print(f"REASON: {best['reason']}")
    print(f"VOLUME: ${best['volume']:,.2f}")
    print(f"RESOLUTION: {best['end_date']}")
    print()
    print(f"TRADE URL: https://polymarket.com/event/{best['slug']}")
    print()
    
    # Position sizing
    total_capital = 100  # $100
    test_capital = 10    # $10 for testing
    position_size = 2.50  # 0.5% of total, 25% of test
    
    expected_return = position_size * best['edge']
    roi_percent = (best['edge'] / (best['yes_price'] if best['action'] == 'BUY YES' else best['no_price'])) * 100
    
    print("POSITION SIZING:")
    print(f"  Total Capital: ${total_capital}")
    print(f"  Test Capital: ${test_capital}")
    print(f"  Position Size: ${position_size:.2f}")
    print(f"  Expected Return: ${expected_return:.2f}")
    print(f"  Expected ROI: {roi_percent:.1f}%")
    print()
    
    # Create trade plan
    trade_plan = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'market': best['question'],
        'slug': best['slug'],
        'action': best['action'],
        'yes_price': best['yes_price'],
        'no_price': best['no_price'],
        'position_size': position_size,
        'edge_percent': best['edge_percent'],
        'reason': best['reason'],
        'expected_return': expected_return,
        'expected_roi': roi_percent,
        'trade_url': f"https://polymarket.com/event/{best['slug']}",
        'status': 'READY_TO_EXECUTE',
        'notes': 'Execute manually on Polymarket website'
    }
    
    with open('recommended_trade.json', 'w', encoding='utf-8') as f:
        json.dump(trade_plan, f, indent=2, ensure_ascii=False)
    
    print(f"Trade plan saved to: recommended_trade.json")
    
else:
    print("\nNo strong opportunities found.")
    print("\nAlternative options:")
    print("1. Check Kalshi for sports/economic markets (NBA games tonight)")
    print("2. Manual review of Polymarket 'Closing Soon' markets")
    print("3. Wait for new market catalysts (Fed meetings, earnings, etc.)")

print("\n" + "="*80)