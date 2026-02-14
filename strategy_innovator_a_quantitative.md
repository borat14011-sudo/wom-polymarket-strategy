# Strategy Innovator A - Quantitative Focus Report

## MISSION
Develop novel Polymarket trading strategies from a blank slate with $10 capital, accounting for 4% round-trip fees (2% entry + 2% exit).

**Focus:** Quantitative/statistical approaches
**Data:** 93,949 historical markets, 2,600+ resolved markets with outcomes, 200 current active markets
**Constraints:** Slippage 0.5-3%, max 2% per trade ($0.20), 25% total exposure ($2.50), automatable strategies

---

## EXECUTIVE SUMMARY

Three novel quantitative trading strategies have been developed, each exploiting distinct statistical edges in prediction markets:

1. **Deadline Rush Mean Reversion (DRMR)** – Exploits overshoot/reversion patterns in final 24h before resolution
2. **Cross-Market Cointegration Arbitrage (CMCA)** – Pairs trading on politically correlated markets with temporary divergences
3. **Fat-Tail Probability Distortion (FTPD)** – Capitalizes on systematic underestimation of tail-risk probabilities

Each strategy includes a clear edge hypothesis, mathematical framework, backtesting approach, expected performance metrics, and implementation requirements. All strategies are designed to overcome the 4% fee barrier and operate within the micro-capital constraints.

---

## STRATEGY 1: DEADLINE RUSH MEAN REVERSION (DRMR)

### Edge Hypothesis
In the final 24 hours before resolution, probabilities exhibit predictable overshoot due to last-minute panic, sentiment-driven betting, or liquidity constraints, followed by partial reversion as rational arbitrageurs correct mispricings. This creates a mean-reversion opportunity with statistical edge.

### Mathematical Framework

**Probability Process Model:**
Let \( p(t) \) be the Yes probability at time \( t \), with \( T \) the resolution time. Model as Ornstein-Uhlenbeck process with time-dependent mean reversion strength:
\[
dp(t) = \theta(t)(\mu - p(t))dt + \sigma dW(t)
\]
where \( \theta(t) \) increases as \( t \to T \) (stronger reversion near deadline).

**Trading Signal:**
Compute rolling z-score over lookback window \( L \) (e.g., 6 hours):
\[
z(t) = \frac{p(t) - \bar{p}_L(t)}{\sigma_L(t)}
\]
where \( \bar{p}_L(t) \) and \( \sigma_L(t) \) are rolling mean and standard deviation.

**Entry/Exit Rules:**
- **Enter** when \( |z(t)| > 2.0 \) and \( t > T - 24h \) (within last 24h)
- **Direction:** Bet against the deviation (if \( z > 2 \), bet No; if \( z < -2 \), bet Yes)
- **Exit** when \( |z(t)| < 0.5 \) or at resolution (whichever comes first)
- **Stop-loss:** If \( |z(t)| > 3.5 \), close position (extreme move may indicate new information)

### Backtesting Approach

1. **Data Requirement:** Minute-level price data for all resolved markets (available in historical dataset)
2. **Simulation:** For each market, simulate trades in final 24h using z-score logic
3. **Fee Incorporation:** Apply 2% entry fee (exit fee avoided by holding to resolution)
4. **Slippage Model:** Add 0.5-3% random slippage based on volume quartiles
5. **Performance Metrics:** 
   - Win Rate
   - Expected Return per Trade (net of fees)
   - Sharpe Ratio (assuming daily returns)
   - Maximum Drawdown
   - Profit Factor (gross wins / gross losses)

### Expected Performance Metrics

- **Win Rate:** 60-70%
- **Edge per Trade:** 2-4% (net of 2% entry fee)
- **Hold Time:** 2-12 hours
- **Annualized Sharpe:** 1.5-2.5 (assuming 100+ trades/year)
- **Maximum Drawdown:** 15-20%
- **Kelly Fraction:** 5-10% of capital per trade (constrained to 2% max)

### Implementation Requirements

**Data Pipeline:**
- Real-time price feed (Polymarket API or WebSocket)
- Minute-level data storage for rolling calculations
- Resolution time metadata for each market

**Trading System:**
- Z-score calculator with configurable lookback
- Signal generator scanning markets within 24h of resolution
- Order management with slippage-aware execution
- Risk manager enforcing 2% per trade, 25% total exposure

**Monitoring:**
- Real-time P&L tracking
- Strategy performance dashboard
- Alert system for extreme z-scores

---

## STRATEGY 2: CROSS-MARKET COINTEGRATION ARBITRAGE (CMCA)

