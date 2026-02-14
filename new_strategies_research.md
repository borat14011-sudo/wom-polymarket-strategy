# Prediction Market Trading Strategies Research Report
**Date:** February 12, 2026  
**Status:** Comprehensive Literature Review

---

## Executive Summary

This report compiles trading strategies for prediction markets gathered from academic sources, successful traders, blogs, and market data. The research covers platforms including Polymarket, Kalshi, PredictIt, Manifold, and Metaculus.

---

## 1. KELLY CRITERION & BANKROLL MANAGEMENT

### 1.1 The Kelly Criterion Formula

**Source:** Gwern.net, SportsbookReview

The Kelly Criterion determines optimal bet sizing based on your edge:

```
f* = (b × p - q) / b

Where:
- f* = fraction of bankroll to bet
- b = decimal odds - 1 (the net profit per $1 wagered)
- p = probability of winning (your estimate)
- q = probability of losing (1 - p)
```

**Simplified version (for double-or-nothing):**
```
f* = 2p - 1
```

**Example from Gwern:**
- Market price: 50% (you can buy at $0.50)
- Your estimate: 60% probability
- Odds: 1:1 (double or nothing)
- Kelly calculation: f* = (1 × 0.60 - 0.40) / 1 = 0.20 = **20% of bankroll**

### 1.2 Fractional Kelly (Real-World Application)

**Source:** Polymarket Trader "Betwick" ($800k+ profits)

> "I tend to stick to 1/3 Kelly-ish on my bigger positions. But I'll only really be going that big on one position a month, maybe not even that."

**Why fractional Kelly?**
- Reduces variance/volatility
- Accounts for uncertainty in your probability estimates
- Prevents catastrophic drawdowns
- Psychologically sustainable

