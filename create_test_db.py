#!/usr/bin/env python3
"""Create test database with sample data and intentional quality issues."""

import sqlite3
import random
from datetime import datetime, timedelta

db_path = 'polymarket_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create markets table
cursor.execute('''
CREATE TABLE IF NOT EXISTS markets (
    market_id TEXT PRIMARY KEY,
    title TEXT,
    category TEXT,
    created_at INTEGER
)
''')

# Create market_snapshots table
cursor.execute('''
CREATE TABLE IF NOT EXISTS market_snapshots (
    market_id TEXT,
    timestamp INTEGER,
    price REAL,
    volume REAL,
    PRIMARY KEY (market_id, timestamp)
)
''')

# Create tweets table
cursor.execute('''
CREATE TABLE IF NOT EXISTS tweets (
    tweet_id TEXT PRIMARY KEY,
    market_id TEXT,
    user TEXT,
    text TEXT,
    timestamp INTEGER
)
''')

print("Creating test data...")

# Insert markets
markets = [
    ('TRUMP2024', 'Will Trump win 2024?', 'politics'),
    ('BTC100K', 'Bitcoin over $100k in 2024?', 'crypto'),
    ('AI-AGI', 'AGI by 2025?', 'technology'),
    ('RECESSION', 'US Recession in 2024?', 'economics'),
    ('SPORTS-NBA', 'Lakers win championship?', 'sports')
]

base_time = datetime.now().timestamp()

for market_id, title, category in markets:
    cursor.execute('INSERT INTO markets VALUES (?, ?, ?, ?)',
                  (market_id, title, category, int(base_time - 86400*30)))

# Insert snapshots with various quality issues
snapshot_count = 0

for market_id, _, _ in markets:
    price = random.uniform(0.3, 0.7)
    volume = random.uniform(10000, 50000)
    
    # Normal data for most snapshots
    for i in range(200):
        ts = base_time - (200 - i) * 300  # 5-minute intervals
        
        # Introduce various issues
        if random.random() < 0.02:  # 2% negative prices (CRITICAL)
            price_val = -random.uniform(0.1, 0.5)
        elif random.random() < 0.05:  # 5% price jumps >50%
            price_val = price * random.uniform(1.6, 2.5)
        elif random.random() < 0.03:  # 3% out of range
            price_val = random.uniform(1.1, 1.5)
        else:
            price_val = price + random.uniform(-0.05, 0.05)
            price_val = max(0.01, min(0.99, price_val))
        
        # Volume issues
        if random.random() < 0.02:  # 2% volume decreases
            volume -= random.uniform(1000, 5000)
        else:
            volume += random.uniform(100, 1000)
        
        cursor.execute('INSERT INTO market_snapshots VALUES (?, ?, ?, ?)',
                      (market_id, int(ts), price_val, max(0, volume)))
        snapshot_count += 1
        
        price = price_val

# Add some gaps (missing data periods)
print("Adding data gaps...")
cursor.execute('''
    DELETE FROM market_snapshots 
    WHERE market_id = 'BTC100K' 
    AND timestamp BETWEEN ? AND ?
''', (int(base_time - 7200), int(base_time - 3600)))

# Add future timestamps
print("Adding future timestamps...")
future_ts = int((datetime.now() + timedelta(days=1)).timestamp())
cursor.execute('INSERT INTO market_snapshots VALUES (?, ?, ?, ?)',
              ('TRUMP2024', future_ts, 0.65, 50000))

# Add duplicate records
print("Adding duplicates...")
for i in range(10):
    cursor.execute('INSERT INTO market_snapshots VALUES (?, ?, ?, ?)',
                  ('RECESSION', int(base_time - 5000), 0.45, 30000))

# Insert Twitter data with quality issues
print("Adding Twitter data...")

# Normal tweets
tweet_texts = [
    "Interesting market on Polymarket! #prediction",
    "This could go either way, what do you think?",
    "Just placed my bet, feeling confident!",
    "Market odds looking good today",
    "Analysis: Trump odds rising steadily"
]

for i in range(50):
    market_id = random.choice([m[0] for m in markets])
    text = random.choice(tweet_texts)
    user = f"user{random.randint(1, 20)}"
    
    cursor.execute('INSERT INTO tweets VALUES (?, ?, ?, ?, ?)',
                  (f'tweet_{i}', market_id, user, text, int(base_time - random.randint(0, 86400))))

# Duplicate tweets (same text)
for i in range(15):
    cursor.execute('INSERT INTO tweets VALUES (?, ?, ?, ?, ?)',
                  (f'dup_tweet_{i}', 'BTC100K', f'user{i}', 
                   'Bitcoin to the moon! 🚀🚀🚀', int(base_time - random.randint(0, 3600))))

# Bot pattern (same text, different users)
bot_text = "Click here for free crypto signals! http://scam.com #crypto #trading #signals #forex #profit"
for i in range(10):
    cursor.execute('INSERT INTO tweets VALUES (?, ?, ?, ?, ?)',
                  (f'bot_tweet_{i}', 'BTC100K', f'bot_account_{i}', 
                   bot_text, int(base_time - random.randint(0, 7200))))

# Spam tweets (excessive hashtags)
spam_text = "Check this out! #crypto #bitcoin #eth #trading #money #profit #gains #moon #lambo #rich #success"
for i in range(8):
    cursor.execute('INSERT INTO tweets VALUES (?, ?, ?, ?, ?)',
                  (f'spam_tweet_{i}', 'BTC100K', f'spammer_{i}', 
                   spam_text, int(base_time - random.randint(0, 3600))))

conn.commit()

print(f"\n✅ Test database created: {db_path}")
print(f"   • {len(markets)} markets")
print(f"   • {snapshot_count} snapshots (with intentional issues)")
print(f"   • ~83 tweets (with spam/bots/duplicates)")
print("\nIntentional issues added:")
print("   • Negative prices")
print("   • Price jumps >50%")
print("   • Prices outside [0,1] range")
print("   • Volume decreases")
print("   • Data gaps (30+ min)")
print("   • Future timestamps")
print("   • Duplicate records")
print("   • Duplicate tweets")
print("   • Bot patterns")
print("   • Spam tweets")

conn.close()
