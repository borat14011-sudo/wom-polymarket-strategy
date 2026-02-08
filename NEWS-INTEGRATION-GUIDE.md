# News Sentiment Integration Guide

This guide shows how to integrate the News Sentiment Analyzer with your existing Polymarket trading systems.

## 🔗 Integration Patterns

### 1. **Pre-Trade Sentiment Check**

Check news sentiment before placing any bet:

```python
from news_sentiment import NewsSentiment

class PolykTradingBot:
    def __init__(self):
        self.news = NewsSentiment()
        
    def should_bet(self, market_question, position="YES"):
        """Check if sentiment supports the bet."""
        # Extract key topics from market question
        topics = self.extract_topics(market_question)
        
        sentiment_scores = []
        for topic in topics:
            sentiment = self.news.get_sentiment(topic)
            if sentiment['articles_found'] >= 10:  # Minimum confidence
                sentiment_scores.append(sentiment['average_score'])
        
        if not sentiment_scores:
            return False, "Insufficient news data"
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        # Bullish sentiment supports YES bets
        if position == "YES" and avg_sentiment > 0.3:
            return True, f"Bullish sentiment: {avg_sentiment:.3f}"
        
        # Bearish sentiment supports NO bets
        elif position == "NO" and avg_sentiment < -0.3:
            return True, f"Bearish sentiment: {avg_sentiment:.3f}"
        
        return False, f"Neutral sentiment: {avg_sentiment:.3f}"
    
    def extract_topics(self, question):
        """Extract key topics from market question."""
        # Simple keyword extraction
        keywords = ["bitcoin", "trump", "biden", "election", "fed", 
                   "ethereum", "crypto", "stock market", "nfl", "nba"]
        
        topics = []
        question_lower = question.lower()
        for keyword in keywords:
            if keyword in question_lower:
                topics.append(keyword)
        
        return topics if topics else [question.split()[0:3]]  # Fallback
```

**Usage:**
```python
bot = PolykTradingBot()
market = "Will Bitcoin reach $50K by March 2026?"

should_bet, reason = bot.should_bet(market, position="YES")
if should_bet:
    print(f"✓ Placing bet: {reason}")
    # Place your bet
else:
    print(f"✗ Skipping: {reason}")
```

---

### 2. **Sentiment Shift Alerts**

Monitor sentiment changes and adjust positions:

```python
import time
from news_sentiment import NewsSentiment

class SentimentMonitor:
    def __init__(self, topics, check_interval=3600):
        self.news = NewsSentiment()
        self.topics = topics
        self.check_interval = check_interval  # seconds
        
    def monitor(self):
        """Continuous monitoring loop."""
        print(f"Starting sentiment monitor for: {', '.join(self.topics)}")
        
        while True:
            for topic in self.topics:
                self.check_topic(topic)
            
            time.sleep(self.check_interval)
    
    def check_topic(self, topic):
        """Check for sentiment shifts on a topic."""
        # Update current sentiment
        self.news.track_sentiment_over_time(topic)
        
        # Check for shifts
        shift = self.news.detect_sentiment_shift(topic)
        
        if shift:
            self.handle_shift(shift)
    
    def handle_shift(self, shift):
        """Handle detected sentiment shift."""
        print(f"\n🚨 ALERT: {shift['topic'].upper()}")
        print(f"   {shift['previous_sentiment']} → {shift['current_sentiment']}")
        print(f"   Change: {shift['score_change']:+.3f}")
        
        # Integration points:
        # - Send notification (Telegram, Discord, email)
        # - Adjust position sizes
        # - Close positions if shift is against you
        # - Open new positions if shift is in your favor
        
        if abs(shift['score_change']) > 0.5:
            print("   ⚠️  MAJOR SHIFT - Consider immediate action")

# Usage
monitor = SentimentMonitor(
    topics=["bitcoin", "trump", "election", "fed"],
    check_interval=3600  # Check every hour
)

# Run in background or as separate process
# monitor.monitor()
```

---

### 3. **Market Discovery**

Find markets with unusual news activity:

