#!/usr/bin/env python3
"""
Kalshi Trading Bot - Buy the Dip Strategy

A trading bot for Kalshi prediction markets that identifies and buys
positions that have experienced significant price drops.

Features:
- RSA key-based authentication
- Paper trading mode (simulated orders)
- Buy the dip strategy
- Position tracking
- Comprehensive logging

Usage:
    python kalshi_trading_bot.py [--paper] [--once]
"""

import argparse
import base64
import datetime
import hashlib
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests

# Fix Windows console encoding for emoji
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass  # Python < 3.7
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

# Import configuration
import kalshi_config as config

# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging():
    """Configure logging with file and console output."""
    log_format = "%(asctime)s | %(levelname)-8s | %(message)s"
    
    # Use UTF-8 encoding for file handler, and handle console encoding gracefully
    file_handler = logging.FileHandler(config.LOG_FILE, encoding='utf-8')
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Set formatters
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Get logger
    logger = logging.getLogger("kalshi_bot")
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Market:
    """Represents a Kalshi market."""
    ticker: str
    title: str
    status: str
    yes_bid: int  # in cents
    yes_ask: int  # in cents
    last_price: int  # in cents
    previous_price: int  # in cents
    volume_24h: int
    open_interest: int
    close_time: str
    
    @property
    def price_change_pct(self) -> float:
        """Calculate percentage change from previous price."""
        if self.previous_price == 0:
            return 0
        return (self.last_price - self.previous_price) / self.previous_price
    
    @property
    def is_active(self) -> bool:
        return self.status == "active"
    
    @property
    def mid_price(self) -> float:
        """Calculate mid price between bid and ask."""
        if self.yes_bid == 0 or self.yes_ask == 0:
            return self.last_price
        return (self.yes_bid + self.yes_ask) / 2

@dataclass
class Position:
    """Represents a position in a market."""
    ticker: str
    side: str  # "yes" or "no"
    quantity: int
    avg_price: int  # in cents
    current_price: int = 0

@dataclass
class Order:
    """Represents an order."""
    ticker: str
    side: str  # "yes" or "no"
    action: str  # "buy" or "sell"
    type: str  # "limit" or "market"
    price: int  # in cents
    quantity: int
    order_id: str = ""
    status: str = "pending"
    created_at: str = ""

@dataclass
class PaperTradingState:
    """State for paper trading simulation."""
    balance_cents: int = 10000  # $100 starting balance
    positions: dict = field(default_factory=dict)
    orders: list = field(default_factory=list)
    pnl_cents: int = 0

# =============================================================================
# KALSHI API CLIENT
# =============================================================================

