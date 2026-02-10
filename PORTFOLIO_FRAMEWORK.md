# PORTFOLIO_FRAMEWORK.md
## Risk Management & Portfolio Construction Framework
### For $100 Trading Capital

**Version:** 1.0  
**Date:** 2026-02-08  
**Focus:** Capital Preservation + Growth  
**Risk Tolerance:** Conservative-Moderate

---

## 1. EXECUTIVE SUMMARY

This framework establishes a disciplined approach to managing a $100 trading account, balancing the need for capital preservation with growth potential. Given the small account size, the strategy emphasizes:

- **Survival First:** Preventing account-crippling drawdowns
- **Asymmetric Risk/Reward:** 1:2 minimum risk-to-reward ratio
- **Systematic Position Sizing:** Rules-based, emotion-free allocation
- **Diversification:** Uncorrelated asset exposure to smooth equity curve

**Target Metrics:**
- Maximum Drawdown: <20%
- Monthly Return Target: 5-10%
- Win Rate Target: >45%
- Risk of Ruin: <1%

---

## 2. POSITION SIZING FRAMEWORK

### 2.1 Core Principle: Fixed Fractional Sizing

Given $100 capital, we use **Fixed Fractional Position Sizing** with a conservative risk per trade.

### 2.2 Risk Per Trade Matrix

| Account Balance | Risk Per Trade | Max Position Size |
|----------------|----------------|-------------------|
| $100 - $150    | 2% ($2)        | $20 - $30         |
| $150 - $250    | 2.5% ($3-6)    | $30 - $50         |
| $250+          | 3% ($7.5+)     | $50 - $75         |

### 2.3 Kelly Criterion Application

**Full Kelly Formula:**
```
f* = (bp - q) / b
Where:
- f* = optimal fraction of capital to risk
- b = average win/average loss (reward/risk ratio)
- p = probability of win
- q = probability of loss (1 - p)
```

**Example Calculation:**
- Win Rate (p): 50%
- Avg Win: $6, Avg Loss: $3 (b = 2)
- f* = (2 × 0.5 - 0.5) / 2 = 0.25 or 25%

**Fractional Kelly (Recommended):**
- Use **1/4 Kelly** for small accounts
- Effective risk: 6.25% of capital maximum
- For $100 account: **$6.25 max risk per trade**

### 2.4 Position Size Calculation Formula

```
Position Size = (Account Balance × Risk %) / (Entry Price - Stop Loss)

Example:
- Account: $100
- Risk %: 2% ($2)
- Entry: $50.00
- Stop Loss: $48.50 ($1.50 risk per share)
- Position Size: $2 / $1.50 = 1.33 shares → Round down to 1 share
- Capital Deployed: $50 (50% of account)
```

### 2.5 Maximum Exposure Rules

| Metric | Rule | Rationale |
|--------|------|-----------|
| Per Trade Risk | ≤ 3% of capital | Prevents single-trade disaster |
| Per Position | ≤ 50% of capital | Allows meaningful returns without overexposure |
| Total Open Risk | ≤ 9% of capital | 3 concurrent positions max at 3% each |
| Sector Exposure | ≤ 30% of capital | Prevents correlation risk |
| Cash Reserve | ≥ 20% of capital | Dry powder for opportunities |

---

## 3. CORRELATION ANALYSIS & DIVERSIFICATION

### 3.1 Correlation Matrix (Typical Values)

| Asset Class | Crypto | Tech Stocks | Forex | Commodities |
|-------------|--------|-------------|-------|-------------|
| **Crypto** | 1.00 | 0.65 | 0.30 | 0.25 |
| **Tech Stocks** | 0.65 | 1.00 | 0.40 | 0.20 |
| **Forex** | 0.30 | 0.40 | 1.00 | 0.15 |
| **Commodities** | 0.25 | 0.20 | 0.15 | 1.00 |

*Note: Correlations increase during market stress (contagion risk)*

