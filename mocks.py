"""
Mock Services for Polymarket Trading System Integration Tests

Provides mock implementations of:
- Polymarket API
- Twitter API
- Telegram Bot API
- Database (SQLite in-memory)
"""

import json
import time
import sqlite3
import threading
from typing import Dict, List, Any, Optional
from unittest.mock import MagicMock
from datetime import datetime, timedelta


class MockPolymarketAPI:
    """Mock Polymarket API with realistic responses"""
    
    def __init__(self, fail_mode: Optional[str] = None, latency_ms: int = 0):
        """
        Args:
            fail_mode: 'timeout', 'rate_limit', 'server_error', 'invalid_data', None
            latency_ms: Artificial latency to simulate network delay
        """
        self.fail_mode = fail_mode
        self.latency_ms = latency_ms
        self.request_count = 0
        self.rate_limit_threshold = 100
        
        # Mock market data
        self.markets = {
            "0x1234": {
                "id": "0x1234",
                "question": "Will Bitcoin reach $100k by end of 2024?",
                "end_date": "2024-12-31T23:59:59Z",
                "volume": 1500000,
                "liquidity": 500000,
                "yes_price": 0.65,
                "no_price": 0.35,
                "created_at": "2024-01-01T00:00:00Z"
            },
            "0x5678": {
                "id": "0x5678",
                "question": "Will Trump win 2024 election?",
                "end_date": "2024-11-05T23:59:59Z",
                "volume": 5000000,
                "liquidity": 2000000,
                "yes_price": 0.52,
                "no_price": 0.48,
                "created_at": "2023-06-01T00:00:00Z"
            },
            "0x9abc": {
                "id": "0x9abc",
                "question": "Will Apple release AI iPhone in 2024?",
                "end_date": "2024-12-31T23:59:59Z",
                "volume": 800000,
                "liquidity": 300000,
                "yes_price": 0.78,
                "no_price": 0.22,
                "created_at": "2024-02-15T00:00:00Z"
            }
        }
    
    def get_markets(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get list of markets"""
        self._simulate_latency()
        self._check_failure()
        
        markets_list = list(self.markets.values())
        return markets_list[offset:offset + limit]
    
    def get_market(self, market_id: str) -> Dict:
        """Get specific market by ID"""
        self._simulate_latency()
        self._check_failure()
        
        if market_id not in self.markets:
            raise ValueError(f"Market {market_id} not found")
        
        return self.markets[market_id]
    
    def get_market_trades(self, market_id: str, limit: int = 50) -> List[Dict]:
        """Get recent trades for a market"""
        self._simulate_latency()
        self._check_failure()
        
        # Generate mock trades
        trades = []
        base_time = datetime.now()
        for i in range(limit):
            trades.append({
                "trade_id": f"trade_{market_id}_{i}",
                "market_id": market_id,
                "side": "yes" if i % 2 == 0 else "no",
                "price": 0.5 + (i % 10) * 0.01,
                "amount": 100 * (i + 1),
                "timestamp": (base_time - timedelta(minutes=i)).isoformat()
            })
        return trades
    
    def _simulate_latency(self):
        """Simulate network latency"""
        if self.latency_ms > 0:
            time.sleep(self.latency_ms / 1000.0)
    
    def _check_failure(self):
        """Check if should fail based on fail_mode"""
        self.request_count += 1
        
        if self.fail_mode == 'timeout':
            raise TimeoutError("Request timed out")
        elif self.fail_mode == 'rate_limit':
            if self.request_count > self.rate_limit_threshold:
                raise Exception("Rate limit exceeded")
        elif self.fail_mode == 'server_error':
            if self.request_count % 3 == 0:  # Fail every 3rd request
                raise Exception("Internal server error (500)")
        elif self.fail_mode == 'invalid_data':
            return {"invalid": "malformed response"}


class MockTwitterAPI:
    """Mock Twitter/X API for sentiment analysis"""
    
    def __init__(self, fail_mode: Optional[str] = None):
        self.fail_mode = fail_mode
        self.request_count = 0
        
        # Mock tweet data
        self.tweets = {
            "bitcoin": [
                {"text": "Bitcoin to the moon! 🚀 #BTC", "likes": 1500, "retweets": 300, "timestamp": "2024-01-15T10:00:00Z"},
                {"text": "BTC looking bullish, expect $100k soon", "likes": 800, "retweets": 150, "timestamp": "2024-01-15T11:00:00Z"},
                {"text": "Bitcoin is dead, sell now!", "likes": 200, "retweets": 50, "timestamp": "2024-01-15T12:00:00Z"},
            ],
            "trump": [
                {"text": "Trump 2024! Best candidate!", "likes": 5000, "retweets": 1000, "timestamp": "2024-01-15T10:00:00Z"},
                {"text": "Trump polling well in swing states", "likes": 2000, "retweets": 400, "timestamp": "2024-01-15T11:00:00Z"},
            ],
            "apple": [
                {"text": "Apple AI iPhone rumors heating up", "likes": 3000, "retweets": 600, "timestamp": "2024-01-15T10:00:00Z"},
                {"text": "AAPL new AI features look amazing!", "likes": 1200, "retweets": 250, "timestamp": "2024-01-15T11:00:00Z"},
            ]
        }
    
    def search_tweets(self, query: str, limit: int = 100) -> List[Dict]:
        """Search tweets by query"""
        self._check_failure()
        
        # Simple keyword matching
        results = []
        for keyword, tweets in self.tweets.items():
            if keyword.lower() in query.lower():
                results.extend(tweets[:limit])
        
        return results
    
    def get_trending_topics(self) -> List[str]:
        """Get trending topics"""
        self._check_failure()
        return ["Bitcoin", "Trump", "Apple", "AI", "Crypto"]
    
    def _check_failure(self):
        """Check if should fail"""
        self.request_count += 1
        
        if self.fail_mode == 'timeout':
            raise TimeoutError("Twitter API timeout")
        elif self.fail_mode == 'rate_limit':
            if self.request_count > 10:
                raise Exception("Rate limit exceeded (429)")


class MockTelegramBot:
    """Mock Telegram Bot API"""
    
    def __init__(self, fail_mode: Optional[str] = None):
        self.fail_mode = fail_mode
        self.sent_messages = []
        self.request_count = 0
    
    def send_message(self, chat_id: str, text: str, **kwargs) -> Dict:
        """Send a message"""
        self._check_failure()
        
        message = {
            "message_id": len(self.sent_messages) + 1,
            "chat_id": chat_id,
            "text": text,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self.sent_messages.append(message)
        return message
    
    def get_sent_messages(self) -> List[Dict]:
        """Get all sent messages (for testing)"""
        return self.sent_messages
    
    def clear_messages(self):
        """Clear message history"""
        self.sent_messages = []
    
    def _check_failure(self):
        """Check if should fail"""
        self.request_count += 1
        
        if self.fail_mode == 'network_error':
            raise ConnectionError("Failed to connect to Telegram")


class MockDatabase:
    """Mock database using SQLite in-memory"""
    
    def __init__(self, fail_mode: Optional[str] = None):
        self.fail_mode = fail_mode
        self.connection = None
        self.cursor = None
        self.is_connected = False
        self._lock = threading.Lock()
        self.query_count = 0
        self.query_times = []
    
    def connect(self):
        """Connect to database"""
        if self.fail_mode == 'connection_error':
            raise ConnectionError("Failed to connect to database")
        
        self.connection = sqlite3.connect(':memory:', check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.is_connected = True
        self._create_tables()
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
        self.is_connected = False
    
    def _create_tables(self):
        """Create database tables"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS markets (
                id TEXT PRIMARY KEY,
                question TEXT,
                end_date TEXT,
                volume REAL,
                liquidity REAL,
                yes_price REAL,
                no_price REAL,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_id TEXT,
                signal_type TEXT,
                confidence REAL,
                price REAL,
                reason TEXT,
                created_at TEXT,
                FOREIGN KEY (market_id) REFERENCES markets(id)
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS hype_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_id TEXT,
                keyword TEXT,
                tweet_count INTEGER,
                sentiment_score REAL,
                hype_score REAL,
                created_at TEXT,
                FOREIGN KEY (market_id) REFERENCES markets(id)
            )
        """)
        
        self.connection.commit()
    
    def insert_market(self, market_data: Dict) -> bool:
        """Insert market data"""
        start_time = time.time()
        self._check_failure()
        
        with self._lock:
            try:
                self.cursor.execute("""
                    INSERT OR REPLACE INTO markets 
                    (id, question, end_date, volume, liquidity, yes_price, no_price, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    market_data.get('id'),
                    market_data.get('question'),
                    market_data.get('end_date'),
                    market_data.get('volume'),
                    market_data.get('liquidity'),
                    market_data.get('yes_price'),
                    market_data.get('no_price'),
                    market_data.get('created_at'),
                    datetime.now().isoformat()
                ))
                self.connection.commit()
                self._record_query_time(time.time() - start_time)
                return True
            except Exception as e:
                self.connection.rollback()
                raise e
    
    def insert_signal(self, signal_data: Dict) -> int:
        """Insert signal data"""
        start_time = time.time()
        self._check_failure()
        
        with self._lock:
            self.cursor.execute("""
                INSERT INTO signals 
                (market_id, signal_type, confidence, price, reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                signal_data.get('market_id'),
                signal_data.get('signal_type'),
                signal_data.get('confidence'),
                signal_data.get('price'),
                signal_data.get('reason'),
                datetime.now().isoformat()
            ))
            self.connection.commit()
            self._record_query_time(time.time() - start_time)
            return self.cursor.lastrowid
    
    def insert_hype_score(self, hype_data: Dict) -> int:
        """Insert hype score data"""
        start_time = time.time()
        self._check_failure()
        
        with self._lock:
            self.cursor.execute("""
                INSERT INTO hype_scores 
                (market_id, keyword, tweet_count, sentiment_score, hype_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                hype_data.get('market_id'),
                hype_data.get('keyword'),
                hype_data.get('tweet_count'),
                hype_data.get('sentiment_score'),
                hype_data.get('hype_score'),
                datetime.now().isoformat()
            ))
            self.connection.commit()
            self._record_query_time(time.time() - start_time)
            return self.cursor.lastrowid
    
    def get_markets(self, limit: int = 100) -> List[Dict]:
        """Get all markets"""
        start_time = time.time()
        self._check_failure()
        
        with self._lock:
            self.cursor.execute(f"SELECT * FROM markets LIMIT ?", (limit,))
            rows = self.cursor.fetchall()
            self._record_query_time(time.time() - start_time)
            
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def get_signals(self, market_id: Optional[str] = None) -> List[Dict]:
        """Get signals, optionally filtered by market_id"""
        start_time = time.time()
        self._check_failure()
        
        with self._lock:
            if market_id:
                self.cursor.execute("SELECT * FROM signals WHERE market_id = ?", (market_id,))
            else:
                self.cursor.execute("SELECT * FROM signals")
            
            rows = self.cursor.fetchall()
            self._record_query_time(time.time() - start_time)
            
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def get_hype_scores(self, market_id: Optional[str] = None) -> List[Dict]:
        """Get hype scores"""
        start_time = time.time()
        self._check_failure()
        
        with self._lock:
            if market_id:
                self.cursor.execute("SELECT * FROM hype_scores WHERE market_id = ?", (market_id,))
            else:
                self.cursor.execute("SELECT * FROM hype_scores")
            
            rows = self.cursor.fetchall()
            self._record_query_time(time.time() - start_time)
            
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def get_performance_stats(self) -> Dict:
        """Get database performance statistics"""
        if not self.query_times:
            return {
                "total_queries": 0,
                "avg_query_time_ms": 0,
                "min_query_time_ms": 0,
                "max_query_time_ms": 0
            }
        
        return {
            "total_queries": self.query_count,
            "avg_query_time_ms": sum(self.query_times) / len(self.query_times) * 1000,
            "min_query_time_ms": min(self.query_times) * 1000,
            "max_query_time_ms": max(self.query_times) * 1000
        }
    
    def _record_query_time(self, duration: float):
        """Record query execution time"""
        self.query_count += 1
        self.query_times.append(duration)
    
    def _check_failure(self):
        """Check if should fail"""
        if self.fail_mode == 'query_error':
            if self.query_count > 0 and self.query_count % 5 == 0:
                raise sqlite3.OperationalError("Database locked")


