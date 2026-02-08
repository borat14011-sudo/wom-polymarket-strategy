# Production Deployment Checklist - Polymarket Trading System

**Version:** 1.0  
**Last Updated:** 2026-02-06  
**System:** Polymarket Automated Trading System  
**Deployment Date:** ___________________  
**Deployed By:** ___________________

---

## ⚠️ CRITICAL WARNING

This system trades with REAL MONEY. Every step in this checklist must be completed and verified. Do not skip steps. Do not rush. When in doubt, STOP and seek guidance.

---

## Pre-Deployment Checklist

### 1. Environment Setup

**Python Version**
```bash
# Verify Python 3.9+
python --version
# Expected: Python 3.9.x or higher

# If using virtual environment (RECOMMENDED)
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```
- [ ] Python 3.9+ installed and verified
- [ ] Virtual environment created (if using)
- [ ] Virtual environment activated

**Dependencies**
```bash
# Install all requirements
pip install -r requirements.txt

# Verify critical packages
pip list | grep -E "pandas|numpy|requests|pyyaml|python-telegram-bot|schedule"

# Test imports
python -c "import pandas, numpy, requests, yaml, telegram, schedule; print('✓ All imports successful')"
```
- [ ] All dependencies installed without errors
- [ ] No version conflicts reported
- [ ] Import test successful
- [ ] Package versions documented: ___________________

**Path Configuration**
```bash
# Verify workspace paths exist
python -c "import os; print('Workspace:', os.getcwd()); print('Config:', os.path.exists('config.yaml')); print('Data:', os.path.exists('data'))"

# Check write permissions
touch test_write.tmp && rm test_write.tmp && echo "✓ Write permissions OK" || echo "✗ Write permission FAILED"
```
- [ ] All required directories exist
- [ ] Write permissions verified
- [ ] No path conflicts

---

### 2. Configuration Validation

**Load and Verify config.yaml**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))" && echo "✓ Valid YAML" || echo "✗ YAML syntax error"

# Check required keys
python validate_config.py
```

**Manual Review - config.yaml**
- [ ] `api_key` → Should be `${POLYMARKET_API_KEY}` (environment variable, NOT hardcoded)
- [ ] `base_url` → Verify correct endpoint (production vs testnet)
- [ ] `database_path` → Absolute or relative path exists
- [ ] `log_level` → Set to `INFO` for production (not DEBUG)
- [ ] `risk_limits.max_position_size` → Appropriate for capital ($500 start = max $100 per position)
- [ ] `risk_limits.max_portfolio_exposure` → Set to 0.8 or lower
- [ ] `risk_limits.stop_loss_percent` → Set to 0.15 or tighter
- [ ] `telegram.enabled` → true/false (optional)
- [ ] `telegram.chat_id` → Correct if enabled
- [ ] `telegram.bot_token` → Should be `${TELEGRAM_BOT_TOKEN}` (environment variable)

**Backup Original Config**
```bash
cp config.yaml config.yaml.backup.$(date +%Y%m%d)
```
- [ ] Configuration backed up
- [ ] All values reviewed and confirmed
- [ ] No hardcoded secrets

---

### 3. Database Initialization

**Create Database Directory**
```bash
mkdir -p data
chmod 700 data  # Owner only (Linux/Mac)
```

**Initialize Database**
```bash
# Run initialization script
python initialize_db.py

# Verify tables created
python -c "import sqlite3; conn = sqlite3.connect('data/polymarket.db'); print('Tables:', conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall()); conn.close()"
```

Expected tables:
- `markets`
- `market_snapshots`
- `trades`
- `positions`
- `performance`
- `alerts`

- [ ] Database file created: `data/polymarket.db`
- [ ] All tables exist
- [ ] Database schema version logged: ___________________
- [ ] No initialization errors

**Set File Permissions**
```bash
# Linux/Mac
chmod 600 data/polymarket.db
ls -l data/polymarket.db  # Should show -rw-------

# Windows (PowerShell)
icacls data\polymarket.db /inheritance:r /grant:r "$env:USERNAME:(R,W)"
```
- [ ] Database file permissions set to 600 (owner read/write only)
- [ ] Permissions verified

---

### 4. API Connectivity Test

**Set Environment Variables**
```bash
# Linux/Mac
export POLYMARKET_API_KEY="your_api_key_here"
export TELEGRAM_BOT_TOKEN="your_bot_token_here"  # Optional

# Windows (PowerShell)
$env:POLYMARKET_API_KEY="your_api_key_here"
$env:TELEGRAM_BOT_TOKEN="your_bot_token_here"  # Optional

# Verify set
echo $POLYMARKET_API_KEY  # Should show key (Linux/Mac)
echo $env:POLYMARKET_API_KEY  # Windows
```
- [ ] Environment variables set
- [ ] Variables persist across terminal sessions (added to .bashrc/.zshrc or system environment)

**Test API Connection**
```bash
# Test authentication and basic API call
python test_api_connectivity.py

