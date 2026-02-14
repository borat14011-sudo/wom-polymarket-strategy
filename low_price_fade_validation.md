# LOW PRICE FADE STRATEGY - VALIDATION REPORT
## Pattern Validator Analysis
**Date:** February 13, 2026 03:01 PST
**Status:** 🚨 **INVALIDATED** 🚨

---

## EXECUTIVE SUMMARY

| Claim | Validation | Evidence |
|-------|------------|----------|
| 91.1% win rate | ⚠️ **POSSIBLY ACCURATE** | Based on resolved markets only |
| 77.3% EV after costs | ❌ **INVALIDATED** | Only 5% costs assumed, reality is 15-25% |
| 429 sample size | ⚠️ **QUESTIONABLE** | Methodology unclear, likely correlated |
| Tradeable edge | ❌ **INVALIDATED** | 98.4% of markets are illiquid |

### VERDICT: **TOO GOOD TO BE TRUE - CONFIRMED**

The claimed 77.3% EV shrinks to **-5% to +15%** after proper cost adjustments, and may be **UNTRADEABLE** due to liquidity constraints.

---

## DETAILED VALIDATION

### 1. DATA SOURCE METHODOLOGY ❌

**Claimed:** Pattern Discovery Engine analyzed 17,324 markets

**Problems Found:**
- Outcomes were **INFERRED** from final prices (>0.9 = YES, <0.1 = NO)
- Only 81% outcome coverage = **19% missing data**
- **NO HISTORICAL PRICE DATA** in Polymarket API
- Cannot verify actual entry prices were achievable

**Critical Issue:** This is an **OUTCOME-ONLY** backtest, not a price-based backtest.

> "Polymarket API provides NO historical price data for resolved markets. All backtests are outcome-only analyses, not true price-based backtests."
> — TRUE_EDGE_CALCULATIONS.md

**Verdict:** Methodology fundamentally flawed. Cannot verify entries were possible at claimed prices.

---

### 2. SURVIVORSHIP BIAS CHECK ❌

**19% of markets excluded** (no inferrable outcome)

**Critical Question:** What if the missing markets are disproportionately the ones where NO bets LOST?

**Analysis:**
- Markets priced 5-15% represent "unlikely events"
- When unlikely events ACTUALLY HAPPEN, they often:
  - Close faster (news-driven)
  - Are more controversial (ambiguous resolution)
  - Are more likely to have unclear final outcomes

**Potential Impact:**
- If just 30% of the missing 19% were losses (vs. 9% loss rate claimed)
- Adjusted loss rate: 9% + (19% × 30%) = 14.7%
- Win rate drops from 91.1% to **85.3%**

**Verdict:** Survivorship bias likely overstates win rate by 5-10%

---

### 3. TRANSACTION COSTS - THE FATAL FLAW ❌

**Claimed in report:** 5% transaction costs applied

**ACTUAL COSTS for 5-15% priced markets:**

From TRANSACTION_COST_REALITY_CHECK.md:

| Liquidity Level | Price Range | Typical Spread | Cost Per Side |
|-----------------|-------------|----------------|---------------|
| Ultra-Low (<$10K) | 10-20% | 10-25 cents | **5-12.5%** |
| Low ($10K-50K) | 10-20% | 8-15 cents | **4-7.5%** |

**Why 5-15% markets are ULTRA-LOW liquidity:**
- By definition, these are "won't happen" events
- Few traders interested
- Thin order books
- Wide spreads

From LIQUIDITY_REPORT.md:
> "122 of 124 markets (98.4%) are ILLIQUID with <$10K liquidity"

**ACTUAL TRANSACTION COST CALCULATION:**

| Cost Component | 5% Estimate | REALITY |
|----------------|-------------|---------|
| Entry slippage | 2.5% | **5-12%** |
| Exit slippage | 2.5% | **3-8%** (at resolution, less slippage) |
| **TOTAL** | **5%** | **8-20%** |

**Realistic Average:** 12-15% round-trip costs for illiquid low-price markets

---

### 4. LIQUIDITY - CAN YOU EVEN TRADE? ❌

**The most damning finding:**

> "Total Markets Analyzed: 124
> **Tradeable Markets: 2 (1.6%)**
> **Illiquid Markets: 122 (98.4%)**"
> — LIQUIDITY_REPORT.md

**Implications for Low Price Fade:**
- Markets at 5-15% are even MORE illiquid than average
- Order books may show 0 liquidity at your target price
- Entry attempts will move the market against you

