#!/usr/bin/env python3
"""
Twitter Hype Monitor - MVP Version
Monitors X/Twitter for prediction market hype using free snscrape

Usage: python twitter-hype-monitor.py
Run as cron job: */15 * * * * python /path/to/twitter-hype-monitor.py
"""

import subprocess
import json
import sqlite3
from datetime import datetime, timedelta
import re
from collections import defaultdict

# Configuration
DB_PATH = "polymarket_data.db"

# Keywords to monitor
KEYWORDS = [
    "polymarket.com",
    "#Polymarket",
    "prediction market bet",
    "manifold.markets",
    "kalshi",
]

# Sentiment lexicon (simple version - can upgrade to VADER)
POSITIVE_WORDS = ["printing", "free money", "easy money", "locked in", "🚀", "📈", "bullish", "great bet"]
NEGATIVE_WORDS = ["losing", "scam", "rigged", "terrible", "📉", "bearish", "bad bet"]

class TwitterHypeMonitor:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize tweets table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tweets (
                tweet_id TEXT PRIMARY KEY,
                timestamp TIMESTAMP,
                text TEXT,
                author_username TEXT,
                author_id TEXT,
                likes INTEGER DEFAULT 0,
                retweets INTEGER DEFAULT 0,
                replies INTEGER DEFAULT 0,
                engagement_score INTEGER,
                sentiment_score REAL,
                market_id TEXT,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Hype signals table (aggregated metrics per market)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hype_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tweet_count INTEGER,
                total_engagement INTEGER,
                avg_sentiment REAL,
                unique_users INTEGER,
                velocity REAL,
                hype_score REAL,
                UNIQUE(market_id, timestamp)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Database initialized: {self.db_path}")
    
    def check_snscrape(self):
        """Check if snscrape is installed"""
        try:
            subprocess.run(["snscrape", "--version"], capture_output=True, check=True)
            return True
        except:
            print("✗ snscrape not installed. Install: pip install snscrape")
            return False
    
    def scrape_tweets(self, query, since_hours=1):
        """Scrape tweets using snscrape"""
        if not self.check_snscrape():
            return []
        
        since_date = (datetime.now() - timedelta(hours=since_hours)).strftime("%Y-%m-%d")
        
        # Build snscrape command
        cmd = [
            "snscrape",
            "--jsonl",
            "--max-results", "1000",
            "twitter-search",
            f"{query} since:{since_date} lang:en -filter:retweets"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"✗ snscrape error: {result.stderr}")
                return []
            
            # Parse JSONL output
            tweets = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        tweet = json.loads(line)
                        tweets.append(tweet)
                    except json.JSONDecodeError:
                        continue
            
            return tweets
            
        except subprocess.TimeoutExpired:
            print("✗ snscrape timeout")
            return []
        except Exception as e:
            print(f"✗ Error scraping tweets: {e}")
            return []
    
    def calculate_sentiment(self, text):
        """Simple sentiment scoring (can upgrade to VADER)"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in POSITIVE_WORDS if word.lower() in text_lower)
        negative_count = sum(1 for word in NEGATIVE_WORDS if word.lower() in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0  # Neutral
        
        sentiment = (positive_count - negative_count) / (positive_count + negative_count)
        return sentiment
    
    def extract_market_mentions(self, text):
        """Extract potential market mentions from tweet"""
        # Look for common patterns
        patterns = [
            r'polymarket\.com/event/([a-z0-9-]+)',
            r'bet on (.+?) at',
            r'market for (.+?)[\.\!]',
        ]
        
        mentions = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            mentions.extend(matches)
        
        return mentions
    
    def match_to_market(self, tweet_text):
        """Try to match tweet to a market in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all active markets
        cursor.execute('SELECT market_id, question FROM markets WHERE resolved = 0')
        markets = cursor.fetchall()
        conn.close()
        
        # Simple keyword matching (can be improved with NLP)
        tweet_lower = tweet_text.lower()
        for market_id, question in markets:
            question_lower = question.lower()
            
            # Extract key terms from question
            key_terms = [word for word in question_lower.split() if len(word) > 4]
            
            # Check if multiple key terms appear in tweet
            matches = sum(1 for term in key_terms[:5] if term in tweet_lower)
            if matches >= 2:
                return market_id
        
        return None
    
    def save_tweet(self, tweet, market_id=None):
        """Save tweet to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        text = tweet.get("content", "")
        sentiment = self.calculate_sentiment(text)
        
        likes = tweet.get("likeCount", 0)
        retweets = tweet.get("retweetCount", 0)
        replies = tweet.get("replyCount", 0)
        engagement = likes + retweets * 2 + replies
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO tweets
                (tweet_id, timestamp, text, author_username, author_id,
                 likes, retweets, replies, engagement_score, sentiment_score, market_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(tweet.get("id")),
                tweet.get("date"),
                text[:500],  # Truncate long tweets
                tweet.get("user", {}).get("username"),
                str(tweet.get("user", {}).get("id")),
                likes,
                retweets,
                replies,
                engagement,
                sentiment,
                market_id
            ))
            conn.commit()
        except Exception as e:
            print(f"✗ Error saving tweet: {e}")
        finally:
            conn.close()
    
    def calculate_hype_signals(self):
        """Calculate aggregate hype signals per market"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get tweets from last hour, grouped by market
        cursor.execute('''
            SELECT 
                market_id,
                COUNT(*) as tweet_count,
                SUM(engagement_score) as total_engagement,
                AVG(sentiment_score) as avg_sentiment,
                COUNT(DISTINCT author_id) as unique_users
            FROM tweets
            WHERE timestamp > datetime('now', '-1 hour')
              AND market_id IS NOT NULL
            GROUP BY market_id
        ''')
        
        signals = cursor.fetchall()
        
        for signal in signals:
            market_id, count, engagement, sentiment, unique_users = signal
            
            # Get previous hour's count for velocity calculation
            cursor.execute('''
                SELECT COUNT(*) FROM tweets
                WHERE market_id = ?
                  AND timestamp BETWEEN datetime('now', '-2 hours') AND datetime('now', '-1 hour')
            ''', (market_id,))
            prev_count = cursor.fetchone()[0]
            
            velocity = (count - prev_count) / max(prev_count, 1) if prev_count > 0 else 0
            
            # Calculate composite hype score (simplified)
            # Real version would be more sophisticated (see TWITTER-SENTIMENT-TRACKING.md)
            volume_score = min(count / 10, 20)  # Max 20 points
            engagement_score = min(engagement / 1000, 25)  # Max 25 points
            velocity_score = min(velocity * 10, 10)  # Max 10 points
            sentiment_score = (sentiment + 1) * 10  # 0-20 points
            diversity_score = min(unique_users / count if count > 0 else 0, 1) * 10  # Max 10 points
            
            hype_score = volume_score + engagement_score + velocity_score + sentiment_score + diversity_score
            
            # Save signal
            try:
                cursor.execute('''
                    INSERT INTO hype_signals
                    (market_id, tweet_count, total_engagement, avg_sentiment, 
                     unique_users, velocity, hype_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (market_id, count, engagement or 0, sentiment or 0, unique_users, velocity, hype_score))
            except sqlite3.IntegrityError:
                # Duplicate - update instead
                cursor.execute('''
                    UPDATE hype_signals
                    SET tweet_count = ?, total_engagement = ?, avg_sentiment = ?,
                        unique_users = ?, velocity = ?, hype_score = ?
                    WHERE market_id = ? AND timestamp = (
                        SELECT MAX(timestamp) FROM hype_signals WHERE market_id = ?
                    )
                ''', (count, engagement or 0, sentiment or 0, unique_users, velocity, hype_score, market_id, market_id))
        
        conn.commit()
        conn.close()
        
        return len(signals)
    
    def run(self):
        """Main monitoring loop"""
        print(f"\n{'='*60}")
        print(f"Twitter Hype Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        all_tweets = []
        
        # Scrape for each keyword
        for keyword in KEYWORDS:
            print(f"📊 Scraping: {keyword}")
            tweets = self.scrape_tweets(keyword, since_hours=1)
            all_tweets.extend(tweets)
            print(f"   Found {len(tweets)} tweets")
        
        if not all_tweets:
            print("\n✗ No tweets found")
            return
        
        # Remove duplicates
        unique_tweets = {t.get("id"): t for t in all_tweets}.values()
        print(f"\n✓ Total unique tweets: {len(unique_tweets)}")
        
        # Process tweets
        matched_count = 0
        for tweet in unique_tweets:
            text = tweet.get("content", "")
            
            # Try to match to a market
            market_id = self.match_to_market(text)
            if market_id:
                matched_count += 1
            
            # Save tweet
            self.save_tweet(tweet, market_id)
        
        print(f"✓ Matched {matched_count} tweets to markets")
        
        # Calculate hype signals
        signal_count = self.calculate_hype_signals()
        print(f"✓ Generated {signal_count} hype signals")
        
        # Show top hype markets
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.question, h.hype_score, h.tweet_count, h.velocity
            FROM hype_signals h
            JOIN markets m ON h.market_id = m.market_id
            WHERE h.timestamp > datetime('now', '-1 hour')
            ORDER BY h.hype_score DESC
            LIMIT 5
        ''')
        
        top_markets = cursor.fetchall()
        conn.close()
        
        if top_markets:
            print(f"\n🔥 TOP HYPE MARKETS:")
            for i, (question, score, count, velocity) in enumerate(top_markets, 1):
                print(f"   {i}. [{score:.1f}] {question[:50]}... | Tweets: {count} | Velocity: {velocity:+.1%}")
        
        print(f"\n{'='*60}\n")

if __name__ == "__main__":
    monitor = TwitterHypeMonitor()
    monitor.run()
