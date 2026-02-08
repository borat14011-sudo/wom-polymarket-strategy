# Data Collection Pipeline for Prediction Market Hype Trading Backtest

**Mission:** Design cost-effective data collection strategy for backtesting prediction market trades correlated with X/Twitter hype.

**Last Updated:** 2026-02-06

---

## Executive Summary

### Key Findings
- **Polymarket:** FREE historical data via public APIs (CLOB + Gamma)
- **Kalshi:** FREE historical data via REST API with candlesticks
- **X/Twitter:** EXPENSIVE - historical data requires paid services or scraping
- **Realistic MVP:** Focus on recent markets (30-90 days) to minimize X data costs
- **Estimated MVP Cost:** $50-200 for Twitter data, $0 for prediction market data

### Critical Constraint
**Historical Twitter data is the bottleneck.** X API charges per request, and full-archive search is expensive. Third-party scrapers work but have reliability/legal gray areas.

---

## 1. Historical Prediction Market Data Sources

### 1.1 Polymarket (Recommended - Best Free Access)

#### **Gamma API** (Market Metadata) - FREE
- **Endpoint:** `https://gamma-api.polymarket.com/`
- **No Authentication Required**
- **Data Available:**
  - Active/closed events
  - Market questions and outcomes
  - Token IDs (required for price queries)
  - Tags, categories, slugs
  - Event metadata (start times, resolution times)

**Example Request:**
```bash
# Get all active events
curl "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=100"

# Get specific market by slug
curl "https://gamma-api.polymarket.com/markets?slug=will-bitcoin-reach-100k-by-2025"
```

#### **CLOB API** (Order Book & Prices) - FREE
- **Endpoint:** `https://clob.polymarket.com/`
- **No Authentication for Read-Only**
- **Data Available:**
  - Current price by token ID
  - Full order book (bids/asks with depth)
  - Last trade price
  - Market trades (requires auth)
  - Simplified markets overview

**Example Requests:**
```bash
# Get current price
curl "https://clob.polymarket.com/price?token_id=YOUR_TOKEN_ID&side=buy"

# Get order book snapshot
curl "https://clob.polymarket.com/book?token_id=YOUR_TOKEN_ID"

# Get simplified markets (no auth)
curl "https://clob.polymarket.com/markets"
```

#### **Historical Data Strategy for Polymarket:**
1. **Method 1: Periodic Snapshots (Recommended for MVP)**
   - Poll CLOB API every 5-15 minutes for active markets
   - Store: timestamp, price, bid/ask spread, volume
   - Cost: FREE (rate limits apply - ~100 req/min)
   - Storage: ~10KB per market per snapshot → 2MB/day/market

2. **Method 2: Trade History Scraping**
   - Requires authentication (create API key)
   - Use `py-clob-client` Python library
   - Poll `/trades` endpoint for each market
   - Cost: FREE but requires wallet setup

3. **Method 3: On-Chain Data**
   - Polymarket runs on Polygon blockchain
   - Use The Graph subgraph or blockchain explorers
   - More complex but gets ALL historical trades
   - Cost: FREE but requires GraphQL/blockchain knowledge

**Python Client Setup:**
```python
from py_clob_client.client import ClobClient

# Read-only client (no auth)
client = ClobClient("https://clob.polymarket.com")

# Get markets
markets = client.get_simplified_markets()

# Get price for token
price = client.get_price(token_id="TOKEN_ID", side="BUY")

# Get order book
book = client.get_order_book(token_id="TOKEN_ID")
```

### 1.2 Kalshi (Alternative/Complement)

#### **REST API** - FREE (with rate limits)
- **Endpoint:** `https://api.kalshi.com/`
- **Authentication:** API key required (free account)
- **Data Available:**
  - Market candlesticks (OHLC price data)
  - Trade history with timestamps
  - Order book snapshots
  - Market metadata, events, series

**Key Endpoints:**
```bash
# Get market candlesticks (historical OHLC)
GET /markets/{ticker}/candlesticks
# Parameters: period_interval (1m, 5m, 1h, 1d), start_ts, end_ts

# Get trades for a market
GET /markets/{ticker}/trades
# Returns: trade_id, price, volume, timestamp, taker_side

# Get all markets
GET /markets
```

**Data Structure:**
```json
{
  "candlesticks": [
    {
      "end_period_ts": 1234567890,
      "price": {
        "open": 45, "high": 52, "low": 43, "close": 50,
        "open_dollars": "0.45", "close_dollars": "0.50"
      },
      "volume": 1500,
      "open_interest": 5000
    }
  ]
}
```

**Advantages:**
- Native candlestick support (saves processing)
- Clean API with good documentation
- Reliable uptime

**Disadvantages:**
- Lower volume than Polymarket
- Fewer crypto/meme markets
- More regulated (US-focused markets)

---

## 2. Historical X/Twitter Data Sources

### ⚠️ THE HARD PART - Twitter Historical Data is Expensive/Difficult

### 2.1 Official X API (Expensive but Legal)

#### **Full-Archive Search** - PAY PER USE
- **Endpoint:** `https://api.x.com/2/tweets/search/all`
- **Cost Model:** ~$0.10-0.50 per 1000 tweets (pricing varies)
- **Authentication:** Bearer token, paid account
- **Data Available:**
  - ALL public tweets back to 2006
  - Tweet text, engagement metrics (likes, retweets, replies)
  - User info, media, hashtags, mentions
  - Timestamp with millisecond precision

