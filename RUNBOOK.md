# Operational Runbook - Polymarket Trading System

**Version:** 1.0  
**Last Updated:** 2026-02-06  
**Purpose:** Quick reference guide for common operational scenarios

---

## Table of Contents

1. [Emergency Procedures](#emergency-procedures)
2. [Bot Won't Start](#bot-wont-start)
3. [No Trades Executing](#no-trades-executing)
4. [Unexpected Losses](#unexpected-losses)
5. [Database Issues](#database-issues)
6. [API Errors](#api-errors)
7. [Performance Degradation](#performance-degradation)
8. [System Maintenance](#system-maintenance)
9. [Recovery Procedures](#recovery-procedures)
10. [Monitoring & Alerts](#monitoring--alerts)

---

## Emergency Procedures

### 🚨 IMMEDIATE STOP - Use When:
- Seeing unexpected rapid losses
- Suspected bot malfunction
- Market manipulation suspected
- Database corruption detected
- API key compromised

### Emergency Stop Procedure

**Method 1: Emergency Stop Flag (Preferred)**
```bash
# Create emergency stop file
touch EMERGENCY_STOP

# Bot checks for this file every loop iteration
# When detected:
# 1. Closes all open positions
# 2. Stops executing new trades
# 3. Sends critical alert
# 4. Logs shutdown reason
```

**Method 2: Kill Process (If unresponsive)**
```bash
# Find bot process
ps aux | grep trading_bot.py

# Graceful shutdown (try first)
kill -TERM <PID>

# Force kill (last resort)
kill -9 <PID>
```

**Method 3: API Key Revocation (Nuclear option)**
```bash
# If bot won't stop and continues trading:
# 1. Log into Polymarket account
# 2. Revoke API key immediately
# 3. Bot will fail authentication and stop
# 4. Investigate why emergency stop didn't work
```

### Post-Emergency Checklist
- [ ] Bot stopped and verified
- [ ] All positions closed or documented
- [ ] Logs preserved: `cp logs/*.log emergency_logs/`
- [ ] Incident documented: `reports/incident_YYYYMMDD.md`
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Testing completed before restart
- [ ] Post-mortem written (if serious)

---

## Bot Won't Start

### Symptoms
- `python trading_bot.py` exits immediately
- Error messages on startup
- Process starts but crashes within seconds

### Diagnostic Steps

#### 1. Check Logs First
```bash
# View most recent log
tail -100 logs/trading_system_$(date +%Y%m%d).log

# Search for ERROR
grep ERROR logs/trading_system_$(date +%Y%m%d).log
```

**Common error patterns:**
- `ModuleNotFoundError` → Missing dependency
- `FileNotFoundError` → Missing config or database
- `ValueError: Invalid configuration` → Config syntax error
- `API authentication failed` → API key issue
- `Database locked` → Another process has DB open

---

#### 2. Verify Environment

**Python Version**
```bash
python --version
# Expected: Python 3.9+

# If wrong version, activate venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```
- [ ] Correct Python version
- [ ] Virtual environment activated (if using)

**Dependencies**
```bash
pip list | grep -E "pandas|numpy|requests|pyyaml|telegram"

# If missing packages:
pip install -r requirements.txt
```
- [ ] All required packages installed
- [ ] No version conflicts

---

#### 3. Verify Configuration

**Check config.yaml exists**
```bash
ls -l config.yaml
# Should exist and be readable
```

**Validate YAML syntax**
```bash
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
# Should output nothing (silent success)
# Any error = invalid YAML syntax
```

**Common config.yaml issues:**
- Extra spaces/tabs (YAML is indentation-sensitive)
- Missing colon after key: `api_key` (wrong) vs `api_key:` (correct)
- Unquoted special characters
- Environment variable not set: `${POLYMARKET_API_KEY}` but variable empty

**Verify environment variables:**
```bash
echo $POLYMARKET_API_KEY  # Linux/Mac
echo $env:POLYMARKET_API_KEY  # Windows

# If empty:
export POLYMARKET_API_KEY="your_key_here"  # Linux/Mac
$env:POLYMARKET_API_KEY="your_key_here"   # Windows
```
- [ ] Environment variables set
- [ ] Environment variables not empty

---

#### 4. Verify Database

**Check database file exists**
```bash
ls -l data/polymarket.db
# Should exist

# If missing, initialize:
python initialize_db.py
```

**Check database is not corrupted**
```bash
sqlite3 data/polymarket.db "PRAGMA integrity_check;"
# Expected output: ok

# If corrupted: restore from backup
cp backups/polymarket_backup_LATEST.db data/polymarket.db
```

**Check database is not locked**
```bash
# Find processes with DB open
lsof data/polymarket.db  # Linux/Mac

# Windows: Check Task Manager for python.exe processes
# Kill any stale processes
```
- [ ] Database exists
- [ ] Database not corrupted
- [ ] Database not locked

---

#### 5. Test in Verbose Mode

```bash
# Start with verbose logging
python trading_bot.py --verbose --dry-run

# This will show detailed startup sequence
# Look for where it fails
```

**Expected startup sequence:**
1. Loading configuration...
2. Connecting to database...
3. Testing API connectivity...
4. Loading markets...
5. Initializing risk management...
6. Starting main loop...

**Note the step where it fails**

---

### Solutions by Error Type

**"ModuleNotFoundError: No module named 'X'"**
```bash
# Solution: Install missing package
pip install X

# Or reinstall all requirements
pip install -r requirements.txt
```

**"FileNotFoundError: config.yaml not found"**
```bash
# Solution: Check you're in correct directory
pwd  # Should be workspace root

# If config missing, restore from backup or template
cp config.yaml.backup config.yaml
```

**"API authentication failed"**
```bash
# Solution: Verify API key
echo $POLYMARKET_API_KEY

# Test API manually
python test_api_connectivity.py

# If invalid, regenerate API key in Polymarket account
```

**"Database is locked"**
```bash
# Solution: Kill other processes using DB
ps aux | grep python
kill <PID>

# Or: Wait 30 seconds for DB lock timeout
sleep 30
python trading_bot.py
```

**"ValueError: Invalid configuration"**
```bash
# Solution: Validate config
python validate_config.py

# Check specific value mentioned in error
# Common issues:
# - max_position_size > capital
# - negative values where positive required
# - missing required fields
```

---

### Still Can't Start?

**Nuclear restart:**
```bash
# 1. Backup everything
cp -r data data.backup
cp config.yaml config.yaml.backup

# 2. Restart from clean state
rm data/polymarket.db
python initialize_db.py

# 3. Verify config
python validate_config.py

# 4. Test API
python test_api_connectivity.py

# 5. Try starting
python trading_bot.py --verbose
```

**If still failing:**
- Check system logs: `dmesg` (Linux), Event Viewer (Windows)
- Verify disk space: `df -h` (need >1GB free)
- Verify permissions: `ls -l data/` (should be writable)
- Check for antivirus blocking (Windows)
- Try running as different user
- Review recent system changes (updates, config changes)

---

## No Trades Executing

### Symptoms
- Bot is running (no errors in logs)
- Markets being monitored
- But no trades executed for hours/days
- P&L not changing

### Diagnostic Steps

#### 1. Check Bot Status
```bash
# Verify bot is actually running
ps aux | grep trading_bot.py
# Should show process

# Check recent logs
tail -50 logs/trading_system_$(date +%Y%m%d).log

# Look for:
# - "Evaluating market: ..." (should appear every loop)
# - "Signal detected: ..." (indicates strategy sees opportunities)
# - "Trade executed: ..." (actual trades)
```

**If no "Evaluating market" messages:**
- Bot is stuck or loop not running
- Restart bot

**If "Evaluating market" but no "Signal detected":**
- No trading opportunities found (normal if markets are stable)
- Strategy may be too conservative
- Check signal criteria

**If "Signal detected" but no "Trade executed":**
- Risk limits preventing trade
- Insufficient funds
- API issues
- See diagnostic steps below

---

#### 2. Check Risk Limits

**View current risk status:**
```bash
python risk_status.py

# Expected output:
# Current positions: 2
# Portfolio exposure: 45%
# Available capital: $300
# Position slots available: 2
# Daily P&L: -$15
```

**Common risk limit blocks:**

| Issue | Risk Limit Triggered | Solution |
|-------|---------------------|----------|
| Too many open positions | `max_positions` reached | Wait for position to close, or increase limit |
| Portfolio fully deployed | `max_portfolio_exposure` reached | Wait for position to close, or increase exposure limit |
| Daily loss limit hit | `daily_loss_limit` exceeded | Wait until next day (resets at midnight), or increase limit |
| Position size too large | `max_position_size` exceeded | Strategy is calculating position size incorrectly, review logic |

**Temporarily adjust risk limits (for testing only):**
```yaml
# config.yaml
risk_limits:
  max_positions: 5  # Increase from 4
  max_portfolio_exposure: 0.9  # Increase from 0.8
  daily_loss_limit: 150  # Increase from 100
```

⚠️ **Warning:** Only increase limits if you understand the risk. Start conservative.

---

#### 3. Check Market Liquidity

**View available markets:**
```bash
python list_markets.py

# Expected output:
# Market ID | Title | Liquidity | Volume
# abc123... | Will BTC reach $50k by March? | $125,000 | $45,000
```

**Issues:**
- **Low liquidity (<$10,000):** Bot may be filtering out illiquid markets (correct behavior)
- **Markets closed:** Check if markets have resolved or deadline passed
- **No markets matching criteria:** Strategy filters may be too restrictive

**Adjust market filters (if needed):**
```yaml
# config.yaml
market_filters:
  min_liquidity: 50000  # Reduce from 100000
  min_volume: 10000     # Reduce from 20000
  categories:
    - crypto
    - politics
    - sports  # Add more categories
```

---

#### 4. Check Strategy Signals

**Run strategy in dry-run mode:**
```bash
python trading_bot.py --dry-run --verbose

# This will:
# - Evaluate markets
# - Calculate signals
# - Show what WOULD trade
# - But not execute actual trades
```

**Expected output:**
```
[INFO] Evaluating market: BTC $50k by March
[INFO] Current probability: 0.72
[INFO] Model prediction: 0.85
[INFO] Edge detected: +0.13 (threshold: 0.05)
[INFO] Signal: BUY
[DRY-RUN] Would execute: BUY $100 at 0.72
```

**If no signals:**
- **Market predictions align with current prices:** No edge detected (correct behavior)
- **Prediction threshold too high:** Reduce `signal_threshold` in config
- **Not enough data:** Need more historical data for model
- **Model not calibrated:** Re-train or adjust model parameters

**Adjust signal threshold (if needed):**
```yaml
# config.yaml
strategy:
  signal_threshold: 0.03  # Reduce from 0.05 (more aggressive)
```

⚠️ **Warning:** Lowering threshold increases trade frequency but may reduce quality.

---

#### 5. Check API Connectivity

**Test API manually:**
```bash
python test_api_connectivity.py

# Expected output:
# ✓ API authentication successful
# ✓ Market data retrieved
# ✓ Account balance retrieved
# ✓ Order placement (test mode): OK
```

**If API issues:**
- Check internet connection: `ping 8.8.8.8`
- Verify API key valid: Regenerate if needed
- Check Polymarket status: https://status.polymarket.com
- Review rate limits: Bot may be throttled

**Check rate limiting:**
```bash
grep "rate limit" logs/trading_system_*.log

# If rate limited:
# - Reduce polling frequency in config
# - Add delays between API calls
```

---

### Solutions Summary

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Bot running, no "Evaluating market" logs | Bot stuck/frozen | Restart bot |
| Evaluating markets, but no signals | No trading edge detected | Normal (or reduce `signal_threshold`) |
| Signals detected, but trades blocked | Risk limits hit | Check `risk_status.py`, adjust limits if safe |
| Trades attempted, but API errors | API connectivity issues | Check `test_api_connectivity.py`, verify key |
| Low liquidity markets | Market filters too strict | Reduce `min_liquidity` in config |
| No markets matching criteria | Category filters too narrow | Add more categories |

---

## Unexpected Losses

### Symptoms
- Losses exceeding expected drawdown
- Rapid consecutive losses
- Single large loss

### Immediate Actions

#### 1. EMERGENCY STOP (if needed)
```bash
# If losses are rapid and unexpected:
touch EMERGENCY_STOP

# Bot will:
# - Stop opening new positions
# - Close existing positions
# - Send alert
```

#### 2. Review Recent Trades
```bash
# View last 10 trades
sqlite3 data/polymarket.db "SELECT timestamp, market_id, direction, size, entry_price, exit_price, pnl FROM trades ORDER BY timestamp DESC LIMIT 10;"

# Calculate total P&L for today
python daily_pnl.py

# Expected output:
# Today's P&L: -$45.50
# Trades: 8 (5 wins, 3 losses)
# Largest loss: -$18.20 (Market: ABC123...)
```

**Document findings:**
- Total loss: $___________________
- Number of losing trades: ___________________
- Largest single loss: $___________________
- Common pattern (if any): ___________________

---

#### 3. Identify Root Cause

**Possible causes:**

| Cause | How to Detect | Action |
|-------|---------------|--------|
| **Normal variance** | Losses within expected range (< max drawdown) | Monitor, no action if risk limits working |
| **Strategy failure** | Win rate dropped significantly | Pause trading, review strategy, re-backtest |
| **Market manipulation** | Sudden price spikes/drops, unusual volume | Report to Polymarket, avoid affected markets |
| **Bug in code** | Trades executed outside risk limits | Emergency stop, fix bug, test thoroughly |
| **API issues** | Trades executed at wrong prices | Check API logs, contact Polymarket support |
| **Data issues** | Stale or incorrect market data | Verify data quality, restart data collection |

**Check if losses are within normal variance:**
```bash
# Compare to backtest max drawdown
# Backtest max drawdown: 15%
# Current drawdown: 12%
# → Within expected range (monitor but don't panic)

# If current drawdown > backtest max drawdown:
# → Unexpected, investigate further
```

---

#### 4. Analyze Losing Trades

**For each significant losing trade, check:**

**Trade Details:**
```bash
sqlite3 data/polymarket.db "SELECT * FROM trades WHERE trade_id='<trade_id>';"
```

**Questions to answer:**
- Was position size within limits? (Should be ≤ `max_position_size`)
- Was entry price reasonable? (Check market price at that time)
- Was exit triggered correctly? (Stop loss, take profit, or manual close?)
- Was trade aligned with strategy signal? (Should have positive edge)

**Market Analysis:**
```bash
# View market snapshots around trade time
sqlite3 data/polymarket.db "SELECT timestamp, probability, volume FROM market_snapshots WHERE market_id='<market_id>' AND timestamp BETWEEN '<start_time>' AND '<end_time>' ORDER BY timestamp;"

# Check for:
# - Sudden price movements (manipulation?)
# - Low volume (illiquid market?)
# - Unusual patterns
```

**Pattern Recognition:**
- Are all losses in the same market category? (e.g., all crypto markets)
- Are all losses in the same time window? (e.g., all between 2-4 PM)
- Are all losses from the same strategy signal type? (e.g., all correlation-based)

---

#### 5. Verify Risk Controls

**Test risk limits are still enforced:**
```bash
python test_risk_limits.py

# Should confirm:
# ✓ Position size limit enforced
# ✓ Portfolio exposure limit enforced
# ✓ Stop loss triggers correctly
# ✓ Daily loss limit enforced
```

**If risk limits are NOT enforced:**
- **CRITICAL BUG** - Emergency stop immediately
- Fix bug before restarting
- Review all recent trades for risk limit violations

---

### Recovery Actions

**Minor Losses (within expected drawdown):**
- [ ] Document trades in loss log: `reports/loss_analysis_YYYYMMDD.md`
- [ ] Continue trading (no action needed)
- [ ] Monitor closely over next 24 hours
- [ ] Review at daily check-in

**Moderate Losses (approaching max drawdown):**
- [ ] Reduce position size by 50%: `max_position_size: 50` (from 100)
- [ ] Reduce max positions: `max_positions: 2` (from 4)
- [ ] Increase stop loss tightness: `stop_loss_percent: 0.10` (from 0.15)
- [ ] Monitor every 2 hours for next 48 hours
- [ ] Review strategy parameters

**Severe Losses (exceeded max drawdown or daily loss limit):**
- [ ] Emergency stop immediately
- [ ] Full trade review (document all losing trades)
- [ ] Root cause analysis (see above)
- [ ] Strategy re-validation (30-day backtest with new data)
- [ ] Paper trading for 7 days before resuming live
- [ ] Reduce capital: Start with $250 instead of $500
- [ ] Post-mortem document: `reports/post_mortem_YYYYMMDD.md`

---

### Loss Analysis Template

Create: `reports/loss_analysis_YYYYMMDD.md`

```markdown
# Loss Analysis - YYYY-MM-DD

## Summary
- Total loss: $XX.XX
- Number of trades: X (W wins, L losses)
- Largest loss: $XX.XX
- Drawdown: XX%

## Losing Trades
| Trade ID | Market | Direction | Size | Entry | Exit | Loss | Reason |
|----------|--------|-----------|------|-------|------|------|--------|
| abc123   | BTC $50k | LONG | $100 | 0.65 | 0.58 | -$7.00 | Market resolved against position |

## Root Cause
[Normal variance / Strategy failure / Bug / Market manipulation / Other]

Details: ...

## Patterns Identified
- [Any common patterns across losing trades]

## Action Items
- [ ] [Specific actions to prevent recurrence]
- [ ] [Strategy adjustments if needed]
- [ ] [Code fixes if bug identified]

## Decision
- [ ] Continue trading (normal variance)
- [ ] Reduce risk limits
- [ ] Pause trading for review
- [ ] Emergency stop

Signed: ___________________ Date: ___________________
```

---

## Database Issues

### Symptoms
- "Database is locked" errors
- "Database disk image is malformed" errors
- Slow query performance
- Database file size growing rapidly

### Solutions by Issue Type

#### 1. Database Locked

**Cause:** Multiple processes trying to write to database simultaneously.

**Solution:**
```bash
# 1. Find all processes with database open
lsof data/polymarket.db  # Linux/Mac
# Windows: Check Task Manager for multiple python.exe

# 2. Kill stale processes
kill <PID>

# 3. Wait for lock timeout (30 seconds)
sleep 30

# 4. Restart bot
python trading_bot.py
```

**Prevention:**
- Only run ONE instance of trading bot
- Ensure scripts close database connections properly
- Use context managers: `with sqlite3.connect(...) as conn:`

---

#### 2. Database Corrupted

**Symptoms:**
```
sqlite3.DatabaseError: database disk image is malformed
```

**Solution:**
```bash
# 1. STOP all processes using database
touch EMERGENCY_STOP

# 2. Attempt repair
sqlite3 data/polymarket.db "PRAGMA integrity_check;"
# If output is not "ok", database is corrupted

# 3. Try to recover
sqlite3 data/polymarket.db ".recover" | sqlite3 data/polymarket_recovered.db

# 4. Verify recovered database
sqlite3 data/polymarket_recovered.db "SELECT COUNT(*) FROM trades;"

# 5. If recovery successful:
mv data/polymarket.db data/polymarket_CORRUPTED.db
mv data/polymarket_recovered.db data/polymarket.db

# 6. If recovery failed:
# Restore from latest backup
cp backups/polymarket_backup_$(ls -t backups/ | head -1) data/polymarket.db

# 7. Verify restored database
python verify_database.py
```

**Data loss assessment:**
```bash
# Compare restored backup to current data
# Check last trade timestamp
sqlite3 data/polymarket.db "SELECT MAX(timestamp) FROM trades;"

# If data is missing (backup was old):
# Re-run data collection for gap period (if possible)
# Or: Document data loss and proceed
```

---

#### 3. Slow Database Performance

**Symptoms:**
- Queries taking >1 second
- Bot lagging
- High disk I/O

**Solution 1: Rebuild Indexes**
```bash
sqlite3 data/polymarket.db <<EOF
REINDEX;
ANALYZE;
EOF
```

**Solution 2: Vacuum Database**
```bash
# Defragment and reclaim space
sqlite3 data/polymarket.db "VACUUM;"

# Check size before/after
ls -lh data/polymarket.db
```

**Solution 3: Archive Old Data**
```bash
# Archive trades older than 90 days
python archive_old_data.py --days 90

# This will:
# 1. Export old data to archive file
# 2. Delete from main database
# 3. Speed up queries
```

**Solution 4: Add Missing Indexes**
```sql
-- Run in sqlite3 cli
sqlite3 data/polymarket.db

-- Check existing indexes
.indexes

-- Add indexes if missing (common queries)
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_market_id ON trades(market_id);
CREATE INDEX IF NOT EXISTS idx_market_snapshots_timestamp ON market_snapshots(timestamp);
CREATE INDEX IF NOT EXISTS idx_market_snapshots_market_id ON market_snapshots(market_id);
```

---

#### 4. Database Size Growing Rapidly

**Check current size:**
```bash
du -h data/polymarket.db
# If >500 MB, investigate

# Expected growth: ~20 MB per day
# At 30 days: ~600 MB (normal)
# At 30 days: >2 GB (abnormal)
```

**Find large tables:**
```bash
sqlite3 data/polymarket.db <<EOF
SELECT 
  name, 
  SUM("pgsize") / 1024 / 1024 as size_mb 
FROM "dbstat" 
GROUP BY name 
ORDER BY size_mb DESC;
EOF
```

**Solutions:**
- **Market snapshots table large:** Normal (high frequency data collection)
  - Archive old snapshots: `python archive_old_data.py --table market_snapshots --days 60`
- **Logs table large:** Logs should be in files, not database
  - If logging to DB: Disable, use file logging instead
- **Unused tables:** Drop unused tables
  - `sqlite3 data/polymarket.db "DROP TABLE unused_table;"`

---

## API Errors

### Common API Error Codes

| Error Code | Meaning | Solution |
|------------|---------|----------|
| 401 | Unauthorized | API key invalid or expired. Regenerate key. |
| 403 | Forbidden | API key lacks permissions. Check account settings. |
| 429 | Rate Limit | Too many requests. Reduce polling frequency. |
| 500 | Internal Server Error | Polymarket issue. Retry after delay. |
| 503 | Service Unavailable | Polymarket maintenance. Check status page. |

### Diagnostic Steps

#### 1. Test API Connection
```bash
python test_api_connectivity.py

# Expected:
# ✓ API authentication successful
# ✓ Market data retrieved
# ✓ Account balance retrieved

# If any fail, proceed to specific error handling
```

---

#### 2. Authentication Errors (401/403)

**Error message:**
```
API Error 401: Unauthorized
```

**Solution:**
```bash
# 1. Verify API key is set
echo $POLYMARKET_API_KEY

# 2. Verify API key is correct (no typos)
# Copy from Polymarket account settings

# 3. Test API key manually
curl -H "Authorization: Bearer $POLYMARKET_API_KEY" https://api.polymarket.com/markets

# 4. If still failing, regenerate API key
# - Log into Polymarket account
# - Settings → API Keys
# - Revoke old key
# - Generate new key
# - Update environment variable
export POLYMARKET_API_KEY="new_key_here"

# 5. Restart bot
python trading_bot.py
```

---

#### 3. Rate Limit Errors (429)

**Error message:**
```
API Error 429: Rate limit exceeded
```

**Solution:**
```bash
# 1. Reduce polling frequency
# Edit config.yaml:
data_collection:
  interval_seconds: 300  # Increase from 60 (every 5 min instead of 1 min)

# 2. Add delays between API calls in code
import time
time.sleep(1)  # 1 second delay between calls

# 3. Review API call frequency
grep "API call" logs/trading_system_*.log | wc -l
# Should be <100 calls per minute

# 4. Batch requests where possible
# Fetch multiple markets in one call instead of individual calls

# 5. Wait for rate limit reset
# Polymarket rate limits typically reset every 1 minute
sleep 60
python trading_bot.py
```

**Check rate limit headers:**
```bash
# In logs, look for rate limit info
grep "X-RateLimit" logs/trading_system_*.log

# Common headers:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 23
# X-RateLimit-Reset: 1675123456
```

---

#### 4. Server Errors (500/503)

**Error message:**
```
API Error 503: Service temporarily unavailable
```

**Solution:**
```bash
# 1. Check Polymarket status
# Visit: https://status.polymarket.com
# Or check Twitter: @Polymarket

# 2. Implement exponential backoff in code
# Retry with increasing delays: 1s, 2s, 4s, 8s, 16s

# 3. Wait for service restoration
# Typically resolves within 5-30 minutes

# 4. Enable graceful degradation
# Bot should:
# - Not crash on API errors
# - Log error and continue
# - Retry after delay
# - Alert if errors persist >15 minutes
```

**Temporary workaround:**
```python
# In code, add retry logic:
import time
from requests.exceptions import RequestException

def api_call_with_retry(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"API error, retrying in {wait_time}s: {e}")
            time.sleep(wait_time)
```

---

#### 5. Network Issues

**Symptoms:**
- Connection timeouts
- DNS resolution failures
- Intermittent connectivity

**Solution:**
```bash
# 1. Check internet connection
ping 8.8.8.8 -c 10
# Should see 0% packet loss

# 2. Check DNS resolution
nslookup api.polymarket.com
# Should resolve to IP address

# 3. Check firewall
# Ensure outbound HTTPS (port 443) is allowed

# 4. Test with curl
curl -v https://api.polymarket.com/markets
# Should connect and return data

# 5. Check proxy settings (if applicable)
echo $HTTP_PROXY
echo $HTTPS_PROXY
# Should be empty unless using proxy

# 6. Increase timeouts in config
api:
  timeout_seconds: 30  # Increase from 10 for slow connections
```

---

## Performance Degradation

### Symptoms
- Bot response time slow
- High CPU/memory usage
- Trades delayed
- Dashboard laggy

### Diagnostic Steps

#### 1. Check System Resources

**CPU Usage:**
```bash
top -p $(pgrep -f trading_bot.py)
# Look at %CPU column
# Should be <50% average
# Spikes to 100% occasionally are normal

# If consistently >80%:
# - Inefficient code (tight loops, complex calculations)
# - Too many markets being monitored
```

**Memory Usage:**
```bash
ps aux | grep trading_bot.py
# Look at %MEM and RSS columns
# Should be <500 MB for typical setup

# If >1 GB:
# - Memory leak (restart bot, monitor growth)
# - Too much data cached in memory
```

**Disk I/O:**
```bash
iotop -p $(pgrep -f trading_bot.py)
# Look at DISK READ/WRITE
# Should be <5 MB/s average

# If high:
# - Database operations inefficient
# - Excessive logging
```

---

#### 2. Profile Code Performance

**Add timing to critical sections:**
```python
import time

start = time.time()
# ... code section ...
elapsed = time.time() - start
logger.debug(f"Section took {elapsed:.2f}s")
```

**Common bottlenecks:**
- Database queries (optimize with indexes)
- API calls (batch where possible, use async)
- Data processing (optimize algorithms, use numpy)
- Model predictions (cache results, use faster model)

---

#### 3. Optimize Database

**See Database Issues section above:**
- Rebuild indexes: `REINDEX;`
- Vacuum database: `VACUUM;`
- Archive old data
- Add missing indexes

---

#### 4. Reduce Monitoring Scope

**If monitoring too many markets:**
```yaml
# config.yaml
market_filters:
  categories:
    - crypto  # Only monitor crypto, not all categories
  min_liquidity: 100000  # Higher threshold = fewer markets
  max_markets: 20  # Limit total markets monitored
```

---

#### 5. Optimize Logging

**If log files are huge (>100 MB):**
```yaml
# config.yaml
logging:
  level: INFO  # Change from DEBUG
  max_file_size_mb: 10
  backup_count: 5
```

**Disable verbose logging for production:**
```python
# Remove debug statements in hot loops
# logger.debug(f"Processing market {market_id}...")  # Comment out
```

---

## System Maintenance

### Daily Maintenance (Automated)

**These should run automatically via cron:**
- [ ] Backup database (2 AM daily)
- [ ] Health check (every 5 minutes)
- [ ] Daily report (6 PM daily)
- [ ] Log rotation (midnight)

**Verify cron jobs are running:**
```bash
# Check cron is active
systemctl status cron  # Linux
# Windows: Check Task Scheduler

# View cron jobs
crontab -l

# Check cron logs
grep trading_bot /var/log/syslog  # Linux
# Windows: Task Scheduler → History
```

---

### Weekly Maintenance (Manual)

**Every Sunday, 15 minutes:**

**1. Review Weekly Performance**
```bash
python weekly_report.py

# Review:
# - Total P&L for week
# - Win rate trend
# - Any unusual patterns
# - Best/worst trades
```
- [ ] Weekly report reviewed
- [ ] P&L documented: $___________________
- [ ] Any concerns noted: ___________________

**2. Check Backups**
```bash
ls -lht backups/ | head -7
# Should see 7 daily backups

# Test latest backup
python test_backup_restore.py --backup backups/$(ls -t backups/ | head -1)
```
- [ ] 7 recent backups exist
- [ ] Backup restoration tested

**3. Check Disk Space**
```bash
df -h .
# Should have >2 GB free
```
- [ ] Disk space adequate: ___________________GB free

**4. Review Alerts**
```bash
grep CRITICAL logs/trading_system_*.log | tail -20
grep WARNING logs/trading_system_*.log | tail -50

# Investigate any unexpected alerts
```
- [ ] Alerts reviewed
- [ ] Any issues addressed

**5. Update Dependencies (if needed)**
```bash
pip list --outdated

# If security updates available:
pip install --upgrade <package>

# Test after update:
python -m pytest tests/
```
- [ ] Dependencies checked
- [ ] Updates applied (if any): ___________________

---

### Monthly Maintenance

**First Sunday of each month, 30 minutes:**

**1. Backup Audit**
```bash
python audit_backups.py

# Verifies:
# - All backups are valid
# - No corrupted backups
# - Retention policy followed (30 days)
```
- [ ] Backup audit passed

**2. Database Maintenance**
```bash
# Vacuum database
sqlite3 data/polymarket.db "VACUUM;"

# Rebuild indexes
sqlite3 data/polymarket.db "REINDEX;"

# Check integrity
sqlite3 data/polymarket.db "PRAGMA integrity_check;"
# Expected: ok
```
- [ ] Database maintained

**3. Archive Old Data**
```bash
# Archive data older than 90 days
python archive_old_data.py --days 90

# Verify archival
ls -lh archives/
```
- [ ] Old data archived

**4. Review Strategy Performance**
```bash
python monthly_strategy_review.py

# Review:
# - Monthly P&L
# - Sharpe ratio
# - Max drawdown
# - Win rate by market category
# - Any strategy drift
```
- [ ] Strategy reviewed
- [ ] Performance acceptable: Yes / No / Adjust

**5. Security Review**
```bash
# Check file permissions
find . -name "*.db" -o -name "config.yaml" | xargs ls -l

# Check for hardcoded secrets
grep -r "api_key.*=.*['\"]" . --exclude-dir=venv

# Review environment variables
env | grep API

# Check for suspicious log entries
grep -i "unauthorized\|forbidden" logs/*.log
```
- [ ] Security checks passed

---

### Quarterly Maintenance

**See PRODUCTION-CHECKLIST.md for detailed quarterly review procedure.**

---

## Recovery Procedures

### Recovering from Crash

**Bot crashed unexpectedly:**

```bash
# 1. Check logs for crash reason
tail -100 logs/trading_system_$(date +%Y%m%d).log

# Look for:
# - Python tracebacks
# - "CRITICAL" or "ERROR" messages
# - Last action before crash

# 2. Check for core dumps
ls -l core*  # Linux
# Windows: Check Event Viewer

# 3. Verify database integrity
sqlite3 data/polymarket.db "PRAGMA integrity_check;"

# 4. Check disk space
df -h .

# 5. Review system logs
dmesg | tail -50  # Linux
# Windows: Event Viewer → Application logs

# 6. Fix identified issue

# 7. Restart bot
python trading_bot.py

# 8. Monitor closely for 1 hour
tail -f logs/trading_system_*.log
```

---

### Recovering from Bad Trades

**If strategy is losing consistently:**

**1. Emergency stop trading**
```bash
touch EMERGENCY_STOP
```

**2. Full trade review**
```bash
python analyze_trades.py --last-n 50

# Review all recent trades
# Identify patterns in losers
```

**3. Re-validate strategy**
```bash
# Run backtest on recent data
python backtest.py --start-date $(date -d '30 days ago' +%Y-%m-%d) --end-date $(date +%Y-%m-%d) --capital 500

# If backtest fails (negative return):
# → Strategy has degraded
# → Need to re-tune or pause
```

**4. Paper trading**
```bash
# Return to paper trading mode
# Edit config.yaml: paper_trading: true
python trading_bot.py
# Monitor for 7 days
```

**5. Gradual return to live**
```bash
# If paper trading successful:
# - Reduce capital: $250 (instead of $500)
# - Reduce position size: $50 (instead of $100)
# - Reduce max positions: 2 (instead of 4)
# Gradually increase over 2 weeks if performing well
```

---

### Recovering from Database Corruption

**See Database Issues section above.**

**Summary:**
1. Stop all processes
2. Attempt repair: `sqlite3 db ".recover" | sqlite3 db_recovered`
3. If repair fails: Restore from backup
4. Verify restored database
5. Document data loss (if any)
6. Resume operations

---

### Recovering from API Key Compromise

**If API key is exposed or compromised:**

**1. Immediately revoke key**
```bash
# Log into Polymarket account
# Settings → API Keys → Revoke compromised key
```

**2. Generate new key**
```bash
# Settings → API Keys → Generate New Key
# Save securely

# Update environment variable
export POLYMARKET_API_KEY="new_key_here"
# Or update .bashrc / system environment
```

**3. Update all systems**
```bash
# Update config if needed (though should use env vars)
# Restart bot
python trading_bot.py
```

**4. Review account activity**
```bash
# Check for unauthorized trades
python review_trades.py --last-n 100

# Check account balance
python check_balance.py

# Report suspicious activity to Polymarket
```

**5. Security audit**
```bash
# Check where key was exposed
# - Logs? (fix logging)
# - Git repo? (remove from history, rotate key)
# - Shared file? (restrict permissions)

# Enhance security:
chmod 600 config.yaml
chmod 600 .bashrc  # If key is there
```

---

## Monitoring & Alerts

### Alert Response Guide

**When you receive an alert, follow this decision tree:**

#### CRITICAL Alert

**Examples:**
- Daily loss limit exceeded
- Emergency stop triggered
- Database corruption
- API key invalid

**Response:**
```bash
# 1. Acknowledge alert (reply to Telegram/email)
# "Acknowledged, investigating..."

# 2. Check bot status
ps aux | grep trading_bot.py
tail -50 logs/trading_system_$(date +%Y%m%d).log

# 3. If bot is still running and issue is critical:
touch EMERGENCY_STOP

# 4. Investigate root cause (use relevant section above)

# 5. Document incident
echo "$(date): [CRITICAL] Alert: ... Root cause: ... Action taken: ..." >> reports/incident_log.txt

# 6. Fix issue before restarting

# 7. Test fix

# 8. Restart when confident
rm EMERGENCY_STOP
python trading_bot.py

# 9. Send follow-up alert
# "Issue resolved, trading resumed"
```

---

#### WARNING Alert

**Examples:**
- Win rate below 50%
- Drawdown approaching max
- API response slow
- No trades in 4 hours

**Response:**
```bash
# 1. No need to stop immediately (monitor closely)

# 2. Review recent activity
python recent_activity.py

# 3. Assess severity:
# - If temporary: Continue monitoring
# - If persistent (>24 hours): Investigate further

# 4. Adjust if needed:
# - Reduce position size
# - Reduce max positions
# - Tighten stop losses

# 5. Document in daily review log
```

---

#### INFO Alert

**Examples:**
- Daily performance summary
- New market detected
- Weekly report

**Response:**
- Review at convenience
- No immediate action required
- Archive for records

---

### Dashboard Monitoring

**If running dashboard, check these metrics hourly:**

**Green (Normal):**
- P&L: Within daily variance (±5% of capital)
- Win rate: >50%
- Open positions: <max_positions
- API latency: <1s
- Health: All checks passing

**Yellow (Monitor):**
- P&L: -5% to -10% (approaching daily loss limit)
- Win rate: 48-50% (slightly below break-even)
- API latency: 1-3s (slow but functional)
- Health: 1-2 checks failing (non-critical)

**Red (Action Required):**
- P&L: <-10% (consider emergency stop)
- Win rate: <45% (strategy failing)
- API latency: >3s (API issues)
- Health: >2 checks failing or critical check failing

---

## Common Commands Quick Reference

```bash
# Start bot
python trading_bot.py

# Start bot in paper trading mode
python trading_bot.py --paper-trading

# Start bot with verbose logging
python trading_bot.py --verbose

# Emergency stop
touch EMERGENCY_STOP

# Check bot status
ps aux | grep trading_bot.py

# View live logs
tail -f logs/trading_system_$(date +%Y%m%d).log

# Daily report
python daily_report.py

# Risk status
python risk_status.py

# Check database
sqlite3 data/polymarket.db "SELECT COUNT(*) FROM trades;"

# Backup database
python backup_database.py

# Test API
python test_api_connectivity.py

# Health check
python health_check.py

# View recent trades
sqlite3 data/polymarket.db "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;"

# Check disk space
df -h .

# View cron jobs
crontab -l
```

---

## Emergency Contact Information

**Your Contact:**
- Name: ___________________
- Phone: ___________________
- Email: ___________________

**Polymarket Support:**
- Email: support@polymarket.com
- Discord: https://discord.gg/polymarket
- Twitter: @Polymarket
- Status Page: https://status.polymarket.com

**Backup Contact:**
- Name: ___________________
- Phone: ___________________

---

## Escalation Matrix

| Issue Severity | Response Time | Escalation | Actions |
|----------------|---------------|------------|---------|
| **Critical** | Immediate (<5 min) | Self + Backup | Emergency stop, investigate, fix |
| **High** | <30 min | Self | Investigate, mitigate, document |
| **Medium** | <2 hours | Self | Monitor, adjust if worsens |
| **Low** | <24 hours | Self | Review in daily check-in |
| **Info** | At convenience | Self | Archive, no action needed |

---

## Post-Incident Review Template

**After any critical incident, complete this review:**

Create: `reports/incident_YYYYMMDD.md`

```markdown
# Incident Report - YYYY-MM-DD

## Summary
- **Incident date/time:** YYYY-MM-DD HH:MM
- **Severity:** Critical / High / Medium
- **Duration:** X hours Y minutes
- **Financial impact:** $XX.XX loss

## Timeline
- HH:MM - Incident detected (how: alert / manual / logs)
- HH:MM - Emergency stop executed
- HH:MM - Root cause identified
- HH:MM - Fix implemented
- HH:MM - Testing completed
- HH:MM - Trading resumed

## Root Cause
[Detailed explanation of what went wrong]

## Impact
- Trades affected: X
- Positions closed: X
- P&L impact: $XX.XX
- Data loss: Yes / No (if yes, describe)

## Response Evaluation
- What went well:
  - ...
- What could be improved:
  - ...

## Preventive Measures
1. [ ] [Specific action to prevent recurrence]
2. [ ] [Code change / config change / process change]
3. [ ] [Testing / monitoring enhancement]

## Lessons Learned
- ...

## Follow-up Actions
- [ ] [Action item 1] - Owner: ___ - Due: ___
- [ ] [Action item 2] - Owner: ___ - Due: ___

Completed by: ___________________ Date: ___________________
```

---

**END OF RUNBOOK**

Print this document and keep it accessible. In an emergency, you want quick answers, not long searches.

Great success! 🎉
