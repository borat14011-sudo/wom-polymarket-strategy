# Polymarket Market Making Strategy

## Executive Summary

Market making on Polymarket involves providing two-sided liquidity (buy and sell orders) to earn spreads while staying delta-neutral. Unlike directional betting, you profit from the bid-ask spread rather than predicting outcomes.

**Key Finding:** Polymarket DOES pay liquidity rewards, making market making potentially profitable even for small accounts, though challenges exist at the $100 scale.

---

## How Polymarket Market Making Works

### Basic Concept
- **Place limit orders on BOTH sides** of a market
  - Example: Buy at 48%, Sell at 52% (4% spread)
- **Earn the spread** when both sides fill
- **Stay delta-neutral** by balancing YES and NO positions
- Orders execute when other traders take your price

### Market Structure
- **Central Limit Order Book (CLOB)** - peer-to-peer trading
- **Binary outcomes** - YES/NO shares priced 0.00 to 1.00 USDC
- **Each pair fully collateralized** - YES + NO shares = $1.00 USDC
- **No trading fees** on most markets (maker-friendly!)
- **15-minute crypto markets** have taker fees but pay maker rebates

---

## Liquidity Rewards Program

### Overview
Polymarket pays **daily USDC rewards** to liquidity providers who post competitive limit orders. This is a game-changer for market makers.

### How Rewards Work

**Paid daily at midnight UTC** directly to your wallet

**Eligibility criteria:**
- Must post limit orders (not market orders)
- Orders must be within **max spread** from midpoint (typically 3 cents)
- Must meet **minimum size requirement** (varies by market)
- Minimum payout threshold: **$1.00** (below this, no payment)

**Reward factors:**
1. **Proximity to mid-price** - tighter spreads earn more
2. **Order size** - larger orders earn proportionally more
3. **Two-sided quoting** - balanced bids and asks earn bonus multiplier
4. **Consistency** - sampled every minute, rewards accumulate daily

### Reward Formula (Technical)

Based on dYdX's liquidity provider model with adaptations for binary markets:

```
S(v,s) = ((v-s)/v)^2 * b

Where:
- v = max spread from midpoint (e.g., 3 cents)
- s = your actual spread from midpoint
- b = bin-game multiplier for two-sided liquidity
```

**Key insight:** Quadratic scoring means 1¢ from mid earns ~4x more than 2¢ from mid.

**Two-sided boost:** Scoring takes the minimum of your YES-side and NO-side scores, multiplied. Single-sided orders earn reduced rewards (divided by 3).

**Example scoring:**
- 100 shares @ 49¢ bid (mid = 50¢, spread = 1¢, max = 3¢)
- 100 shares @ 51¢ ask (spread = 1¢)
- Score: ((3-1)/3)^2 * 100 = 44.4 points per side
- Two-sided multiplier applied

---

## Maker Rebates Program (15-Min Crypto Markets)

**Separate from liquidity rewards**, applies only to fast-moving crypto markets.

### Structure
- **20% of taker fees** redistributed to makers
- **Paid daily in USDC**
- **Performance-based** - proportional to liquidity provided

### Taker Fee Schedule
Fees vary by price (highest at 50% probability):

| Price | Trade Value (100 shares) | Fee | Effective Rate |
|-------|-------------------------|-----|----------------|
| $0.10 | $10 | $0.02 | 0.20% |
| $0.25 | $25 | $0.22 | 0.88% |
| $0.40 | $40 | $0.58 | 1.44% |
| **$0.50** | **$50** | **$0.78** | **1.56% (max)** |
| $0.60 | $60 | $0.86 | 1.44% |
| $0.75 | $75 | $0.66 | 0.88% |
| $0.90 | $90 | $0.18 | 0.20% |

**Note:** Most Polymarket markets are **fee-free**. Maker rebates only apply to 15-minute crypto markets.

---

## Typical Spreads on Polymarket

### Observed Spread Characteristics
- **Max reward spread:** 3 cents (typical configuration)
- **Competitive spreads:** 1-2 cents in liquid markets
- **Wide spreads:** 5-10+ cents in illiquid/new markets

### Spread Dynamics
- **High-volume markets** (politics, major sports): 0.5-2¢ spreads
- **Medium-volume markets:** 2-4¢ spreads
- **Low-volume markets:** 5-15¢ spreads
- **Near extremes** (prices <10¢ or >90¢): wider absolute spreads