class KalshiAuth:
    """Handles RSA key-based authentication for Kalshi API."""
    
    def __init__(self, api_key_id: str, private_key_pem: str):
        self.api_key_id = api_key_id
        self.private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
    
    def sign_request(self, method: str, path: str, timestamp: str) -> str:
        """Sign a request with the private key."""
        message = f"{timestamp}{method}{path}"
        signature = self.private_key.sign(
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
    
    def get_headers(self, method: str, path: str) -> dict:
        """Get authentication headers for a request."""
        timestamp = str(int(time.time() * 1000))
        signature = self.sign_request(method, path, timestamp)
        
        return {
            "KALSHI-ACCESS-KEY": self.api_key_id,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
        }


class KalshiClient:
    """Client for interacting with the Kalshi API."""
    
    def __init__(self, api_key_id: str = "", private_key_pem: str = "", paper_trading: bool = True):
        self.base_url = config.API_BASE_URL
        self.paper_trading = paper_trading
        self.session = requests.Session()
        
        # Authentication (only needed for live trading)
        self.auth = None
        if api_key_id and private_key_pem and not paper_trading:
            self.auth = KalshiAuth(api_key_id, private_key_pem)
        
        # Paper trading state
        self.paper_state = PaperTradingState()
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 60 / config.MAX_REQUESTS_PER_MINUTE
    
    def _rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make an authenticated API request."""
        self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        path = f"/trade-api/v2{endpoint}"
        
        headers = {"Content-Type": "application/json"}
        if self.auth:
            headers = self.auth.get_headers(method.upper(), path)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=data, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    # =========================================================================
    # PUBLIC ENDPOINTS (no auth required)
    # =========================================================================
    
    def get_exchange_status(self) -> dict:
        """Get exchange status."""
        return self._request("GET", "/exchange/status")
    
    def get_markets(self, limit: int = 100, cursor: str = None, status: str = None) -> dict:
        """Get list of markets."""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if status:
            params["status"] = status
        return self._request("GET", "/markets", params)
    
    def get_market(self, ticker: str) -> dict:
        """Get a specific market."""
        return self._request("GET", f"/markets/{ticker}")
    
    def get_market_orderbook(self, ticker: str) -> dict:
        """Get orderbook for a market."""
        return self._request("GET", f"/markets/{ticker}/orderbook")
    
    def get_market_history(self, ticker: str, limit: int = 100) -> dict:
        """Get price history for a market."""
        return self._request("GET", f"/markets/{ticker}/history", {"limit": limit})
    
    # =========================================================================
    # AUTHENTICATED ENDPOINTS
    # =========================================================================
    
    def get_balance(self) -> dict:
        """Get account balance."""
        if self.paper_trading:
            return {"balance": self.paper_state.balance_cents}
        return self._request("GET", "/portfolio/balance")
    
    def get_positions(self) -> dict:
        """Get current positions."""
        if self.paper_trading:
            return {"market_positions": list(self.paper_state.positions.values())}
        return self._request("GET", "/portfolio/positions")
    
    def get_orders(self, status: str = "resting") -> dict:
        """Get orders."""
        if self.paper_trading:
            return {"orders": [o for o in self.paper_state.orders if o.get("status") == status]}
        return self._request("GET", "/portfolio/orders", {"status": status})
    
    def create_order(
        self,
        ticker: str,
        side: str,
        action: str,
        order_type: str,
        count: int,
        yes_price: int = None,
        no_price: int = None,
    ) -> dict:
        """Create a new order."""
        
        if self.paper_trading:
            return self._paper_create_order(ticker, side, action, order_type, count, yes_price, no_price)
        
        data = {
            "ticker": ticker,
            "side": side,
            "action": action,
            "type": order_type,
            "count": count,
        }
        if yes_price is not None:
            data["yes_price"] = yes_price
        if no_price is not None:
            data["no_price"] = no_price
        
        return self._request("POST", "/portfolio/orders", data)
    
    def cancel_order(self, order_id: str) -> dict:
        """Cancel an order."""
        if self.paper_trading:
            for order in self.paper_state.orders:
                if order.get("order_id") == order_id:
                    order["status"] = "canceled"
            return {"status": "canceled"}
        return self._request("DELETE", f"/portfolio/orders/{order_id}")
    
    # =========================================================================
    # PAPER TRADING SIMULATION
    # =========================================================================
    
    def _paper_create_order(
        self,
        ticker: str,
        side: str,
        action: str,
        order_type: str,
        count: int,
        yes_price: int = None,
        no_price: int = None,
    ) -> dict:
        """Simulate order creation in paper trading mode."""
        
        price = yes_price if side == "yes" else no_price
        if price is None:
            price = 50  # Default mid-price
        
        cost = price * count
        
        # Check balance for buys
        if action == "buy" and cost > self.paper_state.balance_cents:
            raise ValueError(f"Insufficient balance. Need {cost}¢, have {self.paper_state.balance_cents}¢")
        
        # Create order
        order_id = f"PAPER-{int(time.time() * 1000)}"
        order = {
            "order_id": order_id,
            "ticker": ticker,
            "side": side,
            "action": action,
            "type": order_type,
            "yes_price": yes_price,
            "no_price": no_price,
            "count": count,
            "status": "filled",  # Instant fill for paper trading
            "created_time": datetime.datetime.now().isoformat(),
        }
        self.paper_state.orders.append(order)
        
        # Update balance and positions
        if action == "buy":
            self.paper_state.balance_cents -= cost
            
            pos_key = f"{ticker}_{side}"
            if pos_key in self.paper_state.positions:
                pos = self.paper_state.positions[pos_key]
                # Update average price
                total_count = pos["count"] + count
                pos["avg_price"] = (pos["avg_price"] * pos["count"] + price * count) // total_count
                pos["count"] = total_count
            else:
                self.paper_state.positions[pos_key] = {
                    "ticker": ticker,
                    "side": side,
                    "count": count,
                    "avg_price": price,
                }
        
        elif action == "sell":
            pos_key = f"{ticker}_{side}"
            if pos_key not in self.paper_state.positions:
                raise ValueError(f"No position to sell: {pos_key}")
            
            pos = self.paper_state.positions[pos_key]
            if count > pos["count"]:
                raise ValueError(f"Cannot sell {count}, only have {pos['count']}")
            
            # Calculate PnL
            sell_value = price * count
            cost_basis = pos["avg_price"] * count
            pnl = sell_value - cost_basis
            self.paper_state.pnl_cents += pnl
            self.paper_state.balance_cents += sell_value
            
            pos["count"] -= count
            if pos["count"] == 0:
                del self.paper_state.positions[pos_key]
        
        logger.info(f"📝 PAPER ORDER: {action.upper()} {count}x {ticker} {side} @ {price}¢")
        logger.info(f"   Balance: ${self.paper_state.balance_cents / 100:.2f} | PnL: ${self.paper_state.pnl_cents / 100:.2f}")
        
        return {"order": order}

# =============================================================================
# DIP BUYER STRATEGY
# =============================================================================

class DipBuyerStrategy:
    """Strategy that buys positions when prices drop significantly."""
    
    def __init__(self, client: KalshiClient):
        self.client = client
        self.config = config.DipBuyerConfig
        self.price_history: dict[str, list[int]] = {}  # ticker -> list of prices
        self.deployed_capital = 0
    
    def analyze_markets(self, markets: list[Market]) -> list[dict]:
        """Analyze markets and return buy signals."""
        signals = []
        
        for market in markets:
            if not market.is_active:
                continue
            
            # Update price history
            if market.ticker not in self.price_history:
                self.price_history[market.ticker] = []
            self.price_history[market.ticker].append(market.last_price)
            
            # Keep only last 100 prices
            self.price_history[market.ticker] = self.price_history[market.ticker][-100:]
            
            # Check for dip
            signal = self._check_dip_signal(market)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _check_dip_signal(self, market: Market) -> Optional[dict]:
        """Check if a market has a buy signal."""
        
        # Price must be in our range
        if market.yes_ask < self.config.MIN_BUY_PRICE_CENTS:
            return None
        if market.yes_ask > self.config.MAX_BUY_PRICE_CENTS:
            return None
        
        # Need price history to detect dip
        history = self.price_history.get(market.ticker, [])
        if len(history) < 2:
            # Use previous_price if available
            if market.previous_price > 0:
                drop_pct = (market.previous_price - market.last_price) / market.previous_price
            else:
                return None
        else:
            # Calculate drop from recent high
            recent_high = max(history[-10:]) if len(history) >= 10 else max(history)
            if recent_high == 0:
                return None
            drop_pct = (recent_high - market.last_price) / recent_high
        
        # Check if drop is significant enough
        if drop_pct < self.config.MIN_DIP_PERCENT:
            return None
        
        # Generate buy signal
        return {
            "ticker": market.ticker,
            "title": market.title[:50],
            "side": "yes",
            "action": "buy",
            "current_price": market.yes_ask,
            "drop_percent": drop_pct,
            "suggested_quantity": self.config.DEFAULT_ORDER_SIZE,
            "reason": f"Price dropped {drop_pct * 100:.1f}%",
        }
    
    def execute_signals(self, signals: list[dict]) -> list[dict]:
        """Execute buy signals (respecting position limits)."""
        executed = []
        
        for signal in signals:
            try:
                # Check capital limits
                cost = signal["current_price"] * signal["suggested_quantity"]
                if self.deployed_capital + cost > self.config.MAX_CAPITAL_CENTS:
                    logger.warning(f"⚠️  Skipping {signal['ticker']}: would exceed max capital")
                    continue
                
                # Check existing position
                positions = self.client.get_positions().get("market_positions", [])
                existing_qty = sum(
                    p.get("count", 0) or p.get("quantity", 0)
                    for p in positions
                    if p.get("ticker") == signal["ticker"]
                )
                
                if existing_qty + signal["suggested_quantity"] > self.config.MAX_POSITION_SIZE:
                    logger.warning(f"⚠️  Skipping {signal['ticker']}: would exceed max position")
                    continue
                
                # Execute order
                result = self.client.create_order(
                    ticker=signal["ticker"],
                    side=signal["side"],
                    action=signal["action"],
                    order_type="limit",
                    count=signal["suggested_quantity"],
                    yes_price=signal["current_price"],
                )
                
                self.deployed_capital += cost
                executed.append({**signal, "result": result})
                
                logger.info(f"✅ EXECUTED: BUY {signal['suggested_quantity']}x {signal['ticker']} @ {signal['current_price']}¢")
                logger.info(f"   Reason: {signal['reason']}")
                
            except Exception as e:
                logger.error(f"❌ Failed to execute {signal['ticker']}: {e}")
        
        return executed

# =============================================================================
# MAIN BOT
# =============================================================================

class KalshiTradingBot:
    """Main trading bot orchestrator."""
    
    def __init__(self, paper_trading: bool = True):
        self.paper_trading = paper_trading
        
        # Initialize client
        api_key = config.API_KEY_ID
        private_key = config.load_private_key()
        
        self.client = KalshiClient(
            api_key_id=api_key,
            private_key_pem=private_key,
            paper_trading=paper_trading,
        )
        
        # Initialize strategy
        self.strategy = DipBuyerStrategy(self.client)
        
        self.running = False
    
    def check_connection(self) -> bool:
        """Verify connection to Kalshi API."""
        try:
            status = self.client.get_exchange_status()
            if status.get("trading_active"):
                logger.info("✅ Connected to Kalshi - Trading ACTIVE")
                return True
            else:
                logger.warning("⚠️  Connected to Kalshi - Trading INACTIVE")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Kalshi: {e}")
            return False
    
    def fetch_markets(self, max_markets: int = 500) -> list[Market]:
        """Fetch active markets (limited for performance)."""
        markets = []
        cursor = None
        page = 0
        max_pages = 5  # Limit pagination to avoid endless loops
        
        while page < max_pages:
            page += 1
            try:
                response = self.client.get_markets(limit=100, cursor=cursor)
                
                fetched = response.get("markets", [])
                if not fetched:
                    break
                
                for m in fetched:
                    # Only include active markets with some activity
                    if m.get("status") != "active":
                        continue
                    
                    markets.append(Market(
                        ticker=m.get("ticker", ""),
                        title=m.get("title", ""),
                        status=m.get("status", ""),
                        yes_bid=m.get("yes_bid", 0) or 0,
                        yes_ask=m.get("yes_ask", 0) or 0,
                        last_price=m.get("last_price", 0) or 0,
                        previous_price=m.get("previous_price", 0) or 0,
                        volume_24h=m.get("volume_24h", 0) or 0,
                        open_interest=m.get("open_interest", 0) or 0,
                        close_time=m.get("close_time", ""),
                    ))
                    
                    if len(markets) >= max_markets:
                        break
                
                if len(markets) >= max_markets:
                    break
                
                cursor = response.get("cursor")
                if not cursor:
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching markets: {e}")
                break
        
        logger.info(f"📊 Fetched {len(markets)} active markets")
        return markets
    
    def run_once(self):
        """Run one iteration of the bot."""
        logger.info("=" * 60)
        logger.info("🔄 Starting bot iteration...")
        
        # Fetch markets
        markets = self.fetch_markets()
        if not markets:
            logger.warning("No markets fetched")
            return
        
        # Filter to watched tickers if configured
        if self.strategy.config.WATCH_TICKERS:
            markets = [m for m in markets if m.ticker in self.strategy.config.WATCH_TICKERS]
            logger.info(f"📋 Filtered to {len(markets)} watched markets")
        
        # Analyze for signals
        signals = self.strategy.analyze_markets(markets)
        
        if signals:
            logger.info(f"🎯 Found {len(signals)} buy signals!")
            for s in signals:
                logger.info(f"   • {s['ticker']}: {s['reason']} (price: {s['current_price']}¢)")
            
            # Execute signals
            executed = self.strategy.execute_signals(signals)
            logger.info(f"✨ Executed {len(executed)} orders")
        else:
            logger.info("😴 No buy signals this iteration")
        
        # Log status
        self._log_status()
    
    def _log_status(self):
        """Log current bot status."""
        if self.paper_trading:
            state = self.client.paper_state
            logger.info("-" * 40)
            logger.info(f"💰 Balance: ${state.balance_cents / 100:.2f}")
            logger.info(f"📈 P&L: ${state.pnl_cents / 100:.2f}")
            logger.info(f"📦 Positions: {len(state.positions)}")
            for key, pos in state.positions.items():
                logger.info(f"   • {pos['ticker']} {pos['side']}: {pos['count']} @ {pos['avg_price']}¢")
    
    def run(self):
        """Run the bot continuously."""
        logger.info("=" * 60)
        logger.info("🤖 KALSHI TRADING BOT STARTING")
        logger.info(f"   Mode: {'PAPER TRADING' if self.paper_trading else 'LIVE TRADING'}")
        logger.info("=" * 60)
        
        if not self.check_connection():
            logger.error("Cannot start bot - connection failed")
            return
        
        config.print_config()
        
        self.running = True
        
        while self.running:
            try:
                self.run_once()
                
                logger.info(f"😴 Sleeping {config.POLL_INTERVAL_SECONDS}s until next iteration...")
                time.sleep(config.POLL_INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                logger.info("\n🛑 Bot stopped by user")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(10)
        
        logger.info("👋 Bot shutdown complete")

# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Kalshi Trading Bot - Buy the Dip")
    parser.add_argument("--live", action="store_true", help="Enable LIVE trading (default: paper)")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--status", action="store_true", help="Show exchange status and exit")
    parser.add_argument("--markets", action="store_true", help="List markets and exit")
    
    args = parser.parse_args()
    
    paper_trading = not args.live
    
    if args.live:
        # Validate config for live trading
        is_valid, errors = config.validate_config()
        if not is_valid:
            logger.error("❌ Configuration errors for live trading:")
            for err in errors:
                logger.error(f"   • {err}")
            sys.exit(1)
        
        # Confirm live trading
        print("\n⚠️  WARNING: LIVE TRADING MODE ⚠️")
        print("Real money will be used. Type 'CONFIRM' to proceed:")
        confirmation = input("> ").strip()
        if confirmation != "CONFIRM":
            print("Aborted.")
            sys.exit(0)
    
    bot = KalshiTradingBot(paper_trading=paper_trading)
    
    if args.status:
        bot.check_connection()
    elif args.markets:
        markets = bot.fetch_markets()
        for m in markets[:20]:
            print(f"{m.ticker}: {m.title[:40]} | {m.yes_bid}¢/{m.yes_ask}¢ | vol: {m.volume_24h}")
    elif args.once:
        bot.run_once()
    else:
        bot.run()

if __name__ == "__main__":
    main()