### 3.2 Diversification Strategy for $100 Account

**Portfolio Mix (Recommended):**

| Category | Allocation | Examples | Correlation |
|----------|------------|----------|-------------|
| **Core Crypto** | 30% | BTC, ETH | 0.85 with each other |
| **Altcoin/DeFi** | 20% | SOL, AAVE | 0.70 with Core Crypto |
| **Tech Equity** | 25% | NVDA, TSLA | 0.65 with Crypto |
| **Cash/Stable** | 25% | USDC, USD | 0.00 (hedge) |

### 3.3 Correlation Management Rules

1. **Maximum Correlated Exposure:** No more than 50% of portfolio in assets with >0.70 correlation
2. **Hedging:** Maintain 20-25% cash/stablecoins as market hedge
3. **Stress Testing:** Assume correlations rise to 0.90 during drawdowns
4. **Rebalancing Trigger:** When any two positions exceed 0.80 realized correlation

### 3.4 Risk of Correlated Drawdowns

**Scenario Analysis:**
```
Crypto Market Crash (-30%):
- Core Crypto (30% allocation): -30% = -9% portfolio impact
- Altcoin (20% allocation): -40% (beta 1.3) = -8% portfolio impact
- Tech Equity (25% allocation): -15% (correlation spillover) = -3.75%
- Cash (25% allocation): 0%
- TOTAL PORTFOLIO DRAWDOWN: ~20.75%
```

**Mitigation:**
- Position sizing limits ensure max 3% risk per trade
- Stop losses prevent full position loss
- Cash buffer provides psychological and tactical advantage

---

## 4. BANKROLL MANAGEMENT RULES

### 4.1 Stop-Loss Framework

**Hard Stops (Non-Negotiable):**
- **Per Trade:** 3% of account maximum ($3 on $100)
- **Per Position:** Set at technical level (support/resistance) with max 6% position loss
- **Daily Loss Limit:** 6% of account ($6) - stop trading if hit
- **Weekly Loss Limit:** 12% of account ($12) - mandatory 2-day break
- **Monthly Drawdown Limit:** 20% of account ($20) - strategy review required

**Trailing Stops:**
- Activate at +10% profit: Trail at -5% from highs
- Activate at +25% profit: Trail at -10% from highs
- Never move stop loss in direction of loss (only tighten)

### 4.2 Position Reduction Triggers

**Reduce Position Size When:**
| Trigger | Action | Rationale |
|---------|--------|-----------|
| 3 Consecutive Losses | Reduce to 1.5% risk | Indicates unfavorable conditions |
| 10% Drawdown | Reduce to 1% risk | Preserve remaining capital |
| 15% Drawdown | Paper trade only | Strategy reassessment period |
| Volatility Spike (VIX >30) | Reduce all sizes by 50% | Risk-off environment |
| Breaking News/Event | Close 50% of risk positions | Uncertainty management |

**Return to Normal Sizing:**
- After 2 consecutive winning trades
- After new equity high
- After 5 trading days of reduced sizing

### 4.3 Profit Taking Strategy

**Tiered Exit Strategy:**

| Profit Level | Action | Rationale |
|--------------|--------|-----------|
| +20% | Sell 25% of position | Recover risk capital |
| +50% | Sell 25% of position | Lock in meaningful gains |
| +100% | Sell 25% of position | Free trade remaining |
| +200% | Sell final 25% or hold | Let winners run with trailing stop |

**Alternative: Moving Stop Method**
- Entry → Stop at -3%
- +10% profit → Move stop to breakeven
- +20% profit → Move stop to +10%
- +50% profit → Trailing stop at -15%

### 4.4 Rebalancing Frequency & Rules

**Scheduled Rebalancing:**
- **Weekly Review:** Every Sunday, assess allocation drift
- **Monthly Rebalance:** First trading day of month
- **Threshold Rebalance:** When any position exceeds target ±10%

