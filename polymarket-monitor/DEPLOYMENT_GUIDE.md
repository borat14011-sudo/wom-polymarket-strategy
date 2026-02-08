# Forward Paper Trading System - Deployment Guide

## 🎯 Quick Start (5 Minutes)

### Prerequisites
- Python 3.7+
- Internet connection
- Telegram configured (for alerts)

### Installation

```bash
# 1. Navigate to polymarket-monitor directory
cd polymarket-monitor

# 2. Install dependencies (if not already installed)
pip install requests schedule

# 3. Start the system
python start_paper_trading.py
```

That's it! The system is now running.

---

## 📊 What Just Happened?

When you run `start_paper_trading.py`, the system:

1. ✅ **Checks requirements** - Python version, packages
2. ✅ **Initializes database** - Creates all necessary tables
3. ✅ **Tests components** - Verifies all modules load correctly
4. ✅ **Starts dashboard** - Opens web UI at http://localhost:8080
5. ✅ **Sends Telegram alert** - Confirms system is running
6. ✅ **Begins monitoring** - Starts 60-minute monitoring cycle

---

## 🔄 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 MONITORING CYCLE                        │
│                 (Every 60 minutes)                      │
└────────────┬────────────────────────────────────────────┘
             │
             ├─→ 1. Process New Signals
             │      ├─ Check signal_detector output
             │      ├─ Evaluate entry conditions
             │      ├─ Execute paper trades
             │      └─ Send entry alerts
             │
             ├─→ 2. Monitor Open Positions
             │      ├─ Fetch current prices
             │      ├─ Check stop-loss triggers
             │      ├─ Check take-profit triggers
             │      ├─ Execute exits
             │      └─ Send exit alerts
             │
             └─→ 3. Check Market Resolutions
                    ├─ Query Polymarket API
                    ├─ Record outcomes
                    ├─ Validate trade correctness
                    └─ Send outcome alerts

┌─────────────────────────────────────────────────────────┐
│                  DAILY REPORT                           │
│                  (10:00 AM daily)                       │
└─────────────────────────────────────────────────────────┘
             │
             └─→ Generate and send comprehensive report:
                 ├─ Portfolio status (bankroll, P&L)
                 ├─ Trade statistics (win rate, ROI)
                 ├─ Strategy breakdown (YES/NO sides)
                 └─ Go-live assessment (when ready)
```

---

## 📁 File Structure

### Core Components

```
polymarket-monitor/
├── start_paper_trading.py           # 🚀 START HERE - One-command launcher
│
├── paper_trading_main.py            # Main orchestrator
├── forward_paper_trader.py          # Paper trade execution
├── paper_position_manager.py        # Position monitoring & exits
├── outcome_tracker.py               # Market resolution tracking
├── daily_reporter.py                # Performance reporting
├── dashboard.py                     # Web monitoring interface
│
├── paper_trading_db.py              # Database initialization
├── polymarket_data.db               # SQLite database (auto-created)
│
└── paper_trading_system.log         # System log (auto-created)
```

### Database Tables

The system creates 4 main tables:

1. **paper_trades** - All paper trade entries/exits
2. **paper_position_ticks** - Price tick history
3. **market_resolutions** - Resolved market outcomes
4. **validation_metrics** - Daily performance snapshots

---

## 🎮 Using the System

### Monitoring Dashboard

Open **http://localhost:8080** in your browser to see:

- **Real-time stats**: Bankroll, P&L, win rate
- **Trade history**: Recent entries and exits
- **Position status**: Open positions
- **Auto-refresh**: Updates every 60 seconds

### Telegram Alerts

You'll automatically receive notifications for:

**🎯 Paper Trade Entries**
```
📝 PAPER TRADE ENTRY (TEST - NO REAL MONEY)

🎯 Signal: BET NO
📊 Market: Will Bitcoin hit $100k by March?
💰 Position: $6.25 (6.25% of bankroll)
📈 Entry: NO @ 12.0%

