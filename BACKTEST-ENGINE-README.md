# Prediction Market Backtesting Engine

**Comprehensive backtesting framework for validating hype → price trading strategies on prediction markets.**

---

## 🎯 Overview

This backtesting engine tests whether Twitter/social media hype can predict price movements in prediction markets (Polymarket, Kalshi, etc.). It implements the trading strategy defined in `TRADING-STRATEGY-FRAMEWORK.md` with:

- **Walk-forward validation** (no look-ahead bias)
- **Realistic execution** (slippage, fees)
- **Comprehensive metrics** (Sharpe, drawdown, win rate, profit factor)
- **Statistical validation** (bootstrap confidence intervals, R²)
- **Professional reports** (HTML, charts, trade logs)

---

## 📦 Installation

### Requirements

```bash
pip install pandas numpy scipy scikit-learn matplotlib plotly
```

### Optional (for better charts)

```bash
pip install plotly  # Interactive HTML charts
```

---

## 🚀 Quick Start

### 1. Generate Sample Data (for testing)

```bash
python generate-sample-data.py
```

This creates a SQLite database (`polymarket_data.db`) with:
- 15 synthetic markets
- 60 days of historical data
- 15-minute price snapshots
- Correlated Twitter hype signals
- Realistic price movements with hype spikes

### 2. Run Backtest

```bash
python backtest-engine.py --db polymarket_data.db --output backtest_results/
```

### 3. View Results

Open `backtest_results/backtest_report.html` in your browser.

---

## 📊 What It Does

### Data Loading
- Connects to SQLite database
- Loads market snapshots (price, volume, liquidity)
- Loads Twitter hype signals (tweet counts, engagement)
- Joins data by timestamp and market ID

### Signal Generation

Implements strategy from `TRADING-STRATEGY-FRAMEWORK.md`:

1. **RVR (Relative Volume Ratio)**
   ```
   RVR = Current_Volume / Avg_Volume_Last_24h
   ```
   - Strong: RVR > 3.0
   - Moderate: RVR > 2.0
   - Weak: RVR > 1.5

2. **ROC (Rate of Change)**
   ```
   ROC = (Current_Price - Price_6h_Ago) / Price_6h_Ago × 100
   ```
   - Strong: |ROC| > 15%
   - Moderate: |ROC| > 10%
   - Weak: |ROC| > 5%

3. **Multi-Signal Confirmation**
   - Requires 3+ signals to enter
   - Classifies as STRONG, MODERATE, or WEAK
   - Checks disqualifying conditions (liquidity, spread, time to expiry)

### Position Sizing

Based on signal strength and Kelly criterion:

| Signal Strength | Position Size | Max Exposure |
|----------------|---------------|--------------|
| STRONG (3 signals) | 4% of capital | 5% hard cap |
| MODERATE (2-3 signals) | 2% of capital | 5% hard cap |
| WEAK | 1% of capital | 5% hard cap |

**Portfolio limits:**
- Max single position: 5% of capital
- Max total exposure: 25% of capital
- Cash reserve: 50%+ always available

### Trade Execution

**Entry:**
- Slippage: 1% (realistic for market orders)
- No fees on entry

**Exit Rules:**

1. **Take Profit (Tiered)**
   - TP1: +8% → Close 25%
   - TP2: +15% → Close 50%
   - TP3: +25% → Close 25%

2. **Stop Loss**
   - Hard stop: -12%

3. **Time Decay**
   - 3 days, <+5% gain → Close 50%
   - 7 days, <+8% gain → Close 100%

4. **Market Expiry**
   - Exit all positions 7 days before market resolution

**Exit:**
- Slippage: 1.5%
- Fees: 2% on profits only

### Walk-Forward Validation

Prevents overfitting by:
1. Training on historical data (e.g., Jan-Mar)
2. Testing on future data (e.g., Apr)
3. Rolling forward in time
4. Never using future information

---

## 📈 Metrics Reported

### Primary Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| **Sharpe Ratio** | > 1.0 | Risk-adjusted returns (annualized) |
| **Max Drawdown** | < 25% | Worst peak-to-trough loss |
| **Win Rate** | > 50% | Percentage of profitable trades |
| **Profit Factor** | > 1.5 | Total wins / Total losses |

### Secondary Metrics

- **Sortino Ratio**: Downside deviation only
- **Expectancy**: Average $ per trade
- **Average Win/Loss**: Size of typical win/loss
- **Holding Period**: How long positions are held
- **Consecutive Wins/Losses**: Streaks
- **Best/Worst Trade**: Extremes

### Statistical Validation

- **95% Confidence Interval**: Bootstrap resampling
- **Out-of-Sample R²**: Predictive power
- **Buy-and-Hold Comparison**: Alpha generation

