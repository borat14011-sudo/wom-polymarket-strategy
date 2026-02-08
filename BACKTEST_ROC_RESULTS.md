# Polymarket ROC Momentum Strategy Backtest Results

## Executive Summary

This backtest evaluates a momentum-based trading strategy on Polymarket markets using Rate of Change (ROC) indicators combined with Risk/Reward Ratio (RVR) filters.

**Data Source**: Synthetic data based on realistic Polymarket market patterns (10 markets, 30 days of hourly data)

### Strategy Parameters
- **Entry Conditions**: ROC ≥ threshold AND RVR > 2.5x
- **Exit Conditions**: 
  - Stop Loss: 12% below entry
  - Tiered Profit Targets: 10% (exit 33%), 20% (exit 33%), 30% (exit 34%)

### ROC Thresholds Tested
- 5%, 10%, 15%, 20%

### Timeframes Tested
- 6 hours, 12 hours, 24 hours

---

## Results by Configuration


### Configuration: 15% ROC over 24h

| Metric | Value |
|--------|-------|
| **Total Trades** | 64 |
| **Winning Trades** | 42 |
| **Losing Trades** | 22 |
| **Win Rate** | 65.63% |
| **Total PnL** | +323.31% |
| **Avg PnL/Trade** | +5.05% |
| **Avg Duration** | 19.8h |


### Configuration: 10% ROC over 6h

| Metric | Value |
|--------|-------|
| **Total Trades** | 84 |
| **Winning Trades** | 48 |
| **Losing Trades** | 36 |
| **Win Rate** | 57.14% |
| **Total PnL** | +222.12% |
| **Avg PnL/Trade** | +2.64% |
| **Avg Duration** | 24.2h |


### Configuration: 5% ROC over 12h

| Metric | Value |
|--------|-------|
| **Total Trades** | 141 |
| **Winning Trades** | 79 |
| **Losing Trades** | 62 |
| **Win Rate** | 56.03% |
| **Total PnL** | +214.60% |
| **Avg PnL/Trade** | +1.52% |
| **Avg Duration** | 27.1h |


### Configuration: 15% ROC over 6h

| Metric | Value |
|--------|-------|
| **Total Trades** | 51 |
| **Winning Trades** | 30 |
| **Losing Trades** | 21 |
| **Win Rate** | 58.82% |
| **Total PnL** | +148.88% |
| **Avg PnL/Trade** | +2.92% |
| **Avg Duration** | 25.4h |


### Configuration: 5% ROC over 24h

| Metric | Value |
|--------|-------|
| **Total Trades** | 140 |
| **Winning Trades** | 68 |
| **Losing Trades** | 72 |
| **Win Rate** | 48.57% |
| **Total PnL** | +95.98% |
| **Avg PnL/Trade** | +0.69% |
| **Avg Duration** | 25.7h |


### Configuration: 10% ROC over 12h

| Metric | Value |
|--------|-------|
| **Total Trades** | 107 |
| **Winning Trades** | 55 |
| **Losing Trades** | 52 |
| **Win Rate** | 51.40% |
| **Total PnL** | +63.25% |
| **Avg PnL/Trade** | +0.59% |
| **Avg Duration** | 21.9h |


### Configuration: 20% ROC over 12h

| Metric | Value |
|--------|-------|
| **Total Trades** | 55 |
| **Winning Trades** | 25 |
| **Losing Trades** | 30 |
| **Win Rate** | 45.45% |
| **Total PnL** | +11.78% |
| **Avg PnL/Trade** | +0.21% |
| **Avg Duration** | 23.9h |


### Configuration: 5% ROC over 6h

| Metric | Value |
|--------|-------|
| **Total Trades** | 143 |
| **Winning Trades** | 67 |
| **Losing Trades** | 76 |
| **Win Rate** | 46.85% |
| **Total PnL** | -34.21% |
| **Avg PnL/Trade** | -0.24% |
| **Avg Duration** | 22.7h |


### Configuration: 20% ROC over 24h

| Metric | Value |
|--------|-------|
| **Total Trades** | 35 |
| **Winning Trades** | 12 |
| **Losing Trades** | 23 |
| **Win Rate** | 34.29% |
| **Total PnL** | -129.22% |
| **Avg PnL/Trade** | -3.69% |
| **Avg Duration** | 27.8h |


