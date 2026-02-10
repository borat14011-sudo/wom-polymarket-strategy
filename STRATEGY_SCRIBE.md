# 📜 POLYMARKET STRATEGY SCRIBE
## Canonical Documentation for All Trading Strategies

**Version:** 1.0  
**Last Updated:** February 8, 2026  
**Scribe:** Strategy Scribe System  
**Purpose:** Single source of truth for all Polymarket trading strategies with full supporting data

---

# 📋 STRATEGY DOCUMENTATION TEMPLATE

## Standard Strategy Writeup Format

Each strategy in the Strategy Scribe follows this standardized template:

---

## Strategy Header

```markdown
# [STRATEGY_NAME]
## [Classification]: [Sub-category]

**Status:** [DEPLOYED | PAPER_TRADING | VALIDATED | TESTING | DORMANT]  
**Confidence Rating:** [A+ | A | A- | B+ | B | B- | C+ | C | C- | D | F]  
**Last Updated:** [YYYY-MM-DD]  
**Primary Source:** [Backtest/Paper Trade/Meta-Analysis]
```

---

## 1. STRATEGY OVERVIEW

### 1.1 Core Hypothesis
*Clear, concise statement of the edge being exploited*

**Example:** 
> Markets systematically overprice unlikely events due to retail panic and base rate neglect. Betting NO on low-probability events (<15%) captures mean reversion + time decay + reality check convergence.

### 1.2 Edge Explanation
*Detailed explanation of WHY the edge exists*

**Components:**
- **Behavioral Bias:** [e.g., Availability heuristic, recency bias]
- **Market Structure:** [e.g., Fragmented liquidity, MM limitations]
- **Information Asymmetry:** [e.g., Slow propagation across related markets]
- **Time Decay Pattern:** [e.g., Convexity compression near resolution]

### 1.3 Classification

| Attribute | Value |
|-----------|-------|
| **Primary Category** | [POLITICAL / CRYPTO / SPORTS / MACRO / SOCIAL / ARBITRAGE] |
| **Strategy Type** | [FADE / MOMENTUM / MEAN_REVERSION / ARBITRAGE / COPY_TRADING] |
| **Time Horizon** | [INTRADAY / SWING / POSITION / EVENT_DRIVEN] |
| **Signal Source** | [TECHNICAL / FUNDAMENTAL / SENTIMENT / ONCHAIN / HYBRID] |
| **Automation Level** | [FULLY_AUTOMATED / SEMI_AUTOMATED / MANUAL] |

---

## 2. HISTORICAL PERFORMANCE DATA

### 2.1 Key Metrics Summary

| Metric | Value | Grade |
|--------|-------|-------|
| **Win Rate** | XX.X% | [A-F] |
| **Average Return** | +X.X% | [A-F] |
| **Sharpe Ratio** | X.XX | [A-F] |
| **Max Drawdown** | -XX.X% | [A-F] |
| **Profit Factor** | X.XX | [A-F] |
| **Sample Size** | XXX trades | [A-F] |
| **Statistical Significance** | p < 0.XXX | [A-F] |

### 2.2 Fee-Adjusted Returns

**Polymarket Fee Structure:**
- Trading Fee: ~2% per side (4% round-trip)
- Slippage: ~0.5-1% (estimated)
- **Total Cost per Trade:** ~4.5-5.5%

| Metric | Gross | After Fees | Edge Retained |
|--------|-------|------------|---------------|
| Average Win | +X.X% | +X.X% | XX% |
| Average Loss | -X.X% | -X.X% | XX% |
| Expected Value | +X.X% | +X.X% | XX% |
| Break-even Win Rate | XX.X% | XX.X% | - |

### 2.3 Performance by Market Condition

| Market Regime | Win Rate | Avg Return | Sample |
|---------------|----------|------------|--------|
| High Volatility (VIX >30) | XX.X% | +X.X% | XX |
| Normal Volatility (VIX 15-30) | XX.X% | +X.X% | XXX |
| Low Volatility (VIX <15) | XX.X% | +X.X% | XX |
| Election Periods | XX.X% | +X.X% | XX |
| Non-Election Periods | XX.X% | +X.X% | XXX |

### 2.4 Monthly Performance History