class MockRiskManager:
    """Mock Risk Manager for signal validation"""
    
    def __init__(self, max_exposure: float = 10000, max_position_size: float = 5000):
        self.max_exposure = max_exposure
        self.max_position_size = max_position_size
        self.current_exposure = 0
        self.positions = {}
    
    def validate_signal(self, signal: Dict) -> Dict:
        """
        Validate a trading signal against risk rules
        
        Returns:
            {
                "approved": bool,
                "reason": str,
                "adjusted_size": float (optional)
            }
        """
        market_id = signal.get('market_id')
        signal_type = signal.get('signal_type')
        confidence = signal.get('confidence', 0)
        suggested_size = signal.get('size', 1000)
        
        # Rule 1: Minimum confidence threshold
        if confidence < 0.6:
            return {
                "approved": False,
                "reason": f"Confidence {confidence} below threshold 0.6"
            }
        
        # Rule 2: Max position size
        if suggested_size > self.max_position_size:
            return {
                "approved": True,
                "adjusted_size": self.max_position_size,
                "reason": f"Position size reduced from {suggested_size} to {self.max_position_size}"
            }
        
        # Rule 3: Max total exposure
        if self.current_exposure + suggested_size > self.max_exposure:
            remaining = self.max_exposure - self.current_exposure
            if remaining <= 0:
                return {
                    "approved": False,
                    "reason": "Max exposure reached"
                }
            return {
                "approved": True,
                "adjusted_size": remaining,
                "reason": f"Position size reduced to stay within exposure limit"
            }
        
        # All checks passed
        return {
            "approved": True,
            "reason": "Signal passed all risk checks"
        }
    
    def add_position(self, market_id: str, size: float):
        """Add a position (for testing)"""
        self.positions[market_id] = size
        self.current_exposure += size
    
    def reset(self):
        """Reset risk manager state"""
        self.current_exposure = 0
        self.positions = {}


