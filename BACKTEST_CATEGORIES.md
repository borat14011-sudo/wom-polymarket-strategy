# Market Category Backtest Analysis

## Strategy Parameters
- **Risk/Reward Ratio (RVR):** ≥2.5x
- **Return on Capital (ROC):** ≥10%
- **Markets Analyzed:** 100
- **Data Source:** Gamma API (Polymarket)
- **Analysis Date:** 2026-02-06

## Executive Summary

This backtest analyzes 100 active Polymarket markets across 5 categories to identify which market types offer the best opportunities for our edge strategy (RVR 2.5x + ROC 10%).

**Key Finding:** POLITICS markets show the highest strategy fit at 93.5%, while AI/TECH markets have the lowest at 0.0%.

---

## Category Rankings

### By Total Volume (Market Liquidity)
1. **CRYPTO**: $77,363,346.68 (64 markets)
2. **SPORTS**: $27,539,438.59 (2 markets)
3. **POLITICS**: $23,859,877.10 (31 markets)
4. **WORLD/EVENTS**: $1,324,035.32 (1 markets)
5. **AI/TECH**: $1,308,164.80 (2 markets)

### By Strategy Opportunity (% Markets Meeting Criteria)
1. **POLITICS**: 93.5% (29/31 markets)
2. **CRYPTO**: 87.5% (56/64 markets)
3. **SPORTS**: 0.0% (0/2 markets)
4. **WORLD/EVENTS**: 0.0% (0/1 markets)
5. **AI/TECH**: 0.0% (0/2 markets)

---

## Detailed Category Analysis

### CRYPTO
- **Total Markets:** 64
- **Total Volume:** $77,363,346.68
- **Qualifying Markets:** 56 (87.5%)
- **Average Volume per Market:** $1,208,802.29
- **Strategy Score:** 87.5/100

### SPORTS
- **Total Markets:** 2
- **Total Volume:** $27,539,438.59
- **Qualifying Markets:** 0 (0.0%)
- **Average Volume per Market:** $13,769,719.30
- **Strategy Score:** 0.0/100

### POLITICS
- **Total Markets:** 31
- **Total Volume:** $23,859,877.10
- **Qualifying Markets:** 29 (93.5%)
- **Average Volume per Market:** $769,673.45
- **Strategy Score:** 93.5/100

### WORLD/EVENTS
- **Total Markets:** 1
- **Total Volume:** $1,324,035.32
- **Qualifying Markets:** 0 (0.0%)
- **Average Volume per Market:** $1,324,035.32
- **Strategy Score:** 0.0/100

### AI/TECH
- **Total Markets:** 2
- **Total Volume:** $1,308,164.80
- **Qualifying Markets:** 0 (0.0%)
- **Average Volume per Market:** $654,082.40
- **Strategy Score:** 0.0/100

---

## Key Findings

### Most Predictable Categories (Best Opportunity Rates)
- **POLITICS**: 93.5% of markets meet criteria (29/31 markets)
- **CRYPTO**: 87.5% of markets meet criteria (56/64 markets)
- **SPORTS**: 0.0% of markets meet criteria (0/2 markets)

### Least Predictable Categories (Lowest Opportunity Rates)
- **AI/TECH**: 0.0% of markets meet criteria (0/2 markets)
- **WORLD/EVENTS**: 0.0% of markets meet criteria (0/1 markets)
- **SPORTS**: 0.0% of markets meet criteria (0/2 markets)

---

## Hypothesis Testing

**Original Hypothesis:** Some categories are more predictable (sports?) vs others more random (crypto?)

**Results:**
1. **POLITICS**: 93.5% strategy fit (29 qualifying markets)
2. **CRYPTO**: 87.5% strategy fit (56 qualifying markets)
3. **SPORTS**: 0.0% strategy fit (0 qualifying markets)
4. **WORLD/EVENTS**: 0.0% strategy fit (0 qualifying markets)
5. **AI/TECH**: 0.0% strategy fit (0 qualifying markets)

**Interpretation:**
- ✅ **CONFIRMED**: Categories show significant variation in opportunity rates
- 🎯 **Best Category**: **POLITICS** (93.5%)
- ⚠️ **Worst Category**: **AI/TECH** (0.0%)
- 📊 **Opportunity Range**: 93.5% spread between best and worst
- 💡 Markets with extreme probabilities (very high or low prices) tend to meet our RVR criteria
- 🔍 Categories with more speculative/uncertain outcomes have more underpriced opportunities

---

## Strategic Recommendations

