# Polymarket Fee Analysis & Implementation Guide

**Document Purpose:** Detailed fee modeling for prediction market arbitrage trades with exact calculations for position sizing, costs, and returns.

**Last Updated:** 2026-02-08

---

## 1. POLYMARKET FEE STRUCTURE

### 1.1 Spread Cost (Implicit)

The spread is the difference between buy and sell prices. When you buy into a market, you pay the ask; when you sell, you receive the bid. This "round-trip" friction erodes returns.

| Market Type | Price Range | Spread Cost |
|-------------|-------------|-------------|
| Tight Markets | 98¢+ | 0.2% - 0.5% |
| Normal Markets | 80¢ - 95¢ | 0.5% - 1.0% |
| Wide Markets | <80¢ | 1.0% - 2.0% |

**Note:** Spread costs apply to both entry AND exit. A 0.75% spread means ~0.375% on entry and ~0.375% on exit.

### 1.2 Gas Fees (Ethereum Mainnet)

| Transaction Type | Cost (USD) | Frequency |
|------------------|------------|-----------|
| Initial Deposit | $2.00 - $5.00 | One-time per funding cycle |
| Per Trade (Open) | ~$0.25 | Every position entry |
| Per Trade (Close) | ~$0.25 | Every position exit |
| Amortized per Round-Trip | ~$0.50 | Combined open + close |
| Withdrawal | $2.00 - $5.00 | One-time per exit cycle |

### 1.3 Explicit Trading Fees

**Polymarket charges 0% maker/taker fees.** No additional platform fees apply beyond spread and gas.

---

## 2. TRADE-BY-TRADE FEE CALCULATIONS

### TRADE #1: MSTR Jun 30 Binary

**Market Conditions:**
- Market: "Will MicroStrategy (MSTR) close above $500 by June 30?"
- Position Direction: Buy NO (betting MSTR will NOT close above $500)
- Position Size: $6.00
- Entry Price: 90.5¢ ($0.905 per share)
- Exit Price: $1.00 (if NO wins)
- Market Type: Normal (80-95¢ range) → **1.0% spread cost assumed**

**Position Sizing:**
```
Shares purchased = Position Size / Entry Price
                 = $6.00 / $0.905
                 = 6.6298 shares
```

**Gross Profit Calculation:**
```
If NO wins (position resolves to $1.00):
Gross payout = 6.6298 shares × $1.00 = $6.63
Gross profit = $6.63 - $6.00 = $0.63
Gross return = $0.63 / $6.00 = 10.5%
```

**Fee Deductions:**

| Fee Type | Calculation | Amount |
|----------|-------------|--------|
| Spread Cost (entry) | $6.00 × 0.5% | $0.030 |
| Spread Cost (exit) | $6.63 × 0.5% | $0.033 |
| **Total Spread** | | **$0.063** |
| Gas (open position) | Flat per tx | $0.25 |
| Gas (close position) | Flat per tx | $0.25 |
| **Total Gas** | | **$0.50** |
| **TOTAL FEES** | | **$0.563** |

**Net Profit Calculation:**
```
Gross expected profit:     $0.630
Less: Total spread cost:  -$0.063
Less: Total gas fees:     -$0.500
-----------------------------
NET EXPECTED PROFIT:       $0.067

Net Return %: $0.067 / $6.00 = 1.12%

Time to expiration: ~40 days
Net IRR (annualized): 1.12% × (365/40) = 10.2%
```

**Fee Impact Analysis:**
- Fees consume: $0.563 / $0.630 = **89.4% of gross profit**
- This is a HIGH FEE IMPACT trade due to small position size

---

### TRADE #2: BTC Halving Prediction

**Market Conditions:**
- Market: "Will BTC halving occur before April 15, 2024?"
- Position Direction: Buy YES (halving will occur)
- Position Size: $25.00
- Entry Price: 94.0¢ ($0.94 per share)
- Exit Price: $1.00 (if YES wins)
- Market Type: Tight (95¢+ range) → **0.5% spread cost assumed**

**Position Sizing:**
```
Shares purchased = $25.00 / $0.94 = 26.5957 shares
```

**Gross Profit Calculation:**
```
If YES wins:
Gross payout = 26.5957 shares × $1.00 = $26.60
Gross profit = $26.60 - $25.00 = $1.60
Gross return = $1.60 / $25.00 = 6.4%
```

**Fee Deductions:**

| Fee Type | Calculation | Amount |
|----------|-------------|--------|
| Spread Cost (entry) | $25.00 × 0.25% | $0.063 |
| Spread Cost (exit) | $26.60 × 0.25% | $0.067 |
| **Total Spread** | | **$0.130** |
| Gas (open position) | Flat per tx | $0.25 |
| Gas (close position) | Flat per tx | $0.25 |
| **Total Gas** | | **$0.50** |
| **TOTAL FEES** | | **$0.630** |

