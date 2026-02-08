# News Sentiment Analyzer - Example Output

This document shows example outputs from the news sentiment analyzer.

## Installation

```bash
# Install required packages
pip install feedparser textblob requests

# Optional: Download TextBlob corpus for better NLP
python -m textblob.download_corpora
```

## Example 1: List News Sources

```bash
$ python news-sentiment.py --sources
```

**Output:**
```
📰 Configured News Sources (30 feeds):

  BUSINESS:
    ✓ Reuters Business
      https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best
    ✓ AP News Business
      https://apnews.com/business.rss
    ✓ Google News - Business
      https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB
    ✓ BBC News - Business
      http://feeds.bbci.co.uk/news/business/rss.xml
    ✓ CNBC Top News
      https://www.cnbc.com/id/100003114/device/rss/rss.html
    ✓ CNBC - Markets
      https://www.cnbc.com/id/10000664/device/rss/rss.html
    ✓ Yahoo Finance
      https://finance.yahoo.com/news/rssindex

  CRYPTO:
    ✓ CoinDesk - Bitcoin
      https://www.coindesk.com/arc/outboundfeeds/rss/
    ✓ CoinTelegraph - Main
      https://cointelegraph.com/rss
    ✓ CryptoSlate
      https://cryptoslate.com/feed/
    ✓ The Block - Crypto
      https://www.theblock.co/rss.xml

  GENERAL:
    ✓ Reuters World News
      https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best
    ✓ AP News Top Stories
      https://apnews.com/rss
    ✓ Google News - Top Stories
      https://news.google.com/rss
    ✓ NPR News
      https://feeds.npr.org/1001/rss.xml
    ✓ BBC News - World
      http://feeds.bbci.co.uk/news/world/rss.xml

  POLITICS:
    ✓ AP News Politics
      https://apnews.com/politics.rss
    ✓ NPR Politics
      https://feeds.npr.org/1014/rss.xml
    ✓ Politico
      https://www.politico.com/rss/politics08.xml
    ✓ The Hill - News
      https://thehill.com/news/feed/

  SPORTS:
    ✓ Google News - Sports
      https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB
    ✓ ESPN - Top Headlines
      https://www.espn.com/espn/rss/news
    ✓ ESPN - NFL
      https://www.espn.com/espn/rss/nfl/news
    ✓ ESPN - NBA
      https://www.espn.com/espn/rss/nba/news

  TECHNOLOGY:
    ✓ Google News - Technology
      https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB
    ✓ BBC News - Technology
      http://feeds.bbci.co.uk/news/technology/rss.xml
    ✓ TechCrunch
      https://techcrunch.com/feed/
    ✓ Hacker News
      https://news.ycombinator.com/rss
    ✓ The Verge
      https://www.theverge.com/rss/index.xml
    ✓ Ars Technica
      https://feeds.arstechnica.com/arstechnica/index
```

---

## Example 2: Daily News Summary

```bash
$ python news-sentiment.py --fetch
```

**Output:**
```
Fetching articles from all feeds...
Fetching: Reuters World News...
Fetching: Reuters Business...
Fetching: AP News Top Stories...
Fetching: CoinDesk - Bitcoin...
Fetching: Google News - Top Stories...
[... fetching 30 feeds ...]

📊 News Summary (342 articles):

Sentiment Distribution:
  🟢 Bullish: 98
  🔴 Bearish: 127
  ⚪ Neutral: 117

Average Sentiment Score: -0.084 (-1 = bearish, +1 = bullish)

Most Mentioned:
  • bitcoin: 45 articles
  • crypto: 38 articles
  • trump: 34 articles
  • fed: 29 articles
  • ai: 24 articles

Recent Headlines:
  1. 🔴 Bitcoin Drops Below $42K as Fed Signals Rate Hike Concerns
     Source: CoinDesk | Wed, 05 Feb 2026 18:23:00 GMT
  2. 🟢 Tech Stocks Rally on Strong Earnings from Major Players
     Source: CNBC Top News | Wed, 05 Feb 2026 17:45:00 GMT
  3. ⚪ Supreme Court Hears Arguments on Controversial Immigration Case
     Source: AP News Politics | Wed, 05 Feb 2026 16:30:00 GMT
  4. 🔴 Global Markets Plunge Amid Recession Fears
     Source: Reuters Business | Wed, 05 Feb 2026 15:12:00 GMT
  5. 🟢 NFL Playoffs Generate Record Betting Volume on Polymarket
     Source: The Block - Crypto | Wed, 05 Feb 2026 14:22:00 GMT
  6. ⚪ New AI Model Raises Questions About Job Market Impact
     Source: TechCrunch | Wed, 05 Feb 2026 13:45:00 GMT
  7. 🔴 Ethereum Network Faces Congestion Issues During Peak Hours
     Source: CoinTelegraph - Main | Wed, 05 Feb 2026 12:33:00 GMT
  8. 🟢 Presidential Candidate Surges in Latest Polls
     Source: Politico | Wed, 05 Feb 2026 11:20:00 GMT
  9. 🔴 Major Tech Company Announces Layoffs Amid Cost-Cutting
     Source: The Verge | Wed, 05 Feb 2026 10:15:00 GMT
  10. 🟢 Breakthrough in Quantum Computing Announced by Research Team
      Source: BBC News - Technology | Wed, 05 Feb 2026 09:30:00 GMT
```

