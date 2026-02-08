# Quick Reference Guide
## Forward Paper Trading System

---

## 🚀 Start/Stop

### Start System
```bash
python start_paper_trading.py
```

### Stop System
Press **Ctrl+C** in the console

### Restart
Just run start command again - all data persists

---

## 📊 Monitoring

### Dashboard
**http://localhost:8080**
- Real-time stats
- Trade history
- Auto-refreshes every 60s

### Telegram Alerts
Automatic notifications for:
- 📝 Paper trade entries
- 💰 Position exits (TP/SL)
- 🏁 Market resolutions
- 📊 Daily reports (10 AM)

### Log Files
- `paper_trading_system.log` - Main system
- `paper_trading.log` - Trade details

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

### Check Resolutions
```bash
python outcome_tracker.py
```

### View Dashboard Only
```bash
python dashboard.py
```

### Run Single Cycle
```bash
python paper_trading_main.py --cycle
```

### Initialize Database
```bash
python paper_trading_main.py --init
```

---

## 📁 Files

### Main Scripts
- `start_paper_trading.py` - **START HERE**
- `paper_trading_main.py` - Main orchestrator
- `forward_paper_trader.py` - Trade execution
- `paper_position_manager.py` - Position monitoring
- `outcome_tracker.py` - Resolution tracking
- `daily_reporter.py` - Performance reports
- `dashboard.py` - Web interface

### Data Files
- `polymarket_data.db` - SQLite database
- `paper_trading_system.log` - System log

### Documentation
- `DEPLOYMENT_GUIDE.md` - Full deployment guide
- `30_DAY_VALIDATION_PLAN.md` - Validation roadmap
- `QUICK_REFERENCE.md` - This file

---

## 🎯 Success Criteria (30 Days)

Must pass ALL 5:
1. ✅ **30+ days** of forward testing
2. ✅ **20+ resolved** trades
3. ✅ **Win rate ≥55%**
4. ✅ **Positive P&L**
5. ✅ **Edge gap <5pp** vs backtest

---

## 🔧 Troubleshooting

### System Not Starting
```bash
# Check Python version (need 3.7+)
python --version

# Install dependencies
pip install requests schedule

# Initialize database
python paper_trading_main.py --init
```

### No Signals Detected
- Normal if markets are slow
- Wait for next cycle (runs every 60 min)
- Check existing signals: Dashboard → Recent Trades

### Dashboard Won't Load
```bash
# Try different port
python dashboard.py --port 8081
```

### Telegram Not Working
```bash
# Test telegram_alerter
python telegram_alerter.py
```

### Check System Health
```bash
# View recent logs
Get-Content paper_trading_system.log -Tail 50
```

---

## 📊 Key Metrics

### Win Rate
```
Win Rate = Wins / Resolved Trades × 100
Target: 55-65%
```

### ROI
```
ROI = (Exit Price - Entry Price) / Entry Price × 100
Target: 10-20% average
```

### Total P&L
```
Total P&L = Sum of all closed trades
Target: Positive after 30 days
```

### Edge Gap
```
Edge Gap = |Forward Win Rate - Backtest Win Rate|
Target: <5 percentage points
```

---

## 🚦 Decision Matrix (Day 30)

### ✅ APPROVED (8/8 criteria)
→ Deploy $50 at Day 31

### ⚠️ CAUTION (6-7/8 criteria)
→ Deploy $25 OR wait to Day 45

### ❌ REJECTED (<6/8 criteria)
→ Do NOT deploy, continue testing

---

## 💾 Database Queries

```python
import sqlite3
conn = sqlite3.connect('polymarket_data.db')
cursor = conn.cursor()

# Get all trades
cursor.execute("SELECT * FROM paper_trades")
trades = cursor.fetchall()

# Get win rate
cursor.execute("""
    SELECT 
        COUNT(*) as resolved,
        SUM(CASE WHEN trade_correct = 1 THEN 1 ELSE 0 END) as wins
    FROM paper_trades
    WHERE resolved = 1
""")
resolved, wins = cursor.fetchone()
win_rate = (wins / resolved * 100) if resolved > 0 else 0
print(f"Win Rate: {win_rate:.1f}%")

# Get P&L
cursor.execute("SELECT SUM(pnl_dollars) FROM paper_trades WHERE status != 'OPEN'")
total_pnl = cursor.fetchone()[0] or 0
print(f"Total P&L: ${total_pnl:.2f}")
```

---

## 🎯 Daily Checklist (5 min)

- [ ] Check dashboard (http://localhost:8080)
- [ ] Review Telegram alerts
- [ ] Verify system still running
- [ ] Note any unusual activity

---

## 📅 Weekly Checklist (15 min)

- [ ] Review week's performance
- [ ] Check win rate trend
- [ ] Analyze best/worst trades
- [ ] Update progress to 30-day goal
- [ ] Document learnings

---

## 🔒 Safety Features

### Automatic Limits
- Max 10% per position
- Max 30% total exposure
- Max 5 open positions
- Mandatory 12% stop-loss

### Circuit Breakers
- Stops if daily loss >15%
- Stops after 5 consecutive losses
- Stops if win rate <40% after 20 trades

### NO REAL MONEY
- 100% simulated trades
- No API keys needed
- Cannot execute real trades
- All data is paper only

---

## 📞 Quick Support

### Something Not Working?
1. Check logs: `paper_trading_system.log`
2. Restart system: `python start_paper_trading.py`
3. Reinitialize DB: `python paper_trading_main.py --init`

### Need Help?
- Check `DEPLOYMENT_GUIDE.md` for detailed instructions
- Check `30_DAY_VALIDATION_PLAN.md` for validation process
- Review log files for error messages

---

## 📈 Expected Activity

### Week 1
- 10-20 signals
- 5-15 trades
- 3-10 resolved

### Week 2-3
- 20-40 signals
- 15-30 trades
- 10-20 resolved

### Week 4
- 30-50 total trades
- 20-30 resolved
- Decision ready

---

## 💡 Pro Tips

1. **Don't panic** on losses - variance is normal
2. **Trust the process** - 30 days reveals truth
3. **Document learnings** - what works/doesn't
4. **Be patient** - wait for 20+ resolved before judging
5. **Follow the data** - not emotions

---

## 🎓 Learning Questions

Track answers over 30 days:

- Which markets perform best?
- Does NO-side outperform YES-side?
- Are filters actually helpful?
- What's optimal position size?
- Which exit strategy works best?

---

## ✅ Pre-Launch Checklist

- [ ] Python 3.7+ installed
- [ ] Dependencies installed
- [ ] Telegram configured
- [ ] Port 8080 available
- [ ] Read deployment guide
- [ ] Understand 30-day plan

**Ready?**
```bash
python start_paper_trading.py
```

---

## 🎯 Remember

**This is validation, not gambling.**

**Data will tell you if edge is real.**

**Don't deploy capital until proven.**

**30 days → truth.**

Good luck! 🚀

---

*Quick Reference v1.0*
