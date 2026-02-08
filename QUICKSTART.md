# 🚀 POLYMARKET HYPE TRADING - QUICK START GUIDE

**Status:** Phase 0 - Initial Setup  
**Time to First Data:** <30 minutes  
**Difficulty:** Intermediate (requires basic Python/command line)

---

## Prerequisites

### 1. System Requirements
- **OS:** Linux, macOS, or Windows (WSL recommended)
- **Python:** 3.8+ 
- **Disk Space:** 1GB+ (for database growth)
- **RAM:** 2GB minimum

### 2. Required Software
```bash
# Python 3
python3 --version  # Should be 3.8+

# pip (Python package manager)
pip3 --version

# Git (optional, for cloning)
git --version
```

---

## Installation (5 minutes)

### Step 1: Install Python Dependencies

```bash
# Core dependencies
pip3 install requests sqlite3

# For correlation analysis (when script arrives)
pip3 install pandas numpy statsmodels scipy matplotlib

# For Twitter scraping (optional - if using free method)
pip3 install snscrape

# For dashboard (when built)
pip3 install flask

# Alternative: Install all at once
pip3 install -r requirements.txt
```

### Step 2: Verify Installation

```bash
# Test imports
python3 -c "import requests, sqlite3, pandas, statsmodels; print('✓ All imports successful')"
```

---

## Quick Start (10 minutes)

### 1. Initialize Database

```bash
# Run data collector once to create database
python3 polymarket-data-collector.py
```

**Expected output:**
```
✓ Database initialized: polymarket_data.db
✓ Fetched 15 high-volume markets
✓ Bitcoin will reach $100k... | Price: $0.523 | Vol: $1,250,000
✓ Trump wins 2024... | Price: $0.687 | Vol: $5,800,000
...
✓ Collected 15/15 market snapshots
```

### 2. Run Twitter Monitor

```bash
# Collect initial Twitter data
python3 twitter-hype-monitor.py
```

**Expected output:**
```
📊 Scraping: polymarket.com
   Found 47 tweets
📊 Scraping: #Polymarket
   Found 23 tweets
...
✓ Total unique tweets: 58
✓ Matched 12 tweets to markets
✓ Generated 3 hype signals

🔥 TOP HYPE MARKETS:
   1. [72.3] Will Bitcoin reach $100k by year end? | Tweets: 8 | Velocity: +150%
```

### 3. Set Up Cron Jobs (Automated Collection)

```bash
# Edit crontab
crontab -e

# Add these lines (adjust paths to your workspace):

# Collect market data every 15 minutes
*/15 * * * * cd /path/to/workspace && python3 polymarket-data-collector.py >> logs/collector.log 2>&1

# Collect Twitter data every 15 minutes
*/15 * * * * cd /path/to/workspace && python3 twitter-hype-monitor.py >> logs/twitter.log 2>&1

# Save and exit
```

**Verify cron is running:**
```bash
# Check logs after 15 minutes
tail -f logs/collector.log
tail -f logs/twitter.log
```

---

## Data Collection Timeline

### Week 1: Initial Collection
- **Day 1-3:** Collect baseline data (288 snapshots per market @ 15min intervals)
- **Day 4-7:** Enough data for preliminary correlation tests
- **Goal:** 50+ markets × 7 days = ~100K data points

### Week 2-3: Analysis Phase
- **Day 8-14:** Run correlation analyzer (requires 7+ days of data)
- **Day 15-21:** Identify markets with strongest hype→price relationships
- **Goal:** Find 5-10 markets with Granger p<0.01

### Week 4: Validation
- **Day 22-28:** Paper trade identified signals
- **Goal:** Validate backtest assumptions match reality

---

## Monitoring Your System

### Check Database Size
```bash
# Linux/Mac
ls -lh polymarket_data.db

# Windows
dir polymarket_data.db
```

**Expected growth:**
- Week 1: ~10-50 MB
- Week 2: ~50-150 MB
- Month 1: ~200-500 MB

### Query Database
```bash
# Open SQLite
sqlite3 polymarket_data.db

# Check market count
SELECT COUNT(*) FROM markets;

# Check snapshot count
SELECT COUNT(*) FROM snapshots;

# Check recent tweets
SELECT timestamp, text FROM tweets ORDER BY timestamp DESC LIMIT 5;

# Check hype signals
SELECT m.question, h.hype_score, h.tweet_count
FROM hype_signals h
JOIN markets m ON h.market_id = m.market_id
ORDER BY h.timestamp DESC LIMIT 10;

# Exit
.exit
```

### View Logs
```bash
# Real-time monitoring
tail -f logs/collector.log
tail -f logs/twitter.log

# Check for errors
grep "Error" logs/*.log
```

---

## Troubleshooting

### Problem: "snscrape not found"
**Solution:**
```bash
pip3 install snscrape

# If still fails, try:
pip3 install --upgrade git+https://github.com/JustAnotherArchivist/snscrape.git
```

### Problem: "Twitter scraping returns no results"
**Causes:**
1. snscrape may be temporarily blocked by X/Twitter
2. No recent tweets match keywords
3. Rate limiting

**Solutions:**
1. Wait 30-60 minutes and retry
2. Try different keywords
3. Consider paid Twitter API ($100/mo Basic tier)

