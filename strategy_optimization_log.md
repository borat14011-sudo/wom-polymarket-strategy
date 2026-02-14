# Strategy Optimization Log
## Kaizen Continuous Improvement Record
*Last Updated: 2026-02-12 22:50 PST (Overnight Kaizen)*

---

## 🎯 Executive Summary

**CRITICAL FINDING:** After analyzing 177,985+ simulated trades across multiple strategies, **only ONE strategy shows consistent positive expected value:**

| Strategy | Expected Value | Win Rate | Verdict |
|----------|---------------|----------|---------|
| **BUY DIP 10%** | **+4.44%** | 11.5% | ✅ PROFITABLE |
| Fade Spike 10% | -5.05% | 14.5% | ❌ AVOID |
| Buy Breakout 80 | -7.75% | 11.8% | ❌ AVOID |
| Fade Longshot | -11.33% | 10.0% | ❌ AVOID |

**Key Insight:** Transaction costs (5.5%) destroy most edges. Only Buy the Dip clears the hurdle.

---

## 📊 Cross-Research Synthesis (Overnight Kaizen Analysis)

### Sources Analyzed:
1. `academic_strategy_analysis.md` - 31 academic papers synthesized
2. `new_strategies_research.md` - Trader interviews & platform strategies
3. `kalshi_pattern_analysis.md` - Kalshi-specific patterns
4. `kalshi_buy_the_dip_backtest.md` - Live Kalshi opportunity scan
5. `real_backtest_price_patterns.md` - 177,985 trade backtest

### 🔗 CONVERGENT FINDINGS (All Sources Agree):

| Finding | Academic | Trader Intel | Backtest |
|---------|----------|--------------|----------|
| Transaction costs critical | 3-10% | 5.5% | 5.5% |
| Mean reversion works | ✅ | ✅ | ✅ (+4.44%) |
| Fade longshots fails | ⚠️ | ⚠️ | ❌ (-11.33%) |
| Avoid extremes (<8%, >92%) | ✅ | ✅ | ✅ |
| Fractional Kelly essential | ✅ | ✅ (1/3) | ✅ |

### ⚡ DIVERGENT FINDINGS (Resolution Required):

| Claim | Source | Backtest Reality | Resolution |
|-------|--------|------------------|------------|
| Favorite-longshot bias: 3-8% edge | Academic | -11.33% (negative!) | **Costs destroy edge** |
| Late-market panic: 5-12% edge | Academic | Not specifically tested | **NEW TEST NEEDED** |
| Narrative fade: 8-18% edge | Academic | Qualitative, hard to backtest | **Manual only** |
| Calibration exploit: 15-25% per bet | Academic | Not tested | **PROMISING - TEST** |

---

## 🆕 NEW INSIGHT: TIME-FILTERED DIP STRATEGY (v2.0)

### The Discovery

Cross-referencing academic research with backtest data reveals an **untested optimization**:

**Academic Finding (Berg & Rietz, Tetlock):**
- Markets LESS efficient at >30 days (early stage, noise)
- Markets LESS efficient at <7 days (panic stage, emotional)
- Markets MOST efficient at 7-30 days (sweet spot for competition)

**Implication:** Our Buy the Dip strategy should EXCLUDE the 7-30 day window!

### Proposed: Buy the Dip v2.0 (Time-Filtered)

```
ENTRY CRITERIA:
1. Price drops >10% from 7-day high
2. Market volume >$10K (liquidity filter)
3. Time to resolution: <7 days OR >30 days (inefficiency windows)
4. Exclude 7-30 day markets (too efficient)

EXIT CRITERIA:
- Mean reversion to 50% of drop, OR
- Resolution, OR
- 14-day maximum hold

EXPECTED IMPROVEMENT:
- Current EV: 4.44%
- Kalshi fee advantage: +2%
- Time filter edge: +1-3% (hypothesis)
- Projected EV: 7-9%
```

### Why This Matters

