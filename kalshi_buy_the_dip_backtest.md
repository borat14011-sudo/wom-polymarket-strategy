# Kalshi "Buy the Dip" Strategy Backtest

**Date:** 2026-02-12 18:40:31

## Executive Summary

- **Total Markets Analyzed:** 9
- **Dip Opportunities Found (>10% drop):** 5
- **Average Expected Value:** 31.05%
- **Total EV (cents):** 13.35

## Methodology

### Entry Criteria
- Price drops >10% from previous day OR previous week price
- Active markets only (excludes settled/expired)

### Exit Strategy
- Hold for mean reversion or resolution
- Target: Previous price level (conservative) or contract resolution (100¢)

### Risk Parameters
- **Win rate:** 11.5% (from Polymarket backtest)
- **Kalshi fees:** ~2% (vs Polymarket 4%)
- **Sample size needed:** 100+ trades for statistical significance

## Results

### Dip Opportunities Identified

| # | Ticker | Title | Entry (¢) | Was (¢) | Drop % | EV % |
|---|--------|-------|-----------|---------|--------|------|
| 1 | KXNEWPOPE-70-AA | Who will the next Pope be? - Anders... | 3¢ | 6¢ | **50.0%** | 275.67% |
| 2 | KXNEWPOPE-70-LA | Who will the next Pope be? - Luis A... | 5¢ | 9¢ | **44.4%** | 125.40% |
| 3 | KXERUPTSUPER-0- | Will a supervolcano erupt before Ja... | 13¢ | 20¢ | **35.0%** | -13.31% |
| 4 | KXNEWPOPE-70-PP | Who will the next Pope be? - Pietro... | 6¢ | 9¢ | **33.3%** | 87.83% |
| 5 | KXCOLONIZEMARS- | Will humans colonize Mars before 20... | 16¢ | 20¢ | **20.0%** | -29.56% |


## Comparison: Kalshi vs Polymarket

| Metric | Polymarket | Kalshi | Difference |
|--------|-----------|--------|------------|
| **Expected Value** | 4.44% | 31.05% | **+26.61%** |
| **Platform Fees** | 4.0% | 2.0% | **-2.0%** (advantage) |

### Conclusion
[OK] Kalshi offers BETTER edge than Polymarket due to lower fees

## Fee Impact Analysis

Lower fees on Kalshi (2% vs 4%) provide a **2% structural advantage**.

If Kalshi markets exhibit similar "dip recovery" dynamics to Polymarket, the edge should be **HIGHER** due to lower transaction costs.

## Recommended Position Sizes

Based on Kelly Criterion with edge of 31.05%:

- **Conservative (¼ Kelly):** 7.8% of bankroll per trade
- **Moderate (½ Kelly):** 15.5% of bankroll per trade
- **Aggressive (Full Kelly):** 31.0% of bankroll per trade

## Risk Warnings

⚠️ **Key Limitations:**

1. **Small sample size:** Current snapshot has only 5 opportunities (need 100+ for statistical significance)
2. **No historical resolution data:** Using Polymarket win rate (11.5%) as proxy - Kalshi markets may behave differently
3. **Liquidity concerns:** Must check bid-ask spreads before entry (not analyzed here)
4. **Mean reversion assumption:** Not all dips recover - requires fundamental analysis
5. **Event risk:** Political/news events can cause permanent price shifts (not just noise)
6. **Survivorship bias:** Only analyzing currently active markets

## Detailed Trade Analysis

### Trade #1: KXNEWPOPE-70-AARB

**Market:** Who will the next Pope be? - Anders Arborelius

- **Entry Price:** 3¢ (current bid)
- **Previous Price:** 6¢ (day/week high)
- **Drop:** 50.0%
- **Expected Value:** 275.67%

**Risk/Reward:**
- **Win scenario (11.5% prob):** Contract resolves YES → +97¢ (or mean reverts)
- **Loss scenario (88.5% prob):** Contract goes to 0 → -3¢

**Rationale:** Price dropped significantly. If this is noise (not fundamentals), mean reversion likely.

---

### Trade #2: KXNEWPOPE-70-LANT

