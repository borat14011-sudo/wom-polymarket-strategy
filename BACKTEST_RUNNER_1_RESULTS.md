# BACKTEST RUNNER 1 - FINAL REPORT
**Generated:** 2026-02-08 14:11:22  
**Dataset:** RESOLVED_DATA_FIXED.json (500 Real Resolved Markets)  
**Fee Structure:** 4% trading fee + 1% slippage  
**Position Size:** $100 per trade

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Total Strategies Tested** | 19 |
| **Validated (>=95% of claim)** | 5 |
| **Profitable (>=55% win rate)** | 11 |
| **Failed (<50% win rate)** | 3 |
| **Total Trades Simulated** | 2,631 |
| **Combined Net P/L** | $-25,952.33 |

---

## SURVIVING STRATEGIES (Actual Win Rate >= 55%)

### 1. FAVORITE_WINS [[OK]]
- **Actual Win Rate:** 100.0% (Claimed: 95.0%)
- **Trades:** 149 (149W / 0L)
- **Net P/L:** $+9,188.33 (ROI: +61.7%)
- **Description:** Bet on favorite (>50% initial price) - validates market efficiency

### 2. SPORTS_FADE [[OK]]
- **Actual Win Rate:** 79.7% (Claimed: 68.0%)
- **Trades:** 64 (51W / 13L)
- **Net P/L:** $+1,793.00 (ROI: +28.0%)
- **Description:** Bet NO on sports outcome predictions

### 3. CRYPTO_HYPE_FADE [[OK]]
- **Actual Win Rate:** 72.7% (Claimed: 66.0%)
- **Trades:** 55 (40W / 15L)
- **Net P/L:** $+906.67 (ROI: +16.5%)
- **Description:** Bet NO on crypto price predictions

### 4. US_MARKETS_FADE [[OK]]
- **Actual Win Rate:** 70.0% (Claimed: 71.0%)
- **Trades:** 30 (21W / 9L)
- **Net P/L:** $+359.00 (ROI: +12.0%)
- **Description:** Bet NO on US-specific markets

### 5. HIGH_VOLUME_FADE [[OK]]
- **Actual Win Rate:** 68.4% (Claimed: 70.0%)
- **Trades:** 297 (203W / 94L)
- **Net P/L:** $+2,742.33 (ROI: +9.2%)
- **Description:** Bet NO on high volume markets (>$100K)

### 6. QUESTION_WORD_FADE [[WIN]]
- **Actual Win Rate:** 68.0% (Claimed: 73.0%)
- **Trades:** 387 (263W / 124L)
- **Net P/L:** $+3,322.33 (ROI: +8.6%)
- **Description:** Bet NO on questions with 'Can', 'Will', 'Does'

### 7. WILL_PREDICTION_FADE [[WIN]]
- **Actual Win Rate:** 67.9% (Claimed: 75.8%)
- **Trades:** 386 (262W / 124L)
- **Net P/L:** $+3,260.67 (ROI: +8.4%)
- **Description:** Bet NO on markets starting with 'Will'

### 8. CONSENSUS_FADE [[WIN]]
- **Actual Win Rate:** 67.6% (Claimed: 75.1%)
- **Trades:** 346 (234W / 112L)
- **Net P/L:** $+2,782.00 (ROI: +8.0%)
- **Description:** Bet NO when high volume indicates consensus

### 9. CELEBRITY_FADE [[WIN]]
- **Actual Win Rate:** 66.9% (Claimed: 76.2%)
- **Trades:** 118 (79W / 39L)
- **Net P/L:** $+815.67 (ROI: +6.9%)
- **Description:** Bet NO on celebrity-related markets

### 10. POLITICAL_FADE [[WIN]]
- **Actual Win Rate:** 65.8% (Claimed: 72.0%)
- **Trades:** 260 (171W / 89L)
- **Net P/L:** $+1,289.00 (ROI: +5.0%)
- **Description:** Bet NO on political prediction markets

### 11. MICRO_MARKET_FADE [[WIN]]
- **Actual Win Rate:** 63.2% (Claimed: 77.2%)
- **Trades:** 19 (12W / 7L)
- **Net P/L:** $+12.00 (ROI: +0.6%)
- **Description:** Bet NO on markets with volume under $5,000

---