---

## 📂 Outputs

### 1. `trade_log.csv`

Complete trade history:
```csv
entry_time,exit_time,market_question,side,entry_price,exit_price,position_size,pnl_net,return_pct,holding_hours,signal_strength,exit_reason
2026-01-15 10:30,2026-01-16 14:45,Bitcoin reaches $100k,YES,0.452,0.489,400,12.34,3.08,28.25,STRONG,TP1
...
```

### 2. `performance_metrics.json`

Machine-readable metrics:
```json
{
  "total_trades": 42,
  "win_rate": 57.14,
  "sharpe_ratio": 1.23,
  "max_drawdown_pct": 18.5,
  ...
}
```

### 3. `performance_charts.png`

Four-panel visualization:
- Equity curve
- Returns distribution
- Win/loss breakdown
- Trade timeline

### 4. `backtest_report.html`

**Comprehensive HTML report** with:
- ✅ Color-coded performance cards
- 📊 Interactive charts (if Plotly installed)
- 📋 Strategy validation table (PASS/FAIL)
- 💰 Win/loss analysis
- ⏱️ Trade statistics

---

## 🔧 Command-Line Options

```bash
python backtest-engine.py [OPTIONS]
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--db` | `polymarket_data.db` | Path to SQLite database |
| `--output` | `backtest_results` | Output directory |
| `--capital` | `10000` | Initial capital ($) |
| `--walk-forward` | False | Enable walk-forward validation |

### Examples

```bash
# Basic backtest
python backtest-engine.py

# Custom database and capital
python backtest-engine.py --db my_data.db --capital 50000

# Walk-forward validation (recommended)
python backtest-engine.py --walk-forward --output results_wf/

# Full production run
python backtest-engine.py \
  --db polymarket_data.db \
  --output backtest_$(date +%Y%m%d) \
  --capital 10000 \
  --walk-forward
```

---

## 🗄️ Database Schema

The engine expects a SQLite database with these tables:

### `markets`

```sql
CREATE TABLE markets (
    market_id TEXT PRIMARY KEY,
    question TEXT,
    category TEXT,
    end_time TIMESTAMP,
    resolved INTEGER DEFAULT 0
);
```

### `snapshots`

```sql
CREATE TABLE snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT,
    timestamp TIMESTAMP,
    price_yes REAL,
    price_no REAL,
    volume_24h REAL,
    liquidity REAL,
    best_bid_yes REAL,
    best_ask_yes REAL,
    spread REAL,
    FOREIGN KEY (market_id) REFERENCES markets(market_id),
    UNIQUE(market_id, timestamp)
);
```

### `hype_signals` (optional)

```sql
CREATE TABLE hype_signals (
    market_id TEXT,
    timestamp TIMESTAMP,
    tweet_count INTEGER,
    total_engagement INTEGER,
    velocity REAL,
    hype_score REAL,
    UNIQUE(market_id, timestamp)
);
```

---

## 🎓 Interpreting Results

### ✅ Strategy is Viable If:

- **Sharpe Ratio > 1.0**: Good risk-adjusted returns
- **Win Rate > 50%**: More winners than losers
- **Profit Factor > 1.5**: Wins are bigger than losses
- **Max Drawdown < 25%**: Manageable risk
- **≥30 trades**: Statistically significant sample

### ⚠️ Warning Signs:

- **Sharpe < 0.5**: Strategy doesn't work
- **Win Rate < 45%**: Too many losers
- **Profit Factor < 1.0**: Losing money overall
- **Max Drawdown > 40%**: Too risky
- **<30 trades**: Not enough data

### 🔍 Debugging Poor Performance

If results are bad:

1. **Check data quality**
   ```bash
   sqlite3 polymarket_data.db "SELECT COUNT(*) FROM snapshots;"
   sqlite3 polymarket_data.db "SELECT COUNT(DISTINCT market_id) FROM markets;"
   ```

2. **Adjust signal thresholds**
   - Lower RVR/ROC thresholds → More trades
   - Raise thresholds → Fewer, higher-quality trades

3. **Review trade log**
   ```bash
   head -20 backtest_results/trade_log.csv
   ```
   - Are exits too early? Adjust TP levels
   - Are losses too big? Tighten stop loss
   - Too many time-decay exits? Adjust thresholds

4. **Check market selection**
   - Low liquidity markets → Skip them
   - Markets near expiry → Exclude

---

## 🧪 Testing Strategy

### Unit Tests (Coming Soon)

```bash
pytest test_backtest_engine.py
```

### Smoke Test

```bash
# Generate sample data
python generate-sample-data.py

# Run backtest
python backtest-engine.py

# Check outputs exist
ls -lh backtest_results/
```

