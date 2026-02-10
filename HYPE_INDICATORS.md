# HYPE_INDICATORS.md
## Identifying and Trading Hype-Driven Markets

> *"Markets are moved by emotion in the short term, fundamentals in the long term. Hype is the bridge between them."*

---

## 10 SIGNS A MARKET IS HYPE-DRIVEN

### 1. Volume Anomalies
| Metric | Normal | Hype Signal |
|--------|--------|-------------|
| Volume vs 20-day Avg | 0.8-1.2x | >3x baseline |
| Volume vs 90-day Avg | 0.7-1.3x | >5x baseline |
| Volume/Price Ratio | Stable | Diverges upward |

**Action:** Monitor for volume spikes >300% of 20-day average without proportional fundamental news.

---

### 2. Social Velocity Spike
- **Twitter/X Mentions:** >10x normal mention rate
- **Reddit Activity:** Unusual activity on r/wallstreetbets, r/cryptocurrency
- **Google Trends:** Search interest up >200% in 7 days
- **StockTwits Message Volume:** >5x 30-day average

**Action:** Set alerts for sudden social mentions spikes. Use tools like: Social Blade, Google Trends API, Brandwatch.

---

### 3. News Cycle Dominance
- **Headline Frequency:** >5 major headlines in 48 hours
- **Cross-Media Presence:** Featured on multiple platforms simultaneously (Twitter, TV, podcasts)
- **Non-Financial Media Coverage:** Mainstream outlets (BuzzFeed, TMZ, major news) covering financial asset
- **Celebrity/Influencer Mentions:** High-follower accounts discussing asset

**Action:** Track news sentiment velocity using: Bloomberg, RavenPack, or custom RSS scrapers.

---

### 4. Price Velocity Extremes
```python
# Price Velocity Score (PVS)
PVS = (Price_today - Price_5d_ago) / (ATR_20 * sqrt(5))

# Hype threshold:
if PVS > 3.0:  # 3x normal volatility-adjusted move
    flag_as_hype_candidate()
```

- **Daily Moves:** >15% on no material news
- **Consecutive Gaps:** 3+ gap-ups in 5 sessions
- **ATH Breaking Speed:** New highs accelerating (parabolic)

---

### 5. Options Flow Distortion
| Indicator | Normal | Hype |
|-----------|--------|------|
| Call/Put Ratio | 0.8-1.2 | >2.0 or <0.5 |
| IV Skew | Gradual | Inverted/steep |
| OTM Call Volume | Low | Explosive |
| 0DTE/Weekly Interest | Normal | Dominant |

**Action:** Monitor for unusual options flow via: Unusual Whales, Cheddar Flow, or Tradytics.

---

### 6. Spread & Liquidity Degradation
- **Bid-Ask Spread Widening:** >2x normal spread
- **Order Book Thinning:** Large gaps between bid levels
- **Slippage on Small Orders:** >0.5% on $1K orders
- **Retail FOMO Signatures:** Small lot (<100 share) orders dominating flow

**Action:** Track Level 2 data for liquidity erosion = retail-driven buying.

---

### 7. Correlation Breakdown
- **Beta Decoupling:** Asset moves opposite to sector/market
- **Sector Rotation Rejection:** Keeps rising while peers fall
- **Cross-Asset Divergence:** Related assets not following

**Action:** Calculate 5-day rolling correlation vs sector ETF. Sudden drops indicate hype.

---

### 8. Short Interest Dynamics
- **Squeeze Signals:** High short interest + sudden price jump
- **Borrow Rate Spikes:** Cost to borrow >50% annually
- **FTD (Fail-to-Deliver) Surge:** Settlement failures increasing
- **Synthetic Long Creation:** Options market implying extreme positioning

**Action:** Check Ortex, S3 Partners for real-time short data.

---

### 9. Meme/Story Metrics
- **Ticker Symbol Mentions:** In memes, TikTok, Instagram
- **Narrative Simplicity:** Story fits in one sentence
- **Emotional Triggers:** Underdog, revenge, anti-establishment themes
- **Merchandise/Community:** Apparel, Discord servers, inside jokes

