# Category Strategy Backtest - REAL DATA Analysis

**Analysis Date:** 2026-02-06  
**Data Source:** Polymarket resolved markets (149 markets)  
**Strategy Parameters:** RVR ≥ 2.5x, ROC ≥ 10%  
**Objective:** Validate claims that politics = 93.5% and crypto = 87.5% "strategy fit"

---

## 🎯 Executive Summary

**CRITICAL FINDING:** We CANNOT validate the 93.5%/87.5% win rate claims using available data.

### Why Not?
The resolved markets dataset contains only **final settlement prices (1|0)**, not the historical prices during the market's lifetime that would allow us to:
- Identify which markets met entry criteria
- Simulate actual trade entry points  
- Calculate real win/loss rates

### What We Found Instead

Analyzed **149 resolved Polymarket markets** by category:

| Category | Markets | % of Total | Total Volume | Avg Volume/Market |
|----------|---------|------------|--------------|-------------------|
| **POLITICS** | 128 | 85.9% | $46,414,093 | $362,610 |
| **SPORTS** | 12 | 8.1% | $63,316,384 | $5,276,365 |
| **AI/TECH** | 8 | 5.4% | $1,497,553 | $187,194 |
| **OTHER** | 1 | 0.7% | $3,624 | $3,624 |

**📊 Total Volume:** $111,231,655 across 149 resolved markets

---

## ❌ Cannot Validate Win Rate Claims

### Original Claims
- **Politics:** 93.5% "strategy fit"
- **Crypto:** 87.5% "strategy fit"

### Data Limitation
The resolved markets JSON contains:
```json
{
  "question": "Will a Democrat win Michigan US Senate Election?",
  "outcomes": "Yes|No",
  "final_prices": "1|0",  // ← Settlement prices, not entry prices
  "winner": "Yes"
}
```

**Problem:** `final_prices` are always `1|0` or `0|1` after resolution. These don't meet our entry criteria (RVR ≥ 2.5x requires price ≤ 0.286).

### What We Need for Real Backtest
1. **Historical price snapshots** during market lifetime
2. **Entry timing** - when did price reach our threshold?
3. **Exit price** - final settlement (0 or 1)
4. **Orderbook depth** - could we actually fill at that price?

---

## 🔍 What "Strategy Fit" Actually Meant

The original BACKTEST_CATEGORIES.md analyzed **ACTIVE markets**, not resolved ones.

### Definition
**"Strategy Fit" = % of markets where AT LEAST ONE outcome meets entry criteria**

Example:
- Market: "Will Trump win 2024?"
- Prices: Yes = 0.65, No = 0.35
- **Yes outcome:** RVR = (1-0.65)/0.65 = **0.54x** ❌ (too low)
- **No outcome:** RVR = (1-0.35)/0.35 = **1.86x** ❌ (too low)
- **Result:** Market does NOT fit strategy (neither outcome qualifies)

### The Crucial Distinction

| Metric | What It Measures | Example |
|--------|------------------|---------|
| **Strategy Fit** | "Can we enter this market?" | 93.5% of politics markets had ≥1 tradeable outcome |
| **Win Rate** | "Did we profit from this trade?" | We won 70% of trades we entered |

**❗ STRATEGY FIT ≠ WIN RATE**

The 93.5%/87.5% figures tell us:
- ✅ Entry opportunities exist in these categories
- ❌ Nothing about whether those trades would have won

---

## 📊 Resolved Markets Analysis

### Category Breakdown

#### POLITICS (128 markets, 85.9%)
- **Total Volume:** $46,414,093
- **Average per Market:** $362,610
- **Sample Markets:**
  - Michigan Senate Election Winner
  - Pennsylvania Senate Election Winner  
  - Various state/federal election markets
- **Observation:** Dominated the resolved markets dataset

#### SPORTS (12 markets, 8.1%)
- **Total Volume:** $63,316,384
- **Average per Market:** $5,276,365
- **Observation:** Fewer markets but MUCH higher volume per market
- **Note:** High volume suggests tight spreads (less edge opportunity)

#### AI/TECH (8 markets, 5.4%)
- **Total Volume:** $1,497,553
- **Average per Market:** $187,194
- **Observation:** Smaller niche with lower liquidity

#### CRYPTO (0 markets)
- **Finding:** NO crypto markets in the resolved dataset
- **Implication:** Cannot validate the 87.5% crypto claim at all

---

## 🧮 Why We Can't Calculate Win Rates

### Entry Criteria
For a market to qualify:
- **Price ≤ 0.286** → RVR = (1-0.286)/0.286 = **2.5x** ✅
- **Price ≤ 0.20** → RVR = (1-0.20)/0.20 = **4.0x** ✅
- **Price ≤ 0.10** → RVR = (1-0.10)/0.10 = **9.0x** ✅

