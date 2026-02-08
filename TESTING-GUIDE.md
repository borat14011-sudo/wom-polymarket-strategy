# 🧪 TESTING GUIDE - System Validation

**Purpose:** Verify each component works before going live  
**Time:** 30 minutes for full test suite  
**Required:** Python environment + internet connection

---

## 🎯 TESTING PHILOSOPHY

**Test everything, trust nothing.**

Before deploying real capital:
1. ✅ Unit test each script independently
2. ✅ Integration test full pipeline
3. ✅ Validate data quality
4. ✅ Stress test edge cases
5. ✅ Verify risk management works

---

## 📋 PRE-TEST CHECKLIST

```bash
# 1. Dependencies installed
pip install -r requirements.txt

# 2. Workspace clean
rm -f polymarket_data.db test_*.db

# 3. Logs directory exists
mkdir -p logs

# 4. Scripts executable
chmod +x *.py
```

---

## 🔬 UNIT TESTS

### Test 1: Polymarket Data Collector

**What it tests:** API access, database creation, data storage

```bash
# Run once
python polymarket-data-collector.py

# Expected output:
# ✓ Database initialized: polymarket_data.db
# ✓ Fetched 15+ high-volume markets
# ✓ Bitcoin will reach $100k... | Price: $0.523 | Vol: $1,250,000
# ...
# ✓ Collected 15/15 market snapshots

# Verify database created
ls -lh polymarket_data.db

# Query data
sqlite3 polymarket_data.db "SELECT COUNT(*) FROM markets;"
# Should return: 15+ (number of markets)

sqlite3 polymarket_data.db "SELECT COUNT(*) FROM snapshots;"
# Should return: 15+ (number of snapshots)
```

**Success criteria:**
- ✅ No errors in output
- ✅ Database file created
- ✅ Markets populated
- ✅ Snapshots recorded
- ✅ Runs in <60 seconds

**If fails:**
- Check internet connection
- Verify Polymarket API accessible: `curl https://gamma-api.polymarket.com/markets`
- Check Python dependencies

---

### Test 2: Twitter Hype Monitor

**What it tests:** Twitter scraping, sentiment analysis, hype scoring

```bash
# Run once (requires markets in DB from Test 1)
python twitter-hype-monitor.py

# Expected output:
# ================================================================================
# Twitter Hype Monitor - 2026-02-06 05:30:00
# ================================================================================
#
# 📊 Scraping: polymarket.com
#    Found 47 tweets
# 📊 Scraping: #Polymarket
#    Found 23 tweets
# ...
# ✓ Total unique tweets: 58
# ✓ Matched 12 tweets to markets
# ✓ Generated 3 hype signals
#
# 🔥 TOP HYPE MARKETS:
#    1. [72.3] Will Bitcoin reach $100k... | Tweets: 8 | Velocity: +150%

# Verify tweets collected
sqlite3 polymarket_data.db "SELECT COUNT(*) FROM tweets;"
# Should return: >0 (number of tweets found)

sqlite3 polymarket_data.db "SELECT COUNT(*) FROM hype_signals;"
# Should return: >0 if hype detected
```

**Success criteria:**
- ✅ No errors
- ✅ Tweets collected (even if 0 recent)
- ✅ Hype signals generated (if applicable)
- ✅ Runs in <60 seconds

**If fails:**
- Check if snscrape installed: `pip install snscrape`
- Test snscrape: `snscrape twitter-search "polymarket" --max-results 5`
- If snscrape broken, consider paid X API

---

### Test 3: Signal Generator

**What it tests:** Signal detection, position sizing, risk management

```bash
# Requires: Data from Test 1 & Test 2 (need snapshots + hype)

# Single scan
python signal-generator.py

# Expected outputs:

# A) If no signals:
# ================================================================================
# No signals detected
# Current market conditions:
#   Markets tracked: 15
#   Hype signals: 3
#   Volume surge markets: 2
#   Momentum markets: 1
#   None meet all entry criteria
# ================================================================================

# B) If signal found:
# ================================================================================
# 🚀 BUY SIGNAL | Confidence: HIGH
# ================================================================================
# Market: Will Bitcoin reach $100,000...
# Entry: $0.450 | Position: 4.0% ($400)
# ...
# ================================================================================

# Check signal log
cat signals.jsonl
```

**Success criteria:**
- ✅ Runs without errors
- ✅ Analyzes markets correctly
- ✅ Applies entry rules properly
- ✅ Generates signals if criteria met
- ✅ Position sizing calculated
- ✅ Risk checks enforced

