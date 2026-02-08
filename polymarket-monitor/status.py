"""
Status checker - Quick health check for the monitoring system
"""
import sqlite3
import os
from datetime import datetime, timedelta
import sys

def check_database():
    """Check if database exists and has data"""
    if not os.path.exists("polymarket_data.db"):
        return False, "Database not found (run monitor first)"
    
    try:
        conn = sqlite3.connect("polymarket_data.db")
        cursor = conn.cursor()
        
        # Check market snapshots
        cursor.execute("SELECT COUNT(*) FROM market_snapshots")
        snapshot_count = cursor.fetchone()[0]
        
        # Check signals
        cursor.execute("SELECT COUNT(*) FROM signals")
        signal_count = cursor.fetchone()[0]
        
        # Check recent activity (last 2 hours)
        two_hours_ago = int((datetime.now() - timedelta(hours=2)).timestamp())
        cursor.execute("""
            SELECT COUNT(*) FROM market_snapshots 
            WHERE timestamp >= ?
        """, (two_hours_ago,))
        recent_count = cursor.fetchone()[0]
        
        conn.close()
        
        if recent_count == 0:
            return False, f"No recent activity (last update >2h ago) | Total: {snapshot_count} snapshots, {signal_count} signals"
        
        return True, f"{snapshot_count} snapshots, {signal_count} signals | {recent_count} in last 2h"
        
    except Exception as e:
        return False, f"Database error: {e}"


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import requests
        import schedule
        return True, "All dependencies installed"
    except ImportError as e:
        return False, f"Missing dependency: {e.name}"


def check_config():
    """Check configuration file"""
    if not os.path.exists("config.py"):
        return True, "Using default config (config.py not found)"
    
    try:
        import config
        return True, f"Telegram: {config.TELEGRAM_TARGET} | RVR: {config.RVR_THRESHOLD} | ROC: {config.ROC_THRESHOLD}%"
    except Exception as e:
        return False, f"Config error: {e}"


def check_logs():
    """Check log file"""
    if not os.path.exists("monitor.log"):
        return False, "No log file (monitor hasn't run yet)"
    
    try:
        # Get last 5 lines
        with open("monitor.log", "r") as f:
            lines = f.readlines()
            if not lines:
                return False, "Log file is empty"
            
            recent = lines[-5:]
            
            # Check for errors
            errors = [line for line in recent if "ERROR" in line or "FAILED" in line]
            if errors:
                return False, f"Recent errors found: {errors[-1].strip()[:80]}"
            
            # Check timestamp of last entry
            last_line = lines[-1]
            return True, f"Log active | Last: {last_line[:60].strip()}..."
            
    except Exception as e:
        return False, f"Log error: {e}"


def main():
    """Run all checks and display status"""
    print("=" * 70)
    print("POLYMARKET MONITOR - STATUS CHECK")
    print("=" * 70)
    print()
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("Database", check_database),
        ("Logs", check_logs),
    ]
    
    all_ok = True
    
    for name, check_func in checks:
        status, message = check_func()
        icon = "✅" if status else "❌"
        print(f"{icon} {name:15s} | {message}")
        if not status:
            all_ok = False
    
    print()
    print("=" * 70)
    
    if all_ok:
        print("✅ SYSTEM HEALTHY - Monitor is running correctly")
        print()
        print("To view live logs: tail -f monitor.log")
        print("To view signals:   sqlite3 polymarket_data.db 'SELECT * FROM signals'")
    else:
        print("⚠️  ISSUES DETECTED - See above for details")
        print()
        print("To fix:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run monitor:          python monitor_daemon.py")
        print("  3. Check logs:           cat monitor.log")
    
    print("=" * 70)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
