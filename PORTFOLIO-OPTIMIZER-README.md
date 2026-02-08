# Portfolio Optimizer for Polymarket Trading

A sophisticated multi-market portfolio optimization module implementing Kelly Criterion with correlation adjustments, sector exposure limits, and comprehensive risk analytics.

## 🎯 Features

### 1. **Kelly Criterion with Correlation Adjustment**
- Calculates optimal position sizing for each market
- Accounts for correlations between markets
- Fractional Kelly (default 25%) for conservative sizing
- Automatic position reduction for highly correlated bets

### 2. **Correlation Matrix**
- Track correlation between market movements
- Reduce position size based on correlation strength:
  - High correlation (>0.7): reduce by 50%
  - Medium correlation (0.4-0.7): reduce by 30%
  - Low correlation (<0.4): reduce by 10%
- Alerts on over-concentration

### 3. **Sector Exposure Limits**
- Max 30% in crypto markets
- Max 30% in politics
- Max 20% in sports
- Max 20% in other
- Automatic proportional reduction when limits exceeded

### 4. **Dynamic Rebalancing**
- Suggests rebalance when drift >5% from optimal
- Priority order: sells first (risk reduction), then buys
- Buys prioritized by edge (best opportunities first)

### 5. **Risk-Adjusted Returns**
- **Sharpe Ratio**: Risk-adjusted returns vs total volatility
- **Sortino Ratio**: Risk-adjusted returns vs downside volatility only
- **Maximum Drawdown**: Worst peak-to-trough decline

### 6. **Portfolio Metrics**
- Total exposure and bankroll utilization
- Sector breakdown with limit compliance
- **HHI (Herfindahl-Hirschman Index)**: Concentration risk
  - HHI < 0.15: Low concentration ✓
  - 0.15 < HHI < 0.25: Moderate concentration
  - HHI > 0.25: High concentration risk ⚠️
- Expected return across portfolio
- **VaR (Value at Risk)**: Maximum loss at 95% confidence

### 7. **Kelly Criterion Formula**

For prediction markets, the Kelly formula is:

```
f = (p - P) / (1 - P)
```

Where:
- `p` = your estimated probability of winning
- `P` = current market price
- `f` = fraction of bankroll to bet

Example: If you think probability is 60% but market price is 50%:
```
f = (0.60 - 0.50) / (1 - 0.50) = 0.10 / 0.50 = 0.20 = 20% of bankroll
```

With 25% fractional Kelly: 20% × 0.25 = 5% of bankroll

## 📦 Installation

```bash
# Clone or download the files
git clone <repo> or copy files

# Optional: Install numpy for better performance
pip install numpy

# If numpy not available, pure Python fallback is automatic
```

## 🚀 Usage

### CLI Interface

```bash
# Analyze current portfolio
python portfolio-optimizer.py --analyze

# Calculate optimal allocation
python portfolio-optimizer.py --optimize

# Generate rebalancing orders
python portfolio-optimizer.py --rebalance

# Show risk metrics for all positions
python portfolio-optimizer.py --risk

# Run example with 5 hypothetical markets
python portfolio-optimizer.py --example

# Run all analyses
python portfolio-optimizer.py --all
```

### API Interface

```python
from portfolio_optimizer import PortfolioOptimizer, Sector

# Initialize with bankroll and fractional Kelly
optimizer = PortfolioOptimizer(bankroll=10000, fractional_kelly=0.25)

# Add positions
optimizer.add_position(
    market_id="btc_100k_eoy",
    amount=1500,  # Current position size
    probability=0.65,  # Your probability estimate
    market_price=0.55,  # Current market price
    sector=Sector.CRYPTO,
    historical_returns=[0.15, -0.08, 0.22, 0.10]  # Optional
)

optimizer.add_position(
    market_id="dem_wins_2024",
    amount=2000,
    probability=0.52,
    market_price=0.48,
    sector=Sector.POLITICS
)

# Set correlations between markets
optimizer.set_correlation("btc_100k_eoy", "eth_5k_q2", 0.85)

# Run optimization
result = optimizer.optimize()
allocations = result['optimal_allocations']
analysis = result['current_analysis']

# Get rebalancing orders
orders = optimizer.calculate_rebalance_orders()

# Calculate risk metrics
risk_metrics = optimizer.calculate_risk_metrics()

# Print formatted output
optimizer.print_analysis()
optimizer.print_optimization()
optimizer.print_rebalance()
optimizer.print_risk_metrics()
```