**Expected Edge:**
- Full Kelly maximizes long-term growth but with high variance
- 1/2 Kelly achieves ~75% of full Kelly's growth with much less variance
- 1/3 Kelly (Betwick's approach) provides more conservative growth

**Pros:**
- Mathematical foundation for bet sizing
- Prevents over-betting and ruin
- Scales with your edge

**Cons:**
- Requires accurate probability estimates
- Sensitive to estimation errors
- Full Kelly can lead to massive drawdowns

---

## 2. CROSS-PLATFORM ARBITRAGE

### 2.1 Price Discrepancy Arbitrage

**Source:** Scott Alexander (Astral Codex Ten)

**Strategy:** Buy shares on one platform that are mispriced relative to another platform.

**Example:** If Polymarket has "Event X" at 60% and Kalshi has it at 40%:
- Buy YES on Kalshi at 40¢
- Buy NO on Polymarket at 40¢
- Total cost: 80¢
- Guaranteed payout: $1
- Risk-free profit: 20¢ (25% return)

**Documented Edge:** 5-20% when discrepancies exist

**Requirements:**
- Accounts on multiple platforms
- Capital on multiple platforms
- Monitoring tools for price discrepancies
- Fast execution capability

**Cons:**
- Regulatory barriers (US users restricted from some platforms)
- Capital locked across platforms
- Resolution risk (different resolution criteria)
- Transaction costs eat into margins

### 2.2 Correlation Arbitrage Warning

**Source:** Betwick Interview

> "People don't think enough about correlation in their positions. You can easily over-size on correlated positions."

**Example:** Iran markets - "US strikes Iran" and "Khamenei ousted" are correlated. Betting big on both is effectively doubling down.

---

## 3. INFORMATION EDGE STRATEGIES

### 3.1 Primary Source Research ("Just Call Them")

**Source:** Chris DeMuth Jr. (Rangeley Capital)

**Strategy:** Call principals directly (CEOs, senators, company insiders) instead of relying on secondary analysis.

**Key Techniques:**
1. **Get 60-70% there on documents first** - Read SEC filings, press releases before calling
2. **Call the decision-maker, not middle management** - They have more freedom to speak
3. **Offer value proposition:** "Be very nice, very interesting, or very quick"
4. **Deputize politicians** - Frame issues in terms of their constituents' jobs
5. **Observe reactions** - Even if they can't answer, body language/typing sounds give information
6. **Use FOIA requests** for government-related markets

**Quote:**
> "I love not just primary sources, but principals. There are more bleeding hearts than skeptics in capitalism. People are happy to tell you if you ask."

**Expected Edge:** Significant, but difficult to quantify

**Requirements:**
- Confidence in cold-calling
- Research skills
- Time investment
- Professional demeanor

### 3.2 Boots-on-the-Ground Research

**Source:** "Scottilicious" ($1.3M+ profits) - Portugal Election Case Study

**Strategy:** Travel to locations, interview locals, develop human sources.

**Methodology:**
1. Find local political science contacts via Twitter/X
2. Conduct formal interviews + random street interviews
3. Interview service workers (Uber drivers provided sentiment data)
4. Measure "enthusiasm gaps" not captured by polls

**Key Insight from Portugal:**
> "Three-quarters of the Mendes supporters we talked to were equivocal... That enthusiasm gap isn't something polls necessarily capture."

**Expected Edge:** Built position from 60s to 80s on correct prediction

**Requirements:**
- Capital for travel
- Local contacts/translators
- Video documentation capability
- Time (multi-day research trips)

### 3.3 Hiring Local Informants

**Source:** Scottilicious

**Strategy:** Hire locals via Fiverr/freelance platforms to provide real-time information.

**Example:** Korean election - hired Korean informants for on-the-ground sentiment
**Example:** Portugal - got information on sexual harassment accusations "within 10 minutes... before it hit the international press"

---

## 4. NICHE MARKET SPECIALIZATION

### 4.1 Lower-Liquidity Market Focus

**Source:** Betwick Interview

> "If you've got a lower bankroll, you can focus on lower liquidity markets that more experienced traders are leaving out because it's not worth their time. You can find much bigger edges in those and focus on a niche."

**Examples:**
- Mention markets (tracking speech content)
- Movie box office markets
- Foreign elections
- Niche sports

**Expected Edge:** Higher than liquid markets

### 4.2 Mention Markets Strategy

**Source:** Betwick

**Strategy:** Bet on what politicians will/won't say in speeches, but index on *context* not historical frequency.

**Example:** Trump town halls are different from rallies:
> "Town halls are much more question and answer, much less combative. After watching videos from his previous campaign, I bet against some of the things he'd said all the time in rallies that wouldn't really fit that Q&A pattern."

**Edge:** Understanding context > pure statistical frequency analysis

### 4.3 Movie Box Office Modeling

**Source:** Betwick

**Strategy:** Systematic modeling rather than vibes:
- Track early reviews on Twitter
- Build statistical models correlating reviews to opening weekends
- Apply model week after week (scalable edge)

> "It's not vibes at all. I'm not a movie fan... I would see what the vibes were from early reviews on Twitter, then model that with some other stuff."

---

## 5. BEHAVIORAL BIAS EXPLOITATION

### 5.1 Underdog/Long-shot Bias

**Source:** Maxim Lott (Maximum Truth), Gwern.net

**Finding:** Both prediction markets AND expert models (538) systematically overvalue underdogs.

**Data:**
- Candidates given 10-20% odds only won ~4.5-7% of the time
- The inverse applies: favorites are undervalued

**Strategy:** Bet against extreme underdogs; favor slight favorites

**Expected Edge:** ~5-10% on extreme cases

**Limitations:** 
- Capital tied up for small returns
- Opportunity cost (betting $99 to win $1)
- PredictIt $850 limits prevent full correction

### 5.2 Partisan Bias Exploitation

**Source:** Maximum Truth analysis

**Finding:** FiveThirtyEight shows measurable Democratic bias; prediction markets show smaller bias.

**Strategy:** 
- In Republican-favoring races, betting markets may offer better value than models suggest
- Average prediction markets + expert models for best accuracy

> "Taking the average of ElectionBettingOdds.com and FiveThirtyEight.com is more accurate than looking at either one individually."

### 5.3 Recency Bias / Overreaction

**Source:** Betwick (Iran markets)

**Strategy:** Don't overreact to noise; focus on macro decision-makers.

> "If you follow OSINT pages... all you're seeing all day is a new tanker showing up in Qatar, three jets in Jordan. That feed will naturally incline you to think something's about to happen. But I think it's better to almost ignore all of that and focus on the macro."

**Key insight:** Presidential statements > flight tracking data

---

## 6. AI/ALGORITHMIC FORECASTING

### 6.1 Mantic AI System (Top 1% Forecaster)

**Source:** Toby Shevlane, Mantic AI

**Achievement:** 4th place out of ~500 entrants in Metaculus Fall Cup 2025

**Architecture:**
- Multiple LLM calls in structured workflow (not single prompt)
- "Factory line" with different workers: question breakdown, research, inquiry, synthesis
- Point-in-time historical data (not Google/Perplexity - need backtest capability)
- Dozens of data sources: Wikipedia, news, economic data, earnings calls

**Key Insights:**

1. **News processing requires skill:**
> "Sometimes people say, 'I accidentally didn't include news in my pipeline, but my score didn't go down.' That is crazy... You need to figure out how to best process the information."

2. **Calibration over confidence:**
> "We pick up a decent amount for being cautious where caution is needed."

3. **Base rates + specific research:**
> "I like to start specific, then zoom out. If you just use 'the US acquiring any territory' as your reference class, you'd get an overestimate."

**Expected Edge:** ~4-10% over market in specific domains

### 6.2 Following Sharp AI Traders

**Source:** Polymarket Oracle "AI Overlords" analysis

**Top AI-focused traders to watch:**
- **@send-tips-plz:** 58.8% accuracy, 9 active AI positions
- **@3tourists:** 85.7% accuracy, specializes in release dates
- **@yyds233:** 91.7% accuracy, #1 in GPT-5 markets

**Strategy:** Use tools like Stand.trade to follow wallet movements of successful traders.

---

## 7. MARKET MICROSTRUCTURE INSIGHTS

### 7.1 Conditions for Efficient Markets

**Source:** Zvi Mowshowitz

**Five requirements for prediction market efficiency:**

1. **Well-Defined:** Clear resolution criteria for all edge cases
2. **Quick Resolution:** Shorter timeframes attract more capital
3. **Probable Resolution:** Conditional markets with <50% trigger rate see reduced participation
4. **Limited Hidden Information:** Insider information kills participation
5. **Sources of Disagreement:** Need "suckers at the table" or subsidies

**Strategy Implication:** Target markets with:
- Clear resolution criteria
- Near-term resolution
- High probability of triggering
- Public information advantages
- Natural disagreement/interest

### 7.2 Why Small Mispricings Persist

**Source:** Scott Alexander

**Reasons mispricings survive:**
- Transaction costs/fees
- Opportunity cost (stock market returns ~5%/year)
- Platform trust issues
- Regulatory limits (PredictIt $850 cap)
- Hassle factors (crypto, account creation)

**Strategy:** Focus on mispricings > 5-10% to account for these frictions

---

## 8. RISK MANAGEMENT & PSYCHOLOGY

### 8.1 Recovery from Drawdowns

**Source:** Betwick (recovered from 70% drawdown)

**Steps:**
1. **Take time off** - At least a week, maybe longer
2. **Stop completely** - Don't think about markets for a few days
3. **Cold analysis** - Review positions without emotion after dust settles
4. **Ask:** Was this good trading? Right size? Would you make this trade again?

### 8.2 Tilt Prevention

**Source:** Betwick

**Warning signs:**
- Over-trading to "win back" losses
- Trading without proper research
- Position sizes causing sleep loss

**Solutions:**
- Have a risk manager (real or virtual)
- Use hedges to prevent over-concentration
> "My risk manager is already giving me grief... The Greenland bet is a hedge against my own worst instincts."

### 8.3 Correlation Management

**Source:** Betwick

**Rule:** Consider total exposure to correlated outcomes, not just individual position sizes.

---

## 9. DOCUMENTED MISPRICINGS (HISTORICAL)

### 9.1 PredictIt Conservative Bias

**Source:** Scott Alexander

After 2016, PredictIt developed small but consistent conservative bias due to departing Hillary bettors.

**Edge:** Few hundred dollars per election cycle
**Limitation:** $850 per market cap

### 9.2 Underdog Bias Across Platforms

**Source:** Multiple

Consistent 5-10% overvaluation of underdogs across prediction markets.

### 9.3 Foreign Election Inefficiencies

**Source:** Scottilicious, Betwick

Less liquid markets (Korean elections, Portuguese elections, Romanian elections) show larger mispricings.

---

## 10. SUMMARY: TOP STRATEGIES BY EXPECTED VALUE

| Strategy | Expected Edge | Difficulty | Capital Req. | Time Req. |
|----------|--------------|------------|--------------|-----------|
| Kelly Criterion Sizing | Prevents ruin | Medium | Any | Low |
| Cross-Platform Arb | 5-20% | High | High | Medium |
| Primary Source Calls | Variable, high | High | Low | High |
| Boots-on-Ground | 10-30%+ | Very High | High | Very High |
| Niche Market Focus | 5-15% | Medium | Low | Medium |
| Underdog Bias Fade | 5-10% | Low | Medium | Low |
| Follow Sharp Traders | 3-8% | Low | Low | Low |
| AI Forecasting Systems | 4-10% | Very High | High | Very High |
| Mention Market Context | 10-20% | Medium | Low | Medium |

---

## 11. SOURCES

1. **Astral Codex Ten** - "Prediction Market FAQ" - https://astralcodexten.substack.com/p/prediction-market-faq
2. **Maximum Truth** - "Deep Dive on Predicting Elections" - Maxim Lott
3. **Zvi Mowshowitz** - "Prediction Markets: When Do They Work?" - thezvi.wordpress.com
4. **Gwern** - "Prediction Markets" - gwern.net/prediction-market
5. **Polymarket Oracle** - Trader Interviews (Betwick, Scottilicious, Mantic AI, Chris DeMuth Jr.)
6. **80,000 Hours** - Philip Tetlock Interview on Forecasting Research
7. **Polymarket Documentation** - docs.polymarket.com
8. **Manifold Markets** - manifold.markets/about
9. **SportsbookReview** - Kelly Criterion Calculator Documentation

---

## 12. ACTION ITEMS FOR IMPLEMENTATION

### Immediate (Low Effort):
- [ ] Implement fractional Kelly (1/3 to 1/2) for all positions
- [ ] Set up wallet tracking for sharp traders on Stand.trade
- [ ] Identify current underdog bias opportunities

### Medium-Term:
- [ ] Build systematic model for repeatable events (Fed rates, movie openings)
- [ ] Develop contact list for primary source research
- [ ] Cross-platform account setup for arbitrage

### Long-Term:
- [ ] Consider AI forecasting system development
- [ ] Build local contact networks in key regions
- [ ] Develop specialized expertise in specific market verticals

---

*Report compiled by Strategy Researcher Subagent*
*Last Updated: February 12, 2026*
