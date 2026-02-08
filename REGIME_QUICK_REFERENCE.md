# 🎯 MARKET REGIME - QUICK REFERENCE CARD

## Current Regime (Feb 2026)
```
🐂 Bull Crypto | 📊 Low-Med Vol | 🗓️ Off-Year | 📈 Growing Volume
```

## Deploy Now
| Strategy | Allocation | Why |
|----------|-----------|-----|
| **Expert Fade** | 35% | 0.5% regime dependency - most consistent |
| **News Reversion** | 40% | 7.9% dependency - excels in volatility |
| **Trend Filter** | 25% | 0.2% dependency - solid baseline |

**Expected Combined:** 20-30% avg return | 56-58% win rate | Sharpe ~0.20

## DO NOT Deploy
- ❌ Whale Tracking (-9.1% avg return, -38% max DD)
- ❌ Time Horizon <3d (-6.2% avg return, -53% max DD)  
- ❌ Pairs Trading (-38.6% avg return, too few opportunities)

---

## Regime Change Triggers

### 🔥 HIGH VOLATILITY DETECTED
**Triggers:** BTC swings >5% daily for 3+ days | VIX >30 | Major crisis

**Actions:**
- ⬆️ News Reversion → 50% (best in chaos)
- ⬇️ Expert Fade → 25%
- ⬇️ Trend Filter → 15%
- 🛑 STOP Whale Tracking
- 💰 Reduce position sizes -40%

---

### 🐻 BEAR MARKET DETECTED
**Triggers:** BTC <-20% YTD | 3+ months downtrend | Volume collapse

**Actions:**
- ⚠️ CAUTION - limited bear market testing
- ⬇️ Reduce total exposure -40%
- 🔬 Monitor strategies closely
- 💰 Smaller positions, higher conviction only

---

### 🗳️ ELECTION YEAR MODE
**Triggers:** Major US election <6 months | Political volume surge

**Actions:**
- ✅ Maintain current allocations
- ⬆️ Increase total capital (more opportunities)
- 🎯 Focus on political markets
- 👁️ Watch for retail inefficiencies

---

## Position Sizing Rules

**Kelly Criterion:** (Edge × WR - (1 - WR)) / Edge

| Strategy | Edge | WR | Kelly % | Recommended % |
|----------|------|----|----|---------------|
| News Reversion | 0.429 | 55.9% | 16.2% | **10-12%** per trade |
| Expert Fade | 0.193 | 57.7% | 9.5% | **6-8%** per trade |
| Trend Filter | 0.172 | 58.6% | 10.1% | **5-7%** per trade |

**In High Volatility:** Reduce all by 50%

---

## Stop Loss & Exit Rules

| Scenario | Action |
|----------|--------|
| Position down -15% | Trailing stop triggered → EXIT |
| Drawdown hits -10% portfolio | STOP new trades, review |
| Regime shifts mid-trade | EXIT 50% of position |
| Strategy shows negative in regime | EXIT immediately |
| Win >30% | Lock in 50% profit, let rest run |

---

## Daily Checklist

- [ ] Check BTC price (regime indicator)
- [ ] Review crypto volatility (regime indicator)
- [ ] Count active trades by strategy
- [ ] Any positions in "wrong" regime? → EXIT
- [ ] Calculate unrealized P&L
- [ ] Update position tracking

---

## Performance Expectations by Regime

### Bull Crypto (CURRENT)
- Expert Fade: +11% avg | 44% WR ✅
- News Reversion: +14% avg | 42% WR ✅
- Trend Filter: -9% avg | 44% WR ⚠️ (needs investigation)

### High Volatility
- News Reversion: +50% avg | 44% WR ⭐⭐⭐
- Expert Fade: +13% avg | 45% WR ✅
- Whale Tracking: -32% avg | 46% WR 🚫 AVOID

### Low Volatility
- Expert Fade: +13% avg | 45% WR ✅
- News Reversion: +19% avg | 60% WR ✅
- Whale Tracking: +22% avg | 71% WR ⚠️ (only if confirmed low vol)

### Low Volume Markets
- NO-Side Bias: +66% avg | 53% WR ⭐ (conditional only)
- Expert Fade: +13% avg | 45% WR ✅
- News Reversion: +11% avg | 41% WR ✅

---

## Emergency Protocol

### 🚨 If Drawdown >20%
1. STOP all new trades immediately
2. Exit losing positions >10% down
3. Let winners run with 20% trailing stops
4. Review strategy allocation
5. Reduce position sizes by 60%
6. Only resume when confidence restored

### 🚨 If Market Manipulation Detected
1. Document evidence
2. Exit affected positions
3. Report to Polymarket
4. Avoid similar markets for 7 days
5. Increase vigilance on low-liquidity markets

### 🚨 If Strategy Underperforming
**Underperformance = -5% vs expected for 20+ consecutive trades**

1. Pause strategy immediately
2. Review recent trades for pattern
3. Check if regime classification correct
4. Backtest on recent data
5. Only resume if root cause found

---

## Regime Indicators (Track These)

### Crypto Market
- **Bull:** BTC >+20% YTD
- **Neutral:** BTC -20% to +20% YTD
- **Bear:** BTC <-20% YTD

### Volatility
- **High:** Daily BTC moves >3% for 5+ days | VIX >30
- **Medium:** Daily BTC moves 1-3% | VIX 15-30
- **Low:** Daily BTC moves <1% | VIX <15

### Volume
- **High:** >$500K daily Polymarket volume | Major events
- **Low:** <$100K daily | Niche markets

### Political Cycle
- **Election Year:** 2024, 2028 (US presidential)
- **Midterm:** 2026 (current) - moderate activity
- **Off-Year:** Other years - low political volume

---

## Strategy Regime Matrix (Quick Lookup)

| Regime | Best Strategy | Second Best | Avoid |
|--------|--------------|-------------|-------|
| Bull + Low Vol | Expert Fade | News Reversion | Pairs |
| Bull + High Vol | News Reversion | Expert Fade | Whale |
| Bear + Low Vol | ⚠️ Untested | ⚠️ Untested | All |
| Bear + High Vol | ⚠️ Untested | ⚠️ Untested | All |
| Election + High Vol | News Reversion | Expert Fade | Whale |
| Off-Year + Low Vol | Expert Fade | NO-Side Bias | Pairs |

---

## Pro Tips

💡 **News Reversion** crushes it when fear is high - look for >40% drops  
💡 **Expert Fade** is your bread-and-butter - deploy consistently  
💡 **Trend Filter** needs more testing - use conservatively  
💡 **Whale Tracking** is a trap in volatility - avoid or inverse it  
💡 **NO-Side Bias** works ONLY in low volume - don't force it  

---

## Contact / Updates

- Full Report: `MARKET_REGIME_REPORT.md`
- Raw Data: `MARKET_REGIME_REPORT.json`
- Backtest Results: `backtest-results/`
- Analysis Script: `regime-analysis.js`

**Last Updated:** February 7, 2026  
**Next Review:** March 1, 2026 (monthly)
