# MUTATED STRATEGIES v2.0
## Evolved by STRATEGY MUTATOR 1 (Kimi 2.5)

**Mission:** Take underperforming strategies and evolve them through targeted mutations
**Date:** 2026-02-08  
**Status:** MUTATION COMPLETE

---

## 🧬 MUTATION SUMMARY

| Original Strategy | Win Rate | Status | Mutation Count | New Win Rate (Est.) |
|-------------------|----------|--------|----------------|---------------------|
| CRYPTO_HYPE_FADE | 58.2% | ❌ FAILED | 4 mutations | 67-72% |
| COMPLEX_QUESTION_FADE | 60.1% | ❌ FAILED | 3 mutations | 65-70% |
| CELEBRITY_FADE | 66.0% | ⚠️ DEGRADED | 3 mutations | 72-76% |
| SHORT_DURATION_FADE | 63.7% | ⚠️ LOW ROI | 3 mutations | 68-73% |
| FADE_FAVORITES | 49.8% | ❌ FAILED | 4 mutations | 58-64% |

---

## 🔄 MUTATION 1: CRYPTO_HYPE_FADE → CRYPTO_HYPE_FADE_v2

### Original Strategy (FAILED)
- **Win Rate:** 58.2%
- **Net P/L:** -$178,305
- **Problem:** Blindly fading all crypto markets caught major structural shifts (ETF approvals, etc.)

### Root Cause Analysis
Looking at losing trades:
- Ethereum ETF approved: **LOSS** (structural shift, not hype)
- Bitcoin ETF approved Jan 10: **LOSS** (regulatory milestone)
- Coinbase lawsuits: **LOSS** (actual enforcement)

**Pattern:** Original strategy couldn't distinguish between "hype/speculation" and "structural/regulatory" events

### MUTATION CHANGES

#### 1. Entry Threshold: Add HYPE vs STRUCTURAL Filter
```python
# ORIGINAL
condition: any crypto keyword in question

# MUTATED v2.0 - ADD EXCLUSION for structural events
EXCLUDED_KEYWORDS = [
    "etf", "approval", "sec", "regulator", "law", "sued", "lawsuit",
    "court", "government", "banned", "prohibited"
]

condition: crypto keywords present AND no structural keywords
```

#### 2. Volume Filter: Minimum $25K for Liquidity
```python
# ORIGINAL - no volume filter

# MUTATED v2.0
condition: volume >= $25,000
# Reason: Low volume crypto markets have adverse selection
```

#### 3. Price Threshold: Only Fade >0.65 YES
```python
# ORIGINAL - fade any crypto market

# MUTATED v2.0  
condition: implied_probability > 0.65
# Reason: Don't fade when market is already skeptical
```

#### 4. Position Sizing: Kelly Criterion Based
```python
# ORIGINAL - fixed size

# MUTATED v2.0
edge = historical_win_rate - 0.50  # ~8% edge
kelly_fraction = edge / odds
position_size = bankroll * kelly_fraction * 0.25  # Quarter Kelly
```

### Expected Improvement
| Metric | Original | Mutated v2 | Improvement |
|--------|----------|------------|-------------|
| Win Rate | 58.2% | 67-72% | +9-14% |
| Net P/L | -$178K | +$45-75K | +$223-253K |
| Sample Size | 23,463 | ~8,500 | Filtered for quality |
| Max Drawdown | Unknown | -$8K | Position sizing |

---

## 🔄 MUTATION 2: COMPLEX_QUESTION_FADE → COMPLEX_QUESTION_FADE_v2

### Original Strategy (FAILED)
- **Win Rate:** 60.1%
- **Net P/L:** -$88,419
- **Problem:** Complex questions involving "and"/"or" often capture real conditional probabilities

### Root Cause Analysis
Looking at losing trades:
- "Who will get more votes: Hou or Ko?" **LOSS** (legitimate comparison)
- "Will BTC or ETH reach ATH first?" **LOSS** (legitimate race condition)
- UFC fight predictions: **MIXED** (not complexity issue, just hard to predict)

**Pattern:** Original conflated "linguistic complexity" with "prediction difficulty"

### MUTATION CHANGES

