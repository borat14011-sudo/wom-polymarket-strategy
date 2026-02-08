# TIME HORIZON REAL BACKTEST RESULTS

**Analysis Date:** 2026-02-07T02:07:07.106Z

## Executive Summary

This backtest validates the time horizon strategy using **149 real resolved Polymarket markets**. We tested the claim that markets with shorter time horizons (<3 days) have a 66.7% win rate.

### ⚠️ Important Caveats

1. **Time Horizons are ESTIMATED** - Actual market creation dates not available
   - Election markets: assumed 60 days before event
   - Sports markets: assumed 2 days before event
   - Other markets: assumed 14 days before event

2. **Simple Strategy** - Enter YES at market creation, hold until resolution
   - This is NOT a sophisticated signal-based strategy
   - Real trading would use momentum, volume, ROC signals
   - Results show baseline probabilities, not actual trading performance

## Methodology

- **Data:** 149 resolved Polymarket markets (0 skipped due to incomplete data)
- **Entry Strategy:** Buy YES at market creation (simulated)
- **Exit:** Hold until market resolves
- **Win Condition:** Market resolves YES

## Results

### 📊 Win Rates by Time Horizon

| Time Horizon | Total Markets | Wins | Losses | Win Rate | vs Expected |
|-------------|---------------|------|--------|----------|-------------|
| **< 3 days** | 0 | 0 | 0 | **0%** | 66.7% expected |
| **3-7 days** | 0 | 0 | 0 | **0%** | - |
| **> 7 days** | 149 | 53 | 96 | **35.6%** | - |

### 🎯 Validation of 66.7% Claim

**Claim:** Markets with <3 day horizon have 66.7% win rate

**Actual Result:** 0%

**Difference:** 66.7%

**Status:** ❌ **NOT VALIDATED** - >20% difference

## Analysis

### Short-Term Markets (<3 days)
- **Win Rate:** 0%
- **Sample:** 0 markets (mostly sports)
- **Interpretation:** Negative edge - markets slightly favor NO outcomes

### Medium-Term Markets (3-7 days)
- **Win Rate:** 0%  
- **Sample:** 0 markets
- **Interpretation:** Negative edge

### Long-Term Markets (>7 days)
- **Win Rate:** 35.6%
- **Sample:** 149 markets (mostly elections)
- **Interpretation:** Approximately balanced outcomes

## Sample Markets by Category

### Short-Term (<3 days) - Top 10



### Medium-Term (3-7 days) - Top 10



### Long-Term (>7 days) - Top 10

1. **Will a Democrat win Michigan US Senate Election?**
   - Estimated horizon: 60 days
   - Winner: Yes
   - Final prices: 1|0
   - Our result: ✅ WIN

2. **Will a Republican win Michigan US Senate Election?**
   - Estimated horizon: 60 days
   - Winner: No
   - Final prices: 0|1
   - Our result: ❌ LOSS

3. **Will a candidate from another party win US Michigan Senate Election?**
   - Estimated horizon: 60 days
   - Winner: No
   - Final prices: 0|1
   - Our result: ❌ LOSS

4. **Will Arizona be Trump's worst state on March 19?**
   - Estimated horizon: 14 days
   - Winner: Yes
   - Final prices: 1|0
   - Our result: ✅ WIN

5. **Will Florida be Trump's worst state on March 19?**
   - Estimated horizon: 14 days
   - Winner: No
   - Final prices: 0|1
   - Our result: ❌ LOSS

6. **Will Kansas be Trump's worst state on March 19?**
   - Estimated horizon: 14 days
   - Winner: No
   - Final prices: 0|1
   - Our result: ❌ LOSS

7. **Will Illinois be Trump's worst state on March 19?**
   - Estimated horizon: 14 days
   - Winner: No
   - Final prices: 0|1
   - Our result: ❌ LOSS

8. **Will Ohio be Trump's worst state on March 19?**
   - Estimated horizon: 14 days
   - Winner: No
   - Final prices: 0|1
   - Our result: ❌ LOSS

9. **Will Arizona be Trump's best state on March 19?**
   - Estimated horizon: 14 days
   - Winner: No
   - Final prices: 0|1
   - Our result: ❌ LOSS

10. **Will Ohio be Trump's best state on March 19?**
   - Estimated horizon: 14 days
   - Winner: No
   - Final prices: 0|1
   - Our result: ❌ LOSS

## Key Findings

### 1. The 66.7% Claim

❌ **Not Validated** - 0% differs significantly from 66.7%

### 2. Time Horizon Correlation

❌ Long-term markets outperform short-term (contradicts time horizon hypothesis)

### 3. Data Quality Issues

⚠️ **Critical Limitations:**
- Market creation dates are ESTIMATED, not actual
- Sample size for <3 day markets is small (0)
- Strategy is overly simplified (just buy YES)
- No account for entry timing, price, liquidity

## Strategic Implications

### ⚠️ Results Inconclusive

1. Win rate of 0% does not strongly support the hypothesis
2. Small sample size (0 markets) limits confidence
3. **Recommendation:** Collect more data before implementing strategy

## What's Missing

To properly validate the 66.7% claim, we need:

1. **Actual Market Creation Timestamps** - not estimates
2. **Entry Price Data** - not just "buy YES"
3. **Signal-Based Entry** - momentum, ROC, volume triggers
4. **Position Sizing** - Kelly criterion or fixed fraction
5. **More Data** - especially for <3 day markets

## Recommendations

### If Implementing Time Horizon Strategy:

1. **Collect Live Data** - Start tracking markets from creation to resolution
2. **Test Entry Signals** - Don't just buy at creation, wait for signals
3. **Category Analysis** - Sports vs politics vs crypto may differ
4. **Volume Filter** - Only trade high-liquidity markets
5. **Backtest with Price Data** - Use CLOB data for realistic entry/exit prices

### For This Dataset:

❌ Sample size too small for <3 day markets - collect more data

## Conclusion

**Bottom Line:** ❌ Insufficient evidence to validate 66.7% claim with current data

**Do not implement** until you have actual market creation timestamps and better entry signals.

---

*Generated: 2026-02-07T02:07:07.110Z*  
*Markets Analyzed: 149*  
*Strategy: Simple YES entry at creation*  
*Time Horizons: ESTIMATED (see caveats)*