The backtest used ALL markets. By filtering to **inefficient time windows only**, we should capture:
- Early-stage noise dips (>30 days) - overreactions with time to correct
- Late-stage panic dips (<7 days) - emotional selling that reverts fast

---

## 🔧 Buy the Dip - Parameter Matrix

### Current Parameters (v1.0):
```
ENTRY_TRIGGER: Price drops >10% from previous week
WIN_RATE: 11.5%
EXPECTED_VALUE: 4.44%
SAMPLE_SIZE: 177,985 trades
FEES: 5.5% (Polymarket)
PLATFORM: Polymarket
```

### Proposed Variations:

| Version | Change | Expected Effect | Priority |
|---------|--------|-----------------|----------|
| **v1.1** | Kalshi platform | +2% from fees | ✅ DEPLOY |
| **v1.2** | 15% dip threshold | Higher conviction, fewer trades | TEST |
| **v1.3** | Volume filter >$10K | Better liquidity | TEST |
| **v1.4** | Politics focus | Faster resolution | TEST |
| **v1.5** | News filter (manual) | Avoid fundamental dips | TEST |
| **v2.0** | Time-filtered (<7d OR >30d) | +1-3% edge | **HIGH PRIORITY** |
| **v2.1** | Combined: Kalshi + Time + Volume | All optimizations | FINAL GOAL |

### v1.1 - Kalshi Fee Advantage (READY TO DEPLOY)
```python
PLATFORM: Kalshi
FEE_REDUCTION: 4% → 2% = +2% EV
NEW_EXPECTED_EV: 4.44% + 2% = ~6.44%
RISK: Lower liquidity on some markets
STATUS: ✅ DEPLOY IMMEDIATELY
```

### v2.0 - Time-Filtered Dips (TOP PRIORITY TEST)
```python
TIME_WINDOWS:
  - EARLY_STAGE: resolution > 30 days (noise dips)
  - PANIC_STAGE: resolution < 7 days (emotional dips)
  - EXCLUDE: 7-30 days (efficient competition)

HYPOTHESIS:
  - Early dips: Mean reversion probability ~15% (vs 11.5% baseline)
  - Panic dips: Mean reversion probability ~20% (faster correction)

STATUS: NEEDS HISTORICAL DATA TO VALIDATE
```

---

## 🧪 NEW STRATEGIES TO TEST (Derived from Synthesis)

### Strategy A: Multi-Outcome Field Arbitrage
**Source Insight:** Pope succession market has 7 candidates at 3-9¢ each

**Theory:** Sum of YES prices in multi-outcome markets often exceeds 100%
**Math:**
```
If 7 Pope candidates each at 7¢ average:
Sum = 7 × 7¢ = 49¢ (underpays, field is value)
Sum = 7 × 15¢ = 105¢ (overpays, sell the field)
```

**Test:** Calculate actual sum of Pope YES prices
**Expected Edge:** 5-15% if mispriced
**Priority:** HIGH - easy to verify

### Strategy B: Late-Market Panic Dip (Academic Hybrid)
**Source:** Tetlock (2004), Levitt (2004) - 5-12% documented edge

**Theory:** Markets <72 hours to resolution show panic trading
**Application:** Buy the Dip ONLY in final 72 hours

**Parameters:**
```
ENTRY: Price drops >10% with <72 hours to resolution
EXIT: Hold to resolution (binary outcome)
POSITION: 2-3% of bankroll (higher variance)
```

**Expected Edge:** 5-12% (academic) + 4.44% (dip) = potentially 9-16%
**Priority:** HIGH - combines two documented edges

### Strategy C: Calibration Fade (Extreme Probability)
**Source:** Manski (2006), Tetlock (2017)

**Theory:** Events at 95% resolve ~92% of time (overconfident)
**Application:** Sell extreme confidence, portfolio approach

**Parameters:**
```
ENTRY: Market >90% or <10% confidence
ACTION: Bet AGAINST extreme (buy NO on 95% favorites)
SIZING: 1-2% per trade (high variance)
DIVERSIFY: 15-25 such bets for portfolio smoothing
```

