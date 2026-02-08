# Prediction Market Hype Trading Strategy Framework

**Version:** 1.0  
**Date:** 2026-02-06  
**Status:** Preliminary Design (Pre-Backtest)

---

## Executive Summary

This framework outlines a disciplined approach to trading prediction markets based on hype cycles and momentum. The strategy exploits short-term mispricings caused by viral attention, news catalysts, and herding behavior, while maintaining strict risk controls to avoid the "degenerate gambling" trap.

**Core Thesis:** Prediction markets exhibit temporary inefficiencies during hype cycles when attention-driven trading overwhelms fundamental pricing. These windows create exploitable momentum opportunities for traders who can detect, enter, and exit systematically.

**Key Principle:** Edge × Discipline > Intuition. Every trade must have a quantifiable signal and predefined risk parameters.

---

## 1. ENTRY SIGNALS

### 1.1 Primary Signal: Volume Surge Detection

**Metric:** Relative Volume Ratio (RVR)
```
RVR = Current_Period_Volume / Avg_Volume_Last_N_Periods
```

**Thresholds:**
- **STRONG:** RVR > 3.0 (volume 3x normal)
- **MODERATE:** RVR > 2.0
- **WEAK:** RVR > 1.5

**Lookback Period:** N = 24 hours for short-term markets, 7 days for longer-dated

**Why it matters:** Volume spikes indicate new attention/information entering the market, often before price fully adjusts.

### 1.2 Secondary Signal: Price Momentum

**Metric:** Rate of Change (ROC)
```
ROC = (Current_Price - Price_T_Hours_Ago) / Price_T_Hours_Ago × 100
```

**Thresholds:**
- **STRONG:** |ROC| > 15% over 6 hours
- **MODERATE:** |ROC| > 10% over 12 hours
- **WEAK:** |ROC| > 5% over 24 hours

**Direction:** Can trade both upward AND downward momentum (hype can work both ways)

### 1.3 Tertiary Signal: Liquidity Depth Imbalance

**Metric:** Order Book Imbalance Ratio
```
Imbalance = (Bid_Liquidity - Ask_Liquidity) / Total_Liquidity
```

**Thresholds:**
- **BULLISH:** Imbalance > 0.3 (strong buying pressure)
- **BEARISH:** Imbalance < -0.3 (strong selling pressure)

**Requirement:** Must have minimum $10k total liquidity to avoid manipulation

### 1.4 Multi-Signal Confirmation Matrix

| Signal Strength | Entry Action | Confidence Level |
|----------------|--------------|------------------|
| 3 STRONG signals | Full position size | HIGH |
| 2 STRONG + 1 MODERATE | 75% position size | HIGH |
| 1 STRONG + 2 MODERATE | 50% position size | MEDIUM |
| 3 MODERATE signals | 25% position size | LOW |
| < 3 signals | NO TRADE | - |

**Anti-Pattern:** Never enter on single signal alone, no matter how strong.

### 1.5 Disqualifying Conditions (DO NOT TRADE)

- Market has < 48 hours until resolution (too little time for momentum)
- Total market liquidity < $5,000 (manipulation risk)
- You already hold a correlated position > 50% of target size
- Market resolution criteria unclear or subjective
- Recent major news event not yet reflected in price (wait for initial reaction)
- Market maker spread > 5% (poor liquidity quality)

---

## 2. POSITION SIZING

### 2.1 Kelly Criterion Foundation

**Classic Kelly Formula:**
```
f* = (p × b - q) / b

Where:
f* = fraction of bankroll to bet
p = probability of winning
q = 1 - p
b = odds received (profit/stake)
```

