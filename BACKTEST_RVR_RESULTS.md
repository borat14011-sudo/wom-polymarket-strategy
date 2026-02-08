# Polymarket RVR Strategy Backtest Results

**Generated:** 2026-02-06 16:57:08

## Strategy Overview

**Entry Criteria:**
- RVR (Relative Volume Ratio) >= Threshold
- ROC (Rate of Change, 12h) >= 10%

**Exit Criteria:**
- Stop Loss: -12%
- Take Profit Levels: +20%, +30%, +50%

---

## Performance Comparison by Threshold

| Threshold | Total Trades | Win Rate | Avg Return | Max Drawdown | Total Return | Final Capital |
|-----------|--------------|----------|------------|--------------|--------------|---------------|
| **1.5x** | 985 | 42.5% | +2.01% | -19.10% | +197.70% | $29,770.27 |
| **2.0x** | 740 | 43.0% | +2.28% | -23.69% | +169.04% | $26,903.78 |
| **2.5x** | 580 | 42.2% | +2.46% | -29.83% | +142.81% | $24,281.15 |
| **3.0x** | 461 | 41.4% | +1.74% | -26.57% | +80.22% | $18,022.02 |
| **4.0x** | 303 | 44.2% | +3.11% | -16.44% | +94.11% | $19,410.76 |

---

## Detailed Analysis by Threshold

### 1.5x Volume Spike Threshold

**Performance Metrics:**
- Total Trades: 985
- Profitable Trades: 419 (42.5%)
- Losing Trades: 566
- Average Return per Trade: +2.01%
- Average Win: +30.62%
- Average Loss: -19.18%
- Maximum Drawdown: -19.10%
- Total Return: +197.70%
- Final Capital: $29,770.27

**Best Trade:**
- Market: Spread: Celtics (-6.5)
- Entry: 0.056 | Exit: 0.285
- Return: +404.79%
- Exit Reason: Take Profit 20.0%

**Worst Trade:**
- Market: Will Athletic Bilbao win the 2025–26 La Liga?
- Entry: 0.206 | Exit: 0.001
- Return: -99.52%
- Exit Reason: Stop Loss

**Sample Trades (first 5):**

1. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.180 @ 2026-01-08 16:57
   - Exit: 0.152 @ 2026-01-08 21:57
   - RVR: 1.85 | ROC: +10.9%
   - Return: -15.13% | Exit: Stop Loss

2. ✅ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.152 @ 2026-01-08 21:57
   - Exit: 0.195 @ 2026-01-09 04:57
   - RVR: 5.57 | ROC: -24.4%
   - Return: +28.00% | Exit: Take Profit 20.0%

3. ✅ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.216 @ 2026-01-09 08:57
   - Exit: 0.262 @ 2026-01-09 12:57
   - RVR: 8.72 | ROC: +23.1%
   - Return: +21.73% | Exit: Take Profit 20.0%

4. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.262 @ 2026-01-09 12:57
   - Exit: 0.221 @ 2026-01-09 13:57
   - RVR: 3.23 | ROC: +64.9%
   - Return: -15.72% | Exit: Stop Loss

5. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.221 @ 2026-01-09 13:57
   - Exit: 0.167 @ 2026-01-09 15:57
   - RVR: 3.35 | ROC: +38.9%
   - Return: -24.43% | Exit: Stop Loss

---

### 2.0x Volume Spike Threshold

**Performance Metrics:**
- Total Trades: 740
- Profitable Trades: 318 (43.0%)
- Losing Trades: 422
- Average Return per Trade: +2.28%
- Average Win: +30.55%
- Average Loss: -19.02%
- Maximum Drawdown: -23.69%
- Total Return: +169.04%
- Final Capital: $26,903.78

**Best Trade:**
- Market: Spread: Celtics (-6.5)
- Entry: 0.056 | Exit: 0.285
- Return: +404.79%
- Exit Reason: Take Profit 20.0%

**Worst Trade:**
- Market: Will Athletic Bilbao win the 2025–26 La Liga?
- Entry: 0.206 | Exit: 0.001
- Return: -99.52%
- Exit Reason: Stop Loss