**Net Profit Calculation:**
```
Gross expected profit:     $1.600
Less: Total spread cost:  -$0.130
Less: Total gas fees:     -$0.500
-----------------------------
NET EXPECTED PROFIT:       $0.970

Net Return %: $0.970 / $25.00 = 3.88%

Time to expiration: ~60 days
Net IRR (annualized): 3.88% × (365/60) = 23.6%
```

**Fee Impact Analysis:**
- Fees consume: $0.630 / $1.600 = **39.4% of gross profit**
- Moderate fee impact; gas is the larger concern

---

### TRADE #3: Fed Rate Decision

**Market Conditions:**
- Market: "Will Fed raise rates at March meeting?"
- Position Direction: Buy NO (rates will not be raised)
- Position Size: $100.00
- Entry Price: 85.0¢ ($0.85 per share)
- Exit Price: $1.00 (if NO wins)
- Market Type: Normal (80-95¢ range) → **1.0% spread cost assumed**

**Position Sizing:**
```
Shares purchased = $100.00 / $0.85 = 117.6471 shares
```

**Gross Profit Calculation:**
```
If NO wins:
Gross payout = 117.6471 shares × $1.00 = $117.65
Gross profit = $117.65 - $100.00 = $17.65
Gross return = $17.65 / $100.00 = 17.65%
```

**Fee Deductions:**

| Fee Type | Calculation | Amount |
|----------|-------------|--------|
| Spread Cost (entry) | $100.00 × 0.5% | $0.500 |
| Spread Cost (exit) | $117.65 × 0.5% | $0.588 |
| **Total Spread** | | **$1.088** |
| Gas (open position) | Flat per tx | $0.25 |
| Gas (close position) | Flat per tx | $0.25 |
| **Total Gas** | | **$0.50** |
| **TOTAL FEES** | | **$1.588** |

**Net Profit Calculation:**
```
Gross expected profit:     $17.650
Less: Total spread cost:  -$1.088
Less: Total gas fees:     -$0.500
-----------------------------
NET EXPECTED PROFIT:      $16.062

Net Return %: $16.062 / $100.00 = 16.06%

Time to expiration: ~30 days
Net IRR (annualized): 16.06% × (365/30) = 195.4%
```

**Fee Impact Analysis:**
- Fees consume: $1.588 / $17.650 = **9.0% of gross profit**
- Low fee impact; gas becomes negligible at scale

---

## 3. FEE IMPACT SUMMARY TABLE

| Trade | Position | Gross Profit | Total Fees | Net Profit | Fee % of Profit | Net Return | Net IRR |
|-------|----------|--------------|------------|------------|-----------------|------------|---------|
| MSTR Jun 30 | $6.00 | $0.63 | $0.563 | $0.067 | **89.4%** | 1.12% | 10.2% |
| BTC Halving | $25.00 | $1.60 | $0.630 | $0.970 | **39.4%** | 3.88% | 23.6% |
| Fed Rate Decision | $100.00 | $17.65 | $1.588 | $16.062 | **9.0%** | 16.06% | 195.4% |

### Key Insights:

1. **Position Size Criticality:** Small positions (<$10) suffer catastrophic fee drag. Gas fees alone can consume 50-90% of expected profit.

2. **Gas as Fixed Cost:** Gas costs are relatively fixed regardless of position size. A $0.50 gas fee on a $6 trade is 8.3% of principal; on a $100 trade it's 0.5%.

3. **Spread Scales Linearly:** Spread costs scale with position size, making them predictable percentage-wise but still material in wide markets.

4. **Minimum Viable Position:** Based on this analysis, minimum position size should be **$20+** to keep fee impact below 50% of gross profit.

---

## 4. BREAKEVEN ANALYSIS

### 4.1 Minimum Position Size by Expected Return

Assuming 1% spread cost + $0.50 gas, what position size is needed to achieve various net returns?

| Target Net Return | Required Gross Return | Min Position Size | Rationale |
|-------------------|----------------------|-------------------|-----------|
| 0% (breakeven) | 1.5% | ~$35 | Fees = expected profit |
| 2% net | 3.5% | ~$20 | Reasonable risk/reward |
| 5% net | 6.5% | ~$12 | Higher return hurdle |
| 10% net | 11.5% | ~$6 | Very high expectation needed |

### 4.2 Breakeven by Time Horizon

For a $25 position with 1% spread cost:

| Time to Expiration | Min Gross Return Needed | Equivalent APR |
|--------------------|-------------------------|----------------|
| 7 days | 2.0% | 104% APR |
| 30 days | 2.0% | 24% APR |
| 60 days | 2.0% | 12% APR |
| 90 days | 2.0% | 8% APR |

**Takeaway:** Short-term trades require exceptionally high conviction to overcome fixed gas costs.

### 4.3 Spread Sensitivity

For a $50 position held for 30 days with $0.50 gas:

| Spread Cost | Total Fees | Min Gross Return | Break-even APR |
|-------------|------------|------------------|----------------|
| 0.5% (tight) | $1.00 | 2.0% | 24% APR |
| 1.0% (normal) | $1.50 | 3.0% | 36% APR |
| 2.0% (wide) | $2.50 | 5.0% | 60% APR |

**Takeaway:** Wide spreads (>1.5%) make most trades uneconomical unless holding period is long or gross edge is very high.

---

## 5. RECOMMENDATIONS FOR MINIMIZING FEES

### 5.1 Position Sizing Strategy

**✅ DO:**
- **Minimum $25 per trade** - Keeps gas fees under 2% of principal
- **Batch deposits** - Fund account with $200+ to amortize deposit gas across multiple trades
- **Batch withdrawals** - Exit multiple positions before withdrawing to reduce withdrawal gas impact

**❌ DON'T:**
- Trade positions under $10 (unless extraordinary edge)
- Deposit/withdraw for single small trades
- Spread capital across many tiny positions

### 5.2 Timing Optimization

**Gas Price Awareness:**
- Monitor Ethereum gas prices at [etherscan.io/gastracker](https://etherscan.io/gastracker)
- Trade during low-congestion periods (weekends, early morning US time)
- Target gas price: <30 gwei for standard transactions

**High Gas Avoidance:**
- Avoid trading during: NFT drops, major DeFi events, market crashes
- Gas can spike to 200+ gwei, making small trades impossible

### 5.3 Market Selection

**Spread Optimization:**
- Prefer markets with tight spreads (95¢+ = 0.5% cost)
- Avoid markets <80¢ unless holding long-term (>60 days)
- Check order book depth before entering large positions

**Liquidity Priority:**
- High-volume markets (BTC, ETH, political events) have tighter spreads
- Obscure markets often have 2%+ spreads, making arbitrage difficult

### 5.4 Holding Period Strategy

**Fee Amortization:**
- Longer holds = lower annualized gas impact
- A 90-day hold amortizes gas over more time than a 7-day hold
- But: Time = uncertainty; balance fee savings vs. event risk

**Sweet Spot:**
- 30-60 day expirations offer good balance of fee amortization and event predictability

### 5.5 Alternative Approaches

**Layer 2 Considerations:**
- Polymarket currently runs on Polygon for settlement (lower gas)
- Deposit/withdrawal still requires Ethereum mainnet
- Monitor for future Layer 2 integrations that could reduce costs further

**Portfolio Approach:**
- Maintain $200-500 minimum account balance
- Run 4-10 concurrent positions to maximize capital efficiency
- Single deposit/withdrawal cycle per quarter

---

## 6. QUICK CALCULATOR FORMULA

Use this formula for rapid trade evaluation:

```
Net Return % = [
    (Position × Gross_Return%) 
    - (Position × 2 × Spread%) 
    - 0.50
] / Position

Where:
- Position = Dollar amount invested
- Gross_Return% = (1 - Entry_Price) if buying NO, or Entry_Price if buying YES
- Spread% = 0.005 (0.5%), 0.01 (1.0%), or 0.02 (2.0%)
- 0.50 = Total gas cost (open + close)
```

### Example Calculation:
```
Position: $40
Entry: 92¢ (buy NO, expecting $1.00)
Spread: 0.5% (tight market)

Gross_Return% = 1 - 0.92 = 8%

Net Return % = [
    ($40 × 0.08) 
    - ($40 × 2 × 0.005) 
    - 0.50
] / $40

= [$3.20 - $0.40 - $0.50] / $40
= $2.30 / $40
= 5.75%

If 45 days to expiration:
Net IRR = 5.75% × (365/45) = 46.6% APR
```

---

## 7. RED FLAGS - AVOID THESE TRADES

| Red Flag | Why It Matters | Threshold |
|----------|----------------|-----------|
| Position <$10 | Gas consumes >50% of profit | Hard minimum: $15 |
| Spread >2% | Entry/exit friction too high | Avoid wide markets |
| Expiration <7 days | Can't amortize gas costs | Minimum 14 days |
| Gas >100 gwei | Transaction costs explode | Wait for <50 gwei |
| Gross edge <2% | Fees make it unprofitable | Minimum 3% gross |

---

## 8. CONCLUSION

Polymarket's 0% trading fees are attractive, but **gas fees and spread costs significantly impact small positions.** The key to profitability is:

1. **Scale matters:** Trade $25+ per position
2. **Batch operations:** Amortize deposit/withdrawal gas
3. **Choose tight markets:** <1% spread when possible
4. **Mind the gas:** Trade during low-congestion periods
5. **Hold longer:** 30-60 days optimizes fee amortization vs. uncertainty

**The Math is Clear:** A $6 position loses 89% of profit to fees. A $100 position loses only 9%. Size appropriately or stay out.

---

*Document Version: 1.0*  
*Created: 2026-02-08*  
*Applies to: Polymarket via Ethereum/Polygon*