**Action:** Monitor cultural penetration - hype assets become "lifestyle brands."

---

### 10. Insider/Fundamental Disconnect
- **Insider Selling:** Executives dumping while price rises
- **Analyst Downgrades:** Price rises despite negative notes
- **SEC Filings Gap:** No 8-K, 10-Q, or material news
- **Fundamental Divergence:** Price up 100%, earnings estimates flat

**Action:** Check SEC EDGAR for filing gaps. Price action without filings = pure hype.

---

## CATEGORIES MOST SUSCEPTIBLE TO HYPE

### Tier 1: Celebrity/Personality-Driven
| Category | Examples | Hype Triggers |
|----------|----------|---------------|
| **Elon Markets** | TSLA, DOGE, X (Twitter) | Tweets, product announcements, controversies |
| **Trump Markets** | DJT, PHUN, conservative SPACs | Rallies, legal news, political events |
| **Cathie Wood** | ARKK holdings | ETF flows, new positions |
| **Ryan Cohen** | GME, BBBY | Chairman tweets, turnaround narratives |

**Characteristics:** 
- Cult of personality
- Twitter/X as primary catalyst
- Retail coordination via social
- High short interest base

---

### Tier 2: Narrative-Driven Sectors
| Sector | Current/Past Narratives | Fade Signal |
|--------|------------------------|-------------|
| **AI/Machine Learning** | NVDA, AI tickers, .AI domain names | When "AI" added to any company name |
| **Crypto/Blockchain** | BTC, ETH, meme coins | Celebrity endorsements peak |
| **EV/Space** | RIVN, LCID, SPCE | Production misses vs hype |
| **Green Energy** | Solar, hydrogen, battery plays | Subsidy uncertainty |
| **Metaverse** | META, RBLX, VR plays | Product launches underwhelm |

---

### Tier 3: Event-Driven
| Event Type | Example Markets | Timeline |
|------------|-----------------|----------|
| **Earnings Memes** | meme stocks into earnings | 1-2 weeks before |
| **Product Launches** | iPhone events, Tesla unveilings | Days before/during |
| **Legal Outcomes** | Patent cases, antitrust | Verdict day |
| **Regulatory Decisions** | FDA approvals, crypto ETFs | Decision date |
| **Short Squeeze Events** | GME, AMC, BBBY | Unpredictable, catalyst-driven |

---

### Tier 4: Cultural/Viral Moments
- **Meme Stocks:** GME, AMC (reflexive, self-reinforcing)
- **TikTok Trends:** Small caps mentioned in viral videos
- **Political Movements:** ESG, anti-ESG, "woke" vs "based" plays
- **Controversy Plays:** Cancel culture rebounds, "buy to support"
- **Meme Coins:** DOGE, SHIB, PEPE (pure narrative, zero fundamentals)

---

## HYPE LIFECYCLE & TRADING STRATEGIES

### Phase 1: EARLY HYPE (Accumulation)
**Timeline:** Days to weeks  
**Characteristics:**
- Volume 2-3x normal
- Social mentions increasing but not viral
- Price up 20-50% from base
- Early adopters accumulating
- Mainstream unaware

**Trading Strategy:**
```
Position: SMALL LONG (speculative)
Entry: On breakout + volume confirmation
Stop: 10% below entry or recent support
Target: 2-3x from entry (trail stops)
Risk: 1-2% of portfolio max
```

**Action:** 
- ✅ Take small position if thesis validated
- ✅ Set strict stops
- ❌ Don't chase >30% in one day

---

### Phase 2: PEAK HYPE (Euphoria)
**Timeline:** Hours to days  
**Characteristics:**
- Volume 5-10x normal
- Trending on Twitter/Reddit
- Mainstream news coverage
- Everyone talking about it
- "This time is different" narratives
- Retail FOMO at maximum
- Parabolic price action

