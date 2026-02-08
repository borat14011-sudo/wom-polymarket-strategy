# 🚀 DEPLOYMENT GUIDE - Production Setup

**For:** Polymarket X Hype Trading System  
**Target:** Windows/Linux/Mac automated deployment  
**Time:** 15 minutes from zero to running

---

## 📋 PRE-FLIGHT CHECKLIST

### System Requirements
- [x] Python 3.8+ installed
- [x] 2GB+ RAM available
- [x] 5GB+ disk space
- [x] Internet connection (for APIs)
- [x] Command line access

### Optional (Recommended)
- [ ] Telegram account (for alerts)
- [ ] Paid X/Twitter API key (if snscrape breaks)
- [ ] PostgreSQL (if scaling beyond SQLite)

---

## ⚡ QUICK DEPLOY (5 Commands)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python polymarket-data-collector.py

# 3. Test Twitter scraping
python twitter-hype-monitor.py

# 4. Set up automation (choose your OS below)
# LINUX/MAC:
crontab -e
# Add these lines:
*/15 * * * * cd /path/to/workspace && python polymarket-data-collector.py >> logs/collector.log 2>&1
*/15 * * * * cd /path/to/workspace && python twitter-hype-monitor.py >> logs/twitter.log 2>&1

# WINDOWS:
# Use deploy-windows.bat (see below)

# 5. Verify running
tail -f logs/collector.log
```

**Done!** System now collecting data every 15 minutes.

---

## 🪟 WINDOWS DEPLOYMENT

### Option A: Task Scheduler (GUI)

**1. Create Collector Task:**
- Open Task Scheduler
- Create Basic Task → Name: "Polymarket Collector"
- Trigger: Daily
- Action: Start a program
  - Program: `python.exe`
  - Arguments: `C:\path\to\workspace\polymarket-data-collector.py`
  - Start in: `C:\path\to\workspace`
- Settings:
  - Run whether user is logged on or not
  - Run with highest privileges
  - Repeat task every 15 minutes for duration of 1 day

**2. Create Twitter Task:**
- Same steps, but:
  - Name: "Twitter Hype Monitor"
  - Arguments: `twitter-hype-monitor.py`

### Option B: PowerShell Script (Automated)

Create `deploy-windows.ps1`:

```powershell
# Polymarket Hype Trading - Windows Deployment Script

$WorkspaceDir = $PSScriptRoot
$PythonExe = (Get-Command python).Path

# Create logs directory
New-Item -ItemType Directory -Force -Path "$WorkspaceDir\logs"

# Test Python dependencies
Write-Host "Testing dependencies..."
python -c "import requests, sqlite3, pandas; print('✓ Dependencies OK')"

# Run initial collection
Write-Host "Running initial data collection..."
python "$WorkspaceDir\polymarket-data-collector.py"

# Create Task Scheduler tasks
Write-Host "Setting up automation..."

# Collector task
$CollectorAction = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "$WorkspaceDir\polymarket-data-collector.py" `
    -WorkingDirectory $WorkspaceDir

$CollectorTrigger = New-ScheduledTaskTrigger -Daily -At 00:00
$CollectorSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Repeat every 15 minutes
$CollectorTrigger.Repetition = $(New-ScheduledTaskTrigger -Once -At 00:00 -RepetitionInterval (New-TimeSpan -Minutes 15)).Repetition

Register-ScheduledTask `
    -TaskName "Polymarket-Collector" `
    -Action $CollectorAction `
    -Trigger $CollectorTrigger `
    -Settings $CollectorSettings `
    -Force

# Twitter task
$TwitterAction = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "$WorkspaceDir\twitter-hype-monitor.py" `
    -WorkingDirectory $WorkspaceDir

$TwitterTrigger = New-ScheduledTaskTrigger -Daily -At 00:00
$TwitterTrigger.Repetition = $(New-ScheduledTaskTrigger -Once -At 00:00 -RepetitionInterval (New-TimeSpan -Minutes 15)).Repetition

Register-ScheduledTask `
    -TaskName "Twitter-Hype-Monitor" `
    -Action $TwitterAction `
    -Trigger $TwitterTrigger `
    -Settings $CollectorSettings `
    -Force

Write-Host "✓ Deployment complete!"
Write-Host "Tasks running every 15 minutes."
Write-Host "Check logs: $WorkspaceDir\logs\"
```

**Run:** `powershell -ExecutionPolicy Bypass -File deploy-windows.ps1`

### Option C: Simple Batch Script (Always Running)

Create `run-continuous.bat`:

```batch
@echo off
cd /d %~dp0

