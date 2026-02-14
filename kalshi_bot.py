#!/usr/bin/env python3
"""
Kalshi Trading Bot
==================
A production-ready trading bot skeleton for Kalshi prediction markets.

Kalshi is the ONLY US-LEGAL prediction market (CFTC regulated).
No VPN needed!

Setup:
1. pip install kalshi-python requests cryptography websockets
2. Get API keys from https://kalshi.com (Account → API Keys)
3. Set your credentials below or use environment variables
4. Run: python kalshi_bot.py

Author: OpenClaw
License: MIT
"""

import os
import json
import time
import uuid
import base64
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

import requests
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class KalshiConfig:
    """Configuration for Kalshi API connection."""
    
    # Environment: 'demo' or 'production'
    environment: str = 'demo'
    
    # API Credentials (set via env vars or directly)
    api_key_id: str = os.getenv('KALSHI_API_KEY_ID', 'YOUR_API_KEY_ID_HERE')
    private_key_path: str = os.getenv('KALSHI_PRIVATE_KEY_PATH', 'kalshi-key.key')
    
    # Trading Parameters
    max_position_size: int = 100  # Max contracts per position
    max_order_value_cents: int = 10000  # Max order value ($100)
    default_order_type: str = 'limit'
    
    @property
    def base_url(self) -> str:
        if self.environment == 'production':
            return 'https://api.elections.kalshi.com/trade-api/v2'
        return 'https://demo-api.kalshi.co/trade-api/v2'
    
    @property
    def ws_url(self) -> str:
        if self.environment == 'production':
            return 'wss://api.elections.kalshi.com/trade-api/ws/v2'
        return 'wss://demo-api.kalshi.co/trade-api/ws/v2'


class OrderSide(Enum):
    YES = 'yes'
    NO = 'no'


class OrderAction(Enum):
    BUY = 'buy'
    SELL = 'sell'


class OrderType(Enum):
    LIMIT = 'limit'
    MARKET = 'market'


# ============================================================================
# KALSHI API CLIENT
# ============================================================================