### Your 4% Spread Strategy
A 4-cent spread (48% bid / 52% ask) is:
- **Competitive** for medium-volume markets
- **Wide** for high-volume markets (you'll earn more rewards with tighter spreads)
- **Narrow** for low-volume markets (higher risk of adverse selection)

---

## Viability for Small Accounts ($100)

### Capital Allocation Model

**Starting capital:** $100 USDC

**Strategy:** Allocate across multiple markets to diversify risk

**Example allocation:**
- 5 markets × $20 per market
- Each market: $10 bid side + $10 ask side
- Or 2-3 markets × $30-50 for more size per market

### Expected Returns Calculation

**Scenario 1: Spread Capture**
- Capital per market: $20 (10 bids + 10 asks)
- Spread: 4 cents (0.04 USDC per share)
- Fill rate: Assume 50% of orders fill per day
- Shares traded: ~20 shares/day (conservative)
- Gross spread profit: 20 × $0.04 = **$0.80/day**
- Monthly: **$24**
- **ROI: 24% per month** (if you can maintain delta-neutral)

**Scenario 2: Liquidity Rewards**
- Order size: 20-40 shares per side
- Spread: 1-2 cents from mid
- Conservative estimate: $0.50-$2.00/day per market
- 3 markets: **$1.50-$6.00/day**
- Monthly: **$45-$180**
- **ROI: 45-180% per month**

**Combined potential:** $3-8/day = $90-240/month on $100 capital

### Challenges for Small Accounts

**1. Minimum payout threshold**
- Need to earn at least $1/day to receive rewards
- Requires meaningful size and tight spreads
- May need to concentrate on 1-2 high-reward markets

**2. Limited diversification**
- $100 spread thin = higher risk
- Adverse selection risk if stuck with losing side
- Need to actively manage inventory

**3. Capital efficiency**
- Larger accounts can spread tighter and still earn rewards
- Compete with sophisticated bots and market makers
- Your 4¢ spread may not be competitive enough

**4. Gas and bridge costs**
- Depositing to Polygon has small costs
- Need to maintain profitability above transaction costs
- Consider batch operations

**5. Inventory risk**
- If market moves against you, can lose more than spread
- Example: Buy at 48¢, market crashes to 20¢ = -$0.28/share loss
- Need tools to merge/split tokens to rebalance

### Risk Management for $100 Account

**Key strategies:**
1. **Monitor positions actively** - can't set and forget
2. **Choose stable markets** - avoid volatile/breaking news markets
3. **Tight stop-loss** - close positions if market moves >5-10¢
4. **Focus on 2-3 markets max** - enough size to earn rewards
5. **Use two-sided scoring** - always quote both sides for reward boost

---

## Practical Strategy for $100 Capital

### Recommended Approach

**Phase 1: Learning (Week 1-2)**
- Start with **1 market, $50 deployed**
- Choose a **stable, medium-volume market** (not breaking news)
- Place orders: 25 shares bid, 25 shares ask
- Spread: **2-3 cents** from midpoint
- Goal: Learn the system, earn first rewards
- Expected: $1-3/day

**Phase 2: Optimization (Week 3-4)**
- Expand to **2-3 markets, $90-100 deployed**
- Tighten spreads to **1.5-2.5 cents** where competitive
- Monitor which markets have best reward-to-risk ratio
- Adjust allocation based on performance
- Expected: $3-7/day

**Phase 3: Scale (Month 2+)**
- Reinvest profits to grow capital to $150-200
- Improved capital efficiency
- Can spread wider diversification
- Better risk management with more size
- Expected: $5-15/day on larger capital

### Market Selection Criteria

**Good markets for small MM:**
1. **Steady trading volume** - daily volume $50k-$500k
2. **Not headline-driven** - avoid breaking news markets
3. **Medium probability** - 30-70% range (avoid extremes)
4. **Liquidity rewards enabled** - check rewards page
5. **Stable spreads** - 2-5 cent typical spread

**Avoid:**
- Breaking news / volatile events
- Very low volume (<$10k/day)
- Extreme probabilities (<15% or >85%)
- Short-duration markets (closing within 24h)

### Tools Needed

**Minimum viable setup:**
1. **Manual trading** via Polymarket UI
   - Check rewards page: polymarket.com/rewards
   - Monitor order book
   - Place limit orders manually
   - Cost: Free

2. **Spreadsheet for tracking**
   - Daily P&L
   - Positions by market
   - Reward earnings
   - Cost: Free

**Advanced (optional):**
- **API access** for automated quoting
- **Python/JavaScript bot** for order management
- **WebSocket feed** for real-time data
- **Inventory management scripts** for rebalancing

---

## Expected Returns vs. Risk

### Base Case (Conservative)
- Capital: $100
- Daily gross: $2-4 (spread + rewards)
- Monthly: $60-120
- **ROI: 60-120% per month**
- **Risk: Medium** (inventory risk, adverse selection)

### Upside Case (Optimal Execution)
- Capital: $100
- Daily gross: $5-8
- Monthly: $150-240
- **ROI: 150-240% per month**
- **Risk: Medium-High** (requires tight spreads, more fills)

### Downside Case (Adverse Events)
- Market moves 10-20¢ against your inventory
- Loss: $10-40
- **Wipeout risk: 10-40% of capital**
- **Mitigation: Stop-loss, active monitoring**

### Risk Factors

**1. Adverse selection**
- Informed traders may take your orders before big moves
- You end up holding the wrong side
- Mitigation: Avoid breaking news markets, wider spreads

**2. Inventory risk**
- Delta exposure if positions don't balance
- Market movement can cause losses exceeding spread
- Mitigation: Actively rebalance, close positions

**3. Competition**
- Sophisticated bots with faster execution
- Larger accounts can offer tighter spreads
- Mitigation: Focus on less competitive markets

**4. Reward uncertainty**
- Scoring is complex and relative to other MMs
- No guarantee of minimum daily reward
- Mitigation: Monitor rewards dashboard, adjust strategy

**5. Smart money risk**
- Prediction markets attract informed traders
- You may be the counterparty to "smart money"
- Mitigation: Wide enough spreads to compensate

---

## Key Insights & Recommendations

### ✅ Pros of Market Making with $100

1. **Liquidity rewards exist** - significant additional income beyond spreads
2. **No maker fees** - entire spread is profit (on most markets)
3. **Two-sided boost** - 3x multiplier for balanced quoting
4. **Daily payouts** - quick feedback and compounding
5. **Low barriers** - can start with just $100

### ⚠️ Challenges

1. **$1 minimum payout** - need meaningful size to clear threshold
2. **Competition** - bots and large MMs dominate tight spreads
3. **Inventory risk** - losses can exceed spread profits
4. **Capital inefficiency** - $100 is on the small side
5. **Time commitment** - manual management is labor-intensive

### 🎯 Verdict on $100 Account

**Viable but challenging.**

- **Best fit:** Learning and testing the strategy
- **Realistic expectation:** $40-100/month with active management
- **Path to scale:** Reinvest profits to reach $200-500 capital
- **Time investment:** 1-2 hours/day monitoring and adjusting
- **Risk level:** Medium - can lose 10-40% in adverse scenarios

**Recommendation:** Start with $50-100 as a learning account. Focus on 1-2 stable markets, earn consistent rewards, and scale up as you gain experience and capital.

---

## Next Steps

### Immediate Actions

1. **Review current markets** at polymarket.com/rewards
   - Identify which markets have active liquidity rewards
   - Check reward amounts and max spreads

2. **Fund your account**
   - Deposit $100 USDC to Polygon via bridge
   - Set token approvals for CLOB trading

3. **Select 1-2 starter markets**
   - Medium volume, stable, rewards-enabled
   - Avoid breaking news

4. **Place initial orders**
   - 2-3 cent spread from midpoint
   - 20-40 shares per side
   - Monitor for 24 hours

5. **Track performance**
   - Spreadsheet with daily P&L
   - Monitor rewards dashboard
   - Adjust spreads based on fills and rewards

### Further Research

1. **Study reward calculations** in detail
   - Understand scoring formula
   - Optimize for two-sided boost
   - Model different spread scenarios

2. **Analyze market microstructure**
   - Which markets have best spreads?
   - What times have most liquidity?
   - Who are the competing market makers?

3. **Build tools**
   - Simple Python script for order placement
   - Spreadsheet for position tracking
   - Alert system for large price moves

4. **Risk management**
   - Define max loss per market
   - Set stop-loss triggers
   - Plan for inventory rebalancing

---

## Resources

- **Polymarket Rewards Dashboard:** https://polymarket.com/rewards
- **Liquidity Rewards Docs:** https://docs.polymarket.com/polymarket-learn/trading/liquidity-rewards
- **Market Maker Guide:** https://docs.polymarket.com/developers/market-makers/introduction
- **Maker Rebates Program:** https://docs.polymarket.com/polymarket-learn/trading/maker-rebates-program
- **API Documentation:** https://docs.polymarket.com/
- **CLOB Quickstart:** https://docs.polymarket.com/developers/CLOB/quickstart

---

## Conclusion

Market making on Polymarket is a **viable strategy for small accounts**, especially with liquidity rewards. A $100 account can realistically earn $40-120/month with:

- **Active management** (1-2 hours/day)
- **Smart market selection** (stable, medium-volume)
- **Tight spreads** (1-3 cents to compete for rewards)
- **Two-sided quoting** (maximize reward multiplier)
- **Risk control** (avoid breaking news, set stop-losses)

The key is treating this as a **learning phase** to build experience and capital. As you grow to $200-500, capital efficiency improves significantly, and you can diversify across more markets.

**Start small, learn fast, scale smart.**

---

*Last updated: 2026-02-07*
*Strategy research by OpenClaw subagent*
