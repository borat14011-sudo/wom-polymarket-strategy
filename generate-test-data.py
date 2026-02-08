#!/usr/bin/env python3
"""
Generate synthetic test data for correlation-analyzer.py

Creates a SQLite database with realistic-looking but synthetic data
for testing the correlation analysis pipeline.

Usage:
    python generate-test-data.py --output test_data.db --markets 5 --days 30
"""

import argparse
import random
import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple

import numpy as np


class TestDataGenerator:
    """Generate synthetic market and hype data"""
    
    MARKET_TEMPLATES = [
        ("Will {person} announce candidacy by {date}?", "politics"),
        ("Will {crypto} reach ${price} by {date}?", "crypto"),
        ("Will {team} win the championship?", "sports"),
        ("Will {company} stock hit ${price} by {date}?", "finance"),
        ("Will {event} happen before {date}?", "world"),
    ]
    
    PEOPLE = ["Taylor Swift", "Elon Musk", "Joe Biden", "Donald Trump", "Kim Kardashian"]
    CRYPTOS = ["Bitcoin", "Ethereum", "Dogecoin", "Solana", "Cardano"]
    TEAMS = ["Lakers", "Warriors", "Celtics", "Heat", "Bucks"]
    COMPANIES = ["Apple", "Tesla", "Amazon", "Google", "Microsoft"]
    EVENTS = ["AI breakthrough", "Climate summit", "Tech IPO", "Space mission", "Elections"]
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_schema()
    
    def _create_schema(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Markets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS markets (
                market_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT
            )
        """)
        
        # Snapshots table (15-min price data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                yes_price REAL,
                no_price REAL,
                volume INTEGER,
                liquidity REAL
            )
        """)
        
        # Hype signals table (hourly)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hype_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_id TEXT NOT NULL,
                hour_timestamp DATETIME NOT NULL,
                tweet_count INTEGER DEFAULT 0,
                total_engagement INTEGER DEFAULT 0,
                unique_authors INTEGER DEFAULT 0,
                avg_sentiment REAL DEFAULT 0,
                high_follower_count INTEGER DEFAULT 0
            )
        """)
        
        self.conn.commit()
    
    def generate_market_title(self) -> Tuple[str, str]:
        """Generate random market title and category"""
        template, category = random.choice(self.MARKET_TEMPLATES)
        
        # Fill in template
        title = template.format(
            person=random.choice(self.PEOPLE),
            crypto=random.choice(self.CRYPTOS),
            team=random.choice(self.TEAMS),
            company=random.choice(self.COMPANIES),
            event=random.choice(self.EVENTS),
            price=random.randint(100, 10000),
            date=f"{random.choice(['March', 'April', 'May', 'June'])} {random.randint(1, 30)}"
        )
        
        return title, category
    
    def generate_price_series(
        self, 
        start_price: float,
        num_points: int,
        hype_influence: float,
        hype_lag: int,
        hype_events: List[Tuple[int, float]]
    ) -> np.ndarray:
        """
        Generate price time series with optional hype influence
        
        Args:
            start_price: Initial price (0-1)
            num_points: Number of data points
            hype_influence: How much hype affects price (0-1)
            hype_lag: Delay between hype and price response (in steps)
            hype_events: List of (time_index, hype_strength) tuples
        
        Returns:
            Array of prices
        """
        prices = np.zeros(num_points)
        prices[0] = start_price
        
        # Random walk component
        volatility = 0.01
        drift = 0.0001
        
        for t in range(1, num_points):
            # Base random walk
            change = drift + volatility * np.random.randn()
            
            # Add hype influence if applicable
            if hype_influence > 0 and t >= hype_lag:
                # Find hype events that should affect this time step
                for hype_time, hype_strength in hype_events:
                    if hype_time <= t - hype_lag and hype_time > t - hype_lag - 24:  # Effect lasts 24 periods
                        # Exponential decay
                        decay = np.exp(-0.1 * (t - hype_lag - hype_time))
                        change += hype_influence * hype_strength * decay
            
            # Update price
            prices[t] = np.clip(prices[t-1] + change, 0.01, 0.99)
        
        return prices
    
    def generate_hype_series(
        self,
        num_hours: int,
        base_level: float = 10.0,
        spike_probability: float = 0.05,
        spike_magnitude: Tuple[float, float] = (2.0, 5.0)
    ) -> Tuple[np.ndarray, List[Tuple[int, float]]]:
        """
        Generate hype metrics time series
        
        Returns:
            (tweet_counts, hype_events) where hype_events is list of (hour, magnitude)
        """
        tweet_counts = np.random.poisson(base_level, num_hours)
        hype_events = []
        
        # Add random spikes
        for i in range(num_hours):
            if random.random() < spike_probability:
                magnitude = random.uniform(*spike_magnitude)
                tweet_counts[i] = int(tweet_counts[i] * magnitude)
                hype_events.append((i, magnitude / spike_magnitude[1]))  # Normalized magnitude
        
        return tweet_counts, hype_events
    
    def generate_market(
        self,
        market_id: str,
        days: int,
        signal_type: str
    ) -> None:
        """
        Generate complete data for one market
        
        Args:
            market_id: Unique market identifier
            days: Number of days of data
            signal_type: 'strong', 'moderate', 'weak', 'none', or 'reverse'
        """
        title, category = self.generate_market_title()
        
        print(f"Generating {signal_type.upper()} signal market: {title}")
        
        # Configure based on signal type
        if signal_type == 'strong':
            hype_influence = 0.5
            hype_lag = random.randint(2, 6)  # 2-6 hours lag
            spike_prob = 0.08
        elif signal_type == 'moderate':
            hype_influence = 0.3
            hype_lag = random.randint(4, 12)
            spike_prob = 0.06
        elif signal_type == 'weak':
            hype_influence = 0.15
            hype_lag = random.randint(8, 24)
            spike_prob = 0.04
        elif signal_type == 'reverse':
            hype_influence = -0.3  # Negative influence (price leads hype)
            hype_lag = -4  # Negative lag
            spike_prob = 0.06
        else:  # 'none'
            hype_influence = 0.0
            hype_lag = 0
            spike_prob = 0.05
        
        # Generate time points
        start_time = datetime.now() - timedelta(days=days)
        num_hours = days * 24
        num_15min = num_hours * 4
        
        # Generate hype data (hourly)
        tweet_counts, hype_events = self.generate_hype_series(
            num_hours, 
            spike_probability=spike_prob
        )
        
        # For reverse causality, we need to generate price first, then hype
        if signal_type == 'reverse':
            # Generate price without hype influence
            prices_15min = self.generate_price_series(
                start_price=random.uniform(0.3, 0.7),
                num_points=num_15min,
                hype_influence=0.0,
                hype_lag=0,
                hype_events=[]
            )
            
            # Create price events (significant moves)
            price_events = []
            for i in range(1, num_15min):
                if abs(prices_15min[i] - prices_15min[i-1]) > 0.02:
                    hour_index = i // 4
                    price_events.append((hour_index, abs(prices_15min[i] - prices_15min[i-1]) * 20))
            
            # Now generate hype influenced by price events
            for hour, magnitude in price_events:
                if 0 <= hour < num_hours:
                    # Add hype spike after price movement
                    lag_hours = abs(hype_lag)
                    if hour + lag_hours < num_hours:
                        tweet_counts[hour + lag_hours] = int(tweet_counts[hour + lag_hours] * (1 + magnitude))
        else:
            # Normal case: hype influences price
            # Convert hourly hype events to 15-min indices
            hype_events_15min = [(h * 4, mag) for h, mag in hype_events]
            
            prices_15min = self.generate_price_series(
                start_price=random.uniform(0.3, 0.7),
                num_points=num_15min,
                hype_influence=hype_influence,
                hype_lag=hype_lag * 4,  # Convert hours to 15-min periods
                hype_events=hype_events_15min
            )
        
        # Insert market
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO markets (market_id, title, category) VALUES (?, ?, ?)",
            (market_id, title, category)
        )
        
        # Insert price snapshots (15-min)
        for i, price in enumerate(prices_15min):
            timestamp = start_time + timedelta(minutes=15*i)
            cursor.execute("""
                INSERT INTO snapshots 
                (market_id, timestamp, yes_price, no_price, volume, liquidity)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                market_id,
                timestamp.isoformat(),
                float(price),
                float(1 - price),
                random.randint(10, 1000),
                random.uniform(1000, 100000)
            ))
        
        # Insert hype signals (hourly)
        for hour, tweet_count in enumerate(tweet_counts):
            timestamp = start_time + timedelta(hours=hour)
            
            # Generate correlated engagement metrics
            engagement = int(tweet_count * random.uniform(5, 15))
            unique_authors = int(tweet_count * random.uniform(0.5, 0.9))
            sentiment = np.random.normal(0, 0.3)  # Slightly positive bias
            high_followers = int(tweet_count * random.uniform(0.1, 0.3))
            
            cursor.execute("""
                INSERT INTO hype_signals
                (market_id, hour_timestamp, tweet_count, total_engagement, 
                 unique_authors, avg_sentiment, high_follower_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                market_id,
                timestamp.isoformat(),
                int(tweet_count),
                engagement,
                unique_authors,
                float(sentiment),
                high_followers
            ))
        
        self.conn.commit()
    
    def generate_dataset(
        self,
        num_markets: int,
        days: int,
        strong_ratio: float = 0.2,
        moderate_ratio: float = 0.3,
        weak_ratio: float = 0.2,
        reverse_ratio: float = 0.1
    ):
        """
        Generate complete test dataset
        
        Args:
            num_markets: Total number of markets to generate
            days: Days of data per market
            strong_ratio: Proportion of strong signals
            moderate_ratio: Proportion of moderate signals
            weak_ratio: Proportion of weak signals
            reverse_ratio: Proportion of reverse causality cases
        """
        print(f"Generating test dataset with {num_markets} markets, {days} days each")
        print(f"Signal distribution:")
        print(f"  Strong: {int(num_markets * strong_ratio)}")
        print(f"  Moderate: {int(num_markets * moderate_ratio)}")
        print(f"  Weak: {int(num_markets * weak_ratio)}")
        print(f"  Reverse: {int(num_markets * reverse_ratio)}")
        print(f"  None: {num_markets - int(num_markets * (strong_ratio + moderate_ratio + weak_ratio + reverse_ratio))}")
        print()
        
        # Generate markets
        signal_types = (
            ['strong'] * int(num_markets * strong_ratio) +
            ['moderate'] * int(num_markets * moderate_ratio) +
            ['weak'] * int(num_markets * weak_ratio) +
            ['reverse'] * int(num_markets * reverse_ratio) +
            ['none'] * (num_markets - int(num_markets * (strong_ratio + moderate_ratio + weak_ratio + reverse_ratio)))
        )
        
        random.shuffle(signal_types)
        
        for i, signal_type in enumerate(signal_types, 1):
            market_id = f"TEST_{i:04d}"
            self.generate_market(market_id, days, signal_type)
        
        print(f"\n✓ Generated {num_markets} markets successfully")
    
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic test data for correlation analyzer"
    )
    
    parser.add_argument('--output', default='test_data.db',
                       help='Output database path (default: test_data.db)')
    parser.add_argument('--markets', type=int, default=10,
                       help='Number of markets to generate (default: 10)')
    parser.add_argument('--days', type=int, default=30,
                       help='Days of data per market (default: 30)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility (default: 42)')
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    np.random.seed(args.seed)
    
    # Generate data
    generator = TestDataGenerator(args.output)
    generator.generate_dataset(
        num_markets=args.markets,
        days=args.days
    )
    generator.close()
    
    print(f"\n✓ Test database created: {args.output}")
    print(f"\nYou can now run:")
    print(f"  python correlation-analyzer.py --db {args.output}")


if __name__ == "__main__":
    main()