**Market:** Who will the next Pope be? - Luis Antonio Tagle

- **Entry Price:** 5¢ (current bid)
- **Previous Price:** 9¢ (day/week high)
- **Drop:** 44.4%
- **Expected Value:** 125.40%

**Risk/Reward:**
- **Win scenario (11.5% prob):** Contract resolves YES → +95¢ (or mean reverts)
- **Loss scenario (88.5% prob):** Contract goes to 0 → -5¢

**Rationale:** Price dropped significantly. If this is noise (not fundamentals), mean reversion likely.

---

### Trade #3: KXERUPTSUPER-0-50JAN01

**Market:** Will a supervolcano erupt before Jan 1, 2050?

- **Entry Price:** 13¢ (current bid)
- **Previous Price:** 20¢ (day/week high)
- **Drop:** 35.0%
- **Expected Value:** -13.31%

**Risk/Reward:**
- **Win scenario (11.5% prob):** Contract resolves YES → +87¢ (or mean reverts)
- **Loss scenario (88.5% prob):** Contract goes to 0 → -13¢

**Rationale:** Price dropped significantly. If this is noise (not fundamentals), mean reversion likely.

---

### Trade #4: KXNEWPOPE-70-PPAR

**Market:** Who will the next Pope be? - Pietro Parolin

- **Entry Price:** 6¢ (current bid)
- **Previous Price:** 9¢ (day/week high)
- **Drop:** 33.3%
- **Expected Value:** 87.83%

**Risk/Reward:**
- **Win scenario (11.5% prob):** Contract resolves YES → +94¢ (or mean reverts)
- **Loss scenario (88.5% prob):** Contract goes to 0 → -6¢

**Rationale:** Price dropped significantly. If this is noise (not fundamentals), mean reversion likely.

---

### Trade #5: KXCOLONIZEMARS-50

**Market:** Will humans colonize Mars before 2050?

- **Entry Price:** 16¢ (current bid)
- **Previous Price:** 20¢ (day/week high)
- **Drop:** 20.0%
- **Expected Value:** -29.56%

**Risk/Reward:**
- **Win scenario (11.5% prob):** Contract resolves YES → +84¢ (or mean reverts)
- **Loss scenario (88.5% prob):** Contract goes to 0 → -16¢

**Rationale:** Price dropped significantly. If this is noise (not fundamentals), mean reversion likely.

---


## Next Steps for Validation

1. **Expand sample:** Monitor Kalshi for 30-60 days to capture 100+ dip opportunities
2. **Track outcomes:** Record which "dips" actually recovered vs went to zero
3. **Calculate actual win rate:** Validate the 11.5% assumption from Polymarket
4. **Refine entry criteria:**
   - Test different dip thresholds (15%, 20%, 25%)
   - Add volume filters (avoid illiquid markets)
   - Check for news catalysts (avoid fundamental shifts)
5. **Factor spreads:** Include bid-ask spread costs in EV calculation
6. **Backtest timing:** Analyze optimal holding period (days to mean reversion)

## Kalshi API Data Quality Notes

- ✅ Provides `previous_day_price` and `previous_week_price` for easy dip detection
- ✅ Real-time data available via API
- ⚠️ Limited historical price data (no full time-series)
- ⚠️ No historical resolution outcomes readily available

## Conclusion

Based on this **preliminary snapshot analysis**:

- **Opportunities exist:** Found 5 markets with >10% price drops
- **Fee advantage:** Kalshi's 2% fees vs Polymarket's 4% = **2% structural edge**
- **Expected value:** 31.05% per trade (if Polymarket dynamics hold)

**⚠️ CRITICAL:** This is NOT sufficient data for live trading. Need:
1. Larger sample size (100+ trades minimum)
2. Actual win rate validation on Kalshi markets
3. Historical outcome tracking
4. Liquidity and spread analysis

**Recommendation:** Start with paper trading / tracking to validate the strategy on Kalshi before committing capital.

---

*Generated by Kalshi Strategy Tester*  
*Data source: Kalshi API (https://api.elections.kalshi.com/v1/events)*  
*Strategy origin: Polymarket "Buy the Dip" backtest (+4.44% EV validated)*
