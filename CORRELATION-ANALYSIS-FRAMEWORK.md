# Correlation Analysis Framework: X Hype → Prediction Market Movements

**Purpose:** Scientifically rigorous framework to test if social media hype predicts prediction market movements, avoiding false positives and cherry-picking.

**Version:** 1.0  
**Date:** 2026-02-06

---

## Table of Contents

1. [Core Hypotheses to Test](#1-core-hypotheses-to-test)
2. [Statistical Methods](#2-statistical-methods)
3. [Time Lag Analysis](#3-time-lag-analysis)
4. [Market Condition Filters](#4-market-condition-filters)
5. [False Positive Patterns](#5-false-positive-patterns)
6. [Success Metrics & Tradeable Signals](#6-success-metrics--tradeable-signals)
7. [Example Analysis Workflow](#7-example-analysis-workflow)
8. [Implementation Checklist](#8-implementation-checklist)

---

## 1. Core Hypotheses to Test

### H1: Lead-Lag Relationship
**Primary Hypothesis:** Does X hype precede prediction market price movements (not just correlate)?

**Sub-hypotheses:**
- **H1a:** Hype spikes lead market movements by τ hours (τ ∈ {1, 2, 4, 8, 12, 24, 48})
- **H1b:** Market movements do NOT lead hype (reverse causality check)
- **H1c:** The relationship is causal, not driven by common external events

**Metrics to Test:**
- Tweet volume (raw count)
- Engagement rate (likes + retweets per tweet)
- Unique author count (breadth of discussion)
- Sentiment intensity (weighted positive/negative)
- High-follower amplification (tweets from accounts >10K followers)
- Reply depth (conversation threading intensity)

### H2: Magnitude Relationship
**Hypothesis:** Larger hype spikes predict larger price movements

**Test:**
- Correlation between hype magnitude (z-score) and subsequent price change %
- Non-linear relationships (does 10x hype = 10x movement, or diminishing returns?)
- Threshold effects (minimum hype level needed for movement)

### H3: Quality vs Quantity
**Hypothesis:** Which hype metrics matter most?

**Priority order to test:**
1. High-engagement tweets (>100 interactions)
2. High-follower accounts (>10K followers)
3. Sustained discussion (duration >4 hours)
4. Cross-platform spillover (Reddit, Discord mentions)
5. Raw tweet volume

### H4: Directional Prediction
**Hypothesis:** Sentiment predicts direction (YES vs NO movement)

**Test:**
- Positive sentiment → YES price increase
- Negative sentiment → NO price increase (or YES price decrease)
- Mixed sentiment → volatility without directional edge

---

## 2. Statistical Methods

### 2.1 Granger Causality Test
**Purpose:** Test if past hype values predict future market prices better than past prices alone

**Method:**
```
Model 1 (restricted): Price(t) = α + Σ β_i * Price(t-i) + ε
Model 2 (unrestricted): Price(t) = α + Σ β_i * Price(t-i) + Σ γ_i * Hype(t-i) + ε
```

**Test:** F-test on γ coefficients (null: all γ = 0)

**Requirements:**
- Stationarity: Augmented Dickey-Fuller test on both series
- If non-stationary: Use first differences or log returns
- Lag selection: AIC/BIC criteria (test lags 1-48 hours)
- Both directions: Test Hype→Price AND Price→Hype

**Interpretation:**
- Reject null + Hype→Price only = True predictive power
- Reject both directions = Bidirectional feedback (still useful)
- Reject Price→Hype only = Reverse causality (DANGER - hype follows price)

### 2.2 Cross-Correlation Function (CCF)
**Purpose:** Identify optimal time lag and correlation strength

**Method:**
```python
for lag in range(-48, 49):  # -48 to +48 hours
    corr[lag] = correlation(hype(t), price(t + lag))
```

**Analysis:**
- Peak at positive lag = Hype leads price
- Peak at negative lag = Price leads hype (reverse causality)
- Peak at lag 0 = Contemporaneous (likely common driver)

**Normalization:**
- Detrend both series (remove linear trends)
- Standardize (z-scores) to compare across different markets
- Remove autocorrelation (pre-whiten if necessary)

### 2.3 Vector Autoregression (VAR)
**Purpose:** Model dynamic interactions between hype and price

**Model:**
```
Price(t) = α₁ + Σ β₁ᵢ * Price(t-i) + Σ γ₁ᵢ * Hype(t-i) + ε₁(t)
Hype(t) = α₂ + Σ β₂ᵢ * Price(t-i) + Σ γ₂ᵢ * Hype(t-i) + ε₂(t)
```

**Output:**
- Impulse response functions (how price responds to hype shock)
- Variance decomposition (what % of price variance explained by hype)
- Forecast error variance (prediction accuracy)

### 2.4 Event Study Analysis
**Purpose:** Isolate hype spike events and measure subsequent price behavior

**Method:**
1. Define "hype event": Hype metric >2σ above 7-day rolling mean
2. Create event window: [-2h, +24h] around event time
3. Calculate abnormal returns: Actual price change - Expected change
4. Average across all events: Cumulative Abnormal Return (CAR)

**Statistical test:** t-test on mean CAR (null: CAR = 0)

### 2.5 Rolling Window Analysis
**Purpose:** Test stability of relationship over time

**Method:**
- 30-day estimation window, roll forward by 1 day
- Re-estimate correlation, Granger causality each window
- Plot coefficient stability over time

**Warning signs:**
- Correlation breaks down after initial period = Overfitting
- Relationship only exists in high-volatility periods = Conditional, not universal

### 2.6 Multiple Testing Correction
**CRITICAL:** When testing many hypotheses, adjust significance levels

**Methods:**
- Bonferroni correction: α_adjusted = α / n_tests
- False Discovery Rate (FDR): Benjamini-Hochberg procedure
- Family-wise error rate (FWER) control

**Example:** Testing 20 markets at α = 0.05
- Uncorrected: Expect 1 false positive by chance
- Bonferroni: Use α = 0.0025 for each test
- FDR: Control expected proportion of false discoveries

---

## 3. Time Lag Analysis

### 3.1 Systematic Lag Testing
**Approach:** Test all lags from 0 to 48 hours (hourly increments)

**For each lag τ:**
1. Calculate correlation: corr(Hype(t), Price(t+τ))
2. Run regression: Price(t+τ) = α + β * Hype(t) + ε
3. Record: β coefficient, p-value, R²

**Visualization:**
- Heatmap: Lag (x-axis) vs Correlation (y-axis)
- Identify peak correlation lag
- Check for multiple peaks (different hype→price pathways)

### 3.2 Differential Lag by Market Type
**Hypothesis:** Time lag varies by market characteristics

**Segmentation:**
- **High liquidity markets (>1000 traders):** Faster response (0-4h)
- **Low liquidity markets (<100 traders):** Slower response (4-24h)
- **Celebrity/mainstream topics:** Faster (0-2h)
- **Technical/niche topics:** Slower (12-48h)

**Test:** Interaction regression
```
Price(t+τ) = α + β₁*Hype(t) + β₂*Liquidity(t) + β₃*Hype(t)*Liquidity(t) + ε
```

### 3.3 Hype Persistence vs Market Response
**Key insight:** Sustained hype (>6 hours) may have different dynamics than spike hype (<1 hour)

**Classify hype patterns:**
- **Spike:** >2σ for <2 hours, then decays
- **Sustained:** >1σ for >6 hours
- **Building:** Gradual increase over 12-24 hours

**Test different lag structures for each pattern.**

### 3.4 Decay Function
**Hypothesis:** Hype impact decays over time

**Model:**
```
Price_change(t to t+τ) = α + β * Hype(t) * exp(-λ * τ) + ε
```

**Estimate decay rate λ:**
- Fast decay (λ > 0.5/hour): Impact fades within 2-4 hours
- Slow decay (λ < 0.1/hour): Impact lasts 10+ hours

**Use:** Optimize entry timing after hype spike

---

## 4. Market Condition Filters

### 4.1 Liquidity Filters
**Rationale:** Hype may only matter in liquid markets where traders can act quickly

**Metrics:**
- Daily trading volume (unique traders)
- Bid-ask spread (proxy if available)
- Open interest (total money staked)
- Order book depth

**Thresholds to test:**
- Minimum 50 traders/day
- Minimum $10K open interest
- Maximum spread <5% of midpoint

**Analysis:** Run correlation separately for high vs low liquidity subsets

### 4.2 Volatility Regime Filtering
**Rationale:** Hype→price relationship may be stronger in high volatility periods

**Volatility measure:**
- Rolling 7-day standard deviation of price changes
- ATR (Average True Range) equivalent for prediction markets

**Regime classification:**
- Low vol: σ < 0.05 (5% daily movement)
- Medium vol: 0.05 ≤ σ < 0.15
- High vol: σ ≥ 0.15

**Hypothesis:** Hype effect strongest in medium volatility
- Low vol: Market ignoring new info
- High vol: Too much noise, hype drowned out

### 4.3 Market Maturity Filtering
**Age of market as moderator:**
- New markets (0-7 days): More susceptible to hype
- Mature markets (>30 days): More price discovery, less hype-driven
- Near-resolution (<7 days to close): Different dynamics

**Test:** Interaction between hype and market age

### 4.4 Broader Market Conditions
**External factors:**
- News cycle intensity (is there major competing news?)
- Platform-wide activity (is X engagement generally high/low today?)
- Competing markets (is attention divided across multiple similar bets?)

**Control variables:**
- Overall X traffic that day (zscore)
- Number of trending topics in category
- Major news events (binary flag)

### 4.5 Time-of-Day Effects
**Hypothesis:** Hype during active trading hours has more impact

**Segments:**
- Market hours (9am-4pm ET): Highest trader activity
- Evening (4pm-11pm ET): Moderate activity
- Night/early morning (11pm-9am ET): Low activity

**Test:** Hype-to-price correlation by time-of-day of hype spike

### 4.6 Bootstrap Confidence Intervals
**Method:** Resample historical data with replacement, re-estimate correlations

**Output:** 95% confidence interval for correlation coefficient

**Decision rule:** Only trade if lower bound of CI > minimum threshold

---

## 5. False Positive Patterns (Trap Avoidance)

### 5.1 Reverse Causality Trap
**Problem:** Price moves → generates hype (not hype → price)

**Detection:**
1. Test Granger causality in BOTH directions
2. Compare lead-lag correlations: corr(Hype(t), Price(t-τ)) vs corr(Hype(t), Price(t+τ))
3. If price→hype is stronger: REJECT this market

**Example:** Market suddenly jumps 20% → people tweet about it → hype spike
- This looks like correlation but has no predictive value

### 5.2 Common Cause Trap
**Problem:** External event drives both hype and price simultaneously

**Examples:**
- Breaking news → instant hype + instant price move
- Celebrity announcement → both spike together
- No predictive edge (hype doesn't *lead* price)

**Detection:**
- Cross-correlation peak at lag 0 (contemporaneous)
- No lead-lag structure
- Event timestamps match hype/price spike times

**Mitigation:**
- Filter out hype within 1 hour of known news events
- Focus on "organic" hype without obvious catalyst

### 5.3 Autocorrelation Trap
**Problem:** Prices/hype trending → spurious correlation

**Example:**
- Market gradually rises over days
- Hype gradually rises over days
- High correlation, but no predictive relationship

**Detection:**
- Augmented Dickey-Fuller test (test for unit root)
- If non-stationary: Detrend or use first differences

**Solution:**
```
Instead of: corr(Hype, Price)
Use: corr(ΔHype, ΔPrice) or corr(Hype_residuals, Price_residuals)
```

### 5.4 Look-Ahead Bias
**Problem:** Using future information to predict past

**Common errors:**
- Using end-of-day hype metrics to predict intraday moves
- Normalizing by full-period statistics before splitting train/test
- Selecting markets based on final outcome

**Prevention:**
- Strict chronological train/test split
- Calculate all statistics on training data only
- Simulate real-time data arrival (no peeking)

### 5.5 Survivorship Bias
**Problem:** Only analyzing markets that had hype + moved (ignoring non-events)

**Correct approach:**
- Sample ALL markets in category over time period
- Include markets where hype occurred but NO price movement
- Include markets where price moved but NO hype

**4-way classification:**
| | Hype | No Hype |
|---|---|---|
| **Price Move** | True Positive | False Negative |
| **No Price Move** | False Positive | True Negative |

**Accuracy = (TP + TN) / Total**

### 5.6 P-Hacking / Data Dredging
**Problem:** Testing many variations until finding significance by chance

**Example:**
- Test 50 different hype metrics
- Test 20 different lags
- Try 10 different market filters
- Report only the 1 that shows p < 0.05

**Prevention:**
- Pre-register hypotheses before testing
- Use held-out test set for validation
- Apply multiple testing corrections
- Report ALL tests performed, not just significant ones

### 5.7 Overfitting Trap
**Problem:** Model fits training data noise, not true signal

**Detection:**
- High in-sample R² but low out-of-sample R²
- Complex models (many parameters) vs simple baselines
- Performance degrades on new time periods

**Prevention:**
- Cross-validation (k-fold temporal splits)
- Penalized regression (Lasso, Ridge)
- Compare to naive baseline (persistence model)
- Walk-forward validation

### 5.8 Small Sample Bias
**Problem:** Too few observations → unstable estimates

**Minimum requirements:**
- 30+ hype events per market (for event study)
- 200+ hourly observations (for time-series regression)
- 20+ markets (for cross-sectional validation)

**If insufficient data:** Report uncertainty, don't trade

---

## 6. Success Metrics & Tradeable Signals

### 6.1 Statistical Significance Thresholds

**Minimum criteria for "real" relationship:**

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| **Correlation coefficient** | r > 0.3 | Effect size: >9% variance explained |
| **Granger causality p-value** | p < 0.01 | Strong evidence (after correction) |
| **Out-of-sample R²** | R² > 0.10 | 10%+ predictive power on unseen data |
| **Hit rate (direction)** | >55% | Better than coin flip + transaction costs |
| **Sharpe ratio (strategy)** | >1.0 | Risk-adjusted returns beat buy-and-hold |

**Red flags (STOP):**
- In-sample significant but out-of-sample fails
- Correlation <0.2
- Inconsistent sign across subperiods

### 6.2 Economic Significance (Tradeability)

**Question:** Even if statistically significant, is it profitable after costs?

**Cost structure:**
- Platform fees (e.g., Polymarket ~2% on winnings)
- Bid-ask spread (cost of immediate execution)
- Opportunity cost (capital locked for days/weeks)
- Slippage (price moves against you as you trade)

**Minimum price movement:**
- Need ≥5% expected movement to cover 2-3% round-trip costs
- Confidence >60% to be +EV

**Expected value calculation:**
```
EV = (Win_prob * Gain) - (Loss_prob * Loss) - Costs

Example:
Hype signal predicts +10% move with 65% confidence
Current price: 50¢
EV = (0.65 * $0.10) - (0.35 * $0.50) - $0.02 = $0.065 - $0.175 - $0.02 = -$0.13
→ NEGATIVE EV, don't trade
```

### 6.3 Win Rate vs Effect Size Tradeoff

**Two paths to profitability:**

**Path A: High win rate, small edge**
- 60% win rate, average gain 3%
- Many trades, low variance
- Requires tight execution, low costs

**Path B: Lower win rate, large edge**
- 45% win rate, but wins average +20%, losses -10%
- EV = 0.45(20) - 0.55(10) = 9 - 5.5 = +3.5%
- Requires patience, emotional discipline

**Recommendation:** Path B better for hype-driven strategies (big moves are where hype matters)

### 6.4 Signal Strength Tiers

**Tier 1 (Strong - Trade aggressively):**
- Correlation >0.5
- Granger p-value <0.001
- Out-of-sample R² >0.20
- Win rate >65%
- Bootstrap CI entirely positive

**Tier 2 (Moderate - Trade cautiously):**
- Correlation 0.3-0.5
- Granger p-value <0.01
- Out-of-sample R² 0.10-0.20
- Win rate 55-65%

**Tier 3 (Weak - Monitor, don't trade):**
- Correlation 0.2-0.3
- Borderline significance
- Collect more data before risking capital

**Tier 4 (No signal - Ignore):**
- Correlation <0.2 or inconsistent
- Not statistically significant
- Failed out-of-sample

### 6.5 Backtesting Framework

**Walk-forward validation:**
```
For each time period t:
  1. Train model on data up to t-1
  2. Generate prediction for t
  3. Simulate trade at actual market prices
  4. Record P&L
  5. Move to t+1
```

**Realism requirements:**
- Use actual bid-ask spreads (not midpoint)
- Include slippage (especially on large orders)
- Respect market liquidity (can't trade $100K in $10K market)
- Account for lag (time to detect hype, analyze, execute)

**Performance metrics:**
- Cumulative return
- Sharpe ratio
- Maximum drawdown
- Win rate
- Average win/loss
- Profit factor (gross profit / gross loss)

### 6.6 Risk Management Rules

**Position sizing:**
- Never >5% of capital in single bet
- Kelly criterion: f = (p*b - q) / b, where p=win prob, q=loss prob, b=odds
- Use fractional Kelly (0.25-0.5x) for safety

**Stop-loss:**
- Exit if market moves >10% against position within 2 hours
- Exit if hype reverses (sentiment flips)
- Exit if new information invalidates thesis

**Time-based exit:**
- If no movement within 24h of hype spike, reassess
- Don't hold to resolution if signal decayed

### 6.7 Minimum Viable Signal (MVS)

**Checklist before trading:**
- [ ] Granger causality p < 0.01 (hype → price)
- [ ] Optimal lag identified and consistent across samples
- [ ] Out-of-sample test shows positive returns
- [ ] Market passes liquidity filter (>50 traders/day)
- [ ] No obvious reverse causality or common cause
- [ ] Expected value >10% after costs
- [ ] Signal strength Tier 2 or above
- [ ] Risk management plan in place

**If ANY checkbox fails:** Don't trade, collect more data.

---

## 7. Example Analysis Workflow

### Case Study: "Will [Celebrity] announce [Event] by [Date]?" market

**Step 1: Data Collection (Days 1-7)**

1. **Hype metrics (hourly):**
   - Tweet volume mentioning celebrity + event
   - Total engagements (likes + RTs)
   - Unique author count
   - Sentiment score (-1 to +1)
   - High-follower amplification (accounts >10K)

2. **Market metrics (hourly):**
   - YES price (midpoint)
   - Trading volume
   - Number of unique traders
   - Price volatility (hourly std dev)

3. **External controls:**
   - News mentions (Google Trends score)
   - Celebrity's own tweet activity (binary: tweeted or not)
   - Related market activity

**Step 2: Data Preprocessing**

```python
# Stationarity check
from statsmodels.tsa.stattools import adfuller

adf_hype = adfuller(hype_series)
adf_price = adfuller(price_series)

if adf_hype[1] > 0.05:  # Non-stationary
    hype_diff = hype_series.diff().dropna()
else:
    hype_diff = hype_series

# Same for price

# Normalize to z-scores
hype_z = (hype_diff - hype_diff.mean()) / hype_diff.std()
price_z = (price_diff - price_diff.mean()) / price_diff.std()
```

**Step 3: Exploratory Analysis**

```python
# Cross-correlation
from statsmodels.tsa.stattools import ccf

lags = range(-24, 25)  # -24h to +24h
ccf_values = [ccf(hype_z, price_z, adjusted=False)[lag] for lag in lags]

# Plot: Should show peak at positive lag if hype leads
optimal_lag = lags[np.argmax(ccf_values)]
print(f"Optimal lag: {optimal_lag} hours")
```

**Step 4: Granger Causality Test**

```python
from statsmodels.tsa.stattools import grangercausalitytests

# Test hype → price
data = pd.DataFrame({'price': price_z, 'hype': hype_z})
gc_results = grangercausalitytests(data[['price', 'hype']], maxlag=24)

# Extract p-values for each lag
p_values = [gc_results[lag+1][0]['ssr_ftest'][1] for lag in range(24)]
best_lag = np.argmin(p_values) + 1
best_p = p_values[best_lag - 1]

print(f"Best lag: {best_lag}h, p-value: {best_p}")

# TEST REVERSE CAUSALITY
gc_reverse = grangercausalitytests(data[['hype', 'price']], maxlag=24)
p_values_rev = [gc_reverse[lag+1][0]['ssr_ftest'][1] for lag in range(24)]

if min(p_values_rev) < 0.05:
    print("WARNING: Reverse causality detected!")
```

**Step 5: Event Study**

```python
# Define hype events: >2σ spike
hype_mean = hype_series.rolling(7*24).mean()  # 7-day rolling mean
hype_std = hype_series.rolling(7*24).std()
events = hype_series > (hype_mean + 2*hype_std)

# For each event, extract price change over next 24h
event_times = events[events].index
abnormal_returns = []

for t in event_times:
    if t + pd.Timedelta(hours=24) <= price_series.index[-1]:
        baseline = price_series.iloc[:t].rolling(7*24).mean().iloc[-1]
        actual = price_series.loc[t + pd.Timedelta(hours=24)]
        ar = actual - baseline
        abnormal_returns.append(ar)

# Test if mean AR significantly different from zero
from scipy.stats import ttest_1samp
t_stat, p_val = ttest_1samp(abnormal_returns, 0)
print(f"Mean abnormal return: {np.mean(abnormal_returns):.4f}, p={p_val:.4f}")
```

**Step 6: Regression with Controls**

```python
import statsmodels.api as sm

# Prepare data with optimal lag
lag_hours = best_lag
price_future = price_series.shift(-lag_hours)
X = pd.DataFrame({
    'hype': hype_z,
    'volume': trading_volume_z,
    'volatility': price_volatility_z,
    'news': news_mentions_z
})
X = sm.add_constant(X)
y = price_future

# Drop NaN from shift
valid = ~(X.isna().any(axis=1) | y.isna())
X = X[valid]
y = y[valid]

# Train-test split (70-30 temporal)
train_size = int(0.7 * len(X))
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Fit model
model = sm.OLS(y_train, X_train).fit()
print(model.summary())

# Out-of-sample R²
y_pred = model.predict(X_test)
ss_res = ((y_test - y_pred)**2).sum()
ss_tot = ((y_test - y_test.mean())**2).sum()
r2_oos = 1 - ss_res/ss_tot
print(f"Out-of-sample R²: {r2_oos:.4f}")
```

**Step 7: Market Condition Filtering**

```python
# Filter for high liquidity only
liquidity_threshold = 50  # traders per day
daily_traders = trading_volume.resample('D').nunique()
high_liq_days = daily_traders > liquidity_threshold

# Re-run analysis on high liquidity subset
X_filtered = X[high_liq_days]
y_filtered = y[high_liq_days]

# Compare correlation
corr_all = np.corrcoef(X['hype'], y)[0,1]
corr_filtered = np.corrcoef(X_filtered['hype'], y_filtered)[0,1]

print(f"Correlation (all): {corr_all:.3f}")
print(f"Correlation (high liq): {corr_filtered:.3f}")
```

**Step 8: False Positive Checks**

```python
# 1. Reverse causality (already done in Step 4)

# 2. Common cause: Check if hype and price spike together (lag 0)
contemporaneous_corr = ccf_values[24]  # Lag 0 is at index 24
if contemporaneous_corr > max([ccf_values[i] for i in range(len(lags)) if i != 24]):
    print("WARNING: Contemporaneous correlation strongest (common cause?)")

# 3. Autocorrelation (already handled via ADF test)

# 4. Overfitting: Cross-validation
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
r2_scores = []

for train_idx, test_idx in tscv.split(X):
    X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
    y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]
    
    m = sm.OLS(y_tr, X_tr).fit()
    y_p = m.predict(X_te)
    r2 = 1 - ((y_te - y_p)**2).sum() / ((y_te - y_te.mean())**2).sum()
    r2_scores.append(r2)

print(f"Cross-validation R²: {np.mean(r2_scores):.4f} ± {np.std(r2_scores):.4f}")
```

**Step 9: Trading Signal Generation**

```python
# Define entry rule
def generate_signal(hype_current, hype_mean, hype_std, model, X_current):
    # Signal: hype spike >1.5σ
    if hype_current > hype_mean + 1.5*hype_std:
        # Predict price movement
        price_pred = model.predict(X_current)[0]
        
        # Trade if predicted movement >3%
        if abs(price_pred) > 0.03:
            direction = 'BUY' if price_pred > 0 else 'SELL'
            confidence = abs(price_pred) / 0.03  # Normalized confidence
            return direction, confidence
    
    return None, None

# Backtest
positions = []
for i in range(train_size, len(X)):
    signal, conf = generate_signal(
        hype_z.iloc[i],
        hype_z.iloc[:i].mean(),
        hype_z.iloc[:i].std(),
        model,
        X.iloc[i:i+1]
    )
    
    if signal:
        # Simulate trade
        entry_price = price_series.iloc[i]
        exit_price = price_series.iloc[min(i+lag_hours, len(price_series)-1)]
        pnl = (exit_price - entry_price) if signal == 'BUY' else (entry_price - exit_price)
        positions.append({'entry': entry_price, 'exit': exit_price, 'pnl': pnl})

# Calculate strategy performance
total_pnl = sum([p['pnl'] for p in positions])
win_rate = len([p for p in positions if p['pnl'] > 0]) / len(positions)
sharpe = np.mean([p['pnl'] for p in positions]) / np.std([p['pnl'] for p in positions])

print(f"Backtest Results:")
print(f"  Total trades: {len(positions)}")
print(f"  Win rate: {win_rate:.2%}")
print(f"  Sharpe ratio: {sharpe:.2f}")
print(f"  Total P&L: {total_pnl:.4f}")
```

**Step 10: Decision**

```python
# Decision matrix
decision_criteria = {
    'granger_p': best_p < 0.01,
    'correlation': corr_filtered > 0.3,
    'oos_r2': r2_oos > 0.10,
    'win_rate': win_rate > 0.55,
    'sharpe': sharpe > 1.0,
    'no_reverse_causality': min(p_values_rev) > 0.05
}

if all(decision_criteria.values()):
    print("✓ TRADE: All criteria met")
    print(f"  Recommended position size: {win_rate * 100:.1f}% of Kelly")
elif sum(decision_criteria.values()) >= 4:
    print("⚠ CAUTION: Partial criteria met - trade small or monitor")
else:
    print("✗ NO TRADE: Insufficient evidence")

# Print which criteria failed
for criterion, passed in decision_criteria.items():
    status = "✓" if passed else "✗"
    print(f"  {status} {criterion}")
```

---

## 8. Implementation Checklist

### Phase 1: Infrastructure Setup
- [ ] Data pipeline: Hourly scraping of X metrics (volume, engagement, sentiment)
- [ ] Market data: API integration with prediction market (Polymarket, Manifold, etc.)
- [ ] Database: Time-series storage (InfluxDB, TimescaleDB, or PostgreSQL)
- [ ] Notebooks: Jupyter setup with statistical libraries (statsmodels, scipy, pandas)

### Phase 2: Pilot Study (1 Market)
- [ ] Select test market (high liquidity, active hype)
- [ ] Collect 30+ days of hourly data
- [ ] Run full analysis workflow (Steps 1-10 above)
- [ ] Document results and refine methods

### Phase 3: Cross-Validation (10+ Markets)
- [ ] Apply framework to diverse market types
- [ ] Test consistency of findings across markets
- [ ] Identify market characteristics where hype works best
- [ ] Multiple testing correction (Bonferroni/FDR)

### Phase 4: Live Monitoring (Paper Trading)
- [ ] Deploy signal generation in real-time
- [ ] Track predictions vs outcomes (no real money yet)
- [ ] Log false positives and false negatives
- [ ] Calibrate thresholds based on live data

### Phase 5: Real Money (If Criteria Met)
- [ ] Start with 1-2% of capital
- [ ] Strict risk management (stop-loss, position limits)
- [ ] Weekly performance review
- [ ] Kill switch if Sharpe <0.5 for 2+ weeks

### Phase 6: Continuous Improvement
- [ ] Monthly re-estimation of models
- [ ] Decay old data (more weight to recent)
- [ ] A/B test new hype metrics
- [ ] Document market regime changes

---

## Appendix: Common Mistakes to Avoid

### ❌ DON'T:
1. **Cherry-pick timeframes** - "It works great in January!" (ignores other 11 months)
2. **Use in-sample metrics only** - Always validate out-of-sample
3. **Ignore transaction costs** - 2% fees turn +3% edge into +1%
4. **Trade on correlation alone** - Need causality, not just association
5. **Forget reverse causality** - Always test both directions
6. **Overfit on limited data** - Need 100s of observations, not 20
7. **Trust p-values blindly** - Economic significance > statistical significance
8. **Assume stationarity** - Always test (ADF test)
9. **Mix training and test data** - Strict temporal split
10. **Report only successes** - Publication bias kills bankrolls

### ✅ DO:
1. **Pre-register hypotheses** - Write down what you're testing before testing
2. **Use walk-forward validation** - Simulate real trading conditions
3. **Test on multiple markets** - One market success could be luck
4. **Control for confounds** - Include news, volume, volatility controls
5. **Set kill criteria** - "If X happens, I stop trading" decided in advance
6. **Document everything** - Failed tests teach as much as successes
7. **Start small** - Prove it works before scaling
8. **Compare to baselines** - Beat "buy and hold" or "momentum" strategies?
9. **Update regularly** - Markets adapt, models must too
10. **Be honest about uncertainty** - Wide confidence intervals = don't trade

---

## Summary: The Rigorous Path

This framework is designed to answer ONE question with scientific rigor:

**"Does X hype predict prediction market movements in a way that's profitable after costs?"**

The answer is probably **"Sometimes, in specific conditions, for certain markets, with careful execution."**

That's not sexy. But it's honest. And honesty is how you avoid losing money on false patterns.

**Key Principles:**
1. **Causality > Correlation** - Hype must LEAD price, not follow it
2. **Out-of-sample > In-sample** - Validate on unseen data
3. **Economic > Statistical** - Profitable matters more than p<0.05
4. **Robustness > Fragility** - Works across markets, timeframes, conditions
5. **Skepticism > Enthusiasm** - Try to break your hypothesis, not confirm it

If after all this analysis you find a strong, stable, profitable signal:
**Congratulations. Trade it carefully.**

If you don't find a signal:
**Congratulations. You saved yourself from a costly mistake.**

Both outcomes are success. The only failure is fooling yourself.

---

**Next Steps:**
1. Implement data collection pipeline
2. Select 3-5 pilot markets with good hype/price data
3. Run complete analysis workflow
4. Report findings (positive or negative)
5. Decide: trade, monitor, or abandon

Good luck. Stay rigorous. 🧪📊
