# News Sentiment Analyzer - README

A comprehensive news sentiment tracking module for Polymarket trading systems. Aggregates news from 30+ free RSS feeds, performs sentiment analysis, and correlates with prediction markets.

## 🚀 Quick Start

```bash
# Install dependencies
pip install feedparser textblob requests

# Optional: Better NLP sentiment
python -m textblob.download_corpora

# List available news sources
python news-sentiment.py --sources

# Fetch and analyze today's news
python news-sentiment.py --fetch

# Get sentiment for specific market
python news-sentiment.py --market bitcoin

# Show overall market sentiment
python news-sentiment.py --sentiment
```

## 📦 Features

### 1. **Multi-Source News Aggregation**
- 30+ pre-configured RSS feeds (Reuters, AP, Google News, BBC, CNBC, etc.)
- Categories: General, Business, Politics, Crypto, Technology, Sports
- Easy to add custom feeds
- All sources are **free** and publicly accessible

### 2. **Sentiment Analysis**
- **Keyword matching**: Bullish/bearish term detection
- **NLP analysis**: TextBlob sentiment polarity
- **Combined scoring**: Weighted average for accuracy
- **Entity extraction**: Markets, topics, prices

### 3. **Market Correlation**
- Match news to prediction markets
- Calculate sentiment scores per topic
- Track sentiment changes over time
- Historical analysis framework

### 4. **Alert System**
- Major news event detection
- Sentiment shift alerts (bullish ↔ bearish)
- Unusual news volume detection
- Configurable thresholds

### 5. **CLI Interface**
```bash
python news-sentiment.py                       # Daily summary
python news-sentiment.py --market "bitcoin"   # Market-specific
python news-sentiment.py --sentiment          # Overall sentiment
python news-sentiment.py --sources            # List sources
python news-sentiment.py --add-feed URL       # Add RSS feed
python news-sentiment.py --alerts             # Configure alerts
python news-sentiment.py --fetch              # Fetch fresh articles
python news-sentiment.py --hours 48           # Look back 48 hours
```

### 6. **Python Module API**
```python
from news_sentiment import NewsSentiment

news = NewsSentiment()

# Fetch articles
news.fetch_all_feeds()

# Get recent articles
articles = news.get_recent(hours=24)

# Analyze topic sentiment
sentiment = news.get_sentiment("bitcoin")

# Track over time
news.track_sentiment_over_time("bitcoin")

# Detect shifts
shift = news.detect_sentiment_shift("bitcoin")

# Correlate with prices
correlation = news.correlate_with_price(market_id, price_history)
```

## 📁 File Structure

```
workspace/
├── news-sentiment.py              # Main module (CLI + API)
├── default-feeds.json             # 30+ default RSS feeds
├── NEWS-SENTIMENT-README.md       # This file
├── EXAMPLE-OUTPUT.md              # Example outputs
└── news_data/                     # Auto-created
    ├── feeds.json                # Active feeds
    ├── articles.json             # Cached articles
    ├── sentiment_history.json    # Historical tracking
    └── alerts.json               # Alert config
```

## 🎯 Use Cases

### 1. **Pre-Trade Research**
```python
# Check sentiment before placing bet
sentiment = news.get_sentiment("election")
if sentiment['average_score'] > 0.3:
    print("Bullish sentiment - consider YES position")
```

### 2. **Sentiment Shift Alerts**
```python
# Monitor for major sentiment changes
shift = news.detect_sentiment_shift("bitcoin")
if shift:
    print(f"ALERT: {shift['previous_sentiment']} → {shift['current_sentiment']}")
    # Adjust positions accordingly
```

### 3. **Market Discovery**
```python
# Find trending topics
articles = news.get_recent(hours=24)
# Extract most mentioned entities
# Find markets with unusual news volume
```

### 4. **Historical Analysis**
```python
# Track sentiment over time
news.track_sentiment_over_time("trump")
# Compare sentiment history with price movements
# Identify lead/lag relationships
```

## 🔧 Configuration

### Add Custom RSS Feed
```bash
python news-sentiment.py --add-feed "https://example.com/rss" \
  --feed-name "Example News" \
  --feed-category politics
```

### Configure Alerts
Edit `news_data/alerts.json`:
```json
{
  "enabled": true,
  "sentiment_shift_threshold": 0.3,
  "volume_threshold_multiplier": 2.0,
  "major_keywords": ["crash", "surge", "breakthrough", "crisis"]
}
```