```python
from news_sentiment import NewsSentiment
from collections import Counter

class MarketDiscovery:
    def __init__(self):
        self.news = NewsSentiment()
        
    def find_trending_topics(self, hours=24, min_articles=20):
        """Find topics with high news volume."""
        # Fetch fresh articles
        print("Fetching latest articles...")
        self.news.fetch_all_feeds()
        
        articles = self.news.get_recent(hours=hours)
        
        # Extract all mentioned entities
        all_entities = []
        for article in articles:
            if 'entities' not in article:
                article = self.news.process_article(article)
            all_entities.extend(article['entities']['markets'])
        
        # Count mentions
        entity_counts = Counter(all_entities)
        
        # Filter by minimum articles
        trending = {
            entity: count 
            for entity, count in entity_counts.items() 
            if count >= min_articles
        }
        
        return trending
    
    def find_sentiment_extremes(self, hours=24):
        """Find topics with extreme sentiment (very bullish or bearish)."""
        trending = self.find_trending_topics(hours=hours, min_articles=10)
        
        extremes = {
            'bullish': [],
            'bearish': []
        }
        
        for topic, count in trending.items():
            sentiment = self.news.get_sentiment(topic)
            
            if sentiment['average_score'] > 0.4:
                extremes['bullish'].append({
                    'topic': topic,
                    'score': sentiment['average_score'],
                    'articles': count
                })
            elif sentiment['average_score'] < -0.4:
                extremes['bearish'].append({
                    'topic': topic,
                    'score': sentiment['average_score'],
                    'articles': count
                })
        
        # Sort by score
        extremes['bullish'].sort(key=lambda x: x['score'], reverse=True)
        extremes['bearish'].sort(key=lambda x: x['score'])
        
        return extremes

# Usage
discovery = MarketDiscovery()

print("🔍 Finding trending topics...")
trending = discovery.find_trending_topics(hours=24)

print("\nTrending Topics (24h):")
for topic, count in sorted(trending.items(), key=lambda x: x[1], reverse=True):
    print(f"  • {topic}: {count} articles")

print("\n📊 Sentiment Extremes:")
extremes = discovery.find_sentiment_extremes(hours=24)

print("\n🟢 Most Bullish:")
for item in extremes['bullish'][:5]:
    print(f"  • {item['topic']}: {item['score']:.3f} ({item['articles']} articles)")

print("\n🔴 Most Bearish:")
for item in extremes['bearish'][:5]:
    print(f"  • {item['topic']}: {item['score']:.3f} ({item['articles']} articles)")
```

---

### 4. **Cron Job / Scheduled Reports**

Send daily sentiment reports:

```python
#!/usr/bin/env python3
"""
Daily sentiment report script
Run with cron: 0 9 * * * /path/to/sentiment-report.py
"""

from news_sentiment import NewsSentiment
from datetime import datetime

def generate_daily_report():
    """Generate and send daily sentiment report."""
    news = NewsSentiment()
    
    # Fetch fresh articles
    print(f"Generating sentiment report for {datetime.now().date()}")
    news.fetch_all_feeds()
    
    articles = news.get_recent(hours=24)
    
    # Key topics to track
    topics = ["bitcoin", "ethereum", "trump", "election", "fed", "crypto"]
    
    report = []
    report.append(f"📰 Daily Sentiment Report - {datetime.now().strftime('%Y-%m-%d')}\n")
    report.append(f"Total Articles: {len(articles)}\n")
    
    # Overall sentiment
    if articles:
        sentiments = [a.get('sentiment', {}).get('sentiment', 'neutral') for a in articles]
        bullish = sentiments.count('bullish')
        bearish = sentiments.count('bearish')
        neutral = sentiments.count('neutral')
        
        report.append(f"Overall: 🟢{bullish} 🔴{bearish} ⚪{neutral}\n")
    
    # Topic-specific sentiment
    report.append("\n📊 Topic Sentiment:\n")
    for topic in topics:
        sentiment = news.get_sentiment(topic)
        if sentiment['articles_found'] > 0:
            emoji = {
                'bullish': '🟢',
                'bearish': '🔴',
                'neutral': '⚪'
            }.get(sentiment['sentiment'], '⚪')
            
            report.append(
                f"  {emoji} {topic.upper()}: {sentiment['sentiment']} "
                f"({sentiment['average_score']:+.3f}, {sentiment['articles_found']} articles)\n"
            )
    
    # Sentiment shifts
    shifts = []
    for topic in topics:
        news.track_sentiment_over_time(topic)
        shift = news.detect_sentiment_shift(topic)
        if shift:
            shifts.append(shift)
    
    if shifts:
        report.append("\n🚨 Sentiment Shifts Detected:\n")
        for shift in shifts:
            report.append(
                f"  • {shift['topic']}: {shift['previous_sentiment']} → "
                f"{shift['current_sentiment']} ({shift['score_change']:+.3f})\n"
            )
    
    report_text = ''.join(report)
    print(report_text)
    
    # Send report (integrate with your notification system)
    # send_telegram(report_text)
    # send_email(report_text)
    # post_to_discord(report_text)
    
    return report_text

if __name__ == "__main__":
    generate_daily_report()
```

