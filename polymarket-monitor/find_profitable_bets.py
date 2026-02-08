"""
Find markets with >5% profit potential
Filter for meaningful ROI, not just high win rate
"""
import json

print("="*80)
print("FINDING PROFITABLE BETS (>5% ROI)")
print("="*80)

# Load live opportunities
with open('live_markets_now.json', 'r') as f:
    opportunities = json.load(f)

print(f"\nTotal live opportunities: {len(opportunities)}")

# Calculate profit potential for each
profitable_bets = []

for opp in opportunities:
    current_price = opp['current_price']
    strategy = opp['strategy']
    expected_win = opp['expected_win'] / 100
    
    # For NO bets: profit when YES price collapses to 0
    # If YES is at 30%, we buy NO shares at ~70%
    # If we win, NO shares = $1, profit = $1 - $0.70 = $0.30 = 30% ROI
    
    # Profit per $1 bet = current_price (what we win when YES goes to 0)
    # For NO bets, we profit when YES fails
    profit_per_dollar = current_price  # Simplified
    profit_percent = profit_per_dollar * 100
    
    # Expected value = win_rate * profit - lose_rate * loss
    # Loss = 1 - current_price (what we paid for NO)
    loss_per_dollar = 1 - current_price
    expected_value = (expected_win * profit_per_dollar) - ((1 - expected_win) * loss_per_dollar)
    
    # Only include if profit potential >5%
    if profit_percent >= 5:
        opp['profit_percent'] = profit_percent
        opp['expected_value'] = expected_value * 100
        profitable_bets.append(opp)

print(f"\n[FILTERED] {len(profitable_bets)} bets with >5% profit potential")

# Breakdown by strategy
from collections import Counter
strategy_counts = Counter([b['strategy'] for b in profitable_bets])

print(f"\n[BREAKDOWN]")
for strategy, count in strategy_counts.most_common():
    print(f"  {strategy:30} {count:4} markets")

# Sort by expected value (win_rate * profit)
profitable_bets.sort(key=lambda b: b['expected_value'], reverse=True)

print("\n" + "="*80)
print("TOP 10 PROFITABLE BETS (>5% ROI + High Expected Value)")
print("="*80)

for i, bet in enumerate(profitable_bets[:10], 1):
    volume = float(bet['volume']) if bet['volume'] else 0
    
    print(f"\n{i}. [{bet['strategy']}] Win: {bet['expected_win']:.1f}%")
    print(f"   {bet['question'][:70]}")
    print(f"   YES Price: {bet['current_price']*100:.1f}%")
    print(f"   Profit if win: {bet['profit_percent']:.1f}%")
    print(f"   Expected value: {bet['expected_value']:.1f}%")
    print(f"   Volume: ${volume/1000:.0f}K | End: {bet.get('end_date', 'Unknown')[:10]}")

# Save
with open('profitable_bets.json', 'w') as f:
    json.dump(profitable_bets, f, indent=2)

print(f"\n[SAVED] profitable_bets.json")
print(f"  {len(profitable_bets)} markets with >5% ROI ready for paper trading")
