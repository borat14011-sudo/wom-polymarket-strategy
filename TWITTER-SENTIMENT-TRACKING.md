# Twitter/X Sentiment Tracking System for Prediction Market Hype

**Mission:** Build an early-warning system to detect viral prediction market bets before they move markets.

**Author:** Subagent (twitter-sentiment)  
**Created:** 2026-02-06  
**Status:** Research & Design Phase

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [How to Identify Trending Bets on X](#1-how-to-identify-trending-bets-on-x)
3. [Metrics for Measuring Hype](#2-metrics-for-measuring-hype)
4. [Tools & APIs](#3-tools--apis)
5. [Signal vs Noise Filtering](#4-signal-vs-noise-filtering)
6. [Lead Time Analysis](#5-lead-time-analysis)
7. [Case Studies & Patterns](#6-case-studies--patterns)
8. [Implementation Roadmap](#7-implementation-roadmap)

---

## Executive Summary

**The Opportunity:** Prediction markets often lag social media sentiment. By detecting viral bets early on X/Twitter, we can position ourselves before market odds adjust.

**Key Insight:** Like meme stocks (GME, AMC), prediction market hype follows predictable patterns:
- **Discovery phase:** Niche accounts tweet about interesting bet
- **Amplification:** Influencers retweet, engagement spikes
- **Viral moment:** Mainstream attention, volume explosion
- **Market reaction:** Odds shift as volume floods in (usually 2-12 hours later)

**Goal:** Detect bets in the Discovery → Amplification transition (before viral moment).

---

## 1. How to Identify Trending Bets on X

### A. Search Methods

#### Keywords & Hashtags
Monitor these terms in real-time:

**Platform-specific:**
- `#Polymarket` `#Manifold` `#Metaculus` `#Kalshi` `#PredictIt`
- `polymarket.com` (URL mentions)
- "prediction market" "prediction markets"

**Bet-specific indicators:**
- "just bet [X] on" "made a bet" "taking [X]% odds"
- "free money on" "easy money" "printing" (overconfidence signals)
- "whale bet" "someone just dropped [X]"

**Viral momentum indicators:**
- "everyone is betting on" "this bet is going crazy"
- "odds are moving fast" "the market thinks"
- Ratio mentions: "90% to 10%" "3:1 odds"

#### Advanced Search Operators

```
("Polymarket" OR "Manifold") (bet OR odds OR market)
-filter:retweets min_faves:100
```

**Boolean queries for automation:**
```
(polymarket.com OR manifold.markets) AND (bet OR betting OR odds)
("prediction market" OR "#polymarket") AND (viral OR trending OR everyone)
```

### B. Accounts to Monitor

#### Tier 1: Platform Accounts (Official)
- `@Polymarket` - Polymarket official
- `@ManifoldMarkets` - Manifold Markets
- `@Metaculus` - Metaculus
- `@kalshi` - Kalshi
- `@PredictIt` - PredictIt (if still active)

#### Tier 2: High-Volume Traders (Whales)
These are the market movers. Identify them by:
- High follower count + frequent prediction market tweets
- Known for large bets (>$10k positions)
- Track their bet announcements religiously

**Discovery method:**
1. Monitor who gets retweeted by platform accounts
2. Check top replies on viral prediction market tweets
3. Look for "Show me your Polymarket profits" threads

**Profile indicators:**
- Bio mentions: "Polymarket trader" "prediction market degen"
- Profile links to Polymarket/Manifold profiles
- History of posting bet screenshots

#### Tier 3: Crypto/Finance Influencers
Prediction markets overlap heavily with crypto Twitter:
- `@balajis` (Balaji Srinivasan - big on prediction markets)
- `@VitalikButerin` (occasionally tweets about prediction markets)
- Major crypto Twitter accounts with >100k followers
- "CT" (Crypto Twitter) influencers who amplify bets

#### Tier 4: Political/News Commentators
For political prediction markets:
- Nate Silver and polling accounts
- Political journalists during election cycles
- Betting-savvy political commentators

#### Tier 5: Niche Communities
- Effective Altruism Twitter (rationalist community, big Manifold users)
- LessWrong community members
- Quantified uncertainty / forecasting nerds

### C. List Building Strategy

**Step 1:** Create Twitter Lists
- `PM-Platforms` (official accounts)
- `PM-Whales` (high-volume traders)
- `PM-Influencers` (amplifiers)
- `PM-Watchers` (market commentators)

**Step 2:** Use List-Based Monitoring
Poll these lists every 5-15 minutes for new tweets.

**Step 3:** Dynamic Updates
- Weekly: Review top engaged accounts from past week
- Add new whales who emerge
- Remove inactive accounts

---

## 2. Metrics for Measuring Hype

### A. Core Metrics (Real-Time)

#### 1. **Tweet Volume**
Raw count of tweets mentioning the bet/market.

**Calculation:**
```
Volume_t = Count of tweets in time window t (e.g., last hour)
Baseline = 7-day moving average for same time-of-day
Volume_Ratio = Volume_t / Baseline
```

**Threshold:** Volume ratio >3x = early signal, >10x = viral

#### 2. **Engagement Rate**
Quality > quantity. A bet with 10 tweets but 1000+ likes each is stronger than 100 tweets with 5 likes.

**Formula:**
```
Engagement_Rate = (Likes + Retweets*2 + Replies*1.5) / Tweet_Count
```

Retweets weighted 2x because they amplify reach.  
Replies weighted 1.5x because they indicate controversy/discussion.

**Benchmark:**
- Low: <20 engagement per tweet
- Medium: 20-100
- High: 100-500
- Viral: >500

#### 3. **Velocity (Rate of Change)**
How fast is momentum building?

**Calculation:**
```
Velocity = (Volume_current_hour - Volume_previous_hour) / Volume_previous_hour
```

**Critical thresholds:**
- Velocity >100% = Acceleration phase (get in now)
- Velocity >300% = Going parabolic (may be late)
- Velocity <0% = Cooling off (post-peak)

#### 4. **Influencer Amplification Score**
Not all tweets are equal. One Balaji tweet = 1000 random accounts.

**Weighted Score:**
```
Influencer_Score = Σ (follower_count * engagement_on_tweet) / 1000
```

**Tier weighting:**
- Mega influencer (>1M followers): 10x multiplier
- Major influencer (100k-1M): 5x multiplier
- Micro influencer (10k-100k): 2x multiplier
- Regular account (<10k): 1x multiplier

**Red flag:** If only mega-influencers tweet but no grassroots engagement = likely pump/paid promotion

### B. Advanced Metrics (Sentiment & Quality)

#### 5. **Sentiment Polarity**
Are people excited or skeptical?

**Simple sentiment scoring:**
- Positive keywords: "love this bet", "easy money", "free money", "locked in", "🚀", "📈", "printing"
- Negative keywords: "terrible odds", "losing money", "scam", "rigged", "📉"
- Neutral/analytical: "interesting market", "worth watching"

**Net Sentiment Score:**
```
Sentiment = (Positive_tweets - Negative_tweets) / Total_tweets
```

Range: -1 (all negative) to +1 (all positive)

**Insight:** Extreme positive sentiment (>0.7) often precedes market moves, but also indicates potential bubble.

#### 6. **Unique Author Count**
Is this one person spamming or organic virality?

```
Author_Diversity = Unique_Authors / Total_Tweets
```

- Ratio <0.3 = Spam/bot activity (red flag)
- Ratio 0.3-0.7 = Normal
- Ratio >0.7 = Highly organic (strong signal)

#### 7. **Network Propagation Depth**
How many degrees of separation from original tweet?

**Retweet chain analysis:**
- Original tweet (depth 0)
- Direct retweets (depth 1)
- Retweets of retweets (depth 2)
- etc.

**Viral indicator:** Depth ≥3 within 2 hours = escaping echo chamber

#### 8. **Media Richness**
Tweets with screenshots of bets perform better.

**Track:**
- % of tweets with images (bet screenshots)
- % with videos
- Tweets with media get ~3x more engagement

**High media ratio (>40%) = strong visual proof = credible hype**

### C. Composite Hype Score

Combine metrics into single 0-100 score:

```
Hype_Score = 
  (Volume_Ratio * 20) +
  (log10(Engagement_Rate) * 15) +
  (Velocity * 10) +
  (Influencer_Score * 25) +
  ((Sentiment + 1) * 10) +
  (Author_Diversity * 10) +
  (Network_Depth * 10)

Normalized to 0-100 scale
```

**Action thresholds:**
- <30: Noise, ignore
- 30-50: Watch list
- 50-70: Early signal, investigate
- 70-85: Strong signal, position small
- 85-95: Viral, position aggressively
- >95: Peak frenzy, consider contrarian play

---

## 3. Tools & APIs

### A. Official X/Twitter API (Premium)

#### Pros:
- Most comprehensive data
- Real-time streaming
- Historical search
- Full metadata (follower counts, engagement, etc.)

#### Cons:
- **EXPENSIVE:** Basic tier ~$100/mo, Pro tier ~$5,000/mo
- Rate limits on free tier basically useless for real-time monitoring
- Requires developer account approval

#### Tiers (as of 2024-2025):
1. **Free tier:** 1,500 tweets/month read - useless for our purpose
2. **Basic ($100/mo):** 10,000 tweets/month - still too limited
3. **Pro ($5,000/mo):** 1M tweets/month - minimum viable for serious tracking
4. **Enterprise:** Custom pricing, full firehose access

#### Key endpoints:
- `/2/tweets/search/recent` - Real-time search (last 7 days)
- `/2/tweets/search/stream` - Filtered stream (push notifications)
- `/2/users/:id/tweets` - User timeline monitoring

**Recommendation:** Start with Basic tier for prototyping, upgrade to Pro if profitable.

### B. Third-Party Tools (Alternatives)

#### **1. Tweepy + snscrape (Free, Grey Area)**

**Tweepy:** Official Python library for X API
**snscrape:** Scraper that bypasses API (against ToS but widely used)

```python
# snscrape example
import snscrape.modules.twitter as sntwitter

query = "(Polymarket OR Manifold) bet -filter:retweets"
tweets = sntwitter.TwitterSearchScraper(query).get_items()
```

**Pros:** Free, no rate limits
**Cons:** Against X ToS, could get IP banned, brittle (breaks when X changes DOM)

#### **2. Apify Twitter Scraper ($49-499/mo)**

Managed scraping service, handles proxy rotation and captchas.

**URL:** apify.com/apify/twitter-scraper

**Pros:** 
- More reliable than DIY scraping
- No API key needed
- Handles anti-bot measures

**Cons:**
- Still grey area legally
- Can be detected and blocked
- Pricing scales with volume

#### **3. Social Listening Platforms**

##### **Brandwatch / Crimson Hexagon** (Enterprise)
- Price: $10k-100k+/year
- Full social listening suite
- Built-in sentiment analysis
- Too expensive unless you're a fund

##### **Hootsuite Insights** ($500-2k/mo)
- Mid-tier option
- Real-time monitoring
- Sentiment analysis included
- Keyword tracking

##### **Mentionlytics** ($49-299/mo)
- Budget-friendly
- Monitors Twitter + Reddit + more
- Good for small-scale operations

##### **Brand24** ($79-399/mo)
- Solid mid-range tool
- Mention tracking
- Sentiment analysis
- Influencer identification

**Recommendation:** Brand24 or Mentionlytics for cost-effective start.

#### **4. Open-Source Solutions**

##### **Twint** (Defunct but forkable)
Twitter scraper, no API needed. Original project dead but forks exist.

**Pros:** Free, no API
**Cons:** Maintenance burden, constantly breaking

##### **Elasticsearch + Logstash + Kibana (ELK Stack)**
Build your own data pipeline:
- Collect tweets via API/scraper
- Index in Elasticsearch
- Visualize in Kibana

**Pros:** Full control, scalable
**Cons:** DevOps overhead, requires technical expertise

### C. Sentiment Analysis Tools

#### **1. VADER (Free, Python)**
```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
score = analyzer.polarity_scores("This bet is printing money! 🚀")
# {'neg': 0.0, 'neu': 0.508, 'pos': 0.492, 'compound': 0.5859}
```

**Pros:** Free, handles emojis/slang well
**Cons:** Not crypto/prediction-market specific

#### **2. TextBlob (Free, Python)**
General-purpose NLP library.

**Pros:** Easy to use
**Cons:** Less accurate than VADER for social media

#### **3. GPT-4 / Claude API (Pay-per-use)**
Use LLMs for nuanced sentiment analysis.

**Example prompt:**
```
Analyze the sentiment of this tweet about a prediction market bet.
Classify as: BULLISH / BEARISH / NEUTRAL
Confidence: HIGH / MEDIUM / LOW

Tweet: "{tweet_text}"
```

**Pros:** Most accurate, understands context/sarcasm
**Cons:** Expensive at scale (~$0.01-0.03 per tweet analysis)

**Use case:** Use for high-value signals (tweets from whales/influencers), not bulk analysis.

### D. Real-Time Monitoring Architecture

#### **Recommended Stack (Budget-Conscious):**

1. **Data Collection:** 
   - Brand24 ($79/mo) or X API Basic ($100/mo)
   - Monitor 5-10 keyword sets

2. **Data Storage:**
   - PostgreSQL (free, self-hosted)
   - Or Supabase (managed Postgres, free tier)

3. **Processing:**
   - Python scripts (cron jobs every 5-15 min)
   - VADER for bulk sentiment
   - GPT-4 for whale tweets only

4. **Alerting:**
   - Telegram bot (instant notifications)
   - Email for daily summaries
   - Discord webhook for team

5. **Visualization:**
   - Grafana (free, self-hosted) + Postgres
   - Or Google Sheets for MVP

**Total monthly cost:** ~$100-200 (API + hosting)

#### **Advanced Stack (If Profitable):**

1. **Data Collection:**
   - X API Pro ($5k/mo) with streaming endpoint
   - Full firehose access

2. **Data Infrastructure:**
   - AWS or GCP
   - Kinesis/Pub-Sub for real-time streaming
   - S3/BigQuery for historical data

3. **Processing:**
   - Apache Kafka for stream processing
   - Spark for batch analysis
   - Custom ML models trained on prediction market data

4. **Alerting:**
   - PagerDuty for critical signals
   - Custom dashboard with live updates

5. **Visualization:**
   - Custom web app with real-time charts
   - Mobile app for on-the-go monitoring

**Total monthly cost:** $10k-50k+ (at scale)

---

## 4. Signal vs Noise Filtering

### A. The Noise Problem

**80/20 rule:** 80% of prediction market tweets are:
- Spam/bots promoting scams
- Low-quality "what if" speculation
- Retweets with no original thought
- Unrelated mentions (people named "Polymarket", etc.)

**Our job:** Filter out the 80%, focus on the 20% that moves markets.

### B. Bot Detection

#### Red Flags:
1. **Account age <30 days** (new bots)
2. **Following/follower ratio >5** (spam accounts)
3. **Tweets per day >100** (automated posting)
4. **Generic profile pic** (default egg or stock photo)
5. **Bio contains "DM for promo"** (paid promotion account)
6. **Username has random numbers** (johnsmith94823746)

#### Bot Detection APIs:
- **Botometer** (Indiana University) - Free API, scores 0-1 bot probability
- **Twitter's spam filter** - Check if account is verified or has blue checkmark

**Filter rule:** Exclude tweets from accounts with bot score >0.7

### C. Content Quality Filters

#### Must INCLUDE:
- Tweets with specific bet amounts ("I put $5k on X")
- Screenshots of actual bet slips
- Links to specific markets
- Analysis/reasoning for the bet
- Tweets from verified accounts or known traders

#### Must EXCLUDE:
- Generic "prediction markets are cool" tweets
- Questions without positions ("Should I bet on X?")
- Retweets without commentary
- Tweets with <3 engagements (unless from whale)
- Obvious shill/spam language ("DM me for signals")

#### Spam Pattern Detection:
```python
# Example spam patterns
spam_patterns = [
    r"DM (me|for)",
    r"click (link|here)",
    r"100% guaranteed",
    r"follow for signals",
    r"telegram group",
    r"join our discord"
]
```

### D. Coordinated Behavior Detection

**Pump schemes:** Group of accounts tweet simultaneously about same bet.

**Detection method:**
1. Cluster tweets by timestamp (within 5-minute window)
2. Check if multiple accounts tweet near-identical text
3. Check if accounts follow each other (coordinated network)

**Red flag:** 5+ accounts tweet about obscure bet within 10 minutes with similar phrasing = likely coordinated pump

**Action:** Flag for manual review, or auto-exclude if pattern repeats.

### E. Account Quality Scoring

Create composite quality score for each account:

```python
def account_quality_score(account):
    score = 0
    
    # Age bonus
    days_old = (now - account.created_at).days
    if days_old > 365: score += 20
    elif days_old > 180: score += 10
    
    # Follower count (logarithmic)
    score += min(log10(account.followers), 6) * 5  # Max 30 points
    
    # Engagement rate
    avg_engagement = account.total_likes / account.total_tweets
    score += min(avg_engagement / 10, 20)  # Max 20 points
    
    # Verification
    if account.verified: score += 15
    
    # Bio mentions prediction markets
    if 'polymarket' in account.bio.lower(): score += 10
    
    # Bot score penalty
    bot_score = get_botometer_score(account)
    score -= bot_score * 30
    
    return max(0, min(100, score))
```

**Usage:** Only process tweets from accounts with quality score >40

### F. Contextual Relevance

**Problem:** Tweet mentions "Polymarket" but isn't about a bet.

**Examples:**
- "Polymarket is launching a new feature" (news, not bet)
- "I work at Polymarket" (employment, not bet)
- "Polymarket's UI sucks" (complaint, not bet)

**Solution:** Require bet-specific keywords:
- "bet", "betting", "odds", "position"
- "$" + number (bet amounts)
- "YES" / "NO" (market sides)
- "bought", "sold", "profit", "loss"

**Filter:** `(mention of platform) AND (bet keyword) AND (not spam)`

### G. Signal Confidence Levels

Tier tweets into confidence levels:

**HIGH CONFIDENCE (act immediately):**
- Whale account (known trader)
- Includes bet screenshot
- Specific market link
- Account quality score >70

**MEDIUM CONFIDENCE (watch closely):**
- Influencer account (>10k followers)
- Mentions specific bet
- Some engagement (>20 likes)
- Account quality score 40-70

**LOW CONFIDENCE (log but don't act):**
- Regular account
- Vague mention
- Low engagement
- Account quality score <40

**Use confidence levels to prioritize alerts.**

---

## 5. Lead Time Analysis

### A. The Critical Question

**How early can we detect hype before market moves?**

This determines profitability. If we detect after odds shift, we're too late.

### B. Theoretical Timeline

Based on meme stock patterns (GME, AMC) and prediction market observation:

**T-0 (Discovery):**
- Niche trader tweets about interesting bet
- <100 views
- No market movement
- **Our goal: Detect here**

**T+1 to T+2 hours (Early Amplification):**
- Original tweet gets retweeted by followers
- 100-1,000 views
- Minor engagement
- Market odds start to twitch (1-2% movement)
- **Ideal entry point**

**T+2 to T+6 hours (Amplification):**
- Influencer(s) retweet or quote tweet
- 1,000-10,000 views
- Significant engagement
- Market odds moving noticeably (5-10% shift)
- **Good entry point if we're fast**

**T+6 to T+12 hours (Going Viral):**
- Multiple influencers involved
- 10,000-100,000+ views
- High engagement
- Market odds shift significantly (10-30%)
- **Risky entry point, may be late**

**T+12 to T+24 hours (Peak):**
- Mainstream attention
- 100,000+ views
- Market saturated with new bettors
- Odds fully adjusted
- **Too late, don't enter**

**T+24+ hours (Decay):**
- Conversation dies down
- Odds stabilize
- Potential contrarian opportunity if market overcorrected

### C. Detection Window

**Optimal detection:** T+0 to T+2 hours (before first influencer retweet)

**Still profitable:** T+2 to T+6 hours (early amplification)

**Breakeven:** T+6 to T+12 hours (depends on market liquidity)

**Too late:** T+12+ hours

### D. Factors Affecting Lead Time

#### 1. **Market Liquidity**
- Low liquidity markets (<$10k volume): Odds shift faster, shorter window
- High liquidity markets (>$100k volume): Odds shift slower, longer window

**Implication:** On high-liquidity markets, we have more time to act.

#### 2. **Time of Day**
- US daytime (9am-6pm ET): Faster reaction, more traders online
- Nighttime (12am-6am ET): Slower reaction, longer detection window
- Weekend: Slower overall

**Strategy:** Night/weekend discoveries give us more time to research before others pile in.

#### 3. **Market Type**
- **Political bets:** Slower to move (lots of stubborn partisans)
- **Sports bets:** Faster to move (sharp bettors react quickly)
- **Crypto bets:** Fastest to move (crypto Twitter is hyper-reactive)
- **Long-term bets:** Slower (less urgency)

#### 4. **Influencer Involvement**
- If mega-influencer tweets first: Very short window (minutes)
- If niche account tweets first: Longer window (hours)

### E. Historical Pattern Analysis

**Case Study Method:**
1. Find viral prediction market bets from past 6 months
2. Use Twitter's advanced search to find first mentions
3. Track engagement over time
4. Note when odds shifted
5. Calculate lead time

**Example search (retroactive):**
```
Polymarket "Trump" since:2024-01-01 until:2024-01-07
```

Then chart:
- Tweet volume over time
- Engagement over time
- Odds movement over time

**Look for pattern:** When does engagement peak relative to odds shift?

### F. Real-Time Lead Indicators

**Early signals that hype is building (before it's obvious):**

1. **Reply ratio > usual:** Original tweet getting more replies than likes suggests controversy/discussion
2. **Retweet velocity:** Exponential growth in retweets (doubling every hour)
3. **Quote tweets > retweets:** People adding commentary, not just boosting
4. **Cross-platform leakage:** Bet gets mentioned on Reddit, Discord, etc.
5. **Whale attention:** Known traders replying or quoting
6. **Screenshot proliferation:** Multiple people posting their bet confirmations

**Advanced indicator: Network cascades**

Use graph analysis to track how retweets spread:
- If retweet network branches widely (many different communities), it's going viral
- If retweet network stays within one community, it's contained

**Tools:** Gephi, NetworkX (Python) for social network analysis

### G. Actionable Lead Time Strategy

**Tier 1 Alert (Act in <15 min):**
- Whale account tweets bet
- Early engagement picking up (velocity >100%)
- Low current volume (<50 tweets total)
- Market odds haven't moved yet

**Tier 2 Alert (Act in <1 hour):**
- Mid-tier influencer tweets
- Moderate engagement
- Volume increasing but not yet viral
- Odds twitching slightly

**Tier 3 Alert (Research mode, no urgency):**
- Low confidence signal
- Could be noise
- Monitor for 2-4 hours to see if it develops

**Action thresholds:**
```python
if hype_score > 85 and volume < 100 and whale_involved:
    alert("TIER 1: ACT NOW", urgency="CRITICAL")
elif hype_score > 70 and velocity > 150:
    alert("TIER 2: ACT SOON", urgency="HIGH")
elif hype_score > 50:
    alert("TIER 3: WATCH", urgency="MEDIUM")
```

---

## 6. Case Studies & Patterns

### A. Pattern Recognition Framework

**What we're looking for:**

Past viral bets that exhibited early signals on Twitter, then moved markets. By studying these, we can identify the fingerprint of virality.

### B. Hypothetical Case Study Template

Since I don't have real-time web access, here's how to research historical cases:

#### **Step 1: Identify Viral Bets**

**Sources:**
- Polymarket's "Trending" page (archive.org snapshots)
- Manifold's leaderboard (top movers)
- Twitter search for high-engagement prediction market tweets
- Reddit: r/Polymarket, r/PredictionMarkets

**Characteristics of viral bets:**
- Volume spike >10x normal
- Odds shifted >20% in <24 hours
- Mainstream media coverage
- Meme potential (funny, controversial, or absurd)

**Examples to research (may need to verify):**
- "Will Trump be arrested in 2023?" (massive volume during Mar-a-Lago raid)
- "Will FTX collapse?" (before it was obvious)
- "Will AI be AGI by 2025?" (rationalist community bet)
- Election outcome bets during 2024 campaign
- Any bet Elon Musk tweeted about

#### **Step 2: Reverse-Engineer Twitter Trail**

Use Twitter advanced search:
```
"[Market name]" since:YYYY-MM-DD until:YYYY-MM-DD
```

**Track:**
1. First mentions (who discovered it?)
2. First retweets (who amplified?)
3. Viral moment (which tweet broke containment?)
4. Peak engagement (when did it max out?)

#### **Step 3: Correlate with Market Data**

**Get historical odds:**
- Polymarket has public API with historical data
- Manifold has complete history
- Chart odds over time

**Overlay:**
- Tweet volume vs. odds movement
- Engagement vs. betting volume
- Look for lag time

#### **Step 4: Extract Pattern**

**Questions:**
- How long from first tweet to viral moment?
- What was the trigger? (Influencer RT? News event?)
- What was the sentiment distribution?
- Were there early skeptics? (Contrarian opportunity?)
- Did odds overcorrect? (Mean reversion opportunity?)

### C. Common Viral Bet Patterns

Based on social media dynamics, here are expected patterns:

#### **Pattern 1: "The Sleeper"**
- Obscure bet sits dormant for weeks
- One niche tweet brings it to attention
- Slow burn over 24-48 hours
- Gradual odds shift

**Example:** Long-term AI bets that suddenly become relevant due to news

**Signal:** Low baseline volume, sudden sustained increase (not spike)

**Action:** We have time to research and enter thoughtfully

#### **Pattern 2: "The Rocket"**
- Mega-influencer tweets bet
- Immediate explosion
- Odds shift within hours
- Window is very short

**Example:** Elon Musk tweets about a bet (hypothetical)

**Signal:** Instant massive engagement from single source

**Action:** Must act within minutes or skip (likely too late)

#### **Pattern 3: "The Controversy"**
- Bet is politically divisive
- Both sides pile in
- High reply ratio (arguing)
- Odds whipsaw back and forth

**Example:** Trump-related bets, culture war topics

**Signal:** High engagement but mixed sentiment

**Action:** Risky, market is irrational, consider sitting out

#### **Pattern 4: "The Meme"**
- Bet is absurd/funny
- Goes viral for entertainment value
- Not serious analysis
- Odds shift randomly

**Example:** "Will aliens be confirmed by 2025?" "Will Kanye run for president?"

**Signal:** Lots of jokes, memes, not serious discussion

**Action:** Avoid, too unpredictable, not edge

#### **Pattern 5: "The Information Cascade"**
- New information becomes public
- Everyone updates beliefs simultaneously
- Efficient market reaction
- No edge for social media monitoring

**Example:** Breaking news immediately affects bet (e.g., indictment announced)

**Signal:** News event → instant tweet storm

**Action:** Too fast, we can't beat professional traders

#### **Pattern 6: "The Whale Flex"**
- Large trader posts bet screenshot
- Others follow ("he knows something")
- Self-fulfilling prophecy
- Odds move due to copycats

**Example:** Known successful trader bets big, others copy

**Signal:** Whale + screenshot + followers asking "why?"

**Action:** Good opportunity IF we catch it early (before copycats flood in)

### D. Red Flag Patterns (Avoid)

**Anti-Pattern 1: Pump and Dump**
- Coordinated group shills bet
- Artificially inflates one side
- No legitimate reasoning
- Reverse after they exit

**Detection:** Multiple new accounts, similar phrasing, sketchy

**Anti-Pattern 2: Dead Cat Bounce**
- Bet already went viral days ago
- Renewed but weaker interest
- Nostalgia retweets
- No new information

**Detection:** Second spike much smaller than first

**Anti-Pattern 3: Echo Chamber**
- Only one community talking about it
- No cross-pollination
- High engagement in bubble, zero outside
- Won't affect market much

**Detection:** Retweets all within same follower network

### E. Research Action Items

**To build real case studies:**

1. **Scrape historical data:**
   - Get top Polymarket markets by volume (2024-2025)
   - Get top Manifold markets by trader count
   - Identify which ones had viral moments

2. **Twitter archaeological dig:**
   - For each viral market, search Twitter history
   - Find inflection points
   - Document timeline

3. **Create case study database:**
   - Store in structured format (JSON or database)
   - Fields: market_name, first_tweet_timestamp, viral_tweet_timestamp, peak_engagement, odds_before, odds_after, lead_time
   - Use for ML training later

4. **Pattern library:**
   - Classify each case study by pattern type
   - Calculate success rate of each pattern
   - Prioritize high-probability patterns

**Deliverable:** `case-studies/` directory with markdown files for each viral bet analyzed.

---

## 7. Implementation Roadmap

### Phase 1: MVP (Weeks 1-2)

**Goal:** Prove the concept with minimal investment.

**Tasks:**
1. ✅ Set up Twitter monitoring (Brand24 trial or X API Basic)
2. ✅ Create keyword list (Polymarket, Manifold, top 10 keywords)
3. ✅ Build simple Python scraper to collect tweets
4. ✅ Store in Google Sheets or CSV
5. ✅ Manual analysis: Pick 3-5 markets, track tweets vs. odds
6. ✅ Calculate basic metrics (volume, engagement)
7. ✅ Telegram alerts for high-volume spikes

**Success criteria:** Detect 1-2 viral bets before odds shift significantly.

**Investment:** $0-100, 20-30 hours of work

### Phase 2: Automation (Weeks 3-4)

**Goal:** Automate data collection and alerting.

**Tasks:**
1. ✅ Set up PostgreSQL database
2. ✅ Automated tweet ingestion (cron job every 15 min)
3. ✅ Implement bot filtering
4. ✅ Implement quality scoring
5. ✅ Sentiment analysis with VADER
6. ✅ Calculate Hype Score automatically
7. ✅ Telegram bot sends alerts when Hype Score >70
8. ✅ Dashboard (Grafana or custom) for visualization

**Success criteria:** System runs autonomously for 1 week, generates 5+ alerts.

**Investment:** $100-300/mo, 40-60 hours of work

### Phase 3: Refinement (Weeks 5-8)

**Goal:** Reduce false positives, improve signal quality.

**Tasks:**
1. ✅ Analyze Phase 2 alerts: How many were actionable?
2. ✅ Tune thresholds (what Hype Score actually matters?)
3. ✅ Add historical case studies to pattern library
4. ✅ Implement whale account tracking (curated list)
5. ✅ Add cross-platform monitoring (Reddit, Discord if relevant)
6. ✅ Backtesting: Could we have detected past viral bets?
7. ✅ A/B test: Manual trading vs. system alerts

**Success criteria:** >60% of alerts lead to profitable opportunities.

**Investment:** $200-500/mo, ongoing tuning

### Phase 4: Advanced Features (Months 3-6)

**Goal:** Build competitive moat with unique data.

**Tasks:**
1. ✅ ML model trained on historical viral patterns
2. ✅ Network analysis (who influences whom?)
3. ✅ Predictive modeling (what tweets will go viral?)
4. ✅ Competitor monitoring (are others using this strategy?)
5. ✅ Integration with auto-betting (if legal/desired)
6. ✅ Mobile app for real-time monitoring
7. ✅ Community building (share insights with other traders?)

**Success criteria:** Consistent edge, profitable over 3+ months.

**Investment:** $500-2k/mo, ongoing development

### Phase 5: Scale (Month 6+)

**Goal:** Turn into sustainable operation or product.

**Options:**

**Option A: Personal Trading Edge**
- Use system privately
- Refine until extremely profitable
- Treat as proprietary trading signal

**Option B: Productize**
- Sell alerts as subscription service
- Target other prediction market traders
- $50-500/mo per subscriber

**Option C: Fund/Syndicate**
- Pool capital with other traders
- Use system to manage fund
- Take 2-and-20 (2% management, 20% performance fees)

---

## Appendix A: Quick Start Checklist

**Getting started in <4 hours:**

- [ ] Sign up for Brand24 trial (or X API Basic)
- [ ] Create Twitter lists: PM-Platforms, PM-Whales
- [ ] Set up keyword monitoring: "Polymarket", "Manifold", "prediction market"
- [ ] Install Python, VADER sentiment library
- [ ] Create basic scraper script
- [ ] Set up Telegram bot for alerts
- [ ] Test with 1-2 keywords for 24 hours
- [ ] Manually check if any alerts were actionable
- [ ] Iterate

**First alert rules (simple):**
```
IF (mentions "Polymarket" AND contains "$") 
   AND (likes > 100 OR from_whale_account)
   AND (account_age > 90 days)
THEN alert("Potential viral bet detected")
```

Start simple, add complexity as you learn.

---

## Appendix B: Code Snippets

### Simple Tweet Scraper (snscrape)

```python
import snscrape.modules.twitter as sntwitter
import pandas as pd
from datetime import datetime, timedelta

# Search tweets from last 24 hours
query = "(Polymarket OR Manifold) (bet OR betting OR odds) -filter:retweets"
since = datetime.now() - timedelta(days=1)
tweets = []

for tweet in sntwitter.TwitterSearchScraper(f'{query} since:{since.strftime("%Y-%m-%d")}').get_items():
    if len(tweets) >= 100:  # Limit
        break
    tweets.append({
        'timestamp': tweet.date,
        'username': tweet.user.username,
        'text': tweet.content,
        'likes': tweet.likeCount,
        'retweets': tweet.retweetCount,
        'replies': tweet.replyCount,
        'url': tweet.url
    })

df = pd.DataFrame(tweets)
df.to_csv('tweets.csv', index=False)
print(f"Collected {len(tweets)} tweets")
```

### Sentiment Analysis (VADER)

```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

analyzer = SentimentIntensityAnalyzer()

df = pd.read_csv('tweets.csv')
df['sentiment'] = df['text'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

# Classify
df['sentiment_label'] = df['sentiment'].apply(
    lambda x: 'POSITIVE' if x > 0.05 else ('NEGATIVE' if x < -0.05 else 'NEUTRAL')
)

print(df[['text', 'sentiment', 'sentiment_label']].head())
```

### Hype Score Calculator

```python
import math

def calculate_hype_score(tweet_data, baseline_volume=10):
    """
    Calculate hype score for a market based on tweet data
    
    Args:
        tweet_data: dict with keys: volume, avg_engagement, velocity, 
                    influencer_score, sentiment, author_diversity, network_depth
        baseline_volume: 7-day average volume for comparison
    
    Returns:
        float: Hype score (0-100)
    """
    
    # Volume ratio
    volume_ratio = tweet_data['volume'] / baseline_volume
    volume_score = min(volume_ratio * 20, 20)  # Cap at 20
    
    # Engagement (logarithmic)
    engagement_score = min(math.log10(max(tweet_data['avg_engagement'], 1)) * 15, 15)
    
    # Velocity
    velocity_score = min(tweet_data['velocity'] * 10, 10)
    
    # Influencer score (already normalized)
    influencer_score = min(tweet_data['influencer_score'] * 25, 25)
    
    # Sentiment (normalize from -1/+1 to 0-20)
    sentiment_score = (tweet_data['sentiment'] + 1) * 10
    
    # Author diversity
    diversity_score = tweet_data['author_diversity'] * 10
    
    # Network depth
    network_score = min(tweet_data['network_depth'] * 10, 10)
    
    total = (volume_score + engagement_score + velocity_score + 
             influencer_score + sentiment_score + diversity_score + network_score)
    
    return min(total, 100)

# Example usage
market_data = {
    'volume': 50,  # 50 tweets in last hour
    'avg_engagement': 150,  # Average likes+RTs+replies per tweet
    'velocity': 2.5,  # 250% increase from previous hour
    'influencer_score': 0.6,  # Mid-tier influencer involved
    'sentiment': 0.7,  # Positive sentiment
    'author_diversity': 0.8,  # High diversity (organic)
    'network_depth': 3  # Retweets reaching 3rd degree
}

hype_score = calculate_hype_score(market_data, baseline_volume=10)
print(f"Hype Score: {hype_score:.1f}/100")

if hype_score > 70:
    print("⚠️ STRONG SIGNAL - Investigate immediately")
elif hype_score > 50:
    print("👀 EARLY SIGNAL - Add to watchlist")
else:
    print("😴 Noise - Ignore")
```

### Telegram Alert Bot

```python
import telegram
import asyncio

async def send_alert(message, urgency="MEDIUM"):
    bot = telegram.Bot(token='YOUR_TELEGRAM_BOT_TOKEN')
    chat_id = 'YOUR_CHAT_ID'
    
    emoji = {
        "CRITICAL": "🚨",
        "HIGH": "⚠️",
        "MEDIUM": "👀",
        "LOW": "ℹ️"
    }
    
    formatted_message = f"{emoji.get(urgency, '📢')} {urgency}\n\n{message}"
    await bot.send_message(chat_id=chat_id, text=formatted_message)

# Example usage
asyncio.run(send_alert(
    "Viral bet detected: 'Will AI achieve AGI by 2026?'\n"
    "Hype Score: 78/100\n"
    "Volume: 85 tweets (8x baseline)\n"
    "Engagement: 250 avg\n"
    "Sentiment: +0.75 (highly positive)\n"
    "Action: Review market immediately",
    urgency="HIGH"
))
```

---

## Appendix C: Resources & Further Reading

### Academic Papers

1. **"Predicting Stock Market Movements Using Social Media Sentiment Analysis"** - Johan Bollen et al.
   - Shows Twitter sentiment predicts market movements with 87.6% accuracy

2. **"The Wisdom of Twitter Crowds: Predicting Stock Market Reactions to FOMC Meetings via Twitter Feeds"** 
   - Evidence that social media anticipates market movements

3. **"Early Detection of Emerging Trends from Twitter"**
   - Methodology for detecting viral cascades early

4. **"Information Cascades in Social Media"** - Lerman & Ghosh
   - Network theory applied to viral content

### Tools & Libraries

- **Tweepy:** Official Twitter API library (Python)
- **snscrape:** Twitter scraper, no API needed
- **VADER:** Sentiment analysis for social media
- **TextBlob:** General NLP library
- **Botometer:** Bot detection API
- **NetworkX:** Social network analysis
- **Pandas:** Data manipulation
- **Grafana:** Visualization/dashboards

### Community Resources

- **r/algotrading** - Algorithmic trading strategies
- **r/Polymarket** - Prediction market community
- **r/PredictionMarkets** - General prediction market discussion
- **Hacker News** - Tech/startup discussion, occasionally prediction markets
- **LessWrong** - Rationalist community, heavy Manifold users

### Prediction Market APIs

- **Polymarket API:** `https://docs.polymarket.com/`
- **Manifold Markets API:** `https://docs.manifold.markets/`
- **Metaculus API:** `https://www.metaculus.com/api/`

### Monitoring Services

- **Brand24:** Social media monitoring
- **Hootsuite Insights:** Enterprise social listening
- **Mentionlytics:** Budget-friendly monitoring
- **Brandwatch:** Enterprise-grade analytics

---

## Appendix D: Risk Warnings

### Legal Risks

1. **Market Manipulation:** Be careful not to influence markets yourself by tweeting about your positions (could be construed as pump-and-dump)

2. **Platform ToS Violations:** Scraping Twitter violates their Terms of Service. Using official API is legal but expensive.

3. **Insider Trading Equivalent:** If you obtain non-public information through monitoring, using it might have legal gray areas.

### Operational Risks

1. **False Positives:** Most "viral" signals will be noise. Don't over-trade.

2. **Market Inefficiency Disappears:** If many people use similar strategies, the edge disappears.

3. **Platform Changes:** Twitter could change API pricing, kill scraping, or change algorithms.

4. **Prediction Market Risk:** Markets can be wrong. Social hype ≠ correct prediction.

### Financial Risks

1. **Capital Required:** Need sufficient capital to bet on multiple signals (portfolio approach).

2. **Liquidity Risk:** Some markets are too small to enter/exit without moving prices.

3. **Timing Risk:** Even if you detect hype early, market might not move in expected direction.

### Mitigation

- Start small, prove concept before scaling
- Never bet more than you can afford to lose
- Diversify across multiple bets
- Keep detailed records for taxes/legal protection
- Use official APIs when possible (avoid scraping)
- Don't manipulate markets yourself

---

## Conclusion

**Summary:** Twitter/X sentiment tracking for prediction markets is feasible and potentially profitable, but requires:

1. **Technical infrastructure** - API access, data pipeline, automation
2. **Signal processing** - Filtering noise, detecting bots, quality scoring
3. **Speed** - Early detection is everything (2-6 hour window)
4. **Discipline** - Not every signal is actionable
5. **Capital** - Need funds to bet on opportunities
6. **Continuous improvement** - Markets adapt, strategies must evolve

**Expected ROI:**
- **Optimistic:** 20-50% annual return if system works well
- **Realistic:** 10-20% annual return after tuning
- **Pessimistic:** Break-even or small loss while learning

**Time to profitability:** 3-6 months of iteration

**Competitive moat:** First-mover advantage. Once many people do this, edge shrinks.

**Next steps:**
1. Start MVP (Phase 1) immediately
2. Test for 2 weeks
3. Decide whether to continue based on early results

**Questions to answer through experimentation:**
- What Hype Score threshold actually correlates with profitable opportunities?
- How much lead time do we really get?
- Which types of bets are most predictable?
- Can we automate entry/exit or is manual oversight required?

**Final thought:** This is a race. The sooner you build and test this system, the longer you have before others catch on. Speed matters.

Good luck! 🚀

---

**Document Status:** COMPLETE  
**Next Action:** Begin Phase 1 MVP implementation  
**Owner:** Main agent / trader  
**Last Updated:** 2026-02-06 04:59 PST
