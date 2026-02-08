"""
Forward Paper Trader - Live Validation System
Executes paper trades on live signals for empirical strategy validation
NO REAL MONEY - Data collection for go-live decision
"""

import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ForwardPaperTrader:
    """
    Forward paper trading system for live validation
    
    Key Features:
    - Processes live signals from signal_detector_v2.py
    - Executes simulated paper trades (NO REAL MONEY)
    - Tracks outcomes for 30-90 day validation
    - Provides empirical data for go-live decision
    """
    
    def __init__(self, starting_bankroll: float = 100.0, db_path: str = "polymarket_data.db"):
        """
        Initialize forward paper trader
        
        Args:
            starting_bankroll: Paper bankroll (default $100)
            db_path: SQLite database path
        """
        self.starting_bankroll = starting_bankroll
        self.current_bankroll = starting_bankroll
        self.db_path = db_path
        
        # Risk management settings (from config)
        self.max_position_pct = 0.10  # 10% max per position
        self.stop_loss_pct = 0.12  # 12% stop loss
        self.take_profit_1_pct = 0.20  # 20% TP1 (exit 25%)
        self.take_profit_2_pct = 0.30  # 30% TP2 (exit 50%)
        self.take_profit_3_pct = 0.50  # 50% TP3 (exit remainder)
        
        # Position limits
        self.max_total_exposure_pct = 0.30  # 30% max total exposure
        self.max_open_positions = 5
        
        logger.info("="*60)
        logger.info("📝 FORWARD PAPER TRADING SYSTEM INITIALIZED")
        logger.info("="*60)
        logger.info(f"💰 Starting Bankroll: ${starting_bankroll:.2f}")
        logger.info(f"🎯 Max Position: {self.max_position_pct*100}%")
        logger.info(f"🛡️ Stop Loss: {self.stop_loss_pct*100}%")
        logger.info(f"📊 Take Profits: {self.take_profit_1_pct*100}% / {self.take_profit_2_pct*100}% / {self.take_profit_3_pct*100}%")
        logger.info("="*60)
        logger.info("✅ PAPER TRADING MODE - NO REAL MONEY INVOLVED")
        logger.info("🎯 Purpose: Validate strategy before deploying capital")
        logger.info("⏰ Timeline: 30-90 days forward testing")
        logger.info("="*60)
    
    
    def process_signal(self, signal: Dict) -> Optional[Dict]:
        """
        Process a V2.0 signal and decide if to execute paper trade
        
        Args:
            signal: Signal dict from signal_detector_v2.py with:
                - market_id
                - title
                - side (YES/NO)
                - entry_price
                - rvr_ratio
                - roc_24h_pct
                - days_to_resolution
                - orderbook_depth
                
        Returns:
            paper_trade dict if executed, None if rejected
        """
        try:
            # Check if we can enter more positions
            current_exposure = self._get_total_exposure()
            num_open = self._get_num_open_positions()
            
            if num_open >= self.max_open_positions:
                logger.warning(f"❌ Max positions reached ({num_open}/{self.max_open_positions})")
                return None
            
            if current_exposure >= self.current_bankroll * self.max_total_exposure_pct:
                logger.warning(f"❌ Max exposure reached (${current_exposure:.2f})")
                return None
            
            # Calculate position size using Quarter Kelly (6.25% of bankroll)
            kelly_fraction = 0.25  # Quarter Kelly
            win_rate = 0.60  # Expected from backtests
            avg_win = 0.30  # +30% average win
            avg_loss = 0.12  # -12% stop loss
            
            kelly_pct = kelly_fraction * ((win_rate * avg_win) - ((1 - win_rate) * avg_loss)) / avg_win
            kelly_pct = max(0.01, min(kelly_pct, self.max_position_pct))  # Clamp to 1-10%
            
            position_size = self.current_bankroll * kelly_pct
            
            # Round to reasonable precision
            position_size = round(position_size, 2)
            
            # Build paper trade
            paper_trade = self._build_paper_trade(signal, position_size)
            
            # Execute paper entry
            success = self._execute_paper_entry(paper_trade)
            
            if success:
                logger.info(f"✅ PAPER TRADE EXECUTED: {paper_trade['side']} on {paper_trade['market_name'][:50]}")
                return paper_trade
            else:
                logger.error("❌ Failed to execute paper trade")
                return None
        
        except Exception as e:
            logger.error(f"Error processing signal: {e}")
            return None
    
    
    def _build_paper_trade(self, signal: Dict, position_size: float) -> Dict:
        """Build paper trade dict from signal"""
        
        entry_price = signal['entry_price']
        side = signal['side']
        
        # Calculate stop-loss and take-profits
        if side == "NO":
            # For NO bets, we're betting the price will go DOWN
            # Entry price is effective entry (1 - YES price)
            # Stop-loss triggers if price goes UP (we lose more than 12%)
            stop_loss = entry_price * (1 + self.stop_loss_pct)
            tp1 = entry_price * (1 - self.take_profit_1_pct)
            tp2 = entry_price * (1 - self.take_profit_2_pct)
            tp3 = entry_price * (1 - self.take_profit_3_pct)
        else:
            # For YES bets, we're betting the price will go UP
            stop_loss = entry_price * (1 - self.stop_loss_pct)
            tp1 = entry_price * (1 + self.take_profit_1_pct)
            tp2 = entry_price * (1 + self.take_profit_2_pct)
            tp3 = entry_price * (1 + self.take_profit_3_pct)
        
        paper_trade = {
            'market_id': signal['market_id'],
            'market_name': signal['title'],
            'side': side,
            'entry_price': entry_price,
            'position_size': position_size,
            'entry_time': int(time.time()),
            
            # Risk management
            'stop_loss': stop_loss,
            'take_profit_1': tp1,
            'take_profit_2': tp2,
            'take_profit_3': tp3,
            
            # Signal metadata
            'rvr_ratio': signal.get('rvr_ratio'),
            'roc_24h_pct': signal.get('roc_24h_pct'),
            'days_to_resolution': signal.get('days_to_resolution'),
            'orderbook_depth': signal.get('orderbook_depth'),
            
            # Initial status
            'status': 'OPEN',
            'exit_price': None,
            'exit_time': None,
            'exit_reason': None,
            'pnl_dollars': 0.0,
            'pnl_percent': 0.0,
            
            # Resolution tracking
            'resolved': 0,
            'resolution_outcome': None,
            'resolution_time': None,
            'trade_correct': None,
            'theoretical_edge': 0.60,  # From backtests
            'actual_edge': None
        }
        
        return paper_trade
    
    
    def _execute_paper_entry(self, paper_trade: Dict) -> bool:
        """
        Record paper trade entry in database
        Send Telegram alert
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO paper_trades (
                    market_id, market_name, side, entry_price, position_size, entry_time,
                    stop_loss, take_profit_1, take_profit_2, take_profit_3,
                    rvr_ratio, roc_24h_pct, days_to_resolution, orderbook_depth,
                    status, theoretical_edge
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper_trade['market_id'],
                paper_trade['market_name'],
                paper_trade['side'],
                paper_trade['entry_price'],
                paper_trade['position_size'],
                paper_trade['entry_time'],
                paper_trade['stop_loss'],
                paper_trade['take_profit_1'],
                paper_trade['take_profit_2'],
                paper_trade['take_profit_3'],
                paper_trade['rvr_ratio'],
                paper_trade['roc_24h_pct'],
                paper_trade['days_to_resolution'],
                paper_trade['orderbook_depth'],
                paper_trade['status'],
                paper_trade['theoretical_edge']
            ))
            
            trade_id = cursor.lastrowid
            paper_trade['id'] = trade_id
            
            conn.commit()
            conn.close()
            
            # Send Telegram alert
            self._send_entry_alert(paper_trade)
            
            logger.info(f"📝 Paper trade #{trade_id} recorded in database")
            return True
            
        except Exception as e:
            logger.error(f"Error executing paper entry: {e}")
            return False
    
    
    def _send_entry_alert(self, trade: Dict):
        """Send Telegram alert for paper trade entry"""
        try:
            # Get current portfolio status
            status = self.get_portfolio_status()
            
            # Format alert message
            message = f"""