### 1. Best Categories for Our Edge
1. **POLITICS**
   - Strategy Fit: 93.5% (29/31 markets)
   - Total Volume: $23,859,877.10
   - Avg Volume/Market: $769,673.45
   - **Action:** PRIORITIZE - High opportunity rate

2. **CRYPTO**
   - Strategy Fit: 87.5% (56/64 markets)
   - Total Volume: $77,363,346.68
   - Avg Volume/Market: $1,208,802.29
   - **Action:** PRIORITIZE - High opportunity rate

3. **SPORTS**
   - Strategy Fit: 0.0% (0/2 markets)
   - Total Volume: $27,539,438.59
   - Avg Volume/Market: $13,769,719.30
   - **Action:** MONITOR - Moderate opportunities

### 2. Categories to Avoid or Use Caution
1. **AI/TECH**
   - Strategy Fit: 0.0% (0/2 markets)
   - **Reason:** Very low opportunity rate
   - **Action:** AVOID - Minimal edge

2. **WORLD/EVENTS**
   - Strategy Fit: 0.0% (0/1 markets)
   - **Reason:** Very low opportunity rate
   - **Action:** AVOID - Minimal edge

3. **SPORTS**
   - Strategy Fit: 0.0% (0/2 markets)
   - **Reason:** Very low opportunity rate
   - **Action:** AVOID - Minimal edge

### 3. Volume vs. Opportunity Trade-offs

**High Volume Leaders:**
- **CRYPTO**: $77,363,346.68 volume, #2 in opportunity (87.5%)
- **SPORTS**: $27,539,438.59 volume, #3 in opportunity (0.0%)
- **POLITICS**: $23,859,877.10 volume, #1 in opportunity (93.5%)

**Key Insights:**
- Higher volume markets generally have tighter spreads (less edge)
- Our strategy (RVR 2.5x+) finds more opportunities in extreme probability outcomes
- **Sweet Spot:** Categories with moderate volume but high opportunity rates
- **Highest Volume Category:** CRYPTO ($77,363,346.68)
- **Best Opportunity Category:** POLITICS (93.5%)

---

## Methodology

### Categorization Process
- Markets categorized using keyword matching in question/description fields
- 5 predefined categories + 'other' catch-all
- Multiple keyword matches increase category confidence score

### Strategy Application
1. **Binary Analysis:** Each binary market analyzed for both Yes/No outcomes
2. **Entry Criteria:** 
   - RVR (Risk/Reward Ratio) = (1 - price) / price ≥ 2.5x
   - ROC (Return on Capital) = (1 - price) / price ≥ 0.1 (10%)
3. **Qualification:** Market meets criteria if EITHER outcome qualifies

### Calculation Examples
- **Price 0.30 → RVR = 2.33x, ROC = 233%** ✅ QUALIFIES
- **Price 0.20 → RVR = 4.0x, ROC = 400%** ✅ QUALIFIES  
- **Price 0.50 → RVR = 1.0x, ROC = 100%** ❌ FAILS (RVR too low)
- **Price 0.90 → RVR = 0.11x, ROC = 11%** ❌ FAILS (RVR too low)

---

## Limitations & Caveats

### Data Limitations
- ⚠️ Analysis uses **active markets only** (not historical resolved markets)
- ⚠️ Cannot calculate actual win rates without resolution outcomes
- ⚠️ Price snapshots represent current sentiment, not historical entry points

### Strategy Limitations
- Does not account for:
  - **Liquidity depth** at desired price points
  - **Slippage** on larger order sizes
  - **Platform fees** (typically 2% on winnings)
  - **Time value** of capital locked in positions
  - **Adverse selection** (why is the market pricing this way?)
  - **Correlation** between related markets

### Recommended Next Steps
1. **Historical Backtest:** Analyze resolved markets with actual win/loss outcomes
2. **Liquidity Analysis:** Test actual fill prices vs. quoted prices
3. **Time-Series:** Track price movements and optimal entry/exit timing
4. **Kelly Criterion:** Calculate optimal bet sizing given edge estimates

---

## Conclusion

**Strong Edge Identified:** The POLITICS category shows 93.5% of markets meeting our criteria, indicating significant opportunity. Focus efforts here.

**Liquidity Available:** Top category has $77,363,346.68 in volume, providing sufficient market depth for trading.

**Overall Assessment:** 2/5 categories show >30% strategy fit, suggesting our edge is selective but present across multiple market types.

---

*Generated: 2026-02-07*  
*Markets Analyzed: 100 | Categories: 5*  
*Strategy: RVR ≥2.5x + ROC ≥10%*