## ALL RESULTS (Ranked by Actual Win Rate)

| Rank | Strategy | Claimed | Actual | Diff | Trades | Net P/L | Status |
|------|----------|---------|--------|------|--------|---------|--------|
| 1 | MUSK_HYPE_FADE | 88.0% | 100.0% | +12.0% | 2 | $+123 | [LOW] INSUFFICIENT SAMPLE |
| 2 | FAVORITE_WINS | 95.0% | 100.0% | +5.0% | 149 | $+9188 | [OK] VALIDATED |
| 3 | TECH_HYPE_FADE | 78.2% | 85.7% | +7.5% | 7 | $+266 | [LOW] INSUFFICIENT SAMPLE |
| 4 | SPORTS_FADE | 68.0% | 79.7% | +11.7% | 64 | $+1793 | [OK] VALIDATED |
| 5 | CRYPTO_HYPE_FADE | 66.0% | 72.7% | +6.7% | 55 | $+907 | [OK] VALIDATED |
| 6 | US_MARKETS_FADE | 71.0% | 70.0% | -1.0% | 30 | $+359 | [OK] VALIDATED |
| 7 | HIGH_VOLUME_FADE | 70.0% | 68.4% | -1.6% | 297 | $+2742 | [OK] VALIDATED |
| 8 | QUESTION_WORD_FADE | 73.0% | 68.0% | -5.0% | 387 | $+3322 | [WIN] PROFITABLE |
| 9 | WILL_PREDICTION_FADE | 75.8% | 67.9% | -7.9% | 386 | $+3261 | [WIN] PROFITABLE |
| 10 | CONSENSUS_FADE | 75.1% | 67.6% | -7.5% | 346 | $+2782 | [WIN] PROFITABLE |
| 11 | CELEBRITY_FADE | 76.2% | 66.9% | -9.3% | 118 | $+816 | [WIN] PROFITABLE |
| 12 | POLITICAL_FADE | 72.0% | 65.8% | -6.2% | 260 | $+1289 | [WIN] PROFITABLE |
| 13 | MICRO_MARKET_FADE | 77.2% | 63.2% | -14.0% | 19 | $+12 | [WIN] PROFITABLE |
| 14 | COMPLEX_QUESTION_FADE | 71.4% | 18.2% | -53.2% | 11 | $-813 | [FAIL] FAILED |
| 15 | EXTREME_HIGH_FADE | 90.0% | 0.0% | -90.0% | 149 | $-15496 | [FAIL] FAILED |
| 16 | EXTREME_LOW_FADE | 85.0% | 0.0% | -85.0% | 351 | $-36504 | [FAIL] FAILED |
| 17 | FIFTY_FIFTY_FADE | 55.0% | 0.0% | -55.0% | 0 | $+0 | [--] NO DATA |
| 18 | LONG_QUESTION_FADE | 69.0% | 0.0% | -69.0% | 0 | $+0 | [--] NO DATA |
| 19 | UNDERDOG_FADE | 60.0% | 0.0% | -60.0% | 0 | $+0 | [--] NO DATA |

---

## FAILED STRATEGIES (< 50% Win Rate)

- **COMPLEX_QUESTION_FADE**: 18.2% win rate (11 trades)
- **EXTREME_HIGH_FADE**: 0.0% win rate (149 trades)
- **EXTREME_LOW_FADE**: 0.0% win rate (351 trades)

---

## DETAILED BREAKDOWN

### MUSK_HYPE_FADE [[LOW]]

**Description:** Bet NO on any Musk-related market

**Performance:**
- Claimed Win Rate: 88.0%
- Actual Win Rate: 100.0%
- Difference: +12.0%
- Sample Size: 2 trades (2W / 0L)

**Financial:**
- Net P/L: $+123.33
- ROI: +61.67%

**Verdict:** INSUFFICIENT SAMPLE

---

### FAVORITE_WINS [[OK]]

**Description:** Bet on favorite (>50% initial price) - validates market efficiency

**Performance:**
- Claimed Win Rate: 95.0%
- Actual Win Rate: 100.0%
- Difference: +5.0%
- Sample Size: 149 trades (149W / 0L)

**Financial:**
- Net P/L: $+9,188.33
- ROI: +61.67%

**Verdict:** VALIDATED

---

