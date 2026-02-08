# Order Book Depth Filter - Forward Testing

**Status:** IMPLEMENTED (Feb 7, 2026 04:20 PST)  
**Purpose:** Test hypothesis that thin markets underperform  
**Timeline:** 2-4 weeks of data collection required

---

## 🎯 What We're Testing

**Hypothesis:** Markets with low order book depth (<$10K liquidity) have:
- Higher manipulation risk
- Worse win rates
- Greater slippage

**Supported By:**
- ✅ Market microstructure theory (academic papers)
- ✅ Polymarket CLOB API (can fetch real-time depth)
- ❌ Historical validation (NO data exists for backtesting)

**Validation Method:** Forward testing with real trades

---

## 📊 How It Works

### Filter Implementation

**Code Location:** `signal_detector_v2.py`

**Filter Logic:**
```python
# Fetch order book for the side we're trading
depth_data = self._get_orderbook_depth(token_id)
total_depth = depth_data['total_depth']  # Bids + Asks

# Reject if depth < $10K
if total_depth < 10000:
    return None  # Skip this market
```

**What Gets Logged:**
Every market evaluated (passed or failed) is logged to `orderbook_depth_log.jsonl`:

```json
{
  "timestamp": "2026-02-07T04:20:00",
  "market_id": "123456",
  "title": "Will Bitcoin reach $100K by Feb 15?",
  "depth_data": {
    "total_depth": 15000,
    "bid_depth": 8000,
    "ask_depth": 7000,
    "spread": 0.02,
    "best_bid": 0.64,
    "best_ask": 0.66
  },
  "passed_depth_filter": true,
  "depth_threshold": 10000,
  "signal": {
    "side": "YES",
    "entry_price": 0.65,
    "outcome": null  // Updated after resolution
  }
}
```

---

## 📈 Analysis Plan (After 2-4 Weeks)

### Step 1: Collect 100+ Samples

**Minimum Dataset:**
- 50+ trades on markets with depth >$10K
- 50+ rejected markets with depth <$10K
- Track outcomes for both groups

### Step 2: Calculate Performance

**Metrics to Compare:**

**Group A (Deep Markets - Passed Filter):**
- Win rate: ??%
- Avg profit: ??%
- Slippage: ??%
- Manipulation events: ??

**Group B (Thin Markets - Rejected):**
- Win rate: ??%
- Avg profit: ??%
- Slippage: ??%
- Manipulation events: ??

**Statistical Test:**
- Chi-square test for win rate difference
- T-test for profit difference
- P-value < 0.05 = statistically significant

### Step 3: Decision Point

**If Group A > Group B by +5pp win rate:**
→ **KEEP FILTER** (validated, reduces risk)

**If Group A ≈ Group B (within 2pp):**
→ **REMOVE FILTER** (no benefit, reduces opportunities)

**If Group A < Group B:**
→ **REVERSE FILTER** (thin markets actually better!)

---

## 🔧 Running Analysis

**After collecting data for 2-4 weeks:**

```python
import json
import pandas as pd

# Load log file
with open('orderbook_depth_log.jsonl') as f:
    data = [json.loads(line) for line in f]

df = pd.DataFrame(data)

# Split into groups
deep_markets = df[df['passed_depth_filter'] == True]
thin_markets = df[df['passed_depth_filter'] == False]

# Calculate win rates (after outcomes are known)
deep_win_rate = deep_markets['outcome'].apply(lambda x: x == 'WIN').mean()
thin_win_rate = thin_markets['outcome'].apply(lambda x: x == 'WIN').mean()

print(f"Deep markets: {deep_win_rate:.1%} win rate ({len(deep_markets)} trades)")
print(f"Thin markets: {thin_win_rate:.1%} win rate ({len(thin_markets)} trades)")
print(f"Difference: {(deep_win_rate - thin_win_rate)*100:+.1f}pp")

# Statistical significance test
from scipy.stats import chi2_contingency

contingency = pd.crosstab(df['passed_depth_filter'], df['outcome'])
chi2, p_value, dof, expected = chi2_contingency(contingency)

print(f"P-value: {p_value:.4f} ({'significant' if p_value < 0.05 else 'not significant'})")
```

---

## 🚨 Important Notes

### This Is Forward Testing, Not Backtesting

❌ **We CANNOT backtest this strategy** - historical order book data doesn't exist  
✅ **We CAN validate it going forward** - collect data starting now

### $10K Threshold Is a Guess

**Why $10K?**
- Not proven - educated guess based on market microstructure theory
- May be too high (losing good opportunities)
- May be too low (still allowing manipulated markets)

**After validation:**
- Adjust threshold based on data (maybe $5K or $20K is optimal)
- Or remove filter entirely if no benefit

### Trade-off: Opportunity Cost

**Benefit:** Avoid bad markets (manipulation, slippage)  
**Cost:** Lose some good signals (fewer trades)

**Unknown until we measure:**
- How many signals do we reject? (10%? 50%?)
- Are those rejected signals actually worse?

---

## 📝 Next Steps

1. **Start logging immediately** (DONE - implemented in V2.1)
2. **Run signal detector daily** - accumulate samples
3. **Track outcomes** - update logs when markets resolve
4. **Week 2 checkpoint:** Review 50+ samples, preliminary analysis
5. **Week 4 decision:** Keep, adjust, or remove filter

---

## 🔍 Transparency

**What we know:**
- ✅ Order book depth is a valid theoretical signal
- ✅ API works, data is available
- ✅ Implementation is correct

**What we DON'T know:**
- ❌ Does this actually improve win rate on Polymarket?
- ❌ Is $10K the right threshold?
- ❌ How many opportunities do we lose?

**Solution:** Collect real data for 2-4 weeks, then decide based on HARD DATA.

---

**Last Updated:** 2026-02-07 04:20 PST  
**Status:** ACTIVE FORWARD TESTING  
**Expected Completion:** 2026-02-21 to 2026-03-07