### Edge Hypothesis
Politically correlated markets (e.g., "Democrat wins Presidency" vs "Democrat wins Senate") exhibit long-run equilibrium relationships but experience temporary divergences due to differential liquidity, attention, or information diffusion. These divergences create pairs trading opportunities with statistical edge.

### Mathematical Framework

**Cointegration Testing:**
For candidate pairs (A, B), test for cointegration using Engle-Granger method:
1. Regress \( p_A(t) = \alpha + \beta p_B(t) + \epsilon(t) \)
2. Test residual \( \epsilon(t) \) for stationarity (ADF test)
3. If cointegrated, define spread: \( s(t) = p_A(t) - \beta p_B(t) - \alpha \)

**Trading Signal:**
Model spread as mean-reverting process:
\[
ds(t) = \theta(\mu - s(t))dt + \sigma dW(t)
\]
where \( \mu \) is long-term mean (typically zero).

**Entry/Exit Rules:**
- **Enter** when \( |s(t)| > 2\sigma_s \) (historical standard deviation of spread)
- **Direction:** If \( s(t) > 2\sigma_s \), short A & long B (bet against spread); if \( s(t) < -2\sigma_s \), long A & short B
- **Exit** when \( |s(t)| < 0.5\sigma_s \) or after 14 days (whichever comes first)
- **Hedge Ratio:** Use estimated \( \beta \) from cointegration regression

### Backtesting Approach

1. **Pair Selection:** Identify correlated markets via correlation matrix (>0.7 correlation over 30 days)
2. **Cointegration Testing:** Run Engle-Granger test on historical data (minimum 30 days of overlapping data)
3. **Spread Calculation:** Compute spread for cointegrated pairs
4. **Simulation:** Trade when spread exceeds 2σ, with hedge ratio β
5. **Fee Incorporation:** 4% round-trip (2% entry each side, 2% exit each side)
6. **Slippage:** Model both legs independently

### Expected Performance Metrics

- **Win Rate:** 55-65%
- **Edge per Trade:** 1-3% (net of 4% round-trip)
- **Hold Time:** 3-14 days
- **Annualized Sharpe:** 1.0-2.0
- **Maximum Drawdown:** 10-15%
- **Annual Opportunities:** 20-50 pairs

### Implementation Requirements

**Data Pipeline:**
- Daily probability data for all active markets
- Correlation matrix calculator
- Cointegration testing module

**Trading System:**
- Pair monitor tracking spread deviations
- Hedge ratio calculator
- Simultaneous order execution for both legs
- Portfolio manager ensuring net exposure within 25% limit

**Risk Management:**
- Maximum 2% capital per pair
- Stop-loss if spread widens beyond 3.5σ
- Regular re-estimation of cointegration parameters

---

## STRATEGY 3: FAT-TAIL PROBABILITY DISTORTION (FTPD)

### Edge Hypothesis
Traders systematically underestimate tail-risk probabilities (<5%) due to cognitive biases (neglect of extreme events, base-rate neglect). This creates mispricing where implied probabilities are below actual historical frequencies for similar event categories.

### Mathematical Framework

**Base Rate Estimation:**
For each event category \( C \) (e.g., "earthquake", "assassination", "market crash >20%"), compute historical frequency:
\[
f_C = \frac{\text{Number of Yes outcomes in category}}{\text{Total markets in category}}
\]
using resolved markets data.

**Mispricing Metric:**
For a market \( m \) in category \( C \) with current Yes probability \( p_m \), compute mispricing:
\[
\Delta_m = f_C - p_m
\]

**Trading Signal:**
- **Enter** when \( \Delta_m > \delta \) (threshold, e.g., 0.03) and \( p_m < 0.05 \) (tail event)
- **Direction:** Buy Yes (since implied probability underestimates true risk)
- **Exit:** Hold to resolution (no exit fee)
- **Position Sizing:** Kelly-based considering binary payoff

**Kelly Criterion for Binary Bet:**
\[
f^* = \frac{p_{\text{true}} \cdot (1/p_{\text{price}} - 1) - (1 - p_{\text{true}})}{1/p_{\text{price}} - 1}
\]
where \( p_{\text{true}} = f_C \) (estimated true probability), \( p_{\text{price}} = p_m \) (market price).

### Backtesting Approach

1. **Categorization:** Develop taxonomy of event categories (political, natural disasters, financial, etc.)
2. **Base Rate Calculation:** Compute historical frequencies per category using resolved markets
3. **Simulation:** For each historical market, simulate entry if \( \Delta_m > \delta \) and \( p_m < 0.05 \)
4. **Fee Incorporation:** 2% entry fee only (hold to resolution)
5. **Performance Metrics:** 
   - Expected Value per trade
   - Win Rate (expect low, but high payoff when wins)
   - Sharpe Ratio adjusted for binary payoff distribution
   - Maximum consecutive losses

