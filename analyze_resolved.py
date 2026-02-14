import json
import sys
import math

with open('polymarket_resolved_markets.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

print(f"Total resolved markets: {len(data)}")

# Determine final price for Yes outcome
yes_prices = []
no_prices = []
for m in data:
    outcomes = m['outcomes'].split('|')
    prices = m['final_prices'].split('|')
    # Assuming Yes is first, No second
    yes_price = float(prices[0])
    no_price = float(prices[1])
    yes_prices.append(yes_price)
    no_prices.append(no_price)

print(f"Yes price mean: {sum(yes_prices)/len(yes_prices):.3f}")
print(f"No price mean: {sum(no_prices)/len(no_prices):.3f}")

# Distribution of yes prices
bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
counts = {f'{bins[i]}-{bins[i+1]}':0 for i in range(len(bins)-1)}
for p in yes_prices:
    for i in range(len(bins)-1):
        if bins[i] <= p < bins[i+1]:
            key = f'{bins[i]}-{bins[i+1]}'
            counts[key] += 1
            break
    else:
        if p == 1.0:
            counts['0.9-1.0'] += 1

print("Yes price distribution:")
for k, v in sorted(counts.items()):
    print(f"  {k}: {v}")

# Winners
winner_yes = sum(1 for m in data if m['winner'] == 'Yes')
winner_no = sum(1 for m in data if m['winner'] == 'No')
print(f"Winner Yes: {winner_yes}, No: {winner_no}")

# Compute favorite range performance
def simulate_favorites(threshold_low, threshold_high, fees_entry=0.02, fees_exit=0.02):
    # Assume we bet on Yes if yes_price within threshold
    total_bets = 0
    wins = 0
    total_invested = 0
    total_return = 0
    for m in data:
        yes_price = float(m['final_prices'].split('|')[0])
        if threshold_low <= yes_price <= threshold_high:
            total_bets += 1
            total_invested += yes_price
            if m['winner'] == 'Yes':
                wins += 1
                # payout is 1 per share, but we pay fees
                # net after fees: (1 - fees_exit) / (1 + fees_entry) ??? Actually we buy shares at price yes_price, paying yes_price * (1 + fees_entry)
                # When win, we receive 1 per share, but after fees we get 1 * (1 - fees_exit)
                # So net profit = (1 * (1 - fees_exit)) - (yes_price * (1 + fees_entry))
                # Let's compute return on investment: (net profit) / (yes_price * (1 + fees_entry))
                # Instead simpler: net multiple = (1 * (1 - fees_exit)) / (yes_price * (1 + fees_entry))
                net = (1 * (1 - fees_exit)) / (yes_price * (1 + fees_entry))
                total_return += net
            else:
                # lose, payout 0
                net = 0
                total_return += net
    win_rate = wins / total_bets if total_bets > 0 else 0
    avg_return = total_return / total_bets if total_bets > 0 else 0
    return total_bets, wins, win_rate, avg_return

print("\nFavorites strategy (bet on Yes with price range):")
for low, high in [(0.8, 0.85), (0.85, 0.9), (0.9, 0.95), (0.95, 1.0)]:
    bets, wins, win_rate, avg_ret = simulate_favorites(low, high)
    print(f"Range {low}-{high}: bets={bets}, wins={wins}, win_rate={win_rate:.3f}, avg_return={avg_ret:.4f}")

# Longshots strategy (bet on Yes with price low)
print("\nLongshots strategy (bet on Yes with price <0.2):")
for low, high in [(0.0, 0.05), (0.05, 0.1), (0.1, 0.15), (0.15, 0.2)]:
    bets, wins, win_rate, avg_ret = simulate_favorites(low, high)
    print(f"Range {low}-{high}: bets={bets}, wins={wins}, win_rate={win_rate:.3f}, avg_return={avg_ret:.4f}")

# Compute expected value after fees (assuming we bet 1 unit each time)
def simulate_bet_unit(threshold_low, threshold_high, bet_amount=1):
    total_bets = 0
    total_profit = 0
    for m in data:
        yes_price = float(m['final_prices'].split('|')[0])
        if threshold_low <= yes_price <= threshold_high:
            total_bets += 1
            # cost to buy shares for bet_amount payout? We buy shares such that if win we get bet_amount after fees?
            # Let's assume we invest 1 unit in shares: we buy 1/yes_price shares, costing 1/yes_price * yes_price = 1? Wait.
            # Actually we want to bet $1 on Yes outcome. The cost per share is yes_price. To receive $1 payout (before fees), we need to buy 1 share? No.
            # In Polymarket, buying a Yes share at price p gives you a claim on $1 if Yes wins. So your profit per share is (1 - p) if win, else -p.
            # So we can buy 1 share. Let's compute profit after fees.
            # Entry fee: we pay yes_price * (1 + fees_entry)
            # If win, we receive 1 * (1 - fees_exit)
            # Profit = 1*(1 - fees_exit) - yes_price*(1 + fees_entry)
            # If lose, profit = -yes_price*(1 + fees_entry)
            fees_entry = 0.02
            fees_exit = 0.02
            cost = yes_price * (1 + fees_entry)
            if m['winner'] == 'Yes':
                profit = (1 * (1 - fees_exit)) - cost
            else:
                profit = -cost
            total_profit += profit
    avg_profit = total_profit / total_bets if total_bets > 0 else 0
    return total_bets, total_profit, avg_profit

print("\nUnit bet profit after fees (2% entry, 2% exit):")
for low, high in [(0.8, 0.85), (0.85, 0.9), (0.9, 0.95), (0.95, 1.0)]:
    bets, profit, avg = simulate_bet_unit(low, high)
    print(f"Range {low}-{high}: bets={bets}, total profit={profit:.2f}, avg={avg:.4f}")