### The Problem
Resolved markets show `final_prices = "1|0"`:
- **Price = 1.0** → RVR = 0x ❌
- **Price = 0.0** → RVR = undefined ❌

Neither qualifies for entry!

### What We'd Need
Historical price data showing:
```
Market: "Will Trump win 2024?"
2024-03-15: Yes=0.55, No=0.45 → No qualifies (RVR=1.22x) ❌
2024-06-20: Yes=0.72, No=0.28 → No qualifies (RVR=2.57x) ✅ ENTER
2024-11-06: Yes=1.00, No=0.00 → Trump wins → EXIT
Result: Win! Profit = 1.0/0.28 - 1 = 257% ROI
```

---

## 📈 Data Sources for Real Backtest

### Option 1: Polymarket CLOB API
- Historical orderbook snapshots
- Trade-by-trade data
- **Pros:** Authoritative, complete
- **Cons:** May require API access, rate limits

### Option 2: Archive.org Snapshots
- Wayback Machine captures of Polymarket pages
- Manual extraction required
- **Pros:** Free, publicly available
- **Cons:** Incomplete coverage, labor-intensive

### Option 3: Gamma API Historical Series
- Some historical price data available
- **Pros:** Structured API access
- **Cons:** Unknown coverage, possibly limited history

### Option 4: Blockchain Event Logs
- On-chain trade data from Polygon
- Complete transaction history
- **Pros:** Immutable, verifiable
- **Cons:** Requires blockchain indexing, complex parsing

---

## 💡 Key Insights from This Analysis

### 1. Politics Dominates Resolved Markets
- **85.9%** of resolved markets were politics-related
- Reflects 2024 election cycle timing
- High availability of entry opportunities (if claim holds)

### 2. Sports = High Volume, Low Opportunity
- Highest avg volume per market ($5.3M)
- Original backtest showed **0% strategy fit**
- Interpretation: Efficient markets with tight spreads

### 3. Crypto Markets Absent
- Zero resolved crypto markets in dataset
- Cannot validate 87.5% claim
- May reflect:
  - Different resolution timelines (crypto markets longer-dated?)
  - Scraping limitations
  - Category misclassification

### 4. Strategy Fit ≠ Predictive Power
The original 93.5%/87.5% metrics measure:
- **Opportunity availability** (can we enter?)
- NOT **win rate** (will we profit?)

A category could have:
- **High strategy fit** (lots of entry opportunities)
- **Low win rate** (most trades lose)

Or vice versa!

---

## 🎯 Recommendations

### 1. Acquire Historical Price Data
**Priority:** HIGH  
**Action:** Explore CLOB API, Archive.org, or blockchain data  
**Goal:** Build dataset with entry prices, not just final settlements

### 2. Reframe Metrics
**Current:** "93.5% strategy fit" (ambiguous)  
**Better:**
- "93.5% of politics markets had ≥1 tradeable outcome"
- "Win rate: TBD (needs historical data)"

### 3. Test with Active Markets
**Short-term validation:**
- Monitor CURRENT active markets
- Track when prices hit entry criteria
- Follow to resolution
- Calculate actual win rate

**Timeline:** 1-6 months depending on market durations

### 4. Focus on Politics (If Claim Holds)
**Hypothesis:** Politics markets offer best edge
**Test:** Enter 20-30 politics trades, track results
**Success threshold:** Win rate >65% to validate strategy

### 5. Investigate Crypto Absence
**Question:** Why no resolved crypto markets?
**Actions:**
- Check longer date ranges
- Verify category keywords
- Explore different data sources

---

## 📋 Methodology Notes

### Market Categorization
Used keyword matching on question + description:

```javascript
POLITICS: ['election', 'senate', 'president', 'governor', 'democrat', 
           'republican', 'vote', 'poll', 'biden', 'trump']
CRYPTO:   ['bitcoin', 'ethereum', 'crypto', 'blockchain', 'token', 
           'defi', 'nft', 'solana']
SPORTS:   ['nba', 'nfl', 'mlb', 'nhl', 'soccer', 'football', 
           'basketball', 'champion', 'playoff']
```

**Limitation:** Keyword-based categorization may miss nuanced markets

### Data Quality
- **Source:** `polymarket_resolved_markets.json`
- **Markets:** 149 resolved
- **Completeness:** Unknown (full universe of resolved markets?)
- **Timeliness:** Scraped 2026-02-06

---

## ⚠️ Critical Limitations

### 1. No Historical Prices
Cannot determine:
- Which markets actually met entry criteria historically
- When entry signals would have fired
- Actual trade outcomes

### 2. Settlement Prices Only
`final_prices = "1|0"` tells us:
- ✅ Who won
- ❌ What prices were during trading