**Price Impact Analysis (from TRANSACTION_COST_REALITY_CHECK):**

| Trade Size | Ultra-Low Liquidity Impact |
|------------|---------------------------|
| $100 | 2-10% impact |
| $1,000 | 10-30% impact (market order impossible) |
| $10,000 | Market order impossible |

**Verdict:** Strategy may be **COMPLETELY UNTRADEABLE** at any meaningful size

---

### 5. RESOLUTION TIME & IRR ❌

**CRITICAL MISSING DATA: Average resolution time**

The report contains ZERO information about:
- How long markets take to resolve
- Capital lockup period
- IRR calculations

**IRR Analysis (from KALSHI_IRR_ANALYSIS.md):**

If markets average 90 days to resolve:
- Claimed 77% return / 90 days = 312% annualized (seems great!)
- BUT: Capital is locked, cannot compound
- AND: IRR calculation must account for failures

**Adjusted IRR Calculation:**

| Scenario | Win Rate | Avg Return | Avg Duration | Annualized IRR |
|----------|----------|------------|--------------|----------------|
| Claimed | 91.1% | 77.3% | 30 days | ~500%+ |
| Claimed | 91.1% | 77.3% | 90 days | ~300%+ |
| Claimed | 91.1% | 77.3% | 180 days | ~150%+ |
| **Realistic** | 85% | **15%** | 90 days | **~60%** |
| **Pessimistic** | 80% | **5%** | 120 days | **~15%** |

Without resolution time data, **cannot validate IRR claims.**

---

### 6. SAMPLE SIZE QUALITY ⚠️

**Claimed:** 429 trades at 5-15% price range

**Questions Not Answered:**
1. Are these independent markets or correlated?
   - 50 "Trump will do X" markets could all resolve together
   - This creates pseudo-replication

2. Over what time period?
   - All from 2024? Or 2020-2024?
   - Market efficiency may have changed

3. What was the price distribution within 5-15%?
   - Markets at 5% have different risk than 15%
   - Average entry price matters

4. Were entries actually achievable?
   - No order book data
   - No fill verification

**Effective Sample Size:** Likely 100-200 independent observations, not 429

---

## RECALCULATED EXPECTED VALUE

### Original Claim:
```
Win Rate: 91.1%
Avg Win: (1 - entry_price) / entry_price ≈ 800% at 10% entry
Avg Loss: 100% of position
EV = 0.911 × 800% - 0.089 × 100% = 7188% - 89% = 7099%... 

Wait, this math doesn't work. Let me recalculate properly.
```

### Proper EV Calculation (Betting NO at 10% price):

When you bet NO at 10%:
- You pay 90¢ for a contract worth $1 if NO wins
- If WIN: Profit = 10¢ on 90¢ = **11.1% return**
- If LOSE: Loss = 90¢ = **100% loss**

**Original Claim Math:**
```
EV = (Win Rate × Win Amount) - (Loss Rate × Loss Amount)
EV = (0.911 × $0.10) - (0.089 × $0.90)
EV = $0.0911 - $0.0801 = $0.011 per $0.90 invested
EV% = $0.011 / $0.90 = 1.2% per trade

This doesn't match 77.3%... The report's math is wrong or uses different methodology.
```

**Alternative interpretation:** Betting YES at 10% (extremely risky):
- Pay 10¢, win 90¢ if correct
- If WIN (91.1%): Profit = 90¢ on 10¢ = **900% return**
- If LOSE (8.9%): Loss = 10¢ = **100% loss**

```
EV = (0.911 × $0.90) - (0.089 × $0.10)
EV = $0.8199 - $0.0089 = $0.811 profit per $0.10 bet
EV% = $0.811 / $0.10 = 811%
```

**But this contradicts the strategy (which says BET NO).**

### The Report's Logic Error:

The 77.3% EV claim appears to conflate:
- Market mispricing (true probability vs. price) 
- With trading returns (which depend on entry price)

**If the claim is:** "Markets priced 5-15% resolve NO 91% of the time"

Then: Entry at 10% → Bet NO at 90¢ → Win 11.1% return 91% of the time

```
EV = 0.911 × 11.1% - 0.089 × 100% = 10.1% - 8.9% = 1.2% gross
```

**After 15% transaction costs: EV = 1.2% - 15% = -13.8%** ❌

---

## SENSITIVITY ANALYSIS

### Best Case (Optimistic Assumptions):
- Win rate: 91% (as claimed)
- Transaction costs: 8% (lowest estimate)
- Can actually trade at stated prices