---

## Example 3: Market-Specific Sentiment

```bash
$ python news-sentiment.py --market bitcoin
```

**Output:**
```
📈 Sentiment Analysis: BITCOIN

Articles Found: 45
Overall Sentiment: BEARISH
Average Score: -0.234
  🟢 Bullish: 12
  🔴 Bearish: 25
  ⚪ Neutral: 8

Recent Articles:
  1. 🔴 Bitcoin Drops Below $42K as Fed Signals Rate Hike Concerns
     Score: -0.567 | CoinDesk
  2. 🔴 Crypto Market Sees $2B in Liquidations as Bitcoin Falls
     Score: -0.723 | CoinTelegraph - Main
  3. ⚪ Bitcoin Mining Difficulty Adjusts to New Levels
     Score: 0.045 | The Block - Crypto
  4. 🟢 Institutional Investors Show Renewed Interest in Bitcoin
     Score: 0.412 | Reuters Business
  5. 🔴 Regulatory Concerns Weigh on Bitcoin Price Action
     Score: -0.389 | CryptoSlate

⚠️  SENTIMENT SHIFT DETECTED!
   bullish → bearish
   Change: -0.421
```

---

## Example 4: Overall Market Sentiment

```bash
$ python news-sentiment.py --sentiment
```

**Output:**
```
📊 News Summary (342 articles):

Sentiment Distribution:
  🟢 Bullish: 98
  🔴 Bearish: 127
  ⚪ Neutral: 117

Average Sentiment Score: -0.084 (-1 = bearish, +1 = bullish)

Most Mentioned:
  • bitcoin: 45 articles
  • crypto: 38 articles
  • trump: 34 articles
  • election: 31 articles
  • fed: 29 articles

Recent Headlines:
  [... top 10 headlines ...]
```

---

## Example 5: Adding a Custom Feed

```bash
$ python news-sentiment.py --add-feed "https://example.com/rss" --feed-name "Example News" --feed-category politics
```

**Output:**
```
✓ Added feed: Example News (politics)
```

---

## Example 6: Alert Configuration

```bash
$ python news-sentiment.py --alerts
```

**Output:**
```
🔔 Alert Configuration

Current settings:
  Enabled: True
  Sentiment shift threshold: 0.3
  Volume threshold multiplier: 2.0
  Major keywords: crash, surge, breakthrough, crisis

To modify, edit: news_data/alerts.json
```

---

## Example 7: Python Module Integration

