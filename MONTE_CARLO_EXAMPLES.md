# Monte Carlo Backtester - Usage Examples

## 🎯 Common Use Cases

### Example 1: Quick Standard Backtest
```bash
python monte-carlo-backtest.py --runs 1000 --report standard-backtest.html
```

**What this does:**
- Runs 1000 Monte Carlo simulations
- Uses default parameters (RVR=2.0, SL=12%, Size=3%)
- Generates beautiful HTML report
- Takes ~5 minutes

**Use when:** You want a quick assessment of strategy performance

---

### Example 2: Full Sensitivity Analysis
```bash
python monte-carlo-backtest.py --sensitivity --report sensitivity-analysis.html
```

**What this does:**
- Tests 27 parameter combinations
- RVR: 1.5, 2.0, 2.5
- Stop Loss: 10%, 12%, 15%
- Position Size: 2%, 3%, 5%
- 100 sims per combination = 2,700 total sims
- Generates heat map showing optimal parameters

**Use when:** You're optimizing your strategy and want to find best parameter settings

---

### Example 3: Stress Test
```bash
python monte-carlo-backtest.py --stress --runs 500 --report stress-test.html
```

**What this does:**
- Simulates extreme market conditions
- 2x volatility (wild price swings)
- 2x slippage (poor execution)
- 50% reduced liquidity
- Shows worst-case scenarios

**Use when:** You want to know if your strategy survives market crashes

---

### Example 4: Custom Configuration
```bash
# Edit backtest-config.json first, then:
python monte-carlo-backtest.py --config backtest-config.json --runs 1000 --report custom.html
```

**Use when:** You have specific parameter ranges to test

---

### Example 5: Quick Test Run (Fast)
```bash
python monte-carlo-backtest.py --runs 100 --report quick-test.html
```

**What this does:**
- Only 100 simulations (very fast, ~30 seconds)
- Good for testing changes
- Less statistically robust

**Use when:** Developing or debugging

---

## 📊 Understanding the Report

### Key Sections

#### 1. Summary Metrics (Top Cards)
- **Average Return:** Your expected profit/loss
- **Sharpe Ratio:** Risk-adjusted performance (>1.0 is good, >2.0 is excellent)
- **Win Rate:** Percentage of winning trades
- **Max Drawdown (95th):** You have 95% chance your worst drawdown is below this
- **Probability of Ruin:** Chance of hitting -25% circuit breaker

#### 2. Distribution Charts
- **Returns Histogram:** Shows range of possible outcomes
  - Wide spread = high variance
  - Shifted right = positive expected value
  
- **Sharpe Ratio Distribution:** Consistency metric
  - Tight distribution = reliable strategy
  - High average = good risk-adjusted returns

- **Drawdown Histogram:** Risk visualization
  - Long tail to right = occasional large losses
  - Most mass on left = usually small drawdowns

#### 3. Drawdown Analysis Table
Shows what drawdown to expect at different confidence levels:
- **50th percentile:** Half the time, DD is below this (typical)
- **95th percentile:** 95% of the time, DD is below this (planning)
- **99th percentile:** Worst-case scenario (stress planning)

#### 4. Sensitivity Analysis (if run)
Heat map showing which parameters work best:
- **Green areas:** Good performance
- **Red areas:** Poor performance
- Find the sweet spot!

---

## 🎓 Interpreting Results

### Good Strategy Signals ✅
- Average return > 10%
- Sharpe ratio > 1.0
- Win rate > 55%
- Max drawdown < 20%
- Probability of ruin < 5%

### Warning Signs ⚠️
- Negative average return (loses money)
- Sharpe ratio < 0.5 (poor risk-adjusted returns)
- Win rate < 45% (loses too often)
- Max drawdown > 25% (hits circuit breaker)
- Probability of ruin > 10% (too risky)

### Red Flags 🚩
- Sharpe ratio < 0 (would be better off not trading)
- Probability of ruin > 20% (strategy is gambling)
- 95th percentile drawdown > 30% (excessive risk)

---

## 🔬 Advanced Usage

### Batch Testing Multiple Configurations
```bash
# Test conservative strategy
python monte-carlo-backtest.py --config conservative.json --report conservative.html

# Test aggressive strategy
python monte-carlo-backtest.py --config aggressive.json --report aggressive.html

# Compare reports to find best risk/reward
```

### Full Analysis Pipeline
```bash
# Step 1: Quick test
python monte-carlo-backtest.py --runs 100 --report quick.html

# Step 2: Full simulation
python monte-carlo-backtest.py --runs 1000 --report full.html

# Step 3: Sensitivity analysis
python monte-carlo-backtest.py --sensitivity --report sensitivity.html

# Step 4: Stress test
python monte-carlo-backtest.py --stress --runs 500 --report stress.html
```

---

## 📈 Real-World Example

Let's say you run the backtester and get:
```
Average Return: +15.34% [11.23%, 19.45%]
Sharpe Ratio: 1.567 [1.234, 1.890]
Win Rate: 62.1% [58.4%, 65.8%]
Max Drawdown (95th): 16.23%
Probability of Ruin: 1.80%
```

**What this means:**
- ✅ **Return:** Expect ~15% profit, likely between 11-19%
- ✅ **Sharpe:** Good risk-adjusted returns (1.567 is solid)
- ✅ **Win Rate:** You win ~62% of trades
- ✅ **Drawdown:** 95% chance worst loss is under 16%
- ✅ **Ruin Risk:** Only 1.8% chance of catastrophic loss

**Decision:** This is a strong strategy worth trading live!

---

Now let's say sensitivity analysis shows:
```
Best parameters: RVR=2.5, SL=10%, Size=2%
Worst parameters: RVR=1.5, SL=15%, Size=5%
```

**What this means:**
- Higher RVR threshold (2.5) = better quality trades
- Tighter stop loss (10%) = cut losses faster
- Smaller position size (2%) = better risk management

**Action:** Adjust your trading config to use the optimal parameters!

---

## 🛡️ Risk Management Insights

### From Drawdown Analysis
If your 95th percentile drawdown is 18%:
- Keep **2x buffer:** Have 36% in reserves
- Set **alerts:** Notify at 15% drawdown
- **Circuit breaker:** Stop at 25% drawdown

### From Probability of Ruin
If probability of ruin is 3%:
- You have **97% chance** of not blowing up
- But **3% chance** is real - prepare mentally
- Consider **position sizing** to reduce this

### From Recovery Time
If average recovery is 14 days:
- After a drawdown, expect **2 weeks** to recover
- Don't panic and change strategy during this period
- Have **patience** and trust the system

---

## 🎉 Summary

The Monte Carlo backtester gives you:
1. **Expected performance** (average metrics)
2. **Confidence ranges** (95% intervals)
3. **Risk assessment** (drawdowns, ruin probability)
4. **Parameter optimization** (sensitivity analysis)
5. **Stress testing** (extreme scenarios)

Use all of this together to:
- Build **confidence** in your strategy
- **Optimize** parameters for best risk/reward
- **Prepare** for worst-case scenarios
- Make **informed decisions** about position sizing

Great success! 🚀