## 📊 Example Output

### Portfolio Analysis
```
============================================================
📊 PORTFOLIO ANALYSIS
============================================================

💰 Total Exposure: $6,000.00
💵 Bankroll: $10,000.00
📈 Utilization: 60.0%
💸 Expected Return: $310.00

🎯 Sector Breakdown:
  CRYPTO      : $2,700.00 (27.0%) [limit: 30%]
  POLITICS    : $2,000.00 (20.0%) [limit: 30%]
  SPORTS      :   $800.00 ( 8.0%) [limit: 20%]
  OTHER       :   $500.00 ( 5.0%) [limit: 20%]

⚠️  Risk Metrics:
  HHI (concentration): 0.212
    → Moderate concentration
  VaR (95%): $156.80
  Positions: 5

🔗 High Correlations:
  btc_100k_eoy ↔ eth_5k_q2: 0.850
```

### Optimal Allocation
```
============================================================
🎯 OPTIMAL ALLOCATION (Kelly Criterion)
============================================================

Fractional Kelly: 25%
Bankroll: $10,000.00

btc_100k_eoy         $ 1,250.00 (12.5%) (-250.00)
  Current: $1,500.00 | Edge: +0.100 | Prob: 0.65 | Price: 0.55

dem_win_2024         $ 2,000.00 (20.0%) 
  Current: $2,000.00 | Edge: +0.040 | Prob: 0.52 | Price: 0.48

lakers_champion      $   900.00 ( 9.0%) (+100.00)
  Current: $800.00 | Edge: +0.100 | Prob: 0.25 | Price: 0.15
```

### Rebalancing Orders
```
============================================================
🔄 REBALANCING ORDERS
============================================================

📉 SELL (Risk Reduction):
  btc_100k_eoy         $250.00

📈 BUY (New Positions):
  lakers_champion      $100.00 (edge: +0.100)
```

### Risk Metrics
```
============================================================
📊 RISK METRICS BY POSITION
============================================================

btc_100k_eoy:
  Edge: +0.100
  Expected Value: $+0.1000
  Sharpe Ratio: 1.234
  Sortino Ratio: 1.567
  Max Drawdown: -15.2%

dem_win_2024:
  Edge: +0.040
  Expected Value: $+0.0400
  Sharpe Ratio: 0.892
  Sortino Ratio: 1.123
  Max Drawdown: -8.3%
```

## 🔬 Key Concepts

### Kelly Criterion
The Kelly Criterion is a formula for optimal bet sizing that maximizes long-term growth while managing risk. It balances:
- **Expected value** (your edge)
- **Win probability** (how often you win)
- **Odds** (payout ratio)

### Fractional Kelly
Full Kelly can be aggressive. Most professionals use fractional Kelly:
- **25% Kelly** (recommended): Conservative, reduces volatility
- **50% Kelly**: Moderate risk/reward
- **100% Kelly**: Full Kelly, maximum growth but high volatility

### Correlation Adjustment
When bets are correlated, they don't provide independent diversification. The optimizer:
1. Calculates correlation between markets
2. Reduces position size for correlated bets
3. Prevents over-concentration in similar outcomes

Example: BTC and ETH are highly correlated (0.85), so positions in both are reduced to avoid doubling down on crypto risk.

### Sector Limits
Prevents over-concentration in any single sector:
- **Crypto**: 30% max (volatile, correlated)
- **Politics**: 30% max (event-driven)
- **Sports**: 20% max (less predictable)
- **Other**: 20% max (miscellaneous)

### HHI (Concentration Risk)
Herfindahl-Hirschman Index measures portfolio concentration:
```
HHI = Σ(market_share²)
```