### Configuration: 10% ROC over 24h

| Metric | Value |
|--------|-------|
| **Total Trades** | 106 |
| **Winning Trades** | 51 |
| **Losing Trades** | 55 |
| **Win Rate** | 48.11% |
| **Total PnL** | -142.02% |
| **Avg PnL/Trade** | -1.34% |
| **Avg Duration** | 24.5h |


### Configuration: 15% ROC over 12h

| Metric | Value |
|--------|-------|
| **Total Trades** | 70 |
| **Winning Trades** | 30 |
| **Losing Trades** | 40 |
| **Win Rate** | 42.86% |
| **Total PnL** | -176.67% |
| **Avg PnL/Trade** | -2.52% |
| **Avg Duration** | 26.3h |


### Configuration: 20% ROC over 6h

| Metric | Value |
|--------|-------|
| **Total Trades** | 85 |
| **Winning Trades** | 28 |
| **Losing Trades** | 57 |
| **Win Rate** | 32.94% |
| **Total PnL** | -340.44% |
| **Avg PnL/Trade** | -4.01% |
| **Avg Duration** | 8.3h |


---

## Performance Ranking

| Rank | Configuration | Total PnL | Win Rate | Trades | Avg PnL/Trade | Avg Duration |
|------|---------------|-----------|----------|--------|---------------|--------------|
| 1 | 15% / 24h | +323.31% | 65.6% | 64 | +5.05% | 19.8h |
| 2 | 10% / 6h | +222.12% | 57.1% | 84 | +2.64% | 24.2h |
| 3 | 5% / 12h | +214.60% | 56.0% | 141 | +1.52% | 27.1h |
| 4 | 15% / 6h | +148.88% | 58.8% | 51 | +2.92% | 25.4h |
| 5 | 5% / 24h | +95.98% | 48.6% | 140 | +0.69% | 25.7h |
| 6 | 10% / 12h | +63.25% | 51.4% | 107 | +0.59% | 21.9h |
| 7 | 20% / 12h | +11.78% | 45.5% | 55 | +0.21% | 23.9h |
| 8 | 5% / 6h | -34.21% | 46.9% | 143 | -0.24% | 22.7h |
| 9 | 20% / 24h | -129.22% | 34.3% | 35 | -3.69% | 27.8h |
| 10 | 10% / 24h | -142.02% | 48.1% | 106 | -1.34% | 24.5h |
| 11 | 15% / 12h | -176.67% | 42.9% | 70 | -2.52% | 26.3h |
| 12 | 20% / 6h | -340.44% | 32.9% | 85 | -4.01% | 8.3h |

---

## Optimal Configuration

**🏆 Best Performer: 15% ROC over 24h timeframe**

- **Total Return**: +323.31%
- **Win Rate**: 65.63%
- **Total Trades**: 64
- **Average PnL per Trade**: +5.05%
- **Average Trade Duration**: 19.8 hours

**⚠️ Worst Performer: 20% ROC over 6h timeframe**

- **Total Return**: -340.44%
- **Win Rate**: 32.94%

---

## Key Insights


### 1. ROC Threshold Analysis

| Threshold Range | Avg Win Rate | Avg Total PnL | Observations |
|----------------|--------------|---------------|--------------|
| **High (15-20%)** | 46.7% | -27.06% | ⚠️ Fewer opportunities |
| **Low (5-10%)** | 51.4% | +69.95% | ✅ More consistent |

**Key Finding**: Lower ROC thresholds capture more opportunities with acceptable quality

### 2. Timeframe Analysis

**6h Timeframe**:
- Average Total PnL: -0.91%
- Average Win Rate: 48.9%
- Average Trades: 90.8

**12h Timeframe**:
- Average Total PnL: +28.24%
- Average Win Rate: 48.9%
- Average Trades: 93.3

**24h Timeframe**:
- Average Total PnL: +37.01%
- Average Win Rate: 49.1%
- Average Trades: 86.3

### 3. Trade Frequency vs Performance

| Configuration | Trades | Total PnL | Win Rate |
|---------------|--------|-----------|----------|
| 5% / 6h | 143 | -34.21% | 46.9% |
| 5% / 12h | 141 | +214.60% | 56.0% |
| 5% / 24h | 140 | +95.98% | 48.6% |

**Observation**: More trades ≠ more profit; quality > quantity

---

