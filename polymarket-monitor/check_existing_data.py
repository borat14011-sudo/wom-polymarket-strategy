"""Review existing collected data"""
import sqlite3
import json
import os

print("="*60)
print("EXISTING DATA REVIEW")
print("="*60)

# 1. Check SQLite database
print("\n[SQLite Database - polymarket_data.db]")
if os.path.exists('polymarket_data.db'):
    conn = sqlite3.connect('polymarket_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM markets")
    total_markets = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM markets WHERE active = 1")
    active_markets = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM prices")
    price_snapshots = cursor.fetchone()[0]
    
    print(f"  Total markets: {total_markets}")
    print(f"  Active markets: {active_markets}")
    print(f"  Price snapshots: {price_snapshots}")
    
    print("\n  Top categories:")
    cursor.execute("""
        SELECT category, COUNT(*) as cnt 
        FROM markets 
        GROUP BY category 
        ORDER BY cnt DESC 
        LIMIT 10
    """)
    for cat, count in cursor.fetchall():
        print(f"    {cat or 'Unknown'}: {count}")
    
    print("\n  Top 5 markets by volume:")
    cursor.execute("""
        SELECT question, volume 
        FROM markets 
        ORDER BY volume DESC 
        LIMIT 5
    """)
    for q, vol in cursor.fetchall():
        print(f"    ${vol/1000:.0f}K - {q[:70]}")
    
    conn.close()
else:
    print("  Database not found")

# 2. Check historical data
print("\n[Historical Data - historical-data-scraper/data/]")
data_dir = "historical-data-scraper/data"
if os.path.exists(data_dir):
    files = []
    for f in os.listdir(data_dir):
        if f.endswith('.json'):
            size = os.path.getsize(os.path.join(data_dir, f))
            files.append((f, size))
    
    files.sort(key=lambda x: x[1], reverse=True)
    
    print("  Large JSON files:")
    for fname, size in files[:5]:
        if size > 1000000:  # > 1 MB
            size_mb = size / 1024 / 1024
            if size_mb > 1000:
                print(f"    {fname}: {size_mb/1024:.2f} GB")
            else:
                print(f"    {fname}: {size_mb:.0f} MB")
    
    # Check backtest dataset
    backtest_path = os.path.join(data_dir, "backtest_dataset_v1.json")
    if os.path.exists(backtest_path):
        print(f"\n  Loading backtest_dataset_v1.json...")
        with open(backtest_path, 'r') as f:
            data = json.load(f)
            print(f"    Keys: {list(data.keys())}")
            if 'markets' in data:
                print(f"    Total markets: {len(data['markets'])}")
                print(f"    Sample: {data['markets'][0]['question'][:80]}")
else:
    print("  Historical data directory not found")

# 3. Check for EVENT_BACKTEST_REPORT
print("\n[Event Backtest Report]")
report_path = "historical-data-scraper/EVENT_BACKTEST_REPORT.md"
if os.path.exists(report_path):
    print(f"  Found: {report_path}")
    with open(report_path, 'r') as f:
        lines = f.readlines()
        print(f"  Lines: {len(lines)}")
        # Find strategy table
        for i, line in enumerate(lines):
            if 'MUSK_FADE_EXTREMES' in line:
                print(f"  Strategy found at line {i}")
                break
else:
    print("  Report not found")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"✓ SQLite database: {total_markets if 'total_markets' in locals() else 0} markets")
print(f"✓ Price snapshots: {price_snapshots if 'price_snapshots' in locals() else 0}")
print(f"✓ Historical data: {'Yes' if os.path.exists(data_dir) else 'No'}")
print(f"✓ Event backtest report: {'Yes' if os.path.exists(report_path) else 'No'}")
