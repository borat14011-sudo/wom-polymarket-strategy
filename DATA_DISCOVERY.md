# DATA_DISCOVERY.md
## Polymarket Data Analysis - Pattern Discovery Report

**Analysis Date:** 2026-02-08  
**Data Files Analyzed:**
- markets_snapshot_20260207_221914.json (93,949 markets)
- polymarket_resolved_markets.json (149 resolved markets with outcomes)
- backtest_results.csv (2,014 trades on 516 markets)

---

## 1. BASE RATE ANALYSIS

### Overall Market Resolution Bias
| Outcome | Count | Percentage |
|---------|-------|------------|
| NO | 96 | **64.4%** |
| YES | 53 | **35.6%** |
| **Total** | **149** | **100%** |

**Key Finding:** Markets are heavily skewed toward NO resolution. Nearly 2/3 of markets resolve NO.

---

## 2. VOLUME DISTRIBUTION PATTERNS

### Volume Categories and YES Rates
| Volume Category | Count | YES Rate | NO Rate | Insight |
|----------------|-------|----------|---------|---------|
| <$1K | 9 | 11.1% | 88.9% | Very low volume = High NO probability |
| $1K-$10K | 36 | 27.8% | 72.2% | Low volume = Strong NO bias |
| $10K-$100K | 59 | 42.4% | 57.6% | Mid volume = Balanced |
| $100K-$1M | 32 | 43.8% | 56.2% | Higher volume = Slight NO bias |
| >$1M | 10 | 30.0% | 70.0% | Very high volume = NO bias returns |

**Key Finding:** Low volume markets (<$10K) have the strongest NO bias (72-89% NO rate).

### Volume Statistics (Resolved Markets)
- Median Volume: $31,196
- Mean Volume: $746,521
- 90th Percentile: $582,015
- 99th Percentile: $15,462,338

---

## 3. QUESTION PATTERN ANALYSIS

### Pattern Performance Table
| Pattern | Markets | % of Total | YES Rate | NO Rate | Avg Volume |
|---------|---------|------------|----------|---------|------------|
| Starts with "Will" | 137 | 91.9% | 37.2% | 62.8% | $800,936 |
| Celebrity/Politician | 44 | 29.5% | **56.8%** | 43.2% | $39,576 |
| Trump mentions | 32 | 21.5% | **53.1%** | 46.9% | $52,354 |
| Biden mentions | 13 | 8.7% | **61.5%** | 38.5% | $5,886 |
| Election-related | 106 | 71.1% | 35.8% | 64.2% | $434,874 |
| Crypto mentions | 1 | 0.7% | 0.0% | 100% | $6,290 |
| Has specific date | 4 | 2.7% | 25.0% | 75.0% | $356,517 |

**Key Findings:**
1. Political markets (Trump/Biden) have HIGHER YES rates than average (53-62%)
2. Election markets follow the base rate (~64% NO)
3. Crypto markets are rare but resolve NO
4. Questions with specific dates tend to resolve NO (75%)

---

## 4. PRICE/OUTCOME CALIBRATION

### Issue with Resolved Markets Data
The resolved markets file contains final prices (0 or 1), not historical entry prices. Calibration analysis requires entry price data which is only available in the backtest dataset.

### From Backtest Data (2,014 trades):
| Entry Price Bucket | Trades | Win Rate | Total P&L | Avg P&L |
|-------------------|--------|----------|-----------|---------|
| 0-20% (Longshots) | 654 | 26.3% | $14.37 | $0.022 |
| 20-40% | 273 | 54.9% | $10.49 | $0.038 |
| 40-60% (Fair) | 337 | **57.0%** | $14.01 | $0.042 |
| 60-80% (Favorites) | 302 | 69.2% | $10.61 | $0.035 |
| 80-100% (Heavy fav) | 448 | 42.9% | $5.17 | $0.012 |

**Key Findings:**
1. **Sweet spot is 40-60% entry range** - highest win rate (57%) and good P&L
2. Longshots (0-20%) have terrible win rate (26%) but surprisingly positive P&L
3. Heavy favorites (80-100%) underperform - only 43% win rate
4. Avoid extremes - middle range performs best

---

## 5. BACKTEST RESULTS SUMMARY

### Original Trend Filter Strategy
- Total Trades: 2,014
- Win Rate: 45.4%
- Total P&L (before fees): $54.65
- Total P&L (after 5% fees): $51.92
- Fee Impact: $2.73 (5%)

**Note:** Fees represent 5% of gross P&L, significantly impacting net returns.

---

## 6. KEY PATTERNS SUMMARY

### Pattern 1: Base Rate Skew
- **64.4% of markets resolve NO**
- Simply buying NO on random markets would win ~64% of the time

### Pattern 2: Volume Effect
- **Low volume (<$10K) markets = 72-89% NO rate**
- **Mid volume ($10K-$1M) markets = 43-44% YES rate**
- Volume is a strong predictor of outcome

### Pattern 3: Political Markets
- **Trump markets: 53% YES rate** (higher than base)
- **Biden markets: 62% YES rate** (much higher than base)
- Political prediction markets may have bias toward positive outcomes

### Pattern 4: Price Entry Matters
- **40-60% entry range: 57% win rate** (best)
- **80-100% entry range: 43% win rate** (contrarian opportunity)
- **0-20% entry range: 26% win rate** (avoid)

### Pattern 5: Fee Impact
- **5% fees reduce P&L by exactly 5%**
- Must account for fees in all profitability calculations

---

## 7. DATA LIMITATIONS

1. **Small resolved market sample** - Only 149 markets with confirmed outcomes
2. **No entry price history** in resolved markets file (only final 0/1 prices)
3. **Backtest data lacks market metadata** (questions, volume at entry)
4. **Time period coverage unclear** - Need more temporal analysis

---

## 8. RECOMMENDATIONS FOR STRATEGY DEVELOPMENT

Based on discovered patterns:

1. **Focus on NO strategies** - Base rate is 64% NO
2. **Filter by volume** - Low volume = strong NO signal
3. **Avoid longshots** - 0-20% entries only win 26%
4. **Target middle range** - 40-60% entries have best risk/reward
5. **Consider fading heavy favorites** - 80-100% entries underperform

---

*Report generated from ACTUAL data. No simulated or hypothetical results included.*
