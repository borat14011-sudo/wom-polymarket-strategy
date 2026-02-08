# Iran Position Monitor - Setup Guide

## Overview
API-based monitoring for "US strikes Iran by February 13" market position.
**No browser automation required** - uses Polymarket Gamma API directly.

## Position Details
- **Entry Price:** 12% (0.12)
- **Entry Time:** 1:00 PM CST, February 6, 2026
- **Position Size:** $4.20 (paper trading)
- **Stop-Loss:** 10.6% (0.106)
- **Market:** "US strikes Iran by February 13"

## Files
- `api_monitor.py` - Main monitoring script (Windows-safe, no emoji encoding)
- `historical_scraper.py` - Fixed emoji encoding issues for Windows console
- `setup_iran_monitor_task.ps1` - Windows Task Scheduler setup
- `cron_config_iran.txt` - Linux/macOS cron configuration

## Prerequisites

### Python Installation
Make sure Python 3.7+ is installed:
```bash
python --version
# or
python3 --version
```

### Required Packages
```bash
pip install requests
```

## Quick Start

### 1. Test Manual Run
```bash
cd polymarket-monitor
python api_monitor.py
```

Expected output:
```
======================================================================
IRAN POSITION MONITOR
======================================================================
Time: 2026-02-06 17:20:00

MARKET INFO:
  Question: Will the US strike Iran by February 13?
  Market ID: 0x...
  Volume 24h: $X,XXX.XX

POSITION:
  Entry Price: 12.0%
  Current Price: XX.X%
  Price Change: +X.X% (+X.X%)
  Position Size: $4.20

P/L:
  Unrealized P/L: $+X.XX
  Entry Time: 2026-02-06 13:00:00 CST

RISK MANAGEMENT:
  Stop-Loss: 10.6%
  Stop Hit: No
  Risk Amount: $X.XX
  Reward Potential: $X.XX
  RVR Ratio: X.XXx
======================================================================
```

### 2. Check Logs
```bash
# View monitoring log
cat logs/api_monitor.log

# Or tail for live updates
tail -f logs/api_monitor.log
```

## Windows Setup (Task Scheduler)

### Automatic Setup (Recommended)
Run PowerShell **as Administrator**:

```powershell
cd C:\Users\Borat\.openclaw\workspace\polymarket-monitor
.\setup_iran_monitor_task.ps1
```

This creates a scheduled task that runs every 15 minutes.

### Manual Setup
1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task
3. Name: `PolymarketIranMonitor`
4. Trigger: Daily, repeat every 15 minutes
5. Action: Start a program
   - Program: `python`
   - Arguments: `api_monitor.py`
   - Start in: `C:\Users\Borat\.openclaw\workspace\polymarket-monitor`
6. Finish and enable the task

### Verify Task
```powershell
# Check task status
Get-ScheduledTask -TaskName "PolymarketIranMonitor"

# Run task immediately (test)
Start-ScheduledTask -TaskName "PolymarketIranMonitor"

# Check results
Get-Content logs\api_monitor.log -Tail 50
```

### Remove Task
```powershell
Unregister-ScheduledTask -TaskName "PolymarketIranMonitor" -Confirm:$false
```

## Linux/macOS Setup (Cron)

### Install Cron Job
```bash
# Edit crontab
crontab -e

# Add this line (replace path):
*/15 * * * * cd /path/to/polymarket-monitor && python3 api_monitor.py >> logs/iran_monitor_cron.log 2>&1

# Save and exit (Ctrl+X, Y, Enter in nano)
```

### Verify Cron Job
```bash
# List installed cron jobs
crontab -l

# Check logs
tail -f logs/iran_monitor_cron.log
```

### Remove Cron Job
```bash
# Edit crontab
crontab -e

# Delete the line, save and exit
```

## Alternative: Continuous Mode

Run monitor in loop mode (checks every 5 minutes):
```bash
python api_monitor.py --loop --interval 300
```

To run in background:
```bash
# Linux/macOS
nohup python api_monitor.py --loop --interval 300 &

# Windows (separate PowerShell window)
Start-Process python -ArgumentList "api_monitor.py --loop --interval 300" -NoNewWindow
```

## Monitoring & Alerts

### Position Status
The monitor checks:
- ✅ Current market price
- ✅ Unrealized P/L
- ✅ Stop-loss violations
- ✅ Risk/reward metrics

### Stop-Loss Alert
If price drops to 10.6% or below:
```
[ALERT] STOP-LOSS HIT - CONSIDER EXITING POSITION!
```

### Check Position Anytime
```bash
python api_monitor.py
```

## Troubleshooting

### "Market not found"
- Market may have closed or been delisted
- Check search terms in `api_monitor.py` (line 40)
- Verify market exists on Polymarket website

### "API request failed"
- Check internet connection
- Gamma API may be down (check status.polymarket.com)
- Rate limiting (wait 1 minute and retry)

### Encoding Errors (Windows)
All emoji characters have been replaced with ASCII tags like `[INFO]`, `[ERROR]`, etc.
No encoding issues should occur.

### Python Not Found
```bash
# Windows: Install from python.org
# Linux: sudo apt install python3
# macOS: brew install python3
```

## Files Modified

### Fixed Emoji Encoding
`historical_scraper.py` - All emoji replaced with ASCII:
- 🔍 → [SCRAPE]
- ✅ → [SUCCESS]
- ❌ → [ERROR]
- ⚠️ → [WARN]
- 📊 → [STATS]
- 🚀 → [START]

This ensures Windows console compatibility.

## Position Exit Strategy

Monitor will alert when:
1. **Stop-loss hit:** Price ≤ 10.6%
2. **Target reached:** Price approaches 100%
3. **Market expiry:** February 13, 2026

**Action:** Check logs daily and respond to alerts.

## Support

For issues or questions:
- Check logs: `logs/api_monitor.log`
- Review this guide
- Test manual run: `python api_monitor.py`

## Success Verification

✅ Script runs without errors  
✅ No encoding crashes on Windows  
✅ Logs created in `logs/` folder  
✅ Position data displayed correctly  
✅ Scheduled task active (Windows) or cron running (Linux)  

**Your Iran position is now monitored via API!** 🎯
