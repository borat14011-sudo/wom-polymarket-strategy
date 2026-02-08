# Trading Signal Generator - User Guide

**Real-time BUY/SELL signal generator for prediction market trading**

## Overview

The Signal Generator monitors your prediction market database in real-time and generates trading signals when markets meet entry criteria defined in the Trading Strategy Framework.

### What It Does

✅ **Monitors** database for new market snapshots  
✅ **Analyzes** volume, momentum, and hype signals  
✅ **Generates** BUY/SELL signals with complete trade parameters  
✅ **Manages** risk through position sizing and exposure limits  
✅ **Notifies** you via Telegram when signals fire  
✅ **Logs** all signals to JSON for record-keeping  

---

## Quick Start

### 1. Prerequisites

Ensure you have:
- Python 3.7+
- SQLite database with market data (from `polymarket-data-collector.py`)
- Hype signals (from `twitter-hype-monitor.py`) - optional but recommended

Install dependencies:
```bash
pip install requests
```

### 2. Configure Settings

Edit `config.json` to set:

**Essential:**
- `bankroll`: Your total trading capital (default: $10,000)
- Database path (default: `polymarket_data.db`)

**Optional but Recommended:**
- Telegram bot token and chat ID (for notifications)
- Signal thresholds (RVR, ROC, hype score)
- Position sizing percentages
- Risk limits

### 3. Set Up Telegram (Optional)

To receive signal notifications on Telegram:

**Step 1: Create a Bot**
1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Step 2: Get Your Chat ID**
1. Message your bot (send any text)
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find `"chat":{"id":12345678}` in the JSON response
4. Copy your chat ID

**Step 3: Update config.json**
```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "12345678"
  }
}
```

---

## Usage

### Single Scan Mode (Default)

Run once to scan all markets and generate signals:

```bash
python signal-generator.py
```

**When to use:** 
- Testing the system
- Manual trading (check periodically)
- Scheduled via cron/Task Scheduler

### Continuous Mode

Run continuously and check for signals every N seconds:

```bash
python signal-generator.py --continuous
```

**When to use:**
- Automated signal generation
- Real-time monitoring
- Keep running in background

**Custom interval:**
```bash
python signal-generator.py --continuous --interval 120
```
(Checks every 120 seconds instead of default 60)

---

## Understanding Signals

### Signal Output

When a signal fires, you'll see:

```
================================================================================
🚀 BUY SIGNAL | Confidence: HIGH
================================================================================
Market: Will Bitcoin reach $100,000 by end of February 2026?

Entry: $0.450
Position: 4.0% ($400)

Exit Levels:
  Stop Loss:     $0.396 (-12%)
  Take Profit 1: $0.486 (+8%)
  Take Profit 2: $0.518 (+15%)
  Take Profit 3: $0.563 (+25%)

Signals:
  Volume STRONG (RVR: 3.50) | Momentum MODERATE (ROC: +12.5%) | Hype STRONG (Score: 82.0)

Metrics:
  RVR: 3.50 | ROC: +12.5% | Hype: 82.0
  Liquidity: $75,000 | Spread: 2.1%

Timestamp: 2026-02-06T05:30:00
================================================================================
```

### Signal Components

**Direction:**
- **BUY** = Buy YES shares (price moving up)
- **SELL** = Buy NO shares (price moving down)

**Confidence Levels:**
- **HIGH**: 3 strong signals OR 2 strong + 1 moderate
- **MEDIUM**: 1 strong + 2 moderate
- **LOW**: 3 moderate signals

**Position Size:**
- Based on signal strength and your bankroll
- Ranges from 1-5% of bankroll
- Respects risk limits (max 25% total exposure)

**Entry Price:**
- Current market price (YES token)
- Use this as your target entry price

**Exit Levels:**
- **Stop Loss (-12%)**: Exit if price drops 12% to limit losses
- **TP1 (+8%)**: Take 25% profit when price rises 8%
- **TP2 (+15%)**: Take 50% profit when price rises 15%
- **TP3 (+25%)**: Take remaining 25% profit when price rises 25%

**Signal Metrics:**
- **RVR (Relative Volume Ratio)**: Current volume vs. average (>2.0 = surge)
- **ROC (Rate of Change)**: Price momentum over last 12 hours (>10% = strong)
- **Hype Score**: Social media sentiment/engagement (>70 = high hype)

---

## Risk Management

### Automatic Risk Checks

The signal generator **automatically prevents** risky trades:

✅ **Position Limits:**
- Single position: Max 5% of bankroll
- Category limit: Max 10% in same category (e.g., Crypto)
- Total exposure: Max 25% across all positions

