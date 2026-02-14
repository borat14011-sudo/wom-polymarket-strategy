# Kalshi Fee Analysis & Optimization

**Date:** February 12, 2026  
**Objective:** Calculate exact Kalshi fees and identify optimal trading zones

---

## 1. Kalshi Fee Formula

### Base Formula (Quadratic)
```
Fee per contract = k × price × (100 - price)
```

Where:
- **k** = 0.0007 (0.07% fee multiplier - standard Kalshi rate)
- **price** = contract price in cents (1-99)
- Fee is highest at 50¢, decreases toward extremes

### Roundtrip Cost
For a full trade (buy + sell):
```
Roundtrip Fee = 2 × k × price × (100 - price)
```

---

## 2. Fee Calculation by Price Point

### Per-Contract Fees (One-Way)

| Price | Formula | Fee (¢) | Fee ($) | Fee % of Price |
|-------|---------|---------|---------|----------------|
| **10¢** | 0.0007 × 10 × 90 | 0.63¢ | $0.0063 | 6.3% |
| **25¢** | 0.0007 × 25 × 75 | 1.31¢ | $0.0131 | 5.2% |
| **50¢** | 0.0007 × 50 × 50 | 1.75¢ | $0.0175 | 3.5% |
| **75¢** | 0.0007 × 75 × 25 | 1.31¢ | $0.0131 | 1.7% |
| **90¢** | 0.0007 × 90 × 10 | 0.63¢ | $0.0063 | 0.7% |

### Roundtrip Fees (Buy + Sell)

| Price | One-Way Fee | Roundtrip Fee | Roundtrip % |
|-------|-------------|---------------|-------------|
| **10¢** | 0.63¢ | **1.26¢** | **12.6%** |
| **25¢** | 1.31¢ | **2.62¢** | **10.5%** |
| **50¢** | 1.75¢ | **3.50¢** | **7.0%** |
| **75¢** | 1.31¢ | **2.62¢** | **3.5%** |
| **90¢** | 0.63¢ | **1.26¢** | **1.4%** |

---

## 3. Kalshi vs Polymarket Comparison

### Polymarket Fee Structure
- **Roundtrip fee:** 4.0% (2% per side)
- **Flat rate** regardless of price

### Cost Comparison Table

| Price | Kalshi Roundtrip | Polymarket Roundtrip | **Advantage** |
|-------|------------------|----------------------|---------------|
| 10¢ | 12.6% | 4.0% | ❌ **Polymarket -8.6%** |
| 25¢ | 10.5% | 4.0% | ❌ **Polymarket -6.5%** |
| 50¢ | 7.0% | 4.0% | ❌ **Polymarket -3.0%** |
| 75¢ | 3.5% | 4.0% | ✅ **Kalshi +0.5%** |
| 90¢ | 1.4% | 4.0% | ✅ **Kalshi +2.6%** |

### Break-Even Price Point
Kalshi becomes cheaper than Polymarket at approximately **73.5¢**

```
0.0007 × 2 × p × (100 - p) = 4.0
Solving: p ≈ 73.5¢ or 26.5¢
```

---

## 4. Optimal Trading Zones

### 🟢 KALSHI ADVANTAGE ZONES (Lower Fees)
**Price ranges: 0-26¢ and 74-99¢**

**Best zones:**
- **85-95¢:** Fee ~1.5-2.0% roundtrip (vs 4% Polymarket)
- **5-15¢:** Fee ~1.5-2.0% roundtrip (vs 4% Polymarket)

**Strategy:** Focus on extreme probability events where you have edge

---

### 🔴 POLYMARKET ADVANTAGE ZONES (Higher Kalshi Fees)
**Price ranges: 27-73¢**

**Worst zones:**
- **45-55¢:** Fee ~7% roundtrip (vs 4% Polymarket)
- **30-70¢:** Fee >4.5% roundtrip

**Strategy:** Avoid Kalshi for coin-flip scenarios; use Polymarket instead

---

## 5. Break-Even Win Rate Analysis

### Formula
To break even including fees:
```
Required Win Rate = (Entry Price + Roundtrip Fee) / 100
```

### Break-Even Table

| Entry Price | Kalshi Fee | Total Cost | **Required Win %** | Polymarket Win % | Difference |
|-------------|------------|------------|-------------------|------------------|------------|
| **10¢** | 1.26¢ | 11.26¢ | **11.3%** | 10.4% | +0.9% |
| **25¢** | 2.62¢ | 27.62¢ | **27.6%** | 26.0% | +1.6% |
| **50¢** | 3.50¢ | 53.50¢ | **53.5%** | 52.0% | +1.5% |
| **75¢** | 2.62¢ | 77.62¢ | **77.6%** | 78.0% | **-0.4%** ✅ |
| **90¢** | 1.26¢ | 91.26¢ | **91.3%** | 93.6% | **-2.3%** ✅ |