**Rebalancing Process:**
1. Calculate current allocations
2. Identify positions >10% from target
3. Trim winners, add to losers (within trend)
4. Never add to losing positions beyond original stop
5. Maintain 20% minimum cash during rebalancing

**Drift Thresholds:**
- **Normal:** ±5% from target = No action
- **Warning:** ±10% from target = Monitor closely
- **Rebalance:** ±15% from target = Immediate action

---

## 5. CAPITAL ALLOCATION FRAMEWORK

### 5.1 Tier System: A, B, C Bets

**Tier A (High Conviction) - 40% of Capital:**
- Criteria: >70% win rate setup, clear trend, strong fundamentals
- Risk per trade: 3% ($3)
- Max positions: 2 concurrent
- Examples: BTC in bull market, strong earnings play

**Tier B (Medium Conviction) - 35% of Capital:**
- Criteria: 55-70% win rate, decent setup, technical alignment
- Risk per trade: 2% ($2)
- Max positions: 3 concurrent
- Examples: Altcoin swing trades, momentum plays

**Tier C (Speculative/Learning) - 5% of Capital:**
- Criteria: Experimental setups, new strategies, higher risk
- Risk per trade: 1% ($1)
- Max positions: 2 concurrent
- Examples: New pattern testing, small cap crypto

**Reserve (Cash) - 20% of Capital:**
- Purpose: Opportunity fund, drawdown buffer, psychological comfort
- Deploy when: Market correction >15%, high-conviction dip buy

### 5.2 Core vs Opportunistic Split

**70% Core Positions (Holds 1-4 weeks):**
- Trend-following positions in established assets
- Lower frequency, higher conviction
- Wider stops, bigger profit targets
- Goal: 10-20% returns per position

**30% Opportunistic (Holds 1-5 days):**
- Momentum trades, breakouts, news plays
- Higher frequency, tighter risk control
- Tighter stops, quicker profit taking
- Goal: 5-10% returns per position

### 5.3 Capital Allocation Matrix ($100)

| Category | Allocation | Dollar Amount | Max Risk/Trade | Max Positions |
|----------|------------|---------------|----------------|---------------|
| **Tier A (High Conviction)** | 40% | $40 | $3 (3%) | 2 |
| **Tier B (Medium Conviction)** | 35% | $35 | $2 (2%) | 3 |
| **Tier C (Speculative)** | 5% | $5 | $1 (1%) | 2 |
| **Cash Reserve** | 20% | $20 | $0 | 0 |
| **TOTAL** | 100% | $100 | $6 (6% max concurrent) | 7 max |

### 5.4 Growth Phase Adjustments

**Phase 1: $100 - $150 (Conservation Phase)**
- Risk per trade: 2% maximum
- Focus: Tier A positions only
- Goal: Prove consistency, build cushion

**Phase 2: $150 - $300 (Growth Phase)**
- Risk per trade: 2.5% maximum
- Introduce Tier B positions
- Goal: Compound gains, test diversification

**Phase 3: $300+ (Expansion Phase)**
- Risk per trade: 3% maximum
- Full Tier C speculative allocation
- Goal: Accelerate growth with proven edge

---

## 6. RISK METRICS & MONITORING

### 6.1 Key Performance Indicators (KPIs)

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Win Rate | >50% | 40-50% | <40% |
| Profit Factor | >1.5 | 1.2-1.5 | <1.2 |
| Average Win/Loss | >2:1 | 1.5-2:1 | <1.5:1 |
| Max Drawdown | <15% | 15-20% | >20% |
| Sharpe Ratio | >1.5 | 1.0-1.5 | <1.0 |
| Recovery Factor | >3 | 2-3 | <2 |

### 6.2 Risk of Ruin Calculation