### TECH_HYPE_FADE [[LOW]]

**Description:** Bet NO on tech company predictions

**Performance:**
- Claimed Win Rate: 78.2%
- Actual Win Rate: 85.7%
- Difference: +7.5%
- Sample Size: 7 trades (6W / 1L)

**Financial:**
- Net P/L: $+266.00
- ROI: +38.00%

**Verdict:** INSUFFICIENT SAMPLE

---

### SPORTS_FADE [[OK]]

**Description:** Bet NO on sports outcome predictions

**Performance:**
- Claimed Win Rate: 68.0%
- Actual Win Rate: 79.7%
- Difference: +11.7%
- Sample Size: 64 trades (51W / 13L)

**Financial:**
- Net P/L: $+1,793.00
- ROI: +28.02%

**Verdict:** VALIDATED

---

### CRYPTO_HYPE_FADE [[OK]]

**Description:** Bet NO on crypto price predictions

**Performance:**
- Claimed Win Rate: 66.0%
- Actual Win Rate: 72.7%
- Difference: +6.7%
- Sample Size: 55 trades (40W / 15L)

**Financial:**
- Net P/L: $+906.67
- ROI: +16.48%

**Verdict:** VALIDATED

---

### US_MARKETS_FADE [[OK]]

**Description:** Bet NO on US-specific markets

**Performance:**
- Claimed Win Rate: 71.0%
- Actual Win Rate: 70.0%
- Difference: -1.0%
- Sample Size: 30 trades (21W / 9L)

**Financial:**
- Net P/L: $+359.00
- ROI: +11.97%

**Verdict:** VALIDATED

---

### HIGH_VOLUME_FADE [[OK]]

**Description:** Bet NO on high volume markets (>$100K)

**Performance:**
- Claimed Win Rate: 70.0%
- Actual Win Rate: 68.4%
- Difference: -1.6%
- Sample Size: 297 trades (203W / 94L)

**Financial:**
- Net P/L: $+2,742.33
- ROI: +9.23%

**Verdict:** VALIDATED

---

### QUESTION_WORD_FADE [[WIN]]

**Description:** Bet NO on questions with 'Can', 'Will', 'Does'

**Performance:**
- Claimed Win Rate: 73.0%
- Actual Win Rate: 68.0%
- Difference: -5.0%
- Sample Size: 387 trades (263W / 124L)

**Financial:**
- Net P/L: $+3,322.33
- ROI: +8.58%

**Verdict:** PROFITABLE

---

### WILL_PREDICTION_FADE [[WIN]]

**Description:** Bet NO on markets starting with 'Will'

**Performance:**
- Claimed Win Rate: 75.8%
- Actual Win Rate: 67.9%
- Difference: -7.9%
- Sample Size: 386 trades (262W / 124L)

**Financial:**
- Net P/L: $+3,260.67
- ROI: +8.45%

**Verdict:** PROFITABLE

---

### CONSENSUS_FADE [[WIN]]

**Description:** Bet NO when high volume indicates consensus

**Performance:**
- Claimed Win Rate: 75.1%
- Actual Win Rate: 67.6%
- Difference: -7.5%
- Sample Size: 346 trades (234W / 112L)

**Financial:**
- Net P/L: $+2,782.00
- ROI: +8.04%

**Verdict:** PROFITABLE

---

### CELEBRITY_FADE [[WIN]]

**Description:** Bet NO on celebrity-related markets

**Performance:**
- Claimed Win Rate: 76.2%
- Actual Win Rate: 66.9%
- Difference: -9.3%
- Sample Size: 118 trades (79W / 39L)

**Financial:**
- Net P/L: $+815.67
- ROI: +6.91%

**Verdict:** PROFITABLE

---

### POLITICAL_FADE [[WIN]]

**Description:** Bet NO on political prediction markets

**Performance:**
- Claimed Win Rate: 72.0%
- Actual Win Rate: 65.8%
- Difference: -6.2%
- Sample Size: 260 trades (171W / 89L)

**Financial:**
- Net P/L: $+1,289.00
- ROI: +4.96%

**Verdict:** PROFITABLE

---

### MICRO_MARKET_FADE [[WIN]]

**Description:** Bet NO on markets with volume under $5,000