## Sample Trades (Top Configuration)

| Market | Entry | ROC | RVR | PnL | Duration | Exit |
|--------|-------|-----|-----|-----|----------|------|
| 2025 US Recession | 0.720 | 17.5% | 3.24x | -13.69% | 25h | stop_loss |
| 2025 US Recession | 0.745 | 16.9% | 2.85x | +12.38% | 67h | profit_target |
| Bitcoin to $100k in 2025 | 0.464 | 15.5% | 9.62x | +12.64% | 7h | profit_target |
| Bitcoin to $100k in 2025 | 0.390 | 24.4% | 13.02x | -12.21% | 34h | stop_loss |
| Bitcoin to $100k in 2025 | 0.443 | 20.8% | 10.49x | +12.42% | 38h | profit_target |
| Bitcoin to $100k in 2025 | 0.496 | 18.3% | 8.47x | +14.03% | 9h | profit_target |
| Bitcoin to $100k in 2025 | 0.339 | 22.5% | 16.25x | +18.85% | 6h | profit_target |
| Bitcoin to $100k in 2025 | 0.434 | 28.0% | 10.87x | -12.01% | 23h | stop_loss |
| Bitcoin to $100k in 2025 | 0.367 | 18.6% | 14.36x | +13.94% | 9h | profit_target |
| Bitcoin to $100k in 2025 | 0.428 | 16.7% | 11.12x | +16.32% | 14h | profit_target |
| Bitcoin to $100k in 2025 | 0.546 | 27.5% | 6.92x | -12.60% | 13h | stop_loss |
| Bitcoin to $100k in 2025 | 0.419 | 16.0% | 11.56x | +21.94% | 4h | profit_target |

---

## Methodology

1. **Data Source**: Synthetic price histories for 10 diverse Polymarket-style markets
2. **Time Period**: 30 days of hourly price data per market (720 data points)
3. **Entry Signal**: ROC over specified timeframe ≥ threshold AND RVR > 2.5x
4. **Position Sizing**: Equal position sizes for all trades
5. **Exit Logic**: 
   - Hit 12% stop loss → full exit
   - Hit 10% profit → exit 33% of position
   - Hit 20% profit → exit another 33%
   - Hit 30% profit → exit remainder
6. **Lookback Period**: Varies by timeframe (6h, 12h, or 24h)
7. **Trade Spacing**: Minimum 24 hours between trades on same market

## Limitations

- **Synthetic Data**: Real markets may behave differently
- **No Liquidity Modeling**: Assumes perfect fills at market price
- **No Slippage**: Actual execution would incur slippage costs
- **No Fees**: Transaction fees would reduce returns
- **Limited History**: 30 days may not capture all market regimes
- **No External Factors**: News events, major announcements not modeled

## Recommendations

Based on this backtest:

1. **🎯 Optimal Setup**: Use **15% ROC threshold** with **24h timeframe**
   - Expected win rate: ~66%
   - Expected avg PnL per trade: ~+5.1%
   - Avg trade duration: ~20 hours

2. **📊 Risk Management**:
   - The 12% stop loss is CRITICAL - never override it
   - Position size should account for correlation between markets
   - Don't exceed 20% of capital per trade

3. **⚙️ Strategy Tuning**:
   - High threshold = fewer but better signals
   - Longer timeframe = more stable signals
   - Consider RVR > 3.0x for even higher quality signals

4. **📈 Market Selection**:
   - Focus on high-volume, liquid markets
   - Avoid markets with binary news catalysts
   - Prefer markets with gradual price discovery

5. **🔄 Monitoring**:
   - Re-run backtest weekly with live data
   - Track actual vs expected performance
   - Pause strategy if win rate drops below 46%

6. **💡 Advanced Optimizations**:
   - Combine with volume analysis for confirmation
   - Add market sentiment filters
   - Use dynamic position sizing based on RVR
   - Implement partial entry on weaker signals

---

## Risk Disclosure

⚠️ **Important**: This backtest uses synthetic data and does not guarantee future performance. Polymarket trading involves substantial risk. Always:

- Start with small position sizes
- Never risk more than you can afford to lose
- Monitor positions actively
- Have a plan for every trade
- Be aware of regulatory considerations

---

*Backtest completed: 2026-02-07 00:58:38 UTC*
*Total configurations tested: 12*
*Total trades simulated: 1081*
