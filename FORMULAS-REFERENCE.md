# Portfolio Optimizer - Formula Reference

Quick reference for all mathematical formulas used in the portfolio optimizer.

## 🎯 Kelly Criterion

### Basic Kelly Formula (General)
```
f = (bp - q) / b
```
Where:
- `f` = fraction of bankroll to bet
- `b` = net odds received (e.g., 2 for 2:1 odds)
- `p` = probability of winning
- `q` = probability of losing = (1 - p)

### Kelly Formula for Prediction Markets
```
f = (p - P) / (1 - P)
```
Where:
- `p` = your estimated probability of winning (0-1)
- `P` = current market price (0-1)
- `f` = Kelly fraction (0-1)

**Example:**
```
p = 0.60 (you think 60% chance)
P = 0.50 (market price is 50¢)
f = (0.60 - 0.50) / (1 - 0.50) = 0.20 = 20% of bankroll
```

### Fractional Kelly
```
f_adjusted = f × fractional_kelly
```

**Example with 25% Kelly:**
```
f = 0.20 (from Kelly formula)
f_adjusted = 0.20 × 0.25 = 0.05 = 5% of bankroll
```

### Dollar Amount
```
dollar_amount = f_adjusted × bankroll
```

**Example:**
```
f_adjusted = 0.05
bankroll = $10,000
dollar_amount = 0.05 × $10,000 = $500
```

## 📊 Risk Metrics

### Edge
```
edge = p - P
```

**Example:**
```
p = 0.60, P = 0.50
edge = 0.60 - 0.50 = 0.10 = +10% edge
```

### Expected Value (EV)
For prediction markets:
```
EV = p × (1/P - 1) - (1-p)
```

Simplified:
```
EV = p - P = edge
```

**Example:**
```
p = 0.60, P = 0.50
EV = 0.60 - 0.50 = 0.10 = +$0.10 per dollar bet
```

### Sharpe Ratio
```
Sharpe = (mean_return - risk_free_rate) / std_dev_returns
```

**Example:**
```
mean_return = 0.08 (8% average return)
risk_free_rate = 0.00 (assume 0%)
std_dev = 0.12 (12% volatility)
Sharpe = 0.08 / 0.12 = 0.667
```

**Interpretation:**
- Sharpe < 1.0: Poor risk-adjusted returns
- Sharpe = 1.0: Good risk-adjusted returns
- Sharpe > 2.0: Excellent risk-adjusted returns

### Sortino Ratio
```
Sortino = (mean_return - risk_free_rate) / downside_deviation
```

Where downside_deviation only considers negative returns.

**Example:**
```
mean_return = 0.08
downside_deviation = 0.08 (only from losing periods)
Sortino = 0.08 / 0.08 = 1.0
```

**Note:** Sortino > Sharpe indicates good downside risk management.

### Maximum Drawdown
```
For each point in time:
  drawdown_t = (value_t - peak_value) / peak_value

max_drawdown = min(all drawdowns)
```

**Example:**
```
Portfolio values: [100, 120, 110, 130, 90, 100]
Peak progresses: [100, 120, 120, 130, 130, 130]
Drawdowns: [0%, 0%, -8.3%, 0%, -30.8%, -23.1%]
Max drawdown = -30.8%
```

### Herfindahl-Hirschman Index (HHI)
```
HHI = Σ(market_share_i)²
```

**Example:**
```
5 positions: $2000, $1500, $1000, $800, $700
Total: $6000
Shares: 0.333, 0.250, 0.167, 0.133, 0.117

HHI = 0.333² + 0.250² + 0.167² + 0.133² + 0.117²
    = 0.111 + 0.063 + 0.028 + 0.018 + 0.014
    = 0.234
```

**Interpretation:**
- HHI < 0.15: Low concentration (well diversified)
- 0.15 ≤ HHI < 0.25: Moderate concentration
- HHI ≥ 0.25: High concentration risk

### Value at Risk (VaR)
```
VaR_α = percentile(returns, 1 - α)
```

**Example (95% VaR):**
```
Returns (sorted): [-20%, -15%, -10%, -5%, 0%, 5%, 10%, 15%, 20%]
95% VaR = 5th percentile = -15%

If portfolio = $10,000:
VaR = $10,000 × 0.15 = $1,500
```

**Interpretation:** 95% confident you won't lose more than $1,500.

## 🔗 Correlation Adjustments

### Correlation Penalty
```
if |correlation| > 0.7:
    penalty = 0.50 (reduce by 50%)
elif |correlation| > 0.4:
    penalty = 0.30 (reduce by 30%)
elif |correlation| > 0.1:
    penalty = 0.10 (reduce by 10%)
else:
    penalty = 0.00 (no penalty)

adjusted_kelly = kelly_fraction × (1 - penalty)
```

