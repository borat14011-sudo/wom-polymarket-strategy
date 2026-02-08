# Correlation Analyzer: Twitter Hype → Market Movements

**Purpose:** Scientifically rigorous analysis to test if Twitter hype predicts prediction market movements.

**Version:** 1.0  
**Date:** 2026-02-06

---

## Overview

This script implements the statistical framework described in `CORRELATION-ANALYSIS-FRAMEWORK.md` to analyze relationships between Twitter hype signals and prediction market price movements.

### Key Features

✅ **Time-lag analysis** (0-48 hours)  
✅ **Granger causality testing** (does hype predict price?)  
✅ **Reverse causality detection** (does price drive hype?)  
✅ **Common cause detection** (external events driving both?)  
✅ **Signal strength classification** (STRONG/MODERATE/WEAK/NONE)  
✅ **Automated report generation** (JSON + visualizations)  
✅ **Multi-market batch analysis**

---

## Installation

### Prerequisites

- Python 3.8 or higher
- SQLite database with the required schema (see Database Schema below)

### Install Dependencies

```bash
pip install -r requirements-correlation.txt
```

Or manually:
```bash
pip install pandas numpy scipy statsmodels matplotlib seaborn
```

---

## Database Schema

The script expects a SQLite database (`polymarket_data.db`) with the following tables:

### `markets` table
```sql
CREATE TABLE markets (
    market_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT
);
```

### `snapshots` table (15-min price data)
```sql
CREATE TABLE snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    yes_price REAL,
    no_price REAL,
    volume INTEGER,
    liquidity REAL
);
```

