# 🎯 Backtesting Engine - Cheat Sheet

**Quick reference for common tasks**

---

## ⚡ Quick Commands

### First Time Setup
```bash
pip install pandas numpy scipy scikit-learn matplotlib
python generate-sample-data.py
python backtest-engine.py
```

### Basic Backtest
```bash
python backtest-engine.py
```

### Recommended (Walk-Forward)
```bash
python backtest-engine.py --walk-forward
```

### With Real Data
```bash
python backtest-engine.py --db polymarket_data.db --walk-forward
```

### Custom Capital
```bash
python backtest-engine.py --capital 50000
```

---

## 📊 Reading Results

### Open Report
```bash
# Windows
start backtest_results\backtest_report.html

# Mac
open backtest_results/backtest_report.html

# Linux
xdg-open backtest_results/backtest_report.html
```

### Check Trade Log
```bash
head -20 backtest_results/trade_log.csv
```

### Check Metrics
```bash
cat backtest_results/performance_metrics.json
```

---

## ✅ Strategy Works If:

| Metric | Target | Means |
|--------|--------|-------|
| Sharpe Ratio | > 1.0 | Good risk-adjusted returns |
| Win Rate | > 50% | More winners than losers |
| Profit Factor | > 1.5 | Wins bigger than losses |
| Max Drawdown | < 25% | Manageable risk |
| Total Trades | 30+ | Statistically significant |

---

## 🔧 Common Adjustments

### Lower Signal Thresholds (More Trades)

Edit `backtest-engine.py` line ~60:
```python
self.signal_generator = SignalGenerator(
    rvr_strong=2.5,      # was 3.0
    roc_strong=12.0,     # was 15.0
)
```

### Tighter Stop Loss

Edit line ~90:
```python
self.stop_loss_pct = 0.08  # was 0.12 (8% instead of 12%)
```

### Earlier Profit Taking

Edit line ~88:
```python
self.tp_levels = [0.06, 0.12, 0.20]  # was [0.08, 0.15, 0.25]
```

---

## 🐛 Quick Fixes

### "Database not found"
```bash
python generate-sample-data.py
```

### "No trades generated"
Lower signal thresholds (see above) or collect more data.

### "Only X trades (need 30+)"
- Collect more historical data
- Lower signal thresholds
- Check disqualifying conditions

### Missing dependencies
```bash
pip install pandas numpy scipy scikit-learn matplotlib plotly
```

---

## 📁 Output Files

```
backtest_results/
├── backtest_report.html        ← Open this!
├── trade_log.csv              ← All trades
├── performance_metrics.json   ← Metrics
└── performance_charts.png     ← Charts
```

---

## 📚 Detailed Docs

- **Quick Start**: `QUICK-START-BACKTEST.md`
- **Full Manual**: `BACKTEST-ENGINE-README.md`
- **Technical**: `BACKTEST-ENGINE-DELIVERY.md`

---

## 🎯 Decision Tree

```
Run backtest
    ↓
Sharpe > 1.0?
    ↓ Yes          ↓ No
Paper trade    Adjust strategy
    ↓              ↓
Still good?    Try again
    ↓ Yes          ↓
Deploy micro   Consider
capital        alternatives
```

---

## 🔢 Key Numbers to Remember

- **Target Sharpe**: > 1.0
- **Target Win Rate**: > 50%
- **Target Profit Factor**: > 1.5
- **Max Acceptable Drawdown**: < 25%
- **Min Sample Size**: 30 trades
- **Slippage**: 1-2%
- **Fees**: 2% on profits

---

## ⚡ One-Liner

Generate data + backtest + open report:
```bash
python generate-sample-data.py && python backtest-engine.py && start backtest_results\backtest_report.html
```

---

**That's all you need!** 🎉

For more details, see the full documentation.