### Problem: "Database locked"
**Cause:** Multiple scripts accessing database simultaneously

**Solution:**
```bash
# Check for running processes
ps aux | grep python

# Kill if needed
pkill -f polymarket-data-collector.py

# Restart
python3 polymarket-data-collector.py
```

### Problem: "No markets found"
**Cause:** Polymarket API may be down or rate-limiting

**Solution:**
```bash
# Test API manually
curl "https://gamma-api.polymarket.com/markets?active=true&limit=10"

# If returns data, wait and retry script
# If API is down, check https://status.polymarket.com
```

---

## Next Steps

Once you have 7+ days of data:

### 1. Run Correlation Analysis
```bash
python3 correlation-analyzer.py
```

This will test if hype actually predicts price movements.

### 2. Generate Signals
```bash
python3 signal-generator.py
```

Start getting BUY/SELL alerts (paper trading only at first).

### 3. Run Backtest
```bash
python3 backtest-engine.py
```

Validate strategy on historical data before risking real money.

### 4. Launch Dashboard
```bash
python3 api.py &  # Start backend
open dashboard.html  # Open frontend in browser
```

Visual monitoring of system status.

---

## Configuration

### Update Collection Frequency

Edit cron jobs if 15 minutes is too frequent/infrequent:

```bash
# Every 5 minutes (more data, higher load)
*/5 * * * * python3 polymarket-data-collector.py

# Every 30 minutes (less data, lower load)
*/30 * * * * python3 polymarket-data-collector.py

# Every hour (minimal viable frequency)
0 * * * * python3 polymarket-data-collector.py
```

**Recommendation:** 15 minutes is optimal balance.

### Update Market Filters

Edit `polymarket-data-collector.py`:

```python
# Line 12-13: Adjust volume threshold
MIN_VOLUME_24H = 50000  # Lower = more markets, more noise
MIN_VOLUME_24H = 500000  # Higher = fewer markets, higher quality

# Line 15-20: Add/remove categories
TARGET_CATEGORIES = [
    "Crypto", "Politics", "Sports",  # Keep these
    "Science", "Weather",  # Add these if interested
]
```

### Update Twitter Keywords

Edit `twitter-hype-monitor.py`:

```python
# Line 14-20: Add more keywords
KEYWORDS = [
    "polymarket.com",
    "#Polymarket",
    "prediction market bet",
    "manifold.markets",
    "kalshi",
    # Add your own:
    "betting on",
    "odds are",
    # Market-specific:
    "bitcoin 100k prediction",
    "trump election odds",
]
```

---

## Cost Breakdown

### Free Tier (MVP)
- Polymarket API: **$0** ✓
- snscrape (Twitter): **$0** ✓
- PostgreSQL/SQLite: **$0** ✓
- Hosting (local): **$0** ✓
- **Total: $0/month**

### Basic Paid Tier
- X API Basic: **$100/mo**
- PostgreSQL hosting: **$25/mo**
- **Total: $125/month**

### Professional Tier
- X API Pro: **$5,000/mo**
- Cloud infrastructure: **$500-2K/mo**
- **Total: $5,500-7,000/month**

**Recommendation:** Start free, upgrade only if backtest proves profitable.

---

## Safety Checklist

Before deploying real money:

- [ ] Collected 30+ days of data
- [ ] Ran correlation analysis (Granger p<0.01)
- [ ] Backtested with walk-forward validation (Sharpe >1.0)
- [ ] Paper traded for 2+ weeks (validated signals work)
- [ ] Tested with micro capital ($100-500) for 2+ weeks
- [ ] Win rate >50%, profit factor >1.5
- [ ] Understand risk management (stop losses, position sizing)
- [ ] Have kill criteria defined (when to stop trading)
- [ ] Only using capital you can afford to lose

**If ALL boxes checked: Proceed carefully with small positions**

**If ANY box unchecked: DO NOT TRADE YET**

---

## Support & Resources

### Documentation
- `MASTER-SYNTHESIS-POLYMARKET-STRATEGY.md` - Complete overview
- `TRADING-STRATEGY-FRAMEWORK.md` - Trading rules
- `CORRELATION-ANALYSIS-FRAMEWORK.md` - Statistical methods
- `DATA-COLLECTION-PIPELINE.md` - Infrastructure guide

### APIs
- Polymarket Gamma: https://gamma-api.polymarket.com/
- Polymarket CLOB: https://clob.polymarket.com/
- X API: https://developer.x.com/

### Community
- r/Polymarket (Reddit)
- Polymarket Discord: https://discord.gg/polymarket
- Prediction Markets Twitter: Search #Polymarket

---

## What's Next?

You're now collecting data! 

**While waiting for data to accumulate:**
1. Read the strategy documents
2. Set up Telegram bot for alerts
3. Practice reading orderbooks on Polymarket
4. Paper trade manually to learn market dynamics
5. Study past viral prediction markets

**After 7 days:**
1. Run correlation-analyzer.py
2. Review which markets show hype→price relationships
3. Adjust collection to focus on best markets

**After 30 days:**
1. Run full backtest
2. Make GO/NO-GO decision
3. If GO: Start paper trading signals
4. If NO-GO: Iterate on strategy or abandon

---

**Good luck! May the hype be with you!** 🇰🇿💰
