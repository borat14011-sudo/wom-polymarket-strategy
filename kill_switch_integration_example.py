"""
Example Integration: Kill Switch with Trading System
Shows how to integrate the kill switch system with your trading infrastructure.
"""

import asyncio
from typing import Dict, Any
from datetime import datetime

from kill_switch_system import (
    KillSwitchSystem,
    get_kill_switch,
    StrategyState
)


class TradingSystemIntegration:
    """
    Example integration showing how to connect the kill switch system
    with your trading system components.
    """
    
    def __init__(self):
        self.kill_switch = get_kill_switch()
        self.setup_callbacks()
    
    def setup_callbacks(self):
        """Register callbacks for kill switch events."""
        # Strategy-level callbacks
        self.kill_switch.register_callback('strategy_halt', self.on_strategy_halt)
        self.kill_switch.register_callback('strategy_close', self.on_strategy_close)
        
        # Portfolio-level callbacks
        self.kill_switch.register_callback('portfolio_soft', self.on_portfolio_soft)
        self.kill_switch.register_callback('portfolio_hard', self.on_portfolio_hard)
        self.kill_switch.register_callback('emergency', self.on_emergency)
    
    # Callback implementations
    
    async def on_strategy_halt(self, strategy_id: str):
        """Called when a strategy is halted."""
        print(f"[CALLBACK] Strategy {strategy_id} halted - stopping new signals")
        
        # Integration: Stop accepting new signals for this strategy
        await self._disable_strategy_signals(strategy_id)
        
        # Integration: Update strategy state in your database
        await self._update_strategy_state(strategy_id, StrategyState.HALTED)
        
        # Integration: Notify strategy engine
        await self._notify_strategy_engine(strategy_id, "HALT")
    
    async def on_strategy_close(self, strategy_id: str):
        """Called when a strategy positions need to be closed."""
        print(f"[CALLBACK] Closing all positions for strategy {strategy_id}")
        
        # Integration: Update state
        await self._update_strategy_state(strategy_id, StrategyState.CLOSING)
        
        # Integration: Get all positions for this strategy
        positions = await self._get_strategy_positions(strategy_id)
        
        # Integration: Submit market orders to close positions
        for position in positions:
            await self._submit_market_order(
                symbol=position['symbol'],
                side='SELL' if position['side'] == 'LONG' else 'BUY',
                quantity=position['quantity'],
                strategy_id=strategy_id
            )
    
    async def on_portfolio_soft(self, **kwargs):
        """Called when portfolio soft halt is triggered."""
        print("[CALLBACK] Portfolio soft halt - stopping all new trades")
        
        # Integration: Reject all new order requests
        await self._disable_all_signals()
        
        # Integration: Stop strategy schedulers
        await self._stop_strategy_schedulers()
        
        # Integration: Update trading mode
        await self._set_trading_mode("HALTED")
    
    async def on_portfolio_hard(self, **kwargs):
        """Called when portfolio hard halt is triggered."""
        print("[CALLBACK] Portfolio hard halt - closing all positions")
        
        # Integration: Cancel all pending orders
        await self._cancel_all_orders()
        
        # Integration: Get all positions
        all_positions = await self._get_all_positions()
        
        # Integration: Close positions concurrently with timeout
        close_tasks = []
        for position in all_positions:
            task = asyncio.create_task(
                self._submit_market_order(
                    symbol=position['symbol'],
                    side='SELL' if position['side'] == 'LONG' else 'BUY',
                    quantity=position['quantity']
                )
            )
            close_tasks.append(task)
        
        # Wait for all closes with 30 second timeout
        if close_tasks:
            await asyncio.wait_for(
                asyncio.gather(*close_tasks, return_exceptions=True),
                timeout=30
            )
    
    async def on_emergency(self, **kwargs):
        """Called when emergency lockdown is triggered."""
        print("[CALLBACK] EMERGENCY LOCKDOWN - Full system shutdown")
        
        # Integration: Immediately cancel all orders
        await self._emergency_cancel_all_orders()
        
        # Integration: Force close all positions at market
        await self._force_close_all_positions()
        
        # Integration: Disconnect from exchanges
        await self._disconnect_exchanges()
        
        # Integration: Preserve state for forensic analysis
        await self._preserve_trading_state()
        
        # Integration: Stop all background processes
        await self._stop_all_processes()
    
    # Mock integration methods (replace with your actual implementations)
    
    async def _disable_strategy_signals(self, strategy_id: str):
        """Disable signal generation for a strategy."""
        # Your implementation here
        print(f"  -> Disabled signals for {strategy_id}")
    
    async def _update_strategy_state(self, strategy_id: str, state: StrategyState):
        """Update strategy state in database."""
        # Your implementation here
        print(f"  -> Updated {strategy_id} state to {state.value}")
    
    async def _notify_strategy_engine(self, strategy_id: str, action: str):
        """Notify strategy engine of state change."""
        # Your implementation here
        print(f"  -> Notified strategy engine: {action} for {strategy_id}")
    
    async def _get_strategy_positions(self, strategy_id: str) -> list:
        """Get all positions for a strategy."""
        # Your implementation here
        return [
            {'symbol': 'AAPL', 'side': 'LONG', 'quantity': 100},
            {'symbol': 'GOOGL', 'side': 'SHORT', 'quantity': 50}
        ]
    
    async def _submit_market_order(self, symbol: str, side: str, quantity: float, strategy_id: str = None):
        """Submit a market order."""
        # Your implementation here
        print(f"  -> Market order: {side} {quantity} {symbol}")
    
    async def _disable_all_signals(self):
        """Disable all signal generation."""
        # Your implementation here
        print("  -> All signals disabled")
    
    async def _stop_strategy_schedulers(self):
        """Stop strategy schedulers."""
        # Your implementation here
        print("  -> Strategy schedulers stopped")
    
    async def _set_trading_mode(self, mode: str):
        """Set overall trading mode."""
        # Your implementation here
        print(f"  -> Trading mode set to {mode}")
    
    async def _cancel_all_orders(self):
        """Cancel all pending orders."""
        # Your implementation here
        print("  -> All pending orders cancelled")
    
    async def _get_all_positions(self) -> list:
        """Get all portfolio positions."""
        # Your implementation here
        return [
            {'symbol': 'AAPL', 'side': 'LONG', 'quantity': 100},
            {'symbol': 'GOOGL', 'side': 'SHORT', 'quantity': 50},
            {'symbol': 'MSFT', 'side': 'LONG', 'quantity': 200}
        ]
    
    async def _emergency_cancel_all_orders(self):
        """Emergency cancel all orders (no timeout)."""
        # Your implementation here
        print("  -> EMERGENCY: All orders cancelled")
    
    async def _force_close_all_positions(self):
        """Force close all positions (aggressive)."""
        # Your implementation here
        print("  -> EMERGENCY: All positions force closed")
    
    async def _disconnect_exchanges(self):
        """Disconnect from all exchanges."""
        # Your implementation here
        print("  -> EMERGENCY: Exchange connections terminated")
    
    async def _preserve_trading_state(self):
        """Preserve trading state for analysis."""
        # Your implementation here
        print("  -> EMERGENCY: State preserved to file")
    
    async def _stop_all_processes(self):
        """Stop all background processes."""
        # Your implementation here
        print("  -> EMERGENCY: All processes stopped")
    
    # Metric update methods
    
    async def update_metrics_loop(self):
        """Continuously update metrics from your trading system."""
        while True:
            try:
                # Get metrics from your trading system
                for strategy_id in ["strategy_1", "strategy_2", "strategy_3"]:
                    metrics = await self._fetch_strategy_metrics(strategy_id)
                    self.kill_switch.update_strategy_metrics(
                        strategy_id=strategy_id,
                        **metrics
                    )
                
                # Update portfolio metrics
                portfolio_metrics = await self._fetch_portfolio_metrics()
                self.kill_switch.update_portfolio_metrics(**portfolio_metrics)
                
                await asyncio.sleep(1)  # Update every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Metrics update error: {e}")
                await asyncio.sleep(5)
    
    async def _fetch_strategy_metrics(self, strategy_id: str) -> Dict[str, Any]:
        """Fetch metrics from your strategy."""
        # Your implementation here
        return {
            'pnl': 1000.0,
            'pnl_pct': 0.02,
            'max_drawdown': 0.03,
            'consecutive_losses': 2,
            'total_trades': 50,
            'winning_trades': 28,
            'win_rate': 0.56,
            'sharpe_ratio': 1.2,
            'current_position': 50000.0,
            'position_count': 3
        }
    
    async def _fetch_portfolio_metrics(self) -> Dict[str, Any]:
        """Fetch portfolio-wide metrics."""
        # Your implementation here
        return {
            'total_nav': 1000000.0,
            'daily_pnl': -25000.0,
            'daily_pnl_pct': -0.025,
            'total_drawdown': -0.03,
            'high_water_mark': 1030000.0,
            'margin_utilization': 0.45,
            'var_95': 0.02,
            'avg_correlation': 0.3,
            'volatility': 0.15,
            'open_position_count': 10,
            'pending_order_count': 3
        }