🔬 Signal Strength:
   RVR: 3.2x (volume spike)
   ROC: +18.5% (24h momentum)
   ...
```

**💰 Position Exits**
```
🎯 PAPER TRADE EXIT

📊 Market: Will Bitcoin hit $100k by March?
✅ Outcome: TAKE_PROFIT_1

💰 Entry: NO @ 12.0%
📉 Exit: NO @ 9.4%
⏱️ Hold Time: 8.3 hours

💵 P&L: +$0.41 (+6.6%)
```

**🏁 Market Resolutions**
```
🏁 MARKET RESOLVED

📊 Market: Will Bitcoin hit $100k by March?
🎯 Our Bet: NO @ 12.0%
✅ Actual Outcome: NO

💰 Trade Result: CORRECT Prediction
```

**📊 Daily Reports** (10:00 AM)
```
📊 DAILY PAPER TRADING REPORT

💰 Portfolio Status:
   Starting: $100.00
   Current: $108.50
   📈 Total P&L: +$8.50 (+8.5%)

📈 Trade Statistics (28 days):
   Total Trades: 23
   Resolved: 18
   Open: 5
   
   ✅ Win Rate: 61.1% (11/18)
   ...
```

---

## 🛠️ Manual Commands

### Generate Report Now
```bash
python daily_reporter.py
```

### Check Open Positions
```bash
python paper_position_manager.py
```

### Check Market Resolutions
```bash
python outcome_tracker.py
```

### Run Dashboard Only
```bash
python dashboard.py
```

### Run Single Monitoring Cycle (Manual)
```bash
python paper_trading_main.py --cycle
```

### Initialize Database (Reset)
```bash
python paper_trading_main.py --init
```

---

## 🚦 System Status & Health

### Check If Running

Look for these indicators:

1. **Console output**: System logs should be flowing
2. **Dashboard**: http://localhost:8080 should load
3. **Log file**: `paper_trading_system.log` updating
4. **Telegram**: You received startup notification

### Monitor Logs

```bash
# Windows PowerShell
Get-Content paper_trading_system.log -Tail 50 -Wait

# Unix/Mac
tail -f paper_trading_system.log
```

### Troubleshooting

**❌ "Module not found" error**
```bash
pip install requests schedule
```

**❌ Dashboard won't load**
- Check if port 8080 is already in use
- Try: `python dashboard.py --port 8081`

**❌ No Telegram alerts**
- Verify `telegram_alerter.py` is configured
- Test manually: `python telegram_alerter.py`

**❌ No signals detected**
- Normal if markets are slow
- Check `signals` table in database
- Wait for next monitoring cycle (60 min)

---

## 📊 Expected Activity

### Week 1 (Days 1-7)
- **Signals**: 10-20 signals
- **Trades**: 5-15 paper trades executed
- **Resolutions**: 3-10 resolved
- **Status**: System ramp-up

### Weeks 2-4 (Days 8-30)
- **Signals**: 30-60 signals
- **Trades**: 20-40 paper trades
- **Resolutions**: 15-25 resolved
- **Status**: Core data collection

### Day 30 Milestone
- **Target**: 20+ resolved trades
- **Action**: First go-live assessment
- **Decision**: Deploy $50 or continue testing

---

## 🎯 30-Day Validation Plan

### Success Criteria (All Must Pass)

1. ✅ **30+ days of forward testing**
2. ✅ **20+ resolved trades**
3. ✅ **Win rate ≥55%**
4. ✅ **Positive total P&L**
5. ✅ **Edge validated** (within 5pp of backtest)

### Timeline

```
Day 1-7:    System initialization, first signals
Day 8-14:   Data accumulation
Day 15-21:  Pattern validation
Day 22-28:  Pre-assessment review
Day 29:     Generate 30-day report
Day 30:     GO-LIVE DECISION

