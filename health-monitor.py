#!/usr/bin/env python3
"""
🏥 Polymarket Hype Trading System - Health Monitor

Automated health checks every 5 minutes:
  - Database size and age
  - Data collection freshness
  - API connectivity
  - Disk space
  - Process status
  - Data quality

Sends alerts via Telegram when issues detected.

Author: Wom + Borat AI
"""

import os
import sys
import sqlite3
import requests
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import psutil
import json
from typing import Dict, List, Tuple, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

WORKSPACE = Path(__file__).parent
CONFIG_FILE = WORKSPACE / "config.yaml"
DB_FILE = WORKSPACE / "polymarket_data.db"
LOG_FILE = WORKSPACE / "logs" / "health-monitor.log"
HEALTH_STATE_FILE = WORKSPACE / "health-state.json"

# Health check thresholds
THRESHOLDS = {
    "db_max_size_gb": 5.0,
    "db_warn_size_gb": 4.0,
    "data_stale_minutes": 30,
    "disk_min_free_gb": 0.5,
    "min_markets": 10,
    "min_snapshots_per_day": 50,
    "min_tweets_per_day": 20,
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_config() -> dict:
    """Load configuration from config.yaml"""
    if not CONFIG_FILE.exists():
        return {}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        log(f"Error loading config: {e}", "ERROR")
        return {}

def log(message: str, level: str = "INFO"):
    """Write log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    
    # Console
    print(log_line)
    
    # File
    LOG_FILE.parent.mkdir(exist_ok=True)
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_line + "\n")
    except:
        pass

def load_health_state() -> dict:
    """Load previous health state"""
    if not HEALTH_STATE_FILE.exists():
        return {}
    
    try:
        with open(HEALTH_STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_health_state(state: dict):
    """Save health state for next run"""
    try:
        with open(HEALTH_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log(f"Could not save health state: {e}", "WARNING")

def send_telegram_alert(message: str, critical: bool = False):
    """Send alert via Telegram (if configured)"""
    config = load_config()
    
    if not config.get("alerts", {}).get("telegram_enabled"):
        return  # Telegram not configured
    
    token = config["alerts"].get("telegram_token")
    chat_id = config["alerts"].get("telegram_chat_id")
    
    if not token or not chat_id:
        return
    
    # Check quiet hours (unless critical)
    if not critical:
        now = datetime.now().time()
        quiet_start = config["alerts"].get("quiet_hours_start", "23:00")
        quiet_end = config["alerts"].get("quiet_hours_end", "08:00")
        
        # Simple time range check (assumes same day)
        try:
            start_time = datetime.strptime(quiet_start, "%H:%M").time()
            end_time = datetime.strptime(quiet_end, "%H:%M").time()
            
            if start_time <= now or now <= end_time:
                log("Skipping alert (quiet hours)", "INFO")
                return
        except:
            pass
    
    # Send message
    emoji = "🚨" if critical else "⚠️"
    full_message = f"{emoji} **HEALTH ALERT**\n\n{message}"
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": full_message,
            "parse_mode": "Markdown",
        }
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            log("Telegram alert sent", "INFO")
        else:
            log(f"Telegram alert failed: {response.status_code}", "WARNING")
    except Exception as e:
        log(f"Could not send Telegram alert: {e}", "WARNING")

# ============================================================================
# HEALTH CHECKS
# ============================================================================

def check_database() -> Tuple[bool, List[str]]:
    """Check database health"""
    issues = []
    
    if not DB_FILE.exists():
        issues.append("❌ Database file not found")
        return False, issues
    
    # Check size
    size_gb = DB_FILE.stat().st_size / (1024 ** 3)
    
    if size_gb >= THRESHOLDS["db_max_size_gb"]:
        issues.append(f"❌ Database size: {size_gb:.2f} GB (exceeds {THRESHOLDS['db_max_size_gb']} GB limit)")
    elif size_gb >= THRESHOLDS["db_warn_size_gb"]:
        issues.append(f"⚠️  Database size: {size_gb:.2f} GB (approaching {THRESHOLDS['db_max_size_gb']} GB limit)")
    else:
        log(f"✅ Database size: {size_gb:.2f} GB", "INFO")
    
    # Check tables and data
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check market count
        cursor.execute("SELECT COUNT(*) FROM markets")
        market_count = cursor.fetchone()[0]
        
        if market_count < THRESHOLDS["min_markets"]:
            issues.append(f"⚠️  Only {market_count} markets tracked (expected {THRESHOLDS['min_markets']}+)")
        else:
            log(f"✅ Markets: {market_count}", "INFO")
        
        # Check data freshness (last snapshot)
        cursor.execute("SELECT MAX(timestamp) FROM snapshots")
        last_snapshot = cursor.fetchone()[0]
        
        if last_snapshot:
            last_time = datetime.fromisoformat(last_snapshot)
            age_minutes = (datetime.now() - last_time).total_seconds() / 60
            
            if age_minutes > THRESHOLDS["data_stale_minutes"]:
                issues.append(f"❌ Data is stale (last snapshot: {age_minutes:.0f} min ago)")
            else:
                log(f"✅ Latest data: {age_minutes:.0f} min ago", "INFO")
        else:
            issues.append("❌ No snapshots in database")
        
        # Check daily collection rates
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        cursor.execute(f"SELECT COUNT(*) FROM snapshots WHERE timestamp >= '{yesterday}'")
        recent_snapshots = cursor.fetchone()[0]
        
        if recent_snapshots < THRESHOLDS["min_snapshots_per_day"]:
            issues.append(f"⚠️  Low snapshot rate: {recent_snapshots} in last 24h (expected {THRESHOLDS['min_snapshots_per_day']}+)")
        else:
            log(f"✅ Snapshots (24h): {recent_snapshots}", "INFO")
        
        cursor.execute(f"SELECT COUNT(*) FROM tweets WHERE timestamp >= '{yesterday}'")
        recent_tweets = cursor.fetchone()[0]
        
        if recent_tweets < THRESHOLDS["min_tweets_per_day"]:
            issues.append(f"⚠️  Low tweet collection: {recent_tweets} in last 24h (expected {THRESHOLDS['min_tweets_per_day']}+)")
        else:
            log(f"✅ Tweets (24h): {recent_tweets}", "INFO")
        
        conn.close()
        
    except Exception as e:
        issues.append(f"❌ Database query error: {e}")
        return False, issues
    
    return len(issues) == 0, issues

def check_api_connectivity() -> Tuple[bool, List[str]]:
    """Check if APIs are reachable"""
    issues = []
    
    # Polymarket API
    try:
        response = requests.get(
            "https://gamma-api.polymarket.com/markets?active=true&limit=1",
            timeout=10
        )
        if response.status_code == 200:
            log("✅ Polymarket API: OK", "INFO")
        else:
            issues.append(f"⚠️  Polymarket API returned {response.status_code}")
    except Exception as e:
        issues.append(f"❌ Polymarket API unreachable: {e}")
    
    # Twitter/X (just check if domain resolves, can't test scraping easily)
    try:
        response = requests.get("https://x.com", timeout=10)
        if response.status_code in [200, 301, 302]:
            log("✅ X/Twitter: OK", "INFO")
        else:
            issues.append(f"⚠️  X/Twitter returned {response.status_code}")
    except Exception as e:
        issues.append(f"❌ X/Twitter unreachable: {e}")
    
    return len(issues) == 0, issues

def check_disk_space() -> Tuple[bool, List[str]]:
    """Check available disk space"""
    issues = []
    
    try:
        disk = psutil.disk_usage(str(WORKSPACE))
        free_gb = disk.free / (1024 ** 3)
        
        if free_gb < THRESHOLDS["disk_min_free_gb"]:
            issues.append(f"❌ Low disk space: {free_gb:.2f} GB free")
        else:
            log(f"✅ Disk space: {free_gb:.1f} GB free", "INFO")
    except Exception as e:
        issues.append(f"⚠️  Could not check disk space: {e}")
    
    return len(issues) == 0, issues

def check_process_status() -> Tuple[bool, List[str]]:
    """Check if all critical processes are running"""
    issues = []
    
    pid_file = WORKSPACE / "system.pids"
    
    if not pid_file.exists():
        issues.append("⚠️  System not running (no PID file found)")
        return False, issues
    
    try:
        with open(pid_file, 'r') as f:
            pids = json.load(f)
    except Exception as e:
        issues.append(f"❌ Could not read PID file: {e}")
        return False, issues
    
    critical_components = ["data-collector", "twitter-monitor", "signal-generator"]
    
    for name in critical_components:
        pid = pids.get(name)
        
        if not pid:
            issues.append(f"❌ {name} not in PID file")
            continue
        
        try:
            process = psutil.Process(pid)
            if process.is_running():
                log(f"✅ {name}: running (PID {pid})", "INFO")
            else:
                issues.append(f"❌ {name}: not running (PID {pid})")
        except psutil.NoSuchProcess:
            issues.append(f"❌ {name}: process not found (PID {pid})")
    
    return len(issues) == 0, issues

def check_data_quality() -> Tuple[bool, List[str]]:
    """Check for data anomalies"""
    issues = []
    
    if not DB_FILE.exists():
        return True, []  # Already caught by check_database
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check for price jumps >50% (likely errors)
        cursor.execute("""
            SELECT m.question, s1.price, s2.price, 
                   ABS(s2.price - s1.price) / s1.price AS change
            FROM snapshots s1
            JOIN snapshots s2 ON s1.market_id = s2.market_id
            JOIN markets m ON s1.market_id = m.market_id
            WHERE s2.timestamp > s1.timestamp
              AND ABS(s2.price - s1.price) / s1.price > 0.5
            ORDER BY change DESC
            LIMIT 5
        """)
        
        anomalies = cursor.fetchall()
        if anomalies:
            issues.append(f"⚠️  Detected {len(anomalies)} suspicious price jumps")
            for q, p1, p2, change in anomalies[:2]:
                issues.append(f"   {q[:50]}... | {p1:.3f} → {p2:.3f} ({change*100:.0f}% change)")
        
        # Check for duplicate tweets
        cursor.execute("""
            SELECT COUNT(*), text 
            FROM tweets 
            GROUP BY text 
            HAVING COUNT(*) > 5
            LIMIT 3
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            issues.append(f"⚠️  Detected {len(duplicates)} duplicate tweets (possible bot activity)")
        
        conn.close()
        
    except Exception as e:
        issues.append(f"⚠️  Could not check data quality: {e}")
    
    return len(issues) == 0, issues

# ============================================================================
# MAIN HEALTH CHECK
# ============================================================================

def run_health_check():
    """Run all health checks and report issues"""
    log("="*80, "INFO")
    log("HEALTH CHECK STARTED", "INFO")
    log("="*80, "INFO")
    
    # Load previous state
    prev_state = load_health_state()
    current_state = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
    }
    
    # Run checks
    checks = [
        ("Database", check_database),
        ("API Connectivity", check_api_connectivity),
        ("Disk Space", check_disk_space),
        ("Process Status", check_process_status),
        ("Data Quality", check_data_quality),
    ]
    
    all_healthy = True
    critical_issues = []
    warnings = []
    
    for check_name, check_func in checks:
        log(f"\n📊 Checking: {check_name}", "INFO")
        
        try:
            healthy, issues = check_func()
            
            current_state["checks"][check_name] = {
                "healthy": healthy,
                "issues": issues,
            }
            
            if not healthy:
                all_healthy = False
            
            # Categorize issues
            for issue in issues:
                if issue.startswith("❌"):
                    critical_issues.append(f"{check_name}: {issue}")
                elif issue.startswith("⚠️"):
                    warnings.append(f"{check_name}: {issue}")
        
        except Exception as e:
            log(f"❌ Check failed: {e}", "ERROR")
            critical_issues.append(f"{check_name}: Check crashed ({e})")
            all_healthy = False
    
    # Summary
    log("\n" + "="*80, "INFO")
    if all_healthy:
        log("✅ ALL CHECKS PASSED - SYSTEM HEALTHY", "INFO")
    else:
        log(f"⚠️  ISSUES DETECTED: {len(critical_issues)} critical, {len(warnings)} warnings", "WARNING")
    log("="*80 + "\n", "INFO")
    
    # Send alerts if needed
    config = load_config()
    if config.get("alerts", {}).get("send_system_alerts", True):
        # New critical issues (not in previous state)
        new_critical = []
        prev_critical = prev_state.get("critical_issues", [])
        
        for issue in critical_issues:
            if issue not in prev_critical:
                new_critical.append(issue)
        
        if new_critical:
            alert_msg = "**Critical System Issues Detected:**\n\n"
            alert_msg += "\n".join(f"• {issue}" for issue in new_critical[:5])
            
            if len(new_critical) > 5:
                alert_msg += f"\n\n... and {len(new_critical) - 5} more issues"
            
            send_telegram_alert(alert_msg, critical=True)
        
        # Warnings (only send once per day)
        if warnings and not prev_state.get("warnings_sent_today"):
            alert_msg = "**System Warnings:**\n\n"
            alert_msg += "\n".join(f"• {w}" for w in warnings[:5])
            send_telegram_alert(alert_msg, critical=False)
            current_state["warnings_sent_today"] = True
    
    # Save state
    current_state["critical_issues"] = critical_issues
    current_state["warnings"] = warnings
    save_health_state(current_state)
    
    log(f"Health check complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
    
    return all_healthy

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        healthy = run_health_check()
        sys.exit(0 if healthy else 1)
    except Exception as e:
        log(f"❌ Health check crashed: {e}", "ERROR")
        sys.exit(1)
