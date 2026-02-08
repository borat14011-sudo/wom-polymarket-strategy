#!/usr/bin/env python3
"""
Generate Sample Data for Backtesting
Creates realistic synthetic prediction market data for testing

Usage: python generate-sample-data.py
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuration
DB_PATH = "polymarket_data.db"
NUM_MARKETS = 15
DAYS_HISTORY = 60
SNAPSHOTS_PER_DAY = 96  # Every 15 minutes

# Market templates
MARKET_TEMPLATES = [
    ("Bitcoin reaches $100,000 by end of year", "Crypto", 180),
    ("Ethereum ETF approved in Q1 2026", "Crypto", 90),
    ("Trump wins 2024 election", "Politics", 270),
    ("Fed cuts rates in March", "Economics", 60),
    ("Lakers win NBA championship", "Sports", 120),
    ("New GTA game releases this year", "Entertainment", 180),
    ("S&P 500 above 6000 by June", "Finance", 120),
    ("Dogecoin reaches $1", "Crypto", 150),
    ("Tesla reaches $500/share", "Finance", 90),
    ("New COVID variant causes lockdowns", "Health", 180),
    ("Major AI breakthrough announced", "Technology", 120),
    ("SpaceX lands on Mars", "Technology", 365),
    ("Apple releases AR glasses", "Technology", 180),
    ("Bitcoin dominance below 40%", "Crypto", 90),
    ("Recession declared in 2026", "Economics", 270),
]


def create_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Markets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS markets (
            market_id TEXT PRIMARY KEY,
            slug TEXT,
            question TEXT,
            description TEXT,
            category TEXT,
            token_id_yes TEXT,
            token_id_no TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            resolved INTEGER DEFAULT 0,
            resolution_outcome TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Snapshots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            price_yes REAL,
            price_no REAL,
            volume_24h REAL,
            liquidity REAL,
            best_bid_yes REAL,
            best_ask_yes REAL,
            best_bid_no REAL,
            best_ask_no REAL,
            spread REAL,
            FOREIGN KEY (market_id) REFERENCES markets(market_id),
            UNIQUE(market_id, timestamp)
        )
    ''')
    
    # Hype signals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hype_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tweet_count INTEGER,
            total_engagement INTEGER,
            velocity REAL,
            hype_score REAL,
            UNIQUE(market_id, timestamp)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_market_time ON snapshots(market_id, timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hype_market_time ON hype_signals(market_id, timestamp)')
    
    conn.commit()
    conn.close()
    print(f"✓ Database created: {DB_PATH}")


def generate_price_series(days: int, snapshots_per_day: int, 
                          initial_price: float = 0.5, 
                          volatility: float = 0.15,
                          trend: float = 0.0,
                          hype_events: list = None) -> pd.Series:
    """Generate realistic price series with optional hype events"""
    n_points = days * snapshots_per_day
    
    # Random walk with drift
    returns = np.random.normal(trend / n_points, volatility / np.sqrt(snapshots_per_day), n_points)
    
    # Add hype events (sudden spikes)
    if hype_events:
        for event_idx, spike_magnitude in hype_events:
            if event_idx < n_points:
                returns[event_idx] += spike_magnitude
                # Gradual decay after spike
                decay_period = min(20, n_points - event_idx)
                for i in range(1, decay_period):
                    returns[event_idx + i] -= spike_magnitude * 0.05
    
    # Convert to prices (bounded between 0.01 and 0.99)
    prices = initial_price * np.exp(np.cumsum(returns))
    prices = np.clip(prices, 0.01, 0.99)
    
    return pd.Series(prices)


def generate_volume_series(days: int, snapshots_per_day: int,
                           base_volume: float = 50000,
                           price_series: pd.Series = None) -> pd.Series:
    """Generate volume correlated with price movements"""
    n_points = days * snapshots_per_day
    
    # Base volume with random noise
    volumes = np.random.lognormal(np.log(base_volume), 0.5, n_points)
    
    # Increase volume during price spikes
    if price_series is not None:
        price_changes = np.abs(price_series.pct_change())
        volume_multiplier = 1 + (price_changes * 10)  # Volume spikes with price volatility
        volumes = volumes * volume_multiplier.fillna(1)
    
    return pd.Series(volumes)


def generate_hype_signals(days: int, snapshots_per_day: int,
                         volume_series: pd.Series,
                         correlation: float = 0.7) -> pd.DataFrame:
    """Generate Twitter hype signals correlated with volume"""
    n_points = days * snapshots_per_day
    
    # Base tweet counts
    base_tweets = np.random.poisson(5, n_points)
    
    # Correlate with volume
    volume_normalized = (volume_series - volume_series.mean()) / volume_series.std()
    correlated_component = volume_normalized * 10 * correlation
    
    tweet_counts = np.maximum(0, base_tweets + correlated_component.fillna(0)).astype(int)
    
    # Engagement
    engagement = tweet_counts * np.random.randint(10, 100, n_points)
    
    # Velocity (rate of change)
    velocity = pd.Series(tweet_counts).pct_change().fillna(0)
    
    # Hype score (composite)
    hype_score = (tweet_counts * 2 + engagement / 100 + velocity * 10)
    
    return pd.DataFrame({
        'tweet_count': tweet_counts,
        'total_engagement': engagement,
        'velocity': velocity,
        'hype_score': hype_score
    })


def insert_market_data():
    """Generate and insert sample data for multiple markets"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    start_date = datetime.now() - timedelta(days=DAYS_HISTORY)
    
    for i in range(NUM_MARKETS):
        question, category, days_to_expiry = random.choice(MARKET_TEMPLATES)
        
        market_id = f"market_{i+1:03d}"
        slug = question.lower().replace(" ", "-")[:50]
        end_time = start_date + timedelta(days=days_to_expiry)
        
        # Insert market
        cursor.execute('''
            INSERT INTO markets 
            (market_id, slug, question, category, token_id_yes, token_id_no, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            market_id, slug, question, f"{question[:100]}...", category,
            f"token_yes_{i+1}", f"token_no_{i+1}",
            start_date, end_time
        ))
        
        # Generate price series with 2-3 hype events
        num_hype_events = random.randint(2, 4)
        hype_events = [
            (random.randint(100, DAYS_HISTORY * SNAPSHOTS_PER_DAY - 100), 
             random.uniform(0.05, 0.15))
            for _ in range(num_hype_events)
        ]
        
        initial_price = random.uniform(0.3, 0.7)
        trend = random.uniform(-0.01, 0.01)
        volatility = random.uniform(0.1, 0.3)
        
        prices = generate_price_series(
            DAYS_HISTORY, SNAPSHOTS_PER_DAY,
            initial_price, volatility, trend, hype_events
        )
        
        # Generate volume
        base_volume = random.uniform(20000, 200000)
        volumes = generate_volume_series(DAYS_HISTORY, SNAPSHOTS_PER_DAY, base_volume, prices)
        
        # Generate hype signals
        hype_df = generate_hype_signals(DAYS_HISTORY, SNAPSHOTS_PER_DAY, volumes)
        
        # Insert snapshots
        timestamps = [start_date + timedelta(minutes=15*j) for j in range(len(prices))]
        
        for j, (ts, price, volume) in enumerate(zip(timestamps, prices, volumes)):
            spread = random.uniform(0.01, 0.04)
            liquidity = volume * random.uniform(0.5, 2.0)
            
            bid = price - spread/2
            ask = price + spread/2
            
            cursor.execute('''
                INSERT INTO snapshots
                (market_id, timestamp, price_yes, price_no, volume_24h, liquidity,
                 best_bid_yes, best_ask_yes, spread)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                market_id, ts, price, 1-price, volume, liquidity,
                bid, ask, spread
            ))
            
            # Insert hype signal (sample every hour to reduce size)
            if j % 4 == 0:
                cursor.execute('''
                    INSERT INTO hype_signals
                    (market_id, timestamp, tweet_count, total_engagement, velocity, hype_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    market_id, ts,
                    int(hype_df.iloc[j]['tweet_count']),
                    int(hype_df.iloc[j]['total_engagement']),
                    float(hype_df.iloc[j]['velocity']),
                    float(hype_df.iloc[j]['hype_score'])
                ))
        
        print(f"✓ Generated market {i+1}/{NUM_MARKETS}: {question[:50]}...")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Sample data generation complete!")
    print(f"  Markets: {NUM_MARKETS}")
    print(f"  Days: {DAYS_HISTORY}")
    print(f"  Snapshots per market: {DAYS_HISTORY * SNAPSHOTS_PER_DAY}")
    print(f"  Total snapshots: {NUM_MARKETS * DAYS_HISTORY * SNAPSHOTS_PER_DAY:,}")


def main():
    print("="*60)
    print("SAMPLE DATA GENERATOR")
    print("="*60)
    print(f"Generating {NUM_MARKETS} markets with {DAYS_HISTORY} days of history...")
    print()
    
    create_database()
    insert_market_data()
    
    print(f"\n✅ Database ready: {DB_PATH}")
    print("\nNow run: python backtest-engine.py --db polymarket_data.db")


if __name__ == '__main__':
    main()