If approved:
Day 31:     Deploy $50 USDC (50% capital)
Day 60:     Review, deploy remaining $50 if sustained
Day 90:     Scale-up decision
```

### Decision Framework

**✅ APPROVED** (Deploy $50)
- All 5 criteria passed
- Strategy edge confirmed
- Risk-reward favorable

**⚠️ CAUTION** (Deploy $25 or wait)
- 4/5 criteria passed
- Edge uncertain
- Need more data

**❌ REJECTED** (Continue testing or pivot)
- <4 criteria passed
- Strategy not working
- Rethink approach

---

## 💾 Data Backup

### Backup Database
```bash
# Windows
copy polymarket_data.db polymarket_data_backup.db

# Unix/Mac
cp polymarket_data.db polymarket_data_backup.db
```

### Export Reports
```bash
# Generate comprehensive report
python daily_reporter.py > report_$(date +%Y%m%d).txt
```

---

## 🛑 Stopping the System

### Graceful Shutdown
1. Press **Ctrl+C** in the console
2. System will generate final report
3. All data is saved automatically

### Restart
```bash
python start_paper_trading.py
```

All data persists in database - you can stop/start anytime.

---

## 🔒 Safety Features

### NO REAL MONEY
- System is 100% simulated
- No API keys required for trading
- No connection to your wallet
- Cannot execute real trades

### Circuit Breakers
- Stops new trades if daily loss >15%
- Stops after 5 consecutive losses
- Stops if win rate drops below 40%

### Position Limits
- Max 10% per position
- Max 30% total exposure
- Max 5 open positions
- Mandatory 12% stop-loss

---

## 📈 Performance Metrics

### Key Indicators to Watch

1. **Win Rate**: Target 55-65%
2. **Average ROI**: Target 10-20%
3. **Max Drawdown**: Keep below 15%
4. **Sharpe Ratio**: Target >1.0
5. **Edge Gap**: Keep within 5pp of backtest

### Red Flags

- ❌ Win rate <50% after 20 trades
- ❌ Consecutive losses >5
- ❌ Daily drawdown >20%
- ❌ Edge gap >10pp from backtest

If you see red flags: **Stop, analyze, don't deploy capital.**

---

## 🎓 Learning & Iteration

### What to Track
1. Which markets perform best?
2. Does NO-side have edge vs YES-side?
3. Are certain categories more profitable?
4. Do filters actually help?
5. What's optimal position sizing?

### Iterate Strategy
- Adjust filters based on data
- Refine entry criteria
- Optimize exit targets
- Test variations in parallel

**Remember**: This is validation AND learning phase!

---

## 📞 Support & Logs

### Log Files
- `paper_trading_system.log` - Main system log
- `paper_trading.log` - Trade-specific log

### Database Queries
```python
import sqlite3
conn = sqlite3.connect('polymarket_data.db')
cursor = conn.cursor()

# Get all trades
cursor.execute("SELECT * FROM paper_trades")
trades = cursor.fetchall()

# Get stats
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN trade_correct = 1 THEN 1 ELSE 0 END) as wins,
        AVG(pnl_percent) as avg_roi
    FROM paper_trades
    WHERE resolved = 1
""")
stats = cursor.fetchone()
```

---

## ✅ Deployment Checklist

Before starting:
- [ ] Python 3.7+ installed
- [ ] Dependencies installed (`pip install requests schedule`)
- [ ] Telegram configured (optional but recommended)
- [ ] Port 8080 available (for dashboard)
- [ ] Monitoring setup reviewed

After starting:
- [ ] System started successfully
- [ ] Dashboard accessible at http://localhost:8080
- [ ] Telegram startup notification received
- [ ] Log file created and updating
- [ ] First monitoring cycle completed

---

## 🎯 Summary

**To start**: `python start_paper_trading.py`

**To monitor**: http://localhost:8080

**To stop**: Press Ctrl+C

**Timeline**: 30 days → go-live decision

**Goal**: Validate 60%+ win rate before deploying $100 USDC

---

**Ready to start?**

```bash
python start_paper_trading.py
```

Good luck! May your edge be real and your drawdowns minimal. 🚀

---

*Last updated: 2026-02-07*
