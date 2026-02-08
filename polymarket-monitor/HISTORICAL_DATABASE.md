# Historical Price Database

**Complete system for tracking Polymarket price movements over time.**

## Overview

The historical database system enables real trend analysis and ROC (Rate of Change) calculations by storing hourly price snapshots of the top 100 active Polymarket markets. This replaces the mock data in `signal_detector_v2.py` (which assumed 10% gains) with actual historical lookups.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Polymarket Gamma API                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Scrape every hour
                     │ (Top 100 active markets)
                     ▼
┌─────────────────────────────────────────────────────────┐
│          historical_scraper.py (Cron Job)               │
│  • Fetches market data from Gamma API                   │
│  • Extracts YES/NO prices + 24h volume                  │
│  • Stores snapshots with timestamp                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Batch INSERT
                     ▼
┌─────────────────────────────────────────────────────────┐
│         polymarket_history.db (SQLite)                  │
│                                                          │
│  Table: price_history                                   │
│  ├─ timestamp (INT)                                     │
│  ├─ market_id (TEXT)                                    │
│  ├─ yes_price (REAL)                                    │
│  ├─ no_price (REAL)                                     │
│  └─ volume_24h (REAL)                                   │
│                                                          │
│  Indexes:                                               │
│  ├─ idx_market_time (market_id, timestamp DESC)        │
│  └─ idx_timestamp (timestamp DESC)                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Query lookups
                     ▼
┌─────────────────────────────────────────────────────────┐
│              historical_db.py (API)                     │
│  • get_price_24h_ago(market_id)                         │
│  • get_volume_24h_ago(market_id)                        │
│  • get_historical_data(market_id)                       │
│  • get_price_history(market_id, hours)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Used by
                     ▼
┌─────────────────────────────────────────────────────────┐
│           signal_detector_v2.py                         │
│  • Trend filter: price UP from 24h ago?                │
│  • ROC calculation: % change over 24h                   │
│  • RVR calculation: volume spike vs 24h ago             │
└─────────────────────────────────────────────────────────┘
```

## Files

### Core Components

1. **`historical_db.py`** - Database interface
   - SQLite schema definition
   - Lookup functions for 24h historical data
   - Batch insert for efficient storage
   - Database maintenance (cleanup, stats)

2. **`historical_scraper.py`** - Data collection
   - Scrapes top 100 active markets from Gamma API
   - Stores snapshots every hour
   - Logs to `logs/historical_scraper.log`
   - Auto-cleanup: keeps last 30 days

3. **`signal_detector_v2.py`** _(updated)_
   - Now uses real historical data instead of mock
   - `_get_historical_data()` queries database
   - Markets without 24h history are skipped

### Setup Scripts

4. **`setup_scraper_task.ps1`** - Windows Task Scheduler
   - Automated setup for Windows
   - Run as Administrator

5. **`setup_scraper_cron.sh`** - Linux/macOS cron
   - Automated setup for Unix systems
   - Run with `chmod +x` and execute

6. **`cron_config.txt`** - Manual cron configuration
   - Instructions for manual setup
   - Alternative schedules (every 30 min, etc.)

## Database Schema

```sql
CREATE TABLE price_history (
    timestamp INTEGER NOT NULL,      -- Unix timestamp
    market_id TEXT NOT NULL,         -- Polymarket market ID
    yes_price REAL NOT NULL,         -- YES probability (0-1)
    no_price REAL NOT NULL,          -- NO probability (0-1)
    volume_24h REAL NOT NULL,        -- 24-hour trading volume
    PRIMARY KEY (timestamp, market_id)
);

CREATE INDEX idx_market_time ON price_history(market_id, timestamp DESC);
CREATE INDEX idx_timestamp ON price_history(timestamp DESC);
```

## Installation & Setup

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Test the Database

```bash
# Run database tests
python historical_db.py

# Expected output:
# ✅ Database initialized: polymarket_history.db
# 🧪 Testing Historical Database...
# ... (test results)
```

### 3. Test the Scraper

```bash
# Run test scrape (10 markets)
python historical_scraper.py --test

# Expected output:
# 🧪 Running test scrape...
# 🔍 Starting scrape of top 10 active markets...
# 📥 Fetched 10 active markets
# ✅ Stored 10 price snapshots
```

### 4. Setup Automated Scraping

**Windows (Task Scheduler):**

```powershell
# Run PowerShell as Administrator
.\setup_scraper_task.ps1

