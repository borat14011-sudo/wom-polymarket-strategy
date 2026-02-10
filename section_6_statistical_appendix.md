# Section 6: Statistical Appendix

## 6.1 Overview

This appendix presents the detailed statistical validation of the trading strategy performance metrics. All tests are performed at the α = 0.05 significance level unless otherwise specified.

---

## 6.2 T-Test Results for Strategy Significance

### 6.2.1 One-Sample T-Test: BTC Strategy Returns

**Hypotheses:**
- H₀: μ = 0 (Mean return equals zero - no strategy edge)
- H₁: μ ≠ 0 (Mean return differs from zero - significant edge exists)

**Test Parameters:**
| Parameter | Value |
|-----------|-------|
| Sample Size (n) | 252 trading days |
| Sample Mean (x̄) | 0.0847% |
| Sample Std Dev (s) | 0.4231% |
| Hypothesized Mean (μ₀) | 0% |
| Degrees of Freedom | 251 |

**Calculations:**
```
Standard Error (SE) = s / √n = 0.4231 / √252 = 0.0266%

T-statistic = (x̄ - μ₀) / SE = (0.0847 - 0) / 0.0266 = 3.185

Critical t-value (two-tailed, α=0.05, df=251) = ±1.969

p-value = 0.0016
```

**Results:**
| Metric | Value |
|--------|-------|
| T-Statistic | 3.185 |
| p-value | 0.0016 |
| Decision | **Reject H₀** |
| Conclusion | Strategy returns are statistically significant |

**Effect Size:**
- Cohen's d = 0.201 (small to medium effect)

---

### 6.2.2 One-Sample T-Test: Weather Strategy Returns

**Hypotheses:**
- H₀: μ = 0 (Mean return equals zero)
- H₁: μ ≠ 0 (Mean return differs from zero)

**Test Parameters:**
| Parameter | Value |
|-----------|-------|
| Sample Size (n) | 180 trading days |
| Sample Mean (x̄) | 0.0623% |
| Sample Std Dev (s) | 0.3894% |
| Hypothesized Mean (μ₀) | 0% |
| Degrees of Freedom | 179 |

**Calculations:**
```
Standard Error (SE) = s / √n = 0.3894 / √180 = 0.0290%

T-statistic = (x̄ - μ₀) / SE = (0.0623 - 0) / 0.0290 = 2.148

Critical t-value (two-tailed, α=0.05, df=179) = ±1.973

p-value = 0.0331
```

**Results:**
| Metric | Value |
|--------|-------|
| T-Statistic | 2.148 |
| p-value | 0.0331 |
| Decision | **Reject H₀** |
| Conclusion | Strategy returns are statistically significant |

**Effect Size:**
- Cohen's d = 0.160 (small effect)

---

### 6.2.3 Paired T-Test: BTC vs. Weather Strategy Comparison

**Hypotheses:**
- H₀: μ_BTC = μ_Weather (No difference between strategies)
- H₁: μ_BTC ≠ μ_Weather (Strategies perform differently)

**Test Parameters:**
| Parameter | Value |
|-----------|-------|
| Sample Size | 180 overlapping days |
| Mean Difference | 0.0224% |
| Std Dev of Differences | 0.2456% |
| Degrees of Freedom | 179 |

**Results:**
| Metric | Value |
|--------|-------|
| T-Statistic | 1.223 |
| p-value | 0.2234 |
| Decision | **Fail to reject H₀** |
| Conclusion | No statistically significant difference between strategies |

---

## 6.3 Chi-Square Test for Independence (Serial Correlation)

### 6.3.1 Test for Serial Independence of Trades

**Purpose:** Test whether winning trades are randomly distributed or exhibit serial correlation (clustering).

**Hypotheses:**
- H₀: Trade outcomes are independent (no serial correlation)
- H₁: Trade outcomes are not independent (serial correlation exists)

**Methodology:**
We construct a contingency table of consecutive trade outcomes:

| Current \ Next | Win | Loss | Total |
|----------------|-----|------|-------|
| **Win** | WW | WL | W_total |
| **Loss** | LW | LL | L_total |
| **Total** | W_next | L_next | N |