📝 PAPER TRADE ENTRY (TEST - NO REAL MONEY)

🎯 Signal: BET {trade['side']}
📊 Market: {trade['market_name'][:60]}
💰 Position: ${trade['position_size']:.2f} ({trade['position_size']/self.current_bankroll*100:.1f}% of bankroll)
📈 Entry: {trade['side']} @ {trade['entry_price']*100:.1f}%

🔬 Signal Strength:
   RVR: {trade.get('rvr_ratio', 0):.1f}x (volume spike)
   ROC: {trade.get('roc_24h_pct', 0):+.1f}% (24h momentum)
   Days to close: {trade.get('days_to_resolution', 0)}d
   Order book: ${trade.get('orderbook_depth', 0)/1000:.1f}K

🛡️ Risk Management:
   Stop-Loss: {trade['stop_loss']*100:.1f}%
   TP1 (25%): {trade['take_profit_1']*100:.1f}% → ${trade['position_size']*0.25*0.20:.2f} (+20%)
   TP2 (50%): {trade['take_profit_2']*100:.1f}% → ${trade['position_size']*0.50*0.30:.2f} (+30%)
   TP3 (100%): {trade['take_profit_3']*100:.1f}% → ${trade['position_size']*0.50:.2f} (+50%)

💼 Paper Portfolio:
   Bankroll: ${status['current_bankroll']:.2f}
   Open Positions: {status['num_open']}
   Total Exposure: ${status['total_exposure']:.2f} ({status['exposure_pct']:.1f}%)

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ PAPER TRADE - Validating strategy before real money!
Tracking outcome for forward validation.
""".strip()
            
            # Send via telegram_alerter
            self._send_telegram(message)
            
        except Exception as e:
            logger.error(f"Error sending entry alert: {e}")
    
    
    def _send_telegram(self, message: str):
        """Send message via Telegram (uses existing telegram_alerter.py)"""
        try:
            from telegram_alerter import send_alert
            send_alert(message)
        except Exception as e:
            logger.warning(f"Telegram alert failed (non-critical): {e}")
    
    
    def get_portfolio_status(self) -> Dict:
        """Get current paper trading portfolio status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get open positions
            cursor.execute("SELECT COUNT(*), SUM(position_size) FROM paper_trades WHERE status = 'OPEN'")
            row = cursor.fetchone()
            num_open = row[0] or 0
            total_exposure = row[1] or 0.0
            
            # Get total P&L
            cursor.execute("SELECT SUM(pnl_dollars) FROM paper_trades WHERE status != 'OPEN'")
            total_pnl = cursor.fetchone()[0] or 0.0
            
            # Update current bankroll
            self.current_bankroll = self.starting_bankroll + total_pnl
            
            # Get resolved stats
            cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE status != 'OPEN'")
            num_resolved = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE trade_correct = 1")
            num_wins = cursor.fetchone()[0] or 0
            
            win_rate = (num_wins / num_resolved * 100) if num_resolved > 0 else 0
            
            conn.close()
            
            return {
                'starting_bankroll': self.starting_bankroll,
                'current_bankroll': self.current_bankroll,
                'total_pnl': total_pnl,
                'total_pnl_pct': (total_pnl / self.starting_bankroll * 100) if self.starting_bankroll > 0 else 0,
                'num_open': num_open,
                'total_exposure': total_exposure,
                'exposure_pct': (total_exposure / self.current_bankroll * 100) if self.current_bankroll > 0 else 0,
                'num_resolved': num_resolved,
                'num_wins': num_wins,
                'win_rate': win_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio status: {e}")
            return {
                'starting_bankroll': self.starting_bankroll,
                'current_bankroll': self.starting_bankroll,
                'total_pnl': 0.0,
                'total_pnl_pct': 0.0,
                'num_open': 0,
                'total_exposure': 0.0,
                'exposure_pct': 0.0,
                'num_resolved': 0,
                'num_wins': 0,
                'win_rate': 0.0
            }
    
    
    def _get_total_exposure(self) -> float:
        """Get total dollar exposure of open positions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT SUM(position_size) FROM paper_trades WHERE status = 'OPEN'")
            total = cursor.fetchone()[0] or 0.0
            
            conn.close()
            return total
            
        except Exception as e:
            logger.error(f"Error getting total exposure: {e}")
            return 0.0
    
    
    def _get_num_open_positions(self) -> int:
        """Get number of open positions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE status = 'OPEN'")
            count = cursor.fetchone()[0] or 0
            
            conn.close()
            return count
            
        except Exception as e:
            logger.error(f"Error getting open positions: {e}")
            return 0


def main():
    """Test the forward paper trader"""
    print("\n" + "="*60)
    print("🧪 FORWARD PAPER TRADER - TEST MODE")
    print("="*60)
    
    # Initialize trader
    trader = ForwardPaperTrader(starting_bankroll=100.0)
    
    # Create fake signal for testing
    fake_signal = {
        'market_id': 'test_market_123',
        'title': 'Test Market: Will Bitcoin hit $100k by March?',
        'side': 'NO',
        'entry_price': 0.12,  # 12% probability (NO bet = 88% effective)
        'rvr_ratio': 3.2,
        'roc_24h_pct': 18.5,
        'days_to_resolution': 2,
        'orderbook_depth': 14200
    }
    
    print("\n📊 Testing signal processing...")
    print(f"Signal: BET {fake_signal['side']} on {fake_signal['title']}")
    
    # Process signal
    paper_trade = trader.process_signal(fake_signal)
    
    if paper_trade:
        print("\n✅ Paper trade executed successfully!")
        print(f"Trade ID: #{paper_trade['id']}")
        print(f"Position Size: ${paper_trade['position_size']:.2f}")
        print(f"Entry: {paper_trade['entry_price']*100:.1f}%")
        print(f"Stop Loss: {paper_trade['stop_loss']*100:.1f}%")
    else:
        print("\n❌ Paper trade rejected")
    
    # Print portfolio status
    print("\n" + "="*60)
    print("💼 PORTFOLIO STATUS")
    print("="*60)
    
    status = trader.get_portfolio_status()
    print(f"Bankroll: ${status['current_bankroll']:.2f}")
    print(f"Open Positions: {status['num_open']}")
    print(f"Exposure: ${status['total_exposure']:.2f} ({status['exposure_pct']:.1f}%)")
    print(f"Total P&L: ${status['total_pnl']:+.2f} ({status['total_pnl_pct']:+.1f}%)")
    print(f"Resolved Trades: {status['num_resolved']}")
    print(f"Win Rate: {status['win_rate']:.1f}%")
    
    print("\n" + "="*60)
    print("✅ Test complete!")
    print("="*60)


if __name__ == "__main__":
    main()
