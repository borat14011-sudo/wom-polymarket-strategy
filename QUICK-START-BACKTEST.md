# 🚀 Quick Start - Backtesting Engine

**Get results in 3 commands** (takes ~2 minutes)

---

## Step 1: Install Dependencies

```bash
pip install pandas numpy scipy scikit-learn matplotlib
```

Optional (for interactive charts):
```bash
pip install plotly
```

---

## Step 2: Generate Sample Data

```bash
python generate-sample-data.py
```

**Output:**
```
============================================================
SAMPLE DATA GENERATOR
============================================================
Generating 15 markets with 60 days of history...

✓ Database created: polymarket_data.db
✓ Generated market 1/15: Bitcoin reaches $100,000 by end of year...
✓ Generated market 2/15: Ethereum ETF approved in Q1 2026...
...
✓ Generated market 15/15: Recession declared in 2026...

✓ Sample data generation complete!
  Markets: 15
  Days: 60
  Snapshots per market: 5,760
  Total snapshots: 86,400

✅ Database ready: polymarket_data.db

Now run: python backtest-engine.py --db polymarket_data.db
```

---

## Step 3: Run Backtest

```bash
python backtest-engine.py
```

**Output:**
```
============================================================
PREDICTION MARKET BACKTESTING ENGINE
============================================================
✓ Loaded 5,760 snapshots across 15 markets
  Date range: 2025-12-07 to 2026-02-05

============================================================
RUNNING BACKTEST
============================================================
Initial capital: $10,000
Walk-forward validation: False

Calculating signals...
Simulating trades...

✓ Backtest complete: 47 trades executed

Calculating performance metrics...
Running bootstrap analysis...

============================================================
PERFORMANCE SUMMARY
============================================================
Total Return:        +18.45% (+$1,845.23)
Win Rate:            57.4% (27/47)
Profit Factor:       1.82
Sharpe Ratio:        1.15
Sortino Ratio:       1.67
Max Drawdown:        -21.3%
Expectancy:          $39.26 per trade
Avg Win:             +12.34%
Avg Loss:            -8.92%
95% CI:              [8.21%, 28.69%]
============================================================

============================================================
GENERATING REPORTS
============================================================
✓ Trade log: backtest_results/trade_log.csv
✓ Metrics JSON: backtest_results/performance_metrics.json
✓ Charts: backtest_results/performance_charts.png
✓ HTML report: backtest_results/backtest_report.html

✓ Reports saved to: backtest_results

✅ Backtest complete!
📁 View results: C:\Users\...\backtest_results
📊 Open: backtest_results\backtest_report.html
```

---

## Step 4: View Results

### Open the HTML Report

**Windows:**
```bash
start backtest_results\backtest_report.html
```

**Mac:**
```bash
open backtest_results/backtest_report.html
```

**Linux:**
```bash
xdg-open backtest_results/backtest_report.html
```

### What You'll See

- 🎯 **Key Performance Metrics** (color-coded cards)
- 📈 **Strategy Validation** (PASS/FAIL table)
- 💰 **Win/Loss Analysis** (detailed breakdown)
- 📊 **Charts** (equity curve, returns distribution, timeline)
- ⏱️ **Trade Statistics** (holding periods, streaks, extremes)

---

## 📊 What the Results Mean

### ✅ Strategy Works If You See:

| Metric | Target | What It Means |
|--------|--------|---------------|
| **Sharpe Ratio** | > 1.0 | Good risk-adjusted returns |
| **Win Rate** | > 50% | More winners than losers |
| **Profit Factor** | > 1.5 | Wins are bigger than losses |
| **Max Drawdown** | < 25% | Manageable risk |

### Example (Good Result):
```
Sharpe Ratio:  1.15  ✓ PASS
Win Rate:      57.4% ✓ PASS
Profit Factor: 1.82  ✓ PASS
Max Drawdown:  21.3% ✓ PASS
```

**This strategy is viable!** → Proceed to paper trading

### Example (Bad Result):
```
Sharpe Ratio:  0.32  ✗ FAIL
Win Rate:      42.1% ✗ FAIL
Profit Factor: 0.87  ✗ FAIL
Max Drawdown:  38.2% ✗ FAIL
```

**This strategy doesn't work** → Adjust parameters or try different approach

