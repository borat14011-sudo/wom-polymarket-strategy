import json
import math

with open('active-markets.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

markets = data['markets']
print(f"Total active markets: {len(markets)}")

# Extract Yes prices (assuming first outcome is Yes)
yes_prices = []
no_prices = []
for m in markets:
    outcomes = json.loads(m['outcomes'])
    prices = json.loads(m['outcomePrices'])
    # assume Yes is first, No second
    yes_prices.append(float(prices[0]))
    no_prices.append(float(prices[1]))

print(f"Yes price mean: {sum(yes_prices)/len(yes_prices):.3f}")
print(f"No price mean: {sum(no_prices)/len(no_prices):.3f}")

# Distribution
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

# Compute expected return after fees (assuming true probability = market price)
fees_entry = 0.02
fees_exit = 0.02
def expected_return(p):
    # p = market price of Yes
    # true probability = p (efficient market)
    # Expected profit per share: p*(1-fees_exit) - p*(1+fees_entry) = -p*(fees_entry+fees_exit)
    return -p * (fees_entry + fees_exit)

# Add spread cost: assume we buy at bestAsk (or outcomePrices which maybe mid?)
# We'll use outcomePrices as mid, spread = bestAsk - bestBid
# We'll compute average spread
spreads = []
for m in markets:
    if 'bestBid' in m and 'bestAsk' in m:
        bid = m['bestBid']
        ask = m['bestAsk']
        if bid is not None and ask is not None:
            spreads.append(ask - bid)
print(f"Average spread: {sum(spreads)/len(spreads):.4f}" if spreads else "No spread data")

# Expected return with spread: assume we buy at ask (price = p + half spread)
# Let's compute for each market
returns = []
for m in markets:
    prices = json.loads(m['outcomePrices'])
    p = float(prices[0])
    # assume we pay ask = p + half spread (if spread data)
    if 'bestBid' in m and 'bestAsk' in m and m['bestBid'] is not None and m['bestAsk'] is not None:
        spread = m['bestAsk'] - m['bestBid']
        p_effective = p + spread/2
    else:
        p_effective = p
    ret = expected_return(p_effective)
    returns.append(ret)

print(f"Average expected return per bet (with fees): {sum(returns)/len(returns):.4f}")
print("This is negative for all markets (due to fees).")

# Now compute for favorites (p > 0.8) vs longshots (p < 0.2)
fav_returns = [r for i, r in enumerate(returns) if yes_prices[i] > 0.8]
long_returns = [r for i, r in enumerate(returns) if yes_prices[i] < 0.2]
print(f"Favorites count: {len(fav_returns)} avg return: {sum(fav_returns)/len(fav_returns) if fav_returns else 0:.4f}")
print(f"Longshots count: {len(long_returns)} avg return: {sum(long_returns)/len(long_returns) if long_returns else 0:.4f}")

# Compute Sharpe ratio? Not possible without volatility.

# However, if there is mispricing (true probability not equal to market price), we could have edge.
# Let's assume we have a model that predicts true probability with some error.
# Not enough data.

# Let's compute the break-even true probability needed for positive EV after fees.
def break_even_prob(p, fees_entry=0.02, fees_exit=0.02):
    # Solve for q: q*(1-fees_exit) - p*(1+fees_entry) = 0
    # q = p*(1+fees_entry) / (1-fees_exit)
    return p * (1 + fees_entry) / (1 - fees_exit)

print("\nBreak-even true probability needed for positive EV:")
for p in [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
    q = break_even_prob(p)
    print(f"Market price {p:.2f} -> need true probability > {q:.4f} (delta {q-p:.4f})")