:loop
echo [%date% %time%] Running data collection...
python polymarket-data-collector.py >> logs\collector.log 2>&1
python twitter-hype-monitor.py >> logs\twitter.log 2>&1

echo [%date% %time%] Sleeping 15 minutes...
timeout /t 900 /nobreak

goto loop
```

**Run:** Double-click `run-continuous.bat` or run in Command Prompt.

---

## 🐧 LINUX DEPLOYMENT

### Systemd Service (Recommended for servers)

**1. Create service files:**

`/etc/systemd/system/polymarket-collector.service`:
```ini
[Unit]
Description=Polymarket Data Collector
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/workspace
ExecStart=/usr/bin/python3 /path/to/workspace/polymarket-data-collector.py
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/polymarket-collector.timer`:
```ini
[Unit]
Description=Run Polymarket Collector every 15 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min

[Install]
WantedBy=timers.target
```

**2. Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable polymarket-collector.timer
sudo systemctl start polymarket-collector.timer
sudo systemctl status polymarket-collector.timer
```

**3. Repeat for twitter-hype-monitor:**
```bash
# Create twitter-hype-monitor.service and .timer
# Same structure as above
```

### Cron (Simple, works everywhere)

```bash
crontab -e

# Add these lines:
*/15 * * * * cd /home/user/workspace && /usr/bin/python3 polymarket-data-collector.py >> logs/collector.log 2>&1
*/15 * * * * cd /home/user/workspace && /usr/bin/python3 twitter-hype-monitor.py >> logs/twitter.log 2>&1

# Save and exit
```

**Verify cron is running:**
```bash
sudo systemctl status cron
crontab -l
```

---

## 🍎 MACOS DEPLOYMENT

### LaunchAgents (Recommended)

**1. Create plist files:**

`~/Library/LaunchAgents/com.polymarket.collector.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.polymarket.collector</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/workspace/polymarket-data-collector.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/workspace</string>
    <key>StartInterval</key>
    <integer>900</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/path/to/workspace/logs/collector.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/workspace/logs/collector-error.log</string>
</dict>
</plist>
```

**2. Load agents:**
```bash
launchctl load ~/Library/LaunchAgents/com.polymarket.collector.plist
launchctl load ~/Library/LaunchAgents/com.polymarket.twitter.plist
```

**3. Verify:**
```bash
launchctl list | grep polymarket
```

### Cron (Alternative)

Same as Linux cron setup above.

---

## 📊 MONITORING DEPLOYMENT

### Check if running:

**Linux/Mac:**
```bash
# Check cron logs
grep CRON /var/log/syslog

# Check processes
ps aux | grep python

# Check our logs
tail -f logs/collector.log
tail -f logs/twitter.log
```

**Windows:**
```powershell
# Check Task Scheduler
Get-ScheduledTask | Where-Object {$_.TaskName -like "*Polymarket*"}

# Check logs
Get-Content logs\collector.log -Tail 50
Get-Content logs\twitter.log -Tail 50
```

### Verify data collection:

```bash
# Check database exists and growing
ls -lh polymarket_data.db

# Query row counts
sqlite3 polymarket_data.db "SELECT COUNT(*) FROM markets;"
sqlite3 polymarket_data.db "SELECT COUNT(*) FROM snapshots;"
sqlite3 polymarket_data.db "SELECT COUNT(*) FROM tweets;"

# Check most recent data
sqlite3 polymarket_data.db "SELECT MAX(timestamp) FROM snapshots;"
```

**Expected:**
- Database size grows ~5-10 MB/day
- New snapshots every 15 minutes
- New tweets every 15 minutes (if any)

---

## 🔧 CONFIGURATION

### Edit config.json (Before Deployment)

```json
{
  "position_sizing": {
    "bankroll": 10000  // YOUR CAPITAL HERE
  },
  "telegram": {
    "enabled": false,  // Set true after setup
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  },
  "thresholds": {
    "min_volume_24h": 100000,  // Adjust if too many/few markets
    "min_liquidity": 10000
  }
}
```

### Environment Variables (Optional)

Create `.env` file:
```bash
POLYMARKET_DB_PATH=polymarket_data.db
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id
MIN_VOLUME_24H=100000
```

Load in scripts:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 🚨 TROUBLESHOOTING DEPLOYMENT

### Issue: Cron job not running