### 3. No Crypto Markets
Cannot validate 87.5% crypto claim at all

### 4. Sample Bias
- Dataset may not represent full universe
- Heavy politics weighting may reflect scraping timing (post-2024 election)

### 5. No Timing Data
Don't know:
- How long markets were active
- Price evolution over time
- Optimal entry/exit windows

---

## 🔬 Validation Plan (Next Steps)

### Phase 1: Data Acquisition (Week 1-2)
- [ ] Explore Polymarket CLOB API
- [ ] Test Archive.org for price snapshots
- [ ] Research blockchain data extraction
- [ ] Identify 20-30 resolved markets with historical data

### Phase 2: Pilot Backtest (Week 3-4)
- [ ] Build dataset with entry/exit prices
- [ ] Simulate trades using strategy rules
- [ ] Calculate actual win rates by category
- [ ] Compare to 93.5%/87.5% claims

### Phase 3: Forward Testing (Month 2-6)
- [ ] Monitor 50+ active markets
- [ ] Enter paper trades when criteria met
- [ ] Track to resolution
- [ ] Calculate live win rates

### Phase 4: Strategy Refinement (Month 6+)
- [ ] Identify winning patterns
- [ ] Adjust entry criteria
- [ ] Optimize by category
- [ ] Build production system

---

## 📊 Summary Statistics

### Dataset Overview
- **Total Markets:** 149 resolved
- **Total Volume:** $111,231,655
- **Date Range:** Unknown (data snapshot 2026-02-06)
- **Categories Identified:** 4 (Politics, Sports, AI/Tech, Other)

### Category Distribution
```
POLITICS:  128 markets (85.9%) - $46.4M volume
SPORTS:     12 markets  (8.1%) - $63.3M volume
AI/TECH:     8 markets  (5.4%) - $1.5M volume
OTHER:       1 market   (0.7%) - $3.6K volume
CRYPTO:      0 markets  (0.0%) - $0 volume
```

### Analysis Completeness
✅ **Completed:**
- Market categorization
- Volume analysis
- Category distribution

❌ **NOT Completed (Data Limitation):**
- Entry signal identification
- Win rate calculation
- Strategy validation
- Claims verification

---

## 🎓 Lessons Learned

### 1. Beware Ambiguous Metrics
"Strategy fit" sounds like win rate but measures entry opportunity.  
**Learning:** Always define metrics precisely.

### 2. Resolution ≠ Trading Data
Final settlement prices tell you WHO won, not WHEN you could've entered.  
**Learning:** Backtest requires full price history, not just outcomes.

### 3. Active vs Resolved Markets
Active markets show current opportunities.  
Resolved markets show historical outcomes.  
**Learning:** Need BOTH for complete analysis.

### 4. Data Quality Matters
Missing crypto markets = incomplete analysis.  
**Learning:** Validate data completeness before drawing conclusions.

---

## 📄 Files Generated

### 1. `category_real_backtest_results.json`
Full dataset with:
- Market categorizations
- Volume statistics
- All 149 resolved markets
- Summary by category

### 2. `backtest_category_real_outcomes_v2.js`
Analysis script:
- Loads resolved markets JSON
- Categorizes by keywords
- Calculates distributions
- Identifies data limitations

### 3. `CATEGORY_REAL_BACKTEST.md` (this file)
Comprehensive report documenting:
- Analysis methodology
- Key findings
- Critical limitations
- Recommendations

---

## 🔚 Conclusion

### Can We Validate the 93.5%/87.5% Claims?
**NO** - Not with current data.

### Why Not?
We have **resolution outcomes** but NOT **historical entry prices**.

### What Did We Learn?
1. **Politics dominates** resolved markets (86% of sample)
2. **Sports has highest** avg volume ($5.3M vs $363K for politics)
3. **Crypto markets absent** from resolved dataset
4. **"Strategy fit" ≠ win rate** - measures different things

### What's Next?
1. **Acquire historical price data** (CLOB API, Archive.org, blockchain)
2. **Pilot backtest** on 20-30 markets with full price history
3. **Forward test** with live active markets
4. **Validate or refute** the 93.5%/87.5% claims with real data

### Bottom Line
The 93.5% politics / 87.5% crypto figures represent:
- ✅ **Entry opportunity rates** (markets with tradeable outcomes)
- ❌ **NOT win rates** (actual trade profitability)

To validate actual strategy performance, we need historical price data showing **when** markets hit entry thresholds and **what** those final outcomes were.

---

**Analysis by:** Subagent (category-analysis-real)  
**Report Date:** 2026-02-06  
**Status:** DATA LIMITATION IDENTIFIED - Cannot validate claims without historical prices  
**Recommendation:** Acquire historical price data for true backtest validation
