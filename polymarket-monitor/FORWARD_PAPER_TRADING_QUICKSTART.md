# FORWARD PAPER TRADING - QUICKSTART GUIDE
## Get Running in 15 Minutes

**Purpose:** Start validating strategies with live forward paper trading TODAY  
**Time Required:** 15 minutes setup  
**Cost:** $0  
**Risk:** Zero (no real money involved)

---

## STEP 1: VERIFY EXISTING SYSTEM (2 min)

Check that your monitoring system is running:

```bash
cd polymarket-monitor

# Check database exists
ls -lh polymarket_data.db

# Check recent data
sqlite3 polymarket_data.db "SELECT COUNT(*) FROM market_snapshots WHERE timestamp > strftime('%s', 'now', '-24 hours');"

# Should return >100 (markets scraped in last 24h)
```

**If database is empty or missing:**
```bash
# Run monitor for 1 hour to collect initial data
python monitor_daemon.py &
# Wait 1 hour, then Ctrl+C
```

---

## STEP 2: INSTALL PAPER TRADING SYSTEM (5 min)

```bash
# 1. Create paper trading tables
sqlite3 polymarket_data.db < schema_paper_trading.sql

# 2. Test signal detector V2.0
python signal_detector_v2.py

# Should show: "Scanned X markets, found Y V2.0 signals"

# 3. Test paper trader
python forward_paper_trader.py --test

# Should show: "Paper trading system initialized, $100 bankroll"
```

---

## STEP 3: START FORWARD PAPER TRADING (1 min)

```bash
# Start the integrated system
python start_forward_paper_trading.py

# Or manually add to existing monitor
python monitor_daemon.py --enable-paper-trading
```

You should see:
```
🚀 FORWARD PAPER TRADING SYSTEM STARTED

💰 Paper Bankroll: $100.00
📊 Monitoring: ACTIVE
🔔 Telegram Alerts: ENABLED

✅ System is now monitoring markets and executing paper trades!
Press Ctrl+C to stop.
```

---

## STEP 4: VERIFY IT'S WORKING (2 min)

**Check Telegram:**
- You should receive: "📝 Forward paper trading started!"

**Check Database:**
```bash
sqlite3 polymarket_data.db "SELECT COUNT(*) FROM paper_trades;"
# Should return 0 initially

# Wait 1 hour, then check again
sqlite3 polymarket_data.db "SELECT market_name, side, status FROM paper_trades ORDER BY entry_time DESC LIMIT 5;"
```

**Check Logs:**
```bash
tail -f paper_trading.log
# Should show: "Monitoring cycle started..."
```

---

## STEP 5: MONITOR PROGRESS (5 min/week)

### Daily Check (30 seconds)
```bash
python validation_analyzer.py --quick-status
```

Output:
```
📊 PAPER TRADING STATUS

Days Running: 3
Trades Executed: 8
Trades Resolved: 3
Open Positions: 5

Win Rate: 66.7% (2/3)
Total P&L: +$1.40 (+1.4%)

Next Weekly Report: Saturday 10:00 AM
```

### Weekly Report (Automatic)
Every Saturday at 10:00 AM, you'll receive a detailed Telegram report with:
- Portfolio status
- Trade statistics
- Strategy breakdown
- Filter effectiveness
- Go-live recommendation

### Manual Report Anytime
```bash
python validation_analyzer.py --generate-report
```

---

## STEP 6: GO-LIVE DECISION (Week 5)

After 30 days, run the go-live checker:

```bash
python validation_analyzer.py --check-go-live
```

Output:
```
🚦 GO-LIVE CRITERIA CHECKLIST

[✅] 30+ days of forward testing (32 days)
[✅] 20+ resolved trades (24 trades)
[✅] Win rate >55% (61.3%)
[✅] Positive total P&L (+$8.20)
[✅] Edge validated (gap: +1.3pp)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ APPROVED FOR GO-LIVE

Recommendation: Deploy $50 now
Review at 60 days for full $100
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**If APPROVED:**
```bash
# Stop paper trading
python stop_forward_paper_trading.py

# Switch to LIVE trading
python auto_trader.py YOUR_WALLET_KEY 50.0
```

**If NOT APPROVED:**
- Continue paper trading
- Review filter settings
- Iterate on strategy
- Re-check at 60 days

---

## COMMON COMMANDS

### Status Check
```bash
python validation_analyzer.py --quick-status
```

### Force Weekly Report
```bash
python validation_analyzer.py --generate-report
```

### View Recent Trades
```bash
sqlite3 polymarket_data.db "SELECT 
    market_name, 
    side, 
    entry_price, 
    status, 
    pnl_percent 
