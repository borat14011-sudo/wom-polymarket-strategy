"""
Find bets where YES is 70-90% (so betting NO has high profit potential)
Correct profit calculation: 
- If YES = 80%, NO = 20%
- Bet $1 on NO at $0.20
- If win, get $1, profit = $0.80 (400% ROI!)
"""
import json

print("="*80)
print("FINDING HIGH-PROFIT BETS (YES = 70-90%)")
print("="*80)

with open('live_markets_now.json', 'r') as f:
    opportunities = json.load(f)

print(f"\nTotal opportunities: {len(opportunities)}")

# Filter for YES between 70-90%
high_profit_bets = []

for opp in opportunities:
    yes_price = opp['current_price']
    
    # We want YES between 0.70 and 0.90
    if 0.70 <= yes_price <= 0.90:
        no_price = 1 - yes_price
        
        # Profit when betting NO and winning
        profit_per_dollar = yes_price / no_price
        roi_percent = profit_per_dollar * 100
        
        # Expected value
        win_rate = opp['expected_win'] / 100
        expected_profit = (win_rate * yes_price) - ((1 - win_rate) * no_price)
        expected_roi = (expected_profit / no_price) * 100
        
        opp['yes_price'] = yes_price * 100
        opp['no_price'] = no_price * 100
        opp['profit_per_dollar'] = yes_price
        opp['roi_percent'] = roi_percent
        opp['expected_roi'] = expected_roi
        
        high_profit_bets.append(opp)

print(f"\n[FOUND] {len(high_profit_bets)} bets with YES at 70-90%")

# Sort by expected ROI
high_profit_bets.sort(key=lambda b: b['expected_roi'], reverse=True)

print("\n" + "="*80)
print("TOP 10 HIGH-PROFIT BETS (Best Expected ROI)")
print("="*80)

for i, bet in enumerate(high_profit_bets[:10], 1):
    volume = float(bet['volume']) if bet['volume'] else 0
    
    print(f"\n{i}. [{bet['strategy']}] Win Rate: {bet['expected_win']:.1f}%")
    print(f"   {bet['question'][:70]}")
    print(f"   YES: {bet['yes_price']:.1f}% | NO: {bet['no_price']:.1f}%")
    print(f"   If we bet $6 on NO and WIN:")
    
    # Calculate actual profit on $6 bet
    cost_per_share = bet['no_price'] / 100
    shares = 6 / cost_per_share
    payout = shares * 1  # Each share pays $1
    profit = payout - 6
    
    print(f"     We pay: $6 (buy NO at {bet['no_price']:.1f}%)")
    print(f"     We get: ${payout:.2f} (if NO wins)")
    print(f"     Profit: ${profit:.2f} ({profit/6*100:.0f}% ROI)")
    print(f"   Expected ROI: {bet['expected_roi']:.1f}%")
    print(f"   Volume: ${volume/1000:.0f}K | End: {bet.get('end_date', 'Unknown')[:10]}")

# Save
with open('high_profit_bets.json', 'w') as f:
    json.dump(high_profit_bets, f, indent=2)

print(f"\n[SAVED] high_profit_bets.json")
print(f"  {len(high_profit_bets)} high-ROI markets ready")