# Verify
Get-ScheduledTask -TaskName "PolymarketHistoricalScraper" | Format-List

# Test run
Start-ScheduledTask -TaskName "PolymarketHistoricalScraper"
```

**Linux/macOS (cron):**

```bash
# Make script executable
chmod +x setup_scraper_cron.sh

# Run setup
./setup_scraper_cron.sh

# Verify
crontab -l | grep historical_scraper

# Check logs
tail -f logs/scraper_cron.log
```

**Manual Setup:**

See `cron_config.txt` for manual cron configuration.

### 5. Wait for Data Collection

**Important:** The system needs at least 24 hours of data before it can detect signals.

- After first run: 0 signals (no historical data yet)
- After 1 day: Signals start appearing
- After 7 days: Full trend analysis available

You can check database stats:

```python
from historical_db import get_db

db = get_db()
stats = db.get_stats()
print(stats)
# {
#   'num_markets': 100,
#   'num_snapshots': 2400,  # 100 markets × 24 hours
#   'oldest_snapshot': datetime(...),
#   'newest_snapshot': datetime(...),
#   'db_size_mb': 0.5
# }
```

## Usage in signal_detector_v2.py

### Before (Mock Data)

```python
def _get_historical_data(self, market_id):
    # TEMPORARY: Mock historical data
    hist_data = {
        'price_24h_ago': current_price * 0.9,  # Assume 10% gain
        'volume_24h_ago': volume * 0.5         # Assume volume doubled
    }
    return hist_data
```

### After (Real Data)

```python
def _get_historical_data(self, market_id):
    from historical_db import get_db
    
    db = get_db()
    hist_data = db.get_historical_data(market_id)
    
    if hist_data and hist_data['price_24h_ago'] is not None:
        return hist_data
    else:
        return None  # Skip market if no historical data
```

## API Reference

### HistoricalDB Class

```python
from historical_db import HistoricalDB, get_db

# Get singleton instance
db = get_db()
```

#### Methods

**`get_price_24h_ago(market_id)`**
- Returns: `float` or `None`
- Gets YES price from 24 hours ago (±2 hour tolerance)

**`get_volume_24h_ago(market_id)`**
- Returns: `float` or `None`
- Gets 24h volume from 24 hours ago

**`get_historical_data(market_id)`**
- Returns: `dict` with `price_24h_ago` and `volume_24h_ago` or `None`
- Convenience method that gets both values

**`get_price_history(market_id, hours=168)`**
- Returns: List of `(timestamp, yes_price, no_price, volume)` tuples
- Gets full price history for a market (default: last 7 days)

**`get_stats()`**
- Returns: `dict` with database statistics
- Keys: `num_markets`, `num_snapshots`, `oldest_snapshot`, `newest_snapshot`, `db_size_mb`

**`store_snapshot(market_id, yes_price, no_price, volume, timestamp=None)`**
- Stores a single price snapshot
- Timestamp defaults to now if not provided

**`cleanup_old_data(days=30)`**
- Removes snapshots older than specified days
- Runs VACUUM to reclaim disk space

### Example Usage

```python
from historical_db import get_db

db = get_db()

# Check if we have historical data for a market
market_id = "0x1234..."
hist = db.get_historical_data(market_id)

if hist:
    price_now = 0.65
    price_24h = hist['price_24h_ago']
    
    # Calculate ROC
    roc_pct = ((price_now - price_24h) / price_24h) * 100
    
    print(f"Price now: {price_now:.1%}")
    print(f"Price 24h ago: {price_24h:.1%}")
    print(f"ROC: {roc_pct:+.1f}%")
    
    # Check trend
    if price_now > price_24h:
        print("✅ Trend filter PASS (price rising)")
    else:
        print("❌ Trend filter FAIL (price falling)")
else:
    print("⚠️ No historical data available")
```

## Monitoring & Maintenance

### Check Scraper Logs

**Windows:**
```powershell
Get-Content logs\historical_scraper.log -Tail 50 -Wait
```

**Linux/macOS:**
```bash
tail -f logs/historical_scraper.log
```

### Database Statistics

```bash
python -c "from historical_db import get_db; import pprint; pprint.pprint(get_db().get_stats())"
```

### Manual Scrape

```bash
# Scrape top 100 markets now
python historical_scraper.py

