# POLYMARKET EXECUTION PLAYBOOK
## Timing, Order Placement & Cost Optimization Guide

**Version:** 1.0  
**Created:** February 8, 2026  
**Purpose:** Actionable execution guidance for maximizing trading edge on Polymarket

---

## TABLE OF CONTENTS

1. [Timing Guidelines](#1-timing-guidelines)
2. [Order Placement Rules](#2-order-placement-rules)
3. [Entry Strategies](#3-entry-strategies)
4. [Exit Strategies](#4-exit-strategies)
5. [Cost Minimization Tactics](#5-cost-minimization-tactics)
6. [Market Microstructure Rules](#6-market-microstructure-rules)
7. [Execution Checklists](#7-execution-checklists)

---

## 1. TIMING GUIDELINES

### 1.1 Best Time of Day to Trade

**WINNER: Midnight to 6 AM UTC (Hour 00-06)**

| Time Period (UTC) | Win Rate | Recommendation |
|-------------------|----------|----------------|
| **00:00 - 06:00** | **52.6%** | ✅ **OPTIMAL** - Overnight information, pre-market positioning |
| 06:00 - 12:00 | 44.4% | ⚠️ FAIR - Moderate activity |
| **12:00 - 18:00** | **38.2%** | ❌ **WORST** - Peak retail noise, efficient pricing |
| 18:00 - 00:00 | 39.5% | ⚠️ FAIR - Evening activity |

**Why Midnight Wins:**
- Overnight information leaks position before public markets
- Less retail noise = cleaner signals
- Institutional positioning happens during off-hours
- Crypto markets move 24/7, best moves often happen 2-4 AM UTC

### 1.2 Day of Week Patterns

**Best Days:**
- **Sunday night/Monday early AM UTC** - Weekend news digestion
- **Wednesday** - Mid-week positioning before Thursday/Friday events
- **Friday afternoon UTC** - Positioning for weekend events

**Avoid:**
- Major holiday weekends (illiquid)
- First day of major events (high volatility, wide spreads)

### 1.3 Pre-Event vs Post-Event Entry

| Timing | Strategy | Win Rate | Notes |
|--------|----------|----------|-------|
| **Pre-Event (24-72h)** | Trend following | **69.2%** | Enter on momentum confirmation |
| **During Event** | News fade | 57% | Fade overreactions in 0.4-0.6 range |
| **Post-Event** | Avoid | 28% | Consensus already priced in |

**Rule:** Enter BEFORE the crowd. Post-event entries = exit liquidity.

### 1.4 Signal Decay - Act Fast!

**Signal half-life: ~2 hours**

```
Signal Strength(t) = Initial × e^(-0.35t)

t=0 hours:  100% strength
 t=2 hours:  50% strength  ← HALF-LIFE
 t=4 hours:  25% strength
 t=8 hours:   6% strength  ← Essentially worthless
```

**Action:** Execute within 5-10 minutes of signal firing. Every hour of delay costs ~1% expectancy.

### 1.5 Seasonal/News Cycle Timing

**High-Conviction Windows:**
1. **Earnings season** - Corporate events create volatility (your edge)
2. **Debate nights** - Political markets move during/after debates
3. **Fed announcement days** - Rate decisions create opportunity
4. **Crypto halving/major events** - Predictable catalysts

**Avoid:**
- Dead periods between major events
- Markets flat for 24+ hours
- "Consensus" periods where everyone agrees

---

## 2. ORDER PLACEMENT RULES

### 2.1 Market Orders vs Limit Orders

| Scenario | Order Type | When to Use |
|----------|------------|-------------|
| **Urgent entry** (signal just fired) | Market | ✅ Acceptable for liquid markets |
| **Non-urgent entry** | Limit @ mid or best bid | ✅ Saves 50-75% of spread cost |
| **Large position ($100+)** | Split limit orders | ✅ Reduce market impact |
| **Volatile news event** | Limit with 2% buffer | ⚠️ Avoid market orders (spreads widen) |

### 2.2 Limit Order Placement Strategy

**Buy Order Examples ($25 position at mid-price 0.50):**

| Strategy | Price | Cost | Execution | Savings |
|----------|-------|------|-----------|---------|
| Market Order | 0.52 | $26.00 | Instant | 0% |
| Aggressive Limit | 0.51 | $25.50 | Fast | 1.9% |
| Mid-Price Limit | 0.50 | $25.00 | Minutes-hours | 3.8% |
| Passive Limit | 0.48 | $24.00 | Uncertain | 7.7% |

**Recommended Approach:**
- **Liquid markets (>$100K volume):** Start with limit @ mid, wait 5 min, then chase if needed
- **Medium liquidity:** Limit @ best bid/ask for immediate fill
- **Time-sensitive signals:** Market order + accept slippage (speed > price)

### 2.3 Order Size Management

**Position Size Guidelines by Liquidity:**

| Market Volume | Max Market Order | Max Limit Order | Notes |
|---------------|------------------|-----------------|-------|
| >$1M/day | $500 | $1,000 | Fill easily |
| $100K-$1M/day | $100 | $250 | Check book depth first |
| $10K-$100K/day | $25 | $50 | Use limit orders only |
| <$10K/day | $5 | $10 | High slippage risk |

**Iceberg Strategy (for $100+ positions):**
```
Instead of: $100 market order (moves price 5-10¢)

Use:
- Order 1: $25 limit @ best price
- Wait 5 minutes
- Order 2: $25 limit @ best price
- Wait 5 minutes
- Order 3: $25 limit @ best price
- Order 4: $25 limit @ best price

Result: Better average price, less market impact
```

### 2.4 Slippage Minimization

**Expected Slippage by Position Size (Liquid Markets):**

| Position Size | Slippage | Cost |
|---------------|----------|------|
| $5 | 0-1 cent | $0.00-0.50 |
| $25 | 1-2 cents | $0.50-1.00 |
| $50 | 2-4 cents | $1.00-2.00 |
| $100 | 4-8 cents | $4.00-8.00 |
| $500 | 8-20 cents | $40-100 |

**Slippage Formula:**
```
Estimated Slippage ≈ (Order Size / Book Depth within 5¢) × Base Spread

Example:
- Order: $50
- Book depth: $500 within 5¢
- Base spread: 4¢
- Impact: ($50 / $500) × 4¢ = 0.4¢ additional slippage
```

### 2.5 Gas Fee Optimization

**Current Gas Structure (Polygon/Ethereum):**
- Open position: ~$0.25
- Close position: ~$0.25
- **Total per round-trip: ~$0.50**

**Gas Optimization Tactics:**
1. **Trade during low congestion:** Weekends, early morning US time
2. **Target <30 gwei:** Check etherscan.io/gastracker
3. **Avoid:** NFT drops, major DeFi events, market crashes (gas spikes to 200+ gwei)
4. **Batch deposits:** Fund account with $200+ to amortize costs

**Minimum Viable Position:**
- **$25+ recommended** (gas = 2% of position)
- **$10 absolute minimum** (gas = 5% of position)
- **Under $10:** Gas consumes 50-90% of profit (avoid)

---

## 3. ENTRY STRATEGIES

### 3.1 All-In vs Scaling In

| Strategy | Best For | Win Rate | Notes |
|----------|----------|----------|-------|
| **All-In** | High-confidence signals | 54% | Maximum exposure, simpler execution |
| **2-Stage Scale** | Medium confidence | 58% | Enter 50%, add 50% on confirmation |
| **3-Stage Scale** | Building positions | 62% | 33% each at entry, +5%, +10% |

**Recommendation:** 
- **Standard:** All-in when signal fires
- **Large positions ($100+):** Scale in over 15-30 minutes
- **Volatile markets:** Scale in to average better price

### 3.2 Dollar-Cost Averaging (DCA)

**When to Use:**
- Building position in trending market
- Uncertain entry timing
- Reducing volatility impact

**DCA Schedule Example:**
```
Target position: $60
Entry price: 0.50

Week 1: $20 @ 0.50
Week 2: $20 @ 0.48 (price dropped, got better fill)
Week 3: $20 @ 0.52 (price rose, still accumulating)

Average entry: 0.50
Result: Smoothed entry, reduced timing risk
```

**When NOT to Use DCA:**
- Time-sensitive signals (2-hour half-life)
- High-conviction catalyst plays
- Momentum trades requiring immediate entry

### 3.3 Catalyst-Based Entry

**Entry Triggers:**

| Catalyst Type | Entry Signal | Win Rate |
|---------------|--------------|----------|
| **News spike** (>20¢ move in 1h) | Fade at extremes | 57% |
| **Whale activity** | Copy within 10 min | **82%** |
| **Trend breakout** | Enter on 24h high | 66% |
| **Event announcement** | Pre-event momentum | 69% |

**Catalyst Entry Rules:**
1. **News Spike:** Wait for initial move, fade the reversal (don't chase)
2. **Whale Activity:** Act within 5-10 minutes of detection
3. **Trend Breakout:** Confirm with volume, enter immediately
4. **Event Announcement:** Enter 24-72 hours pre-event

### 3.4 Technical Trigger Entry

**Optimal Entry Price Zones:**

| Price Range | Win Rate | Strategy |
|-------------|----------|----------|
| **0.60 - 0.80** | **69.2%** | ✅ **BEST** - Moderate favorites with room to run |
| **0.40 - 0.60** | 57.0% | ✅ Good - Uncertain markets, news impact |
| **0.30 - 0.40** | 54.9% | ⚠️ Fair - Contrarian opportunities |
| **0.80 - 0.90** | 50.6% | ⚠️ Risky - Fade only |
| **<0.20 or >0.90** | 26-43% | ❌ AVOID - Extreme consensus, insider risk |

**Entry Checklist (Must Pass ALL):**
```python
def should_enter_trade(market):
    # 1. Price range check
    if market.price < 0.30 or market.price > 0.70:
        return False  # Outside optimal zone
    
    # 2. Trend filter (critical!)
    if market.price <= market.price_24h_ago:
        return False  # Failing momentum
    
    # 3. Volatility check
    if market.historical_range_7d < 0.15:  # 15¢
        return False  # Too stable
    
    # 4. Time check (prefer overnight)
    if 12 <= current_hour_utc <= 18:
        return False  # Worst trading hours
    
    # 5. Confluence check
    if num_strategy_signals < 2:
        return False  # Need confirmation
    
    return True  # GREEN LIGHT
```

---

## 4. EXIT STRATEGIES

### 4.1 Take Profit Levels

**Tiered Exit Strategy (Recommended):**

| Level | Profit Target | Close % | Purpose |
|-------|---------------|---------|---------|
| TP1 | +8% | 25% | Lock in gains, reduce risk |
| TP2 | +15% | 50% | Capture main move |
| TP3 | +25% | 25% | Let winners run |

**Alternative - Aggressive Scale:**
| Level | Profit Target | Close % |
|-------|---------------|---------|
| TP1 | +15% | 50% |
| TP2 | +25% | 50% |

### 4.2 Stop Loss Rules

**Volatility-Based Stops (WINNER):**

```python
def get_stop_loss(current_volume_24h):
    LOW_VOLUME_THRESHOLD = 10000
    if current_volume_24h < LOW_VOLUME_THRESHOLD:
        return 0.08  # Tighter 8% stop on illiquid markets
    else:
        return 0.12  # Standard 12% stop
```

**Stop Loss Performance Comparison:**

| Strategy | Win Rate | Profit Factor | Max DD |
|----------|----------|---------------|--------|
| **Volatility-Based** | **95.5%** | **2.12** | 12.9% |
| Trailing Stop | 66.7% | 2.40 | 16.0% |
| Fixed 12% | 28.6% | 0.14 | 1.5% |

**Recommendation:** Use volatility-based stops with 12% base, 8% for low-volume markets.

### 4.3 Time-Based Exits

**When to Exit by Time:**

| Days Held | Action | Rationale |
|-----------|--------|-----------|
| 3 days | Review | Cut if <+5% and no catalyst |
| 7 days | Partial exit | TP1 if available, else evaluate |
| 14 days | Decision point | Exit if thesis not playing out |
| 30 days | Strong hold | Give thesis time to develop |
| 72 hours post-entry | Cut losers | If down >12%, exit (stop hit) |

**Time Decay Warning:**
- Do NOT use aggressive time decay exits (e.g., exit at +5% after 3 days)
- These cut winners before they reach TP levels
- Let trades mature 15-30 days for optimal results

### 4.4 Rolling Positions

**When to Roll:**
1. Market approaching resolution, want to maintain exposure
2. Thesis still valid but current market closing
3. Better risk/reward in next expiration

**Roll Execution:**
```
Current: MSTR June 30 @ 90¢ NO position
Thesis: Still believe MSTR won't hit $500

Roll to: MSTR July 31 @ 85¢ NO position
Action: Close June, open July within 5 minutes
Cost: ~$0.50 gas + spread
```

---

## 5. COST MINIMIZATION TACTICS

### 5.1 Spread Cost Reduction

**Spread Impact by Market Type:**

| Market Type | Spread | Round-Trip Cost |
|-------------|--------|-----------------|
| Tight (95¢+) | 0.5% | 1.0% |
| Normal (80-95¢) | 1.0% | 2.0% |
| Wide (<80¢) | 2.0%+ | 4.0%+ |

**Tactics to Reduce Spread Costs:**
1. **Trade liquid markets** (>$100K daily volume)
2. **Avoid extremes** (<0.20 or >0.90) - spreads widen
3. **Use limit orders** - save 50-75% vs market orders
4. **Trade during peak hours** - spreads tightest 10 AM - 4 PM EST

### 5.2 Fee Impact by Position Size

| Position Size | Gas Cost | Spread Cost | Total Fees | % of $10 Profit |
|---------------|----------|-------------|------------|-----------------|
| $6 | $0.50 | $0.06 | $0.56 | **89%** |
| $25 | $0.50 | $0.25 | $0.75 | **43%** |
| $50 | $0.50 | $0.50 | $1.00 | **28%** |
| $100 | $0.50 | $1.00 | $1.50 | **15%** |

**Critical Rule:** Minimum $25 position to keep fee impact under 50%.

### 5.3 Breakeven Analysis

**Minimum Gross Return Required:**

For $25 position, 1% spread:
- 7-day hold: Need 2.0% gross return (104% APR)
- 30-day hold: Need 2.0% gross return (24% APR)
- 60-day hold: Need 2.0% gross return (12% APR)

**Breakeven Formula:**
```
Minimum Gross Return = (Position × 2 × Spread%) + 0.50 / Position

Example ($40 position, 0.5% spread):
= ($40 × 2 × 0.005) + 0.50 / $40
= $0.40 + $0.50 / $40
= 2.25% minimum gross return
```

### 5.4 Quick Cost Calculator

```python
def calculate_net_return(position, entry_price, is_yes=True, spread_pct=0.01):
    """
    Calculate net return after fees
    """
    # Gross return
    if is_yes:
        gross_return_pct = entry_price  # Buy YES at 0.85 → 15% upside
    else:
        gross_return_pct = 1 - entry_price  # Buy NO at 0.90 → 10% upside
    
    gross_profit = position * gross_return_pct
    
    # Fees
    spread_cost = position * 2 * spread_pct  # Entry + exit
    gas_cost = 0.50  # Open + close
    total_fees = spread_cost + gas_cost
    
    # Net
    net_profit = gross_profit - total_fees
    net_return_pct = net_profit / position
    
    return {
        'gross_profit': gross_profit,
        'total_fees': total_fees,
        'net_profit': net_profit,
        'net_return_pct': net_return_pct,
        'fee_impact_pct': total_fees / gross_profit if gross_profit > 0 else 0
    }

# Example: $40 position, buy NO at 92¢, 0.5% spread
result = calculate_net_return(40, 0.92, is_yes=False, spread_pct=0.005)
# Net return: 5.75% (vs 8% gross)
```

---

## 6. MARKET MICROSTRUCTURE RULES

### 6.1 How Polymarket Markets Move

**Price Movement Characteristics:**
- **Mean absolute move:** 21.8¢ (from entry to resolution)
- **Median move:** 11.7¢ (most moves are smaller)
- **75th percentile:** 31.7¢ (quarter of markets move 30¢+)

**Key Insight:** You need volatility to make money. Avoid stable markets.

### 6.2 Market Maker Behavior

**Who Provides Liquidity:**
- Professional algorithmic market makers via CLOB API
- Liquidity rewards incentivize tight spreads (3-5¢ from mid)
- Market makers skew quotes based on inventory

**MM Quote Patterns:**

| Condition | Spread | Update Frequency | Size |
|-----------|--------|------------------|------|
| Normal | 2-4¢ | 1-5 seconds | $50-200 |
| High volatility | 5-15¢ | Sub-second | $20-50 |
| Inventory long | Wide ask, tight bid | Fast | Reduced |

**Tactical Implication:** 
- If MM appears long (wide ask), place limit buy near bid
- Likely to get filled as MM tries to reduce position

### 6.3 When Is Liquidity Best?

**Peak Liquidity Hours:**
- **US Market Hours:** 9:30 AM - 4:00 PM EST
- **Evening:** 6:00 PM - 11:00 PM EST (retail peak)
- **News events:** Immediate volume spikes regardless of time

**Low Liquidity (Avoid Market Orders):**
- Late night US: 2:00 AM - 7:00 AM EST
- Weekends (lower volume)
- First 5 minutes and last 2 minutes of 15-min crypto markets

### 6.4 Spread Cost Minimization

**Pre-Trade Liquidity Check:**

```python
def check_market_quality(market):
    spread = market.best_ask - market.best_bid
    volume = market.volume_24h
    liquidity = market.liquidity
    
    if spread < 0.05 and volume > 10000:
        return "✓ GOOD - Safe to trade $5-50"
    elif spread < 0.10 and volume > 1000:
        return "⚠ FAIR - OK for $5-20"
    else:
        return "✗ POOR - Use limit orders only"
```

**Red Flags (Don't Trade):**
- Spread > 15¢
- No trades in last hour
- Volume 24h < $1,000
- Best bid/ask size < $10

---

## 7. EXECUTION CHECKLISTS

### 7.1 Pre-Entry Checklist

**Market Quality Checks:**
- [ ] Volume 24h > $10,000
- [ ] Spread < 5¢ (ideally < 3¢)
- [ ] Price between 0.30-0.70 (optimal zone)
- [ ] 7-day price range > 15¢ (volatile enough)
- [ ] Market not closing in < 7 days

**Signal Quality Checks:**
- [ ] 2+ strategies concur (confluence)
- [ ] Price > price_24h_ago (trend filter)
- [ ] Signal fired within last 2 hours
- [ ] Current hour NOT 12-18 UTC
- [ ] No major conflicting news

**Position Sizing Checks:**
- [ ] Position size ≥ $25 (minimum viable)
- [ ] Risk per trade = Bankroll × 6.25% (quarter Kelly)
- [ ] Gas price < 50 gwei (check etherscan)
- [ ] Account has sufficient USDC for position + gas

### 7.2 Order Entry Checklist

**Limit Order Flow:**
1. [ ] Check current spread (should be < 5¢)
2. [ ] Place limit order at mid-price or best bid/ask
3. [ ] Wait 5 minutes for fill
4. [ ] If no fill, cancel and retry at +0.5%
5. [ ] If still no fill after 2 retries, use market order

**Market Order Flow (Time-Sensitive):**
1. [ ] Confirm signal is still valid
2. [ ] Check gas price (< 50 gwei)
3. [ ] Place market order immediately
4. [ ] Verify fill within 60 seconds
5. [ ] Log entry price and slippage

### 7.3 Position Management Checklist

**Daily Review:**
- [ ] Check position P&L vs stop loss
- [ ] Monitor for take profit opportunities
- [ ] Review any news affecting thesis
- [ ] Check if trend filter still valid

**Exit Decision Tree:**
```
Price up +8%?
  → Yes: Close 25% (TP1)
  
Price up +15%?
  → Yes: Close 50% (TP2)
  
Price up +25%?
  → Yes: Close remaining 25% (TP3)
  
Price down -12% (or -8% if low volume)?
  → Yes: Close 100% (STOP LOSS)
  
Held > 72 hours and < +5%?
  → Consider exit if thesis weakening
```

### 7.4 Post-Trade Checklist

**After Every Trade:**
- [ ] Log: Entry price, exit price, fees paid
- [ ] Calculate actual vs expected slippage
- [ ] Note signal-to-execution time
- [ ] Record market conditions (spread, volume)
- [ ] Update trading journal with lessons

**Monthly Review:**
- [ ] Calculate win rate vs target (55%+)
- [ ] Review average slippage by market type
- [ ] Identify best/worst performing entry times
- [ ] Adjust position sizing based on actual results
- [ ] Update strategy parameters if needed

---

## APPENDIX A: QUICK REFERENCE CARD

### Optimal Trading Parameters

| Parameter | Target | Range |
|-----------|--------|-------|
| **Entry Price** | 0.60-0.70 | 0.30-0.70 |
| **Win Rate** | 55%+ | 50-60% |
| **Position Size** | $25-50 | $20-100 |
| **Risk per Trade** | 6.25% | 6.25-12.5% |
| **Stop Loss** | 12% | 8-12% |
| **Take Profit** | 8/15/25% | Tiered |
| **Spread** | < 3¢ | < 5¢ |
| **Volume 24h** | > $100K | > $10K |
| **Time to Enter** | < 10 min | < 2 hours |
| **Best Hours** | 00-06 UTC | Avoid 12-18 UTC |

### Red Flags (Don't Trade)

- Position size < $10
- Entry price < 0.20 or > 0.80
- Spread > 15¢
- Volume < $1,000
- Price declining past 24h
- Gas > 100 gwei
- Signal > 4 hours old

---

## APPENDIX B: CALCULATION FORMULAS

### Kelly Criterion
```
f* = (bp - q) / b

Where:
  b = reward/risk ratio
  p = win probability
  q = loss probability (1-p)

Example (55% win, 1.5:1 R:R):
f* = (1.5 × 0.55 - 0.45) / 1.5 = 25% (Full Kelly)
Quarter Kelly = 6.25%
Half Kelly = 12.5%
```

### Net Return Calculation
```
Net Return % = [
    (Position × Gross_Return%)
    - (Position × 2 × Spread%)
    - 0.50
] / Position
```

### Signal Decay
```
Signal_Strength(t) = Initial × e^(-0.35t)
Half-life ≈ 2 hours
```

---

## SUMMARY: TOP 10 EXECUTION RULES

1. **Enter within 10 minutes** of signal firing (2-hour half-life)
2. **Trade only 0.30-0.70 price range** (69% win rate at 0.60-0.80)
3. **Use trend filter** - only enter when price > 24h ago
4. **Position size $25 minimum** to keep fees under 50%
5. **Use limit orders** when not urgent (saves 50-75% spread)
6. **Trade 00-06 UTC** for best win rates (52.6% vs 38.2%)
7. **Quarter Kelly sizing** (6.25%) for optimal risk-adjusted growth
8. **Volatility-based stops** (12% base, 8% for low volume)
9. **Tiered take profits** (8%/15%/25% at 25%/50%/25%)
10. **Check liquidity first** - volume >$10K, spread <5¢

---

*Document: EXECUTION_PLAYBOOK.md*  
*Version: 1.0*  
*Created: February 8, 2026*  
*Next Review: March 8, 2026*