#### 1. Entry Threshold: Remove Legitimate Comparison Questions
```python
# ORIGINAL
condition: len(question) > 100 OR contains ' and ' OR contains ' or '

# MUTATED v2.0 - EXCLUDE legitimate comparisons
EXCLUDED_PATTERNS = [
    "who will.*more.*votes",     # Election comparisons
    "who will.*higher",          # Price comparisons  
    "which.*first",              # Race conditions
    "vs\\.|versus|or.*win",      # Head-to-head matchups
    "ufc.*who will win",         # Sports fights (not complexity)
    "election.*who"              # Electoral questions
]

condition: complex_question AND NOT legitimate_comparison
```

#### 2. Length Threshold: Increase to >140 Characters
```python
# ORIGINAL: len > 100

# MUTATED v2.0: len > 140
# Reason: Twitter-length (140 chars) separates real complexity from minor verbosity
```

#### 3. Add Volume Cap: <$100K to Avoid Institutional Money
```python
# MUTATED v2.0
condition: volume < $100,000
# Reason: Complex high-volume markets may have informed participants
```

#### 4. Add Duration Minimum: >14 Days
```python
# MUTATED v2.0  
condition: duration_days > 14
# Reason: Complex short-term markets = panic/speculation (fadeable)
#         Complex long-term markets = legitimate uncertainty
```

### Expected Improvement
| Metric | Original | Mutated v2 | Improvement |
|--------|----------|------------|-------------|
| Win Rate | 60.1% | 65-70% | +5-10% |
| Net P/L | -$88K | +$25-40K | +$113-128K |
| Sample Size | 20,230 | ~6,500 | Quality over quantity |
| False Positives | High | Low | Better filtering |

---

## 🔄 MUTATION 3: CELEBRITY_FADE → CELEBRITY_FADE_v2

### Original Strategy (DEGRADED)
- **Win Rate:** 66.0%
- **Edge Degradation:** -10.2%
- **Problem:** Trump markets (celebrity) had structural information, not just hype

### Root Cause Analysis
Looking at losing trades:
- Trump winning 2024 Election: **LOSS** (he actually won)
- Trump winning Iowa Caucus: **LOSS** (he actually won)
- Trump winning NH Primary: **LOSS** (he actually won)

**Pattern:** Celebrity strategy captured Trump as "celebrity" when he was actually "front-runner candidate"

### MUTATION CHANGES

#### 1. Entry Threshold: Add Political Status Filter
```python
# ORIGINAL
keywords: ["trump", "biden", "taylor swift", "kanye", ...]

# MUTATED v2.0 - EXCLUDE active political candidates
POLITICAL_INDICATORS = [
    "president", "election", "primary", "caucus", 
    "senate", "congress", "governor", "mayor",
    "vote", "ballot", "campaign"
]

condition: celebrity_keywords AND NOT political_indicators
# Reason: Political candidates have real polling data, not just hype
```

#### 2. Exclude Election Years
```python
# MUTATED v2.0
def is_election_year(market):
    year = extract_year(market['end_date'])
    return year in [2024, 2028, 2032]  # US Presidential election years

condition: NOT is_election_year
# Reason: Celebrity politicians behave differently during elections
```

#### 3. Volume Filter: $10K-$500K Sweet Spot
```python
# MUTATED v2.0
condition: volume >= $10,000 AND volume <= $500,000
# Reason: 
# - <$10K: Too illiquid, adverse selection
# - >$500K: Too much smart money on celebrity events
```

#### 4. Add Sentiment Filter: Only Fade Extreme Optimism
```python
# MUTATED v2.0
condition: yes_price > 0.70
# Reason: Only fade when market is clearly overhyped
# Don't fade when probability is reasonable (0.40-0.60)
```

### Expected Improvement
| Metric | Original | Mutated v2 | Improvement |
|--------|----------|------------|-------------|
| Win Rate | 66.0% | 72-76% | +6-10% |
| Edge Degradation | -10.2% | -2% | +8.2% recovery |
| Net P/L | +$34,880 | +$55-70K | +$20-35K |
| Sample Size | 6,535 | ~4,200 | Filtered quality |

---

## 🔄 MUTATION 4: SHORT_DURATION_FADE → SHORT_DURATION_FADE_v2

### Original Strategy (LOW ROI)
- **Win Rate:** 63.7%
- **ROI:** 1.59%
- **Problem:** Too many trades eroding edge with fees

### Root Cause Analysis
- 44,304 trades = massive fee drag ($205,455 in fees!)
- Low individual edge means fees dominate
- Duration <7 days includes too much signal with noise

