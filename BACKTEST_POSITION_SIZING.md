# Position Sizing Backtest Results & Recommendations

**Date:** 2026-02-06  
**Starting Bankroll:** $100  
**Simulations:** 1,000 runs × 100 trades each  
**Win Rate:** 55%  
**Reward/Risk Ratio:** 1.5:1

---

## Executive Summary

**Recommendation for $100 Bankroll: Quarter Kelly (6.25%) or Half Kelly (12.5%)**

- **Quarter Kelly** provides the best risk-adjusted returns with manageable drawdowns
- **Half Kelly** offers higher growth potential for those comfortable with ~57% median drawdowns
- **Full Kelly** maximizes theoretical growth but has extreme variance and psychological burden
- **Fixed sizing** is safest but leaves significant growth on the table

---

## Kelly Criterion Calculation

**Formula:** f* = (bp - q) / b

Where:
- b = reward/risk ratio = 1.5
- p = win probability = 0.55
- q = loss probability = 0.45

**Result:**  
f* = (1.5 × 0.55 - 0.45) / 1.5 = **25%** (Full Kelly)

**Fractional Kelly:**
- Full Kelly: 25.00%
- Half Kelly: 12.50%
- Quarter Kelly: 6.25%

---

## Backtest Results Summary

### 📊 Fixed $4 Position Size
- **Median Final Bankroll:** $250.00 (+150%)
- **Range:** $100 - $400
- **Median Max Drawdown:** 14.5%
- **Worst Drawdown:** 57.4%
- **Risk-Adjusted Return:** 2.944
- **Blown Accounts:** 0/1,000 (0%)

**Characteristics:**
- Most conservative approach
- Predictable, linear growth
- Minimal psychological stress
- Doesn't scale with account growth
- Leaves money on the table

---

### 📊 Fixed $5 Position Size
- **Median Final Bankroll:** $287.50 (+187.5%)
- **Range:** $87.50 - $512.50
- **Median Max Drawdown:** 17.0%
- **Worst Drawdown:** 90.0%
- **Risk-Adjusted Return:** 2.999
- **Blown Accounts:** 0/1,000 (0%)

**Characteristics:**
- Slightly more aggressive than $4
- Still doesn't compound
- Higher drawdown potential
- Simple to execute

---

### 📊 Full Kelly (25% of Bankroll)
- **Median Final Bankroll:** $9,647.29 (+9,547%)
- **Mean Final Bankroll:** $830,066.17 (extreme right skew)
- **Range:** $0.32 - $288,077,701 (!!!)
- **Median Max Drawdown:** 86.2%
- **Worst Drawdown:** 99.9%
- **Risk-Adjusted Return:** 0.001 (worst)
- **Blown Accounts:** 0/1,000 (0%)

**Characteristics:**
- **Theoretically optimal** for long-term growth
- **Extreme volatility** - standard deviation of $9.6M
- **Psychological nightmare** - 86% median drawdown means watching $100 → $1,000 → $140 is common
- **Fat tails** - 25th percentile is only $854, but 75th is $59,447
- Nearly impossible to stick with emotionally
- One bad streak early can cripple the strategy

---

### 📊 Half Kelly (12.5% of Bankroll) ⭐
- **Median Final Bankroll:** $3,686.10 (+3,586%)
- **Range:** $32.05 - $414,210
- **Median Max Drawdown:** 57.1%
- **Worst Drawdown:** 93.9%
- **Risk-Adjusted Return:** 0.159
- **Blown Accounts:** 0/1,000 (0%)

**Characteristics:**
- **Excellent growth** - median 36× return
- **Still volatile** but more manageable than full Kelly
- **Severe drawdowns** - 57% median means $1,000 → $430 is normal
- Requires strong discipline
- Good for aggressive traders with solid psychology

---

### 📊 Quarter Kelly (6.25% of Bankroll) ⭐⭐⭐
- **Median Final Bankroll:** $757.18 (+657%)
- **Range:** $74.99 - $7,645
- **Median Max Drawdown:** 32.1%
- **Worst Drawdown:** 70.0%
- **Risk-Adjusted Return:** 0.748 (2nd best)
- **Blown Accounts:** 0/1,000 (0%)

**Characteristics:**
- **Best balance** of growth and stability
- **Manageable drawdowns** - 32% is uncomfortable but survivable
- **Consistent compounding** - 7.5× median return
- **Highest risk-adjusted returns** among Kelly variants
- Recommended for most traders

---

## Key Insights

### 1. The Kelly Paradox
Full Kelly is **mathematically optimal** for maximizing log wealth over infinite trials, but:
- Requires infinite time horizon
- Assumes perfect parameter estimation
- Ignores psychological costs
- Produces unbearable volatility

**Real-world edge is lower than calculated:**
- Win rate varies
- R:R fluctuates
- Slippage/commissions reduce edge
- You're not a robot

