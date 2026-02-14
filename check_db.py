import sqlite3
import json
conn = sqlite3.connect('polymarket-monitor/polymarket_data.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Tables:', tables)

# Check each table structure
for table in tables:
    table_name = table[0]
    print(f'\n{table_name} table:')
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col[1]} ({col[2]})')
    
    # Count records
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f'  Records: {count:,}')
    
    # For prices table, get date range
    if table_name == 'prices':
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM prices;")
        min_ts, max_ts = cursor.fetchone()
        print(f'  Date range: {min_ts} to {max_ts}')
        
        # Count unique markets
        cursor.execute("SELECT COUNT(DISTINCT market_id) FROM prices;")
        unique_markets = cursor.fetchone()[0]
        print(f'  Unique markets: {unique_markets}')

conn.close()