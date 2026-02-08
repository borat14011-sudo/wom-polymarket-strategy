# Cross-Platform Prediction Market Arbitrage Strategy

## Executive Summary

**Bottom Line:** Cross-platform arbitrage between prediction markets is **theoretically possible but practically difficult** with $100 capital due to high fees, platform restrictions, and the fundamental challenge that **Metaculus doesn't trade real money**.

## Platform Analysis

### 1. Polymarket
- **Type:** Crypto-based prediction market (USDC on Polygon blockchain)
- **Fees:** 
  - **Mostly FREE trading** (no fees on most markets)
  - 15-minute crypto markets have small taker fees
  - No deposit/withdrawal fees (though intermediaries like Coinbase may charge)
- **Trading Mechanism:** Shares priced $0.00-$1.00, winning shares pay $1.00
- **Capital Requirements:** No stated minimums
- **Allows Arbitrage:** YES, but requires crypto wallet
- **Geographic Restrictions:** Geoblocked for US users

### 2. PredictIt
- **Type:** Real-money market (USD)
- **Fees:** **VERY HIGH**
  - **10% fee on profits** (on earnings above investment)
  - **5% withdrawal fee**
  - **Total: ~15% fee drag**
- **Trading Restrictions:**
  - $3,500 cap per contract (recently raised from $850)
  - Former 5,000 person limit per market (removed in 2025)
- **Allows Arbitrage:** YES, but fees make it very difficult
- **Geographic Restrictions:** US citizens only

### 3. Kalshi
- **Type:** CFTC-regulated derivatives exchange (USD)
- **Fees:** Transaction fees charged on expected earnings (see fee schedule)
- **Trading Mechanism:** Event contracts
- **Allows Arbitrage:** YES
- **Geographic Restrictions:** US only

### 4. Metaculus
- **Type:** **REPUTATION-BASED forecasting platform**
- **Fees:** FREE
- **Trading Mechanism:** **NO REAL MONEY** - users make predictions and earn points/reputation
- **Allows Arbitrage:** **NO** - not a real-money market
- **Purpose:** Academic/research forecasting

## Critical Insight: Metaculus ≠ Money

**Metaculus is NOT a tradeable market.** It's a forecasting platform where users:
- Make probabilistic predictions
- Earn points and reputation for accuracy
- Cannot buy/sell or exchange for real money
- Provide data for academic research

**This eliminates Metaculus from arbitrage strategies entirely.**

## Viable Arbitrage Pairs

Given the above, only **three platforms** allow real-money trading:
1. **Polymarket** (crypto)
2. **PredictIt** (USD, high fees)
3. **Kalshi** (regulated USD)

### Realistic Arbitrage Scenarios

**Best case:** Polymarket ↔ Kalshi
- Both allow real trading
- Polymarket has minimal fees
- Kalshi is regulated but has fees
- **Problem:** Polymarket blocks US users, Kalshi is US-only
- **Workaround:** Would require VPN (legal/regulatory risk)

**Difficult case:** PredictIt ↔ Kalshi
- Both US-based, legally accessible
- **Problem:** PredictIt's 15% total fees eat most arbitrage profit
- Example: 5-point price difference → 15% fees = negative return

## Fee Analysis: Can $100 Work?

### Example Arbitrage Scenario

**Event:** "Will X win election?"
- **Platform A:** YES shares @ $0.45
- **Platform B:** YES shares @ $0.55
- **Spread:** 10 cents ($0.10)

### With $100 Capital:

**Buy on Platform A:** 
- $100 ÷ $0.45 = 222 shares @ $0.45

**Sell on Platform B:**
- 222 shares @ $0.55 = $122.10 revenue
- Gross profit: $22.10

**Minus PredictIt fees (worst case):**
- 10% profit fee: $22.10 × 0.10 = $2.21
- 5% withdrawal fee: ~$6
- **Net profit: ~$14** (14% return)

**Reality check:**
- Finding 10-cent spreads on same event across platforms is rare
- Most spreads are 1-3 cents
- With 15% fees, you need >15-cent spread just to break even on PredictIt
- $100 capital limits diversification

### Polymarket-Only (if accessible):
- Near-zero fees
- Smaller spreads (1-2 cents) could be profitable
- $100 could work with high-volume, small-margin trades
- **But:** Geographic restrictions

## Backtesting Possibilities

### Historical Data Availability:

**Polymarket:**
- Has public API
- Historical price data available
- Can compare past odds

**PredictIt:**
- Historical data available through academic partnerships
- Limited public API

**Kalshi:**
- API available
- Historical contract data

**Metaculus:**
- Forecasts are public
- Open-source platform (BSD-2 license)
- **But:** Predictions ≠ tradeable prices