FROM paper_trades 
ORDER BY entry_time DESC 
LIMIT 10;"
```

### View Current Positions
```bash
python paper_position_manager.py --show-positions
```

Output:
```
📊 OPEN PAPER POSITIONS

1. Will Bitcoin hit $100k? (BET YES)
   Entry: 67.5% | Current: 71.2%
   Unrealized P&L: +$0.45 (+7.2%)
   Stop: 59.4% | TP1: 81.0%
   Hold: 6h 32m

2. Iran strike by Feb 15? (BET NO)
   Entry: 88.0% (NO @ 12%)
   Current: 89.5% (NO @ 10.5%)
   Unrealized P&L: +$0.18 (+2.9%)
   Stop: 89.5% (AT STOP LEVEL ⚠️)
   Hold: 14h 18m

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Open: 2 positions
Total Exposure: $12.50 (12.5%)
Unrealized P&L: +$0.63 (+5.0%)
```

### Check Signal Frequency
```bash
python signal_detector_v2.py --monitor 24
# Monitors for 24 hours, reports signal frequency
```

### Export Data for Analysis
```bash
# Export all paper trades to CSV
sqlite3 -header -csv polymarket_data.db \
  "SELECT * FROM paper_trades;" > paper_trades_export.csv

# Export validation metrics
sqlite3 -header -csv polymarket_data.db \
  "SELECT * FROM validation_metrics ORDER BY snapshot_date;" > validation_metrics.csv
```

---

## TROUBLESHOOTING

### No Signals Detected
**Symptom:** Days go by, no paper trades executed

**Check:**
```bash
# Verify historical data exists
python signal_detector_v2.py --debug

# Check filter strictness
python validation_analyzer.py --filter-analysis
```

**Solution:**
- V2.0 filters are VERY strict (by design)
- Expected: 1-3 signals/day, not every hour
- If 0 signals after 3 days, check:
  - Historical database is populated
  - Markets are actively trading
  - Filters aren't too restrictive

### Paper Trades Not Executing
**Symptom:** Signals detected, but no paper trades

**Check:**
```bash
tail -f paper_trading.log | grep ERROR
```

**Common Issues:**
- Paper trading not enabled in config.py
- Database permissions issue
- Telegram alerter failing (non-critical)

**Fix:**
```bash
# Check config
grep PAPER_TRADING config.py

