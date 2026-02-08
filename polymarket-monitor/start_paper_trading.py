"""
One-Command Paper Trading System Launcher
Initializes and starts the complete paper trading system
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   FORWARD PAPER TRADING SYSTEM                              ║
║   Polymarket Strategy Validation                            ║
║                                                              ║
║   NO REAL MONEY - Data Collection Mode                       ║
║   Purpose: Validate strategy before $100 USDC deployment    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """Check if all requirements are met"""
    print("\n🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        return False
    print("✅ Python version OK")
    
    # Check required modules
    try:
        import requests
        import schedule
        print("✅ Required packages installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Run: pip install requests schedule")
        return False
    
    # Check if database files exist
    db_path = Path("polymarket_data.db")
    if not db_path.exists():
        print("⚠️  Database not found - will be created")
    else:
        print("✅ Database found")
    
    return True

def initialize_database():
    """Initialize database tables"""
    print("\n📊 Initializing database...")
    
    try:
        from paper_trading_db import init_paper_trading_tables
        init_paper_trading_tables()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_components():
    """Test all system components"""
    print("\n🧪 Testing components...")
    
    # Test imports
    try:
        from forward_paper_trader import ForwardPaperTrader
        print("✅ Forward paper trader OK")
        
        from paper_position_manager import PaperPositionManager
        print("✅ Position manager OK")
        
        from outcome_tracker import OutcomeTracker
        print("✅ Outcome tracker OK")
        
        from daily_reporter import DailyReporter
        print("✅ Daily reporter OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def send_startup_notification():
    """Send Telegram notification that system started"""
    try:
        from telegram_alerter import send_alert
        
        message = """
🚀 PAPER TRADING SYSTEM STARTED

✅ All components initialized
📊 Monitoring active markets
🎯 Detecting signals (RVR, ROC, trend)
💰 Starting bankroll: $100.00

⏰ Monitoring cycle: Every 60 minutes
📈 Daily reports: 10:00 AM

🧪 PAPER TRADING MODE - NO REAL MONEY
Purpose: 30-day forward validation before live deployment

System is now running. You'll receive alerts when:
• New signals detected
• Paper trades entered
• Positions exited (TP/SL)
• Markets resolved
• Daily performance reports

Happy validating! 🎯
        """.strip()
        
        send_alert(message)
        print("✅ Startup notification sent to Telegram")
        
    except Exception as e:
        print(f"⚠️  Could not send Telegram notification: {e}")

def show_instructions():
    """Show post-startup instructions"""
    instructions = """
╔══════════════════════════════════════════════════════════════╗
║  SYSTEM RUNNING - NEXT STEPS                                 ║
╚══════════════════════════════════════════════════════════════╝

📊 MONITORING DASHBOARD:
   Open: http://localhost:8080
   Real-time stats and trade history

📁 LOG FILES:
   • paper_trading_system.log - Main system log
   • paper_trading.log - Trade execution log

📱 TELEGRAM ALERTS:
   You'll receive notifications for:
   • New signals → Paper trade entries
   • Stop-loss / Take-profit exits
   • Market resolutions
   • Daily performance reports (10:00 AM)

🛑 TO STOP SYSTEM:
   Press Ctrl+C

📊 MANUAL COMMANDS:
   • Generate report now:
     python daily_reporter.py
   
   • Check open positions:
     python paper_position_manager.py
   
   • Check resolutions:
     python outcome_tracker.py
   
   • View dashboard:
     python dashboard.py

⏳ VALIDATION TIMELINE:
   • Days 1-7: System ramp-up, initial signals
   • Days 8-30: Data collection phase
   • Day 30: First go-live assessment
   • Days 31-60: Extended validation (optional)
   • Day 60+: Scale-up decision

🎯 SUCCESS CRITERIA (30 days):
   ✓ 20+ resolved trades
   ✓ 55%+ win rate
   ✓ Positive total P&L
   ✓ Edge validated (within 5pp of backtest)

═══════════════════════════════════════════════════════════════

System is monitoring markets and will alert you automatically.
Keep this window open or run in background.

Press Ctrl+C to stop.
    """
    print(instructions)

def start_dashboard_background():
    """Start dashboard in background (Windows-compatible)"""
    try:
        if sys.platform == 'win32':
            # Windows: use START command to run in new window
            subprocess.Popen(
                ['python', 'dashboard.py'],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Unix: use nohup
            subprocess.Popen(
                ['python', 'dashboard.py'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print("✅ Dashboard started at http://localhost:8080")
        time.sleep(2)
        
    except Exception as e:
        print(f"⚠️  Could not start dashboard: {e}")
        print("   You can start it manually: python dashboard.py")

def main():
    """Main startup sequence"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix issues and try again.")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("\n❌ Database initialization failed.")
        sys.exit(1)
    
    # Test components
    if not test_components():
        print("\n❌ Component testing failed.")
        sys.exit(1)
    
    # Start dashboard in background
    start_dashboard_background()
    
    # Send startup notification
    send_startup_notification()
    
    # Show instructions
    show_instructions()
    
    # Start main system
    print("\n🚀 Starting paper trading system...\n")
    
    try:
        from paper_trading_main import PaperTradingSystem
        
        system = PaperTradingSystem()
        system.run_daemon()
        
    except KeyboardInterrupt:
        print("\n\n🛑 System stopped by user")
        print("\n📊 Final Statistics:")
        
        # Show final stats
        try:
            from daily_reporter import DailyReporter
            reporter = DailyReporter()
            reporter.generate_daily_report()
        except:
            pass
        
        print("\n✅ System shut down cleanly")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ System error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
