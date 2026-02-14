"""
Order Manager for Polymarket Trading Bot
Handles order placement, checking, and cancellation
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

@dataclass
class OrderResult:
    """Result of an order placement attempt"""
    success: bool
    order_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: float = 0.0

@dataclass  
class Position:
    """Represents an open position"""
    token_id: str
    side: str  # "YES" or "NO"
    price: float
    size: float
    cost: float
    order_id: str
    timestamp: float

class OrderManager:
    """Manages orders and positions on Polymarket"""
    
    def __init__(self, client: ClobClient):
        self.client = client
        self.retry_attempts = 3
        self.retry_delay = 1.0  # seconds
    
    def place_limit_order(self, token_id: str, side: str, price: float, 
                         size: float) -> OrderResult:
        """
        Place a limit order
        
        Args:
            token_id: The token ID to trade
            side: "BUY" or "SELL"
            price: Price per share (0.01 to 0.99)
            size: Number of shares
            
        Returns:
            OrderResult with success status and order ID
        """
        # Validate inputs
        if price <= 0 or price >= 1:
            return OrderResult(
                success=False,
                error=f"Invalid price: {price}. Must be between 0.01 and 0.99"
            )
        
        if size <= 0:
            return OrderResult(
                success=False,
                error=f"Invalid size: {size}. Must be positive"
            )
        
        # Convert side string to constant
        side_constant = BUY if side.upper() == "BUY" else SELL
        
        # Create order arguments
        order_args = OrderArgs(
            token_id=token_id,
            price=str(price),
            size=str(size),
            side=side_constant
        )
        
        # Retry logic
        for attempt in range(self.retry_attempts):
            try:
                print(f"Placing {side} order: {size} shares at ${price} (attempt {attempt + 1})")
                
                # Create and sign order
                signed_order = self.client.create_order(order_args)
                
                # Post order
                response = self.client.post_order(signed_order, OrderType.GTC)
                
                # Extract order ID from response
                order_id = None
                if isinstance(response, dict):
                    order_id = response.get('id')
                elif hasattr(response, 'id'):
                    order_id = response.id
                
                print(f"Order placed successfully. Order ID: {order_id}")
                return OrderResult(
                    success=True,
                    order_id=order_id,
                    timestamp=time.time()
                )
                
            except Exception as e:
                error_msg = str(e)
                print(f"Order placement failed (attempt {attempt + 1}): {error_msg}")
                
                if attempt < self.retry_attempts - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    return OrderResult(
                        success=False,
                        error=error_msg,
                        timestamp=time.time()
                    )
        
        return OrderResult(
            success=False,
            error="Max retry attempts exceeded",
            timestamp=time.time()
        )
    
    def get_open_orders(self) -> List[Dict]:
        """Get all open orders"""
        try:
            orders = self.client.get_orders()
            return orders if isinstance(orders, list) else []
        except Exception as e:
            print(f"Error fetching open orders: {e}")
            return []
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get specific order by ID"""
        try:
            # Note: py-clob-client may not have get_order method
            # We'll fetch all orders and filter
            orders = self.get_open_orders()
            for order in orders:
                if order.get('id') == order_id:
                    return order
            return None
        except Exception as e:
            print(f"Error fetching order {order_id}: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order"""
        try:
            self.client.cancel(order_id)
            print(f"Order {order_id} cancelled successfully")
            return True
        except Exception as e:
            print(f"Error cancelling order {order_id}: {e}")
            return False
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        try:
            self.client.cancel_all()
            print("All orders cancelled successfully")
            return True
        except Exception as e:
            print(f"Error cancelling all orders: {e}")
            return False
    
    def get_positions(self) -> List[Position]:
        """
        Get current positions by checking open orders
        Note: This is a simplified implementation. In production,
        you'd want to track fills and calculate net position.
        """
        positions = []
        orders = self.get_open_orders()
        
        for order in orders:
            try:
                # Extract position info from order
                token_id = order.get('token_id')
                side = "BUY" if order.get('side') == 0 else "SELL"  # Assuming 0=BUY, 1=SELL
                price = float(order.get('price', 0))
                size = float(order.get('size', 0))
                order_id = order.get('id')
                
                if token_id and price > 0 and size > 0:
                    cost = price * size
                    position = Position(
                        token_id=token_id,
                        side=side,
                        price=price,
                        size=size,
                        cost=cost,
                        order_id=order_id,
                        timestamp=time.time()
                    )
                    positions.append(position)
                    
            except (ValueError, TypeError) as e:
                print(f"Error parsing order {order.get('id')}: {e}")
                continue
        
        return positions
    
    def get_balance(self) -> Optional[float]:
        """Get USDC balance"""
        try:
            # Note: py-clob-client balance method may vary
            # This is a placeholder - adjust based on actual client methods
            balances = self.client.get_balances()
            if balances and 'USDC' in balances:
                return float(balances['USDC'])
            return None
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return None
    
    def get_order_book(self, token_id: str) -> Optional[Dict]:
        """Get order book for a token"""
        try:
            order_book = self.client.get_order_book(token_id)
            return order_book
        except Exception as e:
            print(f"Error fetching order book for {token_id[:20]}...: {e}")
            return None
    
    def get_midpoint(self, token_id: str) -> Optional[float]:
        """Get midpoint price for a token"""
        try:
            midpoint = self.client.get_midpoint(token_id)
            if isinstance(midpoint, dict):
                return float(midpoint.get('midpoint', 0))
            elif isinstance(midpoint, (int, float, str)):
                return float(midpoint)
            return None
        except Exception as e:
            print(f"Error fetching midpoint for {token_id[:20]}...: {e}")
            return None
    
    def check_order_status(self, order_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if an order is still open
        
        Returns:
            Tuple of (is_open, status_message)
        """
        order = self.get_order(order_id)
        if not order:
            return False, "Order not found"
        
        # Check order status
        status = order.get('status', '').lower()
        if status in ['filled', 'cancelled', 'expired']:
            return False, f"Order {status}"
        
        return True, "Order is open"

if __name__ == "__main__":
    # Test code (requires proper client initialization)
    print("Order Manager module loaded")
    print("To test, initialize with a valid ClobClient and call methods")