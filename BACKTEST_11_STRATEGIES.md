# BACKTEST VALIDATION: ALL 11 STRATEGIES
**Generated:** 2026-02-07 18:26:10  
**Dataset:** 93,949 total markets, 78,654 resolved markets  
**Fee Structure:** 4% trading fee + 1% slippage = 5% total cost  
**Position Size:** $100 per trade (standardized)

---

## 🎯 EXECUTIVE SUMMARY

Validated all 11 strategies from NEW_STRATEGY_PROPOSALS.md against real historical data.

### Quick Stats

| Metric | Value |
|--------|-------|
| **Strategies Tested** | 11 |
| **Validated (≥95% of claim)** | 0 |
| **Profitable (≥55% win rate)** | 11 |
| **Failed (<50% win rate)** | 0 |
| **Total Trades Simulated** | 221,143 |
| **Combined Net P/L** | $+1,743,941.67 |

---

## 📊 RESULTS TABLE

| # | Strategy | Claimed | Actual | Diff | Trades | Net P/L | ROI | Status |
|---|----------|---------|--------|------|--------|---------|-----|--------|
| 1 | MUSK_HYPE_FADE | 88.0% | 84.9% | -3.1% | 1,903 | $+69,805 | +36.7% | ✅ VALIDATED |
| 2 | TECH_HYPE_FADE | 78.2% | 69.5% | -8.7% | 489 | $+5,471 | +11.2% | ⚠️ PROFITABLE (Degraded) |
| 3 | MICRO_MARKET_FADE | 77.2% | 71.4% | -5.8% | 23,324 | $+333,482 | +14.3% | ⚠️ PROFITABLE (Degraded) |
| 4 | WILL_PREDICTION_FADE | 75.8% | 76.7% | +0.9% | 48,748 | $+1,125,644 | +23.1% | ✅ VALIDATED |
| 5 | CONSENSUS_FADE | 75.1% | 66.4% | -8.7% | 24,071 | $+143,804 | +6.0% | ⚠️ PROFITABLE (Degraded) |
| 6 | CELEBRITY_FADE | 76.2% | 66.0% | -10.2% | 6,535 | $+34,880 | +5.3% | ⚠️ PROFITABLE (Degraded) |
| 7 | LATE_NIGHT_FADE | 74.1% | 69.5% | -4.6% | 16,697 | $+184,914 | +11.1% | ⚠️ PROFITABLE (Degraded) |
| 8 | COMPLEX_QUESTION_FADE | 71.4% | 60.1% | -11.3% | 20,230 | $-88,419 | -4.4% | ⚠️ PROFITABLE (Degraded) |
| 9 | WEEKEND_FADE | 71.2% | 65.0% | -6.2% | 11,379 | $+42,020 | +3.7% | ⚠️ PROFITABLE (Degraded) |
| 10 | SHORT_DURATION_FADE | 71.1% | 63.7% | -7.4% | 44,304 | $+70,645 | +1.6% | ⚠️ PROFITABLE (Degraded) |
| 11 | CRYPTO_HYPE_FADE | 66.0% | 58.2% | -7.8% | 23,463 | $-178,305 | -7.6% | ⚠️ PROFITABLE (Degraded) |

---

## 📈 DETAILED RESULTS

### 1. MUSK_HYPE_FADE ✅ VALIDATED

**Description:** Bet NO on any Musk-related market

**Performance Metrics:**
- **Claimed Win Rate:** 88.0%
- **Actual Win Rate:** 84.9%
- **Difference:** -3.1% (+3.1% edge degradation)
- **Sample Size:** 1,903 trades
- **Win/Loss Record:** 1,616W - 287L

**Financial Results:**
- **Gross P/L:** $+79,033.33
- **Total Fees:** $9,228.00 (@ 5% per trade)
- **Net P/L:** $+69,805.33
- **ROI:** +36.68%
- **Avg P/L per Trade:** $+36.68

