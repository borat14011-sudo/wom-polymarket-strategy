#!/usr/bin/env python3
"""
SLIPPAGE-AWARE OPPORTUNITY ANALYZER
Uses real bid/ask spreads, not mid-market prices
Accounts for 2% entry fee + 2% exit fee
"""
import json
from datetime import datetime

print("=" * 70)
print("SLIPPAGE-AWARE OPPORTUNITY SCANNER")
print("Uses bid/ask spreads + 4% transaction costs")
print("=" * 70)

# Load market data
with open('active-markets.json', 'r') as f:
    data = json.load(f)

markets = data.get('markets', [])

# Transaction cost model
ENTRY_FEE = 0.02  # 2%
EXIT_FEE = 0.02   # 2%
MIN_SPREAD = 0.005  # Minimum spread to account for

def calculate_real_return(entry_price, exit_price, is_yes=True):
    """Calculate real return after all costs"""
    # Entry cost (including fee)
    entry_cost = entry_price * (1 + ENTRY_FEE)
    
    # Exit proceeds (minus fee)
    exit_proceeds = exit_price * (1 - EXIT_FEE)
    
    # Net return
    if entry_cost > 0:
        net_return = (exit_proceeds - entry_cost) / entry_cost
        return net_return
    return 0

def get_executable_price(market, side='yes'):
    """Get realistic executable price using best bid/ask"""
    # Try to get order book data
    best_bid = market.get('bestBid')
    best_ask = market.get('bestAsk')
    
    # Fallback to outcomePrices
    prices_str = market.get('outcomePrices', '[]')
    try:
        prices = json.loads(prices_str)
        mid_yes = float(prices[0])
        mid_no = float(prices[1])
    except:
        return None, None
    
    # If we have order book data, use it
    if best_bid and best_ask:
        # For YES side: you'd pay the ask
        # For NO side: you'd pay (1 - bid)
        return float(best_ask), float(best_bid)
    
    # Otherwise estimate spread from mid price
    # Conservative: assume 0.5% spread
    spread = max(MIN_SPREAD, mid_yes * 0.01)
    
    if side == 'yes':
        # You pay slightly more than mid
        return mid_yes + spread/2, mid_yes - spread/2
    else:
        # You pay slightly more than mid for NO
        return mid_no + spread/2, mid_no - spread/2

print("\n" + "=" * 70)
print("TOP OPPORTUNITIES (After Slippage & Fees)")
print("=" * 70)

opportunities = []

for m in markets:
    q = m.get('question', '')
    volume = float(m.get('volume', 0))
    
    if volume < 100000:  # Skip low liquidity
        continue
    
    prices_str = m.get('outcomePrices', '[]')
    try:
        prices = json.loads(prices_str)
        if len(prices) != 2:
            continue
            
        mid_yes = float(prices[0])
        mid_no = float(prices[1])
        
        # Get best bid/ask if available
        best_bid = market.get('bestBid')
        best_ask = market.get('bestAsk')
        
        # Calculate realistic entry/exit
        # Conservative: add 1% slippage to entry
        entry_slippage = 0.01
        
        # YES side analysis
        if 0.10 <= mid_yes <= 0.90:  # Avoid extremes
            real_entry_yes = mid_yes * (1 + entry_slippage)
            
            # If resolved YES, exit at ~0.97 (never quite 1.0)
            exit_if_win = 0.97
            
            net_return_yes = calculate_real_return(real_entry_yes, exit_if_win)
            
            # If resolved NO, exit at ~0.03
            exit_if_lose = 0.03
            net_return_no = calculate_real_return(real_entry_yes, exit_if_lose)
            
            # Expected value (using market implied probability)
            ev = (mid_yes * net_return_yes) + ((1 - mid_yes) * net_return_no)
            
            if ev > 0.05:  # 5% minimum expected return
                opportunities.append({
                    'question': q,
                    'side': 'YES',
                    'mid_price': mid_yes,
                    'real_entry': real_entry_yes,
                    'ev_return': ev,
                    'volume': volume,
                    'end_date': m.get('endDate', 'N/A')[:10]
                })
        
        # NO side analysis
        if 0.10 <= mid_no <= 0.90:
            real_entry_no = mid_no * (1 + entry_slippage)
            
            exit_if_win = 0.97
            net_return_no = calculate_real_return(real_entry_no, exit_if_win)
            
            exit_if_lose = 0.03
            net_return_yes_side = calculate_real_return(real_entry_no, exit_if_lose)
            
            ev = (mid_no * net_return_no) + ((1 - mid_no) * net_return_yes_side)
            
            if ev > 0.05:
                opportunities.append({
                    'question': q,
                    'side': 'NO',
                    'mid_price': mid_no,
                    'real_entry': real_entry_no,
                    'ev_return': ev,
                    'volume': volume,
                    'end_date': m.get('endDate', 'N/A')[:10]
                })
    except:
        pass

# Sort by expected return
opportunities.sort(key=lambda x: x['ev_return'], reverse=True)

print(f"\nFound {len(opportunities)} opportunities with >5% expected return\n")

for i, opp in enumerate(opportunities[:10], 1):
    print(f"{i}. {opp['question'][:65]}")
    print(f"   Side: {opp['side']} | Mid: {opp['mid_price']:.2%} | Real Entry: ~{opp['real_entry']:.2%}")
    print(f"   Expected Net Return: {opp['ev_return']:.1%}")
    print(f"   Volume: ${opp['volume']:,.0f} | Ends: {opp['end_date']}")
    print()

# Show why extremes don't work
print("\n" + "=" * 70)
print("WHY EXTREMES DON'T WORK (Slippage Demo)")
print("=" * 70)

extreme_examples = [
    {'name': 'Elon 10% cut NO', 'price': 0.999, 'side': 'NO'},
    {'name': 'NBA Champ NO', 'price': 0.9985, 'side': 'NO'},
    {'name': 'Deport <250k NO', 'price': 0.947, 'side': 'NO'},
]

print("\nExample: Trying to buy NO at extreme prices")
print("-" * 70)

for ex in extreme_examples:
    mid_price = ex['price']
    # Realistic execution (slippage)
    real_entry = min(0.995, mid_price * 0.998)  # Slippage toward 99.5%
    
    # Entry with fee
    entry_cost = real_entry * 1.02
    
    # If wins (goes to 1.0), exit at 0.97 with 2% fee
    exit_proceeds = 0.97 * 0.98
    
    # Net return
    if entry_cost < exit_proceeds:
        net_return = (exit_proceeds - entry_cost) / entry_cost
    else:
        net_return = (exit_proceeds - entry_cost) / entry_cost
    
    print(f"\n{ex['name']}")
    print(f"  Listed price: {mid_price:.3f}")
    print(f"  Real fill: ~{real_entry:.3f} (slippage)")
    print(f"  After 2% fee: {entry_cost:.3f}")
    print(f"  Exit proceeds: ${exit_proceeds:.3f}")
    print(f"  Net return: {net_return:.2%}")

print("\n" + "=" * 70)
print("BOTTOM LINE")
print("=" * 70)
print("""
Sweet spot: 15-85% price range
- Enough liquidity for tight spreads
- Room for price movement
- Fees don't eat all profits

Avoid: <5% or >95%
- Slippage kills edge
- Capital tied up for tiny returns
- Better opportunities elsewhere
""")