**Problem:** Kelly is aggressive and assumes perfect probability estimation (which we don't have).

### 2.2 Fractional Kelly Approach

**Modified Formula:**
```
Position_Size = (Kelly_Fraction × Confidence_Multiplier × Bankroll) / 4

Confidence_Multiplier:
- HIGH confidence: 1.0
- MEDIUM confidence: 0.5
- LOW confidence: 0.25
```

**Rationale:** Dividing by 4 (quarter-Kelly) significantly reduces variance while preserving most long-term growth. More aggressive than half-Kelly, but safer than full Kelly.

### 2.3 Signal-Based Sizing

**Base Position Sizes:**
- **Strong 3-signal entry:** 4% of bankroll
- **2 strong + 1 moderate:** 3% of bankroll
- **1 strong + 2 moderate:** 2% of bankroll
- **3 moderate signals:** 1% of bankroll

**Dynamic Adjustments:**
- **High volatility market (historical ROC std dev > 20%):** Reduce size by 30%
- **Low liquidity (<$20k):** Reduce size by 50%
- **Perfect setup (all strong + favorable liquidity):** Increase to max 5%

### 2.4 Absolute Position Limits

- **Single market max:** 5% of bankroll (hard cap)
- **Related markets total:** 10% of bankroll (e.g., multiple crypto markets)
- **Total exposure across all positions:** 25% of bankroll
- **Cash reserve minimum:** 50% of bankroll (always)

**Example:**
- Bankroll: $10,000
- Strong 3-signal setup
- Base position: 4% × $10,000 = $400
- Check exposure: Currently 18% deployed
- Can add: Yes (18% + 4% = 22% < 25%)
- Execute: Place $400 position

---

## 3. EXIT RULES

### 3.1 Profit Targets

**Tiered Take-Profit System:**

**For LONG positions (bought YES shares):**
- **TP1 (25% of position):** +8% price move
- **TP2 (50% of position):** +15% price move
- **TP3 (25% of position):** +25% price move OR trailing stop

**For SHORT positions (bought NO shares):**
- Same structure, inverse direction

**Rationale:** Lock in early gains while letting winners run. Prevents "sold too early" regret while ensuring profitability.

### 3.2 Stop Losses

**Hard Stop Loss:** -12% from entry

**Why -12%?** 
- Large enough to avoid noise stops
- Small enough to preserve capital
- Asymmetric risk/reward (targeting +15% average, risking -12%)

**Time-Decay Stop:**
- If position held > 3 days with < +5% gain: Close 50%
- If position held > 7 days with < +8% gain: Close 100%

**Rationale:** Hype trades are time-sensitive. If momentum hasn't developed, edge is gone.

### 3.3 Momentum Reversal Exits

**Exit immediately if:**
- Volume drops to < 0.5x average for 24 hours (hype fading)
- Price retraces > 50% of initial momentum move
- Opposing signal emerges (e.g., strong selling pressure after buying)

### 3.4 Time-Based Exits

**Market Resolution Proximity:**
- **7 days to close:** Exit 50% of position
- **3 days to close:** Exit 100% of position

**Rationale:** As resolution approaches, odds converge to fundamentals. Momentum edge disappears.

### 3.5 Circuit Breaker Exit

**Portfolio-Level Trigger:**
- If total portfolio drawdown reaches -15% from peak: Close ALL positions
- Reassess strategy before re-entering
- This prevents death spirals during adverse market conditions

---

## 4. RISK MANAGEMENT

### 4.1 Position-Level Risk Controls

**Per-Trade Risk Limits:**
- Max loss per trade: 1.2% of bankroll (10% position × 12% stop = 1.2%)
- Max risk across all open positions: 5% of bankroll
- No more than 3 positions in same market category (e.g., crypto)

### 4.2 Correlation Management

**Identify Related Markets:**
- Same underlying event (different resolutions)
- Same category (all crypto, all sports, all politics)
- Same time period (all resolving same week)

**Correlation Limits:**
- Max 2 positions on same underlying event
- Max 10% bankroll in single category
- If correlation coefficient > 0.7 between markets, treat as single position for sizing

### 4.3 Drawdown Controls

**Daily Loss Limit:** -5% of bankroll
- If hit, stop trading for the day
- Journal what went wrong
- Review next day before resuming

**Weekly Loss Limit:** -10% of bankroll
- If hit, pause trading for 3 days
- Conduct full strategy review
- May indicate strategy breakdown or adverse market regime

**Monthly Loss Limit:** -20% of bankroll
- If hit, STOP trading for 30 days
- Full strategy overhaul required
- Only resume after documented improvements

### 4.4 Kelly Criterion as Risk Governor

**Continuous Monitoring:**
```
If Estimated_Edge < 0:
    DO NOT TRADE
    
If Kelly_Fraction > 0.25:
    Cap at 0.25 (never bet > 25% even if Kelly suggests it)
    
If Kelly_Fraction < 0.02:
    Skip trade (edge too small vs risk)
```

### 4.5 Diversification Requirements

**Portfolio Composition:**
- Minimum 3 positions active (unless in drawdown recovery)
- Maximum 8 positions (attention dilution beyond this)
- No more than 40% in a single market category
- Stagger entry times (avoid batch deployment)

### 4.6 Liquidity Risk Management

**Minimum Liquidity Requirements:**
- Position size must be < 10% of available market liquidity
- Must be able to exit position within 2 hours at < 2% slippage
- Monitor liquidity during position (exit if drops below threshold)

**Slippage Budget:**
- Account for 0.5-1% slippage on entry
- Account for 1-2% slippage on exit
- Include in profit calculations (don't ignore friction costs)

---

## 5. MARKET SELECTION CRITERIA

### 5.1 Ideal Market Characteristics

**Must-Haves:**
1. **Clear, objective resolution criteria** (no room for interpretation)
2. **Minimum $10k liquidity** (preferably $50k+)
3. **Active market maker** (bid-ask spread < 3%)
4. **Time to resolution: 1-4 weeks** (sweet spot for hype cycles)
5. **Historical volatility** (boring markets don't hype)

**Nice-to-Haves:**
- Multiple related markets (cross-market opportunities)
- News/social media coverage (external hype indicators)
- Retail participation (institutional markets less prone to hype)

### 5.2 Market Category Ranking

**Tier 1 (Best for Hype Trading):**
- **Cryptocurrency markets** (high volatility, retail participation, news-driven)
- **Sports** (clear outcomes, emotional fans, event-driven)
- **Entertainment** (awards shows, box office, reality TV)
- **Tech product launches** (viral potential, fan communities)

**Tier 2 (Moderate):**
- **Politics** (can work, but insider risk and slower to resolve)
- **Economic indicators** (some momentum, but more efficient)
- **Legal outcomes** (case-dependent)

**Tier 3 (Avoid for Hype Strategy):**
- **Long-dated macro predictions** (too slow for momentum)
- **Niche academic questions** (no retail interest)
- **Highly liquid institutional markets** (too efficient)

### 5.3 Avoid These Market Types

**Red Flags:**
- **Insider information risk** (court cases, private company events)
- **Manipulation potential** (low liquidity + interested parties)
- **Ambiguous resolution** (subjective judgment calls)
- **Binary all-or-nothing** with no middle ground (less momentum opportunity)
- **Markets you don't understand** (stick to your circle of competence)

### 5.4 Market Screening Process

**Step 1: Filter by liquidity**
- Remove markets with < $10k volume

**Step 2: Filter by time horizon**
- Focus on 1-4 week resolution windows

**Step 3: Category focus**
- Prioritize Tier 1 categories

**Step 4: Signal scan**
- Run volume, momentum, and liquidity checks
- Flag markets meeting 2+ entry signal thresholds

**Step 5: Manual review**
- Check news/context
- Verify resolution criteria
- Assess competition (who else is trading this?)

**Output:** Watchlist of 10-20 candidate markets, ranked by signal strength

---

## 6. TIMING STRATEGY

### 6.1 The Hype Cycle Framework

**Phase 1: Ignition (0-20% of cycle)**
- Trigger: News breaks, volume starts rising
- Price: Initial move 5-10%
- **Strategy:** SCOUT but don't enter (too early = false start risk)

**Phase 2: Acceleration (20-50% of cycle)**
- Volume: 2-3x normal, accelerating
- Price: Strong momentum, 10-25% move
- **Strategy:** ENTER here (best risk/reward)
- **Why:** Momentum confirmed, but room to run

**Phase 3: Peak Hype (50-70% of cycle)**
- Volume: 5x+ normal, mania
- Price: Extreme moves, 25-50%+
- **Strategy:** SCALE OUT (take profits, reduce exposure)
- **Why:** Maximum risk of reversal

**Phase 4: Exhaustion (70-100% of cycle)**
- Volume: Declining from peak
- Price: Volatility but no direction
- **Strategy:** EXIT fully (hype over)
- **Why:** Reversion to fundamentals begins

### 6.2 Entry Timing Tactics

**Best Entry Windows:**
- **Early morning (6-9 AM EST):** Overnight news digestion, lower competition
- **After initial spike:** Wait for 1-2 hour consolidation, then enter on retest
- **News catalyst + volume confirmation:** Don't front-run, wait for signal

**Avoid Entering:**
- **After vertical price move:** Wait for pullback (5-8%)
- **At all-time highs/lows:** Often reversal zones
- **During low liquidity hours:** Worse execution, higher manipulation risk

### 6.3 Exit Timing Tactics

**Best Exit Windows:**
- **Profit target hit:** Execute immediately (don't get greedy)
- **Momentum reversal detected:** Exit within 1 hour
- **Pre-market close:** Exit 50% position 7 days before resolution

**Avoid Exiting:**
- **On noise:** Don't stop out on temporary dips if volume/momentum intact
- **Too early:** Let TP1 hit before taking profits

### 6.4 Cycle Detection Metrics

**How to identify which phase you're in:**

```
Cycle_Score = (Current_Volume / Peak_Volume × 40) + 
              (Current_ROC / Max_ROC × 30) +
              (Time_Elapsed / Expected_Cycle_Duration × 30)

If Score < 30: Phase 1 (Ignition) - Scout
If 30 ≤ Score < 60: Phase 2 (Acceleration) - Enter
If 60 ≤ Score < 80: Phase 3 (Peak) - Scale Out
If Score ≥ 80: Phase 4 (Exhaustion) - Exit
```

**Expected Cycle Duration:** 3-7 days for typical hype trades (varies by market)

---

## 7. EDGE PRESERVATION

### 7.1 Avoid Getting Front-Run

**Problem:** If your strategy is predictable, others can trade ahead of you.

**Solutions:**
1. **Randomize timing:** Don't always enter at exact same price/time
2. **Split orders:** Enter 40-30-30 over 2-4 hours instead of 100% immediately
3. **Vary thresholds:** Use ranges (RVR 2.5-3.5) not exact triggers (RVR 3.0)
4. **Multiple signals:** Harder to predict multi-dimensional entry logic

### 7.2 Order Execution Best Practices

**Limit Orders vs Market Orders:**
- **Use limit orders** 90% of the time (control execution price)
- **Use market orders** only when:
  - Momentum is accelerating fast (FOMO justified)
  - Liquidity is very high (low slippage)
  - Position is small (< 1% of bankroll)

**Order Sizing:**
- Never place order > 5% of visible liquidity
- If position requires more, split into 3-5 smaller orders
- Wait 10-30 minutes between orders (avoid showing hand)

### 7.3 Information Edge vs Speed Edge

**You don't have speed edge** (probably) - HFT firms win that game

**You CAN have:**
- **Pattern recognition edge:** Spotting hype cycles others miss
- **Discipline edge:** Not FOMOing at peaks, sticking to stops
- **Psychological edge:** Fading when retail is panicking

**Play to your strengths:** Be the patient, systematic trader while others are emotional.

### 7.4 Avoid Adverse Selection

**Problem:** Market makers adjust prices when they detect informed trading.

**How to minimize:**
- Don't trade illiquid markets (< $10k)
- Don't place huge orders (< 10% of book)
- Don't trade immediately after major news (wait 30-60 min for price discovery)
- Don't trade in same patterns (vary position sizes, timings)

### 7.5 Strategy Drift Prevention

**Your edge decays over time as others copy it.**

**Maintain edge through:**
1. **Regular strategy reviews:** Monthly performance analysis
2. **Signal evolution:** Add new indicators as old ones fail
3. **Market rotation:** Move to new categories as old ones get efficient
4. **Continuous learning:** Study losing trades, adapt

**Warning signs your edge is gone:**
- Win rate drops below 45% for 20+ trades
- Average profit per trade < 1.5% (after costs)
- Sharpe ratio < 0.5 over 3 months

**Response:** STOP trading, re-evaluate, don't stubbornly continue losing strategy.

---

## 8. BACKTESTING PLAN

### 8.1 Data Requirements

**Minimum Data for Valid Backtest:**
- **100+ markets** (preferably 200+)
- **6+ months** of historical data (covers multiple market regimes)
- **Tick-level or hourly data** (daily candles insufficient for hype cycles)
- **Volume and liquidity data** (not just prices)

**Data Sources:**
- Polymarket API (historical orderbook snapshots)
- Manifold API (easier access, more markets)
- Kalshi (if available)
- Manual collection if needed

### 8.2 Backtesting Methodology

**Walk-Forward Testing (Critical):**
```
1. Train on Jan-Mar data → Test on Apr
2. Train on Jan-Apr data → Test on May
3. Train on Jan-May data → Test on Jun
... continue forward
```

**Why:** Avoids look-ahead bias and overfitting to historical data.

**DON'T:** Train on all historical data and test on same data (guaranteed overfitting).

### 8.3 Realistic Assumptions

**Transaction Costs:**
- **Platform fees:** 2-5% on profits (Polymarket ~2%, Manifold 0%)
- **Slippage:** 0.5% on entry, 1.5% on exit (assume worse execution)
- **Bid-ask spread:** 1-3% (half spread on each trade)

**Total friction:** ~3-5% round-trip cost

**Position Constraints:**
- Can't exceed 10% of market liquidity
- Can't exit large positions instantly (model multi-hour exits)
- Liquidity varies over time (markets dry up overnight)

### 8.4 Metrics to Track

**Primary Metrics:**
- **Sharpe Ratio:** Risk-adjusted returns (target > 1.0)
- **Max Drawdown:** Worst peak-to-trough loss (target < 25%)
- **Win Rate:** % of profitable trades (target > 50%)
- **Profit Factor:** Total wins / Total losses (target > 1.5)

**Secondary Metrics:**
- **Average Win:** Size of winning trades
- **Average Loss:** Size of losing trades
- **Expectancy:** (Win% × Avg Win) - (Loss% × Avg Loss) [must be positive]
- **Recovery Time:** Days to recover from max drawdown

**Sample Size:**
- Need minimum 30 trades for statistical relevance
- Prefer 100+ trades for confidence

### 8.5 Overfitting Prevention

**Common Overfitting Traps:**
1. **Too many parameters:** More knobs = more curve fitting
2. **Optimizing to exact thresholds:** "RVR must be exactly 3.14159"
3. **Cherry-picking time periods:** Only testing on bull markets
4. **Look-ahead bias:** Using future data in signals

**Prevention Strategies:**
1. **Simple rules:** Fewer parameters is better (start with 3-5 key variables)
2. **Threshold ranges:** "RVR between 2.5-3.5" vs exact value
3. **Multiple time periods:** Test across bull, bear, sideways markets
4. **Out-of-sample testing:** Hold back 20% of data, never train on it

**Final Validation:**
- If backtest Sharpe > 2.0: **Probably overfit** (too good to be true)
- If backtest Sharpe 1.0-1.5: **Reasonable** (expect live < backtest)
- If backtest Sharpe < 0.5: **Strategy doesn't work** (don't trade it)

### 8.6 Regime Analysis

**Test strategy across different market conditions:**

**Market Regimes:**
- **High volatility** (crypto boom/bust)
- **Low volatility** (quiet periods)
- **High liquidity** (popular markets)
- **Low liquidity** (niche markets)

**Expected Results:**
- Strategy should work in at least 2-3 regimes
- If only works in one regime → too fragile
- Adjust position sizing based on regime detection

### 8.7 Metrics to Optimize (In Order)

**DO NOT optimize for maximum return** - that's overfitting.

**Instead, optimize for:**
1. **Risk-adjusted return** (Sharpe ratio)
2. **Downside protection** (minimum drawdown)
3. **Consistency** (positive returns in 60%+ of months)
4. **Robustness** (works across market types)

**Target Profile:**
- Sharpe: 1.0-1.5
- Max DD: < 20%
- Win rate: 50-60%
- Profit factor: 1.5-2.0
- Monthly positive: 65%+

**If you hit these, you have a tradeable strategy.**

---

## 9. IMPLEMENTATION CHECKLIST

### Phase 1: Pre-Launch (Weeks 1-2)
- [ ] Collect historical data (100+ markets)
- [ ] Build signal calculation infrastructure
- [ ] Code backtesting framework
- [ ] Run walk-forward tests
- [ ] Document results and edge cases

### Phase 2: Paper Trading (Weeks 3-4)
- [ ] Deploy to live markets (no real money)
- [ ] Track theoretical trades in spreadsheet
- [ ] Monitor signal accuracy
- [ ] Measure actual vs expected slippage
- [ ] Identify operational issues

### Phase 3: Micro Capital (Weeks 5-8)
- [ ] Start with $500-1000 real money
- [ ] Trade at 10% of planned position sizes
- [ ] Focus on execution quality over profits
- [ ] Build confidence in system
- [ ] Validate assumptions from backtest

### Phase 4: Scale-Up (Weeks 9-12)
- [ ] Gradually increase position sizes to full allocation
- [ ] Add more markets to watchlist
- [ ] Refine entry/exit timing
- [ ] Optimize execution (limit orders, splits)
- [ ] Document lessons learned

### Phase 5: Production (Week 13+)
- [ ] Full capital deployment
- [ ] Weekly performance reviews
- [ ] Monthly strategy audits
- [ ] Continuous improvement cycle
- [ ] Edge preservation monitoring

---

## 10. PSYCHOLOGICAL DISCIPLINE

### 10.1 Common Traps to Avoid

**FOMO (Fear of Missing Out):**
- Symptom: Entering without signals because market is pumping
- Antidote: "No signal, no trade" rule (write it on sticky note)

**Revenge Trading:**
- Symptom: Doubling position size after loss to "make it back"
- Antidote: Daily loss limit (stop when hit, no exceptions)

**Anchoring:**
- Symptom: "I'll exit when it gets back to my entry price" (after it's dropped)
- Antidote: Stop losses are not suggestions (honor them)

**Confirmation Bias:**
- Symptom: Ignoring negative signals once in a position
- Antidote: Set exit alerts, monitor opposing indicators

**Overconfidence:**
- Symptom: "I'm on a hot streak, time to increase size"
- Antidote: Position sizing is systematic, not emotional

### 10.2 Trading Journal Template

**For EVERY trade, document:**
1. Date/Time
2. Market name
3. Entry price and size
4. Signals present (RVR, ROC, Imbalance)
5. Confidence level (High/Med/Low)
6. Exit price and P&L
7. What went right
8. What went wrong
9. Lessons learned

**Review weekly:** Identify patterns in winners and losers.

### 10.3 Mental Model: You Are a Casino

**The casino always:**
- Has an edge (even if small)
- Plays consistently (no emotion)
- Manages risk (position limits)
- Thinks long-term (variance evens out)
- Stays disciplined (house rules don't change)

**You are the casino. The market is the gambler.**

Your job: Grind out small edges repeatedly with discipline. Not to hit home runs.

---

## 11. RISK DISCLAIMER & REALITY CHECK

### This Strategy Will:
✅ Provide a systematic framework for hype trading  
✅ Reduce emotional decision-making  
✅ Manage risk better than ad-hoc trading  
✅ Give you a statistical edge (if backtested properly)  

### This Strategy Will NOT:
❌ Guarantee profits (nothing does)  
❌ Work 100% of the time (expect 50-60% win rate)  
❌ Make you rich overnight (target 15-30% annual return)  
❌ Eliminate losses (drawdowns will happen)  

### Expected Performance (Realistic)
- **Annual Return:** 15-35% (if edge exists)
- **Max Drawdown:** 15-25% (even with good risk management)
- **Win Rate:** 50-60% (not 80%+)
- **Months to profitability:** 3-6 (not instant)

### When to Abandon Strategy
- Consistent losses for 3+ months
- Edge deteriorates (metrics below targets)
- Fundamental market structure changes
- You can't maintain discipline (emotional trading)

**Bottom Line:** This is professional speculation, not gambling. But speculation still loses sometimes. Only trade with capital you can afford to lose.

---

## 12. NEXT STEPS

1. **Collect Data:** Scrape historical Polymarket/Manifold data
2. **Build Backtest:** Code signal logic and walk-forward testing
3. **Validate Edge:** Achieve Sharpe > 1.0 in out-of-sample data
4. **Paper Trade:** 2-4 weeks theoretical trading
5. **Go Live Micro:** $500-1000 real capital
6. **Scale Gradually:** Double capital every month if profitable
7. **Iterate:** Refine based on live trading lessons

---

## Appendix A: Quick Reference Cheat Sheet

### Entry Checklist
- [ ] RVR > 2.0?
- [ ] |ROC| > 10%?
- [ ] Liquidity imbalance?
- [ ] Minimum 3 signals?
- [ ] No disqualifying conditions?
- [ ] Position size calculated?
- [ ] Total exposure < 25%?

### Exit Checklist
- [ ] Stop loss set at -12%?
- [ ] TP1 alert at +8%?
- [ ] TP2 alert at +15%?
- [ ] Time-decay check scheduled?
- [ ] Momentum reversal monitor active?

### Risk Checklist
- [ ] Position < 5% bankroll?
- [ ] Category exposure < 10%?
- [ ] Total exposure < 25%?
- [ ] Daily loss limit not hit?
- [ ] Correlation check passed?

### Daily Routine
1. Check for signals on watchlist (30 min)
2. Review open positions (15 min)
3. Update trading journal (10 min)
4. Scan for new markets (20 min)
5. Review news/catalysts (15 min)

**Total time:** ~90 minutes/day

---

## Appendix B: Glossary

**RVR (Relative Volume Ratio):** Current volume vs historical average  
**ROC (Rate of Change):** Price momentum percentage  
**Kelly Criterion:** Optimal bet sizing formula based on edge  
**Sharpe Ratio:** Risk-adjusted return metric (return/volatility)  
**Max Drawdown:** Largest peak-to-trough loss  
**Profit Factor:** Total wins divided by total losses  
**Walk-Forward Testing:** Backtesting method that avoids look-ahead bias  
**Slippage:** Difference between expected and actual execution price  

---

## Document Version Control

**v1.0 (2026-02-06):** Initial framework design  
**Next Update:** After backtest completion (add empirical thresholds)  
**Future Versions:** Iterate based on live trading results  

---

**Remember:** Discipline > Discretion. Trust the process, track the results, iterate continuously.

🎯 **Now go backtest this and prove (or disprove) the edge exists.**