### Backtesting Strategy:

1. **Identify common events** across Polymarket, PredictIt, Kalshi
2. **Compare historical prices** at same timestamps
3. **Calculate spreads** accounting for fees
4. **Simulate trades** with $100 capital
5. **Factor in:**
   - Withdrawal times (crypto vs ACH)
   - Slippage
   - Market depth/liquidity
   - Platform limits

**Tools needed:**
- Python + pandas for data analysis
- API access to historical price feeds
- Scripts to identify matching markets

## Real Examples (Hypothetical)

### Example 1: 2024 Election Market

**Event:** "Democratic nominee for President 2024"

| Platform | YES Price | NO Price | Volume |
|----------|-----------|----------|--------|
| Polymarket | $0.62 | $0.38 | High |
| PredictIt | $0.58 | $0.42 | Medium |
| Kalshi | $0.60 | $0.40 | Medium |

**Arbitrage opportunity:**
- Buy YES @ $0.58 on PredictIt
- Sell YES @ $0.62 on Polymarket
- Spread: $0.04 (4 cents)
- **After fees:** Likely break-even or small loss due to PredictIt's 15%

### Example 2: Fed Rate Decision

**Event:** "Will Fed raise rates in March?"

| Platform | YES Price |
|----------|-----------|
| Kalshi | $0.72 |
| Polymarket | $0.68 |

**Arbitrage:**
- Buy YES @ $0.68 (Polymarket)
- Sell YES @ $0.72 (Kalshi)
- Spread: $0.04
- Polymarket fees: ~0%
- Kalshi fees: TBD from fee schedule
- **Potential profit:** 2-4% after fees

## Key Challenges

### 1. **Geographic Restrictions**
- Polymarket: No US users
- PredictIt: US only
- Kalshi: US only
- **Arbitrage requires access to multiple platforms**

### 2. **Capital Efficiency**
- $100 is tight for multi-platform arbitrage
- Platform limits ($3,500 on PredictIt)
- Need funds on multiple platforms simultaneously

### 3. **Timing Risk**
- Markets move fast
- Withdrawal times differ (crypto vs ACH)
- Spreads may close before you can execute both sides

### 4. **Market Matching**
- Same events must exist on multiple platforms
- Question wording must be identical
- Resolution criteria must match

### 5. **Liquidity**
- Small markets may not have counterparties
- Slippage can eat profits
- $100 is small but still needs buyers/sellers

## Recommendations

### For $100 Capital:

**DON'T:**
- ❌ Try to arbitrage with PredictIt (fees too high)
- ❌ Count on Metaculus (not a real-money market)
- ❌ Ignore geographic restrictions (legal risk)

**DO:**
- ✅ Focus on **Kalshi** (US-legal, lower fees than PredictIt)
- ✅ **Paper trade first** (track hypothetical trades)
- ✅ **Backtest** historical data before risking capital
- ✅ Start with **one platform** to learn mechanics
- ✅ Look for **correlated but distinct** markets (e.g., "Candidate wins" vs "Party wins") for hedging

### Better Alternatives with $100:

1. **Single-platform directional trading** (if you have an edge)
2. **Correlated market hedging** on one platform
3. **Save up to $500-1000** for viable arbitrage capital
4. **Use Metaculus for practice** (free, learn forecasting without risk)

## Conclusion

**Is cross-platform arbitrage possible?** Yes, theoretically.

**With $100?** Barely, and only if:
- You have access to low-fee platforms (Polymarket + Kalshi)
- You can navigate geographic restrictions legally
- Spreads are >5 cents after fees
- You execute quickly

**Best path forward:**
1. **Backtest with historical data** from Polymarket/Kalshi APIs
2. **Paper trade** for 1-2 months tracking real opportunities
3. **Calculate actual costs:** fees, spreads, timing
4. **Scale up capital** to $500-1000 if backtests show edge
5. **Use Metaculus** to improve forecasting skills (free practice)

**Reality check:** Most profitable arbitrage is done by:
- High-frequency bots
- Traders with $10k+ capital
- People with cross-border access
- Market makers with low/zero fees

With $100 and PredictIt's fees, you're better off learning directional trading or saving for larger capital.

---

## Resources for Further Research

- **Polymarket Docs:** https://docs.polymarket.com
- **Kalshi Fee Schedule:** https://kalshi.com/docs/kalshi-fee-schedule.pdf  
- **PredictIt Terms:** https://www.predictit.org (academic data access)
- **Metaculus:** https://www.metaculus.com (free forecasting practice)

**Next steps:** Access APIs, pull historical data, write Python scripts to identify real arbitrage opportunities over past 6-12 months.