# Expected output:
# ✓ API authentication successful
# ✓ Market data retrieved
# ✓ Account balance retrieved
# ✓ Rate limits: OK
```
- [ ] API authentication successful
- [ ] Market data retrieved
- [ ] Account balance retrieved
- [ ] Current balance documented: $___________________
- [ ] Rate limits verified
- [ ] Response times acceptable (<2s for queries)

**Network Requirements**
- [ ] Stable internet connection (test with `ping 8.8.8.8 -c 10`)
- [ ] No proxy issues
- [ ] Firewall allows outbound HTTPS (port 443)
- [ ] DNS resolution working

---

### 5. Telegram Bot Configuration (Optional)

**Test Bot Token**
```bash
# Test bot API
curl https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe

# Expected: JSON with bot username and id
```
- [ ] Bot token valid
- [ ] Bot username confirmed: ___________________

**Get Chat ID**
```bash
# Send a message to your bot, then:
curl https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates | grep chat

# Or run helper script
python get_telegram_chat_id.py
```
- [ ] Chat ID obtained: ___________________
- [ ] Chat ID added to config.yaml

**Test Notification**
```bash
python -c "from telegram_notifier import send_notification; send_notification('🚀 Production deployment test - ignore')"
```
- [ ] Test notification received
- [ ] Timestamp correct
- [ ] Formatting correct

**Skip if not using Telegram:**
- [ ] N/A - Telegram disabled in config

---

### 6. Backup System Test

**Create Backup Directory**
```bash
mkdir -p backups
chmod 700 backups
```

**Test Manual Backup**
```bash
# Run backup script
python backup_database.py

# Verify backup created
ls -lh backups/
# Should see: polymarket_backup_YYYYMMDD_HHMMSS.db
```
- [ ] Backup directory created
- [ ] Manual backup successful
- [ ] Backup file size reasonable (check with `ls -lh`)
- [ ] Backup restoration tested:
  ```bash
  # Test restore to temp location
  cp backups/polymarket_backup_*.db /tmp/test_restore.db
  python -c "import sqlite3; conn = sqlite3.connect('/tmp/test_restore.db'); print('Tables:', len(conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall())); conn.close()"
  rm /tmp/test_restore.db
  ```

**Automated Backup Schedule**
- [ ] Backup script added to cron/Task Scheduler (see Maintenance section)
- [ ] Backup retention policy set (keep 30 days)
- [ ] Backup verification script scheduled

---

### 7. Log Directory Setup

**Create Log Directory**
```bash
mkdir -p logs
chmod 700 logs
```

**Test Logging**
```bash
# Run a test that generates logs
python -c "from logger import setup_logger; logger = setup_logger(); logger.info('Production deployment test'); logger.error('Test error message')"