✅ **Market Quality:**
- Minimum liquidity: $10,000
- Maximum spread: 5%
- Minimum time to resolution: 48 hours

✅ **Loss Limits:**
- Daily loss limit: -5% of bankroll
- Weekly loss limit: -10% of bankroll
- Monthly loss limit: -20% of bankroll

If any limit is violated, the signal is **automatically skipped** and you'll see a warning:
```
⚠ Market Name... - Daily loss limit hit: -$500.00
```

### Manual Overrides

You can adjust limits in `config.json`:

```json
{
  "position_sizing": {
    "bankroll": 10000,
    "max_single_position": 0.05,
    "max_total_exposure": 0.25
  },
  "risk_management": {
    "stop_loss_pct": -12.0,
    "daily_loss_limit_pct": -5.0
  }
}
```

---

## Configuration Reference

### Signal Thresholds

Control when signals fire:

```json
{
  "signal_thresholds": {
    "rvr_strong": 3.0,      // Volume surge >3x = STRONG
    "rvr_moderate": 2.0,    // Volume surge >2x = MODERATE
    "roc_moderate": 10.0,   // Price momentum >10% = MODERATE
    "hype_moderate": 70,    // Hype score >70 = MODERATE
    "liquidity_min": 10000  // Minimum $10K liquidity
  }
}
```

**Tuning Tips:**
- **Lower thresholds** = More signals (but lower quality)
- **Higher thresholds** = Fewer signals (but higher quality)
- Start conservative, loosen if you're missing opportunities

### Position Sizing

Control how much to bet:

```json
{
  "position_sizing": {
    "bankroll": 10000,
    "strong_3_signals": 0.04,      // 4% for 3 strong signals
    "strong_2_moderate_1": 0.03,   // 3% for 2 strong + 1 moderate
    "strong_1_moderate_2": 0.02,   // 2% for 1 strong + 2 moderate
    "moderate_3_signals": 0.01     // 1% for 3 moderate
  }
}
```

**Aggressive vs Conservative:**
- **Aggressive**: Increase percentages (max 5% per position)
- **Conservative**: Decrease percentages (min 0.5% per position)

### Exit Levels

Control profit targets and stop loss:

```json
{
  "risk_management": {
    "stop_loss_pct": -12.0,
    "take_profit_1_pct": 8.0,
    "take_profit_2_pct": 15.0,
    "take_profit_3_pct": 25.0
  }
}
```

**Risk/Reward:**
- Tighter stops (-8%) = Less risk, more stopped out
- Wider stops (-15%) = More risk, fewer false stops
- Default -12% balances both

---

## Output Files

### signals.jsonl

All signals logged in JSON Lines format:

```json
{"market_id": "abc123", "direction": "BUY", "confidence": "HIGH", ...}
{"market_id": "def456", "direction": "SELL", "confidence": "MEDIUM", ...}
```

**Use cases:**
- Import into spreadsheet for analysis
- Backtest signal performance
- Train ML models

### positions.json

Active positions (managed separately):

```json
[
  {
    "market_id": "abc123",
    "entry_price": 0.45,
    "position_size_pct": 0.04,
    "status": "ACTIVE"
  }
]
```

**Note:** This file must be manually maintained if you're tracking positions. The signal generator reads it to check exposure limits.

---

## Troubleshooting

### No Signals Generated

**Possible causes:**

1. **No data in database**
   - Run `polymarket-data-collector.py` first
   - Check: `polymarket_data.db` exists

2. **Thresholds too strict**
   - Lower RVR/ROC thresholds in `config.json`
   - Check: Are any markets showing activity?

3. **No markets meet criteria**
   - Wait for volatile markets
   - Check: Run in continuous mode to catch signals

4. **Risk limits blocking**
   - Check: Daily loss limit hit?
   - Check: Total exposure at max?

### Telegram Not Working

1. **Bot token invalid**
   - Verify token from @BotFather
   - Check: No extra spaces in config.json

2. **Chat ID wrong**
   - Get fresh chat ID from `/getUpdates`
   - Check: Message bot first before getting ID

3. **Notifications disabled**
   - Set `"enabled": true` in config.json

### Database Errors

1. **"Unable to open database file"**
   - Check: File path in config.json correct
   - Check: Database file exists

2. **"No such table: snapshots"**
   - Run `polymarket-data-collector.py` first to initialize

---

## Best Practices

### ✅ Do This

