import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('polymarket-monitor/polymarket_data.db')
cursor = conn.cursor()

# Get sample of markets
cursor.execute("SELECT category, COUNT(*) as count FROM markets GROUP BY category ORDER BY count DESC;")
categories = cursor.fetchall()
print("Market categories distribution:")
for cat, count in categories:
    print(f"  {cat}: {count}")

# Get date range of markets
cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM markets;")
min_date, max_date = cursor.fetchone()
print(f"\nMarket creation date range: {min_date} to {max_date}")

# Get active vs inactive
cursor.execute("SELECT active, COUNT(*) FROM markets GROUP BY active;")
active_stats = cursor.fetchall()
print("\nActive status:")
for active, count in active_stats:
    print(f"  Active={active}: {count}")

# Get sample market questions
cursor.execute("SELECT question, category, created_at, end_date FROM markets LIMIT 10;")
samples = cursor.fetchall()
print("\nSample markets:")
for question, category, created, end in samples:
    print(f"  [{category}] {question[:80]}...")
    print(f"    Created: {created}, Ends: {end}")

# Check for resolution data in another way
print("\nChecking for any price/resolution data...")

# Look for any files with market data
import os
import glob

# Check for JSON files with market data
json_files = glob.glob("polymarket-monitor/**/*.json", recursive=True)
market_data_files = [f for f in json_files if 'market' in f.lower() or 'price' in f.lower()]
print(f"\nFound {len(market_data_files)} potential market data files")

conn.close()