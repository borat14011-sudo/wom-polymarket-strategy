# BACKTEST SUMMARY - INSIDER/WHALE COPY STRATEGY

## TL;DR

**Status:** ❌ **CANNOT COMPLETE** - Historical data unavailable  
**Recommendation:** ✅ **FORWARD TEST** for 90 days instead  
**Risk Level:** ⚠️ **HIGH** - Unverified claims, execution challenges  
**Time to Validation:** 90 days of real-time tracking

---

## What We Tried

1. **Polysights Historical Alerts**
   - ❌ Twitter/X API requires paid tier ($100-500/mo)
   - ❌ No public archive available
   - ❌ Cannot verify 85% win rate claim

2. **Top Trader Historical Positions**
   - ❌ Polymarket API only shows current snapshot
   - ❌ No historical entry/exit data publicly available
   - ❌ Blockchain indexing requires 4-8hr setup + infrastructure

3. **Goldsky Blockchain Data**
   - ⚠️ Possible but requires significant setup
   - ⚠️ Not a ready-to-use dataset
   - ⚠️ Would need custom pipeline configuration

---

## Key Findings

### Claimed Performance (Unverified)
- **Polysights:** 85% win rate
- **Axios:** 96% accuracy claim
- **Top Traders:** $800K+ avg monthly P&L (top 10)

### Current Leaderboard (Feb 2026)
| Trader | Monthly P&L | Volume |
|--------|-------------|--------|
| 0x4924...3782 | +$2.64M | $14.2M |
| FeatherLeather | +$1.82M | $3.4M |
| weflyhigh | +$1.07M | $6.3M |

**Problem:** Only see **current winners**, not historical failures (survivorship bias)

---

## Why Historical Backtest Matters

**Without 2-year historical data, we cannot:**
1. Validate 85% / 96% win rate claims independently
2. See which traders blew up in 2024-2025
3. Measure alpha decay (how fast edges disappear after alerts)
4. Calculate true risk-adjusted returns (Sharpe ratio)
5. Identify optimal entry/exit timing
6. Understand drawdown periods

**What we miss:**
- Traders who had +500% months then -80% crashes
- Polysights alerts that failed (cherry-picking bias?)
- Market conditions that kill the strategy
- True capital requirements for execution

---

## Critical Risk Factors

### 1. **Timing Risk**
- Polysights has 200K+ followers
- By the time you see alert, odds may have shifted
- **Alpha decay time unknown** (needs measurement)

### 2. **Execution Risk**
- Whale positions = millions in size
- Your $10K copy may face slippage
- Cannot match whale entry/exit prices exactly

### 3. **Selection Bias**
- Claims may be cherry-picked (best markets only)
- Current top traders may not stay on top
- Survivorship bias in leaderboard

### 4. **Liquidity Risk**
- Small markets = can't copy large positions
- Exit when whale exits = potential slippage
- Order book depth varies widely

---

## Recommended Path: 90-Day Forward Test

### Phase 1: Data Collection (Days 1-30)
**Action:** Track Polysights alerts + top traders  
**Cost:** $0 (manual) or $100/mo (automated)  
**Time:** 15 min/day  
**Risk:** Zero - no money deployed

**What to Log:**
- Every Polysights alert (timestamp, market, odds)
- Top trader new positions (daily)
- Market resolutions (win/loss)

### Phase 2: Paper Trading (Days 31-60)
**Action:** Simulate $100K virtual portfolio  
**Rules:** $1K per position, +20% exit, whale exit tracking  
**Risk:** Zero - still virtual  

**Validate:**
- Can you execute strategy consistently?
- Do your results match claims?
- What's your real win rate?

### Phase 3: Live Micro-Test (Days 61-90)
**Action:** Deploy $1K-5K real capital  
**Position Size:** $100 per trade  
**Stop Loss:** -$1K (20% of capital)  

**Decision Criteria:**
- ✅ Win rate >65% → Continue & scale
- ⚠️ Win rate 55-65% → Investigate issues
- ❌ Win rate <55% → Stop, claims false

---

## If You Had Historical Data...

### Theoretical Backtest (2 Years, 400 Trades)

**Conservative (70% win rate):**
- 280 wins × +12% avg = +3,360%
- 120 losses × -7% avg = -840%
- **Net Return:** +252% over 2 years
- **Annual:** ~75%

**Optimistic (85% win rate, per claims):**
- 340 wins × +15% avg = +5,100%
- 60 losses × -8% avg = -480%
- **Net Return:** +462% over 2 years
- **Annual:** ~115%

**Reality Check:**
- These ignore slippage (5-15% drag)
- Assume perfect execution (unlikely)
- No drawdown management
- No black swan events

**Actual expected:** 30-60% annual (if claims hold)

---

## Files Generated

1. **BACKTEST_INSIDER_WHALE.md**
   - Full analysis (11KB)
   - Data availability assessment
   - Risk factors
   - Implementation notes

2. **trades_insider.csv**
   - Template structure
   - "DATA UNAVAILABLE" notice
   - Expected format for forward test

3. **FORWARD_TEST_IMPLEMENTATION_PLAN.md**
   - 90-day execution plan (12KB)
   - Daily tracking templates
   - Success/failure criteria
   - Tool recommendations

4. **BACKTEST_SUMMARY.md** (this file)
   - Quick reference
   - Key findings
   - Recommendations

---

## Bottom Line

### CAN'T DO (Without Significant Investment)
- ❌ 2-year historical backtest
- ❌ Verify 85% / 96% claims
- ❌ Calculate historical Sharpe/Sortino ratios
- ❌ Identify best entry/exit timing from past data

### CAN DO (Starting Today)
- ✅ Track Polysights alerts in real-time (free)
- ✅ Monitor top traders daily (15 min/day)
- ✅ Paper trade for 30-60 days (zero risk)
- ✅ Validate claims with forward test ($0-5K)
- ✅ Make data-driven decision in 90 days

---

## Final Recommendation

**DO:**
1. Start 90-day forward test (data collection phase)
2. Track every Polysights alert + outcome
3. Monitor top 10 traders for position changes
4. Paper trade for validation
5. Test with $1K-5K after 60 days if results look good

**DON'T:**
1. Deploy significant capital based on unverified claims
2. Trust 85% / 96% win rates without independent data
3. Assume you can execute at same speed as insiders
4. Ignore survivorship bias in leaderboards
5. Skip the forward test validation period

**Timeline:**
- **Today:** Set up tracking (1 hour)
- **Days 1-30:** Data collection only (15 min/day)
- **Day 30:** Review, compare to claims
- **Days 31-60:** Paper trading ($0 risk)
- **Days 61-90:** Live test ($1K-5K)
- **Day 90:** Go/No-Go decision

**Expected Outcome:**
- Best case: Validate claims, scale to $10K-50K
- Base case: 60-70% win rate, modest profitability
- Worst case: Claims false, lose 22.5 hours of tracking time (not money)

**Risk/Reward:**
- Time investment: ~25 hours over 90 days
- Financial risk (Phase 3): $1K-5K max
- Potential upside if valid: 50-100% annual returns
- Downside protection: Stop-loss at -$1K

---

## Questions for Decision Maker

1. **Time availability:** Can you dedicate 15 min/day for tracking?
2. **Risk tolerance:** Comfortable testing with $1K-5K in 60 days?
3. **Patience:** Willing to wait 90 days for data-driven decision?
4. **Alternative:** Should we explore other strategies with available historical data?

---

**Generated:** 2026-02-07 04:45 PST  
**Analysis Time:** 25 minutes  
**Subagent:** backtest-insider  
**Status:** COMPLETE - Awaiting decision on forward test deployment
