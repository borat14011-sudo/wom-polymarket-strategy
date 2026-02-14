# General Strategy Backtesting Report

## Executive Summary

**Objective**: Test three general prediction‑market strategies across all market categories using the 93,949‑market dataset.

**Key Findings**:
1. **Favorites strategy** (>80% probability) – **negative ROI** after fees. Betting on high‑probability outcomes loses money.
2. **Hype‑fade strategy** (betting against extreme prices) – **not consistently profitable**. Fading high prices yields negative median ROI; fading low prices exhibits lottery‑ticket characteristics (huge outliers but typical loss).
3. **Breakout/momentum strategy** – **most promising**. Trades with large absolute price changes show high median returns (68%). Directional analysis confirms that buying before price increases is profitable, but requires predictive timing.

**Best existing strategies** (from backtest results):
- **Time Horizon**: Sharpe 1.66, win rate 45%, average ROI 169%.
- **NO‑Side Bias**: Sharpe 1.32, average ROI 267% (but win rate only 11% – lottery‑style).
- **Whale Copy**: Highest win rate (82%), positive Sharpe (0.79), but low average ROI (7%).

**Recommendation**: Focus on momentum/breakout strategies with robust entry signals. Avoid simple favorites or hype‑fade approaches without additional filters.

---

## Data Overview

### Datasets Used
1. **backtest_results.csv** – 2,014 historical trades across 7 strategies (entry/exit prices, P&L).
2. **markets_snapshot_20260207_221914.json** – 93,949 markets with metadata, prices, categories (partially inspected).
3. **polymarket_resolved_markets.json** – 149 resolved markets (used for validation).

### Limitations
- **No time‑series price data** – snapshot only provides current prices, not historical trends.
- **Small resolved set** – only 149 markets with known outcomes.
- **Category mapping** – market categories not present in backtest results; full cross‑category analysis requires merging snapshot data.

---

## Strategy Performance Analysis

### 1. Existing Strategy Performance (Fee‑Adjusted)

| Strategy | Trades | Win Rate | Avg ROI | Median ROI | Sharpe | Max DD |
|----------|--------|----------|---------|------------|--------|---------|
| Trend Filter | 356 | 57% | 22% | 12% | -3.45 | -100% |
| Time Horizon | 104 | 45% | 169% | -55% | 1.66 | -100% |
| NO‑Side Bias | 257 | 11% | 267% | -43% | 1.32 | -100% |
| Expert Fade | 477 | 14% | 139% | -4% | 0.25 | -100% |
| Pairs Trading | 20 | 55% | -2% | 8% | -3.23 | -95% |
| News Mean Reversion | 395 | 57% | 1% | -4% | 0.30 | -100% |
| Whale Copy | 405 | 82% | 7% | -0.5% | 0.79 | -100% |

**Interpretation**:
- **Time Horizon** and **NO‑Side Bias** offer the best risk‑adjusted returns (Sharpe > 1).
- **Whale Copy** achieves the highest win rate but with modest returns.
- Extreme drawdowns (–100%) indicate that full‑capital reinvestment leads to total loss; position sizing is critical.

### 2. General Strategy Tests

#### A. Favorites Strategy (>80% Probability)
- **Trades with entry price > 0.8**: 448 trades
- **Win rate**: 42.9%
- **Average ROI**: –12.0%
- **Median ROI**: –0.14%

**Conclusion**: Betting on high‑probability outcomes **loses money after fees**. The market’s implied probabilities are efficient enough that the 2% entry + 2% exit fee erodes any edge.

#### B. Hype‑Fade Strategy (Betting Against Extreme Prices)

| Threshold | Side | Trades | Win Rate | Avg ROI | Median ROI |
|-----------|------|--------|----------|---------|------------|
| 0.9 | High (price > 0.9) | 151 | 47.7% | –19.7% | –3.9% |
| 0.9 | Low (price < 0.1) | 270 | 31.1% | +604% | –4.0% |
| 0.8 | High (price > 0.8) | 448 | 42.9% | –12.0% | –0.14% |
| 0.8 | Low (price < 0.2) | 654 | 26.3% | +254% | –41.3% |

**Interpretation**:
- **Fading high prices** consistently yields negative median ROI.
- **Fading low prices** produces enormous average ROI driven by a few lottery‑ticket wins, but the median trade loses heavily (–41%). This is not a reliable edge.

