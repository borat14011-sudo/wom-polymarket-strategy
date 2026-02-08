# File Structure Reference

Complete overview of all files in the Polymarket Monitor system.

## 📂 Core Components

### `monitor_daemon.py` 
**Main orchestrator** - Runs continuously, coordinates all components
- Schedules scraping every hour
- Triggers signal calculation
- Sends alerts
- Handles cleanup and logging
- **Start this to run the monitor**

### `polymarket_scraper.py`
**Data collection** - Fetches market data from Polymarket API
- Connects to Polymarket Gamma API
- Fetches top 50 markets by volume
- Parses market data (price, volume, liquidity)
- Stores snapshots in database
- Can run standalone for testing

### `rvr_calculator.py`
**Signal detection** - Analyzes data for trading opportunities
- Calculates RVR (Risk-Volume Ratio)
- Calculates ROC (Rate of Change)
- Flags markets meeting criteria
- Stores signals in database
- Can run standalone to analyze existing data

### `telegram_alerter.py`
**Notification system** - Sends alerts via Telegram
- Formats signal messages
- Sends via OpenClaw message tool
- Marks signals as alerted
- Prevents spam (cooldown period)
- Can run standalone to send pending alerts

### `database.py`
**Data persistence** - SQLite database management
- Creates database schema
- Insert/query market snapshots
- Insert/query signals
- Cleanup old data
- Provides all database functions

## ⚙️ Configuration & Setup

### `config.py`
**Centralized settings** - Easy customization
- Signal thresholds (RVR, ROC)
- Telegram settings
- Scraping frequency
- Data retention
- API endpoints
- **Edit this file to customize behavior**

### `requirements.txt`
**Python dependencies** - Minimal external libraries
- requests (HTTP requests)
- schedule (task scheduling)
- Uses built-in sqlite3

### `.gitignore`
**Version control** - Excludes runtime data
- Database files
- Log files
- Python cache
- IDE files

## 🚀 Startup Scripts

### `run-monitor.sh`
**Linux/Mac launcher** - Bash script
- Checks for Python
- Installs dependencies if needed
- Starts monitor daemon
- Usage: `bash run-monitor.sh`

### `run-monitor.bat`
**Windows launcher** - Batch script
- Same functionality as .sh
- Windows-compatible syntax
- Usage: `run-monitor.bat`

## 🧪 Testing & Utilities

### `test_system.py`
**System verification** - Tests all components
- Checks dependencies
- Tests database initialization
- Tests scraper connection
- Reports status
- Run before first deployment

### `status.py`
**Health check** - Quick status overview
- Shows database stats
- Recent activity
- Configuration
- Log status
- Run anytime to check system health

## 📚 Documentation

### `README.md`
**Complete documentation** - Full system guide
- Overview and architecture
- Installation instructions
- Usage guide
- Configuration options
- Troubleshooting
- Advanced features
- ~300 lines of detailed docs

### `QUICKSTART.md`
**Fast setup guide** - Get running in 5 minutes
- Condensed instructions
- Copy-paste commands
- Common issues
- Quick reference

### `FILES.md` (this file)
**File reference** - What each file does

## 🗄️ Runtime Files (Auto-created)

### `polymarket_data.db`
**SQLite database** - All market and signal data
- Created on first run
- Two tables: market_snapshots, signals
- Auto-cleaned every 24h (keeps 7 days)
- Can query directly with sqlite3

### `monitor.log`
**Application log** - All system activity
- Created on first run
- Timestamped entries
- Info, warnings, errors
- Use: `tail -f monitor.log` to watch live

## 📦 File Sizes (Approximate)

```
Core Components:        ~20 KB
├── monitor_daemon.py       4 KB
├── polymarket_scraper.py   5 KB
├── rvr_calculator.py       6 KB
├── telegram_alerter.py     5 KB
└── database.py             6 KB

Configuration:           ~2 KB
├── config.py               2 KB
└── requirements.txt      < 1 KB

Scripts:                 ~2 KB
├── run-monitor.sh          1 KB
└── run-monitor.bat         1 KB

Testing:                 ~7 KB
├── test_system.py          3 KB
└── status.py               4 KB

Documentation:          ~15 KB
├── README.md               8 KB
├── QUICKSTART.md           5 KB
└── FILES.md                3 KB

Runtime (grows over time):
├── polymarket_data.db    1-50 MB (auto-cleaned)
└── monitor.log           1-10 MB (grows indefinitely)

Total static size: ~50 KB
Total with runtime: ~50-100 MB
```

## 🔄 Execution Flow

```
1. User runs: python monitor_daemon.py
2. Daemon initializes database (database.py)
3. Daemon runs monitoring cycle:
   a. polymarket_scraper.py → Fetch markets
   b. database.py → Store snapshots
   c. rvr_calculator.py → Analyze signals
   d. database.py → Store signals
   e. telegram_alerter.py → Send alerts
   f. database.py → Mark alerted
4. Daemon sleeps for 60 minutes
5. Repeat step 3
```

## 🎯 Which Files to Edit

**To customize behavior:**
- `config.py` - Change all settings here

**To modify logic:**
- `rvr_calculator.py` - Change signal detection algorithm
- `telegram_alerter.py` - Change message format
- `polymarket_scraper.py` - Change data sources

**To change deployment:**
- `run-monitor.sh` / `.bat` - Change startup behavior
- `monitor_daemon.py` - Change scheduling

**Never edit:**
- `polymarket_data.db` - Managed by code
- `monitor.log` - Append-only log
- Files in `__pycache__/`

## 📋 Dependency Graph

```
monitor_daemon.py
├── database.py
├── polymarket_scraper.py
│   └── database.py
├── rvr_calculator.py
│   └── database.py
└── telegram_alerter.py
    └── database.py

All import config.py (optional)
```

## 🔐 Sensitive Files (Don't share)

- `polymarket_data.db` - Your market data
- `monitor.log` - Your activity logs
- `config.py` - Contains your Telegram username

## 📤 Shareable Files (Safe to share)

- All `.py` files (except personal config)
- All `.md` files
- `requirements.txt`
- Shell scripts

---

**Quick reference:**
- Want to run it? → `python monitor_daemon.py`
- Want to test it? → `python test_system.py`
- Want to check status? → `python status.py`
- Want to customize? → Edit `config.py`
- Want to understand? → Read `README.md`