| Month | Trades | Win Rate | Return | Drawdown |
|-------|--------|----------|--------|----------|
| Oct 2025 | XX | XX% | +X.X% | -X% |
| Nov 2025 | XX | XX% | +X.X% | -X% |
| Dec 2025 | XX | XX% | +X.X% | -X% |
| Jan 2026 | XX | XX% | +X.X% | -X% |
| Feb 2026 | XX | XX% | +X.X% | -X% |

---

## 3. MARKET SELECTION CRITERIA

### 3.1 Liquidity Requirements

| Parameter | Minimum | Preferred | Notes |
|-----------|---------|-----------|-------|
| **Daily Volume** | $10,000 | $50,000+ | Ensures exit liquidity |
| **Market Cap** | $25,000 | $100,000+ | Reduces manipulation risk |
| **Order Book Depth** | 5 levels | 10+ levels | Minimizes slippage |
| **Bid-Ask Spread** | <5% | <2% | Preserves edge |

### 3.2 Volume Thresholds

| Volume Tier | Minimum | Typical Win Rate | Notes |
|-------------|---------|------------------|-------|
| **Micro** | $1K-$10K | XX% | High variance, thin |
| **Small** | $10K-$100K | XX% | Good for small positions |
| **Medium** | $100K-$1M | XX% | Optimal for most strategies |
| **Large** | $1M-$10M | XX% | Best liquidity, hardest edge |
| **Mega** | $10M+ | XX% | Institutional competition |

### 3.3 Time to Resolution

| Time Window | Win Rate | Expectancy | Position Size | Verdict |
|-------------|----------|------------|---------------|---------|
| **<3 days** | XX.X% | +$X.XX | 100% | ✅ **FOCUS** |
| 3-7 days | XX.X% | +$X.XX | 50% | ⚠️ Selective |
| 7-30 days | XX.X% | $X.XX | 25% | ⚠️ Rare |
| >30 days | XX.X% | -$X.XX | 0% | ❌ NEVER |

### 3.4 Category Preferences

| Category | Strategy Fit | Win Rate | Notes |
|----------|--------------|----------|-------|
| **Politics** | XX% | XX.X% | [Notes] |
| **Crypto** | XX% | XX.X% | [Notes] |
| **Sports** | XX% | XX.X% | [Notes] |
| **Macro/Econ** | XX% | XX.X% | [Notes] |
| **Tech/AI** | XX% | XX.X% | [Notes] |
| **Entertainment** | XX% | XX.X% | [Notes] |
| **Geopolitical** | XX% | XX.X% | [Notes] |

---

## 4. ENTRY & EXIT RULES

### 4.1 Entry Criteria

**ALL of the following must be TRUE:**

| # | Filter | Condition | Weight |
|---|--------|-----------|--------|
| 1 | [Filter Name] | [Condition] | XX% |
| 2 | [Filter Name] | [Condition] | XX% |
| 3 | [Filter Name] | [Condition] | XX% |

**Entry Signal Strength:**
- **STRONG:** X+ filters pass → Full position
- **MODERATE:** X filters pass → Half position
- **WEAK:** X filters pass → Quarter position or skip

### 4.2 Entry Price Zones

| Zone | Price Range | Action | RVR |
|------|-------------|--------|-----|
| **Optimal** | $0.XX - $0.XX | Full size | X.Xx |
| **Acceptable** | $0.XX - $0.XX | Reduced size | X.Xx |
| **Avoid** | $0.XX - $0.XX | Skip | X.Xx |

### 4.3 Exit Rules

**Profit Targets:**

| Target | Price Level | Action | % of Position |
|--------|-------------|--------|---------------|
| TP1 | +XX% | Exit | 33% |
| TP2 | +XX% | Exit | 33% |
| TP3 | +XX% | Exit | 34% |

**Stop Loss:**
- **Hard Stop:** -XX% (never override)
- **Time Stop:** Exit if [condition]
- **Trailing Stop:** [If applicable]

**Time-Based Exits:**
- Exit if X% of time to resolution elapsed
- Exit before major events (debates, reports)
- Exit if better opportunity found

---

## 5. POSITION SIZING METHODOLOGY

### 5.1 Base Sizing Formula

