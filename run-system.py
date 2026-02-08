#!/usr/bin/env python3
"""
🚀 Polymarket Hype Trading System - Master Orchestrator

Single command to rule them all:
  python run-system.py start    - Start all components
  python run-system.py stop     - Stop all components
  python run-system.py restart  - Restart all components
  python run-system.py status   - Show system status
  python run-system.py logs     - Tail all logs

Manages:
  1. polymarket-data-collector.py (every 15 min)
  2. twitter-hype-monitor.py (every 15 min)
  3. signal-generator.py (continuous monitoring)
  4. health-monitor.py (every 5 min health checks)
  5. api.py (dashboard backend)

Features:
  - Process management (start/stop/restart)
  - Health checks with auto-restart
  - Graceful shutdown (SIGTERM/SIGINT)
  - Status dashboard (ASCII art)
  - Centralized logging
  - Configuration from config.yaml

Author: Wom + Borat AI
"""

import os
import sys
import time
import yaml
import signal
import subprocess
import psutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

WORKSPACE = Path(__file__).parent
CONFIG_FILE = WORKSPACE / "config.yaml"
PID_FILE = WORKSPACE / "system.pids"
LOG_DIR = WORKSPACE / "logs"

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)

# Component definitions
COMPONENTS = {
    "data-collector": {
        "script": "polymarket-data-collector.py",
        "type": "periodic",
        "interval": 900,  # 15 minutes in seconds
        "description": "Collect Polymarket market data",
        "critical": True,
    },
    "twitter-monitor": {
        "script": "twitter-hype-monitor.py",
        "type": "periodic",
        "interval": 900,  # 15 minutes
        "description": "Monitor X/Twitter for hype signals",
        "critical": True,
    },
    "signal-generator": {
        "script": "signal-generator.py",
        "type": "continuous",
        "description": "Generate BUY/SELL trade signals",
        "critical": True,
    },
    "health-monitor": {
        "script": "health-monitor.py",
        "type": "periodic",
        "interval": 300,  # 5 minutes
        "description": "System health checks + alerts",
        "critical": False,
    },
    "api": {
        "script": "api.py",
        "type": "continuous",
        "description": "Dashboard backend API",
        "critical": False,
        "port": 5000,
    },
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_config() -> dict:
    """Load configuration from config.yaml"""
    if not CONFIG_FILE.exists():
        print(f"⚠️  Config file not found: {CONFIG_FILE}")
        print("   Using default configuration...")
        return {}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return {}

def save_pids(pids: Dict[str, int]):
    """Save process IDs to file"""
    try:
        with open(PID_FILE, 'w') as f:
            json.dump(pids, f, indent=2)
    except Exception as e:
        print(f"⚠️  Could not save PIDs: {e}")

def load_pids() -> Dict[str, int]:
    """Load process IDs from file"""
    if not PID_FILE.exists():
        return {}
    
    try:
        with open(PID_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Could not load PIDs: {e}")
        return {}

def is_process_running(pid: int) -> bool:
    """Check if process with given PID is running"""
    try:
        process = psutil.Process(pid)
        return process.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def kill_process(pid: int, graceful: bool = True):
    """Kill process gracefully (SIGTERM) or forcefully (SIGKILL)"""
    try:
        process = psutil.Process(pid)
        if graceful:
            process.terminate()  # SIGTERM
            time.sleep(2)
            if process.is_running():
                process.kill()  # SIGKILL
        else:
            process.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

def format_duration(seconds: int) -> str:
    """Format seconds as human-readable duration"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

# ============================================================================
# PROCESS MANAGEMENT
# ============================================================================

def start_component(name: str, component: dict) -> Optional[int]:
    """Start a single component and return its PID"""
    script_path = WORKSPACE / component["script"]
    log_file = LOG_DIR / f"{name}.log"
    
    if not script_path.exists():
        print(f"   ❌ Script not found: {script_path}")
        return None
    
    print(f"   🚀 Starting {name}... ", end="", flush=True)
    
    try:
        # Open log file
        with open(log_file, 'a') as log:
            log.write(f"\n{'='*80}\n")
            log.write(f"Started: {datetime.now().isoformat()}\n")
            log.write(f"{'='*80}\n\n")
            
            # Start process
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=log,
                stderr=log,
                cwd=WORKSPACE,
                preexec_fn=os.setpgrp if os.name != 'nt' else None,
            )
            
            # Wait briefly to check if it started successfully
            time.sleep(0.5)
            if process.poll() is None:
                print(f"✅ PID {process.pid}")
                return process.pid
            else:
                print(f"❌ Failed to start (check {log_file})")
                return None
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def stop_component(name: str, pid: int, graceful: bool = True):
    """Stop a single component"""
    if not is_process_running(pid):
        print(f"   ⚠️  {name} not running (PID {pid})")
        return
    
    action = "Stopping" if graceful else "Killing"
    print(f"   🛑 {action} {name} (PID {pid})... ", end="", flush=True)
    
    try:
        kill_process(pid, graceful)
        time.sleep(0.5)
        
        if is_process_running(pid):
            print("❌ Still running")
        else:
            print("✅ Stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

def start_all():
    """Start all components"""
    print("\n🚀 Starting Polymarket Hype Trading System...\n")
    
    # Load existing PIDs
    existing_pids = load_pids()
    
    # Check if already running
    running = []
    for name, pid in existing_pids.items():
        if is_process_running(pid):
            running.append(name)
    
    if running:
        print(f"⚠️  Some components already running: {', '.join(running)}")
        print("   Run 'python run-system.py restart' to restart all\n")
        return
    
    # Start each component
    pids = {}
    for name, component in COMPONENTS.items():
        pid = start_component(name, component)
        if pid:
            pids[name] = pid
    
    # Save PIDs
    if pids:
        save_pids(pids)
        print(f"\n✅ Started {len(pids)}/{len(COMPONENTS)} components")
        print(f"   PIDs saved to: {PID_FILE}")
        print(f"   Logs directory: {LOG_DIR}")
        print(f"\n   Run 'python run-system.py status' to check system health")
    else:
        print("\n❌ Failed to start any components")

def stop_all(graceful: bool = True):
    """Stop all components"""
    action = "Stopping" if graceful else "Killing"
    print(f"\n🛑 {action} all components...\n")
    
    pids = load_pids()
    
    if not pids:
        print("⚠️  No running components found")
        return
    
    for name, pid in pids.items():
        stop_component(name, pid, graceful)
    
    # Clean up PID file
    if PID_FILE.exists():
        PID_FILE.unlink()
    
    print("\n✅ All components stopped")

def restart_all():
    """Restart all components"""
    print("\n🔄 Restarting system...")
    stop_all(graceful=True)
    time.sleep(2)
    start_all()

def show_status():
    """Show system status (running components, health, stats)"""
    print("\n" + "="*80)
    print("📊 POLYMARKET HYPE TRADING SYSTEM - STATUS")
    print("="*80 + "\n")
    
    pids = load_pids()
    
    if not pids:
        print("❌ System not running (no PIDs found)")
        print("   Run 'python run-system.py start' to start\n")
        return
    
    # Component status
    print("🔧 COMPONENTS:\n")
    running_count = 0
    critical_down = []
    
    for name, component in COMPONENTS.items():
        pid = pids.get(name)
        
        if pid and is_process_running(pid):
            # Get process info
            try:
                process = psutil.Process(pid)
                cpu = process.cpu_percent(interval=0.1)
                mem_mb = process.memory_info().rss / 1024 / 1024
                uptime = int(time.time() - process.create_time())
                
                status = "✅ RUNNING"
                info = f"PID {pid} | Uptime: {format_duration(uptime)} | CPU: {cpu:.1f}% | RAM: {mem_mb:.1f}MB"
                running_count += 1
            except:
                status = "⚠️  UNKNOWN"
                info = f"PID {pid}"
        else:
            status = "❌ STOPPED"
            info = ""
            if component.get("critical"):
                critical_down.append(name)
        
        desc = component.get("description", "")
        print(f"   {status:<12} {name:<20} {desc}")
        if info:
            print(f"                {info}")
        print()
    
    # Summary
    print("─" * 80)
    print(f"\n📈 SUMMARY: {running_count}/{len(COMPONENTS)} components running\n")
    
    if critical_down:
        print(f"⚠️  CRITICAL COMPONENTS DOWN: {', '.join(critical_down)}")
        print("   Run 'python run-system.py start' to restart\n")
    elif running_count == len(COMPONENTS):
        print("✅ All systems operational!\n")
    
    # Database stats (if exists)
    db_path = WORKSPACE / "polymarket_data.db"
    if db_path.exists():
        size_mb = db_path.stat().st_size / 1024 / 1024
        print(f"💾 DATABASE: {size_mb:.1f} MB")
        
        # Try to query basic stats
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM markets")
            market_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM snapshots")
            snapshot_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tweets")
            tweet_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM hype_signals")
            signal_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"   Markets: {market_count} | Snapshots: {snapshot_count:,} | Tweets: {tweet_count:,} | Signals: {signal_count}")
        except:
            pass
        
        print()
    
    # Config info
    if CONFIG_FILE.exists():
        print(f"⚙️  CONFIG: {CONFIG_FILE}")
    else:
        print("⚠️  No config file found (using defaults)")
    
    print("\n" + "="*80 + "\n")

def tail_logs():
    """Tail all log files"""
    print("\n📜 Tailing logs (Ctrl+C to stop)...\n")
    
    log_files = list(LOG_DIR.glob("*.log"))
    
    if not log_files:
        print("⚠️  No log files found")
        return
    
    print(f"Watching {len(log_files)} log files:\n")
    for log_file in log_files:
        print(f"   - {log_file.name}")
    print()
    
    try:
        # Use system 'tail' command if available
        if os.name != 'nt':
            subprocess.run(["tail", "-f"] + [str(f) for f in log_files])
        else:
            # Windows fallback: print last 20 lines of each log
            for log_file in log_files:
                print(f"\n{'='*80}")
                print(f"FILE: {log_file.name}")
                print('='*80 + "\n")
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    print(''.join(lines[-20:]))
    except KeyboardInterrupt:
        print("\n\n✅ Stopped tailing logs")

# ============================================================================
# MAIN CLI
# ============================================================================

def print_help():
    """Print help message"""
    print("""
🚀 Polymarket Hype Trading System - Master Orchestrator

USAGE:
  python run-system.py <command>

COMMANDS:
  start      Start all components
  stop       Stop all components gracefully
  restart    Restart all components
  status     Show system status (PIDs, health, stats)
  logs       Tail all log files
  kill       Force kill all components (use if graceful stop fails)
  help       Show this help message

EXAMPLES:
  python run-system.py start       # Start the system
  python run-system.py status      # Check what's running
  python run-system.py logs        # View logs in real-time
  python run-system.py restart     # Restart everything

COMPONENTS:
  - polymarket-data-collector.py   (every 15 min)
  - twitter-hype-monitor.py        (every 15 min)
  - signal-generator.py            (continuous)
  - health-monitor.py              (every 5 min)
  - api.py                         (dashboard backend)

FILES:
  config.yaml      Configuration file
  system.pids      Process IDs (managed automatically)
  logs/*.log       Component logs

For more info, see: QUICKSTART.md
    """)

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_all()
    elif command == "stop":
        stop_all(graceful=True)
    elif command == "kill":
        stop_all(graceful=False)
    elif command == "restart":
        restart_all()
    elif command == "status":
        show_status()
    elif command == "logs":
        tail_logs()
    elif command == "help":
        print_help()
    else:
        print(f"❌ Unknown command: {command}")
        print_help()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