### `hype_signals` table (hourly aggregated metrics)
```sql
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

---

## Usage

### Basic Usage

Analyze all markets in the database:
```bash
python correlation-analyzer.py --db polymarket_data.db
```

### Analyze Specific Market

```bash
python correlation-analyzer.py --db polymarket_data.db --market-id "abc123"
```

### Custom Parameters

```bash
python correlation-analyzer.py \
    --db polymarket_data.db \
    --min-samples 50 \
    --max-lag 24 \
    --significance 0.01 \
    --output my_report.json \
    --output-dir results/
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--db` | Path to SQLite database | **Required** |
| `--market-id` | Analyze specific market only | All markets |
| `--min-samples` | Minimum data points required | 30 |
| `--max-lag` | Maximum lag in hours to test | 48 |
| `--significance` | Statistical significance level (α) | 0.05 |
| `--output` | Output JSON filename | `correlation_report.json` |
| `--output-dir` | Output directory | `output/` |
| `--no-viz` | Skip visualization generation | False |

---

## Output Files

The script generates the following outputs in the `output/` directory:

### 1. JSON Report (`correlation_report.json`)

Complete analysis results including:
- Per-market correlation analysis
- Granger causality test results
- Signal strength classifications
- Warnings and flags
- Configuration parameters

### 2. Visualizations (PNG files)

**Per-Market Plots:**
- `{market_id}_{market_name}_correlation.png` - Cross-correlation vs lag

**Summary Plots:**
- `signal_distribution.png` - Distribution of signal tiers
- `top_markets.png` - Top tradeable markets ranked by correlation

---

## Interpreting Results

### Signal Tiers

| Tier | Criteria | Meaning | Tradeable? |
|------|----------|---------|------------|
| **STRONG** | r>0.5, p<0.001, no reverse causality | High predictive power | ✅ YES |
| **MODERATE** | r>0.3, p<0.01, no reverse causality | Moderate predictive power | ⚠️ Cautiously |
| **WEAK** | r>0.2, p<0.05 | Weak signal, monitor only | ❌ NO |
| **NONE** | Below thresholds | No predictive relationship | ❌ NO |

### Key Metrics

**Correlation Coefficient (r):**
- Measures strength of linear relationship
- Range: -1 to +1
- |r| > 0.3 is generally considered meaningful

**Granger Causality p-value:**
- Tests if hype predicts future price
- p < 0.05 = statistically significant
- p < 0.01 = strong evidence
- p < 0.001 = very strong evidence

**Optimal Lag:**
- Time delay (in hours) between hype spike and price movement
- Positive lag = hype leads price (good!)
- Zero lag = contemporaneous (common cause suspected)
- Negative lag = price leads hype (reverse causality - BAD!)

### Warning Flags

**🚨 Reverse Causality Detected**
- Price movements appear to drive hype (not the other way)
- **DO NOT TRADE** - this is a false pattern
- Example: Price jumps → people tweet about it → hype spike

**⚠️ Common Cause Suspected**
- Hype and price move together at lag=0
- Likely driven by external news events
- Little predictive value (no time advantage)

**⚠️ Bidirectional Relationship**
- Both hype→price AND price→hype are significant
- Feedback loop (still potentially useful)
- More complex dynamics to navigate

---

## Example Workflow

### Step 1: Collect Data

Ensure your database has at least 30 hourly data points per market (ideally 200+).

### Step 2: Run Analysis

```bash
python correlation-analyzer.py --db polymarket_data.db --min-samples 50
```

### Step 3: Review Report

Check the JSON report and console output:
```bash
cat output/correlation_report.json | jq '.top_markets[:5]'
```

### Step 4: Examine Visualizations

Look at the plots in `output/`:
- Which markets show clear lag structure?
- Are correlations stable or noisy?
- Any concerning warning patterns?

### Step 5: Validate Top Signals

For STRONG/MODERATE signals:
1. Check the correlation plot - does the peak make sense?
2. Review warnings - any red flags?
3. Examine data quality - sufficient samples?
4. Consider market context - is this pattern explainable?

### Step 6: Decide to Trade (or Not)

**Trade only if:**
- ✅ Signal tier: STRONG or MODERATE
- ✅ Granger p-value < 0.01
- ✅ No reverse causality
- ✅ Optimal lag > 0 hours
- ✅ Sufficient data (>50 samples)
- ✅ Pattern makes intuitive sense

**Don't trade if:**
- ❌ Any warning flags
- ❌ Weak or no signal
- ❌ Insufficient data
- ❌ Unstable correlations
- ❌ Unclear causality direction

---

## Statistical Methods

### 1. Cross-Correlation Analysis

Tests correlation at different time lags:
```
corr(hype(t), price(t + lag)) for lag ∈ [-48, +48] hours
```

**Positive lag:** Hype leads price (predictive!)  
**Negative lag:** Price leads hype (reverse causality)  
**Zero lag:** Simultaneous movement (common cause)

### 2. Granger Causality Test

Tests if past hype values improve price predictions beyond past prices alone.

**Null hypothesis:** Hype does not Granger-cause price  
**Test:** F-test comparing restricted vs unrestricted VAR model  
**Result:** Reject null → hype has predictive power

The script tests **both directions**:
- Hype → Price (what we want)
- Price → Hype (reverse causality check)

### 3. Stationarity Testing

Uses Augmented Dickey-Fuller (ADF) test to check for unit roots.

**Non-stationary series:** Contains trends or unit roots (spurious correlations)  
**Solution:** First-differencing to make stationary

### 4. Normalization

Both series are converted to z-scores (mean=0, std=1) for comparability across markets.

---

## Avoiding False Positives

The script includes multiple safeguards:

### 1. Reverse Causality Detection
Tests if price drives hype instead of hype driving price.

### 2. Common Cause Detection
Checks if contemporaneous correlation is strongest (external event driving both).

### 3. Stationarity Checks
Ensures correlations are not due to spurious trends.

### 4. Multiple Testing Awareness
Reports all tests performed (not just significant ones).

### 5. Minimum Sample Requirements
Requires at least 30 data points to avoid small-sample bias.

---

## Advanced Usage

### Batch Analysis with Custom Filters

```python
from correlation_analyzer import CorrelationAnalysisPipeline

# Initialize pipeline
pipeline = CorrelationAnalysisPipeline(
    db_path='polymarket_data.db',
    min_samples=50,
    max_lag=24,
    significance_level=0.01
)

# Analyze all markets
report = pipeline.analyze_all()

# Filter for strong signals only
strong_markets = [
    m for m in report.market_results 
    if m.signal_tier == 'STRONG' and m.tradeable
]

print(f"Found {len(strong_markets)} strong tradeable signals")
```

### Custom Hype Score Formula

Edit the `resample_to_hourly` method in `TimeSeriesPreprocessor` class:

```python
# Current formula (line ~350)
merged['hype_score'] = (
    np.log1p(merged['tweet_count']) + 
    0.5 * np.log1p(merged['total_engagement']) + 
    0.3 * merged['unique_authors']
)

# Example alternative: Weight sentiment more heavily
merged['hype_score'] = (
    np.log1p(merged['tweet_count']) + 
    0.5 * np.log1p(merged['total_engagement']) + 
    0.3 * merged['unique_authors'] +
    0.4 * merged['avg_sentiment']  # Add sentiment weight
)
```

### Export Data for External Analysis

```python
# After running analysis
for result in report.market_results:
    if result.signal_tier in ['STRONG', 'MODERATE']:
        # Export correlation data to CSV
        corr_df = pd.DataFrame([
            {'lag': c.lag_hours, 'correlation': c.correlation, 'p_value': c.p_value}
            for c in result.correlations_by_lag
        ])
        corr_df.to_csv(f"output/{result.market_id}_correlations.csv", index=False)