**Performance:**
- Claimed Win Rate: 77.2%
- Actual Win Rate: 63.2%
- Difference: -14.0%
- Sample Size: 19 trades (12W / 7L)

**Financial:**
- Net P/L: $+12.00
- ROI: +0.63%

**Verdict:** PROFITABLE

---

### COMPLEX_QUESTION_FADE [[FAIL]]

**Description:** Bet NO on complex questions (>100 chars or contains 'and'/'or')

**Performance:**
- Claimed Win Rate: 71.4%
- Actual Win Rate: 18.2%
- Difference: -53.2%
- Sample Size: 11 trades (2W / 9L)

**Financial:**
- Net P/L: $-812.67
- ROI: -73.88%

**Verdict:** FAILED

---

### EXTREME_HIGH_FADE [[FAIL]]

**Description:** Bet NO when YES price >90% (extreme confidence)

**Performance:**
- Claimed Win Rate: 90.0%
- Actual Win Rate: 0.0%
- Difference: -90.0%
- Sample Size: 149 trades (0W / 149L)

**Financial:**
- Net P/L: $-15,496.00
- ROI: -104.00%

**Verdict:** FAILED

---

### EXTREME_LOW_FADE [[FAIL]]

**Description:** Bet YES when YES price <10% (extreme underdog)

**Performance:**
- Claimed Win Rate: 85.0%
- Actual Win Rate: 0.0%
- Difference: -85.0%
- Sample Size: 351 trades (0W / 351L)

**Financial:**
- Net P/L: $-36,504.00
- ROI: -104.00%

**Verdict:** FAILED

---

### FIFTY_FIFTY_FADE [[--]]

**Description:** Bet NO on 40-60% probability markets (coin flip)

**Performance:**
- Claimed Win Rate: 55.0%
- Actual Win Rate: 0.0%
- Difference: -55.0%
- Sample Size: 0 trades (0W / 0L)

**Financial:**
- Net P/L: $+0.00
- ROI: +0.00%

**Verdict:** NO DATA

---

### LONG_QUESTION_FADE [[--]]

**Description:** Bet NO on very long questions (>150 chars)

**Performance:**
- Claimed Win Rate: 69.0%
- Actual Win Rate: 0.0%
- Difference: -69.0%
- Sample Size: 0 trades (0W / 0L)

**Financial:**
- Net P/L: $+0.00
- ROI: +0.00%

**Verdict:** NO DATA

---

### UNDERDOG_FADE [[--]]

**Description:** Bet NO on underdog markets (<40% initial price)

**Performance:**
- Claimed Win Rate: 60.0%
- Actual Win Rate: 0.0%
- Difference: -60.0%
- Sample Size: 0 trades (0W / 0L)

**Financial:**
- Net P/L: $+0.00
- ROI: +0.00%

**Verdict:** NO DATA

---

## FINAL VERDICT

### Strategies That SURVIVED (>=55% win rate, >=10 trades):
- [OK] **FAVORITE_WINS** - 100.0% win rate
- [OK] **SPORTS_FADE** - 79.7% win rate
- [OK] **CRYPTO_HYPE_FADE** - 72.7% win rate
- [OK] **US_MARKETS_FADE** - 70.0% win rate
- [OK] **HIGH_VOLUME_FADE** - 68.4% win rate
- [OK] **QUESTION_WORD_FADE** - 68.0% win rate
- [OK] **WILL_PREDICTION_FADE** - 67.9% win rate
- [OK] **CONSENSUS_FADE** - 67.6% win rate
- [OK] **CELEBRITY_FADE** - 66.9% win rate
- [OK] **POLITICAL_FADE** - 65.8% win rate
- [OK] **MICRO_MARKET_FADE** - 63.2% win rate

### Key Findings:
1. **5/19** strategies performed within 5% of claimed win rates
2. **11/19** strategies are profitable (>=55% win rate)
3. **3/19** strategies failed (<50% win rate)
4. Combined portfolio P/L across all strategies: $-25,952.33

### Recommendations:
- Focus on the top 3-5 validated strategies
- Start with small position sizing (1-2% of bankroll)
- Monitor for edge degradation over time
- Combine multiple strategies for diversification

---
*Report generated by BACKTEST RUNNER 1*
*Real historical data from RESOLVED_DATA_FIXED.json (500 markets)*