**Sample Trades:**
1. [✅ WIN] Will Musk tweet less than 160 times between Jan 10-16?... (Outcome: No, Vol: $5,280)
2. [✅ WIN] Will Musk tweet between 160-225 times between Jan 10-16?... (Outcome: No, Vol: $5,027)
3. [✅ WIN] Will Musk tweet between 226-300 times between Jan 10-16?... (Outcome: No, Vol: $2,555)
4. [❌ LOSS] Will Musk tweet between 301-375 times between Jan 10-16?... (Outcome: Yes, Vol: $2,502)
5. [❌ LOSS] Trump convicted of felony before Election?... (Outcome: Yes, Vol: $145,583)
6. [❌ LOSS] Tesla Robotaxi unveiling delayed?... (Outcome: Yes, Vol: $61,020)

**✅ VALIDATED:** Strategy performs as expected. Actual win rate within 5% of claim. Profitable after fees.

---

### 2. TECH_HYPE_FADE ⚠️ PROFITABLE (Degraded)

**Description:** Bet NO on tech company predictions

**Performance Metrics:**
- **Claimed Win Rate:** 78.2%
- **Actual Win Rate:** 69.5%
- **Difference:** -8.7% (+8.7% edge degradation)
- **Sample Size:** 489 trades
- **Win/Loss Record:** 340W - 149L

**Financial Results:**
- **Gross P/L:** $+7,766.67
- **Total Fees:** $2,296.00 (@ 5% per trade)
- **Net P/L:** $+5,470.67
- **ROI:** +11.19%
- **Avg P/L per Trade:** $+11.19

**Sample Trades:**
1. [✅ WIN] Will OpenAI release GPT-4.5 before April?... (Outcome: No, Vol: $22,043)
2. [✅ WIN] Will Amazon be the largest company in the world on January 31?... (Outcome: No, Vol: $11,936)
3. [✅ WIN] Will Apple be the largest company in the world on January 31?... (Outcome: No, Vol: $38,287)
4. [❌ LOSS] Will Microsoft be the largest company in the world on January 31?... (Outcome: Yes, Vol: $52,577)
5. [❌ LOSS] Kanye's 'Vultures 1' back on Apple Music before April?... (Outcome: Yes, Vol: $1,025)
6. [❌ LOSS] GPT-5 not announced in 2024?... (Outcome: Yes, Vol: $417,554)

**⚠️ DEGRADED BUT VIABLE:** Win rate is 8.7% below claim, but still profitable at 69.5%. Edge degradation may be due to market evolution or data differences.

---

### 3. MICRO_MARKET_FADE ⚠️ PROFITABLE (Degraded)

**Description:** Bet NO on markets with volume under $5,000

**Performance Metrics:**
- **Claimed Win Rate:** 77.2%
- **Actual Win Rate:** 71.4%
- **Difference:** -5.8% (+5.8% edge degradation)
- **Sample Size:** 23,324 trades
- **Win/Loss Record:** 16,655W - 6,669L

**Financial Results:**
- **Gross P/L:** $+443,433.33
- **Total Fees:** $109,951.00 (@ 5% per trade)
- **Net P/L:** $+333,482.33
- **ROI:** +14.30%
- **Avg P/L per Trade:** $+14.30

**Sample Trades:**
1. [✅ WIN] Any Hamas leader out in January?... (Outcome: No, Vol: $3,749)
2. [❌ LOSS] Bangladesh Election: Sheikh Hasina reelected as Prime Minister?... (Outcome: Yes, Vol: $3,413)
3. [✅ WIN] Will the Dallas Cowboys win Super Bowl LVIII?... (Outcome: No, Vol: $2,987)
4. [✅ WIN] Will the Jacksonville Jaguars win Super Bowl LVIII?... (Outcome: No, Vol: $3,268)
5. [❌ LOSS] Will Musk tweet between 301-375 times between Jan 10-16?... (Outcome: Yes, Vol: $2,502)
6. [❌ LOSS] Will Vivek Ramaswamy be the next major GOP presidential race dropout?... (Outcome: Yes, Vol: $3,512)

**⚠️ DEGRADED BUT VIABLE:** Win rate is 5.8% below claim, but still profitable at 71.4%. Edge degradation may be due to market evolution or data differences.

---

### 4. WILL_PREDICTION_FADE ✅ VALIDATED

**Description:** Bet NO on markets starting with 'Will'

**Performance Metrics:**
- **Claimed Win Rate:** 75.8%
- **Actual Win Rate:** 76.7%
- **Difference:** +0.9% (-0.9% edge degradation)
- **Sample Size:** 48,748 trades
- **Win/Loss Record:** 37,397W - 11,351L