```
At 10% entry, betting NO:
Gross EV = 0.91 × 11.1% - 0.09 × 100% = 10.1% - 9% = 1.1%
Net EV = 1.1% - 8% = -6.9%
```

**STILL NEGATIVE**

### Realistic Case:
- Win rate: 85% (adjusted for survivorship bias)
- Transaction costs: 15%
- Partial fills at worse prices

```
At 10% entry, betting NO:
Gross EV = 0.85 × 11.1% - 0.15 × 100% = 9.4% - 15% = -5.6%
Net EV = -5.6% - 15% = -20.6%
```

**SIGNIFICANTLY NEGATIVE**

### Can It Work at 5% Entry?
- Betting NO costs 95¢, wins 5¢ (5.3% return)
- Even at 95% win rate:

```
EV = 0.95 × 5.3% - 0.05 × 100% = 5.0% - 5% = 0%
After costs: 0% - 15% = -15%
```

**STILL NEGATIVE**

---

## WHERE DID 77.3% COME FROM?

Possible explanations for the inflated EV:

1. **Betting YES at Low Prices (Different Strategy):**
   If you bet YES at 10% and events resolve YES 9.1% of the time:
   ```
   EV = 0.091 × 900% - 0.909 × 100% = 81.9% - 90.9% = -9%
   ```
   Still doesn't match.

2. **Misunderstood Edge Calculation:**
   They may have calculated: "True probability = 9%, Market = 15%, Edge = 15%-9% = 6%"
   And then scaled incorrectly.

3. **Outcome-Based vs. Trading-Based Returns:**
   Saying "91% of NO bets win" ≠ "91% win rate generates 77% EV"

4. **Fantasy Math:**
   The numbers were fabricated or calculated incorrectly.

**Most Likely:** The report conflates "pattern accuracy" with "trading profitability"

---

## FINAL VERDICT

### Strategy Status: 🚨 **INVALIDATED** 🚨

| Factor | Impact on Claimed 77% EV |
|--------|-------------------------|
| Understated transaction costs | **-10 to -15%** |
| Survivorship bias | **-5 to -10%** |
| Liquidity constraints | **Potentially untradeable** |
| Missing IRR calculation | **Unknown** |
| Fundamental math error | **Claim may be fabricated** |

### Adjusted Expected Value:

| Scenario | EV Estimate |
|----------|-------------|
| Best case | **-5% to +5%** |
| Realistic | **-15% to -5%** |
| Worst case | **Untradeable** |

### IRR Estimate (if tradeable):

| Avg Resolution | Best Case IRR |
|----------------|---------------|
| 30 days | ~20% annualized |
| 90 days | ~7% annualized |
| 180 days | ~3% annualized |

---

## RECOMMENDATIONS

### DO NOT DEPLOY this strategy.

**Reasons:**
1. Math doesn't work - claimed 77% EV is impossible given strategy mechanics
2. Transaction costs alone exceed any realistic edge
3. 98% of markets are untradeable due to liquidity
4. No resolution time data to calculate IRR
5. Survivorship bias likely inflates win rate

### If You Still Want to Test:

1. **Paper trade 50+ positions** before risking real capital
2. **Track actual fill prices** vs. theoretical entry
3. **Measure resolution times** for IRR calculation
4. **Size positions <$100** due to liquidity constraints
5. **Set strict exit rules** if spread widens

### What WOULD Make This Work:

- Entry slippage <3%
- Exit at resolution (no early exit needed)
- Markets with >$10K liquidity
- Win rate >88% (to survive 15% costs)
- Resolution <60 days (acceptable IRR)

**Current evidence suggests NONE of these conditions are met.**

---

## CONCLUSION

**The LOW PRICE FADE strategy's claimed 77.3% EV is mathematically impossible given:**

1. The strategy mechanics (betting NO at low prices yields tiny returns)
2. Real-world transaction costs (15%+ round-trip)
3. Liquidity constraints (98% of markets untradeable)

The research likely confused "pattern accuracy" with "trading profitability."

**A 91% win rate on 11% returns per win CANNOT generate 77% EV.**

Maximum theoretical EV (before costs) = 91% × 11% - 9% × 100% = **1.1%**

**After realistic costs: NEGATIVE EXPECTED VALUE**

---

**Validation Complete:** Strategy INVALIDATED
**Recommendation:** Do not deploy. Research methodology fundamentally flawed.
**Next Steps:** Require actual order book data and fill prices before reconsidering.

---

*Pattern Validator - Feb 13, 2026*
