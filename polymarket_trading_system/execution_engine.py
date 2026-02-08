"""
Execution Engine
Handles trade execution with comprehensive safety checks
"""
import asyncio
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import logging

from database import Signal, Trade, db_manager
from config import TRADING_CONFIG
from polymarket_client import PolymarketClient

logger = logging.getLogger(__name__)

class ExecutionEngine:
    """Safe trade execution with multiple safety checks"""
    
    def __init__(self):
        self.config = TRADING_CONFIG
        self.daily_pnl = Decimal("0")
        self.daily_trades_count = 0
        self.last_reset_date = datetime.utcnow().date()
    
    async def execute_signal(
        self, 
        signal: Signal, 
        client: PolymarketClient,
        agent_votes: list
    ) -> Optional[Trade]:
        """
        Execute a validated trading signal
        Returns Trade object if successful, None if rejected
        """
        # Reset daily counters if needed
        self._check_daily_reset()
        
        logger.info(f"Attempting to execute signal: {signal.market_slug}")
        
        # Pre-execution safety checks
        if not self._pre_execution_checks(signal):
            return None
        
        # Get current market data
        market = await client.get_market(signal.market_slug)
        if not market:
            logger.error(f"Failed to fetch market data for {signal.market_slug}")
            return None
        
        # Verify signal is still valid
        current_probability = Decimal(str(market.get("probabilityYes", 0))) * 100
        
        if not self._validate_signal_still_valid(signal, current_probability):
            logger.info(f"Signal no longer valid for {signal.market_slug}")
            signal.status = "expired"
            db_manager.update_signal(signal)
            return None
        
        # Get execution price
        orderbook = await client.get_market_orderbook(signal.market_slug)
        execution_price = self._get_execution_price(orderbook, signal.suggested_side)
        
        if not execution_price:
            logger.error(f"Could not determine execution price for {signal.market_slug}")
            return None
        
        # Calculate final position size
        final_size = self._calculate_position_size(signal, execution_price)
        
        # Simulate execution (paper trading mode)
        # In production, this would call the actual trading API
        trade = await self._simulate_execution(signal, execution_price, final_size, market)
        
        if trade:
            # Update signal status
            signal.status = "executed"
            signal.execution_price = execution_price
            signal.trade_id = trade.id
            db_manager.update_signal(signal)
            
            self.daily_trades_count += 1
            logger.info(f"Trade executed: {trade.id} - {signal.market_slug} {signal.suggested_side} @ {execution_price}%")
        
        return trade
    
    def _check_daily_reset(self):
        """Reset daily counters if it's a new day"""
        today = datetime.utcnow().date()
        if today != self.last_reset_date:
            self.daily_pnl = Decimal("0")
            self.daily_trades_count = 0
            self.last_reset_date = today
            logger.info("Daily counters reset")
    
    def _pre_execution_checks(self, signal: Signal) -> bool:
        """Run all pre-execution safety checks"""
        
        # 1. Daily loss limit check
        daily_loss_limit = -(self.config.INITIAL_BANKROLL * self.config.MAX_DAILY_RISK_PCT / 100)
        if self.daily_pnl <= daily_loss_limit:
            logger.warning("Daily loss limit reached - blocking new trades")
            return False
        
        # 2. Max daily trades check
        if self.daily_trades_count >= 10:  # Max 10 trades per day
            logger.warning("Daily trade limit reached")
            return False
        
        # 3. Check if signal hasn't expired
        if signal.expires_at and datetime.utcnow() > signal.expires_at:
            logger.info("Signal has expired")
            signal.status = "expired"
            db_manager.update_signal(signal)
            return False
        
        # 4. Verify signal still has required consensus
        if signal.agent_consensus_count < self.config.MIN_AGENT_CONSENSUS:
            logger.warning("Signal lacks required agent consensus")
            return False
        
        # 5. Circuit breaker check
        if self._is_circuit_breaker_active():
            logger.warning("Circuit breaker is active")
            return False
        
        return True
    
    def _validate_signal_still_valid(self, signal: Signal, current_probability: Decimal) -> bool:
        """Check if signal conditions are still met"""
        
        # For extreme probability signals, check if still in range
        if signal.strategy == "extreme_high_fade":
            # Should still be high but not too high (we missed the entry)
            if current_probability < Decimal("85"):
                return False  # Moved too much
            if current_probability > Decimal("97"):
                return False  # Too risky now
        
        elif signal.strategy == "extreme_low_value":
            if current_probability > Decimal("15"):
                return False
            if current_probability < Decimal("3"):
                return False
        
        elif signal.strategy == "musk_hype_fade":
            # Check if probability is still elevated
            if current_probability < signal.current_probability - Decimal("10"):
                return False  # Already faded
        
        # Price shouldn't have moved more than 5% from signal
        price_diff = abs(current_probability - signal.current_probability)
        if price_diff > Decimal("5"):
            logger.info(f"Price moved {price_diff:.1f}% from signal, skipping")
            return False
        
        return True
    
    def _get_execution_price(self, orderbook: Optional[Dict], side: str) -> Optional[Decimal]:
        """Get realistic execution price from orderbook"""
        if not orderbook:
            return None
        
        if side == "yes":
            asks = orderbook.get("asks", [])
            if asks:
                return Decimal(str(asks[0].get("price", 0))) * 100
        else:  # no
            bids = orderbook.get("bids", [])
            if bids:
                # For "no" side, we need to calculate from yes price
                yes_price = Decimal(str(bids[0].get("price", 0))) * 100
                return Decimal("100") - yes_price
        
        return None
    
    def _calculate_position_size(self, signal: Signal, execution_price: Decimal) -> Decimal:
        """Calculate final position size with safety limits"""
        
        # Start with suggested size
        size = signal.suggested_size
        
        # Apply position limit
        max_position = self.config.INITIAL_BANKROLL * (self.config.MAX_POSITION_SIZE_PCT / 100)
        size = min(size, max_position)
        
        # Adjust for execution price (can't buy more than we can afford)
        cost = size * (execution_price / 100)
        
        # Leave some buffer for fees/slippage
        max_cost = self.config.INITIAL_BANKROLL * Decimal("0.95")
        if cost > max_cost:
            size = max_cost / (execution_price / 100)
        
        return size.quantize(Decimal("0.01"))
    
    async def _simulate_execution(
        self, 
        signal: Signal, 
        execution_price: Decimal,
        size: Decimal,
        market: Dict
    ) -> Optional[Trade]:
        """
        Simulate trade execution
        In production, this would execute via CLOB API
        """
        try:
            # Create trade record
            trade = Trade(
                market_id=signal.market_id,
                market_slug=signal.market_slug,
                side=signal.suggested_side,
                entry_price=execution_price,
                size=size,
                signal_id=signal.id,
                status="open",
                strategy=signal.strategy,
                confidence=signal.confidence,
                agent_consensus=signal.agent_consensus_count,
                notes=f"Executed via {signal.strategy} strategy"
            )
            
            # Save to database
            trade.id = db_manager.save_trade(trade)
            
            return trade
            
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return None
    
    def _is_circuit_breaker_active(self) -> bool:
        """Check if circuit breaker should be active"""
        # Get recent performance
        recent_perf = db_manager.get_performance_history(days=1)
        
        if not recent_perf:
            return False
        
        latest = recent_perf[0]
        
        # Circuit breaker conditions
        if latest.current_drawdown > self.config.MAX_DRAWDOWN_PCT * Decimal("0.8"):
            logger.warning("Circuit breaker: Approaching max drawdown")
            return True
        
        if latest.win_rate < Decimal("30") and latest.total_trades > 5:
            logger.warning("Circuit breaker: Low win rate")
            return True
        
        return False
    
    async def check_and_close_positions(self, client: PolymarketClient):
        """Check open positions for exit conditions"""
        open_trades = db_manager.get_open_trades()
        
        for trade in open_trades:
            try:
                await self._evaluate_exit(trade, client)
            except Exception as e:
                logger.error(f"Error evaluating exit for {trade.id}: {e}")
    
    async def _evaluate_exit(self, trade: Trade, client: PolymarketClient):
        """Evaluate if position should be closed"""
        market = await client.get_market(trade.market_slug)
        if not market:
            return
        
        current_probability = Decimal(str(market.get("probabilityYes", 0))) * 100
        
        # Calculate unrealized P&L
        if trade.side == "yes":
            pnl_pct = ((current_probability - trade.entry_price) / trade.entry_price) * 100
        else:
            no_entry = Decimal("100") - trade.entry_price
            no_current = Decimal("100") - current_probability
            pnl_pct = ((no_current - no_entry) / no_entry) * 100
        
        # Exit conditions
        should_close = False
        close_reason = ""
        
        # 1. Take profit (20% gain)
        if pnl_pct >= Decimal("20"):
            should_close = True
            close_reason = "Take profit"
        
        # 2. Stop loss (15% loss)
        elif pnl_pct <= Decimal("-15"):
            should_close = True
            close_reason = "Stop loss"
        
        # 3. Extreme fade complete (probability normalized)
        elif trade.strategy == "extreme_high_fade":
            if current_probability < Decimal("70"):
                should_close = True
                close_reason = "Fade complete - probability normalized"
        
        elif trade.strategy == "extreme_low_value":
            if current_probability > Decimal("30"):
                should_close = True
                close_reason = "Value realized - probability normalized"
        
        # 4. Time-based exit (3 days max for most strategies)
        elif trade.strategy == "musk_hype_fade":
            days_held = (datetime.utcnow() - trade.created_at).days
            if days_held >= 3:
                should_close = True
                close_reason = "Time-based exit"
        
        if should_close:
            await self._close_position(trade, current_probability, close_reason)
    
    async def _close_position(self, trade: Trade, exit_price: Decimal, reason: str):
        """Close a position"""
        # Calculate final P&L
        if trade.side == "yes":
            pnl_pct = ((exit_price - trade.entry_price) / trade.entry_price) * 100
        else:
            no_entry = Decimal("100") - trade.entry_price
            no_exit = Decimal("100") - exit_price
            pnl_pct = ((no_exit - no_entry) / no_entry) * 100
        
        pnl_amount = trade.size * (pnl_pct / 100)
        
        # Update trade
        trade.exit_price = exit_price
        trade.pnl = pnl_amount
        trade.pnl_pct = pnl_pct
        trade.status = "closed"
        trade.closed_at = datetime.utcnow()
        trade.notes = f"{trade.notes} | Closed: {reason}"
        
        db_manager.update_trade(trade)
        
        # Update daily P&L
        self.daily_pnl += pnl_amount
        
        logger.info(f"Position closed: {trade.id} - P&L: {pnl_pct:.2f}% ({pnl_amount:.2f} USD) - {reason}")

# Singleton instance
execution_engine = ExecutionEngine()