**If fails:**
- Ensure database has 24h+ of data (for RVR calculation)
- Check config.json exists and valid
- Verify bankroll set in config

---

### Test 4: Correlation Analyzer (When Available)

**What it tests:** Statistical analysis, Granger causality

```bash
# Requires: 7+ days of data minimum

python correlation-analyzer.py

# Expected: Statistical report on hype → price correlations
```

**Success criteria:**
- ✅ No errors
- ✅ Runs Granger tests
- ✅ Generates correlation report
- ✅ Identifies lag structure

**Skip if:** <7 days of data collected

---

### Test 5: Backtest Engine (When Available)

**What it tests:** Historical simulation, performance metrics

```bash
# Requires: 30+ days of data minimum

python backtest-engine.py

# Expected: HTML report with equity curve, metrics
```

**Success criteria:**
- ✅ No errors
- ✅ Simulates trades
- ✅ Calculates Sharpe, drawdown
- ✅ Generates HTML report

**Skip if:** <30 days of data

---

## 🔗 INTEGRATION TESTS

### Test 6: Full Pipeline (15-Min Cycle)

**What it tests:** All components working together

```bash
# Run complete cycle
python polymarket-data-collector.py && \
python twitter-hype-monitor.py && \
python signal-generator.py

# Expected: Each script completes successfully in sequence
```

**Success criteria:**
- ✅ Collector runs → DB updated
- ✅ Twitter monitor runs → Hype calculated
- ✅ Signal generator runs → Signals detected/logged
- ✅ Total time <3 minutes
- ✅ No conflicts/locks

---

### Test 7: Database Integrity

**What it tests:** Data consistency, relationships

```bash
sqlite3 polymarket_data.db << EOF
-- Check for orphaned records
SELECT COUNT(*) FROM snapshots WHERE market_id NOT IN (SELECT market_id FROM markets);
-- Should return: 0

-- Check for duplicate timestamps
SELECT market_id, timestamp, COUNT(*) 
FROM snapshots 
GROUP BY market_id, timestamp 
HAVING COUNT(*) > 1;
-- Should return: empty (no duplicates)

-- Check data types
SELECT typeof(price_yes), typeof(volume_24h), typeof(timestamp) 
FROM snapshots LIMIT 1;
-- Should return: real, real, text

-- Check for NULLs in critical fields
SELECT COUNT(*) FROM snapshots WHERE price_yes IS NULL OR market_id IS NULL;
-- Should return: 0
EOF
```

**Success criteria:**
- ✅ No orphaned records
- ✅ No duplicates
- ✅ Correct data types
- ✅ No critical NULLs

---

### Test 8: Performance Under Load

**What it tests:** System handles many markets

```bash
# Simulate heavy load
for i in {1..5}; do
  python polymarket-data-collector.py &
done
wait

# Check for errors
grep -i error logs/*.log

# Verify no database corruption
sqlite3 polymarket_data.db "PRAGMA integrity_check;"
# Should return: ok
```

**Success criteria:**
- ✅ All instances complete
- ✅ No database locks
- ✅ No corruption
- ✅ Data consistent

---

## 🎭 EDGE CASE TESTS

### Test 9: API Failures

**What it tests:** Graceful degradation

```bash
# Disconnect internet, run collector
# Expected: Error logged, script exits gracefully (not crash)

# Re-enable internet, verify recovery
python polymarket-data-collector.py
# Expected: Resumes normal operation
```

---

### Test 10: Empty Data Scenarios

**What it tests:** Handling missing data

```bash
# New database (no history)
rm polymarket_data.db
python signal-generator.py

# Expected: "Need 24h+ data for RVR" message, no crash
```

---

### Test 11: Bad Configuration

**What it tests:** Config validation

```bash
# Invalid config
echo '{"invalid": json}' > config.json
python signal-generator.py

# Expected: Clear error message, suggests fix

# Missing config
rm config.json
python signal-generator.py

# Expected: Uses defaults or prompts for config
```

---

## 📊 DATA QUALITY TESTS

### Test 12: Price Sanity Checks

```bash
sqlite3 polymarket_data.db << EOF
-- Prices should be 0-1 range
SELECT COUNT(*) FROM snapshots WHERE price_yes < 0 OR price_yes > 1;
-- Should return: 0

-- Volume should be positive
SELECT COUNT(*) FROM snapshots WHERE volume_24h < 0;
-- Should return: 0

-- Check for impossible spreads
SELECT COUNT(*) FROM snapshots WHERE spread < 0 OR spread > 1;
-- Should return: 0
EOF
```