```

---

## Troubleshooting

### Error: "No data available"

**Cause:** Market has no price or hype data in database  
**Solution:** Check database queries, ensure data collection is working

### Error: "Insufficient data: X samples"

**Cause:** Market doesn't have enough data points for reliable analysis  
**Solution:** 
- Wait for more data to accumulate
- Reduce `--min-samples` (not recommended below 30)
- Check if market is too new or inactive

### Warning: "Stationarity test failed"

**Cause:** Time series has unusual properties (e.g., constant values)  
**Solution:** Script handles this automatically via differencing; usually safe to ignore

### No visualizations generated

**Cause:** matplotlib not installed or `--no-viz` flag used  
**Solution:** `pip install matplotlib seaborn`

### Granger causality test fails

**Cause:** Insufficient data for VAR model estimation  
**Solution:** More data needed, or reduce `--max-lag` parameter

---

## Validation Checklist

Before trusting results, verify:

- [ ] **Data Quality**
  - [ ] At least 30+ hourly observations per market
  - [ ] No large gaps in time series
  - [ ] Price data looks reasonable (no anomalies)

- [ ] **Statistical Validity**
  - [ ] Stationarity achieved (or differencing applied)
  - [ ] Correlation p-value < 0.05
  - [ ] Granger causality p-value < 0.05
  - [ ] Sufficient sample size for lag estimation

- [ ] **Causality Direction**
  - [ ] Hype→Price Granger test is significant
  - [ ] Price→Hype Granger test is NOT significant (or less significant)
  - [ ] Optimal lag is positive (hype leads price)

- [ ] **No Red Flags**
  - [ ] No reverse causality warnings
  - [ ] Common cause check passed
  - [ ] Correlation plot shows clear peak (not flat/noisy)

- [ ] **Practical Considerations**
  - [ ] Effect size is meaningful (|r| > 0.3)
  - [ ] Lag is actionable (not too short or long)
  - [ ] Market has sufficient liquidity
  - [ ] Pattern makes intuitive sense

---

## Limitations

### 1. Correlation ≠ Causation
Even with Granger causality, we can't prove true causation. Results suggest predictive relationships but should be validated with out-of-sample testing.

### 2. Stationarity Assumptions
Granger causality requires stationary series. The script applies differencing, but this may not always be sufficient for complex non-linear dynamics.

### 3. Linear Relationships Only
Pearson correlation and standard Granger tests assume linear relationships. Non-linear patterns may be missed.

### 4. No Regime Detection
Market dynamics may change over time (e.g., becoming less hype-driven as they mature). Script doesn't detect regime shifts.

### 5. Single Hype Score
The composite hype score is a simplified aggregate. Different hype metrics may have different lag structures.

### 6. No Transaction Costs
Analysis doesn't account for platform fees, slippage, or opportunity costs. Economic viability must be assessed separately.

---

## Next Steps

After running the analysis:

### If Strong Signals Found

1. **Validate out-of-sample:** Re-run analysis on new data period
2. **Paper trade:** Test signals in real-time without risking capital
3. **Calculate expected value:** Account for transaction costs
4. **Set risk limits:** Position sizing, stop-losses
5. **Monitor performance:** Track win rate, Sharpe ratio

### If No Signals Found

1. **Collect more data:** May need longer time periods
2. **Try different hype metrics:** Sentiment, high-follower tweets, etc.
3. **Segment markets:** Analyze by category, liquidity tier
4. **Check data quality:** Ensure collection pipeline is working
5. **Consider alternative hypotheses:** Maybe hype doesn't predict this market type

---

## References

- **Framework:** `CORRELATION-ANALYSIS-FRAMEWORK.md`
- **Granger Causality:** Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods"
- **ADF Test:** Dickey, D. A.; Fuller, W. A. (1979). "Distribution of the Estimators for Autoregressive Time Series with a Unit Root"
- **Statsmodels Documentation:** https://www.statsmodels.org/

---

## Support

For issues or questions:
1. Check this README
2. Review `CORRELATION-ANALYSIS-FRAMEWORK.md` for methodology
3. Examine the script source code (heavily commented)
4. Validate your database schema matches expectations

---

## License

MIT License - Use at your own risk. Past performance does not guarantee future results.

---

**Remember:** This tool helps identify statistical patterns, but trading decisions should incorporate broader context, risk management, and healthy skepticism. Always validate findings before risking capital.

Happy analyzing! 📊🔬