# Check log file
ls -lh logs/
tail -20 logs/trading_system_$(date +%Y%m%d).log
```
- [ ] Log directory created
- [ ] Log file created
- [ ] Log rotation configured (daily rotation, keep 90 days)
- [ ] Log format verified (timestamp, level, message)
- [ ] No sensitive data in logs (verify no API keys, passwords)

**Log File Permissions**
```bash
# Linux/Mac
chmod 640 logs/*.log
ls -l logs/

# Windows: Restrict to current user
icacls logs\*.log /inheritance:r /grant:r "$env:USERNAME:(R,W)"
```
- [ ] Log files have restricted permissions (640 or equivalent)

---

### 8. Disk Space Verification

**Check Available Space**
```bash
# Linux/Mac
df -h .
# Need at least 5GB free

# Windows (PowerShell)
Get-PSDrive C | Select-Object Used,Free
```
- [ ] >5GB free space confirmed
- [ ] Available space: ___________________GB
- [ ] Disk monitoring alerts configured (alert if <2GB free)

**Estimate Storage Growth**
```bash
# Estimate: ~10MB per day for market data
# At $500 capital: ~5-10 trades per day = 50KB
# Logs: ~5MB per day
# Total: ~20MB per day = 600MB per month
```
- [ ] Storage growth estimate documented
- [ ] 3-month projection calculated: ___________________GB
- [ ] Cleanup scripts scheduled

---

## Security Checklist

### 1. Environment Variables (No Hardcoded Secrets)

**Verify No Hardcoded Keys**
```bash
# Search for potential hardcoded secrets
grep -r "sk-.*" . --exclude-dir=venv --exclude-dir=.git
grep -r "api_key.*=.*['\"]" . --exclude-dir=venv --exclude-dir=.git
grep -r "bot_token.*=.*['\"]" . --exclude-dir=venv --exclude-dir=.git

# Should return NO results or only environment variable references
```
- [ ] No hardcoded API keys found
- [ ] No hardcoded tokens found
- [ ] config.yaml uses `${VAR}` syntax
- [ ] .env file in .gitignore (if using)

**Environment Variable Persistence**
```bash
# Linux/Mac - Add to ~/.bashrc or ~/.zshrc
echo 'export POLYMARKET_API_KEY="your_key"' >> ~/.bashrc
echo 'export TELEGRAM_BOT_TOKEN="your_token"' >> ~/.bashrc

# Windows - Set permanently
setx POLYMARKET_API_KEY "your_key"
setx TELEGRAM_BOT_TOKEN "your_token"

# Verify persistence (open new terminal)
echo $POLYMARKET_API_KEY
```
- [ ] Environment variables persist across sessions
- [ ] Variables documented in secure location (not in code repo)

---

### 2. File Permissions

**Database File**
```bash
# Linux/Mac
chmod 600 data/polymarket.db
ls -l data/polymarket.db  # Should show -rw-------
```
- [ ] Database: 600 (owner read/write only)

**Log Files**
```bash
chmod 640 logs/*.log
ls -l logs/
```
- [ ] Log files: 640 (owner read/write, group read)

**Configuration Files**
```bash
chmod 600 config.yaml
chmod 600 .env  # If using
```
- [ ] config.yaml: 600
- [ ] .env: 600 (if exists)

**Backup Files**
```bash
chmod 600 backups/*.db
```
- [ ] Backup files: 600

**Verify Permissions**
```bash
find . -name "*.db" -o -name "config.yaml" -o -name ".env" | xargs ls -l
```
- [ ] All sensitive files have restricted permissions

---

### 3. Sensitive Data in Logs

**Review Logging Code**
```bash
# Search for potentially logged sensitive data
grep -r "logger.*api_key" . --exclude-dir=venv
grep -r "logger.*password" . --exclude-dir=venv
grep -r "logger.*token" . --exclude-dir=venv
```
- [ ] No API keys logged
- [ ] No tokens logged
- [ ] Only masked/truncated sensitive values in logs

**Review Existing Logs**
```bash
grep -i "api_key\|token\|password" logs/*.log
# Should return NO matches or only masked values like "sk-****"
```
- [ ] Existing logs clean
- [ ] Masking function verified in code

---

### 4. Firewall Configuration (If Exposing Dashboard)

**Check Current Rules**
```bash
# Linux
sudo ufw status

# Windows
netsh advfirewall show currentprofile
```

**Dashboard Setup (If Applicable)**
```bash
# Only allow localhost by default
# Bind to 127.0.0.1:5000, not 0.0.0.0:5000

# If exposing publicly:
# - Use strong authentication
# - Use HTTPS only
# - Whitelist specific IPs
# - Use reverse proxy (nginx/Caddy)
```
- [ ] N/A - No dashboard exposed
- [ ] Dashboard only on localhost
- [ ] Dashboard behind authentication
- [ ] Dashboard uses HTTPS
- [ ] Firewall rules documented

---

### 5. HTTPS for Dashboard (If Public)

**Certificate Setup**
```bash
# Use Let's Encrypt (certbot)
sudo certbot --nginx -d yourdomain.com

# Or generate self-signed for testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout selfsigned.key -out selfsigned.crt
```
- [ ] N/A - No public dashboard
- [ ] SSL certificate installed
- [ ] Certificate expiry date: ___________________
- [ ] Auto-renewal configured
- [ ] HTTPS enforcement verified (HTTP redirects to HTTPS)

---

## Data Collection Phase

### 1. Cron Job Configuration

**Create Cron Jobs**
```bash
# Edit crontab
crontab -e

# Add entries:
# Data collection every 5 minutes
*/5 * * * * cd /path/to/workspace && /path/to/venv/bin/python collect_market_data.py >> logs/cron.log 2>&1

# Daily backup at 2 AM
0 2 * * * cd /path/to/workspace && /path/to/venv/bin/python backup_database.py >> logs/backup.log 2>&1

# Weekly database maintenance (Sunday 3 AM)
0 3 * * 0 cd /path/to/workspace && /path/to/venv/bin/python maintain_database.py >> logs/maintenance.log 2>&1

# Daily performance report at 6 PM
0 18 * * * cd /path/to/workspace && /path/to/venv/bin/python daily_report.py >> logs/reports.log 2>&1

# Verify crontab
crontab -l
```

**Windows Task Scheduler**
```powershell
# Create task for data collection
schtasks /create /tn "Polymarket_DataCollection" /tr "C:\path\to\venv\Scripts\python.exe C:\path\to\workspace\collect_market_data.py" /sc minute /mo 5 /ru "SYSTEM"

# Create task for daily backup
schtasks /create /tn "Polymarket_Backup" /tr "C:\path\to\venv\Scripts\python.exe C:\path\to\workspace\backup_database.py" /sc daily /st 02:00 /ru "SYSTEM"

