# 🐋 Whale Copy Trading - Quick Reference

## TL;DR Decision

| Question | Answer |
|----------|--------|
| **Is it profitable?** | ✅ YES with 65%+ accuracy whales |
| **What's the expected return?** | +16.8% median (up to +62.7% avg with Kelly sizing) |
| **Win probability?** | 99% chance of positive returns |
| **Can I execute manually?** | ⚠️ Yes if within 4 minutes |
| **Should I do this?** | 🟢 GO - Paper trade 30 days first |

## Optimal Strategy Settings

```python
WHALE_SETTINGS = {
    # Whale Selection
    'min_whale_accuracy': 0.65,    # Don't copy <65% win rate traders
    'min_whale_volume': 100000,    # $100K+ total volume
    
    # Execution
    'max_slippage': 0.02,          # 2% max slippage
    'execution_window_sec': 120,   # Execute within 2 minutes
    
    # Position Sizing (Kelly)
    'base_size_usd': 200,
    'max_position_pct': 0.10,      # 10% of capital max
    
    # Market Filters  
    'categories': ['politics', 'economics', 'crypto'],
    'min_market_volume': 20000,    # $20K+ market liquidity
    
    # Risk Management
    'max_total_exposure': 0.50,    # 50% of capital max
    'daily_loss_limit': 0.15,      # Stop at 15% daily loss
    'position_stop_loss': 0.25     # 25% stop per position
}
```

## Key Numbers

| Metric | Conservative | Optimistic |
|--------|--------------|------------|
| Annual Return | 30-50% | 80-150% |
| Sharpe Ratio | 0.8-1.2 | 1.5-2.0 |
| Max Drawdown | 15-25% | 10-20% |
| Win Rate | 55-60% | 60-70% |

## Category Priority

1. 🟢 **Politics** - Best edge, high volume
2. 🟢 **Economics** - Macro events, Fed decisions
3. 🟡 **Crypto** - Major coins only
4. 🔴 **Sports** - Too fast, avoid
5. 🔴 **Entertainment** - Too noisy, avoid

## Execution Checklist

- [ ] Signal detected (whale opened position)
- [ ] Whale accuracy verified (>65% historical)
- [ ] Market category in whitelist
- [ ] Market volume > $20K
- [ ] Position size calculated (Kelly or 5-10%)
- [ ] Execute within 2 minutes
- [ ] Set stop loss (25% of position)
- [ ] Log trade for tracking

## Files

- `WHALE_BACKTEST_RESULTS.md` - Full analysis report
- `whale-backtest-orchestration/` - All code and data
- `WHALE_TRACKING.md` - Strategy documentation
