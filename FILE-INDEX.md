# 📁 FILE INDEX - Complete Project Structure

**Project:** Polymarket X Hype Trading System  
**Last Updated:** 2026-02-06, 5:20 AM PST  
**Total Files:** 30+ documents + scripts

---

## 📚 DOCUMENTATION (170KB Research + Guides)

### Core Research (Read These First)

| File | Size | Purpose |
|------|------|---------|
| **README.md** | 11KB | Project overview, quick start |
| **MASTER-SYNTHESIS-POLYMARKET-STRATEGY.md** | 11KB | Executive summary, synthesized findings |
| **PROJECT-DELIVERY.md** | 13KB | Complete delivery summary, ROI analysis |
| **PROJECT-STATUS.md** | 13KB | Current progress, milestones, decision gates |
| **QUICKSTART.md** | 9KB | Setup guide (30 minutes to running) |

### Strategy & Research

| File | Size | Purpose |
|------|------|---------|
| **TRADING-STRATEGY-FRAMEWORK.md** | 25KB | Entry/exit rules, position sizing, risk management |
| **CORRELATION-ANALYSIS-FRAMEWORK.md** | Comprehensive | Statistical methods, Granger causality, false positives |
| **POLYMARKET-KALSHI-RESEARCH.md** | 23KB | Platform mechanics, APIs, viral markets |
| **TWITTER-SENTIMENT-TRACKING.md** | 40KB | Hype detection, 8 metrics, 2-6h lead time |
| **DATA-COLLECTION-PIPELINE.md** | 41KB | Database schema, cost optimization, MVP plan |

### Implementation Guides

| File | Size | Purpose |
|------|------|---------|
| **DEPLOYMENT-GUIDE.md** | 13KB | Windows/Linux/Mac deployment, cron/scheduler |
| **TESTING-GUIDE.md** | 12KB | Unit tests, integration tests, validation |
| **SIGNALS-README.md** | 13KB | Signal generator usage, Telegram setup |
| **DASHBOARD-README.md** | Included | Web dashboard setup & API reference |
| **CORRELATION-ANALYZER-README.md** | 14KB | Statistical analysis tool usage |

---

## 🐍 PYTHON SCRIPTS (Working Code)

### Data Collection

| File | Size | Purpose | Run Frequency |
|------|------|---------|---------------|
| **polymarket-data-collector.py** | 9.5KB | Collect market prices, volume, liquidity | Every 15 min |
| **twitter-hype-monitor.py** | 12.8KB | Scrape tweets, calculate hype scores | Every 15 min |

**Usage:**
```bash
python polymarket-data-collector.py
python twitter-hype-monitor.py
```

### Analysis & Signals

| File | Size | Purpose | When to Run |
|------|------|---------|-------------|
| **correlation-analyzer.py** | 36.6KB | Granger causality, lag analysis | After 7+ days data |
| **signal-generator.py** | 25KB | Generate BUY/SELL alerts | Continuous or cron |
| **backtest-engine.py** | TBD | Historical validation | After 30+ days data |

**Usage:**
```bash
# Correlation analysis (after 7 days)
python correlation-analyzer.py --db polymarket_data.db

# Signal generation (continuous monitoring)
python signal-generator.py --continuous

# Backtesting (after 30 days)
python backtest-engine.py --db polymarket_data.db
```

### Dashboard

| File | Size | Purpose |
|------|------|---------|
| **api.py** | 17KB | Flask REST API backend |
| **dashboard.html** | 38KB | Web monitoring interface |
| **start-dashboard.sh** | Small | Linux/Mac launcher |
| **start-dashboard.bat** | Small | Windows launcher |

**Usage:**
```bash
./start-dashboard.sh      # Linux/Mac
start-dashboard.bat       # Windows
# Opens http://localhost:5000
```

---

## ⚙️ CONFIGURATION FILES

| File | Purpose | Edit Before Use? |
|------|---------|------------------|
| **config.json** | Signal thresholds, Telegram, risk limits | ✅ YES (set bankroll) |
| **requirements.txt** | Python dependencies | No |
| **requirements-correlation.txt** | Correlation analysis deps | No |
| **.env** (optional) | Environment variables | Optional |

