# AGENT 5 - QUICK REFERENCE GUIDE 📋

**For Main Agent: Critical findings at a glance**

---

## 🎯 TOP 5 ACTIONABLE INSIGHTS

### 1. **ONLY Trade Volatile Markets**
```
High Vol (>30¢ move):  59% win rate | +3.07 avg ROI ✅
Low Vol (<10¢ move):   29% win rate | -0.35 avg ROI ❌

RULE: Require 7-day price range >15¢ before entry
```

### 2. **Price Sweet Spot: 0.3-0.7**
```
0.3-0.5 range:  56% win rate | 0.12 Sharpe ✅
0.5-0.7 range:  62% win rate | 0.06 Sharpe ✅
<0.2 or >0.8:   26-43% win rate ❌ AVOID

RULE: Hard limit 0.30 ≤ entry ≤ 0.70
```

### 3. **24h Trend Filter = +12pp Win Rate**
```
WITH trend filter:     78% win rate
WITHOUT trend filter:  66% win rate

RULE: IF price ≤ price_24h_ago → SKIP TRADE
```

### 4. **Midnight Has Edge**
```
Hour 00 (midnight):  53% win rate ✅
Hour 12 (noon):      38% win rate ❌

RULE: Prefer entries at UTC 00-06, avoid 12-18
```

### 5. **Uncertain > Certain Markets**
```
"Uncertain" (0.4-0.6):       57% WR | 0.12 Sharpe | 30¢ moves ✅
"High Certainty" (<0.2/>0.8): 33% WR | 0.09 Sharpe | 16¢ moves ❌

RULE: Target markets near 50-50, not slam dunks
```

---

## ❌ TOP 5 RED FLAGS

1. **Entry <0.2 or >0.8** → 26-43% win rate (extreme consensus = trap)
2. **Price declining 24h** → Fails trend filter (negative info flow)
3. **Expected move <10¢** → 29% win rate (no edge in stable markets)
4. **Single strategy signal** → 40% WR vs 83% with confluence
5. **Midday entries (12-18 UTC)** → 38% WR vs 53% at midnight

---

## 📊 STRATEGY RANKINGS

| Strategy | Sharpe | Win Rate | Use Case |
|----------|--------|----------|----------|
| Whale Copy | 3.13 | 82% | **PRIMARY** - Follow smart money |
| Trend Filter | 2.56 | 57% | **CORE** - Momentum plays |
| NO-Side Bias | 2.55 | 11% | **LOTTERY** - Rare huge wins |
| Expert Fade | 1.99 | 14% | **CONTRARIAN** - Only at 0.6-0.8 |
| News Reversion | 1.88 | 57% | **VOLATILITY** - News overreactions |
| Pairs Trading | 0.88 | 55% | **SKIP** - Insufficient data |
| Time Horizon | -2.91 | 45% | **AVOID** - Broken strategy |

---

## ✅ ENTRY CHECKLIST

Must pass ALL before trading:

```python
✅ Price 0.30-0.70 (optimal zone)
✅ Price > price_24h_ago (trend filter)
✅ 7-day range >15¢ (volatility requirement)
✅ Hour 00-06 or 18-00 UTC (avoid midday)
✅ 2+ strategy signals (confluence)
✅ Expected move >12¢ (edge threshold)
```

**If ANY fail → SKIP TRADE**

---

## 💰 POSITION SIZING

**Base:** 10% per trade  
**Adjustments:**
- +5% if 3+ strategies agree
- +5% if in 0.5-0.7 range  
- -5% if edge of zone (0.3-0.4 or 0.6-0.7)
- -5% if first trade in new strategy

**Max:** 20% | **Min:** 5%

---

## 🎯 EXIT RULES

**Take Profit:**
- +20% (standard)
- +30% (high volatility markets)
- +50% (whale copy trades)

**Stop Loss:**
- -12% (standard)
- -18% (lottery strategies: NO-Side, Expert Fade)
- Immediate if -20¢ move against you in 24h

---

## 📈 EXPECTED PERFORMANCE

**With ALL Filters Applied:**
- Win Rate: 60-70%
- Sharpe Ratio: 2.0-3.0
- Max Drawdown: <5%
- Trades/Month: 15-25
- Avg ROI: +0.10 to +0.25 per trade

**Without Filters (Current Baseline):**
- Win Rate: 45%
- Sharpe Ratio: 0.5-1.0
- Max Drawdown: 8%
- Trades/Month: 60-90
- Avg ROI: -0.05 to +0.05

---

## 🚨 CRITICAL WARNINGS

### ⚠️ Data Quality
- Current analysis uses **SYNTHETIC** data
- MUST validate on real Polymarket outcomes
- Real markets may behave differently
- **DO NOT deploy capital until verified with real data**

### ⚠️ Failure Modes
- **Pump & Dumps:** 41% of volatile markets still lose (late entry)
- **Insider Trading:** Some extreme-priced markets are pre-positioned
- **Losing Streaks:** Max observed = 40 trades (Expert Fade at extremes)

### ⚠️ Missing Analysis
- No real volume data (only price proxies)
- No orderbook depth analysis  
- No spread/slippage calculations
- No whale wallet tracking

---

## 📋 IMMEDIATE TODOS

1. **Implement Trend Filter** (+12pp win rate)
2. **Add Price Range Limits** (0.3-0.7 only)
3. **Require Volatility Screen** (>15¢ 7-day range)
4. **Get Real Historical Data** (validate synthetic findings)
5. **Add CLOB API** (spreads, liquidity, depth)

---

## 🔬 RESEARCH QUESTIONS ANSWERED

### Q: What makes markets easier to trade?
**A:** Volatility (>15¢ moves) + Uncertainty (0.3-0.7 range) + Momentum (24h rising)

### Q: What are common failure modes?
**A:** Extreme consensus (<0.2/>0.8), low volatility, declining prices, midday noise

### Q: Volume/volatility relationship?
**A:** High-vol markets have 2x the win rate of low-vol (59% vs 29%)

### Q: Market inefficiencies to exploit?
**A:** Midnight edge (+14pp), trend persistence (+12pp), 0.6-0.8 sweet spot (+22pp WR)

### Q: Predictable vs random markets?
**A:** Predictable = 0.3-0.7 + volatile + rising. Random = extremes + stable + declining

---

## 📁 FULL REPORT

See `AGENT_5_MARKET_MICROSTRUCTURE_REPORT.md` for complete analysis (19KB, 500+ lines)

**Scripts:**
- `analyze_microstructure.py` - Price/ROI patterns
- `deep_pattern_analysis.py` - Market taxonomy

---

**Status:** ✅ MISSION COMPLETE  
**Key Insight:** Quality > Quantity. Filter ruthlessly. Trade only high-edge setups.
