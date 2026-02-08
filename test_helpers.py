"""
Test Helpers - Mock Data Generators for Polymarket Trading System
Generates realistic price series, hype signals, and tweets for testing
"""

import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class MockDataGenerator:
    """Generate realistic mock data for testing"""
    
    @staticmethod
    def generate_price_series(
        length: int = 100,
        start_price: float = 0.5,
        volatility: float = 0.05,
        trend: float = 0.0
    ) -> List[Tuple[float, float]]:
        """
        Generate realistic price series with volume
        
        Args:
            length: Number of data points
            start_price: Starting price (0-1 range)
            volatility: Price volatility (standard deviation)
            trend: Upward/downward trend (-1 to 1)
        
        Returns:
            List of (timestamp, price) tuples
        """
        prices = []
        current_price = start_price
        base_time = time.time() - (length * 60)  # 1 minute intervals
        
        for i in range(length):
            # Random walk with trend
            change = random.gauss(trend * 0.001, volatility)
            current_price = max(0.01, min(0.99, current_price + change))
            
            timestamp = base_time + (i * 60)
            prices.append((timestamp, current_price))
        
        return prices
    
    @staticmethod
    def generate_volume_series(
        length: int = 100,
        base_volume: float = 10000,
        volatility: float = 0.3
    ) -> List[Tuple[float, float]]:
        """
        Generate realistic volume series
        
        Args:
            length: Number of data points
            base_volume: Average volume
            volatility: Volume volatility
        
        Returns:
            List of (timestamp, volume) tuples
        """
        volumes = []
        base_time = time.time() - (length * 60)
        
        for i in range(length):
            # Log-normal distribution for volume
            volume = base_volume * random.lognormvariate(0, volatility)
            timestamp = base_time + (i * 60)
            volumes.append((timestamp, volume))
        
        return volumes
    
    @staticmethod
    def generate_hype_signals(
        length: int = 50,
        intensity: str = 'medium'
    ) -> List[Dict]:
        """
        Generate realistic hype signals (social media mentions)
        
        Args:
            length: Number of signals
            intensity: 'low', 'medium', 'high' - affects frequency and sentiment
        
        Returns:
            List of hype signal dictionaries
        """
        intensity_map = {
            'low': (0.3, 0.5),
            'medium': (0.5, 0.7),
            'high': (0.7, 0.9)
        }
        
        min_sentiment, max_sentiment = intensity_map.get(intensity, (0.5, 0.7))
        signals = []
        base_time = time.time() - (length * 300)  # 5 minute intervals
        
        for i in range(length):
            signal = {
                'timestamp': base_time + (i * 300) + random.randint(-60, 60),
                'sentiment': random.uniform(min_sentiment, max_sentiment),
                'volume': random.randint(1, 100),
                'source': random.choice(['twitter', 'reddit', 'discord', 'telegram'])
            }
            signals.append(signal)
        
        return signals
    
    @staticmethod
    def generate_tweets(
        count: int = 20,
        market_keyword: str = 'BTC'
    ) -> List[Dict]:
        """
        Generate realistic tweet data
        
        Args:
            count: Number of tweets
            market_keyword: Keyword to include in tweets
        
        Returns:
            List of tweet dictionaries
        """
        positive_templates = [
            f"{market_keyword} looking bullish! 🚀",
            f"Big moves incoming for {market_keyword}",
            f"{market_keyword} breaking out! 📈",
            f"Loving the {market_keyword} action today",
            f"{market_keyword} to the moon!"
        ]
        
        negative_templates = [
            f"{market_keyword} looking weak...",
            f"Concerned about {market_keyword} here",
            f"{market_keyword} showing bearish signals 📉",
            f"Time to exit {market_keyword}?",
            f"{market_keyword} losing momentum"
        ]
        
        neutral_templates = [
            f"Watching {market_keyword} closely",
            f"{market_keyword} consolidating",
            f"What's everyone's take on {market_keyword}?",
            f"{market_keyword} update",
            f"Thoughts on {market_keyword}?"
        ]
        
        tweets = []
        base_time = time.time() - (count * 600)  # 10 minute intervals
        
        for i in range(count):
            sentiment_type = random.choice(['positive', 'negative', 'neutral'])
            
            if sentiment_type == 'positive':
                text = random.choice(positive_templates)
                sentiment = random.uniform(0.6, 1.0)
            elif sentiment_type == 'negative':
                text = random.choice(negative_templates)
                sentiment = random.uniform(0.0, 0.4)
            else:
                text = random.choice(neutral_templates)
                sentiment = random.uniform(0.4, 0.6)
            
            tweet = {
                'id': f'tweet_{i}_{random.randint(1000, 9999)}',
                'text': text,
                'timestamp': base_time + (i * 600) + random.randint(-120, 120),
                'sentiment': sentiment,
                'retweets': random.randint(0, 500),
                'likes': random.randint(0, 2000),
                'author': f'user_{random.randint(1, 100)}'
            }
            tweets.append(tweet)
        
        return tweets
    
    @staticmethod
    def generate_market_data(market_id: str = None) -> Dict:
        """
        Generate realistic market metadata
        
        Args:
            market_id: Optional market ID, generates random if None
        
        Returns:
            Market data dictionary
        """
        if market_id is None:
            market_id = f"market_{random.randint(1000, 9999)}"
        
        return {
            'market_id': market_id,
            'question': f"Will event {market_id} occur?",
            'end_date': (datetime.now() + timedelta(days=random.randint(1, 90))).isoformat(),
            'volume': random.uniform(10000, 1000000),
            'liquidity': random.uniform(5000, 500000),
            'category': random.choice(['crypto', 'politics', 'sports', 'entertainment']),
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        }
    
    @staticmethod
    def generate_correlation_data(
        length: int = 100,
        correlation: float = 0.7,
        lag: int = 0
    ) -> Tuple[List[float], List[float]]:
        """
        Generate two correlated time series with optional lag
        
        Args:
            length: Number of data points
            correlation: Correlation coefficient (-1 to 1)
            lag: Time lag in periods
        
        Returns:
            Tuple of (series1, series2)
        """
        # Generate first series
        series1 = [random.gauss(0, 1) for _ in range(length)]
        
        # Generate correlated second series
        series2 = []
        for i in range(length):
            if i < lag:
                # Before lag, uncorrelated
                series2.append(random.gauss(0, 1))
            else:
                # After lag, correlated with series1
                correlated_value = (
                    correlation * series1[i - lag] + 
                    (1 - abs(correlation)) * random.gauss(0, 1)
                )
                series2.append(correlated_value)
        
        return series1, series2