**Sample Trades (first 5):**

1. ✅ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.152 @ 2026-01-08 21:57
   - Exit: 0.195 @ 2026-01-09 04:57
   - RVR: 5.57 | ROC: -24.4%
   - Return: +28.00% | Exit: Take Profit 20.0%

2. ✅ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.216 @ 2026-01-09 08:57
   - Exit: 0.262 @ 2026-01-09 12:57
   - RVR: 8.72 | ROC: +23.1%
   - Return: +21.73% | Exit: Take Profit 20.0%

3. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.262 @ 2026-01-09 12:57
   - Exit: 0.221 @ 2026-01-09 13:57
   - RVR: 3.23 | ROC: +64.9%
   - Return: -15.72% | Exit: Stop Loss

4. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.221 @ 2026-01-09 13:57
   - Exit: 0.167 @ 2026-01-09 15:57
   - RVR: 3.35 | ROC: +38.9%
   - Return: -24.43% | Exit: Stop Loss

5. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.147 @ 2026-01-09 16:57
   - Exit: 0.126 @ 2026-01-09 18:57
   - RVR: 2.86 | ROC: -24.6%
   - Return: -14.54% | Exit: Stop Loss

---

### 2.5x Volume Spike Threshold

**Performance Metrics:**
- Total Trades: 580
- Profitable Trades: 245 (42.2%)
- Losing Trades: 335
- Average Return per Trade: +2.46%
- Average Win: +31.89%
- Average Loss: -19.06%
- Maximum Drawdown: -29.83%
- Total Return: +142.81%
- Final Capital: $24,281.15

**Best Trade:**
- Market: Spread: Celtics (-6.5)
- Entry: 0.056 | Exit: 0.285
- Return: +404.79%
- Exit Reason: Take Profit 20.0%

**Worst Trade:**
- Market: Will Athletic Bilbao win the 2025–26 La Liga?
- Entry: 0.206 | Exit: 0.001
- Return: -99.52%
- Exit Reason: Stop Loss

**Sample Trades (first 5):**

1. ✅ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.152 @ 2026-01-08 21:57
   - Exit: 0.195 @ 2026-01-09 04:57
   - RVR: 5.57 | ROC: -24.4%
   - Return: +28.00% | Exit: Take Profit 20.0%

2. ✅ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.216 @ 2026-01-09 08:57
   - Exit: 0.262 @ 2026-01-09 12:57
   - RVR: 8.72 | ROC: +23.1%
   - Return: +21.73% | Exit: Take Profit 20.0%

3. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.262 @ 2026-01-09 12:57
   - Exit: 0.221 @ 2026-01-09 13:57
   - RVR: 3.23 | ROC: +64.9%
   - Return: -15.72% | Exit: Stop Loss

4. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.221 @ 2026-01-09 13:57
   - Exit: 0.167 @ 2026-01-09 15:57
   - RVR: 3.35 | ROC: +38.9%
   - Return: -24.43% | Exit: Stop Loss

5. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.147 @ 2026-01-09 16:57
   - Exit: 0.126 @ 2026-01-09 18:57
   - RVR: 2.86 | ROC: -24.6%
   - Return: -14.54% | Exit: Stop Loss

---

### 3.0x Volume Spike Threshold

**Performance Metrics:**
- Total Trades: 461
- Profitable Trades: 191 (41.4%)
- Losing Trades: 270
- Average Return per Trade: +1.74%
- Average Win: +30.42%
- Average Loss: -18.55%
- Maximum Drawdown: -26.57%
- Total Return: +80.22%
- Final Capital: $18,022.02

**Best Trade:**
- Market: Will the Fed increase interest rates by 25+ bps after the March 2026 meeting?
- Entry: 0.050 | Exit: 0.091
- Return: +82.81%
- Exit Reason: Take Profit 20.0%

**Worst Trade:**
- Market: Will Athletic Bilbao win the 2025–26 La Liga?
- Entry: 0.220 | Exit: 0.001
- Return: -99.55%
- Exit Reason: Stop Loss

**Sample Trades (first 5):**