# Verify tasks
schtasks /query /tn "Polymarket_DataCollection"
schtasks /query /tn "Polymarket_Backup"
```

- [ ] Data collection cron job created (every 5 min)
- [ ] Backup cron job created (daily)
- [ ] Maintenance cron job created (weekly)
- [ ] Report cron job created (daily)
- [ ] Cron jobs verified: `crontab -l` or Task Scheduler
- [ ] Log output redirected properly
- [ ] Email notifications configured (optional)

---

### 2. Initial Data Collection

**Run Initial Collection**
```bash
# Collect initial market data
python collect_market_data.py --initial

# Verify data collected
python -c "import sqlite3; conn = sqlite3.connect('data/polymarket.db'); print('Markets:', conn.execute('SELECT COUNT(*) FROM markets').fetchone()[0]); print('Snapshots:', conn.execute('SELECT COUNT(*) FROM market_snapshots').fetchone()[0]); conn.close()"
```
- [ ] Initial collection successful
- [ ] Markets collected: ___________________
- [ ] Snapshots created: ___________________
- [ ] No API errors
- [ ] Collection time logged: ___________________

**Wait for Multiple Cycles**
```bash
# Wait 30 minutes, then check again
sleep 1800
python verify_data_collection.py

# Should show multiple snapshots per market
```
- [ ] Multiple collection cycles completed
- [ ] Data accumulating properly
- [ ] No gaps in time series
- [ ] Cron job running automatically

---

### 3. Data Quality Check

**Run Quality Checks**
```bash
python data_quality_check.py

# Checks:
# - No NULL values in critical fields
# - Timestamps sequential
# - Prices within reasonable bounds
# - No duplicate snapshots
# - Data freshness (<10 minutes old)
```

**Expected Output:**
```
✓ No NULL values in critical fields
✓ Timestamps sequential
✓ Prices within bounds (0.01 to 0.99)
✓ No duplicate snapshots
✓ Data fresh (last update: 3 minutes ago)
PASS: Data quality check passed
```

- [ ] All quality checks passed
- [ ] No anomalies detected
- [ ] Data coverage adequate (>80% of target markets)
- [ ] Quality check report saved
- [ ] Issues documented (if any): ___________________

---

### 4. Backup Scheduled

**Verify Backup Schedule**
```bash
# Check cron or Task Scheduler (see section 1)
crontab -l | grep backup

# Test backup manually
python backup_database.py

# Verify backup file
ls -lh backups/ | tail -5
```
- [ ] Backup schedule verified
- [ ] Test backup successful
- [ ] Backup file size reasonable
- [ ] Backup location has sufficient space
- [ ] Backup verification script created

**Backup Retention Policy**
```bash
# Add cleanup script to cron
# Keep 30 days of backups
0 4 * * * find /path/to/backups -name "*.db" -mtime +30 -delete
```
- [ ] Retention policy configured (30 days)
- [ ] Cleanup script scheduled
- [ ] Off-site backup considered (cloud storage, external drive)

---

## Validation Phase

### 1. 7-Day Correlation Test

**Objective:** Verify that market data collection is reliable and correlations are computable.

**Run Correlation Analysis**
```bash
# After 7 days of data collection
python correlation_analysis.py --days 7

# Expected: Correlation matrix for all tracked markets
```
- [ ] 7 days of data collected (start date: ___________________)
- [ ] Correlation matrix computed
- [ ] Strong correlations identified (r > 0.7): ___________________
- [ ] Weak correlations identified (r < 0.3): ___________________
- [ ] No data gaps or anomalies
- [ ] Results documented in `reports/correlation_7day.csv`

**Visual Inspection**
```bash
# Generate correlation heatmap
python plot_correlations.py --days 7 --output reports/correlation_heatmap_7day.png

# Review PNG file
```
- [ ] Heatmap generated
- [ ] Correlations make sense (related markets correlate)
- [ ] No unexpected perfect correlations (1.0) - suggests data duplication

---

### 2. 30-Day Backtest

**Objective:** Validate strategy performance on historical data before risking capital.

**Run Backtest**
```bash
# After 30 days of data collection (start date: ___________________)
python backtest.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD --capital 500

# Expected output:
# Total trades: X
# Win rate: Y%
# Sharpe ratio: Z
# Max drawdown: W%
# Final capital: $XXX
```
- [ ] 30 days of data collected
- [ ] Backtest completed successfully
- [ ] Performance metrics:
  - Total trades: ___________________
  - Win rate: ___________________%
  - Sharpe ratio: ___________________
  - Max drawdown: ___________________%
  - Final capital: $___________________
- [ ] Results documented in `reports/backtest_30day.json`

**Acceptance Criteria**
- [ ] Win rate > 52% (break-even with fees is ~51%)
- [ ] Sharpe ratio > 0.5 (acceptable risk-adjusted return)
- [ ] Max drawdown < 20% (tolerable loss)
- [ ] Positive total return (even if small)

**If Criteria NOT Met:**
- [ ] Strategy parameters adjusted
- [ ] Re-run backtest
- [ ] Document changes: ___________________
- [ ] DO NOT proceed to live trading

---

### 3. Paper Trading Setup

**Objective:** Simulate live trading without real money to validate execution logic.

**Configure Paper Trading Mode**
```bash
# Edit config.yaml
# Set: paper_trading: true