class MockDatabase:
    """In-memory mock database for testing"""
    
    def __init__(self):
        self.tables = {
            'prices': [],
            'signals': [],
            'trades': [],
            'hype': []
        }
        self.indexes = set()
    
    def insert(self, table: str, data: Dict) -> bool:
        """Insert data into table"""
        if table not in self.tables:
            return False
        self.tables[table].append(data.copy())
        return True
    
    def batch_insert(self, table: str, data_list: List[Dict]) -> int:
        """Batch insert multiple records"""
        if table not in self.tables:
            return 0
        count = 0
        for data in data_list:
            if self.insert(table, data):
                count += 1
        return count
    
    def query(self, table: str, conditions: Dict = None) -> List[Dict]:
        """Query table with optional conditions"""
        if table not in self.tables:
            return []
        
        results = self.tables[table]
        
        if conditions:
            filtered = []
            for row in results:
                match = True
                for key, value in conditions.items():
                    if row.get(key) != value:
                        match = False
                        break
                if match:
                    filtered.append(row)
            results = filtered
        
        return results
    
    def update(self, table: str, conditions: Dict, updates: Dict) -> int:
        """Update records matching conditions"""
        if table not in self.tables:
            return 0
        
        count = 0
        for row in self.tables[table]:
            match = True
            for key, value in conditions.items():
                if row.get(key) != value:
                    match = False
                    break
            if match:
                row.update(updates)
                count += 1
        
        return count
    
    def create_index(self, table: str, column: str) -> bool:
        """Create index (simulated)"""
        index_name = f"{table}.{column}"
        self.indexes.add(index_name)
        return True
    
    def has_index(self, table: str, column: str) -> bool:
        """Check if index exists"""
        index_name = f"{table}.{column}"
        return index_name in self.indexes
    
    def clear(self):
        """Clear all data"""
        for table in self.tables:
            self.tables[table].clear()
        self.indexes.clear()


def validate_price(price: float) -> bool:
    """Validate price is in valid range (0-1)"""
    return 0.0 <= price <= 1.0


def validate_timestamp(timestamp: float) -> bool:
    """Validate timestamp is reasonable"""
    # Check if timestamp is within reasonable range (not too far in past/future)
    now = time.time()
    one_year = 365 * 24 * 3600
    return (now - one_year) <= timestamp <= (now + one_year)


def validate_market_id(market_id: str) -> bool:
    """Validate market ID format"""
    if not isinstance(market_id, str):
        return False
    if len(market_id) < 5 or len(market_id) > 100:
        return False
    # Should contain alphanumeric and some special chars
    return all(c.isalnum() or c in '_-.' for c in market_id)
