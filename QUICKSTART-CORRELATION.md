# Quick Start Guide: Correlation Analysis

**Get up and running with correlation analysis in 5 minutes.**

---

## 📋 Prerequisites

- Python 3.8+
- SQLite database with market and hype data (or generate test data)

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements-correlation.txt
```

### Step 2: Test with Synthetic Data

Generate test data to validate the setup:

```bash
python generate-test-data.py --output test_data.db --markets 10 --days 30
```

This creates a test database with:
- 10 markets
- 30 days of data per market
- Mix of strong, moderate, weak, and no signals
- Some reverse causality cases (for testing detection)

### Step 3: Run Analysis

```bash
python correlation-analyzer.py --db test_data.db
```

The script will:
- ✅ Analyze all markets
- ✅ Run statistical tests (correlation, Granger causality)
- ✅ Generate visualizations
- ✅ Create JSON report
- ✅ Print summary to console

### Step 4: Review Results

Check the `output/` directory:

```bash
ls output/
# correlation_report.json          - Full analysis report
# signal_distribution.png          - Signal tier distribution
# top_markets.png                  - Top tradeable markets
# {market_id}_correlation.png      - Per-market correlation plots
```

View the JSON report:

```bash
cat output/correlation_report.json | python -m json.tool | less
```

Or use `jq` for filtering:

```bash
# Show top 5 markets
cat output/correlation_report.json | jq '.top_markets[:5]'

# Show only STRONG signals
cat output/correlation_report.json | jq '.market_results[] | select(.signal_tier=="STRONG")'
```

---

## 📊 Using Real Data

### Database Schema

Your `polymarket_data.db` should have these tables:

```sql
-- Markets metadata
CREATE TABLE markets (
    market_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT
);

-- Price snapshots (15-min frequency)
CREATE TABLE snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    yes_price REAL,
    no_price REAL,
    volume INTEGER,
    liquidity REAL
);

-- Hype signals (hourly aggregated)
CREATE TABLE hype_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT NOT NULL,
    hour_timestamp DATETIME NOT NULL,
    tweet_count INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    unique_authors INTEGER DEFAULT 0,
    avg_sentiment REAL DEFAULT 0,
    high_follower_count INTEGER DEFAULT 0
);
```

### Run on Real Data

```bash
python correlation-analyzer.py --db polymarket_data.db --min-samples 50
```

---

## 🎯 Common Use Cases

### 1. Analyze Single Market

```bash
python correlation-analyzer.py --db polymarket_data.db --market-id "abc123"
```

### 2. Find Strong Signals Only

```bash
python correlation-analyzer.py \
    --db polymarket_data.db \
    --min-samples 50 \
    --significance 0.01
```

Then filter the JSON:

```bash
cat output/correlation_report.json | \
    jq '.market_results[] | select(.signal_tier=="STRONG" and .tradeable==true)'
```

### 3. Test Shorter Time Lags

```bash
python correlation-analyzer.py --db polymarket_data.db --max-lag 24
```

Useful if you expect faster market reactions (within 24 hours).

### 4. Export for Backtesting

Use the example script:

```bash
python example-usage.py
# Uncomment example_6_export_for_backtest() in the script first
```

This creates `output/tradeable_signals.csv` and per-market correlation CSVs.

---

## 📈 Interpreting Results

### Signal Tiers

| Tier | What it means | Action |
|------|---------------|--------|
| **STRONG** | High correlation, significant Granger causality, no red flags | ✅ Tradeable |
| **MODERATE** | Moderate correlation, significant causality | ⚠️ Trade cautiously |
| **WEAK** | Low correlation or borderline significance | 📊 Monitor only |
| **NONE** | No significant relationship | ❌ Ignore |

### Key Metrics

**Max Correlation**
- `> 0.5` = Strong relationship
- `0.3-0.5` = Moderate relationship
- `< 0.3` = Weak relationship

**Granger p-value**
- `< 0.001` = Very strong evidence
- `< 0.01` = Strong evidence
- `< 0.05` = Significant
- `> 0.05` = Not significant

**Optimal Lag**
- `> 0 hours` = Hype leads price ✅
- `= 0 hours` = Contemporaneous (warning)
- `< 0 hours` = Price leads hype ❌

### Warning Flags

**🚨 Reverse Causality**
- Price appears to drive hype (not hype → price)
- Do NOT trade this pattern

**⚠️ Common Cause Suspected**
- Both move together at lag=0
- Likely external event driving both
- Limited predictive value

**⚠️ Bidirectional Relationship**
- Both hype→price AND price→hype are significant
- Feedback loop (more complex, still potentially useful)

---

## 🔬 Advanced Usage

### Programmatic Access

```python
from correlation_analyzer import CorrelationAnalysisPipeline