---

## 🔧 Advanced Usage

### With Walk-Forward Validation (Recommended)

```bash
python backtest-engine.py --walk-forward
```

This is more realistic and prevents overfitting.

### Custom Capital

```bash
python backtest-engine.py --capital 50000
```

### Custom Output Directory

```bash
python backtest-engine.py --output my_results/
```

### All Options Combined

```bash
python backtest-engine.py \
  --db polymarket_data.db \
  --capital 50000 \
  --output results_$(date +%Y%m%d)/ \
  --walk-forward
```

---

## 📁 Output Files

After running, check `backtest_results/`:

```
backtest_results/
├── backtest_report.html        # Main report (open this!)
├── trade_log.csv              # Every trade with details
├── performance_metrics.json   # Machine-readable metrics
└── performance_charts.png     # Equity curve and charts
```

### Trade Log Example

```csv
entry_time,exit_time,market_question,side,entry_price,exit_price,pnl_net,return_pct,holding_hours,signal_strength,exit_reason
2026-01-15 10:30,2026-01-16 14:45,Bitcoin reaches $100k,YES,0.452,0.489,12.34,3.08,28.25,STRONG,TP1
2026-01-16 08:15,2026-01-17 09:30,Trump wins 2024,NO,0.623,0.587,8.92,2.23,25.25,MODERATE,TP2
...
```

### Metrics JSON Example

```json
{
  "total_trades": 47,
  "win_rate": 57.4,
  "sharpe_ratio": 1.15,
  "max_drawdown_pct": 21.3,
  "total_return_pct": 18.45,
  "profit_factor": 1.82,
  ...
}
```

---

## 🐛 Troubleshooting

### "Python not found"

Install Python 3.9+:
- **Windows**: Download from python.org
- **Mac**: `brew install python`
- **Linux**: `sudo apt install python3`

### "ModuleNotFoundError: No module named 'pandas'"

```bash
pip install pandas numpy scipy scikit-learn matplotlib
```

### "Database not found"

Run `generate-sample-data.py` first to create the database.

### "Only X trades generated (need 30+)"

This happens if:
- Not enough data (collect more)
- Signal thresholds too strict (adjust in code)
- Markets near expiry (filter them out)

**Fix:** Lower thresholds or collect more data.

---

## 🎓 Next Steps After Backtesting

### If Sharpe > 1.0 (Strategy Works):

1. **Week 1-2**: Paper trade (track hypothetical trades)
2. **Week 3-4**: Deploy micro capital ($500-1,000)
3. **Month 2**: Scale to 25% of target capital
4. **Month 3+**: Full deployment if still profitable

### If Sharpe < 0.5 (Strategy Doesn't Work):

**Try These Adjustments:**

1. **Lower signal thresholds** (more trades):
   ```python
   # In backtest-engine.py, line ~60
   rvr_strong=2.5,      # was 3.0
   roc_strong=12.0,     # was 15.0
   ```

2. **Focus on specific categories**:
   - Crypto only (high volatility)
   - Politics only (event-driven)

3. **Adjust exit rules**:
   - Tighter stops (-8% instead of -12%)
   - Earlier profit taking (+12% instead of +15%)

4. **Try alternative strategies**:
   - Mean reversion instead of momentum
   - Market maker approach
   - Arbitrage across platforms

---

## 📚 Read More

- **Full Documentation**: `BACKTEST-ENGINE-README.md`
- **Strategy Framework**: `TRADING-STRATEGY-FRAMEWORK.md`
- **Data Collection**: `DATA-COLLECTION-PIPELINE.md`
- **Delivery Summary**: `BACKTEST-ENGINE-DELIVERY.md`

---

## ⚡ TL;DR

```bash
# 1. Install
pip install pandas numpy scipy scikit-learn matplotlib

# 2. Generate data
python generate-sample-data.py

# 3. Run backtest
python backtest-engine.py

# 4. Open report
start backtest_results/backtest_report.html  # Windows
open backtest_results/backtest_report.html   # Mac
```

**That's it!** Results in ~2 minutes.

---

**Questions?** See `BACKTEST-ENGINE-README.md` for detailed documentation.

**Ready to use real data?** Run `polymarket-data-collector.py` first, then backtest with your database.

🎉 **Happy backtesting!**
