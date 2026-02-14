# GENERAL STRATEGY BACKTEST REPORT

## Data Limitations
- **Resolved markets dataset**: Only final outcomes (binary 0/1 prices). No pre-resolution prices.
- **Markets snapshot**: Contains 93,949 markets with current prices, but only snapshot in time; cannot track price movements.
- **Active markets**: 200 current markets with live prices, but unknown future outcomes.
- **No historical price time series** available for backtesting momentum/breakout/hype strategies.

Therefore, only **static probability strategies** can be evaluated using current price snapshots under market efficiency assumptions.

## Methodology
- Assume market price reflects true probability (efficient market).
- Include Polymarket fees: **2% entry + 2% exit** (total ~4% round-trip).
- Include spread cost: average spread = **0.9%** (bid-ask).
- Compute expected return per share:  
  \[
  E[return] = p \cdot (1 - f_{exit}) - p \cdot (1 + f_{entry}) = -p \cdot (f_{entry} + f_{exit})
  \]
  where \(p\) is market price of Yes share.
- Break‑even true probability required for positive EV:  
  \[
  q_{break} = p \cdot \frac{1 + f_{entry}}{1 - f_{exit}}
  \]
- For longshots, also consider spread: effective purchase price = mid price + half spread.

## Results

### 1. FAVORITES STRATEGY (>80% probability)
- **Active markets count**: 6 out of 200 have Yes price > 0.8.
- **Average expected return** (with fees): **‑3.7%** per bet.
- **Break‑even delta**: For \(p = 0.95\), need true probability > **0.9888** (delta +3.9%).
- **Conclusion**: Heavy favorites are **highly unlikely to overcome fees**. Market efficiency suggests no systematic mispricing large enough to offset fee drag. **Not viable.**

### 2. LONGSHOT STRATEGY (<20% probability)
- **Active markets count**: 176 out of 200 have Yes price < 0.2.
- **Average expected return** (with fees): **‑0.1%** per bet.
- **Break‑even delta**: For \(p = 0.05\), need true probability > **0.0520** (delta +0.2%).
- **Implication**: A very small edge (0.2‑0.8% absolute probability mispricing) turns the strategy profitable.
- **Volatility**: Low win rate (≈5%) leads to high variance; requires proper position sizing.
- **Conclusion**: Longshots **could be viable** if you can identify even slight mispricing. Fee impact is relatively smaller because stake is small.

### 3. HYPE FADE STRATEGY
- **Cannot backtest** without event‑tagged price history.
- **Hypothesis**: Overreactions to news (Musk tweets, earnings) create temporary price spikes that revert. Fading these spikes may capture alpha.
- **Required data**: Minute‑level price series around news events. Not available.

### 4. BREAKOUT STRATEGY
- **Cannot backtest** without historical price series.
- **Hypothesis**: Momentum trends exist in prediction markets; entering on breakout of support/resistance could be profitable.
- **Required data**: Time‑series prices, volume. Not available.

## Optimal Parameter Ranges
| Strategy | Price Range | Expected EV (no edge) | Edge Needed | Viability |
|----------|-------------|------------------------|-------------|-----------|
| Favorites | 0.85‑0.95 | ‑3.4% to ‑3.8% | +3‑4% | ❌ Poor |
| Longshots | 0.05‑0.15 | ‑0.1% to ‑0.3% | +0.2‑0.8% | ✅ Possible |
| Longshots | 0.15‑0.20 | ‑0.3% to ‑0.4% | +0.8‑1.2% | ⚠️ Marginal |

## Capital Allocation & Risk Management
- **Kelly Criterion**: For longshots with small edge, optimal bet size is a small fraction of bankroll.
- **Example**: If true probability \(q = p + 0.01\), edge = \(q(1-f_{exit}) - p(1+f_{entry})\). For p=0.05, edge ≈ 0.004. Kelly fraction ≈ edge / (1-p) ≈ **0.42%** of bankroll per bet.
- **Diversification**: Bet on many longshots to reduce variance.
- **Stop‑loss**: Not applicable (hold to resolution).
- **Position sizing**: Fixed fractional betting (e.g., 0.5‑1% per bet).

## Recommendations
1. **Avoid favorites** – fees consume any possible edge.
2. **Focus on longshots** (p < 0.15) where fee drag is minimal. Even a slight predictive advantage can yield positive EV.
3. **Combine with fundamental analysis** to identify mispricing (e.g., news, sentiment, external data).
4. **Monitor spreads** – illiquid markets have wider spreads that further reduce edge.
5. **Use limit orders** to avoid paying the full spread.

## Next Steps for Robust Backtesting
- Collect historical price data via Polymarket API or archive services.
- Build event database (news, tweets) to test hype‑fade strategies.
- Implement simulation engine with realistic slippage and fees.
- Perform cross‑validation on out‑of‑sample periods.

## Conclusion
**Only longshot strategies show potential viability after fees**, provided you can consistently identify small mispricings. Favorites are nearly impossible to profit from due to fee erosion. Hype‑fade and breakout strategies remain untested due to data limitations.

*Note: All conclusions assume efficient markets; any persistent market inefficiencies could change the outlook.*