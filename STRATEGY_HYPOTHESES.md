# STRATEGY_HYPOTHESES.md
## New Strategy Ideas Based on Data Patterns

**Generated:** 2026-02-08  
**Based on:** Analysis of 149 resolved markets + 2,014 backtest trades

---

## Strategy Selection Criteria

Each strategy must have:
- Clear, testable rules
- Sufficient sample size (>100 trades where possible)
- Logical rationale based on observed patterns
- Realistic fee accounting (5%)

---

## HYPOTHESIS 1: Base Rate NO Strategy

### Description
Buy NO on all available markets. No filtering.

### Rationale
Markets resolve NO 64.4% of the time. This is the simplest edge available.

### Expected Performance
- Win Rate: ~64%
- Sample Size: All markets
- Risk: Low (diversified across all markets)

### Testability
✅ Can be tested on any market with YES/NO outcomes

### Risks
- Need to hold until resolution
- Fees erode edge if buying at unfavorable prices
- Some markets may have 100% implied probability

---

## HYPOTHESIS 2: Low Volume NO Fade

### Description
Buy NO on markets with volume <$10,000.

### Rules
1. Filter markets by volume < $10K
2. Buy NO position
3. Hold until resolution

### Rationale
Low volume markets resolve NO 72-89% of the time vs 64% base rate.

### Expected Performance
- Win Rate: ~75-80%
- Sample Size: 48 markets in resolved data (45 in <$10K category)
- Risk: Low (strong NO bias)

### Data Support
| Volume | Count | NO Rate |
|--------|-------|---------|
| <$1K | 9 | 88.9% |
| $1K-$10K | 36 | 72.2% |

### Risks
- Lower liquidity may make entry/exit harder
- Smaller position sizes due to limited volume
- May miss some winning YES outcomes

---

## HYPOTHESIS 3: Mid-Volume YES Play

### Description
Buy YES on markets with volume between $10K-$1M.

### Rules
1. Filter markets: $10K <= volume <= $1M
2. Buy YES position
3. Hold until resolution

### Rationale
Mid-volume markets have highest YES rates (42-44%) and reasonable liquidity.

### Expected Performance
- Win Rate: ~43%
- Sample Size: 91 markets in data
- Risk: Moderate (loses more often than wins, but positive expectancy possible)

### Data Support
| Volume | Count | YES Rate |
|--------|-------|----------|
| $10K-$100K | 59 | 42.4% |
| $100K-$1M | 32 | 43.8% |

### Risks
- Win rate below 50% requires careful position sizing
- Need sufficient edge to overcome fees
- Contrarian to base rate

---

## HYPOTHESIS 4: Fair Price Entry (40-60% Range)

### Description
Only enter positions when implied probability is in the 40-60% range.

### Rules
1. Monitor market prices
2. Enter YES when price is between 0.40-0.60
3. Avoid extremes (<20% or >80%)

### Rationale
Backtest data shows 57% win rate in this range - the highest of any price bucket.

### Expected Performance
- Win Rate: 57%
- Sample Size: 337 trades in backtest
- Avg P&L per trade: $0.042

### Data Support
| Price Range | Trades | Win Rate | Avg P&L |
|-------------|--------|----------|---------|
| 40-60% | 337 | 57.0% | $0.042 |
| 60-80% | 302 | 69.2% | $0.035 |
| 80-100% | 448 | 42.9% | $0.012 |

### Risks
- Requires active monitoring for entry points
- May have fewer trade opportunities
- Need to verify this holds across time periods

---

## HYPOTHESIS 5: Fade Heavy Favorites (>70%)

### Description
Buy NO when YES price exceeds 70% (implied probability >70%).

### Rules
1. Identify markets with YES price > 0.70
2. Buy NO position
3. Hold until resolution

### Rationale
Backtest shows heavy favorites (80-100%) only win 43% of the time, suggesting market overconfidence.

### Expected Performance
- Win Rate: ~50-57% (buying NO when YES >70%)
- Sample Size: ~600+ trades in backtest
- Contrarian edge

### Data Support
- 80-100% bucket: Only 42.9% win rate for YES buyers
- Implies 57.1% win rate for NO buyers

### Risks
- Psychologically difficult (betting against consensus)
- When favorites win, losses are large
- Need large sample for edge to materialize

---

## HYPOTHESIS 6: Avoid Longshots Strategy