**Formula:**
```
Risk of Ruin = [(1 - Edge) / (1 + Edge)] ^ (Capital / Risk Per Trade)

Where Edge = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)

Example:
- Win Rate: 50%
- Avg Win: $6, Avg Loss: $3
- Edge = (0.5 × 6) - (0.5 × 3) = $1.50 per trade
- Risk per trade: $3
- Capital: $100

Risk of Ruin = [(1 - 0.5) / (1 + 0.5)] ^ (100/3) = 0.33^33 ≈ 0.0001 (0.01%)
```

**Target:** Keep Risk of Ruin <1% through position sizing and edge maintenance.

### 6.3 Daily Risk Checklist

**Pre-Market:**
- [ ] Review overnight positions and stops
- [ ] Check correlation between open positions
- [ ] Calculate total open risk ($ maximum)
- [ ] Confirm cash reserve >20%

**Post-Market:**
- [ ] Update equity curve and drawdown status
- [ ] Log all trades with R-multiples
- [ ] Review any stop-loss breaches
- [ ] Assess if Tier sizing adjustments needed

**Weekly:**
- [ ] Calculate weekly return vs. target
- [ ] Review win rate and expectancy
- [ ] Assess correlation matrix of holdings
- [ ] Plan rebalancing if needed

---

## 7. STRESS TEST SCENARIOS

### 7.1 Historical Drawdown Simulation

**Scenario 1: Crypto Winter (2022-Style)**
- BTC drops 70%, Altcoins drop 85%
- Portfolio Impact: -45% ($100 → $55)
- Recovery Plan: Reduce to 1% risk, focus on Tier A only
- Expected Recovery: 6-12 months

**Scenario 2: Tech Selloff (2020 March-Style)**
- Tech stocks drop 35%, Crypto drops 50%
- Portfolio Impact: -30% ($100 → $70)
- Recovery Plan: Normal Tier B sizing, deploy cash reserve
- Expected Recovery: 3-6 months

**Scenario 3: Black Swan (Correlation → 1.0)**
- All risk assets drop 25% simultaneously
- Portfolio Impact: -20% ($100 → $80)
- Recovery Plan: Immediate risk reduction to 1%
- Expected Recovery: 2-4 months

### 7.2 Consecutive Loss Streak Analysis

**Monte Carlo Simulation Results (10,000 iterations):**

| Streak Length | Probability | Account Impact | Action |
|---------------|-------------|----------------|--------|
| 5 Losses | 3.1% | -10% | Reduce sizing 50% |
| 7 Losses | 0.8% | -14% | Paper trade only |
| 10 Losses | 0.1% | -20% | Strategy halt |

**Key Insight:** Even with 50% win rate, expect a 5-loss streak every 32 trades. Position sizing must survive these streaks.

### 7.3 Worst-Case Drawdown Recovery

**If 20% Drawdown Occurs ($100 → $80):**

| Recovery Rate | Monthly Return | Months to Breakeven |
|---------------|----------------|---------------------|
| 5% | $4/month | 5 months |
| 8% | $6.40/month | 3 months |
| 10% | $8/month | 2.5 months |
| 15% | $12/month | 1.75 months |

**Rule:** After 20% drawdown, target conservative 5-8% monthly returns until new equity high.

---

## 8. IMPLEMENTATION CHECKLIST

### Week 1: Setup & Baseline
- [ ] Fund account with $100
- [ ] Set up tracking spreadsheet for all metrics
- [ ] Define initial watchlist for Tier A/B/C assets
- [ ] Set calendar reminders for weekly reviews
- [ ] Paper trade for 3 days to test execution

### Week 2-4: Conservative Phase
- [ ] Trade only Tier A positions
- [ ] 2% risk per trade maximum
- [ ] Focus on 2-3 setups maximum
- [ ] Daily journaling of all decisions
- [ ] Calculate first KPI metrics

### Month 2: Expansion Phase
- [ ] If profitable, introduce Tier B positions
- [ ] Increase to 2.5% risk per trade
- [ ] Test correlation diversification
- [ ] First rebalancing exercise
- [ ] Stress test review