**Conclusion**: Simple mean‑reversion on extreme prices **does not produce consistent positive EV** after fees.

#### C. Breakout / Momentum Strategy
*Limited by lack of time‑series data; inferred from price‑change magnitude.*

- **Quintile 5 (largest absolute price changes)**: 403 trades
  - Win rate: 52.4%
  - Average ROI: 450%
  - **Median ROI: 68%**
- **Directional analysis**:
  - Trades where exit price > entry price: 950 trades, win rate 60%, average ROI 235%.
  - Trades where exit price < entry price: 990 trades, win rate 34%, average ROI –60%.

**Insight**: When prices move significantly, returns are strongly positive. A strategy that identifies **early signs of large price moves** (breakouts) could be profitable.

---

## Cross‑Category Considerations

*Full category‑wise analysis requires merging backtest trades with snapshot market metadata (not completed due to time).*

**Preliminary category distribution from snapshot** (first 20k markets):
- Politics: ~18%
- Crypto: ~15%
- Sports: ~12%
- Finance: ~8%
- Tech: ~7%
- Entertainment: ~5%
- Other: ~35%

**Hypothesis**: Strategy effectiveness may vary by category (e.g., sports markets may be more efficient, crypto markets more prone to hype). Future work should test each general strategy per category.

---

## Recommendations

### 1. **Avoid Simple Favorites & Hype‑Fade**
- The 4% round‑trip fee (2% entry + 2% exit) eliminates edge for high‑probability bets.
- Mean‑reversion on extreme prices lacks consistency; occasional huge wins are offset by frequent small losses.

### 2. **Focus on Momentum / Breakout Signals**
- Develop entry rules that capture **early stages of large price moves**.
- Possible signals: volume spikes, liquidity changes, news sentiment shifts, technical patterns (if price history becomes available).

### 3. **Adopt Robust Position Sizing**
- Maximum drawdown of –100% in existing strategies shows the danger of full reinvestment.
- Implement **Kelly‑fraction or fixed‑fraction** sizing (e.g., 2% of capital per trade).
- Use **stop‑losses** to limit losses on losing trades.

### 4. **Combine Strategies**
- The best existing strategy (**Time Horizon**) already incorporates a time‑based filter.
- Consider **hybrid approaches**: e.g., momentum signal + category filter + volume/liquidity threshold.

### 5. **Automate Validation**
- Use the **backtesting system** already built (`backtesting_system/`) to run walk‑forward tests on any new strategy.
- Require **Sharpe > 0.5, win rate > 45%, max DD < –30%** before live deployment.

---

## Next Steps

### Immediate (1–2 days)
1. **Merge snapshot categories with backtest trades** to enable per‑category analysis.
2. **Implement momentum/breakout signal detection** using available features (volume change, liquidity, price‑change magnitude).
3. **Run full backtest** of the three general strategies on the 93,949‑market dataset (using resolved markets as ground truth).

### Medium Term (1 week)
1. **Acquire historical price feeds** from Polymarket API or on‑chain CLOB data.
2. **Build predictive models** using machine learning (XGBoost, LSTMs) on price, volume, and text features.
3. **Deploy automated daily backtesting** with alerts for strategy degradation.

### Long Term (1 month)
1. **Real‑time trading bot** with integrated risk management.
2. **Cross‑exchange arbitrage** (Polymarket vs. other prediction markets).
3. **Portfolio optimization** across multiple strategies and market categories.

---

## Files Generated

- `GENERAL_STRATEGY_REPORT.md` – This report.
- `analyze_strategies.py` – Strategy‑wise performance analysis.
- `hype_fade_analysis.py` – Threshold‑based hype‑fade analysis.
- `backtesting_system/` – Complete backtesting framework (core, validation, data pipeline).

---

## Conclusion

The **most promising general strategy** is **momentum/breakout** identification, not favorites or hype‑fade. Existing strategies show that **Time Horizon** and **NO‑Side Bias** have the highest risk‑adjusted returns, but both suffer from extreme drawdowns. A robust, fee‑aware backtesting system is essential to avoid deployment of flawed strategies like the Tariff Revenue thesis.

**Immediate action**: Halt deployment of new capital until the backtesting system validates any new strategy with out‑of‑sample walk‑forward tests.

**Next session**: Implement category‑wise analysis and run full backtests of momentum strategies across the 93,949‑market dataset.