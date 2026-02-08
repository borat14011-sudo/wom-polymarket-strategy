# Polymarket Volume Monitoring System

Real-time trade signal detection for Polymarket using RVR (Risk-Volume-ROI) analysis.

## 🎯 What It Does

- **Scrapes** Polymarket trending markets every hour
- **Calculates** RVR (Risk-Volume Ratio) and ROC (Rate of Change) signals
- **Alerts** via Telegram when opportunities arise
- **Runs 24/7** with automatic cleanup and error handling

## 📊 Signal Criteria

Alerts are triggered when BOTH conditions are met:

- **RVR > 2.5**: Current volume is 2.5x+ the 24-hour average
- **|ROC| > 8%**: Price changed more than 8% in the last 12 hours

These thresholds indicate unusual volume with significant price movement.

## 🏗️ Architecture

```
┌─────────────────┐
│  Polymarket API │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐       ┌──────────────┐
│ polymarket_scraper  │──────▶│   SQLite DB  │
└─────────────────────┘       └──────┬───────┘
                                     │
                              ┌──────▼───────┐
                              │ rvr_calculator│
                              └──────┬───────┘
                                     │
                              ┌──────▼───────┐
                              │ telegram_alerter│
                              └──────┬───────┘
                                     │
                              ┌──────▼───────┐
                              │   Telegram   │
                              │ @MoneyManAmex│
                              └──────────────┘
```

## 📦 Installation

### 1. Prerequisites

- Python 3.8+
- OpenClaw CLI (for Telegram integration)

### 2. Install Dependencies

```bash
cd polymarket-monitor
pip install -r requirements.txt
```

### 3. Verify Setup

```bash
# Test scraper
python polymarket_scraper.py

# Test calculator
python rvr_calculator.py

# Test alerter (requires OpenClaw)
python telegram_alerter.py
```

## 🚀 Usage

### Start the Monitor

**Option 1: Using the start script (Linux/Mac)**
```bash
bash run-monitor.sh
```

**Option 2: Direct Python (All platforms)**
```bash
python monitor_daemon.py
```

**Option 3: Background process (Linux/Mac)**
```bash
nohup python monitor_daemon.py > monitor_output.log 2>&1 &
```

**Option 4: Windows background**
```powershell
Start-Process -NoNewWindow python -ArgumentList "monitor_daemon.py"
```

### Stop the Monitor

Press `Ctrl+C` or kill the process:

```bash
# Find the process
ps aux | grep monitor_daemon

# Kill it
kill <PID>
```

## 📁 File Structure

```
polymarket-monitor/
├── monitor_daemon.py          # Main orchestrator (runs continuously)
├── polymarket_scraper.py      # Fetches market data from Polymarket
├── rvr_calculator.py          # Calculates RVR and ROC signals
├── telegram_alerter.py        # Sends Telegram alerts
├── database.py                # SQLite database management
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── run-monitor.sh             # Start script
├── polymarket_data.db         # SQLite database (auto-created)
└── monitor.log                # Application logs (auto-created)
```

## 🗃️ Database Schema

### market_snapshots
```sql
CREATE TABLE market_snapshots (
    id INTEGER PRIMARY KEY,
    market_id TEXT NOT NULL,
    name TEXT NOT NULL,
    price REAL NOT NULL,           -- Current price (0.0-1.0)
    volume REAL NOT NULL,          -- 24h volume in USD
    liquidity REAL,                -- Available liquidity
    timestamp INTEGER NOT NULL     -- Unix timestamp
);
```

### signals
```sql
CREATE TABLE signals (
    id INTEGER PRIMARY KEY,
    market_id TEXT NOT NULL,
    market_name TEXT NOT NULL,
    rvr REAL NOT NULL,             -- Risk-Volume Ratio
    roc REAL NOT NULL,             -- Rate of Change (%)
    price REAL NOT NULL,
    volume REAL NOT NULL,
    timestamp INTEGER NOT NULL,
    alerted INTEGER DEFAULT 0      -- 0 = pending, 1 = sent
);
```