**Cron setup:**
```bash
# Edit crontab
crontab -e

# Add line (runs daily at 9 AM)
0 9 * * * cd /path/to/workspace && python3 sentiment-report.py >> sentiment.log 2>&1
```

---

### 5. **Integration with Existing Hype Monitor**

Combine news sentiment with Twitter/X hype tracking:

```python
from news_sentiment import NewsSentiment
# from twitter_hype_monitor import HypeMonitor  # Your existing module

class CombinedSentiment:
    def __init__(self):
        self.news = NewsSentiment()
        # self.hype = HypeMonitor()
        
    def get_combined_sentiment(self, topic):
        """Combine news sentiment with social media hype."""
        # News sentiment
        news_sentiment = self.news.get_sentiment(topic)
        news_score = news_sentiment['average_score']
        news_count = news_sentiment['articles_found']
        
        # Twitter/X hype (placeholder - integrate with your module)
        # hype_data = self.hype.get_hype(topic)
        # hype_score = hype_data['sentiment_score']
        # hype_count = hype_data['tweet_count']
        
        hype_score = 0.0  # Placeholder
        hype_count = 0    # Placeholder
        
        # Weighted combination
        # News: 60% weight (more reliable)
        # Hype: 40% weight (faster, but noisier)
        
        if news_count > 0 and hype_count > 0:
            combined = (news_score * 0.6) + (hype_score * 0.4)
            confidence = min(news_count + hype_count, 100) / 100
        elif news_count > 0:
            combined = news_score
            confidence = min(news_count, 50) / 50
        elif hype_count > 0:
            combined = hype_score
            confidence = min(hype_count, 100) / 100
        else:
            combined = 0.0
            confidence = 0.0
        
        return {
            'topic': topic,
            'combined_score': combined,
            'confidence': confidence,
            'news': {
                'score': news_score,
                'article_count': news_count
            },
            'hype': {
                'score': hype_score,
                'tweet_count': hype_count
            }
        }

# Usage
combined = CombinedSentiment()
result = combined.get_combined_sentiment("bitcoin")

print(f"Combined Sentiment: {result['combined_score']:.3f}")
print(f"Confidence: {result['confidence']:.1%}")
print(f"News: {result['news']['score']:.3f} ({result['news']['article_count']} articles)")
print(f"Hype: {result['hype']['score']:.3f} ({result['hype']['tweet_count']} tweets)")
```

---

### 6. **Risk Management Integration**

Use sentiment for position sizing and risk adjustment:

```python
from news_sentiment import NewsSentiment

class SentimentRiskManager:
    def __init__(self, base_bet_size=100):
        self.news = NewsSentiment()
        self.base_bet_size = base_bet_size
        
    def calculate_bet_size(self, market_question, position="YES"):
        """Calculate bet size based on sentiment confidence."""
        topics = self.extract_topics(market_question)
        
        if not topics:
            return 0, "No recognizable topics"
        
        sentiment_data = []
        for topic in topics:
            sentiment = self.news.get_sentiment(topic)
            if sentiment['articles_found'] >= 5:
                sentiment_data.append(sentiment)
        
        if not sentiment_data:
            return 0, "Insufficient news data"
        
        # Calculate average sentiment
        avg_score = sum(s['average_score'] for s in sentiment_data) / len(sentiment_data)
        avg_articles = sum(s['articles_found'] for s in sentiment_data) / len(sentiment_data)
        
        # Confidence factor (more articles = higher confidence)
        confidence = min(avg_articles / 30, 1.0)  # Max confidence at 30 articles
        
        # Alignment factor (how well sentiment matches position)
        if position == "YES":
            alignment = max(0, avg_score)  # Positive sentiment aligns with YES
        else:
            alignment = max(0, -avg_score)  # Negative sentiment aligns with NO
        
        # Final bet size
        bet_size = self.base_bet_size * confidence * alignment
        
        return bet_size, f"Confidence: {confidence:.1%}, Alignment: {alignment:.2f}"
    
    def extract_topics(self, question):
        """Extract topics from market question."""
        # Simplified - same as previous example
        keywords = ["bitcoin", "trump", "biden", "election", "fed", "ethereum"]
        return [kw for kw in keywords if kw in question.lower()]

# Usage
risk_mgr = SentimentRiskManager(base_bet_size=1000)

market = "Will Bitcoin reach $50K by March 2026?"
bet_size, reason = risk_mgr.calculate_bet_size(market, position="YES")

print(f"Recommended bet size: ${bet_size:.2f}")
print(f"Reason: {reason}")
```

---

## 🔄 Complete Trading Flow

Putting it all together:

```python
from news_sentiment import NewsSentiment

class PolykTradingSystem:
    def __init__(self):
        self.news = NewsSentiment()
        self.base_bet_size = 1000
        self.markets_to_watch = []
        
    def daily_routine(self):
        """Run daily trading routine."""
        print("🌅 Starting daily routine...")
        
        # 1. Fetch fresh news
        print("\n1️⃣ Fetching news...")
        self.news.fetch_all_feeds()
        
        # 2. Discover trending topics
        print("\n2️⃣ Finding trending topics...")
        trending = self.find_trending_topics()
        
        # 3. Check sentiment for watchlist
        print("\n3️⃣ Checking watchlist sentiment...")
        self.check_watchlist()
        
        # 4. Look for sentiment shifts
        print("\n4️⃣ Detecting sentiment shifts...")
        self.detect_shifts()
        
        # 5. Find trading opportunities
        print("\n5️⃣ Finding opportunities...")
        self.find_opportunities(trending)
        
        print("\n✅ Daily routine complete!")
    
    def find_trending_topics(self):
        """Find trending topics."""
        # Implementation from earlier examples
        pass
    
    def check_watchlist(self):
        """Check sentiment for markets on watchlist."""
        for market in self.markets_to_watch:
            sentiment = self.news.get_sentiment(market['topic'])
            print(f"  • {market['topic']}: {sentiment['sentiment']} ({sentiment['average_score']:+.3f})")
    
    def detect_shifts(self):
        """Detect and alert on sentiment shifts."""
        topics = ["bitcoin", "trump", "election", "fed"]
        for topic in topics:
            self.news.track_sentiment_over_time(topic)
            shift = self.news.detect_sentiment_shift(topic)
            if shift:
                print(f"  🚨 {topic}: {shift['previous_sentiment']} → {shift['current_sentiment']}")
    
    def find_opportunities(self, trending):
        """Find trading opportunities."""
        # Implementation based on your strategy
        pass

# Usage
system = PolykTradingSystem()
system.daily_routine()
```

---

## 🎯 Best Practices

1. **Always fetch fresh data**: Run `fetch_all_feeds()` before analysis
2. **Check article count**: Require minimum 10 articles for confidence
3. **Combine signals**: Don't rely on sentiment alone
4. **Track over time**: Use `track_sentiment_over_time()` for trends
5. **Set thresholds**: Define your own bullish/bearish thresholds
6. **Monitor shifts**: Sentiment changes matter more than absolute values
7. **Test thoroughly**: Backtest your integration before live trading

---

## 📞 Next Steps

1. Install the module: `pip install -r requirements-news-sentiment.txt`
2. Test basic functionality: `python news-sentiment.py --fetch`
3. Integrate with your bot (use examples above)
4. Monitor performance and adjust thresholds
5. Expand with Reddit and Twitter integration

**Great success!** 🚀