**Trading Strategy:**
```
Position: FADE/SHORT (contrarian)
Entry: On exhaustion signals (see below)
Stop: Above recent high or 10%
Target: Retracement to 50% of hype move
Risk: 2-3% (high conviction setups only)
```

**Exhaustion Signals:**
- RSI >85 on daily
- 3+ consecutive gap-ups
- Record volume day
- "Top" posts getting viral
- Inverse ETFs launching
- Everyone in the trade (no buyers left)

**Action:**
- ✅ Take profits on longs
- ✅ Small short on exhaustion
- ❌ No new longs here

---

### Phase 3: HYPE EXHAUSTION (Reversal)
**Timeline:** Days to weeks  
**Characteristics:**
- Volume declining but still elevated
- Failed breakout attempts
- Lower highs forming
- Early shorts getting aggressive
- Bag holders forming
- "Diamond hands" narrative

**Trading Strategy:**
```
Position: SHORT / PUTS
Entry: On break of key support or lower high
Stop: Above recent lower high
Target: 50-61.8% Fibonacci retracement
Risk: 2-3%
```

**Action:**
- ✅ Add to shorts on breakdown
- ✅ Buy OTM puts for asymmetry
- ❌ Don't catch falling knife

---

### Phase 4: POST-HYPE (Recovery/Base)
**Timeline:** Weeks to months  
**Characteristics:**
- Volume back to normal
- Price found new equilibrium
- "It's over" sentiment
- Weak hands flushed
- Fundamentals reasserting
- Short interest declining

**Trading Strategy:**
```
Position: ACCUMULATION (if thesis intact)
Entry: On support hold or reversal pattern
Stop: Below major support
Target: Prior resistance levels
Risk: 2-3%
```

**Action:**
- ✅ Evaluate fundamentals
- ✅ Buy if thesis unchanged
- ✅ Wait for base formation

---

## HYPE SCORING METHODOLOGY

### Composite Hype Score (CHS)
Calculate on scale of 0-100:

```python
def calculate_hype_score(metrics):
    score = 0
    
    # Volume Component (0-25 pts)
    volume_ratio = current_volume / avg_volume_20d
    if volume_ratio > 10: score += 25
    elif volume_ratio > 5: score += 20
    elif volume_ratio > 3: score += 15
    elif volume_ratio > 2: score += 10
    else: score += max(0, (volume_ratio - 1) * 10)
    
    # Price Velocity (0-25 pts)
    pvs = price_velocity_score()  # defined earlier
    if pvs > 5: score += 25
    elif pvs > 3: score += 20
    elif pvs > 2: score += 15
    elif pvs > 1.5: score += 10
    else: score += max(0, (pvs - 1) * 10)
    
    # Social Metrics (0-20 pts)
    if social_mentions_change > 1000: score += 20
    elif social_mentions_change > 500: score += 15
    elif social_mentions_change > 200: score += 10
    elif social_mentions_change > 100: score += 5
    
    # Options Flow (0-15 pts)
    call_put_ratio = get_call_put_ratio()
    if call_put_ratio > 5: score += 15
    elif call_put_ratio > 3: score += 12
    elif call_put_ratio > 2: score += 8
    elif call_put_ratio > 1.5: score += 5
    
    # News/Media (0-15 pts)
    news_count = count_major_headlines(48_hours)
    if news_count > 10: score += 15
    elif news_count > 5: score += 10
    elif news_count > 3: score += 5
    
    return min(100, score)
```

---

### Hype Score Interpretation

| Score | Classification | Action |
|-------|---------------|--------|
| 0-20 | No Hype | Trade normally |
| 21-40 | Early Hype | Small speculative long |
| 41-60 | Moderate Hype | Monitor for entry/fade |
| 61-75 | High Hype | Prepare fade, tighten stops |
| 76-90 | Extreme Hype | Active fade/short |
| 91-100 | Bubble Territory | Heavy short, no longs |

---

### Weighted Variations

**For Crypto:**
- Increase social weight to 30%
- Add exchange flow metrics (inflows/outflows)
- On-chain velocity as volume proxy