class OrderValidator:
    """
    Example: Validate orders against kill switch state before submission.
    """
    
    def __init__(self):
        self.kill_switch = get_kill_switch()
    
    async def validate_order(self, order: Dict[str, Any]) -> bool:
        """Check if order is allowed given current kill switch state."""
        status = self.kill_switch.get_status()
        system_state = status['system_state']
        
        # Reject all orders if emergency or hard halt
        if system_state in ['EMERGENCY', 'PORTFOLIO_HARD']:
            raise Exception(f"Order rejected: System in {system_state} state")
        
        # Reject new positions if soft halt (allow exits)
        if system_state == 'PORTFOLIO_SOFT':
            if order.get('side') == 'BUY' and order.get('quantity', 0) > 0:
                raise Exception("Order rejected: New positions not allowed during soft halt")
        
        # Check strategy-level state
        strategy_id = order.get('strategy_id')
        if strategy_id:
            strategy_state = status['strategy_states'].get(strategy_id)
            if strategy_state in ['halted', 'closing', 'inactive']:
                raise Exception(f"Order rejected: Strategy {strategy_id} is {strategy_state}")
        
        return True


async def example_usage():
    """Example of how to use the kill switch system."""
    
    # Initialize trading system with kill switch integration
    trading_system = TradingSystemIntegration()
    
    # Start the kill switch monitoring
    await trading_system.kill_switch.start_monitoring()
    
    # Start metrics update loop
    metrics_task = asyncio.create_task(trading_system.update_metrics_loop())
    
    print("\n" + "="*60)
    print("Kill Switch System Demo")
    print("="*60 + "\n")
    
    # Simulate some trading activity
    print("1. Simulating normal trading...")
    await asyncio.sleep(2)
    
    # Show status
    status = trading_system.kill_switch.get_status()
    print(f"   System state: {status['system_state']}")
    
    # Simulate a strategy issue
    print("\n2. Simulating strategy drawdown...")
    trading_system.kill_switch.update_strategy_metrics(
        "strategy_1",
        pnl=-50000,
        pnl_pct=-0.10,
        max_drawdown=0.06,  # Above 5% threshold
        consecutive_losses=6  # Above 5 threshold
    )
    await asyncio.sleep(2)
    
    # Show updated status
    status = trading_system.kill_switch.get_status()
    print(f"   System state: {status['system_state']}")
    print(f"   Strategy states: {status['strategy_states']}")
    
    # Simulate portfolio issue
    print("\n3. Simulating portfolio drawdown...")
    trading_system.kill_switch.update_portfolio_metrics(
        total_nav=900000,
        daily_pnl=-100000,
        daily_pnl_pct=-0.11,  # Above 10% threshold
        total_drawdown=-0.11
    )
    await asyncio.sleep(2)
    
    # Show final status
    status = trading_system.kill_switch.get_status()
    print(f"   System state: {status['system_state']}")
    
    # Manual emergency stop example
    print("\n4. Demonstrating manual emergency stop...")
    await trading_system.kill_switch.emergency_stop(
        initiator="demo_user",
        reason="manual_test"
    )
    await asyncio.sleep(2)
    
    # Final status
    status = trading_system.kill_switch.get_status()
    print(f"   Final system state: {status['system_state']}")
    
    # Cleanup
    metrics_task.cancel()
    try:
        await metrics_task
    except asyncio.CancelledError:
        pass
    
    await trading_system.kill_switch.close()
    
    print("\n" + "="*60)
    print("Demo completed")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(example_usage())