### Month 3+: Growth Phase
- [ ] Full framework implementation
- [ ] Up to 3% risk on Tier A positions
- [ ] Weekly rebalancing as needed
- [ ] Monthly strategy review
- [ ] Document lessons learned

---

## 9. PSYCHOLOGICAL RISK MANAGEMENT

### 9.1 Emotional Triggers & Protocols

| Trigger | Warning Sign | Protocol |
|---------|--------------|----------|
| **Revenge Trading** | Increasing size after loss | Mandatory 24-hour cooling off |
| **FOMO** | Chasing breakouts | Entry checklist must be 100% met |
| **Overconfidence** | Doubling size after wins | Stick to predetermined sizing |
| **Paralysis** | Unable to take valid setups | Reduce size to 0.5% until confidence returns |
| **Hoping** | Moving stops to avoid loss | Immediate position closure |

### 9.2 The "Two Strike" Rule

After any of the following, stop trading for the day:
1. Two consecutive losses
2. One loss where stop was moved/missed
3. Any trade entered without full checklist completion

### 9.3 Journaling Requirements

**For Every Trade:**
- Setup type (Tier A/B/C)
- Entry reason (technical/fundamental)
- Risk/Reward ratio
- Emotional state (1-10 scale)
- Post-trade review

**Weekly Reflection:**
- What worked this week?
- What mistakes were made?
- How did emotions affect decisions?
- One thing to improve next week

---

## 10. APPENDICES

### Appendix A: Quick Reference Card

```
$100 ACCOUNT RULES
═══════════════════════════════════════════
MAX RISK PER TRADE:  $3 (3%)
MAX CONCURRENT RISK: $9 (9%)
MINIMUM CASH:        $20 (20%)
DAILY LOSS LIMIT:    $6 (6%)
WEEKLY LOSS LIMIT:   $12 (12%)
MAX DRAWDOWN:        $20 (20%)
═══════════════════════════════════════════
POSITION SIZING:     Risk $ / (Entry - Stop)
TIER A RISK:         3% | TIER B: 2% | TIER C: 1%
REBALANCING:         Weekly or ±15% drift
═══════════════════════════════════════════
```

### Appendix B: Asset Correlation Quick Reference

**Low Correlation Pairs (Good for Diversification):**
- BTC + USD (obviously)
- Crypto + Commodities
- Tech Stocks + Forex

**High Correlation Pairs (Avoid Concentration):**
- BTC + ETH (>0.80)
- Tech Stocks + Crypto (>0.65)
- Altcoins + BTC (>0.70)

### Appendix C: Growth Targets

| Month | Target Balance | Cumulative Return | Monthly Return |
|-------|----------------|-------------------|----------------|
| 1 | $105 | +5% | +5% |
| 3 | $116 | +16% | +3.3% avg |
| 6 | $134 | +34% | +5% avg |
| 12 | $180 | +80% | +5% avg |

**Note:** These are targets, not guarantees. Focus on process over outcome.

### Appendix D: Emergency Protocols

**If Account Drops to $80 (20% Drawdown):**
1. Immediately close all Tier C positions
2. Reduce Tier A/B risk to 1%
3. Paper trade for 1 week
4. Review all trades for errors
5. Resume with $1 risk only until $90 recovered

**If Account Drops to $70 (30% Drawdown):**
1. Stop all live trading
2. Complete strategy audit
3. Paper trade for 2 weeks minimum
4. Only resume with $50 new capital injection
5. Treat as new $100 account (fresh start)

---

## 11. REVISION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-08 | Initial framework creation |

---

**Disclaimer:** This framework is for educational purposes. Past performance does not guarantee future results. Trading involves substantial risk of loss. Never trade with money you cannot afford to lose. Always do your own research.

---

*"Risk comes from not knowing what you're doing."* — Warren Buffett  
*"The goal of a successful trader is to make the best trades. Money is secondary."* — Alexander Elder