- **HHI = 1.0**: All money in one position (maximum concentration)
- **HHI = 0.2**: Evenly split across 5 positions
- **HHI < 0.15**: Well diversified

### VaR (Value at Risk)
VaR estimates potential loss at a confidence level:
- **VaR 95% = $500**: 95% confident you won't lose more than $500
- **VaR 99% = $750**: 99% confident you won't lose more than $750

## 🎓 Example Walkthrough

Let's say you have $10,000 and find these opportunities:

| Market | Your Prob | Market Price | Edge | Current Position |
|--------|-----------|--------------|------|------------------|
| BTC >$100k | 65% | 55% | +10% | $1,500 |
| ETH >$5k | 58% | 50% | +8% | $1,200 |
| Dem Wins | 52% | 48% | +4% | $2,000 |

**Step 1: Calculate Kelly fractions**
```
BTC: (0.65 - 0.55) / (1 - 0.55) = 0.22 = 22% of bankroll
ETH: (0.58 - 0.50) / (1 - 0.50) = 0.16 = 16% of bankroll
Dem: (0.52 - 0.48) / (1 - 0.48) = 0.08 = 8% of bankroll
```

**Step 2: Apply 25% fractional Kelly**
```
BTC: 22% × 0.25 = 5.5% = $550
ETH: 16% × 0.25 = 4.0% = $400
Dem: 8% × 0.25 = 2.0% = $200
```

**Step 3: Adjust for correlation**
BTC and ETH are correlated (0.85), so reduce both by 50%:
```
BTC: $550 × 0.5 = $275
ETH: $400 × 0.5 = $200
Dem: $200 (no change)
```

**Step 4: Check sector limits**
Crypto total: $475 (4.75%) - within 30% limit ✓

**Result:** Optimizer suggests reducing BTC from $1,500 to $275 and ETH from $1,200 to $200. Your current positions are overweight due to high correlation risk.

## ⚠️ Important Notes

### Risk Warnings
- **Kelly is aggressive**: Even fractional Kelly can lead to significant drawdowns
- **Probability estimates are critical**: Garbage in, garbage out
- **Correlation estimates matter**: Underestimating correlation increases risk
- **Historical returns ≠ future returns**: Past performance doesn't guarantee future results

### Best Practices
1. **Use conservative Kelly fractions** (25% or lower)
2. **Regularly update probability estimates** as new information emerges
3. **Monitor correlations** between your positions
4. **Respect sector limits** to avoid concentration risk
5. **Rebalance periodically** when drift exceeds threshold
6. **Track historical performance** to calculate Sharpe/Sortino ratios
7. **Set stop-losses** for individual positions
8. **Don't bet more than you can afford to lose**

### When to Use This Tool
- ✓ Multiple positions across different markets
- ✓ Want to optimize position sizing
- ✓ Need to manage correlation risk
- ✓ Want to track risk metrics
- ✓ Need rebalancing suggestions

### When NOT to Use This Tool
- ✗ Single bet with all capital
- ✗ No edge over market (probability ≤ market price)
- ✗ Can't estimate probabilities reliably
- ✗ Don't understand Kelly Criterion
- ✗ Need guaranteed returns (doesn't exist!)

## 📚 Further Reading

- [Kelly Criterion Wikipedia](https://en.wikipedia.org/wiki/Kelly_criterion)
- [Fortune's Formula](https://www.amazon.com/Fortunes-Formula-Scientific-Betting-Casinos/dp/0809045990) by William Poundstone
- [Quantitative Trading](https://www.amazon.com/Quantitative-Trading-Build-Algorithmic-Business/dp/1119800064) by Ernest Chan
- [Polymarket Documentation](https://docs.polymarket.com/)

## 🤝 Contributing

This module is designed to be extended. Possible enhancements:
- Integration with Polymarket API for live data
- Machine learning for probability estimation
- Backtesting framework
- Real-time portfolio monitoring
- Telegram/Discord notifications
- Multi-account support

## 📝 License

MIT License - use at your own risk!

## ⚡ Great Success!

Built with love for the Polymarket trading community. May your edges be positive and your Kelly fractions optimal! 🎰📈
