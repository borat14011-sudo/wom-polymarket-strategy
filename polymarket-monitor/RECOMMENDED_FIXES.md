# RECOMMENDED FIXES - Line-by-Line Code Changes

This document shows EXACTLY what needs to change in `backtest_fixed.py` to remove all biases.

---

## FIX #1: Remove Look-Ahead Direction Selection

### CURRENT CODE (backtest_fixed.py lines 67-73)
```python
# Calculate P&L based on which side we'd take
# If price is trending up, we buy YES
if outcome == 'Yes':
    pnl = exit_price - entry_price
else:
    pnl = -(exit_price - entry_price)
```

### PROBLEM
- Uses `outcome` (known from final price) to determine P&L calculation
- This is peeking at the future to decide bet direction
- In reality, we must commit to a direction BEFORE knowing the outcome

### FIXED CODE
```python
# ALWAYS bet YES on uptrend signal (no peeking!)
bet_side = 'Yes'

# Calculate P&L based on binary outcome
# Polymarket pays $1 if you win, $0 if you lose
if outcome == 'Yes':
    # We bet YES, outcome is YES → we win
    # Profit = payout - cost = $1 - entry_price
    pnl = 1.0 - entry_price
else:
    # We bet YES, outcome is NO → we lose
    # Profit = payout - cost = $0 - entry_price
    pnl = 0.0 - entry_price
```

**Impact:** Win rate drops from 95% to realistic 35-55%

---

## FIX #2: Realistic Exit Timing

### CURRENT CODE (backtest_fixed.py lines 52-54)
```python
# CRITICAL: Stop at -10 to simulate realistic exit timing
# (can't exit at the exact final price in reality)
max_entry_idx = len(prices) - 10

# ... later ...
# Exit: Simulate exit 5 data points before close
# (realistic - can't time the exact close)
exit_idx = len(prices) - 5
exit_price = prices[exit_idx].get('p', 0)
```

### PROBLEM
- Exit at `len(prices) - 5` is still ~95% of market lifetime
- Prices are already 92% converged to final outcome
- Nobody can trade at those prices (no liquidity)
- Creates artificially tiny losses

### FIXED CODE
```python
# Exit at 70% of market lifetime (realistic)
max_entry_idx = int(len(prices) * 0.7)

# ... later ...
# Exit at same 70% mark (can't time near resolution)
exit_idx = int(len(prices) * 0.7)
exit_price = prices[exit_idx].get('p', 0)  # Only for logging
```

**Impact:** Average loss increases from -$0.003 to realistic -$0.33 to -$0.38

---

## FIX #3: Correct P&L Formula

### CURRENT CODE (implicit in lines 67-73)
```python
pnl = exit_price - entry_price  # or -(exit_price - entry_price)
```

### PROBLEM
- Treats Polymarket like a stock market (profit = price difference)
- Only works if `exit_price` equals resolved price (0.9995 or ~0)
- This is another form of look-ahead bias!

### FIXED CODE
```python
# Binary outcome: Payout is $1 or $0, not a price
# Cost is entry_price (what we paid per share)
if outcome == bet_side:
    pnl = 1.0 - entry_price  # Win: payout $1
else:
    pnl = 0.0 - entry_price  # Lose: payout $0
```

**Impact:** Makes P&L independent of exit timing (binary outcome only)

---

## COMPLETE FIXED FUNCTION

Here's the full `backtest_trend_filter_fixed()` function with all fixes:

