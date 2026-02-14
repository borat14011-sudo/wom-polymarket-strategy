#!/usr/bin/env python3
"""
SLIPPAGE-AWARE OPPORTUNITY ANALYZER - REALISTIC THRESHOLD
"""
import json
from datetime import datetime

print("=" * 70)
print("SLIPPAGE-AWARE OPPORTUNITIES (3% minimum threshold)")
print("=" * 70)

with open('active-markets.json', 'r') as f:
    data = json.load(f)

markets = data.get('markets', [])

# Transaction costs
ENTRY_FEE = 0.02
EXIT_FEE = 0.02
SLIPPAGE = 0.01  # 1% slippage on entry

def analyze_position(market, side, mid_price, volume):
    """Analyze a position after all costs"""
    if volume < 100000:
        return None
    
    if mid_price < 0.08 or mid_price > 0.92:
        return None  # Skip extremes
    
    # Realistic entry (mid + slippage)
    entry = mid_price * (1 + SLIPPAGE)
    
    # After fees
    cost_basis = entry * (1 + ENTRY_FEE)
    
    # If wins: exit at 0.97 (never hits 1.0 perfectly)
    win_proceeds = 0.97 * (1 - EXIT_FEE)
    win_return = (win_proceeds - cost_basis) / cost_basis
    
    # If loses: exit at 0.03
    lose_proceeds = 0.03 * (1 - EXIT_FEE)
    lose_return = (lose_proceeds - cost_basis) / cost_basis
    
    # Expected value using market-implied probability
    ev = (mid_price * win_return) + ((1 - mid_price) * lose_return)
    
    # Annualized return (if end date available)
    end_str = market.get('endDate', '')
    days = 365
    try:
        end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00').replace('+00:00', ''))
        days = max(1, (end_date - datetime.now()).days)
    except:
        pass
    
    annualized = ((1 + ev) ** (365 / days)) - 1 if ev > -1 else -1
    
    return {
        'question': market.get('question', 'N/A'),
        'side': side,
        'mid_price': mid_price,
        'entry_cost': cost_basis,
        'win_return': win_return,
        'ev': ev,
        'annualized': annualized,
        'days': days,
        'volume': volume
    }

opportunities = []

for m in markets:
    prices_str = m.get('outcomePrices', '[]')
    volume = float(m.get('volume', 0))
    
    try:
        prices = json.loads(prices_str)
        if len(prices) != 2:
            continue
        
        yes_price = float(prices[0])
        no_price = float(prices[1])
        
        # Analyze YES side
        yes_opp = analyze_position(m, 'YES', yes_price, volume)
        if yes_opp and yes_opp['ev'] > 0.03:
            opportunities.append(yes_opp)
        
        # Analyze NO side
        no_opp = analyze_position(m, 'NO', no_price, volume)
        if no_opp and no_opp['ev'] > 0.03:
            opportunities.append(no_opp)
            
    except:
        pass

# Sort by expected value
opportunities.sort(key=lambda x: x['ev'], reverse=True)

if opportunities:
    print(f"\nFound {len(opportunities)} viable opportunities:\n")
    
    for i, opp in enumerate(opportunities[:15], 1):
        print(f"{i}. {opp['question'][:60]}...")
        print(f"   Bet: {opp['side']} at {opp['mid_price']:.1%} (cost: {opp['entry_cost']:.1%} after fees)")
        print(f"   If win: {opp['win_return']:.1%} return")
        print(f"   Expected: {opp['ev']:.1%} | Annualized: {opp['annualized']:.0%}")
        print(f"   Days to close: {opp['days']} | Volume: ${opp['volume']:,.0f}")
        print()
else:
    print("\nNo opportunities meet 3% threshold after slippage/fees.")
    print("\nShowing best available (even if negative):\n")
    
    all_opps = []
    for m in markets:
        prices_str = m.get('outcomePrices', '[]')
        volume = float(m.get('volume', 0))
        
        try:
            prices = json.loads(prices_str)
            if len(prices) != 2:
                continue
            
            yes_price = float(prices[0])
            if 0.10 < yes_price < 0.90 and volume > 500000:
                opp = analyze_position(m, 'YES', yes_price, volume)
                if opp:
                    all_opps.append(opp)
        except:
            pass
    
    all_opps.sort(key=lambda x: x['ev'], reverse=True)
    
    for opp in all_opps[:5]:
        print(f"- {opp['question'][:55]}...")
        print(f"  {opp['side']} at {opp['mid_price']:.1%} → EV: {opp['ev']:.1%}")
        print()

# Best specific recommendations
print("\n" + "=" * 70)
print("REALISTIC RECOMMENDATIONS")
print("=" * 70)

print("""
With $10 capital and 4% total costs:

[SKIP] Revenue <$100B at 84.5%
  After fees: Entry ~86.5%, exit ~95% if win
  Net return: ~10% - not bad, but capital tied up
  
[SKIP] Deportation markets
  250-500k at 87%: Too expensive, limited upside
  500-750k at 1.4%: Slippage kills edge on entry

[REALITY CHECK]
Current Polymarket after fees: VERY HARD to find +EV
Your edge needs to be: >5% just to break even
Most "arbitrage" disappears after costs

[BEST MOVE]
Paper trade for 30 days first
Build track record before deploying real capital
Market is efficient at pricing in obvious edges
""")