### Customize Sentiment Keywords
Edit the class in `news-sentiment.py`:
```python
self.bullish_keywords = [
    'surge', 'rally', 'boom', 'moon', 'pump', ...
]

self.bearish_keywords = [
    'crash', 'plunge', 'collapse', 'dump', 'panic', ...
]
```

## 📊 Sentiment Scoring

### How It Works
1. **Keyword Analysis** (60% weight)
   - Counts bullish keywords (surge, rally, breakthrough, etc.)
   - Counts bearish keywords (crash, plunge, decline, etc.)
   - Score = (bullish - bearish) / total

2. **NLP Analysis** (40% weight)
   - Uses TextBlob sentiment polarity
   - Range: -1.0 (negative) to +1.0 (positive)

3. **Combined Score**
   - Weighted average: `0.6 * keyword + 0.4 * nlp`
   - Classification:
     - `> 0.2` = Bullish 🟢
     - `< -0.2` = Bearish 🔴
     - Otherwise = Neutral ⚪

### Entity Extraction
- **Markets**: Bitcoin, Ethereum, Trump, Fed, etc.
- **Prices**: Regex pattern `$X,XXX.XX`
- Uses regex patterns for reliable extraction

## 🔌 Integration Examples

### With Polymarket API
```python
from news_sentiment import NewsSentiment
from polymarket_api import PolykMarketAPI

news = NewsSentiment()
pm = PolykMarketAPI()

# Find markets with strong sentiment
for market in pm.get_active_markets():
    sentiment = news.get_sentiment(market['question'])
    
    if sentiment['average_score'] > 0.4:
        print(f"Strong bullish sentiment: {market['question']}")
        # Consider buying YES
```

### With Discord Bot
```python
from news_sentiment import NewsSentiment
import discord

news = NewsSentiment()

@bot.command()
async def sentiment(ctx, topic):
    result = news.get_sentiment(topic)
    await ctx.send(f"**{topic.upper()}**\n"
                   f"Sentiment: {result['sentiment']}\n"
                   f"Score: {result['average_score']:.3f}\n"
                   f"Articles: {result['articles_found']}")
```

### Scheduled Monitoring
```python
import schedule
from news_sentiment import NewsSentiment

news = NewsSentiment()

def check_sentiment():
    topics = ["bitcoin", "trump", "fed"]
    for topic in topics:
        shift = news.detect_sentiment_shift(topic)
        if shift:
            send_alert(f"Sentiment shift: {topic}")

schedule.every(1).hours.do(check_sentiment)
```

## 📈 Advanced Features

### Historical Sentiment Tracking
The system automatically tracks sentiment over time:
```python
# Stored in news_data/sentiment_history.json
{
  "bitcoin": [
    {
      "timestamp": "2026-02-05T10:00:00",
      "average_score": 0.234,
      "sentiment": "bullish",
      "article_count": 45
    },
    {
      "timestamp": "2026-02-05T14:00:00",
      "average_score": -0.123,
      "sentiment": "bearish",
      "article_count": 52
    }
  ]
}
```

### Price Correlation (Framework)
```python
# Placeholder for price correlation analysis
price_history = [
    {"timestamp": "2026-02-05T10:00:00", "price": 42500},
    {"timestamp": "2026-02-05T11:00:00", "price": 42300},
    {"timestamp": "2026-02-05T12:00:00", "price": 41800},
]

correlation = news.correlate_with_price("bitcoin", price_history)

# Future implementation:
# - Align timestamps
# - Calculate correlation coefficients
# - Detect lead/lag relationships
# - Identify news-driven vs organic moves
```

## 🚨 Alert Types

### 1. Sentiment Shift
```python
{
  'type': 'sentiment_shift',
  'topic': 'bitcoin',
  'previous_sentiment': 'bullish',
  'current_sentiment': 'bearish',
  'score_change': -0.421,
  'timestamp': '2026-02-05T15:30:00'
}
```

### 2. Major News Event
```python
{
  'type': 'major_news',
  'title': 'Bitcoin Crashes Below $30K in Historic Drop',
  'keywords': ['crash', 'crisis'],
  'link': 'https://...',
  'source': 'Reuters',
  'timestamp': '2026-02-05T15:30:00'
}
```