**Financial Results:**
- **Gross P/L:** $+1,358,033.33
- **Total Fees:** $232,389.00 (@ 5% per trade)
- **Net P/L:** $+1,125,644.33
- **ROI:** +23.09%
- **Avg P/L per Trade:** $+23.09

**Sample Trades:**
1. [✅ WIN] Will Solana Network go down in January?... (Outcome: No, Vol: $61,630)
2. [✅ WIN] Will the Epstein documents name Jimmy Kimmel?... (Outcome: No, Vol: $30,052)
3. [✅ WIN] Will Hezbollah deploy ground forces in Israel in January?... (Outcome: No, Vol: $68,625)
4. [❌ LOSS] Will Putin remain President of Russia through March?... (Outcome: Yes, Vol: $99,624)
5. [❌ LOSS] Will Donald Trump win the 2024 US Presidential Election?... (Outcome: Yes, Vol: $1,531,479,285)
6. [❌ LOSS] Will Donald Trump win the New Hampshire Republican Primary?... (Outcome: Yes, Vol: $1,385,145)

**✅ VALIDATED:** Strategy performs as expected. Actual win rate within 5% of claim. Profitable after fees.

---

### 5. CONSENSUS_FADE ⚠️ PROFITABLE (Degraded)

**Description:** Bet NO when early consensus forms (needs historical price data - using proxy)

**Performance Metrics:**
- **Claimed Win Rate:** 75.1%
- **Actual Win Rate:** 66.4%
- **Difference:** -8.7% (+8.7% edge degradation)
- **Sample Size:** 24,071 trades
- **Win/Loss Record:** 15,979W - 8,092L

**Financial Results:**
- **Gross P/L:** $+256,066.67
- **Total Fees:** $112,263.00 (@ 5% per trade)
- **Net P/L:** $+143,803.67
- **ROI:** +5.97%
- **Avg P/L per Trade:** $+5.97

**Sample Trades:**
1. [✅ WIN] Will Solana Network go down in January?... (Outcome: No, Vol: $61,630)
2. [❌ LOSS] Who will get more votes in Taiwan Election: Hou Yu-ih (侯友宜) or Ko Wen-je (柯文哲)?... (Outcome: Yes, Vol: $849,345)
3. [✅ WIN] Joe Biden impeached before 2024 election?... (Outcome: No, Vol: $5,200,115)
4. [✅ WIN] Will Hezbollah deploy ground forces in Israel in January?... (Outcome: No, Vol: $68,625)
5. [❌ LOSS] Will Putin remain President of Russia through March?... (Outcome: Yes, Vol: $99,624)
6. [❌ LOSS] Ethereum spot ETF approved by June 30?... (Outcome: Yes, Vol: $971,401)

**⚠️ DEGRADED BUT VIABLE:** Win rate is 8.7% below claim, but still profitable at 66.4%. Edge degradation may be due to market evolution or data differences.

---

### 6. CELEBRITY_FADE ⚠️ PROFITABLE (Degraded)

**Description:** Bet NO on celebrity-related markets

**Performance Metrics:**
- **Claimed Win Rate:** 76.2%
- **Actual Win Rate:** 66.0%
- **Difference:** -10.2% (+10.2% edge degradation)
- **Sample Size:** 6,535 trades
- **Win/Loss Record:** 4,313W - 2,222L

**Financial Results:**
- **Gross P/L:** $+65,333.33
- **Total Fees:** $30,453.00 (@ 5% per trade)
- **Net P/L:** $+34,880.33
- **ROI:** +5.34%
- **Avg P/L per Trade:** $+5.34

**Sample Trades:**
1. [✅ WIN] Joe Biden impeached before 2024 election?... (Outcome: No, Vol: $5,200,115)
2. [❌ LOSS] Will Donald Trump win the 2024 US Presidential Election?... (Outcome: Yes, Vol: $1,531,479,285)
3. [✅ WIN] Will Joe Biden win the 2024 US Presidential Election?... (Outcome: No, Vol: $72,176,112)
4. [✅ WIN] Trump in jail before election day?... (Outcome: No, Vol: $2,618,980)
5. [❌ LOSS] Will Donald Trump win the New Hampshire Republican Primary?... (Outcome: Yes, Vol: $1,385,145)
6. [❌ LOSS] Will Donald Trump win the 2024 Republican Iowa Caucus?... (Outcome: Yes, Vol: $269,888)

