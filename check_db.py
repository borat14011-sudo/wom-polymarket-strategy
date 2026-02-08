import sqlite3
from datetime import datetime

conn = sqlite3.connect('polymarket_history.db')
cursor = conn.cursor()

# Check market count
cursor.execute("SELECT COUNT(DISTINCT market_id) FROM price_history")
market_count = cursor.fetchone()[0]
print(f"Markets in database: {market_count}")

# Check date range
cursor.execute("SELECT MIN(timestamp), MAX(timestamp), COUNT(*) FROM price_history")
min_ts, max_ts, total_records = cursor.fetchone()
print(f"Date range: {datetime.fromtimestamp(min_ts)} to {datetime.fromtimestamp(max_ts)}")
print(f"Total records: {total_records}")

# Sample some data
cursor.execute("""
    SELECT market_id, COUNT(*) as records, 
           MIN(timestamp) as first_ts, 
           MAX(timestamp) as last_ts
    FROM price_history 
    GROUP BY market_id 
    LIMIT 5
""")

print("\nSample markets:")
for row in cursor.fetchall():
    market_id, records, first_ts, last_ts = row
    print(f"  {market_id[:30]}... - {records} records from {datetime.fromtimestamp(first_ts)} to {datetime.fromtimestamp(last_ts)}")

conn.close()