# Scrape top 200 markets
python historical_scraper.py --limit 200
```

### Backup Database

```bash
# Windows
copy polymarket_history.db polymarket_history_backup_$(date +%Y%m%d).db

# Linux/macOS
cp polymarket_history.db polymarket_history_backup_$(date +%Y%m%d).db
```

### Database Maintenance

```python
from historical_db import get_db

db = get_db()

# Clean up old data (keep last 30 days)
db.cleanup_old_data(days=30)

# Get stats
stats = db.get_stats()
print(f"Database size: {stats['db_size_mb']:.2f} MB")
```

## Expected Performance

### Storage Requirements

- **Per snapshot:** ~100 bytes
- **Per hour (100 markets):** ~10 KB
- **Per day:** ~240 KB
- **Per month:** ~7 MB
- **Per year:** ~85 MB

With auto-cleanup (30 days), database stays under **10 MB**.

### Query Performance

- Lookup for single market: **<5ms**
- Batch lookup for 100 markets: **<50ms**
- Full history (7 days): **<10ms**

SQLite indexes ensure fast lookups even with millions of snapshots.

## Troubleshooting

### "No historical data for market"

**Cause:** Market is new or scraper hasn't run yet.

**Solution:** Wait 24 hours for data to accumulate, or manually run scraper.

### "Database locked"

**Cause:** Scraper and signal detector accessing database simultaneously.

**Solution:** SQLite handles this automatically with retries. Increase timeout if needed:

```python
db = HistoricalDB()
db.conn.execute("PRAGMA busy_timeout = 30000")  # 30 seconds
```

### Scraper not running

**Windows:**
```powershell
# Check task status
Get-ScheduledTask -TaskName "PolymarketHistoricalScraper"

# Check last run result
Get-ScheduledTaskInfo -TaskName "PolymarketHistoricalScraper"
```

**Linux/macOS:**
```bash
# Check cron is running
systemctl status cron  # or 'crond' on some systems

# Check syslog for cron errors
grep CRON /var/log/syslog | tail -20
```

### API rate limiting

**Symptom:** Scraper fails with 429 errors.

**Solution:** Gamma API has generous rate limits. If you hit them:
- Reduce scrape frequency (every 2 hours instead of 1)
- Reduce limit (top 50 markets instead of 100)
- Add `time.sleep(0.1)` between requests

## Integration with Existing System

The historical database is **drop-in compatible** with the existing `signal_detector_v2.py`:

1. **No changes needed** to main monitoring system
2. `signal_detector_v2.py` automatically uses database when available
3. Falls back gracefully if no historical data exists
4. Filters out markets without 24h history

### Signal Detection Flow

```
1. Monitor fetches active markets from Gamma API
2. signal_detector_v2.py analyzes each market
3. For each market:
   a. Query historical_db for 24h price/volume
   b. If no data → skip market (log warning)
   c. If data exists:
      - Calculate ROC (rate of change)
      - Check trend filter (price UP?)
      - Calculate RVR (volume spike)
      - Apply all V2.0 filters
   d. If all filters pass → generate signal
4. Return filtered signals to monitor
```

## Future Enhancements

- [ ] Add 1h, 6h, 12h lookups for shorter timeframes
- [ ] Store additional metadata (liquidity, comment count)
- [ ] Web dashboard to visualize price trends
- [ ] Export to CSV for external analysis
- [ ] Postgres support for larger deployments
- [ ] Price alerts based on historical volatility

## Summary

This historical database system provides:

✅ **Real trend analysis** - No more mock data  
✅ **Accurate ROC calculations** - Actual 24h price movements  
✅ **Volume spike detection** - RVR based on real data  
✅ **Automated data collection** - Runs every hour via cron  
✅ **Efficient storage** - SQLite with indexes, <10 MB  
✅ **Production-ready** - Error handling, logging, monitoring  
✅ **Drop-in integration** - Works with existing signal detector  

After 24 hours of data collection, `signal_detector_v2.py` will use real historical lookups instead of assumptions, dramatically improving signal quality and backtest accuracy.
