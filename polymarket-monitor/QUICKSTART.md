# Quick Start Guide

Get your Polymarket monitor running in 5 minutes!

## ⚡ Installation (60 seconds)

```bash
# 1. Navigate to the folder
cd polymarket-monitor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test the system
python test_system.py
```

## ⚙️ Configuration (30 seconds)

Edit `config.py` to customize:

```python
# Change alert sensitivity
RVR_THRESHOLD = 2.5    # Lower = more alerts (e.g., 2.0)
ROC_THRESHOLD = 8.0    # Lower = more alerts (e.g., 5.0)

# Change your Telegram username
TELEGRAM_TARGET = "@YourUsername"

# Change monitoring frequency
SCRAPE_INTERVAL_MINUTES = 60  # Check every hour
```

## 🚀 Run It!

**Linux/Mac:**
```bash
bash run-monitor.sh
```

**Windows:**
```cmd
run-monitor.bat
```

**Or directly with Python:**
```bash
python monitor_daemon.py
```

## 📱 First Alert

You should see output like:

```
🚀 ============================================================ 🚀
POLYMARKET MONITOR DAEMON STARTING
================================================================
Log file: monitor.log
Database: polymarket_data.db
Monitoring interval: 60 minutes
Cleanup interval: 24 hours
================================================================

Initializing database...
Running initial monitoring cycle...

🔄 ========================================================== 🔄
Starting monitoring cycle at 2026-02-06 11:45:00
================================================================
Step 1/3: Scraping Polymarket data...
Successfully fetched 50 markets
✅ Scraped 50 markets

Step 2/3: Calculating RVR signals...
Analyzing 50 markets
🚨 SIGNAL FOUND: Will Bitcoin hit $100k by March? | RVR: 3.21 | ROC: +9.2%
✅ Found 1 new signals

Step 3/3: Sending Telegram alerts...
Sending message to @MoneyManAmex
✅ Sent 1 alerts
================================================================
✅ Cycle complete in 8.3s
================================================================

⏰ Scheduler active - monitoring every 60 minutes
Press Ctrl+C to stop
```

## 🔍 Verify It's Working

**Check the logs:**
```bash
tail -f monitor.log
```

**Query the database:**
```bash
sqlite3 polymarket_data.db "SELECT COUNT(*) FROM market_snapshots;"
```

**Look for signals:**
```bash
grep "SIGNAL" monitor.log
```

## 🛑 Stop the Monitor

Press `Ctrl+C` or:

```bash
# Find the process
ps aux | grep monitor_daemon

# Kill it
kill <PID>
```

## 🔧 Troubleshooting

### No markets being scraped?
```bash
# Test internet connection to Polymarket
curl https://gamma-api.polymarket.com/markets?limit=1
```

### No signals detected?
- Lower thresholds in `config.py`
- Wait at least 2 hours for historical data to accumulate
- Check: `python rvr_calculator.py` to test manually

### Telegram not working?
```bash
# Test OpenClaw
openclaw message send --channel telegram --target @YourUsername --message "Test"
```

## 📊 Monitor Performance

**View database stats:**
```bash
sqlite3 polymarket_data.db <<EOF
.mode column
.headers on
SELECT 
    COUNT(*) as total_snapshots,
    COUNT(DISTINCT market_id) as unique_markets,
    datetime(MIN(timestamp), 'unixepoch') as first_snapshot,
    datetime(MAX(timestamp), 'unixepoch') as last_snapshot
FROM market_snapshots;
EOF
```

**View recent signals:**
```bash
sqlite3 polymarket_data.db <<EOF
.mode column
.headers on
SELECT 
    market_name,
    ROUND(rvr, 2) as rvr,
    ROUND(roc, 1) as roc,
    datetime(timestamp, 'unixepoch') as time
FROM signals
ORDER BY timestamp DESC
LIMIT 10;
EOF
```

## 🎯 Tips for Best Results

1. **Let it run for 24 hours** - Needs historical data for accurate signals
2. **Start with default thresholds** - Adjust after you see what alerts you get
3. **Check logs daily** - Look for errors or API issues
4. **Monitor in background** - Use `nohup` or a process manager like `systemd`

## 🚀 Production Deployment

For 24/7 operation, use a process manager:

**Option 1: nohup (simple)**
```bash
nohup python monitor_daemon.py > output.log 2>&1 &
```

**Option 2: systemd (Linux)**
```bash
# Create service file: /etc/systemd/system/polymarket-monitor.service
[Unit]
Description=Polymarket Volume Monitor
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/polymarket-monitor
ExecStart=/usr/bin/python3 monitor_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable polymarket-monitor
sudo systemctl start polymarket-monitor
sudo systemctl status polymarket-monitor
```

**Option 3: Docker**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "monitor_daemon.py"]
```

```bash
docker build -t polymarket-monitor .
docker run -d --name pm-monitor polymarket-monitor
```

## 📈 Next Steps

- Monitor for a few days to tune thresholds
- Export signals to analyze patterns: `sqlite3 polymarket_data.db ".dump signals" > signals.sql`
- Add more metrics (momentum, sentiment, etc.)
- Build a dashboard with real-time stats

---

**Need help?** Check `README.md` for full documentation or inspect `monitor.log` for errors.
