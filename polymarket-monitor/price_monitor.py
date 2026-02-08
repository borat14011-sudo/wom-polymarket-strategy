"""
Real-Time Price Monitor for Polymarket Positions
Monitors all open positions and triggers alerts for stop-loss/take-profit conditions

Features:
- Monitors prices for all open positions via CLOB API
- WebSocket support for real-time price updates (fallback to polling)
- Stop-loss triggers (12% loss)
- Take-profit targets (20%, 30%, 50%)
- SQLite price history tracking
- Configurable alerts via Telegram
- 24/7 background operation with auto-reconnection
- Production-ready error handling
"""

import sqlite3
import time
import requests
import logging
import json
import sys
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import threading
import signal

# WebSocket support (optional dependency)
try:
    import websocket
    WS_AVAILABLE = True
except ImportError:
    WS_AVAILABLE = False
    print("⚠️  websocket-client not installed. Install with: pip install websocket-client")
    print("⚠️  Falling back to polling mode only")

# Configuration
DB_PATH = "polymarket_data.db"
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
WS_API = "wss://ws-subscriptions-clob.polymarket.com/ws"

# Monitoring settings
POLL_INTERVAL = 60  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
HEARTBEAT_INTERVAL = 300  # 5 minutes
WS_RECONNECT_DELAY = 10  # seconds

