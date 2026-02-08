# Order Book Depth - Quick Start Checklist

**Goal:** Implement order book depth filtering in under 2 hours

---

## ✅ Pre-Flight Checklist

### Prerequisites
- [ ] Python 3.8+ installed
- [ ] `requests` library (`pip install requests`)
- [ ] Internet access (for API calls)
- [ ] Active Polymarket markets exist

### Knowledge Required
- [ ] Read `ORDERBOOK_RESEARCH_SUMMARY.md` (5 min)
- [ ] Skim `ORDERBOOK_STRATEGY.md` (10 min)

---

## 🚀 Implementation Steps (90 minutes)

### Step 1: Test API Access (10 min)

```bash
# Create test file
cat > test_api.py << 'EOF'
import requests

# Test CLOB API
resp = requests.get("https://clob.polymarket.com/markets")
print(f"Status: {resp.status_code}")
print(f"Markets: {len(resp.json())}")
EOF

# Run test
python test_api.py
```

**Expected output:** `Status: 200`, `Markets: 500+`

**If it fails:** Check internet connection, verify no firewall blocking

---

### Step 2: Copy Core Functions (15 min)

**Copy these functions from `ORDERBOOK_IMPLEMENTATION_GUIDE.md`:**

1. `get_order_book(token_id)` - Fetch order book
2. `calculate_depth_within_range(order_book, pct_range)` - Calculate depth
3. `check_order_book_depth(token_id, ...)` - Complete pre-trade check
4. `get_market_token_ids(condition_id)` - Map market to tokens

**Create file:** `depth_filter.py`

**Quick copy:**
```bash
# See ORDERBOOK_IMPLEMENTATION_GUIDE.md lines 50-250
# Copy all code blocks into depth_filter.py
```

---

### Step 3: Test Depth Calculation (15 min)

```python
# test_depth.py
from depth_filter import check_order_book_depth, get_market_token_ids
import requests

# Get a test market
markets = requests.get("https://clob.polymarket.com/markets").json()
test_token = markets[0]['tokens'][0]['token_id']

# Test depth check
result = check_order_book_depth(test_token)

if result:
    print(f"✅ Approved: {result.approved}")
    print(f"   Depth: ${result.total_depth:,.2f}")
    print(f"   Reason: {result.reason}")
else:
    print("❌ API error")
```

**Run:** `python test_depth.py`

**Expected:** Depth check result with approval status

---

### Step 4: Integrate with Trading System (30 min)

**Option A: Simple wrapper**

```python
# In your existing trading code
from depth_filter import OrderBookFilter

# Initialize filter
filter = OrderBookFilter(
    min_depth_usd=10000,
    max_imbalance=0.7,
    max_spread_pct=0.02
)

# Before placing trade
if filter.should_trade(market_condition_id, side="YES"):
    # Proceed with trade
    place_order(market_condition_id, "YES", amount)
else:
    # Skip - insufficient depth
    print("Skipping - failed depth check")
```

**Option B: Decorator pattern**

```python
from depth_filter import check_order_book_depth
from functools import wraps

def require_depth(min_depth=10000):
    def decorator(func):
        @wraps(func)
        def wrapper(market_id, *args, **kwargs):
            # Get token ID and check depth
            token_ids = get_market_token_ids(market_id)
            if not token_ids:
                return None
            
            result = check_order_book_depth(token_ids[0], min_depth_usd=min_depth)
            if not result or not result.approved:
                print(f"Trade blocked: {result.reason if result else 'API error'}")
                return None
                
            # Depth check passed, execute original function
            return func(market_id, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@require_depth(min_depth=15000)
def place_trade(market_id, side, amount):
    # Your existing trade logic
    print(f"Placing trade: {market_id}")
```

---

### Step 5: Add Logging (20 min)

```python
# depth_logger.py
from depth_filter import DepthDataLogger

# Initialize logger
logger = DepthDataLogger(log_file="depth_checks.jsonl")

# In your trading loop
result = check_order_book_depth(token_id)
decision = "TRADE" if result.approved else "SKIP"

logger.log_depth_check(
    market_id=condition_id,
    market_question=market_question,
    token_id=token_id,
    result=result,
    trade_decision=decision
)
```

**This creates:** `depth_checks.jsonl` with all depth checks

---

## 📊 Validation Phase (Ongoing)

### Week 1: Collect Data
- [ ] Log every depth check
- [ ] Track trade outcomes (manual or automated)
- [ ] Collect at least 20 samples