# Verify setting
grep paper_trading config.yaml
# Should show: paper_trading: true
```
- [ ] Paper trading mode enabled in config
- [ ] Paper trading flag verified

**Run Paper Trading**
```bash
# Start paper trading bot
python trading_bot.py --paper-trading

# Let run for at least 7 days
# Monitor logs daily
tail -f logs/trading_system_*.log
```
- [ ] Paper trading started (date: ___________________)
- [ ] Running for 7+ days
- [ ] Monitoring daily
- [ ] No execution errors
- [ ] Order logic validated (correct sizing, timing, limits)

**Paper Trading Results**
```bash
# After 7 days
python paper_trading_report.py

# Expected metrics:
# - Simulated trades executed
# - Simulated P&L
# - No critical errors
```
- [ ] Paper trading completed (7+ days)
- [ ] Simulated trades: ___________________
- [ ] Simulated P&L: $___________________
- [ ] No critical errors
- [ ] Execution logic verified
- [ ] Results match backtest expectations (roughly)

---

### 4. GO/NO-GO Decision

**Review Checklist:**
- [ ] 7-day correlation test PASSED
- [ ] 30-day backtest PASSED (all acceptance criteria met)
- [ ] Paper trading PASSED (7+ days, no errors)
- [ ] All security checks PASSED
- [ ] Risk management configured correctly
- [ ] Emergency procedures documented
- [ ] Team alignment (if applicable)

**Decision:**
- [ ] **GO** - Proceed to live trading
- [ ] **NO-GO** - Do not proceed (document reason: ___________________)

**Required Signatures:**
- Deployed by: ___________________ Date: ___________________
- Approved by: ___________________ Date: ___________________

**If NO-GO:**
- Document blockers: ___________________
- Set next review date: ___________________
- Return to validation phase

---

## Go-Live Phase

### 1. Start with Micro Capital ($500)

**Pre-Go-Live Checklist:**
- [ ] Paper trading disabled: `paper_trading: false` in config.yaml
- [ ] Account balance verified: $___________________
- [ ] Risk limits configured for $500 capital:
  - `max_position_size: 100` ($100 per position = 20% of capital)
  - `max_portfolio_exposure: 0.8` (max $400 at risk)
  - `stop_loss_percent: 0.15` (15% stop loss)
- [ ] Emergency stop configured
- [ ] Monitoring dashboard ready
- [ ] Telegram notifications enabled (if using)

**Gradual Ramp-Up Plan:**
```
Week 1: $500 (2 concurrent positions max)
Week 2-3: $500 (4 concurrent positions max if performing well)
Week 4+: Consider increasing capital if:
  - Win rate > 55%
  - Max drawdown < 10%
  - No critical errors
  - Confidence high
```
- [ ] Ramp-up plan documented
- [ ] Capital increase thresholds defined

---

### 2. Risk Limits Confirmed

**Double-Check Risk Settings**
```bash
# Verify risk limits in config.yaml
grep -A 10 "risk_limits:" config.yaml
```

Expected for $500 starting capital:
```yaml
risk_limits:
  max_position_size: 100  # $100 per trade
  max_positions: 4  # Max 4 concurrent positions
  max_portfolio_exposure: 0.8  # Max 80% capital at risk
  stop_loss_percent: 0.15  # 15% stop loss
  daily_loss_limit: 100  # Stop trading if lose $100 in one day
  max_leverage: 1.0  # No leverage
```

- [ ] `max_position_size` appropriate (≤20% of capital)
- [ ] `max_positions` conservative (≤5 for $500)
- [ ] `max_portfolio_exposure` ≤0.8
- [ ] `stop_loss_percent` ≤0.20 (tighter is safer)
- [ ] `daily_loss_limit` set (suggest 20% of capital)
- [ ] `max_leverage` = 1.0 (no leverage for first month)

**Test Risk Limits**
```bash
# Simulate risky scenario
python test_risk_limits.py

# Should see:
# ✓ Position size limit enforced
# ✓ Portfolio exposure limit enforced
# ✓ Daily loss limit enforced
# ✓ Stop loss triggers correctly
```
- [ ] All risk limits enforced
- [ ] No bypass logic or errors

---

### 3. Circuit Breakers Tested

**Verify Circuit Breaker Logic**
```bash
# Test emergency stop
python test_circuit_breakers.py

