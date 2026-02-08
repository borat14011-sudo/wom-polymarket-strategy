# Quick Deployment Guide

## 🚀 From Zero to Paper Trading in 10 Minutes

### Step 1: Install Dependencies (2 minutes)

```bash
cd polymarket_trading_system
pip install -r requirements.txt
```

### Step 2: Configure Settings (3 minutes)

```bash
# Copy example config
cp config.example.json config.json

# Edit with your settings
nano config.json  # or use any text editor
```

**Minimum Required Settings:**
- `paper_trading`: `true` (ALWAYS start with paper trading)
- `initial_capital`: `10000.0` (or your amount)

**Optional but Recommended:**
- `telegram_bot_token`: Your Telegram bot token
- `telegram_chat_id`: Your Telegram chat ID

**For Live Trading (Later):**
- `polymarket_api_key`: Your Polymarket API key

### Step 3: Run Paper Trading (30+ days)

```bash
python trading_bot.py
```

Bot will:
- Monitor markets every 60 seconds
- Detect validated trading signals
- Execute paper trades (no real money)
- Log everything to `trading_bot.log`
- Send Telegram alerts (if configured)

### Step 4: Monitor Performance

**View Logs:**
```bash
tail -f trading_bot.log
```

**Check Telegram:**
- Will receive alerts for signals, entries, exits
- Daily performance summaries

**Generate Report (after 30 days):**
```bash
python forward_testing.py --report weekly
```

### Step 5: Evaluate & Decide

After 30+ days and 30+ trades:

```bash
python forward_testing.py --compare
```

**Decision Matrix:**

| Actual vs Expected | Action |
|--------------------|--------|
| Within 20% | ✅ Proceed to live with 10% capital |
| 20-40% below | ⚠️ Continue paper trading or use 5% capital |
| >40% below | ❌ Do NOT go live, review strategy |

### Step 6: Go Live (Only After Validation)

```bash
# Edit config.json
{
  "trading_mode": {
    "paper_trading": false,  # <-- Change to false
    "initial_capital": 1000.0  # <-- Start with 10% of intended capital
  },
  "api_credentials": {
    "polymarket_api_key": "your_real_api_key"
  }
}

# Run live bot
python trading_bot.py --live
```

**⚠️ START SMALL:** Use only 10% of intended capital for first 50 trades.

---

## 📊 Expected Timeline

| Phase | Duration | Goal |
|-------|----------|------|
| **Setup** | 1 hour | Install, configure, test |
| **Paper Trading** | 30+ days | Validate strategy, 30+ trades |
| **Evaluation** | 1 day | Compare vs backtests |
| **Live Pilot** | 30 days | Trade with 10% capital |
| **Scale Up** | 60 days | Gradually increase to 100% |

**Total:** 4-5 months to full deployment (be patient!)

---

## 🔧 Quick Troubleshooting

### Bot Not Finding Signals

**Likely Cause:** Markets don't meet strict filters.

**Check:**
- Are there <3 day markets in Politics/Crypto categories?
- Increase check interval: `"check_interval_seconds": 300` (5 min)
- Review `trading_bot.log` for filtered markets

### No Telegram Alerts

**Fix:**
1. Get bot token from [@BotFather](https://t.me/botfather)
2. Get chat ID: Message bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Update `config.json` with both values

### Bot Crashes

**Check:**
- Python version ≥3.9: `python --version`
- All dependencies installed: `pip install -r requirements.txt`
- Config file valid JSON: Use JSON validator
- Review `trading_bot.log` for errors

---

## 📁 File Overview

**Core Files (Don't Modify):**
- `signal_detector_validated.py` - Proven signal detection
- `trading_bot.py` - Production bot
- `forward_testing.py` - Performance validation

**Configuration (Edit These):**
- `config.json` - Your settings
- `requirements.txt` - Dependencies

**Documentation (Read These):**
- `README.md` - Complete system guide
- `PERFORMANCE_DOCUMENTATION.md` - Backtest results
- `DEPLOYMENT_GUIDE.md` - This file

**Generated Files (Auto-Created):**
- `trading_bot.log` - Bot logs
- `bot_state.json` - Current state
- `data/trade_history.json` - All trades
- `forward_test_report.txt` - Performance reports

---

## ✅ Pre-Flight Checklist

Before starting paper trading:

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `config.json` created and edited
- [ ] Telegram configured (optional but recommended)
- [ ] Understand expected performance (58% win rate, 80% annual return)
- [ ] Read `PERFORMANCE_DOCUMENTATION.md`
- [ ] Understand this is experimental
- [ ] Ready to monitor for 30+ days

---

## 🎯 Success Metrics (30 Days)

**Minimum Requirements:**
- 30+ trades executed
- Win rate: 45-68% (within expected range)
- No technical errors
- Logs show proper filter application

**Ideal Results:**
- 50+ trades executed
- Win rate: 55-65% (in target range)
- Profit factor: >1.5
- Max drawdown: <25%

---

## 🆘 Emergency Stop

If anything goes wrong:

1. **Press Ctrl+C** (stops bot immediately)
2. **Review logs:** `cat trading_bot.log`
3. **Check state:** `cat bot_state.json`
4. **DO NOT restart** until you understand the issue

**Critical Issues:**
- Win rate <40% after 30 trades → STOP
- Drawdown >30% → STOP
- Repeated technical errors → STOP

---

## 📞 Support Resources

**Documentation:**
- `README.md` - Full system documentation
- `PERFORMANCE_DOCUMENTATION.md` - Backtest details
- `MASTER_REAL_BACKTEST_REPORT.md` - Original analysis

**Self-Diagnosis:**
- Check logs: `trading_bot.log`
- Test signal detector: `python signal_detector_validated.py`
- Validate config: JSON validator online

---

**Ready to start?**

```bash
python trading_bot.py
```

**Watch the logs and Telegram for your first signal!** 🎯

---

**Built by:** OpenClaw Backtest Analysis Team  
**Version:** 1.0  
**Support:** Review documentation first, then troubleshoot systematically