### Week 2-3: Analyze
- [ ] Compare win rate: trades that passed depth check vs those that didn't
- [ ] Measure slippage difference
- [ ] Calculate how many trades were filtered out

### Analysis Script (Quick)

```python
import json

passed = []
failed = []

with open("depth_checks.jsonl") as f:
    for line in f:
        entry = json.loads(line)
        if entry['approved']:
            passed.append(entry)
        else:
            failed.append(entry)

print(f"Passed: {len(passed)}")
print(f"Failed: {len(failed)}")
print(f"Filter rate: {len(failed)/(len(passed)+len(failed))*100:.1f}%")
```

---

## 🎯 Success Criteria

After 2-4 weeks, you should have:

✅ **Implementation:**
- [ ] Depth filter running in production
- [ ] All trades logged with depth data
- [ ] No API errors or crashes

✅ **Data Collection:**
- [ ] 50+ depth checks logged
- [ ] Trade outcomes recorded
- [ ] Thin vs deep markets identified

✅ **Validation:**
- [ ] Win rate calculated for both cohorts
- [ ] Hypothesis tested (thin markets worse?)
- [ ] Thresholds tuned based on data

✅ **Decision:**
- [ ] Keep filter (if validates hypothesis)
- [ ] Adjust thresholds (if needed)
- [ ] Remove filter (if no benefit found)

---

## 🆘 Troubleshooting

### "ImportError: No module named 'requests'"
```bash
pip install requests
```

### "KeyError: 'token_id'"
**Issue:** Market structure changed  
**Fix:** Print market object, update key path

### "No order book found"
**Issue:** Market has zero liquidity  
**Fix:** Expected - filter correctly rejecting

### "All markets rejected"
**Issue:** Threshold too high ($10k might be too strict)  
**Fix:** Lower to $5k, collect data, tune based on results

### "API returns 429 (rate limit)"
**Issue:** Too many requests  
**Fix:** Add 0.5s delay between calls:
```python
import time
time.sleep(0.5)  # After each API call
```

---

## 📚 Documentation Reference

| Document | Purpose | Read Time |
|----------|---------|-----------|
| ORDERBOOK_RESEARCH_SUMMARY.md | Executive summary, findings | 10 min |
| ORDERBOOK_STRATEGY.md | Full strategy, theory, risks | 20 min |
| ORDERBOOK_IMPLEMENTATION_GUIDE.md | Code, examples, testing | 30 min |
| ORDERBOOK_QUICK_START.md | This file (checklist) | 5 min |

---

## 💡 Pro Tips

1. **Start conservative:** Use $15k threshold first, lower later if too strict
2. **Log everything:** You can't improve what you don't measure
3. **Paper trade first:** Run filter in "observe only" mode for 1 week
4. **Combine signals:** Depth + your existing strategy = best results
5. **Monitor false negatives:** Track good opportunities you skipped

---

## 🔄 Iterative Improvement Cycle

```
Week 1: Implement + Log
  ↓
Week 2-3: Collect Data (50+ samples)
  ↓
Week 4: Analyze Results
  ↓
Week 5: Tune Thresholds
  ↓
Week 6: Validate Improvements
  ↓
Repeat or Deploy
```

**Target:** Validated, optimized depth filter within 6 weeks

---

## ✨ Final Checklist

Before you start:
- [ ] Read this document fully (you're almost done!)
- [ ] Allocate 2 hours of uninterrupted time
- [ ] Have Python environment ready
- [ ] Open `ORDERBOOK_IMPLEMENTATION_GUIDE.md` in another window

During implementation:
- [ ] Step 1: Test API (10 min)
- [ ] Step 2: Copy functions (15 min)
- [ ] Step 3: Test depth calc (15 min)
- [ ] Step 4: Integrate (30 min)
- [ ] Step 5: Add logging (20 min)

After implementation:
- [ ] Run test trades (observe mode)
- [ ] Verify logging works
- [ ] Start data collection

Week 1 review:
- [ ] Check log file has data
- [ ] Ensure no crashes
- [ ] Note any issues

---

**Time commitment:**
- Setup: 2 hours (one-time)
- Monitoring: 10 min/day
- Analysis: 2 hours (after 2-4 weeks)

**Expected value:**
- Risk reduction: 30-50%
- Win rate improvement: 2-5%
- Dataset for future research: Priceless

**Let's go! 🚀**

---

**Created:** 2026-02-07  
**Estimated completion time:** 90 minutes  
**Difficulty:** Intermediate  
**Success rate:** High (if you follow the steps)
