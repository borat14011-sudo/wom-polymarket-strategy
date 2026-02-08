# 🐋 Whale Copy Trading Backtest - Orchestration Mission

**Orchestrator:** Claude Opus (Whale-Backtest-Orchestrator)
**Date:** 2026-02-07 18:48 PST
**Status:** IN PROGRESS

---

## Mission Context

Previous whale tracking backtest showed:
- **229 trades** executed
- **55.9% win rate** (128W / 101L)
- **-9.15% average return** ❌ NEGATIVE
- **-20.95 total return** (lost money!)
- **Sharpe: -0.11** (terrible)
- **Max Drawdown: -38%**

**PROBLEM:** High win rate but losses are catastrophic (-100% on each loss).

---

## Sub-Agent Army Deployment

| Agent | Focus Area | Key Questions |
|-------|-----------|---------------|
| **A1** | Individual Whale Analysis | Which "whale" signal patterns actually work? |
| **A2** | Portfolio Diversification | Does combining whale signals reduce variance? |
| **A3** | Slippage Impact Analysis | How much edge erodes at 1%, 2%, 3% lag? |
| **A4** | Position Sizing Optimization | Kelly vs fixed vs volatility-scaled sizing |
| **A5** | Market Category Filter | Which market types (politics, sports, crypto) work best? |
| **A6** | Risk-Adjusted Synthesis | Final Sharpe, Sortino, VaR analysis |

---

## Data Assets Available

1. `polymarket_resolved_markets.json` - 2600+ resolved markets
2. `backtest-results/whale_tracking_results.json` - Previous results
3. `WHALE_TRACKING.md` - Comprehensive strategy documentation
4. Proxy whale signals: Large price movements (>15% moves)

---

## Key Constraints

- **NO actual whale wallet data** (API blocked)
- **Must proxy via price movements** as whale activity indicators
- **Focus on finding WHEN whale-following works vs fails**

---

## Success Criteria

1. Identify whale signal patterns with **positive expected value**
2. Find optimal **position sizing** to survive drawdowns
3. Determine **category filters** (which markets to trade)
4. Calculate realistic **Sharpe > 1.0** strategy
5. **GO/NO-GO recommendation** with clear rationale