**Critical config.json settings:**
```json
{
  "position_sizing": {
    "bankroll": 10000  // ← YOUR CAPITAL HERE
  },
  "telegram": {
    "bot_token": "YOUR_TOKEN",  // ← Optional
    "chat_id": "YOUR_CHAT_ID"
  }
}
```

---

## 🗄️ DATA FILES (Generated During Operation)

| File/Folder | Purpose | Size Growth |
|-------------|---------|-------------|
| **polymarket_data.db** | SQLite database (all data) | ~5-10 MB/day |
| **signals.jsonl** | Trading signal log | ~1 KB/signal |
| **logs/** | Collection logs | ~1 MB/week |
| **output/** | Correlation reports, charts | Variable |
| **backups/** | Database backups (manual) | Same as DB |

**Database tables:**
- `markets` - Market metadata
- `snapshots` - Price/volume snapshots (15-min)
- `tweets` - Twitter data
- `hype_signals` - Aggregated hype metrics

---

## 📊 HELPER SCRIPTS & TOOLS

| File | Purpose |
|------|---------|
| **generate-test-data.py** | Create synthetic data for testing |
| **test-dashboard.py** | Automated dashboard tests |
| **example-usage.py** | Correlation analyzer examples |

---

## 🪟 PLATFORM-SPECIFIC

### Windows

| File | Purpose |
|------|---------|
| **deploy-windows.ps1** | PowerShell deployment script |
| **start-dashboard.bat** | Dashboard launcher |
| **run-continuous.bat** | Continuous data collection |

### Linux/Mac

| File | Purpose |
|------|---------|
| **start-dashboard.sh** | Dashboard launcher |
| **deploy-linux.sh** | Bash deployment script |

---

## 📁 DIRECTORY STRUCTURE

```
polymarket-hype-trading/
│
├── README.md                                    # Start here
├── QUICKSTART.md                                # Setup guide
├── PROJECT-STATUS.md                            # Progress tracking
├── PROJECT-DELIVERY.md                          # Delivery summary
│
├── research/                                    # Research documents
│   ├── MASTER-SYNTHESIS-POLYMARKET-STRATEGY.md
│   ├── TRADING-STRATEGY-FRAMEWORK.md
│   ├── CORRELATION-ANALYSIS-FRAMEWORK.md
│   ├── POLYMARKET-KALSHI-RESEARCH.md
│   ├── TWITTER-SENTIMENT-TRACKING.md
│   └── DATA-COLLECTION-PIPELINE.md
│
├── scripts/                                     # Python scripts
│   ├── polymarket-data-collector.py
│   ├── twitter-hype-monitor.py
│   ├── correlation-analyzer.py
│   ├── signal-generator.py
│   ├── backtest-engine.py
│   └── api.py
│
├── dashboard/
│   └── dashboard.html
│
├── config/
│   ├── config.json
│   └── requirements.txt
│
├── data/                                        # Generated
│   ├── polymarket_data.db
│   ├── signals.jsonl
│   └── logs/
│
├── output/                                      # Generated
│   ├── correlation_report.json
│   └── *.png (charts)
│
├── tests/
│   ├── test-dashboard.py
│   └── generate-test-data.py
│
└── deployment/
    ├── deploy-windows.ps1
    ├── deploy-linux.sh
    ├── start-dashboard.sh
    └── start-dashboard.bat
```

---

## 🎯 WHICH FILES DO I NEED?

### Minimum Viable (Free MVP)
```
✅ QUICKSTART.md
✅ polymarket-data-collector.py
✅ twitter-hype-monitor.py
✅ requirements.txt
✅ config.json (edit bankroll)
```

### Basic Analysis (After 7 days)
```
+ correlation-analyzer.py
+ CORRELATION-ANALYSIS-FRAMEWORK.md
```

### Full Trading System (After 30 days)
```
+ signal-generator.py
+ backtest-engine.py
+ TRADING-STRATEGY-FRAMEWORK.md
+ dashboard.html + api.py
```

### Production Deployment
```
+ DEPLOYMENT-GUIDE.md
+ deploy-windows.ps1 OR deploy-linux.sh
+ TESTING-GUIDE.md
```

---

## 📖 READING ORDER (For New Users)

**Day 0 (Before Starting):**
1. README.md (10 min)
2. MASTER-SYNTHESIS-POLYMARKET-STRATEGY.md (15 min)
3. QUICKSTART.md (5 min)
4. PROJECT-DELIVERY.md (10 min)

**Day 1 (Setup Day):**
1. DEPLOYMENT-GUIDE.md
2. Edit config.json
3. Run test collections
4. Set up automation

**Week 1 (While Collecting Data):**
1. TRADING-STRATEGY-FRAMEWORK.md
2. CORRELATION-ANALYSIS-FRAMEWORK.md
3. POLYMARKET-KALSHI-RESEARCH.md
4. TWITTER-SENTIMENT-TRACKING.md

**Day 7 (First Analysis):**
1. Run correlation-analyzer.py
2. Review output/
3. Check PROJECT-STATUS.md

**Day 30 (Decision Day):**
1. Run backtest-engine.py
2. Review results
3. Make GO/NO-GO decision

---

## 🔍 FIND A FILE BY PURPOSE

**Want to...**

- **Understand the project?** → README.md
- **Get started quickly?** → QUICKSTART.md
- **Learn the strategy?** → TRADING-STRATEGY-FRAMEWORK.md
- **Deploy to Windows?** → DEPLOYMENT-GUIDE.md (Windows section)
- **Deploy to Linux?** → DEPLOYMENT-GUIDE.md (Linux section)
- **Collect market data?** → polymarket-data-collector.py
- **Track Twitter hype?** → twitter-hype-monitor.py
- **Analyze correlations?** → correlation-analyzer.py
- **Generate trade signals?** → signal-generator.py
- **Backtest strategy?** → backtest-engine.py
- **Monitor system?** → dashboard.html + api.py
- **Test everything?** → TESTING-GUIDE.md
- **Troubleshoot?** → QUICKSTART.md (troubleshooting section)
- **Check progress?** → PROJECT-STATUS.md
- **Review deliverables?** → PROJECT-DELIVERY.md

---

## 📝 FILE MAINTENANCE

### Keep Updated
- config.json (adjust thresholds as needed)
- PROJECT-STATUS.md (track milestones)
- logs/ (monitor daily)

### Backup Regularly
- polymarket_data.db (weekly minimum)
- signals.jsonl (contains trade log)
- config.json (contains settings)

### Can Delete
- logs/*.log (after reviewing, keep last 7 days)
- output/*.png (regenerate anytime)
- test_data.db (synthetic test data)

### Never Edit
- Python scripts (unless intentional modification)
- Research documents (reference material)
- requirements.txt (managed by pip)

---

## 🚀 QUICK ACCESS CHEAT SHEET

```bash
# Start data collection
python polymarket-data-collector.py
python twitter-hype-monitor.py

# View database
sqlite3 polymarket_data.db

# Generate signals
python signal-generator.py --continuous

# Run analysis
python correlation-analyzer.py --db polymarket_data.db

# Start dashboard
./start-dashboard.sh  # or start-dashboard.bat

# Check logs
tail -f logs/collector.log
tail -f logs/twitter.log

# Backup database
cp polymarket_data.db backups/polymarket_data_$(date +%Y%m%d).db
```

---

## 🆘 HELP & SUPPORT

**Can't find a file?**
- Check this index
- Use `find . -name "filename"` (Linux/Mac)
- Use `dir /s filename` (Windows)

**File missing?**
- Re-run agent that creates it
- Check if it's in wrong directory
- Review PROJECT-DELIVERY.md for what should exist

**File too large?**
- Database: Normal growth (~5-10 MB/day)
- Logs: Delete old entries
- Output: Regenerate charts as needed

---

**Total Project Size:** ~500 MB (including 30 days of data)  
**Core Files:** ~300 KB (code + docs)  
**Data Growth:** ~150-300 MB/month

**Everything is in: C:\Users\Borat\.openclaw\workspace\**