# Initialize
pipeline = CorrelationAnalysisPipeline(
    db_path='polymarket_data.db',
    min_samples=50,
    max_lag=48
)

# Run analysis
report = pipeline.analyze_all()

# Filter results
strong_signals = [
    m for m in report.market_results 
    if m.signal_tier == 'STRONG'
]

print(f"Found {len(strong_signals)} strong signals")

# Access individual results
for market in strong_signals:
    print(f"{market.market_name}: r={market.max_correlation:.3f}, lag={market.optimal_lag_hours}h")

pipeline.close()
```

### Custom Hype Metrics

Edit `correlation-analyzer.py` line ~350:

```python
# Current formula
merged['hype_score'] = (
    np.log1p(merged['tweet_count']) + 
    0.5 * np.log1p(merged['total_engagement']) + 
    0.3 * merged['unique_authors']
)

# Example: Add sentiment weighting
merged['hype_score'] = (
    np.log1p(merged['tweet_count']) + 
    0.5 * np.log1p(merged['total_engagement']) + 
    0.3 * merged['unique_authors'] +
    0.4 * merged['avg_sentiment']  # Weight positive sentiment
)
```

---

## 🐛 Troubleshooting

### "No data available"

**Check:**
1. Market exists in `markets` table
2. Has entries in both `snapshots` and `hype_signals` tables
3. Timestamps are in correct format (ISO 8601)

```sql
-- Verify data
SELECT COUNT(*) FROM snapshots WHERE market_id = 'abc123';
SELECT COUNT(*) FROM hype_signals WHERE market_id = 'abc123';
```

### "Insufficient data: X samples"

**Solution:**
- Need at least 30 hourly data points (default)
- Reduce threshold: `--min-samples 20` (not recommended <30)
- Wait for more data to accumulate

### No visualizations generated

**Solution:**
```bash
pip install matplotlib seaborn
```

### Granger causality test fails

**Common causes:**
1. Too few data points for VAR model
2. Non-stationary series (script auto-handles via differencing)
3. Constant values in series

**Solution:** Usually harmless - script returns non-significant result

---

## 📚 Further Reading

- **Detailed methodology:** `CORRELATION-ANALYSIS-FRAMEWORK.md`
- **Full documentation:** `CORRELATION-ANALYZER-README.md`
- **Code examples:** `example-usage.py`

---

## ✅ Validation Checklist

Before trusting results:

- [ ] At least 30+ hourly observations per market
- [ ] No large gaps in time series
- [ ] Granger causality p-value < 0.05
- [ ] Optimal lag is positive (hype leads price)
- [ ] No reverse causality warnings
- [ ] Correlation plot shows clear peak
- [ ] Effect size is meaningful (|r| > 0.3)

---

## 🎓 Next Steps

### If Strong Signals Found

1. **Validate:** Re-run on new data period
2. **Paper trade:** Test in real-time without capital
3. **Risk management:** Position sizing, stop-losses
4. **Monitor:** Track win rate, Sharpe ratio

### If No Signals Found

1. **More data:** Collect longer time periods
2. **Different metrics:** Try sentiment, high-follower tweets
3. **Market segmentation:** Analyze by category
4. **Alternative hypotheses:** Maybe hype doesn't predict this market type

---

## 💡 Tips

**Best practices:**
- Run on at least 30 days of data
- Higher `--min-samples` = more reliable results
- Check warnings carefully (reverse causality!)
- Validate findings on new data before trading
- Start with strong signals only

**Performance:**
- Analysis time: ~1-5 seconds per market
- RAM usage: ~100-500MB depending on data size
- Disk space: Minimal (mostly output files)

**Data quality matters:**
- Consistent sampling intervals
- No missing gaps
- Accurate timestamps
- Representative hype metrics

---

## 🚨 Important Disclaimers

1. **Correlation ≠ Causation** - Even with Granger tests, relationships may be spurious
2. **Past performance ≠ Future results** - Patterns can break down
3. **No guarantee of profitability** - Transaction costs, slippage, and market changes matter
4. **Use at your own risk** - This is research/analysis tool, not financial advice

---

## Need Help?

1. Check `CORRELATION-ANALYZER-README.md` for detailed docs
2. Review `CORRELATION-ANALYSIS-FRAMEWORK.md` for methodology
3. Inspect code (heavily commented)
4. Run test data to validate setup

Happy analyzing! 📊✨
