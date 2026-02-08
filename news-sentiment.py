#!/usr/bin/env python3
"""
News Sentiment Analyzer for Polymarket Trading System

Tracks news sentiment from multiple sources and correlates with prediction markets.
Can be used as a CLI tool or imported as a module.

Usage:
    python news-sentiment.py                       # Today's news summary
    python news-sentiment.py --market "bitcoin"   # News for specific topic
    python news-sentiment.py --sentiment          # Overall market sentiment
    python news-sentiment.py --sources            # List news sources
    python news-sentiment.py --add-feed URL       # Add RSS feed
    python news-sentiment.py --alerts             # Set up news alerts

Module usage:
    from news_sentiment import NewsSentiment
    
    news = NewsSentiment()
    articles = news.get_recent(hours=24)
    sentiment = news.get_sentiment("bitcoin")
    correlation = news.correlate_with_price(market_id)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter
import time

# Try to import feedparser, fallback to requests
try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False
    print("Warning: feedparser not installed. Install with: pip install feedparser")

# Try to import sentiment analysis libraries
try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False

# Fallback to requests for feed parsing
try:
    import requests
    from xml.etree import ElementTree as ET
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class NewsSentiment:
    """Main class for news sentiment tracking and analysis."""
    
    def __init__(self, data_dir: str = "news_data"):
        """
        Initialize NewsSentiment tracker.
        
        Args:
            data_dir: Directory to store articles, sentiment history, and config
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Data storage paths
        self.feeds_file = self.data_dir / "feeds.json"
        self.articles_file = self.data_dir / "articles.json"
        self.sentiment_history_file = self.data_dir / "sentiment_history.json"
        self.alerts_file = self.data_dir / "alerts.json"
        
        # Load or initialize data
        self.feeds = self._load_feeds()
        self.articles = self._load_articles()
        self.sentiment_history = self._load_sentiment_history()
        self.alerts = self._load_alerts()
        
        # Sentiment keywords
        self.bullish_keywords = [
            'surge', 'rally', 'boom', 'soar', 'skyrocket', 'breakthrough', 
            'record high', 'all-time high', 'ath', 'moon', 'bullish', 'pump',
            'win', 'victory', 'success', 'growth', 'gain', 'profit', 'up',
            'positive', 'optimistic', 'confidence', 'strong', 'expansion'
        ]
        
        self.bearish_keywords = [
            'crash', 'plunge', 'collapse', 'drop', 'fall', 'decline', 'plummet',
            'bearish', 'dump', 'loss', 'down', 'negative', 'pessimistic',
            'concern', 'fear', 'panic', 'recession', 'crisis', 'failure',
            'weak', 'struggle', 'problem', 'risk', 'threat', 'warning'
        ]
        
        # Market/entity patterns
        self.market_patterns = [
            r'\b(bitcoin|btc)\b',
            r'\b(ethereum|eth)\b',
            r'\b(crypto|cryptocurrency)\b',
            r'\b(trump|biden|election)\b',
            r'\b(fed|federal reserve|interest rate)\b',
            r'\b(stock market|s&p|nasdaq|dow)\b',
            r'\b(nfl|nba|mlb|soccer|sports)\b',
            r'\b(ukraine|russia|war)\b',
            r'\b(ai|artificial intelligence|chatgpt)\b',
            r'\b(tesla|tsla)\b',
        ]
        
        # Price patterns
        self.price_pattern = r'\$[\d,]+(?:\.\d{2})?'
    
    def _load_feeds(self) -> Dict:
        """Load RSS feeds from config file."""
        if self.feeds_file.exists():
            with open(self.feeds_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Load default feeds
            default_feeds_path = Path("default-feeds.json")
            if default_feeds_path.exists():
                with open(default_feeds_path, 'r', encoding='utf-8') as f:
                    feeds = json.load(f)
                self._save_feeds(feeds)
                return feeds
            return {"feeds": []}
    
    def _save_feeds(self, feeds: Dict = None):
        """Save feeds to config file."""
        if feeds is None:
            feeds = self.feeds
        with open(self.feeds_file, 'w', encoding='utf-8') as f:
            json.dump(feeds, f, indent=2)
    
    def _load_articles(self) -> List[Dict]:
        """Load cached articles."""
        if self.articles_file.exists():
            with open(self.articles_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_articles(self):
        """Save articles to cache."""
        with open(self.articles_file, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, indent=2)
    
    def _load_sentiment_history(self) -> Dict:
        """Load sentiment history."""
        if self.sentiment_history_file.exists():
            with open(self.sentiment_history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_sentiment_history(self):
        """Save sentiment history."""
        with open(self.sentiment_history_file, 'w', encoding='utf-8') as f:
            json.dump(self.sentiment_history, f, indent=2)
    
    def _load_alerts(self) -> Dict:
        """Load alert configuration."""
        if self.alerts_file.exists():
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "enabled": True,
            "sentiment_shift_threshold": 0.3,
            "volume_threshold_multiplier": 2.0,
            "major_keywords": ["crash", "surge", "breakthrough", "crisis"]
        }
    
    def _save_alerts(self):
        """Save alert configuration."""
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(self.alerts, f, indent=2)
    
    def fetch_rss_feed(self, url: str) -> List[Dict]:
        """
        Fetch articles from an RSS feed.
        
        Args:
            url: RSS feed URL
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        if HAS_FEEDPARSER:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'published': entry.get('published', entry.get('updated', '')),
                    'source': feed.feed.get('title', url),
                    'fetched_at': datetime.now().isoformat()
                }
                articles.append(article)
        
        elif HAS_REQUESTS:
            # Fallback: parse RSS manually
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                root = ET.fromstring(response.content)
                
                # Handle RSS 2.0
                for item in root.findall('.//item'):
                    article = {
                        'title': item.findtext('title', ''),
                        'link': item.findtext('link', ''),
                        'summary': item.findtext('description', ''),
                        'published': item.findtext('pubDate', ''),
                        'source': root.findtext('.//channel/title', url),
                        'fetched_at': datetime.now().isoformat()
                    }
                    articles.append(article)
                
                # Handle Atom
                for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                    article = {
                        'title': entry.findtext('{http://www.w3.org/2005/Atom}title', ''),
                        'link': entry.find('{http://www.w3.org/2005/Atom}link').get('href', ''),
                        'summary': entry.findtext('{http://www.w3.org/2005/Atom}summary', ''),
                        'published': entry.findtext('{http://www.w3.org/2005/Atom}updated', ''),
                        'source': root.findtext('.//{http://www.w3.org/2005/Atom}title', url),
                        'fetched_at': datetime.now().isoformat()
                    }
                    articles.append(article)
                    
            except Exception as e:
                print(f"Error fetching {url}: {e}")
        
        return articles
    
    def fetch_all_feeds(self) -> List[Dict]:
        """
        Fetch articles from all configured RSS feeds.
        
        Returns:
            List of all articles
        """
        all_articles = []
        
        for feed in self.feeds.get('feeds', []):
            if not feed.get('enabled', True):
                continue
            
            print(f"Fetching: {feed['name']}...")
            articles = self.fetch_rss_feed(feed['url'])
            
            # Add category to each article
            for article in articles:
                article['category'] = feed.get('category', 'general')
            
            all_articles.extend(articles)
            time.sleep(0.5)  # Be nice to servers
        
        # Update cache
        self.articles = all_articles
        self._save_articles()
        
        return all_articles
    
    def analyze_sentiment_keyword(self, text: str) -> Tuple[float, int, int]:
        """
        Analyze sentiment using keyword matching.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment_score, bullish_count, bearish_count)
            sentiment_score: -1.0 to 1.0
        """
        text_lower = text.lower()
        
        bullish_count = sum(1 for keyword in self.bullish_keywords if keyword in text_lower)
        bearish_count = sum(1 for keyword in self.bearish_keywords if keyword in text_lower)
        
        total = bullish_count + bearish_count
        if total == 0:
            return 0.0, 0, 0
        
        sentiment_score = (bullish_count - bearish_count) / total
        return sentiment_score, bullish_count, bearish_count
    
    def analyze_sentiment_nlp(self, text: str) -> float:
        """
        Analyze sentiment using NLP (TextBlob).
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment polarity: -1.0 to 1.0
        """
        if not HAS_TEXTBLOB:
            return 0.0
        
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0.0
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Combined sentiment analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        keyword_score, bullish, bearish = self.analyze_sentiment_keyword(text)
        nlp_score = self.analyze_sentiment_nlp(text)
        
        # Weighted average (keyword-based is often more reliable for financial news)
        combined_score = (keyword_score * 0.6 + nlp_score * 0.4)
        
        # Classify
        if combined_score > 0.2:
            sentiment = "bullish"
        elif combined_score < -0.2:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
        
        return {
            'sentiment': sentiment,
            'score': combined_score,
            'keyword_score': keyword_score,
            'nlp_score': nlp_score,
            'bullish_keywords': bullish,
            'bearish_keywords': bearish
        }
    
    def extract_entities(self, text: str) -> Dict:
        """
        Extract entities (markets, prices) from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with extracted entities
        """
        entities = {
            'markets': [],
            'prices': []
        }
        
        # Extract markets/topics
        text_lower = text.lower()
        for pattern in self.market_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                entity = match.group(1) if match.groups() else match.group(0)
                entities['markets'].append(entity.lower())
        
        # Extract prices
        price_matches = re.findall(self.price_pattern, text)
        entities['prices'] = price_matches
        
        # Remove duplicates
        entities['markets'] = list(set(entities['markets']))
        
        return entities
    
    def process_article(self, article: Dict) -> Dict:
        """
        Process an article: analyze sentiment and extract entities.
        
        Args:
            article: Article dictionary
            
        Returns:
            Article with added analysis
        """
        text = f"{article['title']} {article['summary']}"
        
        # Sentiment analysis
        sentiment = self.analyze_sentiment(text)
        article['sentiment'] = sentiment
        
        # Entity extraction
        entities = self.extract_entities(text)
        article['entities'] = entities
        
        return article
    
    def get_recent(self, hours: int = 24) -> List[Dict]:
        """
        Get recent articles from the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of recent articles with analysis
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_articles = []
        for article in self.articles:
            try:
                fetched = datetime.fromisoformat(article['fetched_at'])
                if fetched >= cutoff:
                    # Process if not already processed
                    if 'sentiment' not in article:
                        article = self.process_article(article)
                    recent_articles.append(article)
            except:
                continue
        
        return recent_articles
    
    def get_sentiment(self, topic: str) -> Dict:
        """
        Get sentiment analysis for a specific topic/market.
        
        Args:
            topic: Topic or market name (e.g., "bitcoin", "trump")
            
        Returns:
            Dictionary with sentiment statistics
        """
        topic_lower = topic.lower()
        relevant_articles = []
        
        for article in self.articles:
            # Check if topic is mentioned
            text = f"{article['title']} {article['summary']}".lower()
            if topic_lower in text:
                if 'sentiment' not in article:
                    article = self.process_article(article)
                relevant_articles.append(article)
        
        if not relevant_articles:
            return {
                'topic': topic,
                'articles_found': 0,
                'sentiment': 'neutral',
                'average_score': 0.0,
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0
            }
        
        # Calculate statistics
        scores = [a['sentiment']['score'] for a in relevant_articles]
        avg_score = sum(scores) / len(scores)
        
        sentiments = [a['sentiment']['sentiment'] for a in relevant_articles]
        sentiment_counts = Counter(sentiments)
        
        # Overall sentiment
        if avg_score > 0.2:
            overall = "bullish"
        elif avg_score < -0.2:
            overall = "bearish"
        else:
            overall = "neutral"
        
        return {
            'topic': topic,
            'articles_found': len(relevant_articles),
            'sentiment': overall,
            'average_score': avg_score,
            'bullish_count': sentiment_counts.get('bullish', 0),
            'bearish_count': sentiment_counts.get('bearish', 0),
            'neutral_count': sentiment_counts.get('neutral', 0),
            'recent_articles': relevant_articles[:5]  # Top 5 most recent
        }
    
    def track_sentiment_over_time(self, topic: str):
        """
        Track sentiment changes over time for a topic.
        
        Args:
            topic: Topic to track
        """
        sentiment_data = self.get_sentiment(topic)
        
        timestamp = datetime.now().isoformat()
        
        if topic not in self.sentiment_history:
            self.sentiment_history[topic] = []
        
        self.sentiment_history[topic].append({
            'timestamp': timestamp,
            'average_score': sentiment_data['average_score'],
            'sentiment': sentiment_data['sentiment'],
            'article_count': sentiment_data['articles_found']
        })
        
        # Keep only last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        self.sentiment_history[topic] = [
            entry for entry in self.sentiment_history[topic]
            if datetime.fromisoformat(entry['timestamp']) >= cutoff
        ]
        
        self._save_sentiment_history()
    
    def detect_sentiment_shift(self, topic: str) -> Optional[Dict]:
        """
        Detect significant sentiment shifts for a topic.
        
        Args:
            topic: Topic to check
            
        Returns:
            Alert dictionary if shift detected, None otherwise
        """
        if topic not in self.sentiment_history or len(self.sentiment_history[topic]) < 2:
            return None
        
        history = self.sentiment_history[topic]
        recent = history[-1]
        previous = history[-2]
        
        score_change = recent['average_score'] - previous['average_score']
        threshold = self.alerts.get('sentiment_shift_threshold', 0.3)
        
        if abs(score_change) >= threshold:
            return {
                'type': 'sentiment_shift',
                'topic': topic,
                'previous_sentiment': previous['sentiment'],
                'current_sentiment': recent['sentiment'],
                'score_change': score_change,
                'timestamp': recent['timestamp']
            }
        
        return None
    
    def detect_major_news(self, article: Dict) -> Optional[Dict]:
        """
        Detect major news events based on keywords.
        
        Args:
            article: Article to check
            
        Returns:
            Alert dictionary if major news detected, None otherwise
        """
        major_keywords = self.alerts.get('major_keywords', [])
        text = f"{article['title']} {article['summary']}".lower()
        
        found_keywords = [kw for kw in major_keywords if kw in text]
        
        if found_keywords:
            return {
                'type': 'major_news',
                'title': article['title'],
                'keywords': found_keywords,
                'link': article['link'],
                'source': article['source'],
                'timestamp': article['fetched_at']
            }
        
        return None
    
    def correlate_with_price(self, market_id: str, price_history: List[Dict]) -> Dict:
        """
        Correlate news sentiment with price movements.
        
        Args:
            market_id: Market identifier
            price_history: List of {timestamp, price} dictionaries
            
        Returns:
            Correlation analysis
        """
        # This is a placeholder for price correlation logic
        # In a real implementation, you would:
        # 1. Align news timestamps with price data
        # 2. Calculate correlation coefficients
        # 3. Detect lead/lag relationships
        # 4. Identify news-driven vs organic moves
        
        sentiment_data = self.get_sentiment(market_id)
        
        return {
            'market_id': market_id,
            'current_sentiment': sentiment_data['sentiment'],
            'sentiment_score': sentiment_data['average_score'],
            'correlation_coefficient': 0.0,  # Placeholder
            'lead_lag_hours': 0,  # Placeholder
            'news_driven_percentage': 0.0,  # Placeholder
            'note': 'Price correlation requires historical price data integration'
        }
    
    def add_feed(self, name: str, url: str, category: str = "general"):
        """
        Add a new RSS feed.
        
        Args:
            name: Feed name
            url: RSS feed URL
            category: Feed category
        """
        feed = {
            'name': name,
            'url': url,
            'category': category,
            'enabled': True,
            'added_at': datetime.now().isoformat()
        }
        
        self.feeds.setdefault('feeds', []).append(feed)
        self._save_feeds()
        print(f"✓ Added feed: {name} ({category})")
    
    def list_sources(self):
        """Print all configured news sources."""
        feeds = self.feeds.get('feeds', [])
        
        if not feeds:
            print("No feeds configured. Run with --add-feed to add sources.")
            return
        
        print(f"\n📰 Configured News Sources ({len(feeds)} feeds):\n")
        
        by_category = defaultdict(list)
        for feed in feeds:
            by_category[feed.get('category', 'general')].append(feed)
        
        for category, category_feeds in sorted(by_category.items()):
            print(f"  {category.upper()}:")
            for feed in category_feeds:
                status = "✓" if feed.get('enabled', True) else "✗"
                print(f"    {status} {feed['name']}")
                print(f"      {feed['url']}")
            print()
    
    def configure_alerts(self):
        """Interactive alert configuration."""
        print("\n🔔 Alert Configuration\n")
        print(f"Current settings:")
        print(f"  Enabled: {self.alerts.get('enabled', True)}")
        print(f"  Sentiment shift threshold: {self.alerts.get('sentiment_shift_threshold', 0.3)}")
        print(f"  Volume threshold multiplier: {self.alerts.get('volume_threshold_multiplier', 2.0)}")
        print(f"  Major keywords: {', '.join(self.alerts.get('major_keywords', []))}")
        print()
        print("To modify, edit: news_data/alerts.json")