```python
def backtest_trend_filter_ACTUALLY_fixed(markets):
    """Trend Filter - ALL BIASES REMOVED"""
    
    trades = []
    skipped_ambiguous = 0
    skipped_no_signal = 0
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 30:
            continue
        
        final_price = prices[-1].get('p', 0)
        
        # Infer outcome (only for validation at the end)
        if final_price > 0.95:
            outcome = 'Yes'
        elif final_price < 0.05:
            outcome = 'No'
        else:
            skipped_ambiguous += 1
            continue
        
        # FIX #2: Realistic exit timing (70% of lifetime)
        max_entry_idx = int(len(prices) * 0.7)
        
        for i in range(5, max_entry_idx):
            current_price = prices[i].get('p', 0)
            prev_1 = prices[i-1].get('p', 0)
            prev_2 = prices[i-2].get('p', 0)
            prev_3 = prices[i-3].get('p', 0)
            
            if current_price > prev_1 > prev_2 > prev_3:
                entry_price = current_price
                
                # FIX #1: ALWAYS bet YES on uptrend (no peeking!)
                bet_side = 'Yes'
                
                # FIX #3: Binary P&L calculation
                if outcome == 'Yes':
                    pnl = 1.0 - entry_price  # Win
                else:
                    pnl = 0.0 - entry_price  # Lose
                
                win = pnl > 0
                
                trades.append({
                    'market': market['question'][:60],
                    'entry': entry_price,
                    'bet_side': bet_side,
                    'outcome': outcome,
                    'pnl': pnl,
                    'win': win
                })
                break
        else:
            skipped_no_signal += 1
    
    # Stats calculation remains the same
    total = len(trades)
    wins = len([t for t in trades if t['win']])
    losses = total - wins
    win_rate = wins / total * 100 if total > 0 else 0
    avg_pnl = sum(t['pnl'] for t in trades) / total if total > 0 else 0
    
    winning_trades = [t for t in trades if t['win']]
    losing_trades = [t for t in trades if not t['win']]
    avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
    
    return {
        'strategy': 'Trend Filter (ACTUALLY Fixed)',
        'trades': total,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'avg_pnl': avg_pnl,
        'avg_win': avg_win,
        'avg_loss': avg_loss
    }
```

---

## FIXES FOR OTHER STRATEGIES

The same biases likely appear in:
- `backtest_time_horizon_fixed()` (Strategy 2)
- `backtest_no_side_fixed()` (Strategy 3)

### Time Horizon Strategy - Fixes Needed

**Current exit:** `exit_idx = int(len(prices) * 0.9)` → Still too late!  
**Fix:** `exit_idx = int(len(prices) * 0.7)`

**Current P&L:**
```python
if entry_price > 0.5:
    if outcome == 'Yes':
        pnl = exit_price - entry_price
```

**Fix:**
```python
# Determine bet side from entry price (no peeking!)
bet_side = 'Yes' if entry_price > 0.5 else 'No'

# Binary P&L
if bet_side == 'Yes':
    pnl = (1.0 if outcome == 'Yes' else 0.0) - entry_price
else:
    pnl = (1.0 if outcome == 'No' else 0.0) - (1.0 - entry_price)
```

### NO-Side Bias Strategy - Fixes Needed

**Current P&L:**
```python
if outcome == 'No':
    pnl = exit_no_price - entry_no_price
else:
    pnl = exit_no_price - entry_no_price  # Same formula for both!
```

**Fix:**
```python
# We always bet NO on this signal
bet_side = 'No'
entry_no_price = 1 - entry_price

# Binary P&L for NO bet
if outcome == 'No':
    pnl = 1.0 - entry_no_price  # Win: payout $1, cost entry_no_price
else:
    pnl = 0.0 - entry_no_price  # Lose: payout $0, cost entry_no_price
```

---

## VALIDATION CHECKLIST

After applying fixes, verify:

✅ **Win rate is realistic (30-60%)**  
   - If >70%, still has look-ahead bias  
   - If <30%, strategy is broken or data is bad

✅ **Average win ≈ Average loss magnitude**  
   - Should be within 2x of each other  
   - If avg_loss is <0.1 while avg_win is >0.3, still biased

✅ **P&L doesn't depend on exit timing**  
   - Binary outcome means P&L is determined at entry + resolution  
   - Exit timing should only affect logging, not P&L

✅ **Strategy performance doesn't change if we shuffle test order**  
   - Look-ahead bias can create path dependence  
   - True walk-forward should be order-independent

✅ **Deliberately wrong signals lose money**  
   - Test by betting opposite direction  
   - If opposite direction still wins, you're still peeking!

---

## SUMMARY

**Three lines that need to change:**

1. **Line 52:** `max_entry_idx = len(prices) - 10` → `max_entry_idx = int(len(prices) * 0.7)`

2. **Line 56-57:** `exit_idx = len(prices) - 5` → `exit_idx = int(len(prices) * 0.7)`

3. **Lines 67-73:** Replace conditional P&L with:
   ```python
   bet_side = 'Yes'  # Always on uptrend
   if outcome == 'Yes':
       pnl = 1.0 - entry_price
   else:
       pnl = 0.0 - entry_price
   ```

**Result:** Win rate drops from 95% to ~35-55% (realistic)

---

## ADDITIONAL RESOURCES

- `backtest_ACTUALLY_fixed.py` - Working example with all fixes
- `bias_detector.py` - Automated bias detection
- `bias_validation_test.py` - Test suite to verify fixes

**To run tests:**
```bash
python bias_validation_test.py
```

Expected output: All tests PASS, win rate ~30-60%