```python
from news_sentiment import NewsSentiment

# Initialize
news = NewsSentiment()

# Fetch fresh articles
news.fetch_all_feeds()

# Get recent articles (last 24 hours)
articles = news.get_recent(hours=24)
print(f"Found {len(articles)} articles")

# Analyze sentiment for specific topic
bitcoin_sentiment = news.get_sentiment("bitcoin")
print(f"Bitcoin sentiment: {bitcoin_sentiment['sentiment']}")
print(f"Score: {bitcoin_sentiment['average_score']:.3f}")
print(f"Articles: {bitcoin_sentiment['articles_found']}")

# Track sentiment over time
news.track_sentiment_over_time("bitcoin")

# Detect sentiment shifts
shift = news.detect_sentiment_shift("bitcoin")
if shift:
    print(f"Alert: Sentiment shifted from {shift['previous_sentiment']} to {shift['current_sentiment']}")

# Process individual article
article = articles[0]
processed = news.process_article(article)
print(f"Title: {processed['title']}")
print(f"Sentiment: {processed['sentiment']['sentiment']}")
print(f"Score: {processed['sentiment']['score']:.3f}")
print(f"Entities: {processed['entities']['markets']}")

# Correlate with price data (placeholder)
price_history = [
    {"timestamp": "2026-02-05T10:00:00", "price": 42500},
    {"timestamp": "2026-02-05T11:00:00", "price": 42300},
    {"timestamp": "2026-02-05T12:00:00", "price": 41800},
]
correlation = news.correlate_with_price("bitcoin", price_history)
print(f"Correlation: {correlation}")
```

**Output:**
```
Found 342 articles
Bitcoin sentiment: bearish
Score: -0.234
Articles: 45
Alert: Sentiment shifted from bullish to bearish
Title: Bitcoin Drops Below $42K as Fed Signals Rate Hike Concerns
Sentiment: bearish
Score: -0.567
Entities: ['bitcoin', 'btc', 'fed']
Correlation: {'market_id': 'bitcoin', 'current_sentiment': 'bearish', 'sentiment_score': -0.234, ...}
```

---

## File Structure After Running

```
workspace/
├── news-sentiment.py          # Main module
├── default-feeds.json         # Default RSS feeds
└── news_data/                 # Auto-created data directory
    ├── feeds.json            # Active feed configuration
    ├── articles.json         # Cached articles
    ├── sentiment_history.json # Historical sentiment tracking
    └── alerts.json           # Alert configuration
```

---

## Key Features Demonstrated

1. **Multi-source RSS aggregation** - Pulls from 30+ free news sources
2. **Sentiment analysis** - Keyword matching + NLP sentiment scoring
3. **Entity extraction** - Identifies markets, topics, prices
4. **Historical tracking** - Monitors sentiment changes over time
5. **Alert system** - Detects major news and sentiment shifts
6. **CLI interface** - Easy command-line usage
7. **Module API** - Can be imported into other Python scripts
8. **Flexible configuration** - Add/remove feeds, configure alerts

---

## Integration with Polymarket Trading

```python
# Example: Use sentiment to inform trading decisions
from news_sentiment import NewsSentiment
from polymarket import PolykMarketAPI  # Your existing API

news = NewsSentiment()
pm = PolykMarketAPI()

# Check sentiment before placing bet
topic = "bitcoin"
sentiment = news.get_sentiment(topic)

if sentiment['average_score'] > 0.3 and sentiment['articles_found'] > 10:
    print(f"Strong bullish sentiment detected for {topic}")
    # Consider buying YES on related markets
    
elif sentiment['average_score'] < -0.3 and sentiment['articles_found'] > 10:
    print(f"Strong bearish sentiment detected for {topic}")
    # Consider buying NO on related markets

# Track sentiment shift alerts
shift = news.detect_sentiment_shift(topic)
if shift:
    print(f"ALERT: Sentiment changed {shift['previous_sentiment']} → {shift['current_sentiment']}")
    # Consider adjusting positions
```

---

## Performance Notes

- **Fetching**: ~30 feeds takes 15-30 seconds (with rate limiting)
- **Processing**: Sentiment analysis on 300+ articles takes ~2-5 seconds
- **Storage**: JSON files are human-readable and easy to inspect
- **Memory**: Very lightweight, runs on minimal resources

---

## Next Steps / Enhancements

1. **Reddit Integration**: Add PRAW library support for r/Polymarket, r/wallstreetbets
2. **Twitter/X Integration**: Connect to existing hype monitor
3. **Real Price Correlation**: Implement actual correlation coefficients with market price data
4. **Machine Learning**: Train model on historical news → price movements
5. **Real-time Alerts**: Add webhook/notification system for major events
6. **Web Dashboard**: Create Flask/FastAPI dashboard for visualization
7. **Sentiment Graphs**: Plot sentiment trends over time

Great success! 🚀