Expected files:
- `backtest_report.html`
- `performance_charts.png`
- `trade_log.csv`
- `performance_metrics.json`

---

## 🚨 Critical Requirements from Strategy Framework

### MUST Have (from Section 8 of TRADING-STRATEGY-FRAMEWORK.md)

1. ✅ **Walk-forward validation** (implemented with `--walk-forward`)
2. ✅ **No look-ahead bias** (signals only use past data)
3. ✅ **Realistic slippage** (1-2%)
4. ✅ **Transaction fees** (2% on profits)
5. ✅ **Minimum 30 trades** (warning if <30)
6. ✅ **Risk-adjusted metrics** (Sharpe, Sortino)
7. ✅ **Drawdown tracking** (max and time-series)
8. ✅ **Statistical validation** (bootstrap CI)

### Key Assumptions

- **Slippage**: 1% entry, 1.5% exit (market orders)
- **Fees**: 2% on profits only (Polymarket-style)
- **Execution**: Instant fills (no partial fills modeled)
- **Liquidity**: Must be >$5k to trade
- **Spread**: Must be <5% to trade

---

## 📝 Example Output

```
============================================================
PREDICTION MARKET BACKTESTING ENGINE
============================================================
✓ Loaded 5,760 snapshots across 15 markets
  Date range: 2025-12-07 to 2026-02-05

Calculating signals...
Simulating trades...

✓ Backtest complete: 47 trades executed

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

✓ Reports saved to: backtest_results
✓ HTML report: backtest_results/backtest_report.html
✓ Trade log: backtest_results/trade_log.csv
✓ Metrics JSON: backtest_results/performance_metrics.json
✓ Charts: backtest_results/performance_charts.png

✅ Backtest complete!
📁 View results: C:\Users\...\backtest_results
📊 Open: backtest_results\backtest_report.html
```

---

## 🔮 Next Steps

### If Strategy Works (Sharpe > 1.0):

1. **Paper trading** (4-8 weeks live simulation)
2. **Deploy with micro capital** ($500-1,000)
3. **Monitor real slippage vs assumptions**
4. **Scale gradually** if profitable

### If Strategy Doesn't Work:

1. **Try different signal combinations**
   - Pure volume spike (no ROC)
   - Twitter sentiment instead of volume
   - Combine with market maker flow

2. **Adjust parameters**
   - Different RVR/ROC thresholds
   - Shorter/longer holding periods
   - Tighter/wider stops

3. **Different markets**
   - Focus on crypto only (high volatility)
   - Politics only (event-driven)
   - High-liquidity only (>$100k/day)

4. **Alternative strategies**
   - Mean reversion instead of momentum
   - Market maker strategy (provide liquidity)
   - Arbitrage across platforms

---

## 🐛 Troubleshooting

### "Database not found"

```bash
# Generate sample data first
python generate-sample-data.py
```

### "No trades generated"

Signal thresholds too strict. Adjust in `backtest-engine.py`:

```python
# Lower thresholds
rvr_strong=2.5,  # was 3.0
roc_strong=12.0  # was 15.0
```

### "Only X trades (need 30+)"

- Collect more data (longer history)
- Lower signal thresholds
- Include more markets

### "ImportError: No module named 'plotly'"

```bash
pip install plotly
```

Or run without Plotly (charts will be matplotlib only).

### "Charts not showing in HTML"

Ensure `performance_charts.png` is in same directory as HTML report.

---

## 📚 References

- **Strategy Framework**: `TRADING-STRATEGY-FRAMEWORK.md`
- **Data Collection**: `DATA-COLLECTION-PIPELINE.md`
- **Correlation Analysis**: `CORRELATION-ANALYSIS-FRAMEWORK.md`
- **Twitter Tracking**: `TWITTER-SENTIMENT-TRACKING.md`

---

## 🤝 Contributing

Improvements welcome:

- [ ] Add support for multiple strategies
- [ ] Implement portfolio optimization
- [ ] Add Monte Carlo simulation
- [ ] Support for other data sources (Kalshi, Manifold)
- [ ] Real-time backtesting dashboard
- [ ] Machine learning signal generation

---

## ⚖️ Disclaimer

This is for **research and educational purposes only**. Trading prediction markets involves:

- **Financial risk** (you can lose money)
- **Regulatory considerations** (check your jurisdiction)
- **No guarantees** (past performance ≠ future results)

**Backtest results are optimistic**. Expect real trading to underperform by:
- 20-30% (typical degradation)
- More slippage than modeled
- Unexpected issues (API failures, liquidity crunches)

**Only trade with capital you can afford to lose.**

---

## 📜 License

MIT License - Free to use, modify, and distribute.

---

**Built with 🔥 by OpenClaw Agent**  
**Version:** 1.0  
**Last Updated:** 2026-02-06