**Query Capabilities:**
```bash
# Search tweets about a topic in date range
curl "https://api.x.com/2/tweets/search/all?query=polymarket%20lang:en&start_time=2024-01-01T00:00:00Z&end_time=2024-01-31T23:59:59Z" \
  -H "Authorization: Bearer $TOKEN"

# Search by user
query=from:polymarket OR from:kalshi_markets

# Search with engagement filters
query=(polymarket OR prediction market) min_faves:10
```

**Cost Estimation:**
- Backtesting 10 markets over 30 days
- Assume 1,000 relevant tweets per market per day
- Total: 10 × 30 × 1,000 = 300,000 tweets
- **Cost: $30-150** (depends on pricing tier)

### 2.2 Third-Party Scraping Services

#### **Apify Twitter Scraper** (Paid, Reliable)
- **URL:** `https://apify.com/scrapers/twitter`
- **Cost:** $0.25 per 1,000 tweets (competitive)
- **Pros:**
  - No API rate limits
  - Can get engagement data
  - Reliable infrastructure
  - Export to JSON/CSV
  - Scheduling and automation
- **Cons:**
  - Against Twitter ToS (gray area)
  - May break if Twitter changes UI
  - Not real-time for historical data

**Cost Estimation:**
- 300,000 tweets = $75
- **Budget-friendly for MVP**

#### **snscrape** (Free, Open-Source)
- **GitHub:** `https://github.com/JustAnotherArchivist/snscrape`
- **Cost:** FREE
- **Pros:**
  - Completely free
  - Python CLI and library
  - No API key needed
  - Supports hashtags, users, searches
- **Cons:**
  - Fragile (Twitter blocks it periodically)
  - Rate limiting issues
  - May miss tweets
  - Against Twitter ToS
  - Limited reliability for large-scale historical collection

**Usage Example:**
```bash
# Get tweets from user
snscrape --jsonl --max-results 1000 twitter-user polymarket > tweets.jsonl

# Get tweets by hashtag in date range
snscrape --jsonl twitter-search "polymarket since:2024-01-01 until:2024-01-31" > tweets.jsonl

# Get tweets with keyword
snscrape --jsonl --max-results 10000 twitter-search "prediction market" > tweets.jsonl
```

**Reliability Strategy:**
- Use snscrape for MVP/testing
- Fall back to paid Apify if snscrape breaks
- Keep scraped data as backups

### 2.3 Alternative: Focus on Recent Data Only

**Strategy:** Instead of expensive full historical data, collect forward-looking:
1. Start data collection NOW for live markets
2. Build 30-90 day dataset over time
3. Use for live testing and incremental backtesting
4. Much cheaper (can use free Twitter API limits for recent data)

**Recent Search API** (Cheaper):
- Last 7 days of tweets
- ~$100/month for moderate usage
- Good for real-time trading, not backtesting

---

## 3. Data Alignment Strategy: Matching Hype → Market Movements

### 3.1 Temporal Synchronization

**Core Challenge:** Align Twitter signal timing with market price changes

#### **Time Granularity Options:**

| Granularity | Use Case | Storage | Complexity |
|-------------|----------|---------|------------|
| **1 minute** | High-frequency trading signals | High (~100MB/market/month) | Complex |
| **5 minutes** | Short-term momentum plays | Medium (~20MB/market/month) | Moderate |
| **15 minutes** | Swing trading signals | Low (~7MB/market/month) | **Recommended** |
| **1 hour** | Trend analysis | Minimal (~2MB/market/month) | Simple but lossy |

**Recommendation: 15-minute buckets** - balances signal quality with data volume

#### **Alignment Process:**

```python
# Pseudocode for time alignment

def align_twitter_to_market(market_snapshots, tweets):
    """
    Align Twitter data to market price snapshots
    """
    # 1. Bucket tweets into 15-min windows
    tweet_buckets = bucket_by_time(tweets, interval_minutes=15)
    
    # 2. Calculate Twitter metrics per bucket
    for bucket in tweet_buckets:
        bucket.metrics = {
            'tweet_count': len(bucket.tweets),
            'total_likes': sum(t.likes for t in bucket.tweets),
            'total_retweets': sum(t.retweets for t in bucket.tweets),
            'total_replies': sum(t.replies for t in bucket.tweets),
            'unique_users': len(set(t.user_id for t in bucket.tweets)),
            'avg_engagement': (sum(t.likes + t.retweets) / len(bucket.tweets)),
            'sentiment_score': calculate_sentiment(bucket.tweets)  # Optional
        }
    
    # 3. Join with market data on timestamp
    aligned_data = []
    for snapshot in market_snapshots:
        timestamp = snapshot.timestamp
        bucket = find_bucket_for_time(tweet_buckets, timestamp)
        
        aligned_data.append({
            'timestamp': timestamp,
            'market_price': snapshot.price,
            'price_change_15m': snapshot.price - prev_snapshot.price,
            'volume': snapshot.volume,
            'spread': snapshot.ask - snapshot.bid,
            # Twitter features
            'tweet_count': bucket.metrics.tweet_count,
            'engagement_score': bucket.metrics.avg_engagement,
            'hype_velocity': bucket.metrics.tweet_count / prev_bucket.metrics.tweet_count,
            'unique_users': bucket.metrics.unique_users,
        })
    
    return aligned_data
```

### 3.2 Lead/Lag Analysis

**Key Question:** Does Twitter hype LEAD or LAG market movements?

