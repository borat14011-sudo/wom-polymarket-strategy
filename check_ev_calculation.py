import json

# Test EV calculation for a sample market
def calculate_ev(entry_price_cents, win_prob=0.115, kalshi_fee=0.02):
    """Calculate expected value with more realistic assumptions"""
    entry_price = entry_price_cents / 100
    
    # Win: contract resolves YES at $1 (100¢)
    # But in reality, we might exit at mean reversion, not full $1
    # Let's assume mean reversion to previous price level
    # For now, use conservative assumption: target 2x entry price
    target_price = min(entry_price * 2, 0.50)  # Cap at 50¢ for safety
    
    win_payout = target_price - entry_price - (entry_price * kalshi_fee)  # Fee on entry
    loss_amount = entry_price + (entry_price * kalshi_fee)  # Lose entry + fee
    
    ev = (win_prob * win_payout) - ((1 - win_prob) * loss_amount)
    ev_percent = (ev / entry_price) * 100 if entry_price > 0 else 0
    
    return ev, ev_percent, win_payout, loss_amount

# Test with some example prices
test_prices = [1, 3, 5, 10, 16, 40]  # cents

print("EV Calculation Test:")
print("=" * 80)
for price in test_prices:
    ev, ev_percent, win_payout, loss_amount = calculate_ev(price)
    print(f"Entry: {price}¢")
    print(f"  Target price: {min(price * 2, 50)}¢")
    print(f"  Win payout: ${win_payout:.4f} ({win_payout*100:.1f}¢)")
    print(f"  Loss amount: ${loss_amount:.4f} ({loss_amount*100:.1f}¢)")
    print(f"  EV: ${ev:.4f} ({ev_percent:.1f}%)")
    print()

# Now let's check what happens if we target full $1 payout
def calculate_ev_full_payout(entry_price_cents, win_prob=0.115, kalshi_fee=0.02):
    """Calculate EV assuming full $1 payout if win"""
    entry_price = entry_price_cents / 100
    
    # Win: contract resolves YES at $1 (100¢)
    win_payout = 1.00 - entry_price - (entry_price * kalshi_fee)
    loss_amount = entry_price + (entry_price * kalshi_fee)
    
    ev = (win_prob * win_payout) - ((1 - win_prob) * loss_amount)
    ev_percent = (ev / entry_price) * 100 if entry_price > 0 else 0
    
    return ev, ev_percent, win_payout, loss_amount

print("\n\nEV Calculation with FULL $1 Payout:")
print("=" * 80)
for price in test_prices:
    ev, ev_percent, win_payout, loss_amount = calculate_ev_full_payout(price)
    print(f"Entry: {price}¢")
    print(f"  Win payout: ${win_payout:.4f} ({win_payout*100:.1f}¢)")
    print(f"  Loss amount: ${loss_amount:.4f} ({loss_amount*100:.1f}¢)")
    print(f"  EV: ${ev:.4f} ({ev_percent:.1f}%)")
    print()