**For Meme Stocks:**
- Increase options flow weight to 25%
- Add short interest component (20%)
- Reddit sentiment analysis critical

**For Event-Driven:**
- Increase news weight to 30%
- Add calendar proximity factor
- Regulatory filing watch

---

## ACTIONABLE DETECTION WORKFLOW

### Daily Hype Scan
```
1. Run volume scan: >3x 20-day average
2. Cross-reference with social mention spikes
3. Check for news catalyst or narrative
4. Calculate Hype Score
5. Determine lifecycle phase
6. Execute appropriate strategy
```

### Alert Setup
**Technical Alerts:**
- Volume spike >300%
- Price move >15% (day)
- RSI >75 or <25
- Gap up/down >10%

**Social Alerts:**
- Twitter trending (financial)
- Reddit front page mentions
- StockTwits trending
- Google Trends breakout

**Options Alerts:**
- Unusual call volume
- IV spike >50%
- OTM call buying surge

---

## RISK MANAGEMENT FOR HYPE TRADING

### The Hype Trading Rules
1. **Never bet against the hype until exhaustion confirmed**
2. **Size small - these are lottery tickets**
3. **Use defined risk (options, not stock shorts)**
4. **Set time stops (hype decays fast)**
5. **Take profits quickly (don't get greedy)**
6. **Never average into losers**
7. **Respect the squeeze potential**

### Position Sizing
- Early Hype Long: 1-2% max
- Peak Hype Fade: 1-2% max
- Hype Exhaustion Short: 2-3% max
- Post-Hype Recovery: 3-5% max

---

## TOOLS & RESOURCES

### Data Sources
| Data | Free | Paid |
|------|------|------|
| Volume/Price | Yahoo Finance | Bloomberg, Refinitiv |
| Social Mentions | Reddit API, Google Trends | Brandwatch, Sprout |
| Options Flow | CBOE | Unusual Whales, Cheddar Flow |
| Short Interest | FINRA | Ortex, S3 Partners |
| News | RSS feeds | RavenPack, Bloomberg |

### Recommended Tech Stack
- **Python:** pandas, yfinance, praw (Reddit), tweepy
- **Alerts:** TradingView, ThinkorSwim alerts
- **Social:** ApeWisdom, SwaggyStocks
- **Options:** MarketChameleon, FlowAlgo

---

## CASE STUDIES

### Case Study 1: GME (Jan 2021)
- **Early Hype:** r/wallstreetbets coordination (Dec 2020)
- **Peak Hype:** $483 peak, mainstream news (Jan 28)
- **Exhaustion:** Trading halts, broker restrictions
- **Post-Hype:** $40 base, then multiple cycles

**Lesson:** Hype can override fundamentals for months. Don't short too early.

---

### Case Study 2: DOGE (April 2021)
- **Catalyst:** Elon tweets + SNL appearance
- **Peak:** $0.74 pre-SNL
- **Fade:** "The Dogefather" SNL sketch (sell the news)
- **Result:** -75% in 3 months

**Lesson:** Event-driven hype peaks AT the event, not after.

---

### Case Study 3: NVDA (2023 AI Boom)
- **Narrative:** ChatGPT, AI infrastructure
- **Characteristics:** Sustained, fundamental-backed hype
- **Differentiation:** Actual earnings growth vs narrative
- **Result:** Legitimate trend, not pure hype

**Lesson:** Distinguish between hype and real paradigm shifts.

---

## SUMMARY

**Key Takeaways:**
1. Hype is quantifiable through volume, velocity, social, and options metrics
2. Different asset classes have different hype signatures
3. Lifecycle phases require different strategies
4. Never fight hype until exhaustion is confirmed
5. Risk management is critical - these are asymmetric bets

**Remember:**
> "The market can stay irrational longer than you can stay solvent." - Keynes

Hype trading is about timing, not prediction. Use these indicators to measure the temperature of the market, not to predict the future.

---

*Last Updated: 2026-02-09*  
*Version: 1.0*