**Debug:**
```bash
# Check cron service
sudo systemctl status cron

# Check cron logs
grep CRON /var/log/syslog

# Test script manually
cd /path/to/workspace
python3 polymarket-data-collector.py

# Check permissions
ls -la polymarket-data-collector.py
chmod +x polymarket-data-collector.py
```

### Issue: Task Scheduler not running (Windows)

**Debug:**
- Open Task Scheduler
- Find task → Right-click → Run
- Check "Last Run Result" (should be 0x0 for success)
- Check "Last Run Time"
- View History tab

### Issue: Python not found

**Fix:**
```bash
# Find Python
which python3
which python

# Update cron/task with full path
# Example: /usr/bin/python3 or C:\Python39\python.exe
```

### Issue: Database locked

**Cause:** Multiple scripts accessing DB simultaneously

**Fix:**
```bash
# Check for running processes
ps aux | grep python

# Kill if needed
pkill -f polymarket-data-collector

# Restart
```

### Issue: Logs not updating

**Check:**
```bash
# Verify log directory exists
mkdir -p logs

# Check disk space
df -h

# Check permissions
ls -la logs/
```

---

## 🛡️ SECURITY CONSIDERATIONS

### File Permissions

```bash
# Make scripts executable (Linux/Mac)
chmod +x *.py

# Protect config
chmod 600 config.json

# Protect database
chmod 600 polymarket_data.db
```

### API Keys

**DO NOT:**
- Commit config.json to git
- Share Telegram bot tokens
- Post API keys publicly

**DO:**
- Use .env files
- Add to .gitignore
- Rotate keys periodically

### Database Backups

```bash
# Daily backup script
sqlite3 polymarket_data.db ".backup polymarket_data_$(date +%Y%m%d).db"

# Cron backup
0 3 * * * cd /path/to/workspace && sqlite3 polymarket_data.db ".backup backups/polymarket_data_$(date +\%Y\%m\%d).db"
```

---

## 📈 SCALING UP

### When to upgrade:

**From SQLite to PostgreSQL:**
- Database >1 GB
- Multiple concurrent readers
- Need better concurrency

**From free scraping to paid API:**
- snscrape breaks frequently
- Need reliable data
- Budget allows ($100+/mo)

**From local to cloud:**
- Need 24/7 uptime
- Want remote access
- Scaling to multiple markets

### Cloud Deployment

**Options:**
- AWS EC2 t3.micro ($10/mo)
- DigitalOcean Droplet ($5/mo)
- Google Cloud e2-micro (free tier)
- Raspberry Pi at home (one-time $50)

**Steps:**
1. Provision server
2. SSH in
3. Clone/upload workspace
4. Follow Linux deployment steps
5. Set up monitoring

---

## ✅ POST-DEPLOYMENT CHECKLIST

After deployment, verify:

- [ ] Cron/Task Scheduler shows tasks
- [ ] Database file exists and growing
- [ ] Logs updating every 15 minutes
- [ ] No errors in logs
- [ ] Markets table populated
- [ ] Snapshots being recorded
- [ ] Tweets being collected
- [ ] Hype signals generated

**Day 1 checklist:**
- [ ] Monitor logs hourly first day
- [ ] Verify data quality
- [ ] Check for errors
- [ ] Ensure continuous operation

**Week 1 checklist:**
- [ ] Daily log review
- [ ] Database size check
- [ ] Data quality audit
- [ ] Adjust thresholds if needed

---

## 🆘 SUPPORT

**If deployment fails:**

1. Check QUICKSTART.md (simpler guide)
2. Review error logs
3. Test scripts manually
4. Verify dependencies installed
5. Check file paths absolute (not relative)

**Common fixes:**
- Use absolute paths in cron/scheduler
- Ensure Python in PATH
- Check file permissions
- Verify network access
- Confirm disk space available

---

## 🎯 NEXT STEPS AFTER DEPLOYMENT

**Day 1-7:**
- Monitor data collection
- Verify quality
- No action needed (just watch)

**Day 7:**
- Run correlation-analyzer.py
- Check for preliminary signals

**Day 30:**
- Run backtest-engine.py
- Make GO/NO-GO decision

**Day 45+:**
- Paper trade if backtest passed
- Deploy signal-generator.py continuous mode

---

**Deployment complete!** System now running autonomously. ✅

**Monitor:** `tail -f logs/*.log`  
**Stop:** Kill cron job / Task Scheduler task  
**Restart:** Re-run deployment script