### 2. The Compounding Advantage
Look at the sample equity curve for Quarter Kelly vs Fixed $5:
- Both start at $100
- Fixed $5: $100 → $287.50 (2.9×)
- Quarter Kelly: $100 → $757.18 (7.6×)

**Why?** Position sizing scales with wins. After a winning streak:
- Fixed: still risking $5
- Kelly: risking 6.25% of larger bankroll = bigger positions

### 3. Drawdown Psychology
**Median max drawdowns:**
- Fixed $4: 14.5%
- Quarter Kelly: 32.1%
- Half Kelly: 57.1%
- Full Kelly: 86.2%

**Reality check:**
- 14.5% DD: $100 → $85.50 (annoying)
- 32.1% DD: $100 → $67.90 (painful)
- 57.1% DD: $100 → $42.90 (gut-wrenching)
- 86.2% DD: $100 → $13.80 (account looks dead)

Can you watch your account drop 86% and keep trading? Probably not.

### 4. The Risk-Adjusted Winner
**Risk-Adjusted Performance (Return/Volatility):**
1. Fixed $5: **2.999**
2. Fixed $4: **2.944**
3. Quarter Kelly: **0.748**
4. Half Kelly: **0.159**
5. Full Kelly: **0.001**

Fixed sizing wins on risk-adjusted basis, but this metric doesn't account for:
- Opportunity cost of not compounding
- Time value of reaching goals faster
- Flexibility as bankroll grows

### 5. No Blown Accounts (With These Parameters)
With 55% win rate and 1.5:1 R:R, even Full Kelly never blew accounts in 1,000 simulations.

**But this changes if:**
- Win rate drops to 50% (Kelly becomes 16.7%)
- Losing streak hits early when using Full Kelly
- You overestimate your edge (think 55%, actually 50%)

---

## Recommendations by Trader Type

### 🟢 Conservative Trader ($100 → $500 goal)
**Use: Fixed $4 or Quarter Kelly**
- Fixed $4: predictable, low stress, slower growth
- Quarter Kelly: better compounding, manageable 32% drawdowns
- **Recommended:** Quarter Kelly if you can handle -$32 swings

### 🟡 Balanced Trader ($100 → $1,500 goal)
**Use: Quarter Kelly or Half Kelly**
- Quarter Kelly: safer, 7.5× median return
- Half Kelly: aggressive, 37× median return, 57% drawdowns
- **Recommended:** Start Quarter Kelly, graduate to Half Kelly as bankroll grows