### 3. Volume Spike (Coming Soon)
- Detects unusual increase in news volume
- Compares to historical average
- Threshold: 2x normal volume

## 🛠️ Troubleshooting

### "feedparser not found"
```bash
pip install feedparser
```

### "textblob not found" (optional)
```bash
pip install textblob
python -m textblob.download_corpora
```

### "requests not found"
```bash
pip install requests
```

### RSS Feed Fails
- Some feeds may change URLs over time
- Test individual feeds: `python -c "import feedparser; print(feedparser.parse('URL'))"`
- Remove broken feeds or add alternatives

### No Articles Found
- Run with `--fetch` to fetch fresh articles
- Check internet connection
- Verify feeds are still active

## 📚 Data Sources

All news sources are **free** and **publicly accessible**:

| Category | Sources |
|----------|---------|
| **General** | Reuters, AP, Google News, NPR, BBC |
| **Business** | CNBC, Yahoo Finance, Bloomberg (free feeds) |
| **Crypto** | CoinDesk, CoinTelegraph, CryptoSlate, The Block |
| **Technology** | TechCrunch, Hacker News, The Verge, Ars Technica |
| **Politics** | Politico, The Hill, NPR Politics, AP Politics |
| **Sports** | ESPN (NFL, NBA, MLB), Yahoo Sports |

See `default-feeds.json` for the complete list.

## 🔮 Future Enhancements

1. **Reddit Integration**
   - Use PRAW library
   - Monitor r/Polymarket, r/wallstreetbets
   - Track post sentiment and upvotes

2. **Twitter/X Integration**
   - Connect to existing hype monitor
   - Track trending topics
   - Analyze influencer sentiment

3. **Real Price Correlation**
   - Calculate actual correlation coefficients
   - Lead/lag analysis
   - News-driven vs organic classification

4. **Machine Learning**
   - Train on historical news → price data
   - Predict market movements
   - Optimize sentiment weights

5. **Real-time Alerts**
   - Webhook notifications
   - Email/SMS alerts
   - Telegram bot integration

6. **Web Dashboard**
   - Flask/FastAPI backend
   - Real-time sentiment charts
   - Market recommendations

## 📝 Example Workflow

```bash
# 1. Initial setup
pip install feedparser textblob requests
python -m textblob.download_corpora

# 2. Check available sources
python news-sentiment.py --sources

# 3. Fetch today's news
python news-sentiment.py --fetch

# 4. Check overall sentiment
python news-sentiment.py --sentiment

# 5. Analyze specific market
python news-sentiment.py --market bitcoin

# 6. Add custom feed
python news-sentiment.py --add-feed "https://custom.com/rss" \
  --feed-name "Custom Source" --feed-category crypto

# 7. Monitor for shifts
python news-sentiment.py --market bitcoin
# Look for "SENTIMENT SHIFT DETECTED" alerts

# 8. Integrate with trading bot
# See integration examples above
```

## 🎓 Understanding the Output

### Sentiment Score
- **-1.0 to -0.2**: Strong bearish → Bearish
- **-0.2 to +0.2**: Neutral (mixed or unclear)
- **+0.2 to +1.0**: Bullish → Strong bullish

### Article Count
- **< 10 articles**: Low confidence (not enough data)
- **10-30 articles**: Medium confidence
- **> 30 articles**: High confidence (reliable signal)

### Sentiment Shift
- **Change > 0.3**: Significant shift worth noting
- **Change > 0.5**: Major shift (rare, important)

## 💡 Pro Tips

1. **Combine with other signals**: Don't rely on sentiment alone
2. **Check article count**: More articles = more reliable sentiment
3. **Look for shifts**: Changes matter more than absolute values
4. **Time decay**: Recent sentiment matters more than old news
5. **Category-specific**: Crypto news may be more volatile than politics
6. **Cross-reference**: Compare multiple sources for confirmation

## 📞 Support & Contributing

This is a standalone module for Polymarket trading systems. Feel free to:
- Modify sentiment keywords for your use case
- Add more RSS feeds
- Enhance the correlation algorithm
- Integrate with your existing trading infrastructure

## 📄 License

Open source - use freely for your Polymarket trading systems.

---

**Great success!** 🚀

Built for the Polymarket community. Trade smart, not hard.