# Risk thresholds
STOP_LOSS_PCT = 0.12  # 12% loss
TAKE_PROFIT_1_PCT = 0.20  # 20% profit
TAKE_PROFIT_2_PCT = 0.30  # 30% profit
TAKE_PROFIT_3_PCT = 0.50  # 50% profit

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('price_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Represents an open trading position"""
    id: int
    market_id: str
    market_name: str
    side: str  # YES or NO
    entry_price: float
    position_size: float
    entry_time: int
    stop_loss: float
    take_profit_1: Optional[float]
    take_profit_2: Optional[float]
    take_profit_3: Optional[float]


class PriceMonitor:
    """Main price monitoring system with WebSocket and polling support"""
    
    def __init__(self, use_websocket=True):
        """Initialize price monitor"""
        self.use_websocket = use_websocket and WS_AVAILABLE
        self.running = False
        self.positions: Dict[str, Position] = {}
        self.ws = None
        self.ws_thread = None
        self.last_heartbeat = time.time()
        
        # HTTP session for REST API calls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        logger.info("Price Monitor initialized")
        logger.info(f"WebSocket mode: {'ENABLED' if self.use_websocket else 'DISABLED (polling only)'}")
    
    def start(self):
        """Start the price monitoring system"""
        logger.info("=" * 80)
        logger.info("🚀 Starting Real-Time Price Monitor")
        logger.info("=" * 80)
        
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Load initial positions
        self._refresh_positions()
        
        if self.use_websocket and self.positions:
            # Start WebSocket connection in separate thread
            logger.info("Starting WebSocket connection...")
            self.ws_thread = threading.Thread(target=self._websocket_loop, daemon=True)
            self.ws_thread.start()
        
        # Main monitoring loop (handles polling and health checks)
        try:
            self._monitoring_loop()
        except Exception as e:
            logger.error(f"Fatal error in monitoring loop: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Stop the monitoring system gracefully"""
        logger.info("Stopping price monitor...")
        self.running = False
        
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        
        logger.info("Price monitor stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def _refresh_positions(self):
        """Load all open positions from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, market_id, market_name, side, entry_price, position_size, 
                       entry_time, stop_loss, take_profit_1, take_profit_2, take_profit_3
                FROM paper_trades
                WHERE status = 'OPEN'
                ORDER BY entry_time DESC
            """)
            
            positions = {}
            for row in cursor.fetchall():
                pos = Position(
                    id=row[0],
                    market_id=row[1],
                    market_name=row[2],
                    side=row[3],
                    entry_price=row[4],
                    position_size=row[5],
                    entry_time=row[6],
                    stop_loss=row[7],
                    take_profit_1=row[8],
                    take_profit_2=row[9],
                    take_profit_3=row[10]
                )
                positions[pos.market_id] = pos
            
            conn.close()
            
            self.positions = positions
            logger.info(f"Loaded {len(self.positions)} open positions")
            
            if self.positions:
                for pos in self.positions.values():
                    logger.info(f"  → {pos.side} {pos.market_name[:50]} @ {pos.entry_price*100:.1f}%")
            
        except Exception as e:
            logger.error(f"Error loading positions: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting monitoring loop...")
        
        while self.running:
            try:
                # Refresh positions periodically
                self._refresh_positions()
                
                if not self.positions:
                    logger.info("No open positions to monitor")
                    time.sleep(POLL_INTERVAL)
                    continue
                
                # If WebSocket is not active, use polling
                if not self.use_websocket or not self._is_websocket_healthy():
                    logger.info("Polling mode: Fetching prices for all positions...")
                    self._poll_all_positions()
                
                # Health check and heartbeat
                if time.time() - self.last_heartbeat > HEARTBEAT_INTERVAL:
                    self._heartbeat()
                    self.last_heartbeat = time.time()
                
                # Sleep until next check
                time.sleep(POLL_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(RETRY_DELAY)
    
    def _poll_all_positions(self):
        """Poll prices for all open positions via REST API"""
        for market_id, position in self.positions.items():
            try:
                current_price = self._fetch_price_rest(market_id)
                
                if current_price is not None:
                    self._process_price_update(position, current_price)
                else:
                    logger.warning(f"Failed to fetch price for {market_id}")
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error polling {market_id}: {e}")
    
    def _fetch_price_rest(self, market_id: str, retry_count=0) -> Optional[float]:
        """Fetch current price via REST API"""
        try:
            # Try CLOB API first (more reliable for real-time prices)
            url = f"{CLOB_API}/prices-history"
            params = {
                'market': market_id,
                'interval': '1m',
                'limit': 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Get the latest price for the first outcome (YES side)
                    price = float(data[0].get('p', 0))
                    return price
            
            # Fallback to Gamma API
            url = f"{GAMMA_API}/markets/{market_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'outcomePrices' in data and len(data['outcomePrices']) > 0:
                    return float(data['outcomePrices'][0])
            
            # Retry logic
            if retry_count < MAX_RETRIES:
                logger.warning(f"Retry {retry_count + 1}/{MAX_RETRIES} for {market_id}")
                time.sleep(RETRY_DELAY)
                return self._fetch_price_rest(market_id, retry_count + 1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price for {market_id}: {e}")
            
            if retry_count < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                return self._fetch_price_rest(market_id, retry_count + 1)
            
            return None
    
    def _process_price_update(self, position: Position, current_price: float):
        """Process a price update and check exit conditions"""
        try:
            # Calculate P&L
            if position.side == "NO":
                # NO bet profits when price goes DOWN
                pnl_pct = (position.entry_price - current_price) / position.entry_price
            else:
                # YES bet profits when price goes UP
                pnl_pct = (current_price - position.entry_price) / position.entry_price
            
            pnl_dollars = position.position_size * pnl_pct
            
            # Log price tick to database
            self._log_price_tick(position, current_price, pnl_dollars, pnl_pct)
            
            # Check exit conditions
            should_exit, exit_reason = self._check_exit_conditions(position, current_price)
            
            if should_exit:
                logger.warning(f"🚨 EXIT SIGNAL: {exit_reason} for {position.market_name[:50]}")
                self._send_exit_alert(position, current_price, exit_reason, pnl_dollars, pnl_pct)
                # Note: Actual exit execution would happen in a separate system
                # This monitor only alerts and logs
            else:
                # Regular status log (reduced verbosity)
                logger.debug(
                    f"Position #{position.id}: {current_price*100:.1f}% "
                    f"P&L: ${pnl_dollars:+.2f} ({pnl_pct*100:+.1f}%)"
                )
            
        except Exception as e:
            logger.error(f"Error processing price update: {e}")
    
    def _check_exit_conditions(self, position: Position, current_price: float) -> tuple:
        """
        Check if position should exit
        Returns: (should_exit: bool, exit_reason: str)
        """
        side = position.side
        
        if side == "NO":
            # NO bet: We WIN if price goes DOWN, LOSE if price goes UP
            # Stop loss triggers if price goes UP above threshold
            if current_price >= position.stop_loss:
                return True, "STOP_LOSS"
            
            # Take profits trigger if price goes DOWN below thresholds
            if position.take_profit_3 and current_price <= position.take_profit_3:
                return True, "TAKE_PROFIT_3_50%"
            if position.take_profit_2 and current_price <= position.take_profit_2:
                return True, "TAKE_PROFIT_2_30%"
            if position.take_profit_1 and current_price <= position.take_profit_1:
                return True, "TAKE_PROFIT_1_20%"
        
        else:  # YES
            # YES bet: We WIN if price goes UP, LOSE if price goes DOWN
            if current_price <= position.stop_loss:
                return True, "STOP_LOSS"
            
            if position.take_profit_3 and current_price >= position.take_profit_3:
                return True, "TAKE_PROFIT_3_50%"
            if position.take_profit_2 and current_price >= position.take_profit_2:
                return True, "TAKE_PROFIT_2_30%"
            if position.take_profit_1 and current_price >= position.take_profit_1:
                return True, "TAKE_PROFIT_1_20%"
        
        return False, None
    
    def _log_price_tick(self, position: Position, current_price: float, 
                        pnl_dollars: float, pnl_pct: float):
        """Log price tick to database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO paper_position_ticks 
                (trade_id, timestamp, current_price, pnl_unrealized, pnl_pct)
                VALUES (?, ?, ?, ?, ?)
            """, (
                position.id,
                int(time.time()),
                current_price,
                pnl_dollars,
                pnl_pct
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging price tick: {e}")
    
    def _send_exit_alert(self, position: Position, exit_price: float, 
                         exit_reason: str, pnl_dollars: float, pnl_pct: float):
        """Send Telegram alert for exit condition"""
        try:
            # Calculate hold time
            hold_seconds = int(time.time()) - position.entry_time
            hold_hours = hold_seconds / 3600
            
            if hold_hours < 1:
                hold_str = f"{int(hold_seconds / 60)} minutes"
            elif hold_hours < 24:
                hold_str = f"{hold_hours:.1f} hours"
            else:
                hold_str = f"{hold_hours / 24:.1f} days"
            
            # Format alert
            alert_emoji = "🛑" if "STOP_LOSS" in exit_reason else "🎯"
            pnl_emoji = "✅" if pnl_dollars > 0 else "❌"
            
            message = f"""
{alert_emoji} PRICE ALERT: EXIT SIGNAL

📊 Market: {position.market_name[:60]}
🎲 Position: BET {position.side}
⚡ Trigger: {exit_reason.replace('_', ' ')}

💰 Entry: {position.entry_price*100:.1f}%
📉 Current: {exit_price*100:.1f}%
⏱️ Hold Time: {hold_str}

{pnl_emoji} Unrealized P&L:
   Position: ${position.position_size:.2f}
   {"Profit" if pnl_dollars > 0 else "Loss"}: ${abs(pnl_dollars):.2f} ({pnl_pct*100:+.1f}%)

💡 Action: Consider {"taking profit" if pnl_dollars > 0 else "cutting loss"}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""".strip()
            
            # Send via existing telegram alerter
            self._send_telegram(message)
            
            logger.info(f"Exit alert sent for position #{position.id}")
            
        except Exception as e:
            logger.error(f"Error sending exit alert: {e}")
    
    def _send_telegram(self, message: str):
        """Send message via Telegram"""
        try:
            import subprocess
            from config import TELEGRAM_TARGET
            
            cmd = [
                "openclaw",
                "message",
                "send",
                "--channel", "telegram",
                "--target", TELEGRAM_TARGET,
                "--message", message
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Telegram send failed: {result.stderr}")
            
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
    
    def _heartbeat(self):
        """Periodic health check and status report"""
        logger.info("=" * 80)
        logger.info(f"💓 HEARTBEAT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Open Positions: {len(self.positions)}")
        logger.info(f"WebSocket: {'CONNECTED' if self._is_websocket_healthy() else 'DISCONNECTED'}")
        logger.info(f"Mode: {'WebSocket' if self.use_websocket else 'Polling'}")
        
        # Check database size
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM paper_position_ticks")
            tick_count = cursor.fetchone()[0]
            conn.close()
            logger.info(f"Price ticks logged: {tick_count:,}")
        except:
            pass
        
        logger.info("=" * 80)
    
    # ===== WebSocket Implementation =====
    
    def _is_websocket_healthy(self) -> bool:
        """Check if WebSocket connection is healthy"""
        return self.ws is not None and self.ws.sock and self.ws.sock.connected
    
    def _websocket_loop(self):
        """WebSocket connection loop with auto-reconnection"""
        while self.running:
            try:
                logger.info("Connecting to Polymarket WebSocket...")
                
                self.ws = websocket.WebSocketApp(
                    WS_API,
                    on_open=self._on_ws_open,
                    on_message=self._on_ws_message,
                    on_error=self._on_ws_error,
                    on_close=self._on_ws_close
                )
                
                # Run WebSocket (blocks until connection closes)
                self.ws.run_forever()
                
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            
            # Wait before reconnecting
            if self.running:
                logger.info(f"Reconnecting WebSocket in {WS_RECONNECT_DELAY}s...")
                time.sleep(WS_RECONNECT_DELAY)
    
    def _on_ws_open(self, ws):
        """WebSocket connection opened"""
        logger.info("✅ WebSocket connected")
        
        # Subscribe to price updates for all positions
        for market_id in self.positions.keys():
            try:
                subscribe_msg = {
                    "type": "subscribe",
                    "channel": "market",
                    "market": market_id
                }
                ws.send(json.dumps(subscribe_msg))
                logger.info(f"Subscribed to market: {market_id}")
            except Exception as e:
                logger.error(f"Error subscribing to {market_id}: {e}")
    
    def _on_ws_message(self, ws, message):
        """WebSocket message received"""
        try:
            data = json.loads(message)
            
            # Parse price update (adjust based on actual Polymarket WS format)
            if data.get('type') == 'market_update':
                market_id = data.get('market')
                price = float(data.get('price', 0))
                
                if market_id in self.positions:
                    position = self.positions[market_id]
                    self._process_price_update(position, price)
            
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    def _on_ws_error(self, ws, error):
        """WebSocket error occurred"""
        logger.error(f"WebSocket error: {error}")
    
    def _on_ws_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed"""
        logger.warning(f"WebSocket closed: {close_status_code} - {close_msg}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Polymarket Price Monitor")
    parser.add_argument(
        '--no-websocket',
        action='store_true',
        help='Disable WebSocket, use polling only'
    )
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=POLL_INTERVAL,
        help='Polling interval in seconds (default: 60)'
    )
    
    args = parser.parse_args()
    
    # Update global polling interval
    global POLL_INTERVAL
    POLL_INTERVAL = args.poll_interval
    
    # Create and start monitor
    monitor = PriceMonitor(use_websocket=not args.no_websocket)
    
    try:
        monitor.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        monitor.stop()


if __name__ == "__main__":
    main()
