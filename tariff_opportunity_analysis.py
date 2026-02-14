"""
Analysis of Tariff $200-500B opportunity at 8c
"""
print("=" * 70)
print("TARIFF $200-500B OPPORTUNITY ANALYSIS")
print("=" * 70)
print()

# Market data
current_price = 0.08  # 8c
our_thesis = 0.35     # 35c (35% probability)
days_to_resolution = 16  # Feb 28, 2026

# Calculate edge
edge_percentage = (our_thesis - current_price) * 100
edge_ratio = our_thesis / current_price

print("MARKET DATA:")
print("-" * 40)
print(f"Current Price: {current_price*100:.1f}c ({current_price*100:.0f}% probability)")
print(f"Our Thesis: {our_thesis*100:.1f}c ({our_thesis*100:.0f}% probability)")
print(f"Edge: {edge_percentage:.1f} percentage points")
print(f"Edge Ratio: {edge_ratio:.1f}x (we think it's {edge_ratio:.1f} more likely)")
print(f"Days to Resolution: {days_to_resolution}")
print()

# Expected returns
print("EXPECTED RETURNS:")
print("-" * 40)

# If YES (35% probability)
if_yes_return = (1.00 - current_price) / current_price  # (100c - 8c) / 8c
if_yes_return_net = if_yes_return * 0.96  # After 4% transaction costs
print(f"If YES (35% chance): {if_yes_return*100:.0f}% return")
print(f"After 4% costs: {if_yes_return_net*100:.0f}% return")

# If NO (65% probability)
if_no_loss = -1.00  # Lose entire position
print(f"If NO (65% chance): {if_no_loss*100:.0f}% loss")

# Expected value
expected_value = (our_thesis * if_yes_return_net) + ((1 - our_thesis) * if_no_loss)
expected_return_percent = expected_value * 100
annualized_return = (1 + expected_value) ** (365 / days_to_resolution) - 1

print(f"\nExpected Value: {expected_value*100:.1f}% per trade")
print(f"Annualized Return: {annualized_return*100:.0f}%")
print()

# Position sizing
capital = 10.00  # $10 capital
kelly_fraction = (our_thesis * if_yes_return - (1 - our_thesis)) / if_yes_return
kelly_position = capital * kelly_fraction

print("POSITION SIZING:")
print("-" * 40)
print(f"Capital: ${capital:.2f}")
print(f"Kelly Fraction: {kelly_fraction:.2%}")
print(f"Kelly Position: ${kelly_position:.2f}")
print(f"Risk Rules (2% testing): ${capital * 0.02:.2f}")
print(f"Recommended: ${min(kelly_position, capital * 0.25):.2f} (conservative)")
print()

# Comparison with paper trade
print("COMPARISON WITH PAPER TRADE:")
print("-" * 40)
paper_entry = 0.11  # 11c
paper_edge = (our_thesis - paper_entry) * 100
current_edge = (our_thesis - current_price) * 100

print(f"Paper Trade Entry: {paper_entry*100:.1f}c")
print(f"Paper Trade Edge: {paper_edge:.1f} percentage points")
print(f"Current Opportunity Edge: {current_edge:.1f} percentage points")
print(f"Edge Improvement: {current_edge - paper_edge:.1f} percentage points")
print()

# Action recommendation
print("ACTION RECOMMENDATION:")
print("-" * 40)
print("1. MANUAL EXECUTION REQUIRED (bot login failed)")
print("2. Buy YES at <= 8c")
print(f"3. Position size: ${min(2.00, kelly_position):.2f}")
print("4. Time: URGENT (16 days to resolution)")
print()

# Risk management
print("RISK MANAGEMENT:")
print("-" * 40)
print("Stop-loss: 9.5c (12% loss)")
print("Max drawdown: 15% total")
print("Exit: Feb 27 (day before resolution)")
print("Monitor: Tariff revenue news, trade deal announcements")
print()

print("=" * 70)
print("CONCLUSION: EXECUTE TRADE MANUALLY NOW")
print("=" * 70)