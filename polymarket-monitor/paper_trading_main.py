"""
Paper Trading Main Orchestrator
Coordinates all paper trading components
"""

import sys
import time
import logging
from datetime import datetime
import schedule

# Import components
from forward_paper_trader import ForwardPaperTrader
from paper_position_manager import PaperPositionManager
from outcome_tracker import OutcomeTracker
from daily_reporter import DailyReporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_trading_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class PaperTradingSystem:
    """Main system coordinator"""
    
    def __init__(self):
        """Initialize all components"""
        logger.info("="*60)
        logger.info("FORWARD PAPER TRADING SYSTEM STARTING")
        logger.info("="*60)
        
        self.trader = ForwardPaperTrader(starting_bankroll=100.0)
        self.position_manager = PaperPositionManager()
        self.outcome_tracker = OutcomeTracker()
        self.daily_reporter = DailyReporter()
        
        logger.info("All components initialized successfully")
    
    def process_signals(self):
        """
        Process any new signals from signal detector
        This gets called by the monitor_daemon cycle
        """
        try:
            logger.info("Checking for new signals...")
            
            # Import here to avoid circular dependency
            import sqlite3
            
            # Check for unprocessed signals from signal_detector
            conn = sqlite3.connect('polymarket_data.db')
            cursor = conn.cursor()
            
            # Look for recent signals (last hour)
            cutoff_time = int(time.time()) - 3600
            
            cursor.execute("""
                SELECT market_id, market_name, rvr, roc, price, volume, timestamp
                FROM signals
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            """, (cutoff_time,))
            
            signals = cursor.fetchall()
            conn.close()
            
            if not signals:
                logger.info("No new signals found")
                return
            
            logger.info(f"Found {len(signals)} recent signals")
            
            for signal_data in signals:
                market_id, market_name, rvr, roc, price, volume, timestamp = signal_data
                
                # Convert to signal dict format
                signal = {
                    'market_id': market_id,
                    'title': market_name,
                    'entry_price': price,
                    'rvr_ratio': rvr,
                    'roc_24h_pct': roc,
                    'side': 'NO' if price < 0.15 else 'YES',  # Favor NO on low probability
                    'days_to_resolution': 3,  # Default
                    'orderbook_depth': 10000  # Assume passed filter
                }
                
                # Process signal (will check if already traded)
                self.trader.process_signal(signal)
        
        except Exception as e:
            logger.error(f"Error processing signals: {e}")
    
    def monitoring_cycle(self):
        """
        Main monitoring cycle - runs every hour
        This is the core loop that coordinates everything
        """
        logger.info("="*60)
        logger.info(f"MONITORING CYCLE START - {datetime.now()}")
        logger.info("="*60)
        
        try:
            # 1. Process any new signals (execute entries)
            logger.info("Step 1: Processing new signals...")
            self.process_signals()
            
            # 2. Monitor open positions (check exits)
            logger.info("Step 2: Monitoring open positions...")
            self.position_manager.monitor_open_positions()
            
            # 3. Check for market resolutions
            logger.info("Step 3: Checking market resolutions...")
            self.outcome_tracker.check_resolutions()
            
            logger.info("Monitoring cycle complete")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
    
    def generate_daily_report(self):
        """Generate and send daily report"""
        try:
            logger.info("Generating daily report...")
            self.daily_reporter.generate_daily_report()
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
    
    def run_daemon(self):
        """
        Run as daemon with scheduled tasks
        - Monitoring cycle every 60 minutes
        - Daily report at 10:00 AM
        """
        logger.info("Starting daemon mode...")
        logger.info("Monitoring cycle: Every 60 minutes")
        logger.info("Daily report: 10:00 AM")
        
        # Schedule tasks
        schedule.every(60).minutes.do(self.monitoring_cycle)
        schedule.every().day.at("10:00").do(self.generate_daily_report)
        
        # Run first cycle immediately
        self.monitoring_cycle()
        
        # Main loop
        logger.info("Daemon running - Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        except KeyboardInterrupt:
            logger.info("Daemon stopped by user")
            sys.exit(0)
    
    def run_manual_cycle(self):
        """Run a single monitoring cycle manually"""
        logger.info("Running manual monitoring cycle...")
        self.monitoring_cycle()
        logger.info("Manual cycle complete")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Forward Paper Trading System')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--cycle', action='store_true', help='Run single monitoring cycle')
    parser.add_argument('--report', action='store_true', help='Generate daily report')
    parser.add_argument('--init', action='store_true', help='Initialize database')
    
    args = parser.parse_args()
    
    # Initialize database if requested
    if args.init:
        from paper_trading_db import init_paper_trading_tables
        init_paper_trading_tables()
        print("✅ Database initialized")
        return
    
    # Create system
    system = PaperTradingSystem()
    
    if args.daemon:
        system.run_daemon()
    elif args.cycle:
        system.run_manual_cycle()
    elif args.report:
        system.generate_daily_report()
    else:
        # Default: run daemon
        system.run_daemon()


if __name__ == "__main__":
    main()