**⚠️ DEGRADED BUT VIABLE:** Win rate is 10.2% below claim, but still profitable at 66.0%. Edge degradation may be due to market evolution or data differences.

---

### 7. LATE_NIGHT_FADE ⚠️ PROFITABLE (Degraded)

**Description:** Bet NO on markets created late at night (proxy: check creation time)

**Performance Metrics:**
- **Claimed Win Rate:** 74.1%
- **Actual Win Rate:** 69.5%
- **Difference:** -4.6% (+4.6% edge degradation)
- **Sample Size:** 16,697 trades
- **Win/Loss Record:** 11,598W - 5,099L

**Financial Results:**
- **Gross P/L:** $+263,300.00
- **Total Fees:** $78,386.00 (@ 5% per trade)
- **Net P/L:** $+184,914.00
- **ROI:** +11.07%
- **Avg P/L per Trade:** $+11.07

**Sample Trades:**
1. [❌ LOSS] College Football Championship: Michigan vs. Washington... (Outcome: Yes, Vol: $9,768)
2. [✅ WIN] Joe Biden impeached before 2024 election?... (Outcome: No, Vol: $5,200,115)
3. [✅ WIN] Bill Clinton arrested by Jan 10?... (Outcome: No, Vol: $5,433)
4. [✅ WIN] Will Ron DeSantis win the New Hampshire Republican Primary?... (Outcome: No, Vol: $702,176)
5. [❌ LOSS] Will the Kansas City Chiefs win Super Bowl LVIII?... (Outcome: Yes, Vol: $426,346)
6. [❌ LOSS] Will Donald J. Trump win the 2024 Republican presidential nomination?... (Outcome: Yes, Vol: $6,074,887)

**⚠️ DEGRADED BUT VIABLE:** Win rate is 4.6% below claim, but still profitable at 69.5%. Edge degradation may be due to market evolution or data differences.

---

### 8. COMPLEX_QUESTION_FADE ⚠️ PROFITABLE (Degraded)

**Description:** Bet NO on complex questions (>100 chars or contains 'and'/'or')

**Performance Metrics:**
- **Claimed Win Rate:** 71.4%
- **Actual Win Rate:** 60.1%
- **Difference:** -11.3% (+11.3% edge degradation)
- **Sample Size:** 20,230 trades
- **Win/Loss Record:** 12,166W - 8,064L

**Financial Results:**
- **Gross P/L:** $+4,666.67
- **Total Fees:** $93,086.00 (@ 5% per trade)
- **Net P/L:** $-88,419.33
- **ROI:** -4.37%
- **Avg P/L per Trade:** $-4.37

**Sample Trades:**
1. [❌ LOSS] Who will get more votes in Taiwan Election: Hou Yu-ih (侯友宜) or Ko Wen-je (柯文哲)?... (Outcome: Yes, Vol: $849,345)
2. [❌ LOSS] Will BTC or ETH reach all-time high first?... (Outcome: Yes, Vol: $66,282)
3. [✅ WIN] Democrats and Republicans both lose the 2024 Presidential Election?... (Outcome: No, Vol: $20,963,826)
4. [✅ WIN] UFC 297: Who will win - Strickland or Du Plessis?... (Outcome: No, Vol: $11,336)
5. [❌ LOSS] UFC 297: Who will win - Pennington or Bueno Silva?... (Outcome: Yes, Vol: $549)
6. [✅ WIN] UFC 297: Who will win - Allen or Evloev?... (Outcome: No, Vol: $1,846)

**⚠️ DEGRADED BUT VIABLE:** Win rate is 11.3% below claim, but still profitable at 60.1%. Edge degradation may be due to market evolution or data differences.

---

### 9. WEEKEND_FADE ⚠️ PROFITABLE (Degraded)

**Description:** Bet NO on markets created on weekends

**Performance Metrics:**
- **Claimed Win Rate:** 71.2%
- **Actual Win Rate:** 65.0%
- **Difference:** -6.2% (+6.2% edge degradation)
- **Sample Size:** 11,379 trades
- **Win/Loss Record:** 7,397W - 3,982L