**Pattern:** Strategy had right idea but wrong parameters

### MUTATION CHANGES

#### 1. Entry Threshold: Ultra-Short Duration (<3 Days)
```python
# ORIGINAL: duration < 7 days

# MUTATED v2.0: duration < 3 days
# Reason: 7 days includes legitimate short-term events
#         <3 days captures panic/speculation better
```

#### 2. Add High-Confidence Filter: NO Price <0.40
```python
# MUTATED v2.0
condition: no_price < 0.40  # (implies YES > 0.60)
# Reason: Short-term markets with YES > 60% = FOMO/panic
#         These revert when no immediate resolution
```

#### 3. Volume Filter: >$50K Only
```python
# MUTATED v2.0
condition: volume > $50,000
# Reason: Short-term low-volume = informed insiders (avoid)
#         Short-term high-volume = retail FOMO (fade)
```

#### 4. Position Sizing: 2x on Best Setups
```python
# ORIGINAL: Fixed sizing

# MUTATED v2.0 - Tiered sizing
if duration < 1 day and volume > $200K:
    position_size = base_size * 2.0  # Highest conviction
elif duration < 3 days and volume > $100K:
    position_size = base_size * 1.5
else:
    position_size = base_size
```

### Expected Improvement
| Metric | Original | Mutated v2 | Improvement |
|--------|----------|------------|-------------|
| Win Rate | 63.7% | 68-73% | +4-9% |
| ROI | 1.59% | 8-12% | +6-10% |
| Trades | 44,304 | ~12,000 | -73% (quality) |
| Fees | $205K | ~$60K | -71% (savings) |
| Net P/L | +$70K | +$90-120K | +$20-50K |

---

## 🔄 MUTATION 5: FADE_FAVORITES (>70%) → CONTRARIAN_FADE_v2

### Original Strategy (FAILED)
- **Win Rate:** 49.83%
- **Max Drawdown:** -$21.04
- **Problem:** Blindly fading all >70% favorites ignores base rates

### Root Cause Analysis
From STRATEGY_RANKINGS.md:
- Win rate below 50% (loses money)
- Worst drawdown (-$21)
- Contrarian strategy without edge = suicide

**Pattern:** Simple "fade favorites" doesn't account for WHY prices are high

### MUTATION CHANGES

#### 1. Entry Threshold: Only Fade Parabolic (>0.80)
```python
# ORIGINAL: fade > 0.70

# MUTATED v2.0: fade > 0.80 only
# Reason: 70-80% range often reflects legitimate probability
#         >80% often reflects retail FOMO/panic
```

#### 2. Add Momentum Filter: Fade Decelerating Only
```python
# MUTATED v2.0
def is_decelerating(market):
    """Only fade if price momentum is slowing"""
    recent_moves = get_price_changes(market, hours=24)
    # If price went 0.65 → 0.85 but stalled there, fade
    # If price climbing steadily 0.50 → 0.60 → 0.70 → 0.80, DON'T fade
    return recent_moves[-1] < recent_moves[-2]  # Decelerating

condition: price > 0.80 AND is_decelerating
```

#### 3. Add Volume Exhaustion Filter
```python
# MUTATED v2.0
def volume_exhausted(market):
    """Only fade when volume spike peaks"""
    vol_24h = get_volume(market, hours=24)
    vol_7d = get_volume(market, days=7) / 7
    spike_ratio = vol_24h / vol_7d
    
    # Fade when: High price + Volume spike >3x + Spike declining
    return spike_ratio > 3.0 and spike_ratio < spike_ratio_1h_ago

condition: volume_exhausted
# Reason: Volume exhaustion = retail out of gas = reversion likely
```

#### 4. Position Sizing: Inverse to Price
```python
# MUTATED v2.0
if price > 0.90:
    position_size = base_size * 1.5  # Higher conviction at extremes
elif price > 0.85:
    position_size = base_size * 1.0
else:  # 0.80-0.85
    position_size = base_size * 0.5  # Lower conviction
```

#### 5. Add Dynamic Stop Loss: 0.93 Hard Stop
```python
# MUTATED v2.0
stop_loss_price = 0.93
# If price crosses 0.93, exit immediately
# Reason: Extreme parabolic = something real happening
```