**Expected Edge:** 15-25% per bet (academic claim)
**Win Rate:** 30-40% (low win rate, high payoff)
**Priority:** MEDIUM - needs live tracking

### Strategy D: Supervolcano NO (Base Rate Exploit)
**Current Situation:**
- Kalshi: Supervolcano by 2050 at 13-19¢
- Geological base rate: ~0.3% per 25 years
- Market implies: 13-19% probability
- Overpriced by: 13-18 percentage points!

**Parameters:**
```
ENTRY: Buy NO at 81-87¢
PAYOUT: 100¢ at resolution (if no eruption)
HOLD TIME: Until 2050 (capital lock problem)
EDGE: ~15% but locked for decades
```

**Verdict:** HIGH edge but AVOID due to capital lock
**Alternative:** Trade around news events (volcanic activity spikes)

---

## 📈 Kalshi-Specific Optimization

### Fee Advantage Analysis
| Platform | Entry Fee | Exit Fee | Total | Advantage |
|----------|-----------|----------|-------|-----------|
| Polymarket | 2% | 2% | 4% | baseline |
| Kalshi | 1% | 1% | 2% | **+2%** |

**Impact:** Kalshi's 2% lower fees directly add to EV
- Polymarket EV: 4.44%
- Kalshi Expected EV: **~6.44%**

### Current Kalshi Dip Opportunities (2026-02-12)
| Market | Drop | Entry | Time to Resolution | Priority |
|--------|------|-------|-------------------|----------|
| Pope - Anders Arborelius | 50% | 3¢ | Unknown | HIGH |
| Pope - Luis Antonio Tagle | 44% | 5¢ | Unknown | HIGH |
| Pope - Pietro Parolin | 33% | 6¢ | Unknown | MEDIUM |
| Supervolcano 2050 | 35% | 13¢ | 24 years | LOW (lock) |
| Mars Colony 2050 | 20% | 16¢ | 24 years | LOW (lock) |

**Analysis:** Pope candidates show LARGEST dips + near-term resolution = PRIORITY

### Pope Market Arbitrage Check
```
Anders Arborelius:  3¢
Luis Antonio Tagle: 5¢
Pietro Parolin:     6¢
Other candidates:   ~5-9¢ each (estimate)

NEED TO VERIFY: Total sum of all YES prices
If sum > 100¢: Sell the overpriced options
If sum < 100¢: Buy underpriced candidates
```

---

## ⚠️ Risk Management Framework

### Position Sizing (Refined from Academic + Trader Intel)

**Kelly Criterion with Fractional Adjustment:**
```python
# Base Kelly
kelly = (win_rate * avg_win - loss_rate * avg_loss) / avg_win

# Our parameters (Buy the Dip)
win_rate = 0.115
avg_win = 0.90  # ~90¢ profit on YES resolution
loss_rate = 0.885
avg_loss = 0.10  # ~10¢ average position

# Calculate
kelly = (0.115 * 0.90 - 0.885 * 0.10) / 0.90
kelly = (0.1035 - 0.0885) / 0.90
kelly = 0.0167 = 1.67%

# Apply fractional (1/3 per Betwick)
recommended_size = 1.67% * 0.33 = 0.55% per trade
```

**Recommended Position Sizes:**
| Risk Level | Size | Max Concurrent Positions |
|------------|------|--------------------------|
| Conservative | 0.5% | 20 |
| Moderate | 1.0% | 15 |
| Aggressive | 2.0% | 10 |

### Drawdown Limits
- **Daily:** 5% of bankroll max loss → stop trading
- **Weekly:** 10% → pause and review
- **Monthly:** 15% → major strategy reassessment

### Correlation Management
**Rule:** Don't stack correlated positions
- If trading multiple Pope candidates, they're correlated (one wins, others lose)
- Treat as SINGLE position for sizing purposes
- Same for political events in same region

---

## 📋 Action Items (Prioritized)

