"""
Performance Tracking System
Real-time ROI and risk monitoring
"""
import asyncio
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging
from collections import deque

from database import Trade, PerformanceMetrics, db_manager
from config import TRADING_CONFIG

logger = logging.getLogger(__name__)

class PerformanceTracker:
    """Tracks and analyzes trading performance"""
    
    def __init__(self):
        self.config = TRADING_CONFIG
        self.price_history: Dict[str, deque] = {}  # For Sharpe calculation
        self.equity_curve: deque = deque(maxlen=252)  # Daily equity values
        self.trade_history: deque = deque(maxlen=1000)  # Recent trades
    
    async def update_metrics(self):
        """Update all performance metrics"""
        try:
            # Get all trades
            all_trades = db_manager.get_trades_by_date_range(
                datetime.utcnow() - timedelta(days=365),
                datetime.utcnow()
            )
            
            # Calculate metrics
            metrics = self._calculate_metrics(all_trades)
            
            # Save to database
            db_manager.save_performance(metrics)
            
            logger.info(f"Performance updated: Win rate {metrics.win_rate:.1f}%, ROI: {metrics.roi_all_time:.2f}%")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
            return None
    
    def _calculate_metrics(self, trades: List[Trade]) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        
        # Get closed trades
        closed_trades = [t for t in trades if t.status == "closed"]
        open_trades = [t for t in trades if t.status == "open"]
        
        # Basic counts
        total_trades = len(closed_trades)
        winning_trades = [t for t in closed_trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in closed_trades if t.pnl and t.pnl <= 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        
        # Win rate
        win_rate = (Decimal(win_count) / Decimal(total_trades) * 100) if total_trades > 0 else Decimal("0")
        
        # P&L calculations
        total_profit = sum(t.pnl for t in winning_trades if t.pnl)
        total_loss = sum(t.pnl for t in losing_trades if t.pnl)
        
        avg_profit = (total_profit / win_count) if win_count > 0 else Decimal("0")
        avg_loss = (total_loss / loss_count) if loss_count > 0 else Decimal("0")
        
        # Profit factor
        profit_factor = abs(total_profit / total_loss) if total_loss != 0 else Decimal("999")
        
        # Calculate returns for Sharpe ratio
        daily_returns = self._calculate_daily_returns(closed_trades)
        sharpe_ratio = self._calculate_sharpe_ratio(daily_returns)
        
        # Drawdown calculation
        max_drawdown, current_drawdown = self._calculate_drawdown(closed_trades)
        
        # ROI calculations
        roi_daily = self._calculate_roi_period(closed_trades, 1)
        roi_weekly = self._calculate_roi_period(closed_trades, 7)
        roi_monthly = self._calculate_roi_period(closed_trades, 30)
        roi_all_time = self._calculate_roi_all_time(closed_trades)
        
        # Current bankroll
        bankroll = self._calculate_bankroll(closed_trades)
        exposure = sum(t.size for t in open_trades)
        
        return PerformanceMetrics(
            total_trades=total_trades,
            winning_trades=win_count,
            losing_trades=loss_count,
            win_rate=win_rate,
            avg_profit=avg_profit,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            current_drawdown=current_drawdown,
            roi_daily=roi_daily,
            roi_weekly=roi_weekly,
            roi_monthly=roi_monthly,
            roi_all_time=roi_all_time,
            bankroll=bankroll,
            exposure=exposure,
            open_positions=len(open_trades)
        )
    
    def _calculate_daily_returns(self, trades: List[Trade]) -> List[Decimal]:
        """Calculate daily returns from trades"""
        if not trades:
            return []
        
        # Group trades by day
        daily_pnl: Dict[datetime.date, Decimal] = {}
        
        for trade in trades:
            if trade.closed_at and trade.pnl:
                day = trade.closed_at.date()
                daily_pnl[day] = daily_pnl.get(day, Decimal("0")) + trade.pnl
        
        # Sort by date and calculate returns
        sorted_days = sorted(daily_pnl.keys())
        returns = []
        
        for i, day in enumerate(sorted_days):
            if i == 0:
                returns.append(Decimal("0"))
            else:
                prev_value = self.config.INITIAL_BANKROLL + sum(
                    daily_pnl[d] for d in sorted_days[:i]
                )
                if prev_value > 0:
                    daily_return = (daily_pnl[day] / prev_value) * 100
                    returns.append(daily_return)
        
        return returns
    
    def _calculate_sharpe_ratio(self, returns: List[Decimal], risk_free_rate: Decimal = Decimal("0.02")) -> Decimal:
        """Calculate annualized Sharpe ratio"""
        if len(returns) < 10:
            return Decimal("0")
        
        # Calculate average return
        avg_return = sum(returns) / len(returns)
        
        # Calculate standard deviation
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance.sqrt()
        
        if std_dev == 0:
            return Decimal("0")
        
        # Annualize (assuming 252 trading days)
        sharpe = ((avg_return * 252) - risk_free_rate) / (std_dev * (252 ** Decimal("0.5")))
        
        return sharpe
    
    def _calculate_drawdown(self, trades: List[Trade]) -> Tuple[Decimal, Decimal]:
        """Calculate max and current drawdown"""
        if not trades:
            return Decimal("0"), Decimal("0")
        
        # Sort trades by close date
        sorted_trades = sorted(
            [t for t in trades if t.closed_at and t.pnl],
            key=lambda x: x.closed_at
        )
        
        peak = self.config.INITIAL_BANKROLL
        current_value = self.config.INITIAL_BANKROLL
        max_drawdown = Decimal("0")
        
        for trade in sorted_trades:
            current_value += trade.pnl
            
            if current_value > peak:
                peak = current_value
            
            drawdown = ((peak - current_value) / peak) * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        current_drawdown = ((peak - current_value) / peak) * 100 if peak > 0 else Decimal("0")
        
        return max_drawdown, current_drawdown
    
    def _calculate_roi_period(self, trades: List[Trade], days: int) -> Decimal:
        """Calculate ROI for a specific period"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        period_trades = [
            t for t in trades 
            if t.closed_at and t.closed_at >= cutoff and t.pnl
        ]
        
        total_pnl = sum(t.pnl for t in period_trades)
        
        # Approximate starting capital
        starting_capital = self.config.INITIAL_BANKROLL
        
        return (total_pnl / starting_capital) * 100 if starting_capital > 0 else Decimal("0")
    
    def _calculate_roi_all_time(self, trades: List[Trade]) -> Decimal:
        """Calculate all-time ROI"""
        total_pnl = sum(t.pnl for t in trades if t.pnl)
        return (total_pnl / self.config.INITIAL_BANKROLL) * 100
    
    def _calculate_bankroll(self, trades: List[Trade]) -> Decimal:
        """Calculate current bankroll"""
        total_pnl = sum(t.pnl for t in trades if t.pnl)
        return self.config.INITIAL_BANKROLL + total_pnl
    
    def get_strategy_performance(self, trades: List[Trade]) -> Dict[str, Dict]:
        """Get performance breakdown by strategy"""
        closed_trades = [t for t in trades if t.status == "closed"]
        
        strategies = {}
        for trade in closed_trades:
            strategy = trade.strategy or "unknown"
            
            if strategy not in strategies:
                strategies[strategy] = {
                    "trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "total_pnl": Decimal("0"),
                    "avg_pnl": Decimal("0")
                }
            
            s = strategies[strategy]
            s["trades"] += 1
            
            if trade.pnl:
                s["total_pnl"] += trade.pnl
                if trade.pnl > 0:
                    s["wins"] += 1
                else:
                    s["losses"] += 1
        
        # Calculate averages
        for strategy, data in strategies.items():
            if data["trades"] > 0:
                data["win_rate"] = (Decimal(data["wins"]) / Decimal(data["trades"])) * 100
                data["avg_pnl"] = data["total_pnl"] / data["trades"]
            else:
                data["win_rate"] = Decimal("0")
                data["avg_pnl"] = Decimal("0")
        
        return strategies
    
    def get_recent_stats(self, days: int = 7) -> Dict:
        """Get statistics for recent period"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        all_trades = db_manager.get_trades_by_date_range(cutoff, datetime.utcnow())
        closed_trades = [t for t in all_trades if t.status == "closed"]
        
        if not closed_trades:
            return {
                "period_days": days,
                "trades": 0,
                "win_rate": Decimal("0"),
                "total_pnl": Decimal("0"),
                "avg_trade": Decimal("0")
            }
        
        wins = sum(1 for t in closed_trades if t.pnl and t.pnl > 0)
        total_pnl = sum(t.pnl for t in closed_trades if t.pnl)
        
        return {
            "period_days": days,
            "trades": len(closed_trades),
            "win_rate": (Decimal(wins) / Decimal(len(closed_trades))) * 100,
            "total_pnl": total_pnl,
            "avg_trade": total_pnl / len(closed_trades)
        }
    
    def generate_performance_report(self) -> str:
        """Generate formatted performance report"""
        metrics = db_manager.get_performance_history(days=1)
        if not metrics:
            return "No performance data available"
        
        latest = metrics[0]
        
        report = f"""
╔════════════════════════════════════════════════════════╗
║         PATS PERFORMANCE REPORT - {latest.date}         ║
╠════════════════════════════════════════════════════════╣
║ OVERALL STATISTICS                                     ║
║ ─────────────────                                      ║
║  Total Trades:     {latest.total_trades:>5}                              ║
║  Win Rate:         {latest.win_rate:>5.1f}%                            ║
║  Profit Factor:    {latest.profit_factor:>5.2f}                             ║
║  Sharpe Ratio:     {latest.sharpe_ratio:>5.2f}                             ║
║  Max Drawdown:     {latest.max_drawdown:>5.1f}%                            ║
╠════════════════════════════════════════════════════════╣
║ RETURNS                                                ║
║ ───────                                                ║
║  Daily:   {latest.roi_daily:>7.2f}%                                    ║
║  Weekly:  {latest.roi_weekly:>7.2f}%                                    ║
║  Monthly: {latest.roi_monthly:>7.2f}%                                    ║
║  All-Time:{latest.roi_all_time:>7.2f}%                                    ║
╠════════════════════════════════════════════════════════╣
║ CURRENT STATUS                                         ║
║ ──────────────                                         ║
║  Bankroll:      ${latest.bankroll:>10.2f}                       ║
║  Exposure:      ${latest.exposure:>10.2f}                       ║
║  Open Positions: {latest.open_positions:>3}                               ║
╚════════════════════════════════════════════════════════╝
"""
        return report
    
    def check_alerts(self) -> List[str]:
        """Check for performance alerts"""
        alerts = []
        
        metrics = db_manager.get_performance_history(days=1)
        if not metrics:
            return alerts
        
        latest = metrics[0]
        
        # Check drawdown
        if latest.max_drawdown > self.config.MAX_DRAWDOWN_PCT * Decimal("0.7"):
            alerts.append(f"⚠️ WARNING: Drawdown at {latest.max_drawdown:.1f}% (limit: {self.config.MAX_DRAWDOWN_PCT}%)")
        
        # Check Sharpe ratio
        if latest.sharpe_ratio < self.config.SHARPE_RATIO_MIN:
            alerts.append(f"⚠️ WARNING: Sharpe ratio {latest.sharpe_ratio:.2f} below minimum {self.config.SHARPE_RATIO_MIN}")
        
        # Check win rate
        if latest.total_trades > 10 and latest.win_rate < Decimal("40"):
            alerts.append(f"⚠️ WARNING: Win rate {latest.win_rate:.1f}% below threshold")
        
        # Check recent performance
        recent = self.get_recent_stats(days=7)
        if recent["trades"] >= 5 and recent["total_pnl"] < 0:
            alerts.append(f"⚠️ WARNING: Negative P&L over last 7 days: ${recent['total_pnl']:.2f}")
        
        return alerts

# Singleton instance
performance_tracker = PerformanceTracker()