**Test multiple time offsets:**
```python
# Test if Twitter signal at time T predicts price at T+offset
offsets_to_test = [
    -30,  # Twitter lags market by 30 min (not useful)
    -15,  # Twitter lags by 15 min
    0,    # Synchronous
    +15,  # Twitter leads by 15 min (useful!)
    +30,  # Twitter leads by 30 min
    +60,  # Twitter leads by 1 hour
]

for offset in offsets_to_test:
    correlation = correlate(twitter_signal[t], price_change[t + offset])
    print(f"Offset {offset}min: correlation = {correlation}")
```

**Expected Pattern:**
- If Twitter hype LEADS markets → positive correlation at positive offsets
- If it's just noise → low correlation everywhere
- If it LAGS → correlation at negative offsets (less useful)

### 3.3 Market-Specific Keyword Tracking

**Problem:** Generic "prediction market" tweets don't map to specific markets

**Solution:** Extract market-specific keywords from each market question

```python
def extract_market_keywords(market_question):
    """
    Extract keywords to search Twitter for this specific market
    
    Example:
    Market: "Will Trump win 2024 election?"
    Keywords: ["Trump", "2024 election", "Trump 2024"]
    """
    # Remove common words
    stopwords = ["will", "is", "the", "a", "by"]
    
    # Extract entities (people, places, events)
    entities = extract_entities(market_question)  # Use NER
    
    # Generate search queries
    queries = []
    queries.append(market_question.lower())  # Exact phrase
    queries.extend(entities)  # Individual entities
    queries.append(" ".join(entities[:2]))  # Top 2 entities combined
    
    return queries

# Example outputs:
# "Will Bitcoin reach $100k?" → ["bitcoin", "100k", "btc", "bitcoin 100k"]
# "Trump win 2024?" → ["Trump", "2024 election", "Trump win", "Trump 2024"]
```

**Twitter Query Construction:**
```python
def build_twitter_query(market):
    keywords = extract_market_keywords(market.question)
    
    # Build OR query
    query = " OR ".join(f'"{kw}"' for kw in keywords)
    
    # Add filters
    query += " lang:en"  # English only
    query += " -is:retweet"  # Exclude retweets (optional)
    
    # Add date range
    query += f" since:{market.start_date} until:{market.end_date}"
    
    return query

# Example output:
# "(Bitcoin OR $100k OR BTC) lang:en -is:retweet since:2024-01-01 until:2024-12-31"
```

---

## 4. Sample Dataset Specification

### 4.1 Database Schema

#### **markets** table
```sql
CREATE TABLE markets (
    market_id VARCHAR(100) PRIMARY KEY,
    platform VARCHAR(20),  -- 'polymarket' or 'kalshi'
    question TEXT,
    slug VARCHAR(200),
    token_id_yes VARCHAR(100),
    token_id_no VARCHAR(100),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    resolution_time TIMESTAMP,
    resolved_outcome VARCHAR(10),  -- 'yes', 'no', 'null'
    category VARCHAR(50),
    tags TEXT[],  -- Array of tags
    twitter_keywords TEXT[],  -- Extracted keywords for this market
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### **market_snapshots** table (time series)
```sql
CREATE TABLE market_snapshots (
    id BIGSERIAL PRIMARY KEY,
    market_id VARCHAR(100) REFERENCES markets(market_id),
    timestamp TIMESTAMP,
    
    -- Price data
    price_yes DECIMAL(10, 6),  -- 0.00 to 1.00
    price_no DECIMAL(10, 6),
    midpoint DECIMAL(10, 6),   -- (yes + no) / 2
    spread DECIMAL(10, 6),     -- ask - bid
    
    -- Order book depth (optional, storage-heavy)
    bid_depth_yes JSON,  -- [{"price": 0.45, "size": 100}, ...]
    ask_depth_yes JSON,
    bid_depth_no JSON,
    ask_depth_no JSON,
    
    -- Volume
    volume_24h DECIMAL(20, 2),
    open_interest DECIMAL(20, 2),
    
    -- Metadata
    is_active BOOLEAN,
    
    UNIQUE(market_id, timestamp)
);