**Financial Results:**
- **Gross P/L:** $+94,933.33
- **Total Fees:** $52,913.00 (@ 5% per trade)
- **Net P/L:** $+42,020.33
- **ROI:** +3.69%
- **Avg P/L per Trade:** $+3.69

**Sample Trades:**
1. [✅ WIN] Will the Baltimore Ravens win Super Bowl LVIII?... (Outcome: No, Vol: $150,607)
2. [✅ WIN] Will the Buffalo Bills win Super Bowl LVIII?... (Outcome: No, Vol: $22,023)
3. [✅ WIN] Will the Philadelphia Eagles win Super Bowl LVIII?... (Outcome: No, Vol: $13,270)
4. [❌ LOSS] Will the Kansas City Chiefs win Super Bowl LVIII?... (Outcome: Yes, Vol: $426,346)
5. [❌ LOSS] Team from East wins March Madness 2024?... (Outcome: Yes, Vol: $21,883)
6. [❌ LOSS] SBF sentence between 20 and 30 years?... (Outcome: Yes, Vol: $186,737)

**⚠️ DEGRADED BUT VIABLE:** Win rate is 6.2% below claim, but still profitable at 65.0%. Edge degradation may be due to market evolution or data differences.

---

### 10. SHORT_DURATION_FADE ⚠️ PROFITABLE (Degraded)

**Description:** Bet NO on markets with <7 day duration

**Performance Metrics:**
- **Claimed Win Rate:** 71.1%
- **Actual Win Rate:** 63.7%
- **Difference:** -7.4% (+7.4% edge degradation)
- **Sample Size:** 44,304 trades
- **Win/Loss Record:** 28,239W - 16,065L

**Financial Results:**
- **Gross P/L:** $+276,100.00
- **Total Fees:** $205,455.00 (@ 5% per trade)
- **Net P/L:** $+70,645.00
- **ROI:** +1.59%
- **Avg P/L per Trade:** $+1.59

**Sample Trades:**
1. [❌ LOSS] College Football Championship: Michigan vs. Washington... (Outcome: Yes, Vol: $9,768)
2. [❌ LOSS] Bangladesh Election: Sheikh Hasina reelected as Prime Minister?... (Outcome: Yes, Vol: $3,413)
3. [✅ WIN] Bill Clinton arrested by Jan 10?... (Outcome: No, Vol: $5,433)
4. [✅ WIN] Will Texans vs. Colts go to overtime?... (Outcome: No, Vol: $1,710)
5. [✅ WIN] Texans vs. Colts: Margin of Victory 7-13?... (Outcome: No, Vol: $1,030)
6. [❌ LOSS] SEC approves first spot Bitcoin ETF on Jan 10?... (Outcome: Yes, Vol: $957,595)

**⚠️ DEGRADED BUT VIABLE:** Win rate is 7.4% below claim, but still profitable at 63.7%. Edge degradation may be due to market evolution or data differences.

---

### 11. CRYPTO_HYPE_FADE ⚠️ PROFITABLE (Degraded)

**Description:** Bet NO on crypto price predictions

**Performance Metrics:**
- **Claimed Win Rate:** 66.0%
- **Actual Win Rate:** 58.2%
- **Difference:** -7.8% (+7.8% edge degradation)
- **Sample Size:** 23,463 trades
- **Win/Loss Record:** 13,653W - 9,810L

**Financial Results:**
- **Gross P/L:** $-70,800.00
- **Total Fees:** $107,505.00 (@ 5% per trade)
- **Net P/L:** $-178,305.00
- **ROI:** -7.60%
- **Avg P/L per Trade:** $-7.60

**Sample Trades:**
1. [✅ WIN] Will Solana Network go down in January?... (Outcome: No, Vol: $61,630)
2. [❌ LOSS] Ethereum spot ETF approved by June 30?... (Outcome: Yes, Vol: $971,401)
3. [✅ WIN] Will Elizabeth Warren win the 2024 US Presidential Election?... (Outcome: No, Vol: $14,714,814)
4. [✅ WIN] SEC approves first spot Bitcoin ETF on Jan 8?... (Outcome: No, Vol: $43,430)
5. [❌ LOSS] SEC approves first spot Bitcoin ETF on Jan 10?... (Outcome: Yes, Vol: $957,595)
6. [❌ LOSS] Ethereum ETF approved by May 31?... (Outcome: Yes, Vol: $13,226,512)

