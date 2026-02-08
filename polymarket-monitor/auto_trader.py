"""
Polymarket Auto-Trader
Combines monitoring + signal evaluation + trade execution
"""

import sqlite3
import time
import os
import subprocess
from datetime import datetime
from typing import List, Dict
import logging

from trading_executor import TradingExecutor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoTrader:
    """Automated trading system that monitors signals and executes trades"""
    
    def __init__(self, wallet_key: str, bankroll: float = 100.0):
        """
        Initialize auto-trader
        
        Args:
            wallet_key: Wallet private key (encrypted)
            bankroll: Starting capital in USDC
        """
        self.executor = TradingExecutor(wallet_key, bankroll)
        self.db_path = "polymarket_data.db"
        self.processed_signals = set()
        
        logger.info("="*60)
        logger.info("🤖 POLYMARKET AUTO-TRADER INITIALIZED")
        logger.info("="*60)
        logger.info(f"💰 Starting Bankroll: ${bankroll}")
        logger.info(f"📊 Risk Parameters:")
        logger.info(f"   Max Position: {self.executor.max_position_pct*100}%")
        logger.info(f"   Max Exposure: {self.executor.max_exposure_pct*100}%")
        logger.info(f"   Stop Loss: {self.executor.stop_loss_pct*100}%")
        logger.info(f"   Circuit Breaker: {self.executor.circuit_breaker_pct*100}%")
        logger.info("="*60)
    
    
    def get_new_signals(self) -> List[Dict]:
        """Fetch new unprocessed signals from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get signals that haven't been processed yet
            cursor.execute("""
                SELECT * FROM signals 
                WHERE alerted = 1 
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            
            signals = []
            for row in cursor.fetchall():
                signal_id = f"{row['market_id']}_{row['timestamp']}"
                
                # Skip if already processed
                if signal_id in self.processed_signals:
                    continue
                
                signals.append({
                    'signal_id': signal_id,
                    'market_id': row['market_id'],
                    'market_name': row['market_name'],
                    'rvr': row['rvr'],
                    'roc': row['roc'],
                    'price': row['price'],
                    'volume': row['volume'],
                    'timestamp': row['timestamp']
                })
            
            conn.close()
            return signals
            
        except Exception as e:
            logger.error(f"Error fetching signals: {e}")
            return []
    
    
    def send_telegram_alert(self, message: str):
        """Send alert via Telegram using OpenClaw message tool"""
        try:
            # Use OpenClaw CLI to send message
            cmd = [
                'openclaw', 'message', 'send',
                '--channel', 'telegram',
                '--to', '@MoneyManAmex',
                '--message', message
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Telegram alert sent successfully")
            else:
                logger.error(f"❌ Failed to send Telegram alert: {result.stderr}")
        
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
    
    
    def process_signal(self, signal: Dict):
        """Process a trading signal - evaluate and execute if criteria met"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🔔 NEW SIGNAL RECEIVED")
        logger.info(f"{'='*60}")
        
        # Evaluate signal
        trade = self.executor.evaluate_signal(signal)
        
        if trade is None:
            logger.info("❌ Signal rejected - criteria not met")
            return
        
        # Execute trade
        success = self.executor.execute_trade(trade)
        
        if success:
            # Send Telegram alert
            alert_message = self.executor.send_telegram_alert(trade)
            self.send_telegram_alert(alert_message)
            
            # Mark signal as processed
            self.processed_signals.add(signal['signal_id'])
            
            logger.info(f"✅ Trade completed and alert sent!")
        else:
            logger.error(f"❌ Trade execution failed!")
    
    
    def send_daily_report(self):
        """Send daily P&L report"""
        status = self.executor.get_portfolio_status()
        
        message = f"""
📊 DAILY TRADING REPORT

💰 Portfolio Summary:
   Starting: ${status['initial_bankroll']:.2f}
   Current: ${status['bankroll']:.2f}
   P&L: ${status['total_pnl']:+.2f} ({status['total_pnl_pct']:+.1f}%)

📈 Positions:
   Active: {status['num_positions']}
   Exposure: ${status['total_exposure']:.2f} ({status['exposure_pct']:.1f}%)

🛡️ Risk Status:
   Circuit Breaker: {'🚨 ACTIVE' if status['circuit_breaker_active'] else '✅ OK'}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""".strip()
        
        self.send_telegram_alert(message)
        logger.info("📊 Daily report sent")
    
    
    def run(self, check_interval: int = 60):
        """
        Run the auto-trader continuously
        
        Args:
            check_interval: Seconds between signal checks
        """
        logger.info(f"\n🚀 Auto-trader started! Checking for signals every {check_interval}s")
        logger.info(f"Press Ctrl+C to stop\n")
        
        last_daily_report = datetime.now().date()
        
        try:
            while True:
                # Check for new signals
                signals = self.get_new_signals()
                
                if signals:
                    logger.info(f"📥 Found {len(signals)} new signal(s)")
                    for signal in signals:
                        self.process_signal(signal)
                
                # Send daily report if new day
                current_date = datetime.now().date()
                if current_date > last_daily_report:
                    self.send_daily_report()
                    last_daily_report = current_date
                
                # Wait before next check
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            logger.info("\n⛔ Auto-trader stopped by user")
            self.send_final_report()
        
        except Exception as e:
            logger.error(f"❌ Auto-trader crashed: {e}")
            self.send_telegram_alert(f"🚨 AUTO-TRADER CRASHED: {e}")
    
    
    def send_final_report(self):
        """Send final report when trader stops"""
        status = self.executor.get_portfolio_status()
        
        message = f"""
⛔ AUTO-TRADER STOPPED

💰 Final Portfolio:
   Starting: ${status['initial_bankroll']:.2f}
   Final: ${status['bankroll']:.2f}
   Total P&L: ${status['total_pnl']:+.2f} ({status['total_pnl_pct']:+.1f}%)

📈 Open Positions: {status['num_positions']}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""".strip()
        
        self.send_telegram_alert(message)


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python auto_trader.py <wallet_private_key> [bankroll]")
        print("Example: python auto_trader.py YOUR_KEY_HERE 100.0")
        sys.exit(1)
    
    wallet_key = sys.argv[1]
    bankroll = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0
    
    # Initialize and run auto-trader
    trader = AutoTrader(wallet_key, bankroll)
    trader.run(check_interval=60)


if __name__ == "__main__":
    main()