-- Index for fast time-series queries
CREATE INDEX idx_snapshots_market_time ON market_snapshots(market_id, timestamp);
```

#### **tweets** table
```sql
CREATE TABLE tweets (
    tweet_id VARCHAR(50) PRIMARY KEY,
    market_id VARCHAR(100) REFERENCES markets(market_id),
    timestamp TIMESTAMP,
    
    -- Tweet content
    text TEXT,
    author_id VARCHAR(50),
    author_username VARCHAR(50),
    
    -- Engagement metrics
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    quotes INTEGER DEFAULT 0,
    impressions BIGINT,  -- Often not available
    
    -- Derived metrics
    engagement_score INTEGER GENERATED ALWAYS AS (likes + retweets * 2 + replies) STORED,
    
    -- Metadata
    is_retweet BOOLEAN DEFAULT FALSE,
    language VARCHAR(10),
    hashtags TEXT[],
    mentions TEXT[],
    urls TEXT[],
    
    -- Sentiment (optional, can add later)
    sentiment_score DECIMAL(5, 3),  -- -1 to +1
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tweets_market_time ON tweets(market_id, timestamp);
CREATE INDEX idx_tweets_engagement ON tweets(engagement_score DESC);
```

#### **twitter_metrics_15m** table (aggregated)
```sql
CREATE TABLE twitter_metrics_15m (
    id BIGSERIAL PRIMARY KEY,
    market_id VARCHAR(100) REFERENCES markets(market_id),
    bucket_start TIMESTAMP,  -- Start of 15-min window
    bucket_end TIMESTAMP,
    
    -- Volume metrics
    tweet_count INTEGER,
    unique_users INTEGER,
    total_tweets_cumulative INTEGER,  -- Running total
    
    -- Engagement metrics
    total_likes INTEGER,
    total_retweets INTEGER,
    total_replies INTEGER,
    avg_engagement DECIMAL(10, 2),
    max_engagement INTEGER,  -- Most viral tweet in window
    
    -- Velocity metrics (rate of change)
    tweet_velocity DECIMAL(10, 2),  -- tweets per minute
    engagement_velocity DECIMAL(10, 2),  -- engagement per minute
    
    -- User metrics
    verified_users INTEGER,  -- If tracking verification
    avg_follower_count DECIMAL(12, 2),
    
    -- Sentiment (optional)
    avg_sentiment DECIMAL(5, 3),
    sentiment_std DECIMAL(5, 3),
    
    UNIQUE(market_id, bucket_start)
);

CREATE INDEX idx_twitter_metrics_market_time ON twitter_metrics_15m(market_id, bucket_start);
```

#### **aligned_features** table (final ML-ready dataset)
```sql
CREATE TABLE aligned_features (
    id BIGSERIAL PRIMARY KEY,
    market_id VARCHAR(100) REFERENCES markets(market_id),
    timestamp TIMESTAMP,
    
    -- Target variables (what we're predicting)
    price_current DECIMAL(10, 6),
    price_change_15m DECIMAL(10, 6),  -- Price 15 min later
    price_change_1h DECIMAL(10, 6),
    price_change_direction VARCHAR(10),  -- 'up', 'down', 'stable'
    
    -- Market features (current)
    spread DECIMAL(10, 6),
    volume_24h DECIMAL(20, 2),
    price_momentum_1h DECIMAL(10, 6),  -- Price change over last hour
    
    -- Twitter features (lagged/leading depending on offset)
    tweet_count_15m INTEGER,
    engagement_score_15m INTEGER,
    tweet_velocity DECIMAL(10, 2),
    unique_users_15m INTEGER,
    hype_ratio DECIMAL(10, 3),  -- Current engagement / avg engagement
    
    -- Derived features
    is_viral_spike BOOLEAN,  -- engagement_score > 3 * avg
    user_concentration DECIMAL(5, 3),  -- tweets / unique_users (1 = everyone tweets once)
    
    -- Metadata
    time_to_expiry_hours INTEGER,
    hour_of_day INTEGER,
    day_of_week INTEGER,
    
    UNIQUE(market_id, timestamp)
);

CREATE INDEX idx_aligned_market_time ON aligned_features(market_id, timestamp);
```

### 4.2 Data Volume Estimates

**Per market, 30-day backtest:**

| Data Type | Frequency | Records | Size per Record | Total Size |
|-----------|-----------|---------|-----------------|------------|
| Market snapshots | 15 min | 2,880 | 500 bytes | **1.4 MB** |
| Tweets | Variable | ~1,000-10,000 | 2 KB | **2-20 MB** |
| Twitter 15m metrics | 15 min | 2,880 | 300 bytes | **864 KB** |
| Aligned features | 15 min | 2,880 | 600 bytes | **1.7 MB** |
| **Total per market** | | | | **~6-25 MB** |

**For 10 markets over 30 days: ~60-250 MB total**

**Storage recommendations:**
- PostgreSQL for relational data and time-series
- TimescaleDB extension for efficient time-series queries
- Parquet files for ML training (export from DB)

### 4.3 Feature Engineering Pipeline

```python
def engineer_features(market_snapshots, twitter_metrics):
    """
    Create ML-ready features from raw data
    """
    features = []
    
    for i, snapshot in enumerate(market_snapshots):
        # Skip first hour (need historical context)
        if i < 4:  # 4 * 15min = 1 hour
            continue
        
        # Get corresponding Twitter data
        twitter = find_twitter_metrics(snapshot.timestamp)
        
        # Market features
        market_features = {
            'price': snapshot.price_yes,
            'spread': snapshot.spread,
            'volume_24h': snapshot.volume_24h,
            'price_change_15m': snapshot.price_yes - market_snapshots[i-1].price_yes,
            'price_change_1h': snapshot.price_yes - market_snapshots[i-4].price_yes,
            'price_volatility_1h': np.std([s.price_yes for s in market_snapshots[i-4:i]]),
        }
        
        # Twitter features
        twitter_features = {
            'tweet_count': twitter.tweet_count,
            'engagement_total': twitter.total_likes + twitter.total_retweets,
            'engagement_per_tweet': twitter.avg_engagement,
            'unique_users': twitter.unique_users,
            'tweet_velocity': twitter.tweet_velocity,
            
            # Ratio features (compare to historical average)
            'hype_ratio': twitter.tweet_count / avg_tweet_count_7d,
            'engagement_ratio': twitter.avg_engagement / avg_engagement_7d,
            
            # Momentum features
            'tweet_count_change': twitter.tweet_count - prev_twitter.tweet_count,
            'engagement_acceleration': (twitter.avg_engagement - prev_twitter.avg_engagement) / 15,  # per minute
        }
        
        # Target variable (what we want to predict)
        # Look forward 15 minutes
        if i + 1 < len(market_snapshots):
            target = {
                'price_change_next_15m': market_snapshots[i+1].price_yes - snapshot.price_yes,
                'direction': 'up' if market_snapshots[i+1].price_yes > snapshot.price_yes else 'down'
            }
        else:
            target = None
        
        # Combine all features
        features.append({
            **market_features,
            **twitter_features,
            **target,
            'timestamp': snapshot.timestamp,
            'market_id': snapshot.market_id
        })
    
    return pd.DataFrame(features)
```

---

## 5. Free vs Paid Data Sources: Cost Optimization

### 5.1 Cost Breakdown Matrix

| Data Source | Type | Cost | Rate Limits | Data Quality | Reliability |
|-------------|------|------|-------------|--------------|-------------|
| **Polymarket CLOB API** | FREE | $0 | ~100 req/min | Excellent | High |
| **Polymarket Gamma API** | FREE | $0 | Generous | Excellent | High |
| **Kalshi REST API** | FREE | $0 | Moderate | Excellent | High |
| **X API (Recent)** | FREE/Paid | $0-100/mo | 500K tweets/mo (free tier) | Excellent | High |
| **X API (Full Archive)** | Paid | $0.10-0.50 per 1K tweets | Pay-as-you-go | Excellent | High |
| **Apify Twitter Scraper** | Paid | $0.25 per 1K tweets | None | Good | Medium-High |
| **snscrape** | FREE | $0 | Soft limits (IP-based) | Fair | Low-Medium |

### 5.2 Cost-Optimized Strategies

#### **Strategy 1: MVP on $50 Budget** ⭐ RECOMMENDED
**Goal:** Minimal viable backtest dataset

**Data Collection:**
1. **Prediction Markets:** FREE
   - Use Polymarket CLOB API
   - Collect 5-10 high-volume markets
   - 30-day lookback
   - 15-minute snapshots
   - Cost: $0

2. **Twitter Data:** $50 budget
   - Use snscrape first (free)
   - If snscrape fails, use Apify as backup
   - Focus on 5 highest-profile markets (e.g., election, major crypto)
   - Collect ~200,000 tweets total
   - Cost with Apify: $50

**Total Cost: $0-50**

**Limitations:**
- Small dataset (5-10 markets)
- Short time period (30 days)
- May miss some tweets if using snscrape
- Cannot validate edge cases

**Best for:** Proof of concept, initial hypothesis testing

#### **Strategy 2: Professional Backtest on $200 Budget**
**Goal:** Robust dataset for strategy validation

**Data Collection:**
1. **Prediction Markets:** FREE
   - Polymarket + Kalshi
   - 20-30 markets across categories
   - 90-day lookback
   - 15-minute snapshots
   - Cost: $0

2. **Twitter Data:** $200 budget
   - Use X API Full Archive Search (reliable, legal)
   - OR use Apify (cheaper, gray area)
   - Collect ~800,000 tweets (X API) or ~800,000 tweets (Apify)
   - Cost: $150-200

**Total Cost: $150-200**

**Advantages:**
- Larger market sample (20-30 markets)
- Longer history (90 days = more market cycles)
- Higher reliability
- Legal compliance (if using X API)

**Best for:** Serious strategy development, fundraising pitch

#### **Strategy 3: Continuous Collection (Forward-Looking, FREE)**
**Goal:** Build dataset over time instead of buying historical

**Process:**
1. **Start collection NOW**
   - Run data collection scripts 24/7
   - Use free APIs (Polymarket, recent X API)
   - Store in local database

2. **Data accumulation:**
   - Week 1-4: Collect real-time data
   - Week 5-8: Start backtesting on 4+ weeks of data
   - Week 9+: Continuously expand dataset

**Cost: $0** (uses free tiers only)

**Advantages:**
- Zero cost
- High-quality real-time data
- Can start live trading immediately
- Continuous validation

**Disadvantages:**
- Requires 1-3 months to build useful dataset
- Misses past market events
- Need to run infrastructure 24/7

**Best for:** Patient builders, live trading focus

### 5.3 Cost-Saving Tactics

1. **Market Selection:**
   - Focus on HIGH-PROFILE markets (more Twitter discussion)
   - Avoid niche markets (sparse Twitter data)
   - Examples: elections, major crypto events, popular culture

2. **Date Range Optimization:**
   - Focus on FINAL WEEK before market resolution (highest activity)
   - Skip dead periods (low trading, low tweets)

3. **Twitter Query Optimization:**
   - Use NARROW queries to reduce irrelevant tweets
   - Filter by engagement threshold (min_faves:10)
   - Exclude retweets (-is:retweet saves 50-70% of tweets)

4. **Caching Strategy:**
   - NEVER re-scrape the same data
   - Store raw data permanently
   - Reprocess locally if needed

5. **Free Tier Maximization:**
   - X API free tier: 500K tweets/month
   - Use for RECENT data (last 7 days) during live trading
   - Only buy historical data once for backtesting

---

## 6. Data Quality Issues and Limitations

### 6.1 Prediction Market Data Issues

| Issue | Impact | Mitigation |
|-------|--------|------------|
| **Missing trades** | Sparse time series (some 15-min windows = no trades) | Interpolate prices, or skip windows with no data |
| **Low liquidity markets** | Wide spreads, stale prices | Filter markets by min volume threshold ($10K+/day) |
| **Order book depth** | Not always available, storage-heavy | Focus on midpoint price, ignore depth for MVP |
| **Market manipulation** | Wash trading, artificial pumps | Filter outliers, use volume-weighted prices |
| **Resolution delays** | Markets may not resolve on time | Track resolution timestamp separately |

**Quality Checks:**
```python
def validate_market_data(snapshots):
    issues = []
    
    # Check for price anomalies
    for i, snap in enumerate(snapshots[1:]):
        prev = snapshots[i]
        price_change = abs(snap.price - prev.price)
        
        # Flag if price changes >20% in 15 minutes (likely error or manipulation)
        if price_change > 0.20:
            issues.append(f"Large price jump at {snap.timestamp}: {price_change:.2%}")
    
    # Check for stale data (no updates for >1 hour)
    time_gaps = [snapshots[i+1].timestamp - snapshots[i].timestamp 
                 for i in range(len(snapshots)-1)]
    max_gap = max(time_gaps)
    if max_gap > timedelta(hours=1):
        issues.append(f"Stale data: max gap = {max_gap}")
    
    # Check for unrealistic spreads
    avg_spread = np.mean([s.spread for s in snapshots])
    if avg_spread > 0.10:  # 10 cent spread is suspicious
        issues.append(f"High spread: avg = {avg_spread:.3f}")
    
    return issues
```

### 6.2 Twitter Data Issues

| Issue | Impact | Mitigation |
|-------|--------|------------|
| **Bots and spam** | Inflated tweet counts, fake engagement | Filter by account age, follower count |
| **Retweets vs original** | Double-counting, echo chamber | Exclude retweets OR count separately |
| **Language detection** | Non-English tweets may be irrelevant | Filter by lang:en in queries |
| **Deleted tweets** | Historical data may be incomplete | Accept as limitation (can't fix) |
| **Sarcasm/irony** | Sentiment analysis fails | Use simple volume metrics, avoid sentiment for MVP |
| **Keyword ambiguity** | "Trump" could mean many things | Use specific phrases, combine with market keywords |
| **Engagement lag** | Likes/RTs accumulate over time | Snapshot engagement at consistent intervals |

**Quality Checks:**
```python
def validate_twitter_data(tweets):
    issues = []
    
    # Check for bot-like accounts
    author_tweet_counts = Counter(t.author_id for t in tweets)
    for author, count in author_tweet_counts.items():
        if count > 50:  # More than 50 tweets about same market = likely bot
            issues.append(f"Potential bot: {author} posted {count} times")
    
    # Check for spam patterns
    exact_duplicates = len(tweets) - len(set(t.text for t in tweets))
    if exact_duplicates > len(tweets) * 0.1:  # >10% duplicates
        issues.append(f"High duplicate rate: {exact_duplicates / len(tweets):.1%}")
    
    # Check language distribution
    lang_dist = Counter(t.language for t in tweets)
    if lang_dist.get('en', 0) / len(tweets) < 0.8:  # <80% English
        issues.append(f"Low English rate: {lang_dist.get('en', 0) / len(tweets):.1%}")
    
    return issues
```

### 6.3 Alignment Issues

| Issue | Impact | Mitigation |
|-------|--------|------------|
| **Timezone mismatches** | Incorrect time alignment | Convert all timestamps to UTC |
| **Timestamp precision** | Twitter = seconds, markets = milliseconds | Round to 15-min buckets |
| **Missing data windows** | Some 15-min buckets may have 0 tweets | Impute with 0s or skip |
| **Keyword precision** | Generic keywords → unrelated tweets | Manually refine keywords per market |
| **Lagged engagement** | Tweets get likes over hours/days | Snapshot at consistent time offsets |

### 6.4 Known Limitations

**Fundamental Limits:**
1. **Survivorship Bias:** Can only study markets that existed. Misses "markets that should have been created"
2. **Look-Ahead Bias:** Must be careful not to use future data when backtesting
3. **Overfitting Risk:** Small dataset (10-30 markets) = easy to overfit
4. **Non-Stationarity:** Market dynamics change over time (what worked in 2024 may not work in 2026)
5. **Missing Context:** Tweets lack context (images, links, threads) that humans see

**Statistical Limits:**
- Small sample size → low confidence in results
- High variance in social media data
- Difficult to isolate causal effects (correlation ≠ causation)

**Practical Limits:**
- Twitter data is expensive for large-scale historical collection
- Scrapers break frequently
- Data storage costs grow quickly
- Real-time collection requires 24/7 infrastructure

---

## 7. Minimum Viable Dataset for Initial Backtest

### 7.1 MVP Specification

**Goal:** Smallest dataset to test if Twitter hype predicts market movements

#### **Scope:**
- **Markets:** 5-10 high-profile markets
- **Time Period:** 30 days
- **Granularity:** 15-minute buckets
- **Twitter Data:** 50,000-200,000 tweets total

#### **Market Selection Criteria:**
1. **High volume:** >$100K traded/day
2. **High Twitter activity:** >100 relevant tweets/day
3. **Clear resolution:** Yes/No markets (not multi-outcome)
4. **Recent events:** Active in last 90 days
5. **Diverse categories:** Mix of politics, crypto, sports, entertainment

**Example Markets:**
1. Trump 2024 Election Winner (Politics)
2. Bitcoin >$100K by EOY (Crypto)
3. Lakers Win NBA Finals (Sports)
4. Fed Rate Cut in Q1 (Economics)
5. New GTA Game Release Date (Entertainment)

### 7.2 Data Collection Workflow (MVP)

```mermaid
graph TD
    A[Select 5-10 Markets] --> B[Extract Keywords]
    B --> C[Scrape Market Data]
    B --> D[Scrape Twitter Data]
    C --> E[Store in Database]
    D --> E
    E --> F[Align Data 15min buckets]
    F --> G[Engineer Features]
    G --> H[Export to Parquet]
    H --> I[Run Backtest]
```

**Implementation:**

```python
# 1. Market selection
markets = [
    {
        'id': 'trump-2024',
        'platform': 'polymarket',
        'question': 'Trump wins 2024 election?',
        'keywords': ['Trump', '2024 election', 'Trump win'],
        'start_date': '2024-01-01',
        'end_date': '2024-11-05'
    },
    # ... 4-9 more markets
]

# 2. Collect market data
for market in markets:
    snapshots = collect_market_snapshots(
        market_id=market['id'],
        start_date=market['start_date'],
        end_date=market['end_date'],
        interval_minutes=15
    )
    save_to_db(snapshots, table='market_snapshots')

# 3. Collect Twitter data
for market in markets:
    query = build_twitter_query(market['keywords'], market['start_date'], market['end_date'])
    tweets = scrape_tweets(query, max_tweets=20000)  # Cap per market
    save_to_db(tweets, table='tweets')

# 4. Align and aggregate
aligned_data = align_data(markets)
save_to_db(aligned_data, table='aligned_features')

# 5. Export for ML
df = load_from_db('aligned_features')
df.to_parquet('backtest_data.parquet')
```

### 7.3 Expected Results from MVP

**Success Criteria:**
1. **Data completeness:** >80% of 15-min windows have both market and Twitter data
2. **Correlation detected:** Twitter hype correlates with price changes (|r| > 0.1)
3. **Signal timing:** Twitter leads market by 15-60 minutes (positive correlation at +15min offset)
4. **Strategy viability:** Simple rule (e.g., "buy when tweets spike 3x") shows >55% win rate

**Failure Criteria:**
1. Correlation near zero (|r| < 0.05)
2. Twitter lags market (signal is reactive, not predictive)
3. High noise (Twitter spikes happen randomly)
4. No timing advantage (can't act fast enough)

### 7.4 Timeline for MVP (Realistic)

| Phase | Duration | Effort |
|-------|----------|--------|
| **1. Market Selection** | 2-4 hours | Manual research |
| **2. Setup Infrastructure** | 1-2 days | Database, scripts, API keys |
| **3. Collect Market Data** | 1 day | Run API scripts |
| **4. Collect Twitter Data** | 2-5 days | Scraping (depends on method) |
| **5. Data Cleaning** | 1-2 days | Quality checks, deduplication |
| **6. Alignment & Features** | 1 day | SQL queries, feature engineering |
| **7. Initial Analysis** | 1-2 days | Correlation tests, visualization |
| **Total:** | **1-2 weeks** | **~40-80 hours of work** |

---

## 8. Recommended Implementation Roadmap

### Phase 1: MVP (Week 1-2) - $0-50 Budget

**Goal:** Prove the hypothesis: "Twitter hype predicts market movements"

**Tasks:**
1. Set up PostgreSQL database
2. Implement Polymarket CLOB data collector (Python)
3. Collect 5 markets, 30 days, 15-min intervals
4. Scrape Twitter with snscrape (free)
5. Align data in 15-min buckets
6. Run correlation analysis
7. Visualize results (charts)

**Deliverable:** Report showing correlation between Twitter metrics and price changes

### Phase 2: Strategy Development (Week 3-4) - $50-200 Budget

**Goal:** Develop and backtest trading strategy

**Tasks:**
1. Expand to 10-20 markets
2. Upgrade to Apify or X API for reliable Twitter data ($50-200)
3. Engineer advanced features (velocity, momentum, ratios)
4. Train simple ML model (logistic regression, XGBoost)
5. Backtest with realistic execution assumptions
6. Calculate Sharpe ratio, win rate, max drawdown

**Deliverable:** Backtested strategy with performance metrics

### Phase 3: Live Testing (Week 5-12) - $0 Budget (Paper Trading)

**Goal:** Validate strategy in real-time without risking capital

**Tasks:**
1. Deploy data collectors to cloud (24/7 uptime)
2. Implement signal generation pipeline
3. Paper trade for 4-8 weeks
4. Monitor performance vs backtest
5. Identify and fix issues (latency, data quality, false signals)
6. Iterate on strategy

**Deliverable:** Live performance metrics, comparison to backtest

### Phase 4: Real Money (Week 13+) - Capital Required

**Goal:** Execute strategy with real capital

**Tasks:**
1. Set up wallet with USDC on Polygon
2. Implement automated trading via py-clob-client
3. Start with small positions ($100-500 per trade)
4. Monitor P&L, risk metrics
5. Scale gradually if profitable

**Deliverable:** Real trading results, profitability

---

## 9. Technical Implementation Details

### 9.1 Required Tools & Libraries

**Python Stack:**
```bash
# Core
pip install pandas numpy

# Database
pip install psycopg2-binary sqlalchemy

# Prediction Markets
pip install py-clob-client requests

# Twitter (choose one)
pip install snscrape  # Free but fragile
# OR use Apify SDK
pip install apify-client

# ML & Analysis
pip install scikit-learn xgboost matplotlib seaborn

# Time series
pip install pytz python-dateutil

# Optional: faster data processing
pip install polars pyarrow
```

**Infrastructure:**
- PostgreSQL 14+ (or TimescaleDB for time-series optimization)
- Python 3.9+
- 2-4 GB RAM for MVP (10-20 GB for full dataset)
- Cron or systemd for scheduled data collection

### 9.2 Sample Data Collection Script

```python
#!/usr/bin/env python3
"""
Collect Polymarket and Twitter data for backtesting
"""

import time
from datetime import datetime, timedelta
import pandas as pd
from py_clob_client.client import ClobClient
import snscrape.modules.twitter as sntwitter
from sqlalchemy import create_engine

# Database connection
engine = create_engine('postgresql://user:pass@localhost/prediction_markets')

# Initialize Polymarket client
clob_client = ClobClient("https://clob.polymarket.com")

def collect_market_snapshot(token_id):
    """Collect current market data"""
    try:
        price = clob_client.get_price(token_id, side="BUY")
        book = clob_client.get_order_book(token_id)
        
        snapshot = {
            'timestamp': datetime.utcnow(),
            'token_id': token_id,
            'price': float(price),
            'bid': float(book.bids[0]['price']) if book.bids else None,
            'ask': float(book.asks[0]['price']) if book.asks else None,
            'spread': float(book.asks[0]['price']) - float(book.bids[0]['price']) if book.bids and book.asks else None,
        }
        return snapshot
    except Exception as e:
        print(f"Error collecting market data: {e}")
        return None

def scrape_tweets(query, since_date, until_date, max_tweets=10000):
    """Scrape tweets using snscrape"""
    tweets = []
    
    # Build snscrape query
    scraper_query = f"{query} since:{since_date} until:{until_date}"
    
    try:
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(scraper_query).get_items()):
            if i >= max_tweets:
                break
            
            tweets.append({
                'tweet_id': tweet.id,
                'timestamp': tweet.date,
                'text': tweet.content,
                'author_id': tweet.user.id,
                'author_username': tweet.user.username,
                'likes': tweet.likeCount,
                'retweets': tweet.retweetCount,
                'replies': tweet.replyCount,
                'language': tweet.lang,
            })
        
        return pd.DataFrame(tweets)
    except Exception as e:
        print(f"Error scraping tweets: {e}")
        return pd.DataFrame()

def main():
    # Example: collect data for one market
    market = {
        'token_id': 'YOUR_TOKEN_ID',
        'keywords': 'bitcoin OR btc OR $100k',
        'start_date': '2024-01-01',
        'end_date': '2024-01-31'
    }
    
    # 1. Collect market snapshot (run this every 15 minutes via cron)
    snapshot = collect_market_snapshot(market['token_id'])
    if snapshot:
        df_snapshot = pd.DataFrame([snapshot])
        df_snapshot.to_sql('market_snapshots', engine, if_exists='append', index=False)
        print(f"Saved snapshot: {snapshot}")
    
    # 2. Collect Twitter data (run once for historical, or daily for recent)
    tweets_df = scrape_tweets(
        query=market['keywords'],
        since_date=market['start_date'],
        until_date=market['end_date'],
        max_tweets=10000
    )
    
    if not tweets_df.empty:
        tweets_df.to_sql('tweets', engine, if_exists='append', index=False)
        print(f"Saved {len(tweets_df)} tweets")

if __name__ == '__main__':
    main()
```

### 9.3 Cron Schedule for Data Collection

```bash
# Collect market snapshots every 15 minutes
*/15 * * * * /usr/bin/python3 /path/to/collect_markets.py >> /var/log/markets.log 2>&1

# Collect recent tweets every hour (for live markets)
0 * * * * /usr/bin/python3 /path/to/collect_tweets_recent.py >> /var/log/tweets.log 2>&1

# Daily cleanup and aggregation at 3 AM
0 3 * * * /usr/bin/python3 /path/to/aggregate_data.py >> /var/log/aggregate.log 2>&1
```

---

## 10. Next Steps & Open Questions

### Immediate Actions:
1. ✅ Research data sources (DONE - this document)
2. ⬜ Set up database schema
3. ⬜ Write data collection scripts
4. ⬜ Select 5-10 markets for MVP
5. ⬜ Start collecting data (either historical or forward-looking)

### Open Questions to Answer:
1. **Which markets to focus on?** (High-profile vs niche)
2. **snscrape vs paid service?** (Free but risky vs reliable but costly)
3. **30 days vs 90 days?** (Faster MVP vs more robust data)
4. **Forward-looking vs historical?** (Free but slow vs paid but immediate)
5. **What features matter most?** (Tweet count vs engagement vs velocity?)

### Decision Point: Choose MVP Strategy

**Option A: Fast & Cheap ($0-50, 1-2 weeks)**
- Use snscrape
- 5 markets, 30 days
- Risk: May fail due to scraper issues

**Option B: Reliable & Moderate ($150-200, 1-2 weeks)**
- Use X API or Apify
- 10-20 markets, 90 days
- Higher confidence in results

**Option C: Patient & Free ($0, 4-12 weeks)**
- Start collecting NOW
- Build dataset over time
- Best for live trading focus

---

## Appendix: Quick Reference URLs

**Polymarket:**
- CLOB API: `https://clob.polymarket.com/`
- Gamma API: `https://gamma-api.polymarket.com/`
- Docs: `https://docs.polymarket.com/`
- Python Client: `https://github.com/Polymarket/py-clob-client`

**Kalshi:**
- API Docs: `https://docs.kalshi.com/`
- Base URL: `https://api.kalshi.com/`

**X/Twitter:**
- API Docs: `https://docs.x.com/x-api/introduction`
- Developer Portal: `https://developer.x.com/`

**Third-Party Tools:**
- Apify Twitter Scraper: `https://apify.com/scrapers/twitter`
- snscrape: `https://github.com/JustAnotherArchivist/snscrape`

---

**Document Version:** 1.0  
**Created:** 2026-02-06  
**Author:** OpenClaw Subagent (data-collection)  
**Status:** COMPLETE - Ready for implementation