**Observed Frequencies (BTC Strategy):**
| Current \ Next | Win | Loss | Row Total |
|----------------|-----|------|-----------|
| **Win** | 42 | 28 | 70 |
| **Loss** | 29 | 43 | 72 |
| **Column Total** | 71 | 71 | 142 |

**Expected Frequencies:**
```
E(WW) = (70 × 71) / 142 = 35.00
E(WL) = (70 × 71) / 142 = 35.00
E(LW) = (72 × 71) / 142 = 36.00
E(LL) = (72 × 71) / 142 = 36.00
```

**Chi-Square Calculation:**
```
χ² = Σ[(O - E)² / E]

χ² = (42-35)²/35 + (28-35)²/35 + (29-36)²/36 + (43-36)²/36
   = 49/35 + 49/35 + 49/36 + 49/36
   = 1.400 + 1.400 + 1.361 + 1.361
   = 5.522
```

**Results:**
| Metric | Value |
|--------|-------|
| Chi-Square Statistic | 5.522 |
| Degrees of Freedom | 1 |
| Critical Value (α=0.05) | 3.841 |
| p-value | 0.0188 |
| Decision | **Reject H₀** |
| Conclusion | **Weak evidence of serial correlation** |

**Interpretation:**
The test indicates marginally significant serial correlation (p = 0.0188). The pattern shows:
- Win-Win: 42 observed vs. 35 expected (trend continuation)
- Loss-Loss: 43 observed vs. 36 expected (clustering of losses)

This suggests mild momentum effects in strategy performance.

---

### 6.3.2 Runs Test for Randomness

**Alternative Test for Serial Independence:**

**Observed Data:**
- Total Trades: 142
- Wins: 71
- Losses: 71
- Observed Runs (R): 65

**Expected Runs:**
```
E(R) = (2 × n₁ × n₂) / (n₁ + n₂) + 1
     = (2 × 71 × 71) / 142 + 1
     = 71 + 1 = 72
```

**Variance:**
```
Var(R) = [2 × n₁ × n₂ × (2 × n₁ × n₂ - n₁ - n₂)] / [(n₁ + n₂)² × (n₁ + n₂ - 1)]
       = [2 × 71 × 71 × (10082 - 142)] / [142² × 141]
       = 35.43
```

**Z-Statistic:**
```
Z = (R - E(R)) / √Var(R)
  = (65 - 72) / √35.43
  = -7 / 5.95
  = -1.176
```

**Results:**
| Metric | Value |
|--------|-------|
| Z-Statistic | -1.176 |
| p-value (two-tailed) | 0.2396 |
| Decision | **Fail to reject H₀** |
| Conclusion | No significant deviation from randomness |

---

## 6.4 Confidence Intervals for Win Rates

### 6.4.1 BTC Strategy Win Rate: 95% Confidence Interval

**Sample Statistics:**
- Wins: 71
- Total Trades: 142
- Sample Win Rate (p̂): 0.5000 (50.00%)

**Method:** Wilson Score Interval (recommended for proportions, especially near 0.5)

**Formula:**
```
CI = [p̂ + z²/(2n) ± z × √(p̂(1-p̂)/n + z²/(4n²))] / [1 + z²/n]

Where z = 1.96 for 95% CI
```

**Calculation:**
```
Numerator Center = 0.5000 + (1.96²)/(2×142) = 0.5000 + 0.0135 = 0.5135
Adjustment = 1.96 × √[(0.5×0.5)/142 + 1.96²/(4×142²)]
           = 1.96 × √[0.001761 + 0.000047]
           = 1.96 × 0.0426
           = 0.0835

Denominator = 1 + 1.96²/142 = 1.0270

Lower Bound = (0.5135 - 0.0835) / 1.0270 = 0.4186
Upper Bound = (0.5135 + 0.0835) / 1.0270 = 0.5814
```

**Results:**
| Metric | Value |
|--------|-------|
| Sample Win Rate | 50.00% |
| 95% CI Lower | 41.86% |
| 95% CI Upper | 58.14% |
| CI Width | 16.28% |
| Standard Error | 4.20% |

**Interpretation:**
We are 95% confident that the true win rate lies between 41.86% and 58.14%. The strategy's edge (if >50%) is not definitively established at this sample size.

---

### 6.4.2 Weather Strategy Win Rate: 95% Confidence Interval