**Key Insight:** At high probabilities (>74¢), Kalshi requires LOWER win rates than Polymarket

---

## 6. Trading Strategy Adjustments

### A. Price-Based Platform Selection

```
IF market_price < 26¢ OR market_price > 74¢:
    → USE KALSHI (lower fees)
    
IF 26¢ ≤ market_price ≤ 74¢:
    → USE POLYMARKET (lower fees)
```

### B. Edge Requirements by Price

**For Kalshi profitability:**

| Price Zone | Minimum Edge Required | Notes |
|------------|----------------------|-------|
| 5-15¢ | +2% true prob | Low fees, high returns |
| 25-35¢ | +6% true prob | Moderate fees |
| 45-55¢ | +7% true prob | **AVOID - highest fees** |
| 65-75¢ | +4% true prob | Decreasing fees |
| 85-95¢ | +2% true prob | **OPTIMAL - lowest fees** |

### C. Arbitrage Considerations

When same market exists on both platforms:
1. **Calculate effective price including fees**
2. **Kalshi is better for extremes** (>74¢, <26¢)
3. **Polymarket is better for mid-range** (26-74¢)

### D. Position Sizing Impact

For large positions (e.g., $1000):

**At 90¢:**
- Kalshi fee: ~$14 roundtrip
- Polymarket fee: ~$40 roundtrip
- **Savings: $26 using Kalshi**

**At 50¢:**
- Kalshi fee: ~$35 roundtrip
- Polymarket fee: ~$40 roundtrip
- **Savings: $5 using Polymarket**

---

## 7. Advanced Fee Optimization

### Minimize Fee Impact
1. **Trade extreme probabilities** (>80¢ or <20¢)
2. **Hold longer** (reduce roundtrip frequency)
3. **Scale into positions** (but avoid mid-range prices)

### Fee-Adjusted Kelly Criterion
When calculating optimal bet size, use:
```
f* = (bp - q) / b - fee_percentage
```

Where fee burden is LOWEST at extremes on Kalshi.

---

## 8. Summary & Recommendations

### ✅ USE KALSHI WHEN:
- Market price >74¢ (high probability events)
- Market price <26¢ (low probability events)
- Trading large size on extreme outcomes
- You have strong conviction on tails

### ❌ AVOID KALSHI WHEN:
- Market price 26-74¢ (use Polymarket instead)
- Coin-flip scenarios near 50¢
- High-frequency trading mid-range prices

### 💡 OPTIMAL KALSHI STRATEGY:
Focus on **85-95¢ range** where:
- Fees are 1.4-2.0% roundtrip (vs 4% Polymarket)
- 2.6% fee advantage = extra edge
- Break-even win rates are 2-3% lower than Polymarket

---

## Appendix: Full Fee Table (0-100¢)

| Price | One-Way Fee | Roundtrip Fee | Roundtrip % |
|-------|-------------|---------------|-------------|
| 5¢ | 0.33¢ | 0.67¢ | 13.3% |
| 10¢ | 0.63¢ | 1.26¢ | 12.6% |
| 15¢ | 0.89¢ | 1.79¢ | 11.9% |
| 20¢ | 1.12¢ | 2.24¢ | 11.2% |
| 25¢ | 1.31¢ | 2.62¢ | 10.5% |
| 30¢ | 1.47¢ | 2.94¢ | 9.8% |
| 35¢ | 1.60¢ | 3.19¢ | 9.1% |
| 40¢ | 1.68¢ | 3.36¢ | 8.4% |
| 45¢ | 1.73¢ | 3.47¢ | 7.7% |
| **50¢** | **1.75¢** | **3.50¢** | **7.0%** |
| 55¢ | 1.73¢ | 3.47¢ | 6.3% |
| 60¢ | 1.68¢ | 3.36¢ | 5.6% |
| 65¢ | 1.60¢ | 3.19¢ | 4.9% |
| 70¢ | 1.47¢ | 2.94¢ | 4.2% |
| 75¢ | 1.31¢ | 2.62¢ | 3.5% |
| 80¢ | 1.12¢ | 2.24¢ | 2.8% |
| 85¢ | 0.89¢ | 1.79¢ | 2.1% |
| 90¢ | 0.63¢ | 1.26¢ | 1.4% |
| 95¢ | 0.33¢ | 0.67¢ | 0.7% |

---

**Generated by:** Kalshi Fee Optimizer  
**Model:** Quadratic fee structure with k=0.0007  
**Recommendation:** Trade extremes on Kalshi, mid-range on Polymarket
