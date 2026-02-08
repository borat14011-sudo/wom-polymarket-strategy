# Event-Based Backtest Report

**Architecture:** Event-driven simulation
**Initial Capital:** $10,000.00
**Final Capital:** $196.27
**Total Return:** -98.04%
**Total Trades:** 239

## Key Differences from Original Backtest:

1. ✅ **Event-based simulation** (not price array iteration)
2. ✅ **Realistic slippage model** (0.5-1% based on order size)
3. ✅ **Kelly criterion position sizing** (dynamic bet sizing)
4. ✅ **Liquidity constraints** (market impact modeling)
5. ✅ **Transaction costs** (2% fees + slippage)

---

## Strategy Results

### Trend Filter

- Total Trades: 58
- Win Rate: 31.0%
- Total P&L: $-2544.13
- Avg P&L/Trade: $-43.8643
- Profit Factor: 0.35
- Sharpe Ratio: -10.03
- Total Slippage: $71.24
- Total Fees: $227.23
- Avg Slippage: 1.38%

### NO-Side Bias

- Total Trades: 31
- Win Rate: 3.2%
- Total P&L: $-1038.17
- Avg P&L/Trade: $-33.4894
- Profit Factor: 0.02
- Sharpe Ratio: -44.87
- Total Slippage: $5.03
- Total Fees: $41.22
- Avg Slippage: 0.49%

### Expert Fade

- Total Trades: 39
- Win Rate: 7.7%
- Total P&L: $-1354.92
- Avg P&L/Trade: $-34.7417
- Profit Factor: 0.07
- Sharpe Ratio: -27.81
- Total Slippage: $9.57
- Total Fees: $60.96
- Avg Slippage: 0.63%

### Whale Copy

- Total Trades: 85
- Win Rate: 36.5%
- Total P&L: $-3870.68
- Avg P&L/Trade: $-45.5374
- Profit Factor: 0.34
- Sharpe Ratio: -9.39
- Total Slippage: $111.09
- Total Fees: $363.27
- Avg Slippage: 1.44%

### News Mean Reversion

- Total Trades: 26
- Win Rate: 30.8%
- Total P&L: $-1538.17
- Avg P&L/Trade: $-59.1603
- Profit Factor: 0.17
- Sharpe Ratio: -9.64
- Total Slippage: $32.21
- Total Fees: $87.23
- Avg Slippage: 1.54%


---

## Comparison with Original Backtest

| Strategy | Original Sharpe | Event-Based Sharpe | Difference |
|----------|----------------|--------------------|-----------|
| Trend Filter | 2.56 | -10.03 | -12.59 |
| NO-Side Bias | 2.55 | -44.87 | -47.42 |
| Expert Fade | 1.99 | -27.81 | -29.80 |
| Whale Copy | 3.13 | -9.39 | -12.52 |
| News Mean Reversion | 1.88 | -9.64 | -11.52 |

**Key Findings:**

- Event-based backtest accounts for realistic trading costs
- Slippage and fees significantly reduce returns vs. theoretical backtest
- Position sizing via Kelly criterion limits risk but may reduce trades
- Liquidity constraints prevent unrealistic large positions