# Scenarios tested:
# 1. API failure (3 consecutive errors) → STOP
# 2. Daily loss limit exceeded → STOP
# 3. Unexpected position size → STOP
# 4. Database corruption detected → STOP
# 5. Manual emergency stop → STOP
```

- [ ] Circuit breaker #1: API failure (3 errors) → STOP ✓
- [ ] Circuit breaker #2: Daily loss limit → STOP ✓
- [ ] Circuit breaker #3: Position size anomaly → STOP ✓
- [ ] Circuit breaker #4: Database corruption → STOP ✓
- [ ] Circuit breaker #5: Manual emergency stop → STOP ✓

**Emergency Stop Procedure**
```bash
# Create emergency stop flag
touch EMERGENCY_STOP

# Bot checks for this file every loop
# If exists: close all positions, stop trading, send alert
```
- [ ] Emergency stop mechanism tested
- [ ] Notification sent when triggered
- [ ] Positions closed automatically

**Recovery Procedure**
```bash
# After resolving issue:
rm EMERGENCY_STOP
python trading_bot.py --restart

# Verify clean restart
```
- [ ] Recovery procedure documented
- [ ] Recovery tested

---

### 4. Emergency Contacts Listed

**Primary Contact:**
- Name: ___________________
- Phone: ___________________
- Email: ___________________
- Telegram: ___________________

**Backup Contact:**
- Name: ___________________
- Phone: ___________________
- Email: ___________________

**Polymarket Support:**
- Email: support@polymarket.com
- Discord: https://discord.gg/polymarket
- Twitter: @Polymarket

**Critical Scenarios:**
- **Account locked:** Contact Polymarket support immediately
- **Bot malfunction:** Execute emergency stop, assess logs
- **Market manipulation suspected:** Stop trading, report to Polymarket
- **Database corruption:** Restore from latest backup, verify integrity
- **API key compromised:** Regenerate immediately, update environment variables

- [ ] All contacts documented
- [ ] Contacts verified (phone/email tested)
- [ ] Emergency procedures printed and accessible

---

### 5. Runbook for Common Issues

**See RUNBOOK.md for detailed procedures.**

Quick reference:
- [ ] Bot won't start → Check logs, API key, database
- [ ] No trades executing → Check risk limits, market liquidity
- [ ] Unexpected losses → Emergency stop, review trades
- [ ] Database errors → Restore from backup
- [ ] API rate limit → Reduce polling frequency

- [ ] Runbook reviewed
- [ ] Runbook accessible (bookmarked/printed)

---

## Monitoring

### 1. Health Checks Every 5 Minutes

**Automated Health Check**
```bash
# Add to cron
*/5 * * * * cd /path/to/workspace && /path/to/venv/bin/python health_check.py >> logs/health.log 2>&1

# Health check script verifies:
# - Bot process running
# - API connectivity
# - Database accessible
# - Recent trades logged (<1 hour)
# - No critical errors in logs
# - Disk space available
```

**Expected Output:**
```
[OK] Bot process running (PID: 12345)
[OK] API connectivity (response time: 234ms)
[OK] Database accessible
[OK] Last trade: 23 minutes ago
[OK] No critical errors
[OK] Disk space: 12.3 GB free
```

- [ ] Health check script created
- [ ] Health check scheduled (every 5 min)
- [ ] Health check logs reviewed
- [ ] All checks passing

---

### 2. Alert Thresholds Configured

**Critical Alerts (Immediate Action Required):**
- Daily loss limit exceeded ($100 for $500 capital)
- API authentication failure
- Database corruption
- Emergency stop triggered
- Unexpected position > `max_position_size`

**Warning Alerts (Monitor Closely):**
- Win rate drops below 50% (over 20 trades)
- Drawdown exceeds 15%
- API response time > 3 seconds
- No trades in 4 hours (during market activity)
- Disk space < 2GB

**Info Alerts:**
- Daily performance summary
- Weekly P&L report
- New market detected

**Configure Alert Channels**
```yaml
# config.yaml
alerts:
  critical:
    - telegram  # Immediate push notification
    - email     # Backup notification
  warning:
    - telegram
  info:
    - email
```

- [ ] Critical alerts configured
- [ ] Warning alerts configured
- [ ] Info alerts configured
- [ ] Test alert sent and received:
  ```bash
  python test_alerts.py --level critical
  ```

---

### 3. Dashboard Accessible

**Dashboard Setup (Optional)**
```bash
# Run dashboard server
python dashboard.py --port 5000