---

### Test 13: Hype Score Validation

```bash
sqlite3 polymarket_data.db << EOF
-- Hype scores should be 0-100
SELECT COUNT(*) FROM hype_signals WHERE hype_score < 0 OR hype_score > 100;
-- Should return: 0

-- Tweet counts should be positive
SELECT COUNT(*) FROM hype_signals WHERE tweet_count < 0;
-- Should return: 0
EOF
```

---

## 🚨 FAILURE MODE TESTS

### Test 14: Corrupted Database

```bash
# Backup first
cp polymarket_data.db polymarket_data.db.backup

# Simulate corruption
echo "garbage" >> polymarket_data.db

# Run scripts
python polymarket-data-collector.py

# Expected: Detects corruption, suggests restore
# Restore from backup
cp polymarket_data.db.backup polymarket_data.db
```

---

### Test 15: Disk Space Exhaustion

```bash
# Check available space
df -h .

# Estimate growth rate
ls -lh polymarket_data.db
# ~5-10 MB/day expected

# Verify enough space for 30+ days
# Need: ~300-500 MB minimum
```

---

## ✅ ACCEPTANCE CRITERIA

### System is READY when:

**Data Collection:**
- ✅ Collector runs error-free
- ✅ Twitter monitor runs error-free
- ✅ Data populating continuously
- ✅ No gaps >2 hours in snapshots

**Data Quality:**
- ✅ Prices in valid range (0-1)
- ✅ Volumes positive
- ✅ No database corruption
- ✅ Timestamps sequential

**Signal Generation:**
- ✅ Analyzes markets correctly
- ✅ Applies risk management
- ✅ Generates valid position sizes
- ✅ Logs signals properly

**Performance:**
- ✅ Each run <60 seconds
- ✅ No memory leaks
- ✅ Handles concurrent access
- ✅ Recovers from failures

---

## 🐛 COMMON TEST FAILURES & FIXES

### "Database is locked"
**Cause:** Multiple scripts accessing DB  
**Fix:** Kill other processes, retry

### "No module named 'statsmodels'"
**Cause:** Missing dependencies  
**Fix:** `pip install -r requirements.txt`

### "snscrape: command not found"
**Cause:** Not installed or not in PATH  
**Fix:** `pip install snscrape`

### "Empty result from API"
**Cause:** Network issue or API down  
**Fix:** Retry, check Polymarket status

### "Need 24h+ of data"
**Cause:** Insufficient history for calculations  
**Fix:** Wait for data to accumulate

---

## 📈 CONTINUOUS TESTING

### Daily Tests (Automated)

Add to cron/Task Scheduler:

```bash
# Run data quality checks daily at 3 AM
0 3 * * * cd /path/to/workspace && python test_data_quality.py
```

Create `test_data_quality.py`:

```python
#!/usr/bin/env python3
"""Daily data quality checks"""
import sqlite3

def run_checks():
    conn = sqlite3.connect('polymarket_data.db')
    cursor = conn.cursor()
    
    # Check for recent data
    cursor.execute("""
        SELECT MAX(timestamp) FROM snapshots
    """)
    last_snapshot = cursor.fetchone()[0]
    # Verify <2 hours old
    
    # Check row counts growing
    # Check for anomalies
    # Send alert if issues
    
    conn.close()

if __name__ == '__main__':
    run_checks()
```

---

## 🎯 PRE-LIVE CHECKLIST

Before deploying real capital, verify:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] 30+ days of clean data
- [ ] Backtest shows positive Sharpe (>1.0)
- [ ] Paper trading validates backtest
- [ ] Risk management tested
- [ ] Emergency stop procedures documented
- [ ] Backup/recovery tested
- [ ] Monitoring alerts working

**Only proceed if ALL boxes checked.**

---

## 📞 TEST SUPPORT

**If tests fail unexpectedly:**

1. Check logs: `cat logs/*.log`
2. Verify dependencies: `pip list`
3. Test internet: `ping 8.8.8.8`
4. Check disk space: `df -h`
5. Restart fresh: Delete DB, re-run tests

**Still failing?**
- Review error messages carefully
- Google specific error
- Check GitHub issues
- Simplify test (isolate component)

---

**All tests passing?** ✅ **System validated!** Ready for deployment.

**Tests failing?** 🔴 **Do not deploy.** Fix issues first.