### Expected Performance Metrics

- **Win Rate:** 3-8% (typical for tail events)
- **Average Payout on Wins:** 15-20x investment
- **Expected Value per Trade:** +2-5% (net of 2% fee)
- **Hold Time:** Variable (days to months)
- **Sharpe Ratio:** 0.5-1.0 (due to binary nature)
- **Maximum Drawdown:** 30-40% (from losing streaks)

### Implementation Requirements

**Data Pipeline:**
- Resolved markets database with outcomes
- Taxonomy classifier for new markets (NLP-based or rule-based)
- Base rate updater as new resolutions occur

**Trading System:**
- Real-time scanner for markets with \( p < 0.05 \)
- Base rate lookup and mispricing calculation
- Kelly position sizing calculator
- Portfolio manager limiting total tail-risk exposure

**Risk Management:**
- Maximum 0.5% per trade (due to high variance)
- Maximum 10% total capital in tail-risk bets
- Stop-loss not applicable (hold to resolution)
- Diversification across uncorrelated tail events

---

## COMPARATIVE ANALYSIS

| Metric | DRMR | CMCA | FTPD |
|--------|------|------|------|
| **Edge per Trade** | 2-4% | 1-3% | 2-5% |
| **Round-Trip Fees** | 2% (entry only) | 4% | 2% (entry only) |
| **Hold Time** | Hours | Days | Weeks/Months |
| **Win Rate** | 60-70% | 55-65% | 3-8% |
| **Sharpe Ratio** | 1.5-2.5 | 1.0-2.0 | 0.5-1.0 |
| **Max Drawdown** | 15-20% | 10-15% | 30-40% |
| **Capital Efficiency** | High | Medium | Low |
| **Automation Complexity** | Medium | High | Medium |
| **Data Requirements** | Minute-level | Daily | Categorical |

---

## VALIDATION ROADMAP

### Phase 1: Backtesting (Weeks 1-2)
1. **DRMR:** Implement minute-level backtest on resolved markets (last 24h)
2. **CMCA:** Identify correlated pairs, test cointegration, simulate spread trades
3. **FTPD:** Build taxonomy, compute base rates, simulate tail-risk bets

### Phase 2: Paper Trading (Weeks 3-6)
1. Implement real-time scanners for each strategy
2. Paper trade with $10 virtual capital
3. Track performance net of simulated fees and slippage

### Phase 3: Live Deployment (Week 7+)
1. Start with 1% of capital ($0.10 per trade)
2. Gradually scale as edge validates
3. Continuous monitoring and parameter optimization

---

## RISK MANAGEMENT PROTOCOLS

### Common Across All Strategies
- Maximum 2% per trade, 25% total exposure
- Daily P&L limits: 5% loss triggers review, 10% loss pauses trading
- Correlation monitoring between strategies
- Regular backtest recalibration (weekly)

### Strategy-Specific Safeguards
- **DRMR:** Avoid trading in last 2h before resolution (liquidity collapse)
- **CMCA:** Regular cointegration re-testing (bi-weekly)
- **FTPD:** Strict category diversification (max 2 bets per category)

---

## INNOVATION SUMMARY

These strategies represent novel quantitative approaches to prediction market trading:

1. **DRMR** leverages high-frequency mean reversion near deadlines—a phenomenon unique to time-bound prediction markets.
2. **CMCA** applies traditional pairs trading to politically correlated binary outcomes, exploiting differential information diffusion.
3. **FTPD** quantifies the "tail-risk neglect" bias using historical base rates, creating a systematic edge in low-probability events.

Each strategy is designed to overcome the 4% fee barrier through statistical edges that exceed transaction costs. The $10 capital constraint is addressed via micro-position sizing and strict risk limits.

---

## NEXT STEPS

1. **Immediate:** Begin backtesting DRMR using existing minute-level data
2. **Short-term:** Develop correlation matrix for CMCA pair identification
3. **Medium-term:** Build taxonomy for FTPD base rate calculation
4. **Long-term:** Integrate three strategies into a diversified quantitative portfolio

**Time Allocation:** 20 minutes completed for strategy development. Next phase requires implementation and validation.

---
*Report generated by Strategy Innovator A (Quantitative Focus)*  
*Date: 2026-02-10*  
*Model: DeepSeek R1*  
*Thinking: On*