# Utility functions for test data generation
def generate_mock_market(market_id: str = None, **kwargs) -> Dict:
    """Generate a mock market with customizable fields"""
    market_id = market_id or f"0x{hash(time.time()) % 10000:04x}"
    
    defaults = {
        "id": market_id,
        "question": f"Test market question {market_id}?",
        "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "volume": 1000000,
        "liquidity": 500000,
        "yes_price": 0.5,
        "no_price": 0.5,
        "created_at": datetime.now().isoformat()
    }
    
    defaults.update(kwargs)
    return defaults


def generate_mock_signal(market_id: str, **kwargs) -> Dict:
    """Generate a mock signal"""
    defaults = {
        "market_id": market_id,
        "signal_type": "BUY",
        "confidence": 0.75,
        "price": 0.5,
        "size": 1000,
        "reason": "Test signal"
    }
    
    defaults.update(kwargs)
    return defaults


def generate_mock_tweets(keyword: str, count: int = 10, sentiment: str = "positive") -> List[Dict]:
    """Generate mock tweets"""
    tweets = []
    
    sentiment_texts = {
        "positive": [f"{keyword} is great!", f"Bullish on {keyword}", f"{keyword} to the moon!"],
        "negative": [f"{keyword} is terrible", f"Bearish on {keyword}", f"{keyword} will fail"],
        "neutral": [f"{keyword} update", f"News about {keyword}", f"{keyword} analysis"]
    }
    
    texts = sentiment_texts.get(sentiment, sentiment_texts["neutral"])
    
    for i in range(count):
        tweets.append({
            "text": texts[i % len(texts)],
            "likes": 100 * (i + 1),
            "retweets": 20 * (i + 1),
            "timestamp": (datetime.now() - timedelta(minutes=i)).isoformat()
        })
    
    return tweets