## 🔧 Configuration

### Change Alert Thresholds

Edit `rvr_calculator.py`:

```python
RVR_THRESHOLD = 2.5  # Increase for fewer, stronger signals
ROC_THRESHOLD = 8.0  # Increase for more volatile movements
```

### Change Telegram Target

Edit `telegram_alerter.py`:

```python
TELEGRAM_TARGET = "@YourUsername"
```

### Change Monitoring Interval

Edit `monitor_daemon.py`:

```python
schedule.every(60).minutes.do(monitoring_cycle)  # Change 60 to desired minutes
```

### Change Data Retention

Edit `database.py`:

```python
cleanup_old_data(days=7)  # Change 7 to desired days
```

## 📊 Monitoring

### Check Logs

```bash
# Watch live logs
tail -f monitor.log

# View recent activity
tail -n 100 monitor.log

# Search for signals
grep "SIGNAL" monitor.log
```

### Query Database

```bash
sqlite3 polymarket_data.db

# View recent markets
SELECT name, volume, timestamp FROM market_snapshots 
ORDER BY timestamp DESC LIMIT 10;

# View all signals
SELECT market_name, rvr, roc, timestamp FROM signals 
ORDER BY timestamp DESC;

# Count markets tracked
SELECT COUNT(DISTINCT market_id) FROM market_snapshots;
```

## 🔍 Troubleshooting

### No markets being scraped
- Check internet connection
- Verify Polymarket API is accessible: `curl https://gamma-api.polymarket.com/markets`
- Check logs for rate limiting errors

### No signals detected
- Lower thresholds in `rvr_calculator.py`
- Verify sufficient historical data: `SELECT COUNT(*) FROM market_snapshots;`
- Markets need at least 2+ hours of data for signals

### Telegram alerts not sending
- Verify OpenClaw is installed: `openclaw --version`
- Test manually: `openclaw message send --channel telegram --target @MoneyManAmex --message "test"`
- Check OpenClaw is configured for Telegram

### Database locked errors
- Only run one instance of the monitor at a time
- If stuck, restart: `rm polymarket_data.db` (warning: deletes all history)

## 📈 Performance

- **Storage**: ~1-2 MB per day (50 markets, hourly snapshots)
- **Memory**: ~50-100 MB typical usage
- **CPU**: Minimal (<1% average)
- **Network**: ~1-5 MB per hour (API requests)

Auto-cleanup keeps database under 50 MB (7 days retention).

## 🔐 Security Notes

- No API keys required (uses public Polymarket data)
- Database contains only market data (no personal info)
- Telegram messages sent via OpenClaw (uses your configured auth)
- All data stored locally

## 📝 Example Alert

```
🚨 POLYMARKET SIGNAL

📊 Market: Will Donald Trump win the 2024 election?

📈 RVR: 3.45x
📉 ROC: +12.3%
💰 Price: 67.5%
💵 Volume: $2.4M

⏰ 2026-02-06 14:30:15
```

## 🛠️ Advanced Usage

### Run One-Time Analysis

```bash
# Scrape once
python polymarket_scraper.py

# Calculate signals on existing data
python rvr_calculator.py

# Send any pending alerts
python telegram_alerter.py
```

### Manual Database Cleanup

```python
from database import cleanup_old_data
cleanup_old_data(days=7)
```

### Export Signals to CSV

```bash
sqlite3 -header -csv polymarket_data.db \
  "SELECT * FROM signals ORDER BY timestamp DESC;" > signals.csv
```

## 🤝 Support

For issues or questions:
1. Check logs: `monitor.log`
2. Verify all components work individually
3. Check database: `sqlite3 polymarket_data.db`

## 📜 License

Free to use and modify for personal trading research.

---

**⚠️ Disclaimer**: This tool is for informational purposes only. Always do your own research before making any trading decisions. Past volume patterns do not guarantee future results.