# Access at: http://localhost:5000
```

**Dashboard Metrics:**
- Real-time P&L
- Open positions
- Trade history (last 24h)
- Win rate
- Sharpe ratio
- Active markets
- System health

- [ ] Dashboard running (if applicable)
- [ ] Dashboard accessible at: ___________________
- [ ] All metrics displaying correctly
- [ ] Dashboard secured (authentication enabled)
- [ ] Dashboard bookmarked

**If No Dashboard:**
- [ ] N/A - Using Telegram notifications only
- [ ] N/A - Using log files only

---

### 4. Daily Review Scheduled

**Daily Review Checklist** (5-10 minutes)
- [ ] Review P&L: `python daily_report.py`
- [ ] Check open positions
- [ ] Review unusual trades (losses >10%)
- [ ] Check health check logs: `grep ERROR logs/health.log`
- [ ] Verify backups completed: `ls -lh backups/ | tail -1`
- [ ] Review Telegram alerts
- [ ] Spot-check data quality

**Daily Review Time:**
- Preferred time: ___________________ (e.g., 6:00 PM daily)
- Backup reviewer: ___________________ (if applicable)

**Daily Review Log:**
- Create: `reports/daily_review_log.md`
- Format:
  ```markdown
  # Daily Review Log
  
  ## 2026-02-06
  - P&L: +$12.50
  - Open positions: 3
  - Win rate: 58%
  - Issues: None
  - Action items: None
  
  ## 2026-02-07
  ...
  ```

- [ ] Daily review scheduled (calendar reminder set)
- [ ] Daily review log created
- [ ] Review process documented

---

## Maintenance

### 1. Weekly Database Vacuum

**Why:** SQLite databases fragment over time. VACUUM defragments and reclaims space.

**Schedule Weekly VACUUM**
```bash
# Add to cron (Sunday 3 AM)
0 3 * * 0 cd /path/to/workspace && /path/to/venv/bin/python maintain_database.py >> logs/maintenance.log 2>&1
```

**maintain_database.py Should Include:**
```python
import sqlite3

conn = sqlite3.connect('data/polymarket.db')
print("Starting VACUUM...")
conn.execute("VACUUM")
print("VACUUM complete")

# Also run integrity check
result = conn.execute("PRAGMA integrity_check").fetchone()
print(f"Integrity check: {result[0]}")
conn.close()
```

- [ ] Maintenance script created
- [ ] Scheduled (weekly, Sunday 3 AM)
- [ ] First maintenance run successful
- [ ] Maintenance logs reviewed

---

### 2. Monthly Backup Audit

**Verify Backups Are Valid**
```bash
# Run monthly (1st of each month)
python audit_backups.py

# Script should:
# 1. List all backups
# 2. Check file integrity
# 3. Test restore for latest backup
# 4. Verify backup count (should be ~30 files for 30-day retention)
# 5. Check off-site backup (if configured)
```

- [ ] Backup audit script created
- [ ] Scheduled (monthly, 1st at 4 AM)
- [ ] First audit run successful
- [ ] Audit report generated: `reports/backup_audit_YYYYMM.txt`

**Off-Site Backup (Recommended)**
```bash
# Copy to cloud storage or external drive
# Example: rsync to external drive
rsync -av backups/ /mnt/external/polymarket_backups/

# Or upload to cloud (S3, Dropbox, etc.)
rclone copy backups/ dropbox:polymarket_backups/
```
- [ ] Off-site backup configured
- [ ] Off-site backup tested
- [ ] Off-site backup scheduled (daily or weekly)

---

### 3. Quarterly Strategy Review

**Schedule Quarterly Review:**
- Q1: March 31
- Q2: June 30
- Q3: September 30
- Q4: December 31

**Review Agenda:**
1. **Performance Analysis**
   - Overall P&L
   - Win rate trend
   - Sharpe ratio
   - Max drawdown
   - Best/worst months
   
2. **Strategy Evaluation**
   - Are correlations still predictive?
   - Market conditions changed?
   - Any strategy adjustments needed?
   
3. **Risk Review**
   - Were risk limits appropriate?
   - Any near-misses or close calls?
   - Should limits be adjusted?
   
4. **Technical Review**
   - System uptime
   - API issues encountered
   - Database performance
   - Any bugs or errors?
   
5. **Capital Allocation**
   - Should capital be increased?
   - Should risk per trade be adjusted?
   - Portfolio diversification adequate?

**Action Items Template:**
```markdown
# Quarterly Review: Q1 2026

## Performance
- P&L: +$XXX (+XX%)
- Win rate: XX%
- Sharpe: X.XX
- Max drawdown: XX%

## Strategy
- Keep/adjust/replace

## Risk
- Limits appropriate: Yes/No
- Recommended changes: ...

## Technical
- Uptime: XX%
- Issues: ...

## Capital
- Current: $XXX
- Recommended: $XXX
- Rationale: ...

## Action Items
1. [ ] ...
2. [ ] ...
```

- [ ] Quarterly review calendar invites created
- [ ] Review template saved: `reports/quarterly_review_template.md`
- [ ] First review scheduled for: ___________________

---

### 4. Update Procedures Documented

**System Update Procedure:**
```bash
# 1. Backup everything
python backup_database.py
cp config.yaml config.yaml.backup
git commit -am "Pre-update backup"

# 2. Stop bot
touch EMERGENCY_STOP
# Wait for bot to stop
ps aux | grep trading_bot.py  # Verify stopped