1. ✅ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.152 @ 2026-01-08 21:57
   - Exit: 0.195 @ 2026-01-09 04:57
   - RVR: 5.57 | ROC: -24.4%
   - Return: +28.00% | Exit: Take Profit 20.0%

2. ✅ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.216 @ 2026-01-09 08:57
   - Exit: 0.262 @ 2026-01-09 12:57
   - RVR: 8.72 | ROC: +23.1%
   - Return: +21.73% | Exit: Take Profit 20.0%

3. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.262 @ 2026-01-09 12:57
   - Exit: 0.221 @ 2026-01-09 13:57
   - RVR: 3.23 | ROC: +64.9%
   - Return: -15.72% | Exit: Stop Loss

4. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.221 @ 2026-01-09 13:57
   - Exit: 0.167 @ 2026-01-09 15:57
   - RVR: 3.35 | ROC: +38.9%
   - Return: -24.43% | Exit: Stop Loss

5. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.365 @ 2026-01-11 05:57
   - Exit: 0.314 @ 2026-01-11 14:57
   - RVR: 3.10 | ROC: +57.6%
   - Return: -13.77% | Exit: Stop Loss

---

### 4.0x Volume Spike Threshold

**Performance Metrics:**
- Total Trades: 303
- Profitable Trades: 134 (44.2%)
- Losing Trades: 169
- Average Return per Trade: +3.11%
- Average Win: +29.92%
- Average Loss: -18.15%
- Maximum Drawdown: -16.44%
- Total Return: +94.11%
- Final Capital: $19,410.76

**Best Trade:**
- Market: Will the Fed increase interest rates by 25+ bps after the March 2026 meeting?
- Entry: 0.050 | Exit: 0.091
- Return: +82.81%
- Exit Reason: Take Profit 20.0%

**Worst Trade:**
- Market: Grizzlies vs. Trail Blazers
- Entry: 0.616 | Exit: 0.245
- Return: -60.24%
- Exit Reason: Stop Loss

**Sample Trades (first 5):**

1. ✅ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.152 @ 2026-01-08 21:57
   - Exit: 0.195 @ 2026-01-09 04:57
   - RVR: 5.57 | ROC: -24.4%
   - Return: +28.00% | Exit: Take Profit 20.0%

2. ✅ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.216 @ 2026-01-09 08:57
   - Exit: 0.262 @ 2026-01-09 12:57
   - RVR: 8.72 | ROC: +23.1%
   - Return: +21.73% | Exit: Take Profit 20.0%

3. ❌ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.307 @ 2026-01-11 15:57
   - Exit: 0.266 @ 2026-01-12 04:57
   - RVR: 11.78 | ROC: -15.0%
   - Return: -13.31% | Exit: Stop Loss

4. ✅ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.243 @ 2026-01-12 19:57
   - Exit: 0.300 @ 2026-01-13 00:57
   - RVR: 7.79 | ROC: -21.2%
   - Return: +23.29% | Exit: Take Profit 20.0%

5. ✅ **Will the Fed decrease interest rates by 50+ bps af**
   - Entry: 0.319 @ 2026-01-13 01:57
   - Exit: 0.383 @ 2026-01-13 22:57
   - RVR: 5.54 | ROC: +14.1%
   - Return: +20.20% | Exit: Take Profit 20.0%

---

## Recommendations

**Optimal Threshold: 1.5x**

Based on total return (+197.70%), the 1.5x threshold provides the best risk-adjusted performance with:
- Win Rate: 42.5%
- Average Return: +2.01%
- Max Drawdown: -19.10%

**Key Insights:**

1. **Trade Frequency:** Lower thresholds (1.5x) generate more signals (985 trades) but may have more false positives. Higher thresholds (4.0x) are more selective (303 trades) but may miss opportunities.

2. **Win Rate:** The 4.0x threshold achieved the highest win rate (44.2%), suggesting stronger signal quality at this level.

3. **Risk Management:** The 4.0x threshold showed the lowest maximum drawdown (-16.44%), indicating better risk control.


---

*Note: This backtest uses simulated historical data. Real results may vary. Always conduct forward testing before live trading.*
