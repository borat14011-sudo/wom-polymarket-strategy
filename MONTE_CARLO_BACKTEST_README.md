# Monte Carlo Backtester for Polymarket Trading System

## 🚀 Quick Start

```bash
# Basic Monte Carlo simulation (1000 runs)
python monte-carlo-backtest.py --runs 1000 --report results.html

# Parameter sensitivity analysis
python monte-carlo-backtest.py --sensitivity --report sensitivity.html

# Stress test (high volatility, 2x slippage)
python monte-carlo-backtest.py --stress --runs 500 --report stress-test.html

# Custom configuration
python monte-carlo-backtest.py --config backtest-config.json --report custom.html
```

## 📋 Features

### 1. Monte Carlo Simulation
- **1000+ randomized simulations** with variations in:
  - Entry timing (±1 hour jitter)
  - Slippage (1-3% random range)
  - Signal threshold variations (±5%)
- Generates distribution of outcomes
- Fast execution: ~1000 sims in under 5 minutes

### 2. Stress Testing
- 2x volatility multiplier
- 2x slippage
- Reduced liquidity conditions
- Tests strategy resilience

### 3. Sensitivity Analysis
- Tests parameter combinations:
  - **RVR threshold:** 1.5, 2.0, 2.5
  - **Stop loss:** 10%, 12%, 15%
  - **Position size:** 2%, 3%, 5%
- Generates heat maps showing optimal parameters
- 27 total combinations tested

### 4. Bootstrap Confidence Intervals
- 95% confidence intervals for:
  - Sharpe ratio
  - Win rate
  - Total return
  - Max drawdown

### 5. Drawdown Analysis
- Maximum drawdown distribution
- Percentile analysis (50th, 75th, 90th, 95th, 99th)
- Expected recovery time
- Probability of ruin (circuit breaker)

### 6. Beautiful HTML Reports
- Interactive Plotly charts
- Distribution histograms
- Parameter sensitivity heat maps
- Risk metrics with confidence intervals
- Professional styling with gradient backgrounds

## 🎯 Configuration

Edit `backtest-config.json` to customize:

```json
{
  "trade_config": {
    "rvr_threshold": 2.0,           // Risk/Reward Ratio threshold
    "stop_loss_pct": 0.12,          // 12% stop loss
    "position_size_pct": 0.03,      // 3% per trade
    "max_positions": 5,             // Max concurrent positions
    "signal_threshold": 0.65,       // Entry confidence threshold
    "max_drawdown_circuit_breaker": 0.25,  // 25% max DD
    "daily_loss_limit": 0.05        // 5% daily loss limit
  },
  "sim_config": {
    "num_runs": 1000,
    "entry_timing_jitter_hours": 1.0,
    "slippage_range": [0.01, 0.03],
    "signal_threshold_variance": 0.05
  }
}
```

## 📊 Output Metrics

### Performance Metrics
- **Total Return:** Average P&L across simulations
- **Sharpe Ratio:** Risk-adjusted returns
- **Win Rate:** Percentage of profitable trades
- **Max Drawdown:** Largest peak-to-trough decline

### Risk Metrics
- **Probability of Ruin:** Chance of hitting circuit breaker
- **Expected Recovery Time:** Days to recover from drawdown
- **Drawdown Percentiles:** Distribution analysis

### Distribution Analysis
- Returns histogram
- Sharpe ratio distribution
- Drawdown distribution
- All with 95% confidence intervals

## 🔬 Sensitivity Analysis

The sensitivity analysis tests all combinations of:
- 3 RVR thresholds
- 3 stop loss levels
- 3 position sizes

Results are ranked by average return, showing which parameter combinations perform best.

## 🔥 Stress Testing

Stress tests simulate extreme market conditions:
- **High volatility:** 2x normal price movements
- **High slippage:** 2x normal slippage (2-6%)
- **Reduced liquidity:** 50% liquidity reduction

Use this to understand worst-case scenarios and ensure your strategy is robust.

## 📈 Example Output

```
🎲 MONTE CARLO SIMULATION
Running 1000 simulations...
  Progress: 100/1000 (145.2 sims/sec, ~6s remaining)
  Progress: 200/1000 (156.8 sims/sec, ~5s remaining)
  ...
✅ Completed in 6.4 seconds (156.3 sims/sec)

📈 CALCULATING CONFIDENCE INTERVALS

📉 DRAWDOWN ANALYSIS

============================================================
📊 SUMMARY STATISTICS
============================================================
Total Simulations: 1,000

Average Return: +12.45% [8.23%, 16.78%]
Sharpe Ratio: 1.234 [0.987, 1.456]
Win Rate: 58.3% [55.1%, 61.4%]

Max Drawdown (95th): 18.45%
Probability of Ruin: 2.30%
Avg Recovery Time: 12 days
============================================================

📊 GENERATING HTML REPORT: results.html
✅ Report saved: results.html

✅ Analysis complete! Great success! 🎉
```

## 🧪 Dependencies

- **Python 3.7+**
- **NumPy** (optional, recommended for performance)
- **SciPy** (optional)

Falls back to pure Python if NumPy/SciPy not available.

```bash
# Install dependencies (optional but recommended)
pip install numpy scipy
```

## 🎨 HTML Report Features

The generated HTML report includes:
- Responsive design
- Interactive Plotly charts
- Color-coded metrics (green = good, red = bad)
- Distribution histograms
- Sensitivity heat maps
- Professional gradient styling
- Risk level badges
- Confidence interval displays

## 📝 Notes

- **Simulation speed:** ~150-200 sims/sec on modern hardware
- **Memory usage:** Low, scales linearly with number of runs
- **Output format:** HTML with embedded JavaScript (self-contained)
- **Browser compatibility:** All modern browsers

## 🚦 Risk Warnings

⚠️ **This is a simulation based on historical patterns**
- Past performance ≠ future results
- Real market conditions may differ
- Use for research and strategy development only
- Not financial advice

## 🛠️ Troubleshooting

**Slow performance?**
- Install NumPy: `pip install numpy`
- Reduce number of runs: `--runs 500`
- Skip sensitivity analysis for faster results

**Charts not showing?**
- Check internet connection (loads Plotly from CDN)
- View in modern browser (Chrome, Firefox, Edge, Safari)

**Need more history?**
- Edit `MarketDataSimulator(days=90)` to increase days
- More data = longer runtime but more realistic

## 📚 Further Customization

Edit the script to:
- Add more parameters to sensitivity analysis
- Change market data generation logic
- Customize HTML report styling
- Add additional risk metrics
- Export raw data to CSV

Great success! 🎉
