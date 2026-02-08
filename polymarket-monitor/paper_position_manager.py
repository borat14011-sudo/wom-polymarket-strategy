"""
Paper Position Manager
Monitors open positions and executes stop-loss/take-profit exits
"""

import sqlite3
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

DB_PATH = "polymarket_data.db"
GAMMA_API = "https://gamma-api.polymarket.com"


class PaperPositionManager:
    """Manages open paper trading positions"""
    
    def __init__(self):
        """Initialize position manager"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def monitor_open_positions(self):
        """Check all open positions and execute exits if needed"""
        logger.info("Monitoring open paper positions...")
        
        open_positions = self._get_open_positions()
        
        if not open_positions:
            logger.info("No open positions to monitor")
            return
        
        logger.info(f"Found {len(open_positions)} open positions")
        
        for position in open_positions:
            try:
                self._monitor_position(position)
            except Exception as e:
                logger.error(f"Error monitoring position #{position['id']}: {e}")
    
    def _get_open_positions(self) -> List[Dict]:
        """Get all open paper positions"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, market_id, market_name, side, entry_price, position_size, 
                   entry_time, stop_loss, take_profit_1, take_profit_2, take_profit_3
            FROM paper_trades
            WHERE status = 'OPEN'
            ORDER BY entry_time DESC
        """)
        
        positions = []
        for row in cursor.fetchall():
            positions.append({
                'id': row[0],
                'market_id': row[1],
                'market_name': row[2],
                'side': row[3],
                'entry_price': row[4],
                'position_size': row[5],
                'entry_time': row[6],
                'stop_loss': row[7],
                'take_profit_1': row[8],
                'take_profit_2': row[9],
                'take_profit_3': row[10]
            })
        
        conn.close()
        return positions
    
    def _monitor_position(self, position: Dict):
        """Monitor a single position and execute exits if needed"""
        # Get current market price
        current_price = self._get_current_price(position['market_id'])
        
        if current_price is None:
            logger.warning(f"Could not fetch price for market {position['market_id']}")
            return
        
        # Log tick
        self._log_price_tick(position, current_price)
        
        # Check exit conditions
        should_exit, exit_reason = self._check_exit_conditions(position, current_price)
        
        if should_exit:
            self._execute_exit(position, current_price, exit_reason)
    
    def _get_current_price(self, market_id: str) -> Optional[float]:
        """Fetch current market price from Polymarket API"""
        try:
            # Try to get market data
            url = f"{GAMMA_API}/markets/{market_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Polymarket returns outcomes array, we want the first outcome's price
                if 'outcomes' in data and len(data['outcomes']) > 0:
                    return float(data['outcomes'][0].get('price', 0))
            
            # Fallback: try CLOB API
            url = f"https://clob.polymarket.com/prices-history"
            params = {'market': market_id, 'interval': '1m', 'limit': 1}
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return float(data[0].get('p', 0))
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price for {market_id}: {e}")
            return None
    
    def _log_price_tick(self, position: Dict, current_price: float):
        """Log current price tick for position"""
        try:
            # Calculate unrealized P&L
            entry_price = position['entry_price']
            side = position['side']
            position_size = position['position_size']
            
            if side == "NO":
                # NO bet profits when price goes DOWN
                pnl_pct = (entry_price - current_price) / entry_price
            else:
                # YES bet profits when price goes UP
                pnl_pct = (current_price - entry_price) / entry_price
            
            pnl_dollars = position_size * pnl_pct
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO paper_position_ticks 
                (trade_id, timestamp, current_price, pnl_unrealized, pnl_pct)
                VALUES (?, ?, ?, ?, ?)
            """, (
                position['id'],
                int(time.time()),
                current_price,
                pnl_dollars,
                pnl_pct
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging tick: {e}")
    
    def _check_exit_conditions(self, position: Dict, current_price: float) -> tuple:
        """
        Check if position should exit
        Returns: (should_exit: bool, exit_reason: str)
        """
        side = position['side']
        
        if side == "NO":
            # NO bet: We WIN if price goes DOWN, LOSE if price goes UP
            # Stop loss triggers if price goes UP above threshold
            if current_price >= position['stop_loss']:
                return True, "STOP_LOSS"
            
            # Take profits trigger if price goes DOWN below thresholds
            if position['take_profit_1'] and current_price <= position['take_profit_1']:
                return True, "TAKE_PROFIT_1"
            if position['take_profit_2'] and current_price <= position['take_profit_2']:
                return True, "TAKE_PROFIT_2"
            if position['take_profit_3'] and current_price <= position['take_profit_3']:
                return True, "TAKE_PROFIT_3"
        
        else:  # YES
            # YES bet: We WIN if price goes UP, LOSE if price goes DOWN
            if current_price <= position['stop_loss']:
                return True, "STOP_LOSS"
            
            if position['take_profit_1'] and current_price >= position['take_profit_1']:
                return True, "TAKE_PROFIT_1"
            if position['take_profit_2'] and current_price >= position['take_profit_2']:
                return True, "TAKE_PROFIT_2"
            if position['take_profit_3'] and current_price >= position['take_profit_3']:
                return True, "TAKE_PROFIT_3"
        
        return False, None
    
    def _execute_exit(self, position: Dict, exit_price: float, exit_reason: str):
        """Execute paper position exit"""
        logger.info(f"Executing exit for position #{position['id']}: {exit_reason}")
        
        # Calculate P&L
        entry_price = position['entry_price']
        side = position['side']
        position_size = position['position_size']
        
        if side == "NO":
            pnl_pct = (entry_price - exit_price) / entry_price
        else:
            pnl_pct = (exit_price - entry_price) / entry_price
        
        pnl_dollars = position_size * pnl_pct
        
        # Update database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE paper_trades
            SET status = 'CLOSED',
                exit_price = ?,
                exit_time = ?,
                exit_reason = ?,
                pnl_dollars = ?,
                pnl_percent = ?
            WHERE id = ?
        """, (
            exit_price,
            int(time.time()),
            exit_reason,
            pnl_dollars,
            pnl_pct * 100,
            position['id']
        ))
        
        conn.commit()
        conn.close()
        
        # Send Telegram alert
        self._send_exit_alert(position, exit_price, exit_reason, pnl_dollars, pnl_pct)
        
        logger.info(f"Position #{position['id']} closed: ${pnl_dollars:+.2f} ({pnl_pct*100:+.1f}%)")
    
    def _send_exit_alert(self, position: Dict, exit_price: float, exit_reason: str, 
                         pnl_dollars: float, pnl_pct: float):
        """Send Telegram alert for position exit"""
        try:
            from telegram_alerter import send_alert
            
            # Calculate hold time
            hold_seconds = int(time.time()) - position['entry_time']
            hold_hours = hold_seconds / 3600
            
            if hold_hours < 1:
                hold_str = f"{int(hold_seconds / 60)} minutes"
            elif hold_hours < 24:
                hold_str = f"{hold_hours:.1f} hours"
            else:
                hold_str = f"{hold_hours / 24:.1f} days"
            
            # Format P&L
            pnl_emoji = "✅" if pnl_dollars > 0 else "❌"
            
            message = f"""
🎯 PAPER TRADE EXIT

📊 Market: {position['market_name'][:60]}
🎯 Side: BET {position['side']}
{pnl_emoji} Outcome: {exit_reason.replace('_', ' ')}

💰 Entry: {position['side']} @ {position['entry_price']*100:.1f}%
📉 Exit: {position['side']} @ {exit_price*100:.1f}%
⏱️ Hold Time: {hold_str}

💵 P&L:
   Position: ${position['position_size']:.2f}
   {"Profit" if pnl_dollars > 0 else "Loss"}: ${pnl_dollars:+.2f} ({pnl_pct*100:+.1f}%)

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""".strip()
            
            send_alert(message)
            
        except Exception as e:
            logger.error(f"Error sending exit alert: {e}")


def main():
    """Test position manager"""
    logging.basicConfig(level=logging.INFO)
    
    manager = PaperPositionManager()
    manager.monitor_open_positions()


if __name__ == "__main__":
    main()
