"""
Monitor Daemon - Main orchestrator for Polymarket monitoring
Runs continuously: scrape → calculate → alert every hour
"""
import logging
import time
import schedule
from datetime import datetime
import sys

from database import init_database, cleanup_old_data
from polymarket_scraper import scrape_and_store
from rvr_calculator import calculate_signals
from telegram_alerter import send_alerts


# Import config
try:
    from config import LOG_FILE, SCRAPE_INTERVAL_MINUTES, CLEANUP_TIME, DATA_RETENTION_DAYS, DEBUG_MODE
except ImportError:
    # Fallback defaults
    LOG_FILE = "monitor.log"
    SCRAPE_INTERVAL_MINUTES = 60
    CLEANUP_TIME = "03:00"
    DATA_RETENTION_DAYS = 7
    DEBUG_MODE = False

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def monitoring_cycle():
    """
    One complete monitoring cycle: scrape → calculate → alert
    """
    cycle_start = datetime.now()
    logger.info("")
    logger.info("🔄 " + "=" * 58 + " 🔄")
    logger.info(f"Starting monitoring cycle at {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 64)
    
    try:
        # Step 1: Scrape market data
        logger.info("Step 1/3: Scraping Polymarket data...")
        markets_scraped = scrape_and_store()
        logger.info(f"✅ Scraped {markets_scraped} markets")
        
        # Small delay between steps
        time.sleep(2)
        
        # Step 2: Calculate signals
        logger.info("Step 2/3: Calculating RVR signals...")
        signals = calculate_signals()
        logger.info(f"✅ Found {len(signals)} new signals")
        
        # Small delay between steps
        time.sleep(2)
        
        # Step 3: Send alerts
        logger.info("Step 3/3: Sending Telegram alerts...")
        alerts_sent = send_alerts()
        logger.info(f"✅ Sent {alerts_sent} alerts")
        
        cycle_end = datetime.now()
        duration = (cycle_end - cycle_start).total_seconds()
        
        logger.info("=" * 64)
        logger.info(f"✅ Cycle complete in {duration:.1f}s")
        logger.info("=" * 64)
        
    except Exception as e:
        logger.error(f"❌ Error in monitoring cycle: {e}", exc_info=True)
        logger.error("=" * 64)


def daily_cleanup():
    """
    Daily cleanup task - remove old data
    """
    logger.info("🧹 Running daily cleanup...")
    try:
        cleanup_old_data(days=DATA_RETENTION_DAYS)
        logger.info("✅ Cleanup complete")
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")


def run_daemon():
    """
    Main daemon loop - runs continuously
    """
    logger.info("🚀 " + "=" * 58 + " 🚀")
    logger.info("POLYMARKET MONITOR DAEMON STARTING")
    logger.info("=" * 64)
    logger.info(f"Log file: {LOG_FILE}")
    logger.info(f"Database: polymarket_data.db")
    logger.info(f"Monitoring interval: {SCRAPE_INTERVAL_MINUTES} minutes")
    logger.info(f"Cleanup interval: 24 hours")
    logger.info("=" * 64)
    
    # Initialize database
    logger.info("Initializing database...")
    init_database()
    
    # Run initial cycle immediately
    logger.info("Running initial monitoring cycle...")
    monitoring_cycle()
    
    # Schedule recurring tasks
    schedule.every(SCRAPE_INTERVAL_MINUTES).minutes.do(monitoring_cycle)
    schedule.every().day.at(CLEANUP_TIME).do(daily_cleanup)
    
    logger.info("")
    logger.info(f"⏰ Scheduler active - monitoring every {SCRAPE_INTERVAL_MINUTES} minutes")
    logger.info("Press Ctrl+C to stop")
    logger.info("")
    
    # Main loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 64)
        logger.info("🛑 Shutdown signal received")
        logger.info("=" * 64)
        logger.info("Daemon stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_daemon()
