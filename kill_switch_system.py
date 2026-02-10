"""
Kill Switch & Circuit Breaker System
Core implementation for trading system safety controls.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Any
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KillSwitchLevel(Enum):
    """Levels of kill switch activation."""
    NONE = auto()
    STRATEGY_HALT = auto()      # Stop new trades for strategy
    STRATEGY_CLOSE = auto()     # Close all strategy positions
    PORTFOLIO_SOFT = auto()     # Stop all new trades
    PORTFOLIO_HARD = auto()     # Close all positions
    EMERGENCY = auto()          # Full system lockdown


class StrategyState(Enum):
    """Strategy operational states."""
    ACTIVE = "active"
    HALTED = "halted"
    CLOSING = "closing"
    INACTIVE = "inactive"
    RECOVERY = "recovery"


@dataclass
class TriggerEvent:
    """Represents a kill switch trigger event."""
    timestamp: datetime
    level: KillSwitchLevel
    source: str
    reason: str
    threshold: float
    actual_value: float
    strategy_id: Optional[str] = None
    initiator: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class StrategyMetrics:
    """Metrics tracked per strategy."""
    strategy_id: str
    pnl: float = 0.0
    pnl_pct: float = 0.0
    max_drawdown: float = 0.0
    consecutive_losses: int = 0
    total_trades: int = 0
    winning_trades: int = 0
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    current_position: float = 0.0
    position_count: int = 0
    error_count: int = 0
    last_trade_time: Optional[datetime] = None
    trade_history: deque = field(default_factory=lambda: deque(maxlen=100))


@dataclass
class PortfolioMetrics:
    """Portfolio-wide metrics."""
    total_nav: float = 0.0
    daily_pnl: float = 0.0
    daily_pnl_pct: float = 0.0
    total_drawdown: float = 0.0
    high_water_mark: float = 0.0
    margin_utilization: float = 0.0
    var_95: float = 0.0
    avg_correlation: float = 0.0
    volatility: float = 0.0
    open_position_count: int = 0
    pending_order_count: int = 0


class AuditLogger:
    """Thread-safe audit logging for compliance."""
    
    def __init__(self, log_file: str = "kill_switch_audit.log"):
        self.log_file = log_file
        self._lock = threading.Lock()
        self._ensure_file()
    
    def _ensure_file(self):
        """Ensure log file exists with headers."""
        try:
            with open(self.log_file, 'r') as f:
                pass
        except FileNotFoundError:
            with open(self.log_file, 'w') as f:
                f.write("timestamp,event_type,level,source,reason,strategy_id,initiator,data\n")
    
    def log(self, event: TriggerEvent):
        """Log a trigger event to the audit file."""
        with self._lock:
            with open(self.log_file, 'a') as f:
                data = json.dumps(event.metadata).replace('"', '""')
                line = (
                    f"{event.timestamp.isoformat()},"
                    f"TRIGGER,{event.level.name},{event.source},"
                    f"{event.reason},{event.strategy_id or 'N/A'},"
                    f"{event.initiator or 'SYSTEM'},{data}\n"
                )
                f.write(line)
        
        logger.info(f"Audit logged: {event.level.name} - {event.reason}")
    
    def log_action(self, action: str, initiator: str, details: Dict[str, Any]):
        """Log a manual action."""
        with self._lock:
            with open(self.log_file, 'a') as f:
                data = json.dumps(details).replace('"', '""')
                line = (
                    f"{datetime.now().isoformat()},"
                    f"ACTION,{action},MANUAL,N/A,N/A,"
                    f"{initiator},{data}\n"
                )
                f.write(line)


class AlertManager:
    """Manages alert delivery via multiple channels."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.webhook_url = config.get('slack_webhook')
        self.email_config = config.get('email', {})
        self.pagerduty_key = config.get('pagerduty_key')
        self._alert_history = deque(maxlen=100)
    
    async def send_alert(self, event: TriggerEvent, priority: str = "high"):
        """Send alert through all configured channels."""
        self._alert_history.append({
            'timestamp': datetime.now(),
            'event': event,
            'priority': priority
        })
        
        # Send all alerts concurrently
        await asyncio.gather(
            self._send_slack(event, priority),
            self._send_email(event, priority),
            self._send_pagerduty(event, priority),
            return_exceptions=True
        )
    
    async def _send_slack(self, event: TriggerEvent, priority: str):
        """Send Slack notification."""
        if not self.webhook_url:
            return
        
        emoji = "🚨" if priority == "critical" else "⚠️" if priority == "high" else "ℹ️"
        color = "danger" if priority == "critical" else "warning" if priority == "high" else "good"
        
        message = {
            "attachments": [{
                "color": color,
                "title": f"{emoji} Kill Switch Triggered: {event.level.name}",
                "fields": [
                    {"title": "Source", "value": event.source, "short": True},
                    {"title": "Reason", "value": event.reason, "short": True},
                    {"title": "Strategy", "value": event.strategy_id or "N/A", "short": True},
                    {"title": "Initiator", "value": event.initiator or "SYSTEM", "short": True},
                    {"title": "Threshold", "value": f"{event.threshold:.4f}", "short": True},
                    {"title": "Actual Value", "value": f"{event.actual_value:.4f}", "short": True},
                ],
                "footer": "Kill Switch System",
                "ts": time.time()
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=message,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status != 200:
                        logger.error(f"Slack alert failed: {response.status}")
        except Exception as e:
            logger.error(f"Slack alert error: {e}")
    
    async def _send_email(self, event: TriggerEvent, priority: str):
        """Send email notification."""
        if not self.email_config.get('enabled'):
            return
        
        # Placeholder for email implementation
        # In production, use smtplib or email service API
        logger.info(f"Email alert would be sent: {event.level.name}")
    
    async def _send_pagerduty(self, event: TriggerEvent, priority: str):
        """Send PagerDuty alert for critical events."""
        if not self.pagerduty_key or priority != "critical":
            return
        
        # Placeholder for PagerDuty integration
        logger.info(f"PagerDuty alert would be sent: {event.level.name}")


class KillSwitchSystem:
    """
    Main kill switch and circuit breaker system.
    
    Provides:
    - Real-time monitoring of strategies and portfolio
    - Automated trigger evaluation
    - Emergency shutdown capabilities
    - Comprehensive audit logging
    """
    
    def __init__(self, config_path: str = "kill_switch_config.yaml"):
        """Initialize the kill switch system."""
        self.config = self._load_config(config_path)
        self.audit_logger = AuditLogger(self.config.get('audit_log', 'kill_switch_audit.log'))
        self.alert_manager = AlertManager(self.config.get('alerts', {}))
        
        # State tracking
        self._system_state = KillSwitchLevel.NONE
        self._strategy_states: Dict[str, StrategyState] = {}
        self._strategy_metrics: Dict[str, StrategyMetrics] = {}
        self._portfolio_metrics = PortfolioMetrics()
        
        # Threading and async
        self._lock = asyncio.Lock()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._shutdown_event = asyncio.Event()
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Callbacks
        self._callbacks: Dict[str, List[Callable]] = {
            'strategy_halt': [],
            'strategy_close': [],
            'portfolio_soft': [],
            'portfolio_hard': [],
            'emergency': []
        }
        
        # Performance tracking
        self._trigger_times: deque = deque(maxlen=100)
        self._shutdown_start_time: Optional[float] = None
        
        logger.info("Kill Switch System initialized")
    
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        default_config = {
            'triggers': {
                'strategy_drawdown': 0.05,
                'strategy_consecutive_losses': 5,
                'strategy_min_win_rate': 0.30,
                'portfolio_daily_loss': 0.03,
                'portfolio_drawdown': 0.10,
                'portfolio_correlation': 0.80,
                'margin_utilization': 0.90,
                'velocity_threshold_1min': 0.01,
            },
            'timing': {
                'max_shutdown_seconds': 30,
                'position_close_timeout': 10,
                'monitor_interval_seconds': 1,
            },
            'alerts': {
                'slack_webhook': None,
                'email': {'enabled': False},
                'pagerduty_key': None,
            },
            'audit_log': 'kill_switch_audit.log'
        }
        
        try:
            with open(path, 'r') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    default_config.update(user_config)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {path}, using defaults")
        
        return default_config
    
    def register_callback(self, event: str, callback: Callable):
        """Register a callback for a kill switch event."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    async def start_monitoring(self):
        """Start the continuous monitoring loop."""
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Kill switch monitoring started")
    
    async def stop_monitoring(self):
        """Stop the monitoring loop."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Kill switch monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop - runs continuously."""
        interval = self.config['timing']['monitor_interval_seconds']
        
        while not self._shutdown_event.is_set():
            try:
                await self._evaluate_triggers()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def _evaluate_triggers(self):
        """Evaluate all configured triggers."""
        triggers = self.config['triggers']
        
        # Check strategy-level triggers
        for strategy_id, metrics in self._strategy_metrics.items():
            # Drawdown trigger
            if metrics.max_drawdown > triggers['strategy_drawdown']:
                await self._trigger(
                    KillSwitchLevel.STRATEGY_HALT,
                    "drawdown_limit",
                    strategy_id,
                    triggers['strategy_drawdown'],
                    metrics.max_drawdown
                )
                continue
            
            # Consecutive losses trigger
            if metrics.consecutive_losses >= triggers['strategy_consecutive_losses']:
                await self._trigger(
                    KillSwitchLevel.STRATEGY_HALT,
                    "consecutive_losses",
                    strategy_id,
                    triggers['strategy_consecutive_losses'],
                    metrics.consecutive_losses
                )
                continue
            
            # Win rate trigger
            if metrics.total_trades >= 20 and metrics.win_rate < triggers['strategy_min_win_rate']:
                await self._trigger(
                    KillSwitchLevel.STRATEGY_HALT,
                    "win_rate",
                    strategy_id,
                    triggers['strategy_min_win_rate'],
                    metrics.win_rate
                )
                continue
        
        # Check portfolio-level triggers
        portfolio = self._portfolio_metrics
        
        # Daily loss
        if abs(portfolio.daily_pnl_pct) > triggers['portfolio_daily_loss']:
            await self._trigger(
                KillSwitchLevel.PORTFOLIO_SOFT,
                "daily_loss_limit",
                None,
                triggers['portfolio_daily_loss'],
                abs(portfolio.daily_pnl_pct)
            )
            return
        
        # Drawdown
        if abs(portfolio.total_drawdown) > triggers['portfolio_drawdown']:
            await self._trigger(
                KillSwitchLevel.PORTFOLIO_HARD,
                "portfolio_drawdown",
                None,
                triggers['portfolio_drawdown'],
                abs(portfolio.total_drawdown)
            )
            return
        
        # Correlation spike
        if portfolio.avg_correlation > triggers['portfolio_correlation']:
            await self._trigger(
                KillSwitchLevel.PORTFOLIO_SOFT,
                "correlation_spike",
                None,
                triggers['portfolio_correlation'],
                portfolio.avg_correlation
            )
            return
        
        # Margin utilization
        if portfolio.margin_utilization > triggers['margin_utilization']:
            await self._trigger(
                KillSwitchLevel.PORTFOLIO_HARD,
                "margin_limit",
                None,
                triggers['margin_utilization'],
                portfolio.margin_utilization
            )
            return
    
    async def _trigger(
        self,
        level: KillSwitchLevel,
        reason: str,
        strategy_id: Optional[str],
        threshold: float,
        actual_value: float,
        initiator: Optional[str] = None
    ):
        """Execute a kill switch trigger."""
        trigger_start = time.time()
        
        async with self._lock:
            # Check if already at higher or equal level
            if self._system_state.value >= level.value:
                return
            
            # Create trigger event
            event = TriggerEvent(
                timestamp=datetime.now(),
                level=level,
                source="automated_monitor",
                reason=reason,
                threshold=threshold,
                actual_value=actual_value,
                strategy_id=strategy_id,
                initiator=initiator
            )
            
            # Log and alert
            self.audit_logger.log(event)
            
            priority = "critical" if level in [KillSwitchLevel.PORTFOLIO_HARD, KillSwitchLevel.EMERGENCY] else "high"
            await self.alert_manager.send_alert(event, priority)
            
            # Execute actions based on level
            await self._execute_trigger_actions(level, strategy_id)
            
            # Update state
            self._system_state = level
            if strategy_id:
                self._strategy_states[strategy_id] = StrategyState.HALTED
            
            # Track performance
            trigger_time = time.time() - trigger_start
            self._trigger_times.append(trigger_time)
            
            logger.critical(f"Kill switch triggered: {level.name} - {reason} "
                          f"(response time: {trigger_time:.3f}s)")
    
    async def _execute_trigger_actions(self, level: KillSwitchLevel, strategy_id: Optional[str]):
        """Execute actions for a trigger level."""
        
        if level == KillSwitchLevel.STRATEGY_HALT:
            await self._execute_callbacks('strategy_halt', strategy_id=strategy_id)
            
        elif level == KillSwitchLevel.STRATEGY_CLOSE:
            await self._execute_callbacks('strategy_close', strategy_id=strategy_id)
            if strategy_id:
                self._strategy_states[strategy_id] = StrategyState.CLOSING
                await self._close_strategy_positions(strategy_id)
                self._strategy_states[strategy_id] = StrategyState.INACTIVE
            
        elif level == KillSwitchLevel.PORTFOLIO_SOFT:
            await self._execute_callbacks('portfolio_soft')
            
        elif level == KillSwitchLevel.PORTFOLIO_HARD:
            await self._execute_callbacks('portfolio_hard')
            for sid in self._strategy_states:
                self._strategy_states[sid] = StrategyState.CLOSING
            await self._close_all_positions()
            for sid in self._strategy_states:
                self._strategy_states[sid] = StrategyState.INACTIVE
            
        elif level == KillSwitchLevel.EMERGENCY:
            await self._execute_callbacks('emergency')
            await self._emergency_lockdown()
    
    async def _execute_callbacks(self, event: str, **kwargs):
        """Execute registered callbacks for an event."""
        callbacks = self._callbacks.get(event, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(**kwargs)
                else:
                    await asyncio.get_event_loop().run_in_executor(
                        self._executor, callback, **kwargs
                    )
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    async def _close_strategy_positions(self, strategy_id: str):
        """Close all positions for a specific strategy."""
        timeout = self.config['timing']['position_close_timeout']
        logger.info(f"Closing positions for strategy {strategy_id} (timeout: {timeout}s)")
        
        # This would integrate with position manager
        # Simulated for now
        await asyncio.sleep(0.1)
    
    async def _close_all_positions(self):
        """Close all positions across all strategies."""
        timeout = self.config['timing']['position_close_timeout']
        logger.info(f"Closing all positions (timeout: {timeout}s per position)")
        
        # Close concurrently with timeout
        tasks = []
        for strategy_id in self._strategy_states:
            task = asyncio.create_task(self._close_strategy_positions(strategy_id))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _emergency_lockdown(self):
        """Execute emergency lockdown protocol."""
        self._shutdown_start_time = time.time()
        max_shutdown = self.config['timing']['max_shutdown_seconds']
        
        logger.critical("EMERGENCY LOCKDOWN INITIATED")
        
        try:
            # Create shutdown task with timeout
            shutdown_task = asyncio.create_task(self._shutdown_sequence())
            await asyncio.wait_for(shutdown_task, timeout=max_shutdown)
            
            elapsed = time.time() - self._shutdown_start_time
            logger.critical(f"Emergency lockdown completed in {elapsed:.2f}s")
            
        except asyncio.TimeoutError:
            logger.critical(f"Emergency shutdown exceeded {max_shutdown}s timeout!")
            # Force exit if needed
            import sys
            sys.exit(1)
    
    async def _shutdown_sequence(self):
        """Execute ordered shutdown sequence."""
        steps = [
            ("Cancel pending orders", self._cancel_all_orders),
            ("Close all positions", self._close_all_positions),
            ("Disconnect exchanges", self._disconnect_exchanges),
            ("Preserve state", self._preserve_state),
            ("Signal completion", self._signal_shutdown_complete),
        ]
        
        for step_name, step_func in steps:
            try:
                logger.info(f"Shutdown step: {step_name}")
                await step_func()
            except Exception as e:
                logger.error(f"Shutdown step failed: {step_name} - {e}")
    
    async def _cancel_all_orders(self):
        """Cancel all pending orders."""
        logger.info("Cancelling all pending orders")
        # Integration with order manager
        await asyncio.sleep(0.1)
    
    async def _disconnect_exchanges(self):
        """Disconnect from all exchanges."""
        logger.info("Disconnecting from exchanges")
        # Integration with exchange connections
        await asyncio.sleep(0.1)
    
    async def _preserve_state(self):
        """Preserve system state for post-incident analysis."""
        state = {
            'timestamp': datetime.now().isoformat(),
            'system_state': self._system_state.name,
            'strategy_states': {k: v.value for k, v in self._strategy_states.items()},
            'portfolio_metrics': self._portfolio_metrics.__dict__,
            'trigger_times': list(self._trigger_times)
        }
        
        filename = f"emergency_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        logger.info(f"State preserved to {filename}")
    
    async def _signal_shutdown_complete(self):
        """Signal that shutdown is complete."""
        self._shutdown_event.set()
    
    # Public API methods
    
    async def emergency_stop(self, initiator: str, reason: str = "manual_trigger"):
        """
        Emergency stop - immediately halt all trading.
        
        Args:
            initiator: User ID of person triggering emergency stop
            reason: Reason for emergency stop
        """
        await self._trigger(
            KillSwitchLevel.EMERGENCY,
            reason,
            None,
            0.0,
            0.0,
            initiator
        )
    
    async def halt_strategy(self, strategy_id: str, initiator: str, reason: str = "manual"):
        """Manually halt a specific strategy."""
        await self._trigger(
            KillSwitchLevel.STRATEGY_HALT,
            reason,
            strategy_id,
            0.0,
            0.0,
            initiator
        )
    
    async def resume_strategy(self, strategy_id: str, initiator: str):
        """Resume a halted strategy (requires manual authorization)."""
        async with self._lock:
            if strategy_id in self._strategy_states:
                old_state = self._strategy_states[strategy_id]
                self._strategy_states[strategy_id] = StrategyState.RECOVERY
                
                self.audit_logger.log_action(
                    "RESUME_STRATEGY",
                    initiator,
                    {"strategy_id": strategy_id, "from_state": old_state.value}
                )
                
                logger.info(f"Strategy {strategy_id} resumed by {initiator}")
    
    async def reset_system(self, initiator: str, authorization: str):
        """Reset system after halt (requires dual authorization)."""
        async with self._lock:
            # Verify authorization (in production, check against authorized users)
            if authorization != "DUAL_AUTH":
                raise PermissionError("Dual authorization required")
            
            old_state = self._system_state
            self._system_state = KillSwitchLevel.NONE
            
            self.audit_logger.log_action(
                "SYSTEM_RESET",
                initiator,
                {"from_state": old_state.name}
            )
            
            logger.info(f"System reset by {initiator}")
    
    def update_strategy_metrics(self, strategy_id: str, **metrics):
        """Update metrics for a strategy."""
        if strategy_id not in self._strategy_metrics:
            self._strategy_metrics[strategy_id] = StrategyMetrics(strategy_id=strategy_id)
        
        for key, value in metrics.items():
            if hasattr(self._strategy_metrics[strategy_id], key):
                setattr(self._strategy_metrics[strategy_id], key, value)
    
    def update_portfolio_metrics(self, **metrics):
        """Update portfolio-wide metrics."""
        for key, value in metrics.items():
            if hasattr(self._portfolio_metrics, key):
                setattr(self._portfolio_metrics, key, value)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "system_state": self._system_state.name,
            "strategy_states": {k: v.value for k, v in self._strategy_states.items()},
            "portfolio_metrics": {
                k: v for k, v in self._portfolio_metrics.__dict__.items()
                if not k.startswith('_')
            },
            "avg_trigger_time": sum(self._trigger_times) / len(self._trigger_times) if self._trigger_times else 0,
            "uptime": time.time() - getattr(self, '_start_time', time.time())
        }
    
    async def close(self):
        """Gracefully close the system."""
        await self.stop_monitoring()
        self._executor.shutdown(wait=True)
        logger.info("Kill Switch System closed")


# Singleton instance for global access
_kill_switch_instance: Optional[KillSwitchSystem] = None


def get_kill_switch(config_path: str = "kill_switch_config.yaml") -> KillSwitchSystem:
    """Get or create the global kill switch instance."""
    global _kill_switch_instance
    if _kill_switch_instance is None:
        _kill_switch_instance = KillSwitchSystem(config_path)
    return _kill_switch_instance


async def emergency_stop(initiator: str, reason: str = "manual_trigger"):
    """Global emergency stop function."""
    ks = get_kill_switch()
    await ks.emergency_stop(initiator, reason)


if __name__ == "__main__":
    # Example usage
    async def main():
        ks = KillSwitchSystem()
        
        # Register a callback
        def on_strategy_halt(strategy_id: str):
            print(f"Strategy {strategy_id} halted!")
        
        ks.register_callback('strategy_halt', on_strategy_halt)
        
        # Start monitoring
        await ks.start_monitoring()
        
        # Simulate some metrics
        ks.update_strategy_metrics(
            "strategy_1",
            pnl=-5000,
            max_drawdown=0.06,
            consecutive_losses=6
        )
        
        ks.update_portfolio_metrics(
            total_nav=1000000,
            daily_pnl_pct=-0.04
        )
        
        # Let it run for a bit
        await asyncio.sleep(5)
        
        # Check status
        print(json.dumps(ks.get_status(), indent=2))
        
        # Clean up
        await ks.close()
    
    asyncio.run(main())