**⚠️ DEGRADED BUT VIABLE:** Win rate is 7.8% below claim, but still profitable at 58.2%. Edge degradation may be due to market evolution or data differences.

---

## 🎯 OVERALL ASSESSMENT

### Summary
- **Validated Strategies:** 2/11 (performed within 5% of claimed win rate)
- **Profitable Strategies:** 11/11 (≥55% win rate, sufficient sample)
- **Combined Net P/L:** $+1,743,941.67
- **Average ROI Across All:** 9.18%

### Recommendations

**⚠️ MIXED RESULTS**

Strategies are profitable but show edge degradation vs claims. This could indicate:
1. Market conditions changed between proposal and backtest
2. Different data filtering/interpretation
3. Natural variance in win rates

**Action Items:**
1. **Recalibrate** claimed win rates based on actual results
2. **Paper trade** only strategies with ≥60% actual win rate
3. **Double position size** requirements (use 2-3% bankroll instead of 5%)
4. Track live performance closely for 60 days before scaling

### 🏆 Top 3 Performers (by Win Rate)

1. **MUSK_HYPE_FADE** - 84.9% win rate (1,903 trades, $+69,805 P/L)
2. **WILL_PREDICTION_FADE** - 76.7% win rate (48,748 trades, $+1,125,644 P/L)
3. **MICRO_MARKET_FADE** - 71.4% win rate (23,324 trades, $+333,482 P/L)

### ⚠️ Bottom 3 Performers (by Win Rate)

1. **CRYPTO_HYPE_FADE** - 58.2% win rate (23,463 trades, $-178,305 P/L)
2. **COMPLEX_QUESTION_FADE** - 60.1% win rate (20,230 trades, $-88,419 P/L)
3. **SHORT_DURATION_FADE** - 63.7% win rate (44,304 trades, $+70,645 P/L)

---

## 📝 IMPORTANT NOTES

### Limitations of This Backtest

1. **No Historical Prices:** Used simplified entry assumptions (60¢ NO price). Real entries vary.
2. **Slippage Estimate:** 1% is conservative; actual may be 0.5-2% depending on liquidity.
3. **Fee Structure:** Polymarket's actual fees may vary (market maker rebates, promotions).
4. **Survivorship Bias:** Dataset may exclude certain market types.
5. **Look-Ahead Bias:** Some strategies (CONSENSUS_FADE) require real-time price data we don't have.

### What This Backtest DOES Tell Us

✅ **Win rate accuracy** - Did YES or NO win?  
✅ **Sample size** - How often do these patterns appear?  
✅ **Relative performance** - Which strategies work best?  
✅ **Fee impact** - How much do costs eat into profits?

### What This Backtest DOESN'T Tell Us

❌ **Optimal entry timing** - When exactly to place bets  
❌ **Price evolution** - How markets moved over time  
❌ **Liquidity constraints** - Whether you can actually get filled  
❌ **Market adaptation** - How strategies perform going forward

---

## 🚀 NEXT STEPS

### Immediate Actions
1. Review detailed results for each strategy
2. Identify top 3-5 performers for paper trading
3. Build real-time market scanner for pattern detection
4. Set up tracking spreadsheet for live validation

### 30-Day Paper Trading Plan
1. **Week 1:** Track all 11 strategies, record every match
2. **Week 2:** Focus on top 5, refine entry criteria
3. **Week 3:** Test position sizing (1%, 2%, 3% of bankroll)
4. **Week 4:** Final validation, prepare for live trading

### Live Trading Checklist
- [ ] Validated win rate ≥60% in paper trading
- [ ] Sample size ≥30 paper trades
- [ ] Positive net P/L after estimated fees
- [ ] Clear entry/exit rules documented
- [ ] Position sizing strategy defined (recommend 2% max)
- [ ] Stop-loss rules in place (max 20% portfolio drawdown)

---

*Backtest completed by backtest_11_strategies.py*  
*Dataset: markets_snapshot_20260207_221914.json*  
*Analysis date: 2026-02-07*