- **Start small**: Test with 1% position sizes first
- **Run continuously**: Real-time monitoring catches more signals
- **Track results**: Log your actual trades and compare to signals
- **Review daily**: Check signal quality and adjust thresholds
- **Honor stops**: Exit when stop loss hits (discipline > emotion)

### ❌ Don't Do This

- **Don't override signals manually** (trust the system or fix the rules)
- **Don't ignore risk limits** (they're there to protect you)
- **Don't chase signals** (if you miss entry, wait for next one)
- **Don't forget liquidity** (can't exit if market dries up)
- **Don't trade without data** (need history for RVR/ROC calculations)

---

## Integration with Other Tools

### Cron Job (Linux/Mac)

Run every 5 minutes:
```bash
*/5 * * * * cd /path/to/workspace && python signal-generator.py >> signal-generator.log 2>&1
```

### Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Every 5 minutes
4. Action: Start program `python.exe`
5. Arguments: `signal-generator.py`
6. Start in: `C:\path\to\workspace`

### Background Service (Screen/tmux)

```bash
# Start detached session
screen -dmS signals python signal-generator.py --continuous

# Reattach to view
screen -r signals

# Detach: Ctrl+A, D
```

---

## Advanced Usage

### Custom Bankroll Per Run

Override config bankroll:
```bash
# Edit config.json before running, or
# Modify positions.json to reflect current bankroll
```

### Signal-Specific Actions

Parse `signals.jsonl` with custom scripts:

```python
import json

# Read latest signal
with open('signals.jsonl', 'r') as f:
    lines = f.readlines()
    latest = json.loads(lines[-1])
    
    if latest['confidence'] == 'HIGH':
        # Auto-execute high confidence signals
        print(f"Execute: {latest['direction']} {latest['market_question']}")
```

### Backtesting Signals

Compare signals to actual market outcomes:

```python
# Load all signals
signals = []
with open('signals.jsonl', 'r') as f:
    for line in f:
        signals.append(json.loads(line))

# Check which would have been profitable
# (requires historical price data)
```

---

## Performance Expectations

### Realistic Goals

Based on the Trading Strategy Framework:

- **Win Rate:** 50-60% (not 80%+)
- **Average Return:** 8-15% per winning trade
- **Max Drawdown:** 15-25% (even with good risk management)
- **Signals Per Day:** 2-10 (depends on market volatility)

### Metrics to Track

**Essential:**
- Total signals generated
- Signals actually traded
- Win/loss ratio
- Average P&L per trade
- Max drawdown

**Advanced:**
- Sharpe ratio (return/risk)
- Profit factor (wins/losses)
- Recovery time after drawdown

---

## Support & Debugging

### Verbose Output

The script prints progress:

```
================================================================================
Signal Scanner - 2026-02-06 05:30:00
================================================================================
Scanning 45 active markets...

✓ Bitcoin $100K by Feb 2026? | Price: $0.45 | Vol: $125,000
  ⊘ Tesla $200 by Q1 2026 - Liquidity too low: $3,500
  ⚠ Trump Re-Election 2028 - Daily loss limit hit: -$500

✓ Generated 1 signal(s)
================================================================================
```

### Log Files

Check:
- `signals.jsonl` - All generated signals
- `positions.json` - Active positions
- Terminal output - Real-time diagnostics

### Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| No signals | Strict thresholds | Lower RVR/ROC in config |
| Too many signals | Loose thresholds | Raise RVR/ROC in config |
| Can't place trades | Exposure maxed | Close existing positions |
| Telegram fails | Invalid credentials | Re-check bot token/chat ID |

---

## Next Steps

1. ✅ **Test the system**: Run `python signal-generator.py` and verify output
2. ✅ **Configure Telegram**: Set up notifications
3. ✅ **Paper trade**: Log signals for 1-2 weeks without real money
4. ✅ **Backtest**: Compare signals to actual market outcomes
5. ✅ **Go live**: Start with small positions (1% of bankroll)
6. ✅ **Iterate**: Adjust thresholds based on results

---

## Documentation References

- **TRADING-STRATEGY-FRAMEWORK.md**: Full strategy rules and rationale
- **config.json**: All configuration options with comments
- **signal-generator.py**: Source code with inline documentation

---

## Version History

**v1.0 (2026-02-06)**
- Initial release
- Core signal generation
- Risk management
- Telegram integration
- JSON logging

---

## Questions?

Check the strategy framework first:
```bash
cat TRADING-STRATEGY-FRAMEWORK.md | grep -i "your question here"
```

Or review the config file:
```bash
cat config.json
```

---

**Remember:** This is a systematic trading tool, not a money printer. Discipline and risk management are more important than finding the perfect signal. Trade responsibly! 🎯