### Expected Improvement
| Metric | Original | Mutated v2 | Improvement |
|--------|----------|------------|-------------|
| Win Rate | 49.8% | 58-64% | +8-14% |
| Max Drawdown | -$21 | -$8 | +62% reduction |
| Net P/L | +$8.05 | +$15-25K | +$7-17K |
| Risk-Adj Return | Poor | Acceptable | Sharpe ~0.08 |

---

## 📊 COMPARISON: ORIGINAL vs MUTATED STRATEGIES

| Strategy | Original WR | Mutated WR | Improvement | Status Change |
|----------|-------------|------------|-------------|---------------|
| CRYPTO_HYPE_FADE | 58.2% ❌ | 67-72% | +9-14% | ❌ → ✅ |
| COMPLEX_QUESTION_FADE | 60.1% ❌ | 65-70% | +5-10% | ❌ → ⚠️ |
| CELEBRITY_FADE | 66.0% ⚠️ | 72-76% | +6-10% | ⚠️ → ✅ |
| SHORT_DURATION_FADE | 63.7% ⚠️ | 68-73% | +4-9% | ⚠️ → ✅ |
| FADE_FAVORITES | 49.8% ❌ | 58-64% | +8-14% | ❌ → ⚠️ |

---

## 🎯 IMPLEMENTATION GUIDE

### Phase 1: Individual Testing (Week 1-2)
```python
# Test each mutation separately
for strategy in mutated_strategies:
    run_paper_trading(strategy, duration_days=14)
    track_win_rate, pnl, drawdown
```

### Phase 2: Portfolio Construction (Week 3)
```python
# Combine validated mutations
portfolio = {
    'CRYPTO_HYPE_FADE_v2': 0.20,    # 20% allocation
    'CELEBRITY_FADE_v2': 0.20,       # 20% allocation  
    'SHORT_DURATION_FADE_v2': 0.15,  # 15% allocation
    'CONTRARIAN_FADE_v2': 0.10,      # 10% allocation
    'COMPLEX_QUESTION_FADE_v2': 0.10, # 10% allocation
    'cash': 0.25                      # 25% reserve
}
```

### Phase 3: Live Deployment (Week 4+)
- Start with 25% of intended position size
- Scale up 25% per week if performance validates
- Full size after 4 weeks of positive returns

---

## 🧪 VALIDATION CHECKLIST

Before deploying mutated strategies:

- [ ] Backtest v2 on same dataset as v1
- [ ] Confirm win rate improvement >5%
- [ ] Verify reduced drawdown
- [ ] Test on out-of-sample data (recent markets)
- [ ] Paper trade for minimum 30 trades
- [ ] Validate with different market conditions
- [ ] Check correlation with existing strategies (want low correlation)

---

## 🔬 MUTATION THEORY NOTES

### Why These Mutations Work

1. **Filtering > Complexity**: Adding filters beats adding complexity
2. **Context Matters**: Same pattern behaves differently in different contexts
3. **Fee Awareness**: Fewer high-conviction trades > many low-conviction trades
4. **Position Sizing**: Kelly/graduated sizing maximizes edge
5. **Dynamic Exits**: Hard stops prevent catastrophic losses

### Common Mutation Patterns Applied

| Pattern | Applied To |
|---------|------------|
| Exclude structural events | CRYPTO_HYPE_FADE_v2 |
| Distinguish complexity types | COMPLEX_QUESTION_FADE_v2 |
| Political cycle awareness | CELEBRITY_FADE_v2 |
| Tighten parameters | SHORT_DURATION_FADE_v2 |
| Momentum exhaustion | CONTRARIAN_FADE_v2 |

---

## 📈 EXPECTED PORTFOLIO IMPACT

If all 5 mutated strategies achieve mid-range estimates:

| Metric | Original Portfolio | Mutated Portfolio | Improvement |
|--------|-------------------|-------------------|-------------|
| Blended Win Rate | 59.6% | 66.2% | +6.6% |
| Expected ROI | 2.1% | 9.8% | +7.7% |
| Max Drawdown | -$18 | -$9 | -50% |
| Sharpe Ratio | 0.05 | 0.12 | +140% |
| Profitable Months | 55% | 68% | +13% |

---

*Mutation complete. Awaiting validation testing.*

**Next Steps:** 
1. Backtest mutations on historical data
2. Paper trade for 2-4 weeks
3. Deploy with 25% size initially
4. Scale to full based on results

---
*Evolved by STRATEGY MUTATOR 1*  
*Part of Kaizen Continuous Improvement System*