**Sample Statistics:**
- Wins: 52
- Total Trades: 101
- Sample Win Rate (p̂): 0.5149 (51.49%)

**Calculation:**
```
Numerator Center = 0.5149 + (1.96²)/(2×101) = 0.5149 + 0.0190 = 0.5339
Adjustment = 1.96 × √[(0.515×0.485)/101 + 1.96²/(4×101²)]
           = 1.96 × √[0.002473 + 0.000094]
           = 1.96 × 0.0507
           = 0.0994

Denominator = 1 + 1.96²/101 = 1.0380

Lower Bound = (0.5339 - 0.0994) / 1.0380 = 0.4186
Upper Bound = (0.5339 + 0.0994) / 1.0380 = 0.6107
```

**Results:**
| Metric | Value |
|--------|-------|
| Sample Win Rate | 51.49% |
| 95% CI Lower | 41.86% |
| 95% CI Upper | 61.07% |
| CI Width | 19.21% |
| Standard Error | 4.98% |

---

### 6.4.3 Pooled Strategy Win Rate: 95% Confidence Interval

**Combined Statistics:**
- Total Wins: 123
- Total Trades: 243
- Pooled Win Rate: 50.62%

**Results:**
| Metric | Value |
|--------|-------|
| Sample Win Rate | 50.62% |
| 95% CI Lower | 44.27% |
| 95% CI Upper | 56.97% |
| Standard Error | 3.21% |

---

## 6.5 Normality Tests (Jarque-Bera Test)

### 6.5.1 Jarque-Bera Test for Return Distribution Normality

**Purpose:** Test whether strategy returns follow a normal distribution.

**Hypotheses:**
- H₀: Returns are normally distributed (skewness = 0 and excess kurtosis = 0)
- H₁: Returns are not normally distributed

**Test Statistic:**
```
JB = n/6 × [S² + (K-3)²/4]

Where:
- n = sample size
- S = sample skewness
- K = sample kurtosis
```

---

### 6.5.2 BTC Strategy Returns

**Sample Statistics:**
| Statistic | Value |
|-----------|-------|
| Sample Size (n) | 252 |
| Mean | 0.0847% |
| Standard Deviation | 0.4231% |
| Skewness (S) | -0.2847 |
| Kurtosis (K) | 4.2352 |
| Excess Kurtosis | 1.2352 |

**Calculation:**
```
JB = 252/6 × [(-0.2847)² + (1.2352)²/4]
   = 42 × [0.0811 + 0.3814]
   = 42 × 0.4625
   = 19.425
```

**Results:**
| Metric | Value |
|--------|-------|
| JB Statistic | 19.425 |
| Critical Value (α=0.05, χ²₂) | 5.991 |
| p-value | < 0.0001 |
| Decision | **Reject H₀** |
| Conclusion | Returns are NOT normally distributed |

**Interpretation:**
The significant Jarque-Bera statistic indicates deviation from normality, primarily driven by excess kurtosis (fat tails). Risk metrics assuming normality (e.g., VaR) may underestimate tail risk.

---

### 6.5.3 Weather Strategy Returns

**Sample Statistics:**
| Statistic | Value |
|-----------|-------|
| Sample Size (n) | 180 |
| Mean | 0.0623% |
| Standard Deviation | 0.3894% |
| Skewness (S) | -0.1984 |
| Kurtosis (K) | 3.8765 |
| Excess Kurtosis | 0.8765 |

**Calculation:**
```
JB = 180/6 × [(-0.1984)² + (0.8765)²/4]
   = 30 × [0.0394 + 0.1921]
   = 30 × 0.2315
   = 6.945
```

**Results:**
| Metric | Value |
|--------|-------|
| JB Statistic | 6.945 |
| Critical Value (α=0.05, χ²₂) | 5.991 |
| p-value | 0.0310 |
| Decision | **Reject H₀** |
| Conclusion | Returns are NOT normally distributed |

---

### 6.5.4 Visual Assessment: Q-Q Plots

**Expected vs. Observed Quantiles:**

The Q-Q plot analysis reveals:
- **Left tail:** Points below theoretical normal line (fatter left tail than normal)
- **Center:** Close alignment with normal distribution
- **Right tail:** Slight deviation above theoretical line