class KalshiClient:
    """
    Kalshi API Client with full authentication support.
    
    This client handles:
    - RSA-PSS signature generation
    - All REST API endpoints
    - WebSocket connections (async)
    """
    
    def __init__(self, config: KalshiConfig):
        self.config = config
        self.private_key = None
        self.session = requests.Session()
        self.logger = logging.getLogger('KalshiClient')
        
        # Load private key
        self._load_private_key()
    
    def _load_private_key(self):
        """Load the RSA private key from file."""
        try:
            with open(self.config.private_key_path, 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            self.logger.info("Private key loaded successfully")
        except FileNotFoundError:
            self.logger.warning(f"Private key not found at {self.config.private_key_path}")
            self.logger.warning("Only unauthenticated endpoints will work")
        except Exception as e:
            self.logger.error(f"Error loading private key: {e}")
            raise
    
    def _sign_request(self, timestamp: str, method: str, path: str) -> str:
        """
        Create RSA-PSS signature for request authentication.
        
        The signature is created by:
        1. Concatenating: timestamp + method + path (without query params)
        2. Signing with RSA-PSS + SHA256
        3. Base64 encoding the result
        """
        # Strip query parameters
        path_without_query = path.split('?')[0]
        
        # Create message to sign
        message = f"{timestamp}{method}{path_without_query}".encode('utf-8')
        
        # Sign with RSA-PSS
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _get_auth_headers(self, method: str, path: str) -> Dict[str, str]:
        """Generate authentication headers for a request."""
        timestamp = str(int(time.time() * 1000))
        signature = self._sign_request(timestamp, method, path)
        
        return {
            'KALSHI-ACCESS-KEY': self.config.api_key_id,
            'KALSHI-ACCESS-SIGNATURE': signature,
            'KALSHI-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
    
    def _request(self, method: str, path: str, 
                 data: Optional[Dict] = None, 
                 auth: bool = True) -> Dict[str, Any]:
        """Make an authenticated or public request to the API."""
        url = f"{self.config.base_url}{path}"
        
        headers = {}
        if auth and self.private_key:
            headers = self._get_auth_headers(method, path)
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=data)
            elif method == 'POST':
                response = self.session.post(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json() if response.text else {}
            
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP Error: {e}")
            self.logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Request error: {e}")
            raise
    
    # ========================================================================
    # PUBLIC ENDPOINTS (No Authentication Required)
    # ========================================================================
    
    def get_exchange_status(self) -> Dict:
        """Get current exchange status (trading active, maintenance, etc.)."""
        return self._request('GET', '/exchange/status', auth=False)
    
    def get_markets(self, 
                    status: str = 'open',
                    limit: int = 100,
                    cursor: Optional[str] = None,
                    series_ticker: Optional[str] = None,
                    event_ticker: Optional[str] = None) -> Dict:
        """
        Get list of markets.
        
        Args:
            status: 'open', 'closed', 'settled', or 'all'
            limit: Max results (1-1000)
            cursor: Pagination cursor
            series_ticker: Filter by series
            event_ticker: Filter by event
        """
        params = {'status': status, 'limit': limit}
        if cursor:
            params['cursor'] = cursor
        if series_ticker:
            params['series_ticker'] = series_ticker
        if event_ticker:
            params['event_ticker'] = event_ticker
        
        return self._request('GET', '/markets', data=params, auth=False)
    
    def get_market(self, ticker: str) -> Dict:
        """Get details for a specific market."""
        return self._request('GET', f'/markets/{ticker}', auth=False)
    
    def get_orderbook(self, ticker: str, depth: int = 10) -> Dict:
        """Get orderbook for a market."""
        params = {'depth': depth}
        return self._request('GET', f'/markets/{ticker}/orderbook', 
                            data=params, auth=False)
    
    def get_trades(self, ticker: str, limit: int = 100) -> Dict:
        """Get recent trades for a market."""
        params = {'ticker': ticker, 'limit': limit}
        return self._request('GET', '/markets/trades', data=params, auth=False)
    
    def get_events(self, 
                   status: str = 'open',
                   limit: int = 100) -> Dict:
        """Get list of events."""
        params = {'status': status, 'limit': limit}
        return self._request('GET', '/events', data=params, auth=False)
    
    def get_series(self, ticker: Optional[str] = None) -> Dict:
        """Get series information."""
        if ticker:
            return self._request('GET', f'/series/{ticker}', auth=False)
        return self._request('GET', '/series', auth=False)
    
    # ========================================================================
    # AUTHENTICATED ENDPOINTS
    # ========================================================================
    
    def get_balance(self) -> Dict:
        """Get your account balance."""
        return self._request('GET', '/portfolio/balance')
    
    def get_positions(self, 
                      ticker: Optional[str] = None,
                      limit: int = 100) -> Dict:
        """Get your current positions."""
        params = {'limit': limit}
        if ticker:
            params['ticker'] = ticker
        return self._request('GET', '/portfolio/positions', data=params)
    
    def get_orders(self,
                   ticker: Optional[str] = None,
                   status: str = 'resting',
                   limit: int = 100) -> Dict:
        """
        Get your orders.
        
        Args:
            ticker: Filter by market ticker
            status: 'resting', 'pending', 'executed', 'canceled'
            limit: Max results
        """
        params = {'status': status, 'limit': limit}
        if ticker:
            params['ticker'] = ticker
        return self._request('GET', '/portfolio/orders', data=params)
    
    def get_order(self, order_id: str) -> Dict:
        """Get a specific order by ID."""
        return self._request('GET', f'/portfolio/orders/{order_id}')
    
    def create_order(self,
                     ticker: str,
                     action: OrderAction,
                     side: OrderSide,
                     count: int,
                     order_type: OrderType = OrderType.LIMIT,
                     yes_price: Optional[int] = None,
                     no_price: Optional[int] = None,
                     client_order_id: Optional[str] = None,
                     expiration_ts: Optional[int] = None,
                     post_only: bool = False) -> Dict:
        """
        Create a new order.
        
        Args:
            ticker: Market ticker (e.g., 'KXHARRIS24-LSV')
            action: BUY or SELL
            side: YES or NO
            count: Number of contracts
            order_type: LIMIT or MARKET
            yes_price: Price in cents (1-99) for YES side
            no_price: Price in cents (1-99) for NO side
            client_order_id: Your unique ID for deduplication
            expiration_ts: Unix timestamp for order expiration
            post_only: If True, order will be canceled if it would match
        
        Returns:
            Created order details
        """
        # Validate inputs
        if count <= 0:
            raise ValueError("Count must be positive")
        if count > self.config.max_position_size:
            raise ValueError(f"Count exceeds max position size: {self.config.max_position_size}")
        
        if order_type == OrderType.LIMIT:
            if yes_price is None and no_price is None:
                raise ValueError("Limit orders require yes_price or no_price")
            if yes_price is not None and not (1 <= yes_price <= 99):
                raise ValueError("Price must be between 1 and 99 cents")
            if no_price is not None and not (1 <= no_price <= 99):
                raise ValueError("Price must be between 1 and 99 cents")
        
        # Build order data
        order_data = {
            'ticker': ticker,
            'action': action.value,
            'side': side.value,
            'count': count,
            'type': order_type.value,
            'client_order_id': client_order_id or str(uuid.uuid4())
        }
        
        if yes_price is not None:
            order_data['yes_price'] = yes_price
        if no_price is not None:
            order_data['no_price'] = no_price
        if expiration_ts is not None:
            order_data['expiration_ts'] = expiration_ts
        if post_only:
            order_data['post_only'] = True
        
        self.logger.info(f"Creating order: {order_data}")
        return self._request('POST', '/portfolio/orders', data=order_data)
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order by ID."""
        self.logger.info(f"Canceling order: {order_id}")
        return self._request('DELETE', f'/portfolio/orders/{order_id}')
    
    def cancel_all_orders(self, ticker: Optional[str] = None) -> Dict:
        """Cancel all resting orders, optionally filtered by ticker."""
        params = {}
        if ticker:
            params['ticker'] = ticker
        self.logger.info(f"Canceling all orders for {ticker or 'all markets'}")
        return self._request('DELETE', '/portfolio/orders', data=params)
    
    def get_fills(self, 
                  ticker: Optional[str] = None,
                  limit: int = 100) -> Dict:
        """Get your fill history."""
        params = {'limit': limit}
        if ticker:
            params['ticker'] = ticker
        return self._request('GET', '/portfolio/fills', data=params)
    
    def get_settlements(self, limit: int = 100) -> Dict:
        """Get your settlement history."""
        params = {'limit': limit}
        return self._request('GET', '/portfolio/settlements', data=params)


# ============================================================================
# TRADING BOT
# ============================================================================

class TradingBot:
    """
    Example trading bot implementing various strategies.
    
    This is a skeleton - implement your own strategies!
    """
    
    def __init__(self, config: KalshiConfig):
        self.config = config
        self.client = KalshiClient(config)
        self.logger = logging.getLogger('TradingBot')
        self.running = False
        
        # Track state
        self.positions: Dict[str, int] = {}
        self.pending_orders: Dict[str, Dict] = {}
    
    def check_exchange_status(self) -> bool:
        """Verify exchange is open for trading."""
        status = self.client.get_exchange_status()
        
        if not status.get('exchange_active'):
            self.logger.warning("Exchange is not active")
            return False
        
        if not status.get('trading_active'):
            self.logger.warning("Trading is not active (outside trading hours)")
            return False
        
        self.logger.info("Exchange is active and trading is open")
        return True
    
    def get_account_summary(self) -> Dict:
        """Get account balance and positions summary."""
        balance = self.client.get_balance()
        positions = self.client.get_positions()
        orders = self.client.get_orders(status='resting')
        
        return {
            'balance_cents': balance.get('balance', 0),
            'balance_usd': balance.get('balance', 0) / 100,
            'positions': positions.get('market_positions', []),
            'open_orders': orders.get('orders', [])
        }
    
    def find_opportunities(self, 
                           min_volume: int = 1000,
                           max_spread: int = 10) -> List[Dict]:
        """
        Find trading opportunities based on criteria.
        
        Args:
            min_volume: Minimum 24h volume
            max_spread: Maximum bid-ask spread in cents
        
        Returns:
            List of market opportunities
        """
        opportunities = []
        markets = self.client.get_markets(status='open', limit=200)
        
        for market in markets.get('markets', []):
            volume_24h = market.get('volume_24h', 0)
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 0)
            
            if yes_bid and yes_ask:
                spread = yes_ask - yes_bid
                
                if volume_24h >= min_volume and spread <= max_spread:
                    opportunities.append({
                        'ticker': market['ticker'],
                        'title': market.get('title', ''),
                        'yes_bid': yes_bid,
                        'yes_ask': yes_ask,
                        'spread': spread,
                        'volume_24h': volume_24h,
                        'last_price': market.get('last_price', 0)
                    })
        
        # Sort by spread (tightest first)
        opportunities.sort(key=lambda x: x['spread'])
        
        return opportunities
    
    def market_make(self, 
                    ticker: str,
                    spread: int = 2,
                    size: int = 10,
                    mid_price: Optional[int] = None) -> tuple:
        """
        Simple market making strategy - post bid and ask.
        
        Args:
            ticker: Market ticker
            spread: Total spread in cents (will be split)
            size: Order size in contracts
            mid_price: Optional mid price (otherwise fetched from orderbook)
        
        Returns:
            Tuple of (bid_order, ask_order)
        """
        # Get current orderbook if no mid price provided
        if mid_price is None:
            orderbook = self.client.get_orderbook(ticker)
            yes_bids = orderbook.get('orderbook', {}).get('yes', [])
            
            if yes_bids:
                # Use best bid as reference
                best_bid = max(yes_bids, key=lambda x: x[0])
                mid_price = best_bid[0] + 1
            else:
                self.logger.warning("No orderbook data, using 50 as mid")
                mid_price = 50
        
        half_spread = spread // 2
        bid_price = max(1, mid_price - half_spread)
        ask_price = min(99, mid_price + half_spread)
        
        self.logger.info(f"Market making {ticker}: bid={bid_price}, ask={ask_price}, size={size}")
        
        # Place bid (buy YES)
        bid_order = self.client.create_order(
            ticker=ticker,
            action=OrderAction.BUY,
            side=OrderSide.YES,
            count=size,
            order_type=OrderType.LIMIT,
            yes_price=bid_price,
            post_only=True
        )
        
        # Place ask (sell YES / buy NO at inverse price)
        ask_order = self.client.create_order(
            ticker=ticker,
            action=OrderAction.BUY,
            side=OrderSide.NO,
            count=size,
            order_type=OrderType.LIMIT,
            no_price=100 - ask_price,  # NO price is inverse of YES
            post_only=True
        )
        
        return bid_order, ask_order
    
    def execute_directional_trade(self,
                                   ticker: str,
                                   side: OrderSide,
                                   count: int,
                                   max_price: Optional[int] = None) -> Dict:
        """
        Execute a directional trade (you have a view on the outcome).
        
        Args:
            ticker: Market ticker
            side: YES or NO
            count: Number of contracts
            max_price: Maximum price to pay (cents)
        
        Returns:
            Order result
        """
        market = self.client.get_market(ticker)
        
        if side == OrderSide.YES:
            current_ask = market.get('market', {}).get('yes_ask', 0)
            if max_price and current_ask > max_price:
                raise ValueError(f"Ask ({current_ask}) exceeds max price ({max_price})")
            price = max_price or current_ask
        else:
            current_ask = market.get('market', {}).get('no_ask', 0)
            if max_price and current_ask > max_price:
                raise ValueError(f"Ask ({current_ask}) exceeds max price ({max_price})")
            price = max_price or current_ask
        
        self.logger.info(f"Directional trade: {side.value} {count}x {ticker} @ {price}¢")
        
        if side == OrderSide.YES:
            return self.client.create_order(
                ticker=ticker,
                action=OrderAction.BUY,
                side=OrderSide.YES,
                count=count,
                order_type=OrderType.LIMIT,
                yes_price=price
            )
        else:
            return self.client.create_order(
                ticker=ticker,
                action=OrderAction.BUY,
                side=OrderSide.NO,
                count=count,
                order_type=OrderType.LIMIT,
                no_price=price
            )
    
    def close_position(self, ticker: str) -> Optional[Dict]:
        """Close out an existing position."""
        positions = self.client.get_positions(ticker=ticker)
        
        for pos in positions.get('market_positions', []):
            if pos['ticker'] == ticker:
                # Determine position size and direction
                yes_pos = pos.get('position', 0)
                
                if yes_pos > 0:
                    # Sell YES position
                    self.logger.info(f"Closing long YES position: {yes_pos} contracts")
                    return self.client.create_order(
                        ticker=ticker,
                        action=OrderAction.SELL,
                        side=OrderSide.YES,
                        count=yes_pos,
                        order_type=OrderType.MARKET
                    )
                elif yes_pos < 0:
                    # This means we're long NO (short YES)
                    no_pos = abs(yes_pos)
                    self.logger.info(f"Closing long NO position: {no_pos} contracts")
                    return self.client.create_order(
                        ticker=ticker,
                        action=OrderAction.SELL,
                        side=OrderSide.NO,
                        count=no_pos,
                        order_type=OrderType.MARKET
                    )
        
        self.logger.info(f"No position found for {ticker}")
        return None
    
    def run_demo(self):
        """Run a demo showing bot capabilities (read-only, no trades)."""
        print("\n" + "="*60)
        print("KALSHI TRADING BOT - DEMO MODE")
        print("="*60)
        
        # Check exchange status
        print("\n📊 Checking exchange status...")
        if not self.check_exchange_status():
            print("❌ Exchange not available for trading")
            return
        print("✅ Exchange is active!")
        
        # Show account info (if authenticated)
        try:
            print("\n💰 Account Summary:")
            summary = self.get_account_summary()
            print(f"   Balance: ${summary['balance_usd']:.2f}")
            print(f"   Open positions: {len(summary['positions'])}")
            print(f"   Open orders: {len(summary['open_orders'])}")
        except Exception as e:
            print(f"   ⚠️  Not authenticated: {e}")
            print("   (Set your API credentials to see account info)")
        
        # Find opportunities
        print("\n🔍 Scanning for opportunities...")
        opportunities = self.find_opportunities(min_volume=500, max_spread=15)
        
        print(f"\n📈 Top 5 Markets by Spread:")
        print("-" * 60)
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"{i}. {opp['ticker']}")
            print(f"   {opp['title'][:50]}...")
            print(f"   Bid: {opp['yes_bid']}¢  Ask: {opp['yes_ask']}¢  "
                  f"Spread: {opp['spread']}¢  Vol: {opp['volume_24h']}")
        
        print("\n" + "="*60)
        print("Demo complete! Set KALSHI_ENVIRONMENT=demo to test trading.")
        print("="*60 + "\n")


# ============================================================================
# WEBSOCKET CLIENT (Async)
# ============================================================================

class KalshiWebSocket:
    """
    Async WebSocket client for real-time market data.
    """
    
    def __init__(self, config: KalshiConfig):
        self.config = config
        self.ws = None
        self.message_id = 1
        self.logger = logging.getLogger('KalshiWebSocket')
        
        # Load private key for auth
        try:
            with open(config.private_key_path, 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
        except:
            self.private_key = None
    
    def _sign(self, timestamp: str, method: str, path: str) -> str:
        """Create signature for WebSocket auth."""
        message = f"{timestamp}{method}{path}".encode('utf-8')
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    
    def _get_ws_headers(self) -> Dict[str, str]:
        """Get WebSocket authentication headers."""
        if not self.private_key:
            return {}
        
        timestamp = str(int(time.time() * 1000))
        path = '/trade-api/ws/v2'
        signature = self._sign(timestamp, 'GET', path)
        
        return {
            'KALSHI-ACCESS-KEY': self.config.api_key_id,
            'KALSHI-ACCESS-SIGNATURE': signature,
            'KALSHI-ACCESS-TIMESTAMP': timestamp
        }
    
    async def connect(self):
        """Establish WebSocket connection."""
        import websockets
        
        headers = self._get_ws_headers()
        self.ws = await websockets.connect(
            self.config.ws_url,
            additional_headers=headers
        )
        self.logger.info("WebSocket connected")
    
    async def subscribe(self, channels: List[str], 
                        market_ticker: Optional[str] = None):
        """Subscribe to WebSocket channels."""
        msg = {
            'id': self.message_id,
            'cmd': 'subscribe',
            'params': {
                'channels': channels
            }
        }
        if market_ticker:
            msg['params']['market_ticker'] = market_ticker
        
        await self.ws.send(json.dumps(msg))
        self.message_id += 1
    
    async def listen(self, handler):
        """Listen for messages and call handler."""
        async for message in self.ws:
            data = json.loads(message)
            await handler(data)
    
    async def close(self):
        """Close WebSocket connection."""
        if self.ws:
            await self.ws.close()


# ============================================================================
# MAIN
# ============================================================================

def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('kalshi_bot.log')
        ]
    )


def main():
    """Main entry point."""
    setup_logging()
    logger = logging.getLogger('main')
    
    # Load configuration
    config = KalshiConfig(
        environment=os.getenv('KALSHI_ENVIRONMENT', 'demo'),
        api_key_id=os.getenv('KALSHI_API_KEY_ID', 'YOUR_API_KEY_ID_HERE'),
        private_key_path=os.getenv('KALSHI_PRIVATE_KEY_PATH', 'kalshi-key.key')
    )
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              🎲 KALSHI TRADING BOT 🎲                        ║
║                                                              ║
║  US-Legal Prediction Markets (CFTC Regulated)                ║
║  Environment: {config.environment.upper():10}                              ║
║  API URL: {config.base_url[:35]}...                  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create bot instance
    bot = TradingBot(config)
    
    # Run demo
    bot.run_demo()
    
    # Example: Place a trade (uncomment to test)
    # WARNING: This will place a real order in production!
    """
    if config.environment == 'demo':
        # Find an open market
        markets = bot.client.get_markets(status='open', limit=1)
        if markets['markets']:
            ticker = markets['markets'][0]['ticker']
            
            # Place a small test order
            order = bot.client.create_order(
                ticker=ticker,
                action=OrderAction.BUY,
                side=OrderSide.YES,
                count=1,
                order_type=OrderType.LIMIT,
                yes_price=1  # Lowest possible price (unlikely to fill)
            )
            print(f"Test order placed: {order}")
            
            # Cancel it
            order_id = order['order']['order_id']
            bot.client.cancel_order(order_id)
            print("Test order canceled")
    """


if __name__ == '__main__':
    main()