# 3. Update code
git pull origin main
# Or: Download new version

# 4. Update dependencies
pip install -r requirements.txt --upgrade

# 5. Run tests
python -m pytest tests/

# 6. Review changelog
cat CHANGELOG.md

# 7. Update config if needed
# Check for new config options in config.yaml.example

# 8. Restart bot
rm EMERGENCY_STOP
python trading_bot.py

# 9. Monitor closely for 24 hours
tail -f logs/trading_system_*.log
```

**Rollback Procedure:**
```bash
# If update causes issues:

# 1. Stop bot
touch EMERGENCY_STOP

# 2. Restore database
cp backups/polymarket_backup_YYYYMMDD_HHMMSS.db data/polymarket.db

# 3. Restore config
cp config.yaml.backup config.yaml

# 4. Revert code
git revert HEAD
# Or: Re-download previous version

# 5. Restart bot
rm EMERGENCY_STOP
python trading_bot.py

# 6. Document what went wrong
echo "Rollback reason: ..." >> logs/rollback_log.txt
```

**Emergency Patch Procedure:**
```bash
# For critical security issues or bugs:

# 1. Stop bot immediately
touch EMERGENCY_STOP

# 2. Apply patch
git cherry-pick <commit-hash>
# Or: Edit files directly

# 3. Test thoroughly
python -m pytest tests/test_security.py

# 4. Restart with monitoring
rm EMERGENCY_STOP
python trading_bot.py --verbose

# 5. Watch logs for 1 hour before leaving unattended
```

- [ ] Update procedure documented
- [ ] Rollback procedure documented
- [ ] Emergency patch procedure documented
- [ ] Procedures tested (dry run)
- [ ] Procedures saved in `docs/update_procedures.md`

---

## Final Go-Live Checklist

**Before Starting Live Trading:**
- [ ] All pre-deployment checks PASSED
- [ ] All security checks PASSED
- [ ] Data collection running smoothly (7+ days)
- [ ] Validation phase completed successfully
- [ ] 30-day backtest PASSED
- [ ] Paper trading PASSED (7+ days)
- [ ] GO decision made and documented
- [ ] Micro capital funded ($500)
- [ ] Risk limits configured correctly
- [ ] Circuit breakers tested
- [ ] Emergency contacts listed
- [ ] Monitoring configured and active
- [ ] Telegram notifications working
- [ ] Dashboard accessible (if using)
- [ ] Daily review scheduled
- [ ] Maintenance scheduled
- [ ] Backup system operational
- [ ] Runbook reviewed and accessible
- [ ] Team aligned (if applicable)

**Start Live Trading:**
```bash
# 1. Final verification
python pre_launch_check.py

# Expected:
# ✓ All systems operational
# ✓ Ready for live trading

# 2. Disable paper trading
# Edit config.yaml: paper_trading: false

# 3. Start trading bot
python trading_bot.py

# 4. Verify startup
tail -f logs/trading_system_$(date +%Y%m%d).log

# Should see:
# [INFO] Trading bot started (LIVE MODE)
# [INFO] Capital: $500.00
# [INFO] Risk limits: max_position=$100, max_exposure=0.8
# [INFO] Monitoring markets...
```

**First Hour Monitoring:**
- [ ] Bot started successfully
- [ ] No errors in logs
- [ ] API connectivity confirmed
- [ ] Markets being monitored
- [ ] Health checks passing
- [ ] Stay and monitor for 1 hour minimum

**First 24 Hours:**
- [ ] Check logs every 2 hours
- [ ] Verify trades execute as expected
- [ ] Confirm P&L tracking
- [ ] Monitor for any anomalies
- [ ] Emergency stop accessible

**First Week:**
- [ ] Daily review completed each day
- [ ] No critical issues
- [ ] Performance tracking
- [ ] Confidence level: ___________________

---

## Post-Deployment Notes

**Deployment Date:** ___________________  
**Deployed By:** ___________________  
**Initial Capital:** $___________________  
**Configuration:** ___________________  

**Issues Encountered:**
- ___________________
- ___________________

**Lessons Learned:**
- ___________________
- ___________________

**Next Review Date:** ___________________

---

## Appendix: Quick Command Reference

**Start bot:**
```bash
python trading_bot.py
```

**Stop bot (graceful):**
```bash
touch EMERGENCY_STOP
```

**Check status:**
```bash
python health_check.py
```

**Manual backup:**
```bash
python backup_database.py
```

**Daily report:**
```bash
python daily_report.py
```

**View logs:**
```bash
tail -50 logs/trading_system_$(date +%Y%m%d).log
```

**Database query:**
```bash
sqlite3 data/polymarket.db "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;"
```

**Test API:**
```bash
python test_api_connectivity.py
```

---

**END OF CHECKLIST**

Great success! 🎉

Print this document and check off each item as you complete it. Do not rush. Do not skip steps. When in doubt, STOP and seek guidance.