```
Position Size = min(
    Kelly_Suggested × Fractional_Kelly,
    Max_Position_Percent × Bankroll,
    Max_Dollar_Amount,
    Market_Liquidity_Limit
)
```

### 5.2 Kelly Criterion Calculation

```
Kelly % = Win_Rate - ((1 - Win_Rate) / Average_RVR)

Example:
- Win Rate: 70%
- Average RVR: 2.5x
- Kelly % = 0.70 - (0.30 / 2.5) = 0.70 - 0.12 = 58%

Fractional Kelly: 58% × 0.10 = 5.8% per trade
```

### 5.3 Position Size Tiers

| Conviction Level | Kelly % | Position Size | Max Trades |
|------------------|---------|---------------|------------|
| **MAXIMUM** | >50% | 10% of bankroll | 2 |
| **HIGH** | 40-50% | 7.5% of bankroll | 3 |
| **MODERATE** | 30-40% | 5% of bankroll | 5 |
| **LOW** | 20-30% | 2.5% of bankroll | 8 |
| **MINIMAL** | <20% | 1% of bankroll | 10 |

### 5.4 Liquidity-Based Limits

| Market Volume | Max Position | % of Market |
|---------------|--------------|-------------|
| <$10K | $100 | 1% |
| $10K-$50K | $500 | 1% |
| $50K-$100K | $1,000 | 1% |
| $100K-$500K | $2,500 | 0.5% |
| $500K-$1M | $5,000 | 0.5% |
| $1M+ | $10,000 | 0.25% |

---

## 6. RISK MANAGEMENT RULES

### 6.1 Position-Level Limits

| Limit Type | Threshold | Action |
|------------|-----------|--------|
| **Hard Stop** | -XX% | Auto exit |
| **Soft Stop** | -XX% | Manual review |
| **Time Decay** | X days | Reduce size |
| **Correlation** | >0.7 | Skip trade |

### 6.2 Portfolio-Level Limits

| Limit Type | Threshold | Action |
|------------|-----------|--------|
| **Max Positions** | 10 | No new trades |
| **Max Exposure** | 50% | Reduce sizes |
| **Daily Loss** | -5% | Pause trading |
| **Weekly Loss** | -10% | Reduce sizes |
| **Monthly Loss** | -15% | Full stop |
| **Max Drawdown** | -20% | Halt all trading |

### 6.3 Circuit Breakers

```python
# Pseudo-code for circuit breakers
if daily_pnl < -0.05 * total_capital:
    halt_trading('DAILY_LOSS_LIMIT')
    
if drawdown > 0.20:
    halt_trading('MAX_DRAWDOWN')
    
if len(positions) > 10:
    halt_new_entries('MAX_POSITIONS')
    
if max_correlation(positions) > 0.8:
    halt_trading('HIGH_CORRELATION')
```

### 6.4 Black Swan Contingencies

| Scenario | Response |
|----------|----------|
| Market gaps past stop | Accept loss, don't chase |
| Platform outage | Have backup brokers |
| Regulatory news | Exit all positions |
| Liquidity crisis | Reduce sizes by 50% |
| Whale manipulation | Skip affected markets |

---

## 7. BACKTEST RESULTS

### 7.1 Test Parameters

| Parameter | Value |
|-----------|-------|
| **Period** | [Start Date] - [End Date] |
| **Markets** | XXX resolved markets |
| **Fee Model** | 4% trading + 1% slippage |
| **Position Size** | Fixed $XXX per trade |
| **Starting Capital** | $XXX |

### 7.2 Key Performance Metrics

| Metric | Value | Benchmark | Assessment |
|--------|-------|-----------|------------|
| **Total Return** | +XXX% | S&P 500: +XX% | [Excellent/Good/Poor] |
| **Annualized Return** | +XXX% | - | [Excellent/Good/Poor] |
| **Sharpe Ratio** | X.XX | 1.0+ | [Excellent/Good/Poor] |
| **Sortino Ratio** | X.XX | 1.5+ | [Excellent/Good/Poor] |
| **Max Drawdown** | -XX% | <20% | [Excellent/Good/Poor] |
| **Win Rate** | XX.X% | >55% | [Excellent/Good/Poor] |
| **Profit Factor** | X.XX | >1.5 | [Excellent/Good/Poor] |
| **Calmar Ratio** | X.XX | >1.0 | [Excellent/Good/Poor] |

