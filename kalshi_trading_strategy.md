# Kalshi Trading Strategy - Quick Reference

## TL;DR - The Fee Advantage Rule

```
IF price > 74¢ OR price < 26¢:
    → TRADE ON KALSHI (lower fees)
    
ELSE (26-74¢):
    → TRADE ON POLYMARKET (lower fees)
```

---

## Fee Comparison At-A-Glance

| Platform | Fee Structure | Best For |
|----------|---------------|----------|
| **Kalshi** | Quadratic: 0.07% × price × (100-price) × 2 | Extreme probabilities |
| **Polymarket** | Flat: 4% roundtrip | Mid-range probabilities |

---

## Sweet Spots

### 🎯 KALSHI OPTIMAL ZONES

**85-95¢ range (HIGH PROBABILITY):**
- Roundtrip fee: 1.4-2.0%
- **2.6% fee advantage over Polymarket**
- Required win rate: 91-97% (vs 93-99% on Polymarket)

**5-15¢ range (LOW PROBABILITY):**
- Roundtrip fee: 1.8-2.0%
- **2.2% fee advantage over Polymarket**
- Required win rate: 5-17% (vs 5-16% on Polymarket)

### ⚠️ AVOID ON KALSHI

**45-55¢ range:**
- Roundtrip fee: 7%
- **3% fee DISADVANTAGE vs Polymarket**
- Use Polymarket instead

---

## Break-Even Win Rates

| Entry Price | Kalshi Required | Polymarket Required | Kalshi Advantage |
|-------------|-----------------|---------------------|------------------|
| 90¢ | **91.3%** | 93.6% | ✅ -2.3% |
| 75¢ | **77.6%** | 78.0% | ✅ -0.4% |
| 50¢ | **53.5%** | 52.0% | ❌ +1.5% |
| 25¢ | **27.6%** | 26.0% | ❌ +1.6% |
| 10¢ | **11.3%** | 10.4% | ❌ +0.9% |

*Lower is better - Kalshi has advantage at 75¢+*

---

## Decision Tree

```
1. Find market opportunity
   ↓
2. Check current price
   ↓
3. Is price > 74¢?
   ├─ YES → Use Kalshi (save ~2-3% in fees)
   ├─ NO → Is price < 26¢?
   │       ├─ YES → Use Kalshi (save ~2-3% in fees)
   │       └─ NO → Use Polymarket (save ~3-6% in fees)
   └─
4. Calculate required edge
   ↓
5. Execute if edge > fees
```

---

## Position Sizing Examples

### Scenario 1: High Probability Event (90¢)
**$1000 position**

| Platform | Fee Cost | Net Profit (if wins) |
|----------|----------|---------------------|
| **Kalshi** | ~$14 | $86 |
| Polymarket | ~$40 | $60 |

**Advantage:** +$26 using Kalshi ✅

### Scenario 2: Coin Flip (50¢)
**$1000 position**

| Platform | Fee Cost | Net Profit (if wins) |
|----------|----------|---------------------|
| Kalshi | ~$35 | $465 |
| **Polymarket** | ~$40 | $460 |

**Advantage:** +$5 using Polymarket (marginal)

### Scenario 3: High Volume Trading
**100 trades/month at various prices**

- **Strategy A:** Use only Kalshi
  - Average fee: ~4-5%
  - Total cost: High variance

- **Strategy B:** Price-based platform selection
  - Use Kalshi for >74¢ and <26¢
  - Use Polymarket for 26-74¢
  - **Average savings: ~15-20% on fee costs**

---

## Edge Requirements by Price Zone

### What edge do you need to be profitable?

| Price | Kalshi Min Edge | Strategy |
|-------|----------------|----------|
| **5-15¢** | +2% true prob | ✅ TRADE - Low fees |
| 25-35¢ | +6% true prob | ⚠️ AVOID - High fees |
| 45-55¢ | +7% true prob | ❌ NEVER - Use Polymarket |
| 65-75¢ | +4% true prob | ⚠️ OKAY - Fees moderate |
| **85-95¢** | +2% true prob | ✅✅ OPTIMAL - Lowest fees |

---

## Advanced Tactics

### 1. Ladder Into Positions
- **Start at extreme price** (e.g., 85¢)
- Add as price moves more extreme (90¢+)
- Fees decrease as probability increases
- Each leg has lower fee impact

### 2. Market Making Consideration
If providing liquidity on Kalshi:
- Focus on **>80¢ and <20¢ markets**
- Fee advantage compounds over multiple roundtrips
- Avoid tight spreads near 50¢ (high fee drag)

### 3. Arbitrage Windows
When same event exists on both platforms:
1. Calculate effective price INCLUDING fees
2. Look for price + fee < opposite side
3. **Best arb zones:** Kalshi 85¢+ vs Polymarket 82-83¢

### 4. Kelly Sizing Adjustment
Standard Kelly: `f* = (bp - q) / b`

Fee-adjusted Kelly on Kalshi:
```
f* = (bp - q) / b - (fee_rate / expected_value)

At 90¢: fee_drag ≈ 1.5% → reduce Kelly by 1-2%
At 50¢: fee_drag ≈ 7.0% → reduce Kelly by 7-10%
```

---

## Common Mistakes to Avoid

### ❌ DON'T:
1. **Trade 50¢ on Kalshi** - Worst fee zone
2. **Ignore platform choice** - Costs 2-3% edge
3. **High-frequency trade mid-range** - Fees compound quickly
4. **Scale positions near 50¢** - Linear fee increase

### ✅ DO:
1. **Check price before platform selection**
2. **Focus on 85-95¢ for Kalshi edge**
3. **Use Polymarket for 30-70¢**
4. **Calculate effective price including fees**

---

## Real-World Examples

### Example 1: Election Market
**Market:** "Will X win?" at 88¢

- **Your edge:** +3% (true prob 91%)
- **Kalshi fee:** 1.68% roundtrip
- **Polymarket fee:** 4% roundtrip
- **Decision:** ✅ Use Kalshi
- **Savings:** 2.32% × position size

### Example 2: Binary Outcome
**Market:** "Will event happen?" at 45¢

- **Your edge:** +8% (true prob 53%)
- **Kalshi fee:** 7% roundtrip
- **Polymarket fee:** 4% roundtrip
- **Decision:** ✅ Use Polymarket
- **Savings:** 3% × position size

### Example 3: Long-Shot Bet
**Market:** "Unlikely event" at 8¢

- **Your edge:** +5% (true prob 13%)
- **Kalshi fee:** 1.15% roundtrip
- **Polymarket fee:** 4% roundtrip
- **Decision:** ✅ Use Kalshi
- **Savings:** 2.85% × position size

---

## Summary Checklist

Before every trade:

- [ ] What's the current market price?
- [ ] Is it >74¢ or <26¢? (Use Kalshi)
- [ ] Is it 26-74¢? (Use Polymarket)
- [ ] What's my true probability estimate?
- [ ] Does my edge exceed the fee cost?
- [ ] Am I sizing appropriately for fee drag?

---

## Fee Optimization Score

**Maximize this ratio:**
```
Score = (Your Edge - Fee Cost) / Capital at Risk

Best score: High edge + Extreme price on Kalshi
Worst score: Low edge + 50¢ price on Kalshi
```

---

**Last Updated:** February 12, 2026  
**Next Review:** After any Kalshi fee structure change  
**Contact:** Fee optimizer subagent