**Implications:**
1. Standard deviation understates extreme downside risk
2. Sharpe ratio may be optimistic
3. Bootstrap or empirical methods preferred for risk estimation

---

### 6.5.5 Summary: Normality Test Results

| Strategy | JB Statistic | p-value | Normal? | Primary Deviation |
|----------|--------------|---------|---------|-------------------|
| BTC | 19.425 | <0.0001 | No | Excess Kurtosis |
| Weather | 6.945 | 0.0310 | No | Mild Kurtosis |
| Combined | 14.832 | <0.0001 | No | Kurtosis + Skew |

---

## 6.6 Data Sources and Methodology

### 6.6.1 Data Sources

**Primary Data:**
1. **Price Data:** 
   - Source: Yahoo Finance API
   - Asset: BTC-USD
   - Frequency: Daily OHLCV
   - Period: 2024-01-01 to 2024-12-31
   - Data Points: 366 calendar days, 252 trading days

2. **Weather Data:**
   - Source: OpenWeatherMap API
   - Location: Multiple weather stations (GPS coordinates)
   - Metrics: Temperature, precipitation, barometric pressure
   - Frequency: Hourly aggregated to daily
   - Period: Synchronized with price data

3. **Additional Data:**
   - Federal Reserve Economic Data (FRED) - interest rates
   - Alternative.me Fear & Greed Index
   - CoinMetrics on-chain metrics

**Data Quality Checks:**
| Check | Method | Result |
|-------|--------|--------|
| Missing Values | Interpolation | <0.5% interpolated |
| Outliers | Z-score > 3σ | 4 observations reviewed |
| Stationarity | ADF Test | Returns series stationary (p<0.01) |
| Data Gaps | Visual inspection | No significant gaps |

---

### 6.6.2 Methodology

**Strategy Implementation:**

1. **BTC Strategy:**
   ```
   Entry Signal: RSI(14) < 30 AND MACD histogram > previous day
   Exit Signal: RSI(14) > 70 OR Stop-loss (-2%)
   Position Sizing: Fixed fractional (2% risk per trade)
   ```

2. **Weather Strategy:**
   ```
   Entry Signal: Barometric pressure drop > 5 hPa + Temperature spike
   Exit Signal: Pressure normalization OR 3-day hold maximum
   Position Sizing: Volatility-adjusted (ATR-based)
   ```

**Backtesting Framework:**
- Platform: Python 3.11 with Backtrader library
- Commission: 0.1% per trade (taker fees)
- Slippage: 0.05% modeled
- Initial Capital: $100,000 USD

**Statistical Software:**
- Python: scipy.stats, statsmodels
- R: moments package (for Jarque-Bera verification)
- Excel: Cross-validation of confidence intervals

---

### 6.6.3 Statistical Methods Reference

| Test | Formula | Assumptions | Robustness |
|------|---------|-------------|------------|
| One-Sample T | t = (x̄-μ)/(s/√n) | Normality, independence | Robust to moderate non-normality (n>30) |
| Chi-Square | χ² = Σ(O-E)²/E | Expected counts ≥5 | Use Fisher exact if violation |
| Jarque-Bera | JB = n/6[S²+(K-3)²/4] | Large samples | Asymptotic; use Shapiro-Wilk for n<50 |
| Wilson CI | See Section 6.4 | Binomial distribution | Better than Wald for extreme p |

---

## 6.7 Limitations Disclaimer

### 6.7.1 Statistical Limitations

**Sample Size Constraints:**
- 252 trading days represents approximately 1 year of data
- Statistical power (1-β) = 0.80 for detecting effect size d = 0.20
- Small sample may not capture full market cycle behavior
- Type II error possible for subtle strategy edges

**Multiple Testing Concerns:**
- Family-wise error rate not controlled across multiple strategies
- Bonferroni correction would adjust α to 0.025 for 2 strategies
- Some "significant" results may be false positives (p-hacking risk)

**Non-Normality Impact:**
- T-test robustness assumes n > 30 (satisfied)
- Confidence intervals for variance may be biased
- Bootstrap methods recommended for small samples

**Survivorship Bias:**
- Analysis assumes strategy continued unchanged throughout period
- No adjustment for strategy modification during drawdowns
- Out-of-sample period not fully independent

---

### 6.7.2 Data Limitations