### 7.3 Trade Distribution

| Outcome Range | Count | % of Total | Cumulative % |
|---------------|-------|------------|--------------|
| >+50% | XX | X% | X% |
| +30% to +50% | XX | X% | X% |
| +10% to +30% | XX | X% | X% |
| 0% to +10% | XX | X% | X% |
| 0% to -10% | XX | X% | X% |
| -10% to -30% | XX | X% | X% |
| <-30% | XX | X% | X% |

### 7.4 Walk-Forward Analysis

| Period | In-Sample | Out-of-Sample | Degradation |
|--------|-----------|---------------|-------------|
| Q1-Q2 2024 | XX.X% | XX.X% | -X.X% |
| Q3-Q4 2024 | XX.X% | XX.X% | -X.X% |
| Q1 2025 | XX.X% | XX.X% | -X.X% |

---

## 8. LIVE/PAPER TRADING RESULTS

### 8.1 Paper Trading Track Record

| Date Range | Trades | Win Rate | Net P&L | vs Backtest |
|------------|--------|----------|---------|-------------|
| [Period 1] | XX | XX% | $XXX | [+/- X%] |
| [Period 2] | XX | XX% | $XXX | [+/- X%] |
| **Total** | **XX** | **XX%** | **$XXX** | **[+/- X%]** |

### 8.2 Live Trading Track Record

| Date Range | Trades | Win Rate | Net P&L | vs Paper |
|------------|--------|----------|---------|----------|
| [Period 1] | XX | XX% | $XXX | [+/- X%] |
| **Total** | **XX** | **XX%** | **$XXX** | **[+/- X%]** |

### 8.3 Execution Quality

| Metric | Target | Actual | Grade |
|--------|--------|--------|-------|
| **Slippage** | <1% | X.X% | [A-F] |
| **Fill Rate** | >95% | XX% | [A-F] |
| **Latency** | <5s | X.Xs | [A-F] |
| **Error Rate** | <1% | X.X% | [A-F] |

---

## 9. CONFIDENCE RATING JUSTIFICATION

### 9.1 Grade Components

| Factor | Weight | Score | Weighted |
|--------|--------|-------|----------|
| **Win Rate** | 20% | X/10 | X.X |
| **Sample Size** | 20% | X/10 | X.X |
| **Sharpe Ratio** | 15% | X/10 | X.X |
| **Max Drawdown** | 15% | X/10 | X.X |
| **Fee-Adjusted Returns** | 15% | X/10 | X.X |
| **Live Validation** | 10% | X/10 | X.X |
| **Robustness** | 5% | X/10 | X.X |
| **TOTAL** | 100% | - | **X.X** |

### 9.2 Grade Scale

| Grade | Score Range | Interpretation |
|-------|-------------|----------------|
| **A+** | 9.5-10.0 | Exceptional edge, deploy immediately |
| **A** | 9.0-9.4 | Strong edge, deploy with standard risk mgmt |
| **A-** | 8.5-8.9 | Good edge, minor concerns |
| **B+** | 8.0-8.4 | Viable edge, watch closely |
| **B** | 7.5-7.9 | Marginal edge, validate further |
| **B-** | 7.0-7.4 | Weak edge, high risk |
| **C+** | 6.5-6.9 | Unproven, needs more data |
| **C** | 6.0-6.4 | Likely no edge, not recommended |
| **C-** | 5.5-5.9 | Poor results, do not trade |
| **D** | 5.0-5.4 | Failed validation |
| **F** | <5.0 | Dangerous, avoid completely |

### 9.3 Trend Indicator

| Indicator | Meaning |
|-----------|---------|
| 📈 Improving | Win rate increasing over last 3 months |
| ➡️ Stable | Performance consistent with backtest |
| 📉 Declining | Win rate decreasing, monitor closely |
| ⚠️ At Risk | Approaching failure threshold |

---

## 10. IMPLEMENTATION GUIDE

### 10.1 Required Infrastructure

| Component | Specification | Cost | Priority |
|-----------|--------------|------|----------|
| **Polymarket API** | CLOB + Gamma API | Free | Critical |
| **Data Feed** | Real-time WebSocket | $0-500/mo | Critical |
| **Execution** | Sub-5 second latency | Varies | High |
| **Database** | Price history storage | $50/mo | Medium |
| **Monitoring** | P&L tracking dashboard | $0-100/mo | Medium |

