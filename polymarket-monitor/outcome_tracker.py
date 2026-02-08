"""
Outcome Tracker
Monitors market resolutions and validates trade outcomes
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


class OutcomeTracker:
    """Tracks market resolutions and validates trades"""
    
    def __init__(self):
        """Initialize outcome tracker"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def check_resolutions(self):
        """Check for resolved markets and update trades"""
        logger.info("Checking for market resolutions...")
        
        # Get all markets with paper trades that aren't resolved yet
        markets = self._get_unresolved_markets()
        
        if not markets:
            logger.info("No unresolved markets to check")
            return
        
        logger.info(f"Checking {len(markets)} markets for resolutions")
        
        for market_id, market_name in markets:
            try:
                self._check_market_resolution(market_id, market_name)
            except Exception as e:
                logger.error(f"Error checking resolution for {market_id}: {e}")
    
    def _get_unresolved_markets(self) -> List[tuple]:
        """Get markets with unresolved paper trades"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT market_id, market_name
            FROM paper_trades
            WHERE resolved = 0
        """)
        
        markets = cursor.fetchall()
        conn.close()
        
        return markets
    
    def _check_market_resolution(self, market_id: str, market_name: str):
        """Check if a market has resolved"""
        try:
            url = f"{GAMMA_API}/markets/{market_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.debug(f"Market {market_id} not found or error")
                return
            
            data = response.json()
            
            # Check if market is closed/resolved
            closed = data.get('closed', False)
            
            if not closed:
                logger.debug(f"Market {market_id} not yet resolved")
                return
            
            # Get resolution outcome
            outcomes = data.get('outcomes', [])
            if not outcomes:
                logger.warning(f"Market {market_id} closed but no outcomes")
                return
            
            # Determine which side won (YES or NO)
            # In Polymarket, resolved markets have one outcome at price ~1.0 (winner) and others at ~0.0
            winning_outcome = None
            for outcome in outcomes:
                price = float(outcome.get('price', 0))
                if price > 0.9:  # Winner has price ~1.0
                    winning_outcome = outcome.get('outcome', 'YES')
                    break
            
            if not winning_outcome:
                # Check prices array if available
                try:
                    if outcomes[0].get('price', 0) > 0.5:
                        winning_outcome = 'YES'
                    else:
                        winning_outcome = 'NO'
                except:
                    logger.warning(f"Could not determine winner for {market_id}")
                    return
            
            logger.info(f"Market {market_id} resolved: {winning_outcome} won")
            
            # Record resolution
            self._record_resolution(market_id, market_name, winning_outcome, data)
            
        except Exception as e:
            logger.error(f"Error checking resolution for {market_id}: {e}")
    
    def _record_resolution(self, market_id: str, market_name: str, 
                           outcome: str, market_data: dict):
        """Record market resolution and update trades"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Insert/update resolution record
        cursor.execute("""
            INSERT OR REPLACE INTO market_resolutions 
            (market_id, market_name, resolution_time, resolution_outcome, 
             final_yes_price, total_volume)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            market_id,
            market_name,
            int(time.time()),
            outcome,
            float(market_data.get('outcomes', [{}])[0].get('price', 0)),
            float(market_data.get('volume', 0))
        ))
        
        # Get all trades for this market
        cursor.execute("""
            SELECT id, side, position_size, pnl_dollars, status
            FROM paper_trades
            WHERE market_id = ? AND resolved = 0
        """, (market_id,))
        
        trades = cursor.fetchall()
        
        for trade_id, side, position_size, pnl_dollars, status in trades:
            # Determine if trade was correct
            trade_correct = self._is_trade_correct(side, outcome)
            
            # If trade is still open, calculate theoretical P&L
            if status == 'OPEN':
                if trade_correct:
                    # Won - would have gotten full payout
                    theoretical_pnl = position_size * 0.5  # ~50% gain on average
                    theoretical_pnl_pct = 50.0
                else:
                    # Lost - would have lost position
                    theoretical_pnl = -position_size
                    theoretical_pnl_pct = -100.0
                
                # Update trade with theoretical outcome
                cursor.execute("""
                    UPDATE paper_trades
                    SET resolved = 1,
                        resolution_outcome = ?,
                        resolution_time = ?,
                        trade_correct = ?,
                        status = 'RESOLVED',
                        pnl_dollars = ?,
                        pnl_percent = ?
                    WHERE id = ?
                """, (
                    outcome,
                    int(time.time()),
                    1 if trade_correct else 0,
                    theoretical_pnl,
                    theoretical_pnl_pct,
                    trade_id
                ))
            else:
                # Trade already closed, just mark resolution
                cursor.execute("""
                    UPDATE paper_trades
                    SET resolved = 1,
                        resolution_outcome = ?,
                        resolution_time = ?,
                        trade_correct = ?
                    WHERE id = ?
                """, (
                    outcome,
                    int(time.time()),
                    1 if trade_correct else 0,
                    trade_id
                ))
            
            # Send outcome alert
            self._send_outcome_alert(trade_id, market_name, side, outcome, trade_correct)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Recorded resolution for {market_id}: {len(trades)} trades updated")
    
    def _is_trade_correct(self, bet_side: str, outcome: str) -> bool:
        """Determine if a trade was correct"""
        # BET YES + outcome YES = WIN
        # BET YES + outcome NO = LOSS
        # BET NO + outcome YES = LOSS
        # BET NO + outcome NO = WIN
        return bet_side == outcome
    
    def _send_outcome_alert(self, trade_id: int, market_name: str, 
                            bet_side: str, outcome: str, was_correct: bool):
        """Send Telegram alert for market resolution"""
        try:
            from telegram_alerter import send_alert
            
            # Get trade details
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT entry_price, exit_price, pnl_dollars, pnl_percent, 
                       entry_time, exit_time, status
                FROM paper_trades
                WHERE id = ?
            """, (trade_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return
            
            entry_price, exit_price, pnl_dollars, pnl_pct, entry_time, exit_time, status = row
            
            # Calculate duration
            if exit_time:
                duration = exit_time - entry_time
            else:
                duration = int(time.time()) - entry_time
            
            if duration < 86400:
                duration_str = f"{duration // 3600} hours"
            else:
                duration_str = f"{duration // 86400} days"
            
            result_emoji = "✅" if was_correct else "❌"
            
            message = f"""
🏁 MARKET RESOLVED

📊 Market: {market_name[:60]}
🎯 Our Bet: {bet_side} @ {entry_price*100:.1f}%
{result_emoji} Actual Outcome: {outcome}

💰 Trade Result:
   {"CORRECT" if was_correct else "INCORRECT"} Prediction
   {"Won" if pnl_dollars > 0 else "Lost"}: ${pnl_dollars:+.2f} ({pnl_pct:+.1f}%)
   Duration: {duration_str}
   Status: {status}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""".strip()
            
            send_alert(message)
            
        except Exception as e:
            logger.error(f"Error sending outcome alert: {e}")


def main():
    """Test outcome tracker"""
    logging.basicConfig(level=logging.INFO)
    
    tracker = OutcomeTracker()
    tracker.check_resolutions()


if __name__ == "__main__":
    main()