**Example:**
```
Kelly fraction = 0.20 (20% of bankroll)
Correlation with another position = 0.85 (high)
Penalty = 0.50
Adjusted Kelly = 0.20 × (1 - 0.50) = 0.10 = 10% of bankroll
```

### Correlation Coefficient
```
correlation = cov(X, Y) / (std(X) × std(Y))
```

Range: -1 to +1
- -1: Perfect negative correlation
- 0: No correlation
- +1: Perfect positive correlation

## 🎯 Sector Limits

### Sector Exposure Check
```
For each sector:
  sector_total = Σ(allocations in sector)
  
  if sector_total > sector_limit:
    reduction_factor = sector_limit / sector_total
    
    For each position in sector:
      adjusted_allocation = allocation × reduction_factor
```

**Example:**
```
Crypto positions: $4,000 total
Crypto limit: 30% of $10,000 = $3,000
Reduction factor = $3,000 / $4,000 = 0.75

Position A: $2,000 → $2,000 × 0.75 = $1,500
Position B: $2,000 → $2,000 × 0.75 = $1,500
New total: $3,000 ✓
```

## 📈 Rebalancing

### Drift Calculation
```
drift = |optimal_amount - current_amount| / bankroll
```

**Example:**
```
Optimal: $1,500
Current: $2,000
Bankroll: $10,000
drift = |1500 - 2000| / 10000 = 0.05 = 5%
```

### Rebalance Order
```
if drift > threshold:
    order_amount = optimal_amount - current_amount
```

**Example:**
```
drift = 6% (> 5% threshold)
order_amount = $1,500 - $2,000 = -$500 (sell $500)
```

## 📊 Statistical Formulas

### Mean
```
mean = Σ(values) / n
```

### Variance
```
variance = Σ(x_i - mean)² / (n - 1)
```

### Standard Deviation
```
std_dev = √variance
```

### Downside Deviation
```
downside_dev = √(Σ(negative_returns - mean)² / n_negative)
```

## 🎲 Example: Complete Calculation

**Given:**
- Bankroll: $10,000
- Market: BTC > $100k by EOY
- Your probability: 65%
- Market price: 55%
- Fractional Kelly: 25%
- Correlation with ETH position: 0.85

**Step 1: Calculate Kelly fraction**
```
f = (p - P) / (1 - P)
f = (0.65 - 0.55) / (1 - 0.55)
f = 0.10 / 0.45
f = 0.222 = 22.2%
```

**Step 2: Apply fractional Kelly**
```
f_adjusted = 0.222 × 0.25 = 0.0555 = 5.55%
```

**Step 3: Apply correlation penalty**
```
Correlation = 0.85 (> 0.7)
Penalty = 50%
f_final = 0.0555 × (1 - 0.50) = 0.0278 = 2.78%
```

**Step 4: Calculate dollar amount**
```
amount = 0.0278 × $10,000 = $278
```

**Step 5: Check sector limit**
```
Crypto limit: 30% = $3,000
Current crypto total (including this): $278
Within limit ✓
```

**Final allocation: $278**

## 📝 Notes

### When Kelly Says Don't Bet
```
if p ≤ P:
    edge ≤ 0
    kelly_fraction = 0
    → Don't bet!
```

### Maximum Kelly Fraction
Kelly fraction is capped at 1.0 (100% of bankroll). In practice, anything above 0.25 should be scrutinized carefully.

### Probability Calibration
The quality of Kelly sizing depends entirely on probability estimation. Consider:
- Historical frequency
- Base rates
- Recent news/events
- Market liquidity
- Time decay

### Risk of Ruin
Even with Kelly sizing, there's always risk:
```
P(ruin) > 0 for any betting system
```

Key safeguards:
1. Fractional Kelly (25% recommended)
2. Correlation adjustments
3. Sector limits
4. Diversification
5. Stop-losses

## 🔢 Quick Reference Table

| Metric | Formula | Good Value | Bad Value |
|--------|---------|------------|-----------|
| Edge | p - P | > 0.05 | < 0.02 |
| Kelly % | (p-P)/(1-P) | 0.10-0.30 | > 0.50 |
| Sharpe | R/σ | > 1.5 | < 0.5 |
| Sortino | R/σ_down | > 2.0 | < 1.0 |
| HHI | Σs² | < 0.15 | > 0.25 |
| Max DD | peak→trough | < 15% | > 30% |
| VaR 95% | 5th %ile | < 10% | > 25% |

## 💡 Remember

**Kelly Criterion Assumptions:**
1. You know the true probabilities (you don't!)
2. You can bet fractionally (often you can't)
3. Outcomes are independent (they often aren't)
4. You have infinite time horizon (you don't)

**Use with caution and always bet less than full Kelly!**