def print_summary(articles: List[Dict]):
    """Print a summary of articles."""
    if not articles:
        print("No articles found.")
        return
    
    print(f"\n📊 News Summary ({len(articles)} articles):\n")
    
    # Sentiment distribution
    sentiments = [a.get('sentiment', {}).get('sentiment', 'neutral') for a in articles]
    sentiment_counts = Counter(sentiments)
    
    print(f"Sentiment Distribution:")
    print(f"  🟢 Bullish: {sentiment_counts.get('bullish', 0)}")
    print(f"  🔴 Bearish: {sentiment_counts.get('bearish', 0)}")
    print(f"  ⚪ Neutral: {sentiment_counts.get('neutral', 0)}")
    print()
    
    # Average sentiment
    scores = [a.get('sentiment', {}).get('score', 0) for a in articles]
    avg_score = sum(scores) / len(scores) if scores else 0
    print(f"Average Sentiment Score: {avg_score:.3f} (-1 = bearish, +1 = bullish)")
    print()
    
    # Top entities
    all_markets = []
    for article in articles:
        all_markets.extend(article.get('entities', {}).get('markets', []))
    
    if all_markets:
        market_counts = Counter(all_markets)
        print("Most Mentioned:")
        for market, count in market_counts.most_common(5):
            print(f"  • {market}: {count} articles")
        print()
    
    # Recent headlines
    print("Recent Headlines:")
    for i, article in enumerate(articles[:10], 1):
        sentiment_emoji = {
            'bullish': '🟢',
            'bearish': '🔴',
            'neutral': '⚪'
        }.get(article.get('sentiment', {}).get('sentiment', 'neutral'), '⚪')
        
        print(f"  {i}. {sentiment_emoji} {article['title'][:80]}")
        print(f"     Source: {article['source']} | {article.get('published', 'N/A')}")
    print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="News Sentiment Analyzer for Polymarket Trading",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--market', type=str, help='Get news for specific market/topic')
    parser.add_argument('--sentiment', action='store_true', help='Show overall market sentiment')
    parser.add_argument('--sources', action='store_true', help='List configured news sources')
    parser.add_argument('--add-feed', type=str, help='Add RSS feed URL')
    parser.add_argument('--feed-name', type=str, help='Name for new feed')
    parser.add_argument('--feed-category', type=str, default='general', help='Category for new feed')
    parser.add_argument('--alerts', action='store_true', help='Configure alerts')
    parser.add_argument('--fetch', action='store_true', help='Fetch fresh articles from all feeds')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back (default: 24)')
    
    args = parser.parse_args()
    
    # Initialize sentiment tracker
    news = NewsSentiment()
    
    # Handle commands
    if args.sources:
        news.list_sources()
        return
    
    if args.add_feed:
        name = args.feed_name or input("Feed name: ")
        news.add_feed(name, args.add_feed, args.feed_category)
        return
    
    if args.alerts:
        news.configure_alerts()
        return
    
    # Fetch fresh articles if requested or cache is empty
    if args.fetch or not news.articles:
        print("Fetching articles from all feeds...")
        news.fetch_all_feeds()
    
    # Get recent articles
    articles = news.get_recent(hours=args.hours)
    
    # Process articles if not already processed
    articles = [news.process_article(a) if 'sentiment' not in a else a for a in articles]
    
    if args.market:
        # Market-specific sentiment
        sentiment_data = news.get_sentiment(args.market)
        
        print(f"\n📈 Sentiment Analysis: {args.market.upper()}\n")
        print(f"Articles Found: {sentiment_data['articles_found']}")
        print(f"Overall Sentiment: {sentiment_data['sentiment'].upper()}")
        print(f"Average Score: {sentiment_data['average_score']:.3f}")
        print(f"  🟢 Bullish: {sentiment_data['bullish_count']}")
        print(f"  🔴 Bearish: {sentiment_data['bearish_count']}")
        print(f"  ⚪ Neutral: {sentiment_data['neutral_count']}")
        
        if sentiment_data['recent_articles']:
            print(f"\nRecent Articles:")
            for i, article in enumerate(sentiment_data['recent_articles'], 1):
                sentiment_emoji = {
                    'bullish': '🟢',
                    'bearish': '🔴',
                    'neutral': '⚪'
                }.get(article['sentiment']['sentiment'], '⚪')
                print(f"  {i}. {sentiment_emoji} {article['title']}")
                print(f"     Score: {article['sentiment']['score']:.3f} | {article['source']}")
        print()
        
        # Track over time
        news.track_sentiment_over_time(args.market)
        
        # Check for sentiment shifts
        shift = news.detect_sentiment_shift(args.market)
        if shift:
            print(f"⚠️  SENTIMENT SHIFT DETECTED!")
            print(f"   {shift['previous_sentiment']} → {shift['current_sentiment']}")
            print(f"   Change: {shift['score_change']:+.3f}")
            print()
    
    elif args.sentiment:
        # Overall market sentiment
        print_summary(articles)
    
    else:
        # Default: today's summary
        print_summary(articles)


if __name__ == "__main__":
    main()