### 🔴 Aggressive Trader ($100 → $5,000+ goal)
**Use: Half Kelly**
- Full Kelly is too volatile even for aggressive traders
- Half Kelly captures most growth (38% of Full Kelly's median return) with half the drawdown
- **Recommended:** Half Kelly with strict risk management

### 🎓 Professional/Experienced Trader
**Use: Fractional Kelly (1/3 to 1/2)**
- You understand the math
- You've lived through drawdowns
- You have emotional discipline
- You know your edge precisely
- **Recommended:** 1/3 Kelly (8.33%) as baseline, adjust based on confidence level

---

## Practical Implementation for $100 Bankroll

### Quarter Kelly (6.25%) - RECOMMENDED
**Initial position size:** $100 × 6.25% = **$6.25**

**As account grows:**
- $150 bankroll → $9.38 risk
- $200 bankroll → $12.50 risk
- $500 bankroll → $31.25 risk
- $1,000 bankroll → $62.50 risk

**Drawdown management:**
- Expect to see $100 → $68 (32% DD)
- Don't panic and switch strategies mid-stream
- Trust the process over 100+ trades

**Position sizing formula:**
- Risk per trade = Current Bankroll × 0.0625
- Stop loss distance = Entry price - Stop price
- Position size = Risk per trade / Stop loss distance

**Example trade:**
- Bankroll: $100
- Risk: $6.25
- Entry: $50
- Stop: $49 (1% stop)
- Position size: $6.25 / $0.50 = 12.5 shares

---

### Half Kelly (12.5%) - AGGRESSIVE
**Initial position size:** $100 × 12.5% = **$12.50**

**Warning signs:**
- If you feel sick during a losing streak, you're overleveraged
- If you're checking account every 5 minutes, reduce size
- If you can't sleep, drop to Quarter Kelly

---

### Fixed $5 - CONSERVATIVE
**Position size:** Always $5

**When it makes sense:**
- You're learning and want consistency
- Psychology is more important than optimization
- You plan to increase size manually as you gain confidence
- Your bankroll is too small for Kelly (under $80)

---

## Common Mistakes to Avoid

### ❌ Switching strategies mid-drawdown
- Seeing -30% and switching from Quarter Kelly to Fixed $5
- This locks in losses and abandons compounding right before recovery
- **Solution:** Choose strategy before you start, commit for 100+ trades

### ❌ Using Full Kelly with estimated parameters
- Your win rate is probably not exactly 55%
- Your R:R probably varies
- Small overestimation of edge → massive overleveraging
- **Solution:** Use fractional Kelly to account for uncertainty

### ❌ Not adjusting position size
- Calculating Kelly once at $100 and never updating
- Defeats the entire purpose of Kelly sizing
- **Solution:** Recalculate position size after every trade or at minimum every 10 trades

### ❌ Confusing Kelly percentage with account risk
- "I'm risking 25% of my account per trade"
- No - you're risking 25% of bankroll to the stop loss, not putting 25% at total risk
- If your stop is 2% from entry, you're risking: 25% bankroll × 2% = 0.5% total account risk
- **Solution:** Understand the formula: Position size = (Kelly % × Bankroll) / Stop distance

### ❌ Ignoring drawdowns
- "I can handle anything!"
- Reality: watching $1,000 → $138 (86% DD with Full Kelly) breaks most people
- **Solution:** Backtest emotionally - visualize living through the drawdown

---

## Advanced: Adjusting for Parameter Uncertainty

**Problem:** You don't know your true win rate and R:R perfectly.

**Solution:** Apply a "certainty factor" to Kelly percentage.

If you're 80% confident in your edge estimate:
- Full Kelly: 25% × 0.80 = 20%
- Half Kelly: 12.5% × 0.80 = 10%
- Quarter Kelly: 6.25% × 0.80 = 5%

**Conservative approach:**
- Always use fractional Kelly (1/4 to 1/2)
- Reduces risk of overestimating edge
- Fractional Kelly has been shown to outperform Full Kelly in real-world trading

---

## Final Recommendation for $100 Bankroll

### 🏆 Best Choice: **Quarter Kelly (6.25%)**

**Starting position size:** $6.25 risk per trade

**Reasoning:**
1. **Growth:** 7.5× median return (657%) vs 2.9× for Fixed $5
2. **Safety:** 32% median drawdown - uncomfortable but manageable
3. **Psychology:** Most traders can stick with this through rough patches
4. **Flexibility:** Scales naturally as account grows
5. **Risk-adjusted:** 2nd best Sharpe-like ratio (0.748)

**When to upgrade to Half Kelly:**
- Bankroll reaches $300+
- You've experienced the 30% drawdown and stayed disciplined
- Your actual tracked win rate confirms ≥55%
- You have 6+ months of consistent execution

**When to downgrade to Fixed $5:**
- You're new to trading (< 6 months live)
- You feel anxiety about position sizing
- Your edge is unproven
- You'd rather learn with consistency than optimize mathematically

---

## Conclusion

The "optimal" Kelly Criterion is a mathematical ideal that assumes:
- Perfect parameter knowledge
- Infinite time horizon
- Zero emotional costs
- No parameter drift

**Reality is messier.**

Quarter Kelly strikes the best balance between:
- Theoretical optimality
- Practical survivability
- Psychological sustainability
- Real-world compounding

**Start conservative. Prove your edge. Scale slowly.**

The goal isn't to maximize growth rate - it's to *stay in the game long enough* for compounding to work its magic.

---

## Appendix: Sample Equity Curves (Single Run)

These show one possible path for each strategy using the same random sequence:

**Fixed $4:**
$100 → $70 → $60 → $90 → $120 → $130 → $140 → $140 → $190 → $220 → **$250**
- Steady, predictable
- Smallest drawdown ($60 = -40%)

**Fixed $5:**
$100 → $62.50 → $50 → $87.50 → $125 → $137.50 → $150 → $150 → $212.50 → $250 → **$287.50**
- Similar pattern, larger swings

**Quarter Kelly (6.25%):**
$100 → $61 → $51 → $79 → $121 → $138 → $156 → $151 → $318 → $491 → **$757**
- Early struggle, then compounding kicks in
- Nearly triples Fixed $5 final result

**Half Kelly (12.5%):**
$100 → $36 → $23 → $52 → $117 → $142 → $171 → $153 → $628 → $1,402 → **$3,128**
- Brutal early drawdown ($100 → $23 = -77%)
- Massive compounding in second half
- 10× final result vs Fixed $5

**Full Kelly (25%):**
$100 → $10 → $4 → $14 → $55 → $64 → $75 → $48 → $628 → $2,461 → **$9,647**
- Catastrophic early drawdown ($100 → $4 = -96%)
- Most traders would quit here
- Explosive growth after recovery
- Highest final result but highest stress

**Key takeaway:** Notice how the early drawdown gets worse as Kelly percentage increases, but so does the eventual recovery. Can you survive the drawdown psychologically? That's the real question.

---

**Generated:** 2026-02-06  
**Simulation code:** `backtest_position_sizing.js`  
**Raw results:** `backtest_results.json`