# Should show:
# PAPER_TRADING_ENABLED = True
```

### Positions Not Closing
**Symptom:** Open positions exceed 30 days

**Check:**
```bash
python paper_position_manager.py --check-stale
```

**Fix:**
```bash
# Force close stale positions
python paper_position_manager.py --close-stale --days 30
```

### Telegram Alerts Not Sending
**Symptom:** Paper trades execute but no Telegram notifications

**Check:**
```bash
# Test Telegram manually
openclaw message send --channel telegram --target @YourUsername --message "Test"
```

**Fix:**
- Verify OpenClaw is configured
- Check telegram_alerter.py target username
- Alerts are optional (system works without them)

---

## CONFIGURATION OPTIONS

### Adjust Paper Bankroll
Edit `config.py`:
```python
PAPER_STARTING_BANKROLL = 100.0  # Change to 200, 500, etc
```

### Adjust Position Sizing
Edit `config.py`:
```python
PAPER_MAX_POSITION_PCT = 0.10  # 10% max per position
# For more aggressive: 0.15 (15%)
# For more conservative: 0.05 (5%)
```

### Adjust Stop-Loss
Edit `config.py`:
```python
PAPER_STOP_LOSS_PCT = 0.12  # 12% stop
# Tighter: 0.08 (8%)
# Wider: 0.15 (15%)
```

### Adjust Validation Criteria
Edit `config.py`:
```python
VALIDATION_MIN_DAYS = 30  # Minimum testing period
VALIDATION_MIN_TRADES = 20  # Minimum resolved trades
VALIDATION_TARGET_WIN_RATE = 0.55  # 55% minimum win rate
```

### Change Report Schedule
Edit `config.py`:
```python
WEEKLY_REPORT_DAY = 6  # 0=Monday, 6=Sunday
WEEKLY_REPORT_HOUR = 10  # 10:00 AM
```

---

## WHAT TO EXPECT

### Week 1
- 5-10 signals detected
- 3-7 paper trades executed
- 1-3 trades resolved
- First exits (stop-loss or take-profit)
- Initial win rate appears (too early to judge)

### Week 2
- 10-15 total signals
- 7-12 total paper trades
- 3-6 trades resolved
- Win rate stabilizing (still noisy)
- First weekly report generated

### Week 3
- 15-25 total signals
- 10-18 total paper trades
- 6-12 trades resolved
- Win rate becoming meaningful
- Filter effectiveness visible

### Week 4 (30 Days)
- 25-40 total signals
- 15-25 total paper trades
- 10-20 trades resolved ✅
- **GO-LIVE DECISION POINT**
- Win rate statistically significant
- Edge validated (or invalidated)

### Week 8 (60 Days)
- 50-80 total signals
- 35-55 total paper trades
- 25-45 trades resolved ✅
- **STRONG CONFIDENCE LEVEL**
- Consistent performance visible
- Deploy full capital decision

---

## KEY METRICS TO WATCH

### Must Track
1. **Win Rate** - Target: >55%
2. **Total P&L** - Must be positive
3. **Edge Gap** - Difference from backtest (<5pp)
4. **Sample Size** - Need 20+ resolved trades

### Nice to Track
5. **Sharpe Ratio** - Risk-adjusted returns (>1.5 ideal)
6. **Max Drawdown** - Largest peak-to-trough loss (<15% ideal)
7. **Filter Effectiveness** - Which filters are working
8. **Side Performance** - YES vs NO win rates

### Warning Signs
- Win rate <50% after 20 trades 🚨
- Negative P&L after 30 days 🚨
- Edge gap >10pp from backtest 🚨
- 5+ consecutive losses 🚨
- Max drawdown >25% 🚨

**If you see warning signs:**
1. Stop paper trading
2. Review strategy
3. Analyze losing trades
4. Adjust filters
5. Restart validation

---

## SUCCESS CHECKLIST

After 30 days, you should have:

- [ ] 30+ days of continuous operation
- [ ] 20+ resolved paper trades
- [ ] Win rate calculated (>55% target)
- [ ] Total P&L recorded (positive target)
- [ ] Edge gap measured (<5pp target)
- [ ] Filter analysis completed
- [ ] Weekly reports generated
- [ ] Go-live recommendation received

**If ALL checkboxes are ticked + win rate >55% + positive P&L:**
→ **DEPLOY REAL CAPITAL** 🚀

**If some checkboxes missing or metrics below target:**
→ **CONTINUE PAPER TRADING** (iterate strategy)

---

## NEXT STEPS AFTER GO-LIVE

Once you deploy real capital:

1. **Start small:** $50 (50% capital)
2. **Monitor closely:** Daily checks for first week
3. **Compare results:** Paper vs real performance
4. **Adjust if needed:** Position sizing, filters, etc
5. **Scale gradually:** Full $100 after 30 days
6. **Beyond $100:** Scale beyond initial capital after 90 days

**Remember:**
- Paper trading proves the strategy
- Real trading proves the execution
- Different challenges (slippage, psychology, etc)
- But you'll have empirical data backing your decision

---

## SUPPORT & RESOURCES

### Documentation
- `FORWARD_PAPER_TRADING_SYSTEM.md` - Full architecture
- `VALIDATION_REPORT_TEMPLATE.md` - Report format
- `GO_LIVE_CHECKLIST.md` - Decision framework

### Code Files
- `forward_paper_trader.py` - Paper trade execution
- `paper_position_manager.py` - Position tracking
- `outcome_tracker.py` - Resolution validation
- `validation_analyzer.py` - Performance analysis

### Database Queries
```bash
# View all tables
sqlite3 polymarket_data.db ".tables"

# Schema of paper_trades
sqlite3 polymarket_data.db ".schema paper_trades"

# Recent activity
sqlite3 polymarket_data.db "SELECT * FROM paper_trades ORDER BY entry_time DESC LIMIT 5;"
```

---

## FINAL CHECKLIST - READY TO START?

Before running `start_forward_paper_trading.py`:

- [ ] Existing monitor_daemon is working
- [ ] Database has 24h+ of market data
- [ ] signal_detector_v2.py detects signals
- [ ] Telegram alerts configured (optional)
- [ ] Paper trading tables created
- [ ] Config settings reviewed

**All checked? RUN THIS:**
```bash
python start_forward_paper_trading.py
```

**Then sit back and let it collect data for 30 days!** 📊

---

**Questions? Check the logs:**
```bash
tail -f paper_trading.log
```

**Good luck! You're now validating strategies like a quant fund.** 🎯