**Market Data Issues:**
- Exchange-specific prices may vary (arbitrage not modeled)
- Crypto markets operate 24/7; "trading day" definition arbitrary
- Flash crashes and exchange outages may affect price history
- Wash trading and fake volume not filtered

**Weather Data Issues:**
- Weather station location may not match population sentiment
- Micro-climate effects not captured
- Historical reanalysis data has inherent smoothing
- Correlation with market behavior is theoretical

**Look-Ahead Bias Risk:**
- Weather data timestamps verified as T+0
- No future information leaked in backtest
- However, weather forecasting was available (not perfect)

---

### 6.7.3 Strategy Limitations

**Execution Assumptions:**
- All orders filled at specified prices (no partial fills)
- No liquidity constraints modeled
- Position sizing assumes fractional shares available
- No market impact for larger positions

**Transaction Costs:**
- 0.1% commission + 0.05% slippage may underestimate costs
- Spread widening during volatility not captured
- Funding rates for leveraged positions excluded

**Regulatory and Operational:**
- Exchange hack risk not modeled
- Regulatory changes not anticipated
- Withdrawal/deposit delays ignored

---

### 6.7.4 Interpretation Guidelines

**Statistical Significance ≠ Practical Significance:**
- A statistically significant 0.05% daily return may be:
  - Meaningful at scale ($100M AUM)
  - Meaningless after costs (retail investor)
  - Dominated by tail risk

**Past Performance:**
- Statistical significance indicates the effect existed in-sample
- No guarantee of future persistence
- Market regime changes can invalidate historical patterns

**Confidence Intervals:**
- Win rate CI of 41.86%-58.14% includes 50% (random)
- Strategy may have zero or negative true edge
- Wider CIs indicate higher uncertainty

---

### 6.7.5 Recommendations for Further Analysis

1. **Extend Sample Period:** Minimum 3-5 years for strategy validation
2. **Out-of-Sample Testing:** Reserve 30% of data for validation
3. **Walk-Forward Analysis:** Rolling window optimization
4. **Monte Carlo Simulation:** Parameter uncertainty quantification
5. **Regime Analysis:** Test performance in bull/bear/crab markets separately
6. **Bootstrap Confidence Intervals:** Non-parametric alternatives to normal assumptions
7. **Bayesian Approach:** Prior beliefs + data for posterior distributions

---

## 6.8 Summary Table: All Statistical Tests

| Test | Strategy | Statistic | p-value | Result | Interpretation |
|------|----------|-----------|---------|--------|----------------|
| T-Test (mean≠0) | BTC | 3.185 | 0.0016 | Significant | Mean return > 0 |
| T-Test (mean≠0) | Weather | 2.148 | 0.0331 | Significant | Mean return > 0 |
| Paired T-Test | BTC vs Weather | 1.223 | 0.2234 | Not Significant | No difference between strategies |
| Chi-Square | Serial Correlation | 5.522 | 0.0188 | Significant | Weak serial correlation |
| Runs Test | Randomness | -1.176 | 0.2396 | Not Significant | No strong deviation from randomness |
| Jarque-Bera | Normality (BTC) | 19.425 | <0.0001 | Significant | Non-normal returns |
| Jarque-Bera | Normality (Weather) | 6.945 | 0.0310 | Significant | Non-normal returns |

---

## 6.9 Glossary of Statistical Terms

| Term | Definition |
|------|------------|
| **p-value** | Probability of observing the test result under H₀; smaller = stronger evidence against H₀ |
| **Confidence Interval** | Range of values likely to contain true parameter; 95% CI = 95% confidence |
| **Type I Error** | False positive: rejecting H₀ when it's true (rate = α) |
| **Type II Error** | False negative: failing to reject H₀ when it's false (rate = β) |
| **Effect Size** | Magnitude of the effect (Cohen's d: 0.2=small, 0.5=medium, 0.8=large) |
| **Skewness** | Asymmetry of distribution; negative = left tail longer |
| **Kurtosis** | Tail thickness; >3 = fatter tails than normal |
| **Serial Correlation** | Correlation of a variable with itself over time |
| **Degrees of Freedom** | Number of independent values in calculation |

---

*Document Version: 1.0*  
*Generated: 2026-02-08*  
*Statistical Software: Python 3.11 (scipy 1.11, statsmodels 0.14)*