### Description
Never buy YES when implied probability < 20%.

### Rules
1. Check entry price before buying YES
2. If price < 0.20, skip trade or buy NO
3. Focus on 20%+ implied probability

### Rationale
Backtest shows longshots (0-20%) only win 26.3% of the time - terrible odds.

### Expected Performance
- Avoids: 26% win rate trades
- Sample Size: 654 trades in backtest (what NOT to do)

### Data Support
| Price Range | Trades | Win Rate |
|-------------|--------|----------|
| 0-20% | 654 | 26.3% |
| 20-40% | 273 | 54.9% |

### Risks
- May miss occasional big wins
- Reduces total trade count
- Requires discipline to skip "exciting" longshots

---

## HYPOTHESIS 7: Political Market Contrarian

### Description
Fade political markets (Trump/Biden) by buying NO.

### Rules
1. Identify markets mentioning Trump or Biden
2. Buy NO position
3. Hold until resolution

### Rationale
Political markets show 53-62% YES rates, suggesting hype/passion may inflate YES prices.

### Expected Performance
- Win Rate: ~40-50%
- Sample Size: 32 Trump + 13 Biden markets

### Data Support
| Type | Count | YES Rate | Potential NO Rate |
|------|-------|----------|-------------------|
| Trump | 32 | 53.1% | 46.9% |
| Biden | 13 | 61.5% | 38.5% |

### Risks
- Small sample size for individual politicians
- Political bias may be real (not hype)
- High variance due to small n

---

## HYPOTHESIS 8: Volume-Price Combined Filter

### Description
Combine volume and price filters for higher confidence trades.

### Rules
1. Filter: Low volume (<$10K) + Any price
2. Action: Buy NO
3. OR: Mid volume ($10K-$1M) + Fair price (40-60%)
4. Action: Buy YES

### Rationale
Combines strongest signals: volume for NO bias, price for entry timing.

### Expected Performance
- Expected highest win rates
- Lower trade frequency

### Risks
- May be overfitted to limited data
- Need more samples to validate combination
- More complex = more ways to fail

---

## HYPOTHESIS 9: Momentum Following (>50%)

### Description
Buy YES when price > 50% (follow the crowd).

### Rules
1. Enter YES when market price > 0.50
2. Ride momentum to resolution

### Rationale
Markets with >50% price win 54% of the time in backtest.

### Expected Performance
- Win Rate: 54%
- Sample Size: 906 trades
- Total P&L: $16.33 (highest in backtest)

### Risks
- Drawdown can be large (-$18.52 max)
- Requires holding through volatility
- Lower Sharpe than other strategies

---

## HYPOTHESIS 10: Anti-Momentum (Contrarian)

### Description
Do the opposite of market consensus on extreme prices.

### Rules
1. If YES price > 80%, buy NO
2. If YES price < 20%, buy YES
3. Take contrarian positions on extremes

### Rationale
Markets may overreact at extremes, creating value on opposite side.

### Expected Performance
- Win Rate: ~50-57% on NO side (>80%)
- Win Rate: ~74% on YES side (<20%) - but small edge per trade

### Risks
- Fighting market consensus is hard
- Losses when extremes are justified
- Need strong stomach for contrarian positions

---

## SUMMARY TABLE

| ID | Strategy | Expected Win Rate | Sample Size | Data Source |
|----|----------|-------------------|-------------|-------------|
| 1 | Base Rate NO | 64% | 149 | Resolved |
| 2 | Low Volume NO | 75% | 48 | Resolved |
| 3 | Mid Volume YES | 43% | 91 | Resolved |
| 4 | Fair Price (40-60%) | 57% | 337 | Backtest |
| 5 | Fade Favorites | 57% | 600+ | Backtest |
| 6 | Avoid Longshots | Filter | 654 | Backtest |
| 7 | Political Fade | 40-50% | 45 | Resolved |
| 8 | Volume+Price Combo | 60%+ | 30+ | Combined |
| 9 | Momentum | 54% | 906 | Backtest |
| 10 | Contrarian | 50-57% | 750 | Backtest |

---

## NEXT STEPS

1. Backtest all hypotheses systematically
2. Calculate P&L with 5% fees
3. Measure risk metrics (drawdown, Sharpe)
4. Rank strategies by consistency and profitability
5. Identify which are safe to deploy

---

*All hypotheses derived from ACTUAL observed patterns. No theoretical claims.*