### IMMEDIATE (Tonight/Tomorrow):
- [x] Synthesize all 5 research sources ✅
- [x] Document time-filtered dip hypothesis ✅
- [x] Propose v2.0 parameters ✅
- [ ] Calculate Pope market YES sum (arbitrage check)

### THIS WEEK (Feb 13-19):
- [ ] Paper trade Buy the Dip v1.1 on Kalshi (5+ trades)
- [ ] Track all dip opportunities with time-to-resolution
- [ ] Begin building time-filtered dataset
- [ ] Test Strategy B (Late-Market Panic Dip) manually

### THIS MONTH (Feb 2026):
- [ ] Collect 50+ dip opportunities on Kalshi
- [ ] Calculate actual Kalshi win rate
- [ ] Validate v2.0 time filter hypothesis
- [ ] Implement volume filter in screening
- [ ] Test Multi-Outcome Arbitrage live

### Q1 2026:
- [ ] 100+ trade sample for statistical validity
- [ ] Finalize v2.1 (combined optimizations)
- [ ] Compare Kalshi vs Polymarket actual performance
- [ ] Document which categories perform best
- [ ] Consider automation

---

## 📝 Change Log

| Date | Time | Change | Result |
|------|------|--------|--------|
| 2026-02-12 | 20:47 | Initial optimization log created | Baseline established |
| 2026-02-12 | 20:47 | Synthesized 5 research sources | Buy the Dip only profitable strategy |
| 2026-02-12 | 20:47 | Identified Kalshi 2% fee advantage | Expected EV: ~6.44% |
| **2026-02-12** | **22:50** | **Overnight Kaizen: Time-filter discovery** | **v2.0 proposed: exclude 7-30 day markets** |
| 2026-02-12 | 22:50 | Cross-referenced academic + backtest | Late-market panic dip = HIGH PRIORITY |
| 2026-02-12 | 22:50 | Kelly sizing calculated | 0.5-2% per trade recommended |
| 2026-02-12 | 22:50 | 4 new strategy variations proposed | A, B, C, D documented |

---

## 🎯 Key Metrics to Track

### Primary KPIs
1. **Win Rate:** Target 11.5%+ (baseline)
2. **Expected Value per Trade:** Target 6%+ (Kalshi)
3. **Sharpe Ratio:** Track risk-adjusted returns
4. **Max Drawdown:** Keep under 15% monthly

### Secondary KPIs
1. **Opportunities per Week:** Track deal flow
2. **Average Hold Time:** Optimize for capital efficiency
3. **Category Performance:** Which markets work best
4. **Time-to-Resolution Correlation:** Validate v2.0 hypothesis

---

## 🧠 Theoretical Framework (Academic Summary)

### Why Buy the Dip Works (Academic Backing)
1. **Behavioral Overreaction** (Kahneman & Tversky, 1979)
   - Prospect theory: People overweight recent negative information
   - Dips often overshoot fair value

2. **Mean Reversion** (De Bondt & Thaler, 1985)
   - Extreme price movements tend to reverse
   - Works better in prediction markets (bounded 0-100)

3. **Liquidity Premium** (Amihud, 2002)
   - Panic selling creates temporary illiquidity discounts
   - Patient capital captures reversion

### Why Other Strategies Failed
1. **Fade Longshot (-11.33%):** Costs > theoretical bias (3-8%)
2. **Fade Spike (-5.05%):** Spikes often information-driven, not noise
3. **Buy Breakout (-7.75%):** Prediction markets efficient at extremes

---

## 🎯 Next Kaizen Cycle Focus

**Priority 1:** Validate Time-Filtered Dip (v2.0) with historical data
**Priority 2:** Paper trade Buy the Dip v1.1 on Kalshi
**Priority 3:** Test Late-Market Panic Dip (Strategy B)
**Priority 4:** Calculate Pope market arbitrage

---

*Kaizen = Continuous Improvement*
*"Compounding small edges beats chasing big wins"*
*Next Review: 2026-02-13 (daily) or next overnight Kaizen*