### 10.2 Automation Requirements

| Task | Automation Level | Tool |
|------|-----------------|------|
| **Signal Detection** | Full | Custom script |
| **Entry Execution** | Full | API integration |
| **Exit Management** | Full | Stop/limit orders |
| **Risk Monitoring** | Full | Circuit breakers |
| **Reporting** | Semi | Daily/weekly scripts |

### 10.3 Implementation Checklist

**Phase 1: Setup (Week 1)**
- [ ] API access configured
- [ ] Data pipeline operational
- [ ] Paper trading environment ready
- [ ] Risk framework in place

**Phase 2: Validation (Weeks 2-5)**
- [ ] 30 days paper trading
- [ ] Win rate validation
- [ ] Execution quality verified
- [ ] Drawdown within limits

**Phase 3: Deployment (Week 6+)**
- [ ] Live trading with 10% capital
- [ ] Scale up if profitable
- [ ] Monthly performance reviews
- [ ] Continuous monitoring

---

## 11. KNOWN LIMITATIONS & RISKS

### 11.1 Data Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **No historical prices** | Entry timing uncertain | Use mid-price assumption |
| **Survivorship bias** | Failed markets excluded | Acknowledge in analysis |
| **Look-ahead bias** | Future knowledge in signals | Strict train/test split |
| **Sample size** | Limited statistical power | Use Bayesian analysis |

### 11.2 Execution Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Slippage** | High | Medium | Limit orders, size constraints |
| **Liquidity gaps** | Medium | High | Volume minimums |
| **Platform downtime** | Low | High | Multiple exchanges |
| **API errors** | Medium | Medium | Error handling, retries |

### 11.3 Market Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Edge decay** | High | High | Monitor monthly, adapt |
| **Black swan events** | Low | Very High | Position sizing, stops |
| **Regulatory changes** | Medium | Very High | Stay informed, diversify |
| **Competition** | High | Medium | Faster execution, unique signals |

---

## 12. RELATED STRATEGIES

### 12.1 Synergistic Strategies

| Strategy | Synergy Type | Correlation | Notes |
|----------|--------------|-------------|-------|
| [Strategy A] | Complementary | Low | [Notes] |
| [Strategy B] | Hedge | Negative | [Notes] |

### 12.2 Mutually Exclusive Strategies

| Strategy | Reason | Notes |
|----------|--------|-------|
| [Strategy C] | Same signal source | Avoid double counting |
| [Strategy D] | Opposite thesis | Contradictory positions |

### 12.3 Strategy Evolution

| Version | Date | Changes | Performance Impact |
|---------|------|---------|-------------------|
| v1.0 | [Date] | Initial strategy | Baseline |
| v1.1 | [Date] | Added filter X | +X% win rate |
| v2.0 | [Date] | Combined with Y | +X% Sharpe |

---

## 13. APPENDICES

### Appendix A: Mathematical Formulations

[Detailed formulas for signals, sizing, etc.]

### Appendix B: Code Implementation

```python
# Example signal calculation
def calculate_signal(market_data):
    # Implementation here
    pass
```

### Appendix C: Raw Data Access

- Backtest data: `data/strategy_[name]_backtest.csv`
- Trade log: `data/strategy_[name]_trades.csv`
- Performance: `data/strategy_[name]_performance.json`

### Appendix D: Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| [Date] | 1.0 | Initial documentation | [Name] |
| [Date] | 1.1 | Added live results | [Name] |

---

## 14. REFERENCES & FURTHER READING

### Primary Sources
1. [Original backtest report]
2. [Paper trading results]
3. [Live trading track record]

### Related Research
1. [Academic paper on prediction markets]
2. [Behavioral finance study]
3. [Market microstructure analysis]

### Tools & Resources
1. [Backtest engine repository]
2. [Live trading implementation]
3. [Monitoring dashboard]

---

**END OF TEMPLATE**

---

*This template should be used as the foundation for documenting all strategies in the Strategy Scribe system. Each strategy writeup should be comprehensive, data-driven, and include both historical and live performance metrics where available.*
