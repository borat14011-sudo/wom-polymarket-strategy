# KAIZEN TRADING SYSTEM v2.0
## Continuous Improvement Framework
**Created:** 2026-02-12 | **Status:** ACTIVE

---

## 🎯 SYSTEM OVERVIEW

This is a **forward-testing focused** trading system. After rigorous 5-agent validation, we discovered:

1. **Most backtests are unreliable** - built on non-existent historical data
2. **Only BTC_TIME_BIAS** has decent confidence (8/10)
3. **Position sizes must be 0.5%** until validated with 30+ forward trades
4. **Data freshness is critical** - stale data = bad decisions

---

## 📊 ACTIVE CRON JOBS

| Job | Frequency | Purpose |
|-----|-----------|---------|
| Market Data Auto-Fetch | 15 min | Keep active-markets.json fresh |
| Kaizen Forward Test Monitor | 1 hour | Track paper trade results |
| Daily Strategy Review | 9 AM PST | R1 deep analysis |
| Weekly System Audit | Monday 10 AM | Full system review |

---

## 🧪 FORWARD TESTING PROTOCOL

### Position Sizing
- **Capital:** $100 paper
- **Per Trade:** 0.5% ($0.50)
- **Max Positions:** 10 concurrent
- **Goal:** 30 trades before scaling

### Tracking
- File: `forward_test_results.json`
- Script: `forward_test_tracker.py`

### Commands
```bash
# Show status
python forward_test_tracker.py status

# Add paper trade
python forward_test_tracker.py add <strategy> <market> <side> <price>

# Close trade
python forward_test_tracker.py close <trade_id> <exit_price> <WIN/LOSS>
```

---

## 📈 VALIDATED STRATEGIES

### ✅ BTC_TIME_BIAS (8/10 Confidence)
- Win Rate: 58.8% (claimed, needs forward validation)
- Edge: ~2-3% per trade after costs
- Status: PAPER TESTING

### ⚠️ WEATHER_FADE_LONGSHOTS (6/10 Confidence)
- Win Rate: 85.1% (9.4% degradation from claims)
- Status: PAPER TESTING with caution

### ❌ INVALIDATED
- MUSK_HYPE_FADE (1/10)
- WILL_PREDICTION_FADE (2/10)
- Whale Copy (3/10)

---

## 🔴 RISK RULES (Updated per Risk Analyst)

| Rule | Old | New |
|------|-----|-----|
| Max per trade | 2% | **0.5%** |
| Total exposure | 25% | 25% (keep) |
| Stop-loss | 12% | **N/A** (binary markets) |
| Circuit breaker | 15% | **Tiered: 10%/15%/20%** |

---

## 📁 KEY FILES

| File | Purpose |
|------|---------|
| `active-markets.json` | Fresh market data (auto-updated) |
| `forward_test_results.json` | Paper trade tracker |
| `strategy_validation_opus1.md` | Strategy validation report |
| `risk_analysis_opus2.md` | Risk analysis report |
| `current_opportunities_scan.md` | Latest opportunities |

---

## 🚀 NEXT STEPS

1. **Continue paper trading** - track 30+ trades
2. **Monitor forward test results** - hourly via cron
3. **Validate edge is real** - compare claimed vs actual win rate
4. **Scale up only if proven** - move to 1%, then 2%

---

## 📝 DECISION LOG

| Date | Decision | Reason |
|------|----------|--------|
| 2026-02-12 | Reduced position size to 0.5% | Risk Analyst recommendation |
| 2026-02-12 | Disabled noisy cron jobs | System consolidation |
| 2026-02-12 | Created forward test tracker | Need real validation |
| 2026-02-12 | Invalidated most strategies | Backtest data unreliable |

---

*Kaizen = Continuous Improvement. Every day, get a little better.* 🇰🇿
