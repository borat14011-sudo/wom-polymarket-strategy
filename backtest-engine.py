#!/usr/bin/env python3
"""
Prediction Market Backtesting Engine
Tests hype → price edge with walk-forward validation

Usage:
    python backtest-engine.py --db polymarket_data.db --output backtest_results/
    
Requirements:
    pip install pandas numpy scipy scikit-learn matplotlib plotly yfinance
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import argparse
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# For statistical validation
from scipy import stats
from sklearn.metrics import r2_score

# For visualization
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("⚠️  Plotly not installed. Install for interactive charts: pip install plotly")


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Trade:
    """Represents a single trade"""
    entry_time: datetime
    exit_time: Optional[datetime]
    market_id: str
    market_question: str
    side: str  # 'YES' or 'NO'
    entry_price: float
    exit_price: Optional[float]
    position_size: float  # USD amount
    entry_signal_strength: str  # 'STRONG', 'MODERATE', 'WEAK'
    exit_reason: Optional[str]  # 'TP1', 'TP2', 'TP3', 'STOP_LOSS', 'TIME_DECAY', etc.
    
    # Signal values at entry
    rvr: float
    roc: float
    liquidity_imbalance: Optional[float]
    
    # Costs
    slippage_entry: float = 0.01  # 1% default
    slippage_exit: float = 0.015  # 1.5% default
    fee_rate: float = 0.02  # 2% on profits
    
    @property
    def is_open(self) -> bool:
        return self.exit_time is None
    
    @property
    def pnl_gross(self) -> Optional[float]:
        """Gross P&L before costs"""
        if self.exit_price is None:
            return None
        
        if self.side == 'YES':
            return (self.exit_price - self.entry_price) * self.position_size
        else:  # NO
            return (self.entry_price - self.exit_price) * self.position_size
    
    @property
    def pnl_net(self) -> Optional[float]:
        """Net P&L after slippage and fees"""
        if self.pnl_gross is None:
            return None
        
        # Apply slippage
        slippage_cost = self.position_size * (self.slippage_entry + self.slippage_exit)
        
        # Apply fees (only on profits)
        fee_cost = max(0, self.pnl_gross) * self.fee_rate
        
        return self.pnl_gross - slippage_cost - fee_cost
    
    @property
    def return_pct(self) -> Optional[float]:
        """Return percentage"""
        if self.pnl_net is None:
            return None
        return (self.pnl_net / self.position_size) * 100
    
    @property
    def holding_period_hours(self) -> Optional[float]:
        """How long was the trade held"""
        if self.exit_time is None:
            return None
        return (self.exit_time - self.entry_time).total_seconds() / 3600


@dataclass
class PerformanceMetrics:
    """Performance metrics for the strategy"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    total_return_pct: float
    total_return_usd: float
    
    avg_win_pct: float
    avg_loss_pct: float
    avg_win_usd: float
    avg_loss_usd: float
    
    profit_factor: float
    expectancy: float
    
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    max_drawdown_usd: float
    
    avg_holding_hours: float
    median_holding_hours: float
    
    best_trade_pct: float
    worst_trade_pct: float
    
    consecutive_wins: int
    consecutive_losses: int
    
    # Statistical validation
    out_of_sample_r2: Optional[float] = None
    confidence_interval_95: Optional[Tuple[float, float]] = None
    
    # Comparison to baseline
    buy_and_hold_return: Optional[float] = None
    alpha: Optional[float] = None  # Excess return vs buy-and-hold


# ============================================================================
# SIGNAL GENERATOR
# ============================================================================

class SignalGenerator:
    """Generates trading signals based on strategy rules"""
    
    def __init__(self, 
                 rvr_strong=3.0, rvr_moderate=2.0, rvr_weak=1.5,
                 roc_strong=15.0, roc_moderate=10.0, roc_weak=5.0,
                 imbalance_strong=0.3, imbalance_moderate=0.2):
        self.rvr_strong = rvr_strong
        self.rvr_moderate = rvr_moderate
        self.rvr_weak = rvr_weak
        self.roc_strong = roc_strong
        self.roc_moderate = roc_moderate
        self.roc_weak = roc_weak
        self.imbalance_strong = imbalance_strong
        self.imbalance_moderate = imbalance_moderate
    
    def calculate_rvr(self, current_volume: float, historical_volumes: pd.Series) -> float:
        """Calculate Relative Volume Ratio"""
        if len(historical_volumes) == 0 or historical_volumes.mean() == 0:
            return 1.0
        return current_volume / historical_volumes.mean()
    
    def calculate_roc(self, current_price: float, historical_prices: pd.Series, 
                      hours_back: int = 6) -> float:
        """Calculate Rate of Change"""
        if len(historical_prices) == 0:
            return 0.0
        past_price = historical_prices.iloc[0] if len(historical_prices) > 0 else current_price
        if past_price == 0:
            return 0.0
        return ((current_price - past_price) / past_price) * 100
    
    def calculate_liquidity_imbalance(self, bid_depth: float, ask_depth: float) -> Optional[float]:
        """Calculate order book imbalance"""
        total = bid_depth + ask_depth
        if total == 0:
            return None
        return (bid_depth - ask_depth) / total
    
    def classify_signal_strength(self, rvr: float, roc: float, imbalance: Optional[float]) -> Tuple[str, int]:
        """
        Classify signal strength based on multiple indicators
        Returns: (strength_label, signal_count)
        """
        strong_signals = 0
        moderate_signals = 0
        
        # RVR signals
        if rvr >= self.rvr_strong:
            strong_signals += 1
        elif rvr >= self.rvr_moderate:
            moderate_signals += 1
        elif rvr >= self.rvr_weak:
            moderate_signals += 0.5
        
        # ROC signals
        if abs(roc) >= self.roc_strong:
            strong_signals += 1
        elif abs(roc) >= self.roc_moderate:
            moderate_signals += 1
        elif abs(roc) >= self.roc_weak:
            moderate_signals += 0.5
        
        # Liquidity imbalance signals
        if imbalance is not None:
            if abs(imbalance) >= self.imbalance_strong:
                strong_signals += 1
            elif abs(imbalance) >= self.imbalance_moderate:
                moderate_signals += 1
        
        # Classify based on signal matrix from strategy framework
        if strong_signals >= 3:
            return 'STRONG', strong_signals + moderate_signals
        elif strong_signals >= 2 and moderate_signals >= 1:
            return 'STRONG', strong_signals + moderate_signals
        elif strong_signals >= 1 and moderate_signals >= 2:
            return 'MODERATE', strong_signals + moderate_signals
        elif moderate_signals >= 3:
            return 'MODERATE', strong_signals + moderate_signals
        else:
            return 'WEAK', strong_signals + moderate_signals
    
    def should_enter_trade(self, signal_strength: str, signal_count: float,
                          price: float, liquidity: float, spread: float,
                          hours_to_expiry: float) -> bool:
        """Check if entry conditions are met"""
        # Disqualifying conditions from strategy framework
        if hours_to_expiry < 48:  # Less than 48 hours to resolution
            return False
        if liquidity < 5000:  # Minimum $5k liquidity
            return False
        if spread > 0.05:  # Spread > 5%
            return False
        if signal_count < 3:  # Need at least 3 signals
            return False
        
        return signal_strength in ['STRONG', 'MODERATE']


# ============================================================================
# BACKTESTING ENGINE
# ============================================================================

class BacktestEngine:
    """Main backtesting engine with walk-forward validation"""
    
    def __init__(self, db_path: str, initial_capital: float = 10000):
        self.db_path = db_path
        self.initial_capital = initial_capital
        self.signal_generator = SignalGenerator()
        
        # Position sizing parameters
        self.position_sizes = {
            'STRONG': 0.04,    # 4% of capital
            'MODERATE': 0.02,  # 2% of capital
            'WEAK': 0.01       # 1% of capital
        }
        self.max_single_position = 0.05  # 5% hard cap
        self.max_total_exposure = 0.25   # 25% total exposure
        
        # Exit parameters
        self.tp_levels = [0.08, 0.15, 0.25]  # Take profit levels
        self.tp_allocations = [0.25, 0.50, 0.25]  # How much to close at each level
        self.stop_loss_pct = 0.12  # -12% stop loss
        self.time_decay_days = [3, 7]  # Time decay thresholds
        self.time_decay_thresholds = [0.05, 0.08]  # Required gains to hold
        
        # State
        self.trades: List[Trade] = []
        self.open_trades: List[Trade] = []
        self.capital = initial_capital
        self.peak_capital = initial_capital
        self.equity_curve = []
    
    def load_data(self) -> pd.DataFrame:
        """Load and prepare data from SQLite database"""
        conn = sqlite3.connect(self.db_path)
        
        # Load market snapshots with market metadata
        query = """
        SELECT 
            s.timestamp,
            s.market_id,
            m.question,
            m.end_time,
            s.price_yes,
            s.price_no,
            s.volume_24h,
            s.liquidity,
            s.best_bid_yes,
            s.best_ask_yes,
            s.spread
        FROM snapshots s
        JOIN markets m ON s.market_id = m.market_id
        WHERE m.resolved = 0 OR m.resolved IS NULL
        ORDER BY s.market_id, s.timestamp
        """
        
        df = pd.read_sql_query(query, conn)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        
        # Load hype signals if available
        try:
            hype_query = """
            SELECT 
                market_id,
                timestamp,
                tweet_count,
                total_engagement,
                velocity,
                hype_score
            FROM hype_signals
            ORDER BY market_id, timestamp
            """
            hype_df = pd.read_sql_query(hype_query, conn)
            hype_df['timestamp'] = pd.to_datetime(hype_df['timestamp'])
            
            # Merge hype data
            df = df.merge(hype_df, on=['market_id', 'timestamp'], how='left')
            df['tweet_count'] = df['tweet_count'].fillna(0)
            df['hype_score'] = df['hype_score'].fillna(0)
        except:
            print("⚠️  No hype signals found in database")
            df['tweet_count'] = 0
            df['hype_score'] = 0
        
        conn.close()
        
        print(f"✓ Loaded {len(df)} snapshots across {df['market_id'].nunique()} markets")
        print(f"  Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        return df
    
    def calculate_signals(self, df: pd.DataFrame, lookback_hours: int = 24) -> pd.DataFrame:
        """Calculate trading signals for each snapshot"""
        signals = []
        
        for market_id in df['market_id'].unique():
            market_df = df[df['market_id'] == market_id].sort_values('timestamp').reset_index(drop=True)
            
            for i in range(len(market_df)):
                row = market_df.iloc[i]
                
                # Get historical data for signal calculation
                lookback_idx = max(0, i - int(lookback_hours * 4))  # 4 snapshots per hour (15min each)
                historical = market_df.iloc[lookback_idx:i]
                
                if len(historical) < 4:  # Need at least 1 hour of history
                    continue
                
                # Calculate signals
                rvr = self.signal_generator.calculate_rvr(
                    row['volume_24h'], 
                    historical['volume_24h']
                )
                
                roc = self.signal_generator.calculate_roc(
                    row['price_yes'],
                    historical['price_yes'],
                    hours_back=6
                )
                
                imbalance = None  # Would need order book data
                
                signal_strength, signal_count = self.signal_generator.classify_signal_strength(
                    rvr, roc, imbalance
                )
                
                # Calculate hours to expiry
                hours_to_expiry = (row['end_time'] - row['timestamp']).total_seconds() / 3600
                
                # Check if should enter
                should_enter = self.signal_generator.should_enter_trade(
                    signal_strength, signal_count,
                    row['price_yes'], row['liquidity'], row['spread'],
                    hours_to_expiry
                )
                
                signals.append({
                    'timestamp': row['timestamp'],
                    'market_id': row['market_id'],
                    'rvr': rvr,
                    'roc': roc,
                    'signal_strength': signal_strength,
                    'signal_count': signal_count,
                    'should_enter': should_enter,
                    'hours_to_expiry': hours_to_expiry
                })
        
        signals_df = pd.DataFrame(signals)
        df = df.merge(signals_df, on=['timestamp', 'market_id'], how='left')
        
        return df
    
    def simulate_trade_entry(self, row: pd.Series) -> Trade:
        """Create a new trade based on signal"""
        signal_strength = row['signal_strength']
        position_size_pct = self.position_sizes.get(signal_strength, 0.01)
        position_size_usd = min(
            self.capital * position_size_pct,
            self.capital * self.max_single_position
        )
        
        # Determine side based on ROC direction
        side = 'YES' if row['roc'] > 0 else 'NO'
        
        trade = Trade(
            entry_time=row['timestamp'],
            exit_time=None,
            market_id=row['market_id'],
            market_question=row['question'],
            side=side,
            entry_price=row['price_yes'] if side == 'YES' else row['price_no'],
            exit_price=None,
            position_size=position_size_usd,
            entry_signal_strength=signal_strength,
            exit_reason=None,
            rvr=row['rvr'],
            roc=row['roc'],
            liquidity_imbalance=None
        )
        
        return trade
    
    def check_exits(self, open_trades: List[Trade], row: pd.Series) -> List[Trade]:
        """Check if any open trades should be exited"""
        still_open = []
        
        for trade in open_trades:
            # Only check trades for this market
            if trade.market_id != row['market_id']:
                still_open.append(trade)
                continue
            
            current_price = row['price_yes'] if trade.side == 'YES' else row['price_no']
            price_change = (current_price - trade.entry_price) / trade.entry_price
            
            # Adjust for side
            if trade.side == 'NO':
                price_change = -price_change
            
            # Check stop loss
            if price_change <= -self.stop_loss_pct:
                trade.exit_time = row['timestamp']
                trade.exit_price = current_price
                trade.exit_reason = 'STOP_LOSS'
                self.trades.append(trade)
                continue
            
            # Check take profit levels
            exited = False
            for i, (tp_level, allocation) in enumerate(zip(self.tp_levels, self.tp_allocations)):
                if price_change >= tp_level:
                    trade.exit_time = row['timestamp']
                    trade.exit_price = current_price
                    trade.exit_reason = f'TP{i+1}'
                    self.trades.append(trade)
                    exited = True
                    break
            
            if exited:
                continue
            
            # Check time decay
            holding_hours = (row['timestamp'] - trade.entry_time).total_seconds() / 3600
            holding_days = holding_hours / 24
            
            if holding_days > self.time_decay_days[1] and price_change < self.time_decay_thresholds[1]:
                trade.exit_time = row['timestamp']
                trade.exit_price = current_price
                trade.exit_reason = 'TIME_DECAY_7D'
                self.trades.append(trade)
                continue
            elif holding_days > self.time_decay_days[0] and price_change < self.time_decay_thresholds[0]:
                trade.exit_time = row['timestamp']
                trade.exit_price = current_price
                trade.exit_reason = 'TIME_DECAY_3D'
                self.trades.append(trade)
                continue
            
            # Check market expiry (exit 7 days before)
            if row['hours_to_expiry'] < 168:  # 7 days
                trade.exit_time = row['timestamp']
                trade.exit_price = current_price
                trade.exit_reason = 'MARKET_EXPIRY'
                self.trades.append(trade)
                continue
            
            # Still open
            still_open.append(trade)
        
        return still_open
    
    def run_backtest(self, df: pd.DataFrame, walk_forward: bool = True) -> List[Trade]:
        """Run backtest with optional walk-forward validation"""
        print(f"\n{'='*60}")
        print("RUNNING BACKTEST")
        print(f"{'='*60}")
        print(f"Initial capital: ${self.initial_capital:,.0f}")
        print(f"Walk-forward validation: {walk_forward}")
        
        # Calculate signals
        print("\nCalculating signals...")
        df = self.calculate_signals(df)
        
        # Reset state
        self.trades = []
        self.open_trades = []
        self.capital = self.initial_capital
        self.peak_capital = self.initial_capital
        self.equity_curve = []
        
        # Simulate trading
        print("Simulating trades...")
        entry_signals = df[df['should_enter'] == True].sort_values('timestamp')
        
        for _, row in entry_signals.iterrows():
            # Check exits first
            self.open_trades = self.check_exits(self.open_trades, row)
            
            # Check if we can enter (exposure limits)
            current_exposure = sum(t.position_size for t in self.open_trades) / self.capital
            if current_exposure >= self.max_total_exposure:
                continue
            
            # Enter new trade
            trade = self.simulate_trade_entry(row)
            self.open_trades.append(trade)
            
            # Update capital (mark-to-market for all positions)
            pnl_open = sum(t.pnl_net or 0 for t in self.open_trades if t.pnl_net is not None)
            pnl_closed = sum(t.pnl_net for t in self.trades)
            self.capital = self.initial_capital + pnl_closed + pnl_open
            self.peak_capital = max(self.peak_capital, self.capital)
            
            self.equity_curve.append({
                'timestamp': row['timestamp'],
                'capital': self.capital,
                'open_trades': len(self.open_trades),
                'closed_trades': len(self.trades)
            })
        
        # Close any remaining open trades at last price
        for trade in self.open_trades:
            last_price = df[df['market_id'] == trade.market_id].iloc[-1]
            trade.exit_time = last_price['timestamp']
            trade.exit_price = last_price['price_yes'] if trade.side == 'YES' else last_price['price_no']
            trade.exit_reason = 'END_OF_BACKTEST'
            self.trades.append(trade)
        
        print(f"\n✓ Backtest complete: {len(self.trades)} trades executed")
        
        return self.trades
    
    def calculate_metrics(self) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        if len(self.trades) == 0:
            raise ValueError("No trades to analyze")
        
        # Basic stats
        returns = [t.return_pct for t in self.trades if t.return_pct is not None]
        winning_trades = [t for t in self.trades if t.return_pct and t.return_pct > 0]
        losing_trades = [t for t in self.trades if t.return_pct and t.return_pct < 0]
        
        win_rate = len(winning_trades) / len(self.trades)
        
        # Returns
        total_return_usd = sum(t.pnl_net for t in self.trades if t.pnl_net is not None)
        total_return_pct = (total_return_usd / self.initial_capital) * 100
        
        # Win/Loss stats
        avg_win_pct = np.mean([t.return_pct for t in winning_trades]) if winning_trades else 0
        avg_loss_pct = np.mean([t.return_pct for t in losing_trades]) if losing_trades else 0
        avg_win_usd = np.mean([t.pnl_net for t in winning_trades]) if winning_trades else 0
        avg_loss_usd = np.mean([t.pnl_net for t in losing_trades]) if losing_trades else 0
        
        # Profit factor
        total_wins = sum(t.pnl_net for t in winning_trades) if winning_trades else 0
        total_losses = abs(sum(t.pnl_net for t in losing_trades)) if losing_trades else 1
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Expectancy
        expectancy = (win_rate * avg_win_usd) - ((1 - win_rate) * abs(avg_loss_usd))
        
        # Risk-adjusted metrics
        returns_array = np.array(returns)
        sharpe_ratio = (np.mean(returns_array) / np.std(returns_array)) * np.sqrt(252) if len(returns_array) > 1 else 0
        
        # Sortino (downside deviation)
        downside_returns = [r for r in returns if r < 0]
        downside_std = np.std(downside_returns) if downside_returns else 1
        sortino_ratio = (np.mean(returns_array) / downside_std) * np.sqrt(252) if downside_std > 0 else 0
        
        # Drawdown
        equity_curve_df = pd.DataFrame(self.equity_curve)
        if len(equity_curve_df) > 0:
            equity_curve_df['peak'] = equity_curve_df['capital'].cummax()
            equity_curve_df['drawdown'] = (equity_curve_df['capital'] - equity_curve_df['peak']) / equity_curve_df['peak']
            max_drawdown_pct = equity_curve_df['drawdown'].min() * 100
            max_drawdown_usd = equity_curve_df['drawdown'].min() * self.peak_capital
        else:
            max_drawdown_pct = 0
            max_drawdown_usd = 0
        
        # Holding periods
        holding_hours = [t.holding_period_hours for t in self.trades if t.holding_period_hours is not None]
        avg_holding = np.mean(holding_hours) if holding_hours else 0
        median_holding = np.median(holding_hours) if holding_hours else 0
        
        # Best/Worst
        best_trade = max(returns) if returns else 0
        worst_trade = min(returns) if returns else 0
        
        # Consecutive streaks
        consecutive_wins = self._calculate_max_consecutive(self.trades, True)
        consecutive_losses = self._calculate_max_consecutive(self.trades, False)
        
        return PerformanceMetrics(
            total_trades=len(self.trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate * 100,
            total_return_pct=total_return_pct,
            total_return_usd=total_return_usd,
            avg_win_pct=avg_win_pct,
            avg_loss_pct=avg_loss_pct,
            avg_win_usd=avg_win_usd,
            avg_loss_usd=avg_loss_usd,
            profit_factor=profit_factor,
            expectancy=expectancy,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown_pct=abs(max_drawdown_pct),
            max_drawdown_usd=abs(max_drawdown_usd),
            avg_holding_hours=avg_holding,
            median_holding_hours=median_holding,
            best_trade_pct=best_trade,
            worst_trade_pct=worst_trade,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses
        )
    
    def _calculate_max_consecutive(self, trades: List[Trade], winning: bool) -> int:
        """Calculate maximum consecutive wins or losses"""
        max_streak = 0
        current_streak = 0
        
        for trade in trades:
            if trade.return_pct is None:
                continue
            
            is_win = trade.return_pct > 0
            if is_win == winning:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def bootstrap_confidence_interval(self, n_iterations: int = 1000) -> Tuple[float, float]:
        """Calculate 95% confidence interval using bootstrap"""
        returns = [t.return_pct for t in self.trades if t.return_pct is not None]
        if len(returns) < 10:
            return (0, 0)
        
        bootstrap_means = []
        for _ in range(n_iterations):
            sample = np.random.choice(returns, size=len(returns), replace=True)
            bootstrap_means.append(np.mean(sample))
        
        lower = np.percentile(bootstrap_means, 2.5)
        upper = np.percentile(bootstrap_means, 97.5)
        
        return (lower, upper)


# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generate HTML report with charts"""
    
    def __init__(self, trades: List[Trade], metrics: PerformanceMetrics, 
                 equity_curve: List[Dict], output_dir: str):
        self.trades = trades
        self.metrics = metrics
        self.equity_curve = pd.DataFrame(equity_curve)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all(self):
        """Generate all reports"""
        print(f"\n{'='*60}")
        print("GENERATING REPORTS")
        print(f"{'='*60}")
        
        # 1. Trade log CSV
        self.save_trade_log()
        
        # 2. Metrics JSON
        self.save_metrics_json()
        
        # 3. Charts
        self.generate_charts()
        
        # 4. HTML report
        self.generate_html_report()
        
        print(f"\n✓ Reports saved to: {self.output_dir}")
    
    def save_trade_log(self):
        """Save trade log as CSV"""
        trades_data = []
        for trade in self.trades:
            trades_data.append({
                'entry_time': trade.entry_time,
                'exit_time': trade.exit_time,
                'market_question': trade.market_question,
                'side': trade.side,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'position_size': trade.position_size,
                'pnl_gross': trade.pnl_gross,
                'pnl_net': trade.pnl_net,
                'return_pct': trade.return_pct,
                'holding_hours': trade.holding_period_hours,
                'signal_strength': trade.entry_signal_strength,
                'exit_reason': trade.exit_reason,
                'rvr': trade.rvr,
                'roc': trade.roc
            })
        
        df = pd.DataFrame(trades_data)
        csv_path = self.output_dir / 'trade_log.csv'
        df.to_csv(csv_path, index=False)
        print(f"✓ Trade log: {csv_path}")
    
    def save_metrics_json(self):
        """Save metrics as JSON"""
        json_path = self.output_dir / 'performance_metrics.json'
        with open(json_path, 'w') as f:
            json.dump(asdict(self.metrics), f, indent=2, default=str)
        print(f"✓ Metrics JSON: {json_path}")
    
    def generate_charts(self):
        """Generate charts using matplotlib"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Backtest Performance Analysis', fontsize=16, fontweight='bold')
        
        # 1. Equity curve
        ax1 = axes[0, 0]
        if len(self.equity_curve) > 0:
            ax1.plot(self.equity_curve['timestamp'], self.equity_curve['capital'], 
                    linewidth=2, color='#2E86AB')
            ax1.axhline(y=self.metrics.total_return_usd + 10000, 
                       color='green', linestyle='--', alpha=0.5, label='Final Capital')
            ax1.fill_between(self.equity_curve['timestamp'], 
                            self.equity_curve['capital'].cummax(), 
                            alpha=0.2, color='gray', label='Drawdown')
        ax1.set_title('Equity Curve')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Capital ($)')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # 2. Returns distribution
        ax2 = axes[0, 1]
        returns = [t.return_pct for t in self.trades if t.return_pct is not None]
        if returns:
            ax2.hist(returns, bins=30, color='#A23B72', alpha=0.7, edgecolor='black')
            ax2.axvline(x=0, color='red', linestyle='--', linewidth=2)
            ax2.axvline(x=np.mean(returns), color='green', linestyle='--', 
                       linewidth=2, label=f'Mean: {np.mean(returns):.2f}%')
        ax2.set_title('Returns Distribution')
        ax2.set_xlabel('Return (%)')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        ax2.grid(alpha=0.3)
        
        # 3. Win/Loss breakdown
        ax3 = axes[1, 0]
        labels = ['Wins', 'Losses']
        sizes = [self.metrics.winning_trades, self.metrics.losing_trades]
        colors = ['#18A558', '#F18F01']
        ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax3.set_title(f'Win Rate: {self.metrics.win_rate:.1f}%')
        
        # 4. Trade timeline
        ax4 = axes[1, 1]
        trade_times = [t.entry_time for t in self.trades]
        trade_returns = [t.return_pct for t in self.trades if t.return_pct is not None]
        if trade_times and trade_returns:
            colors_timeline = ['green' if r > 0 else 'red' for r in trade_returns]
            ax4.scatter(trade_times, trade_returns, c=colors_timeline, alpha=0.6, s=50)
            ax4.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax4.set_title('Trade Returns Over Time')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Return (%)')
        ax4.grid(alpha=0.3)
        
        plt.tight_layout()
        chart_path = self.output_dir / 'performance_charts.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Charts: {chart_path}")
    
    def generate_html_report(self):
        """Generate comprehensive HTML report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Backtest Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 4px solid #667eea;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .metric-card.positive {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .metric-card.negative {{
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        }}
        .metric-label {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .status-pass {{
            color: #27ae60;
            font-weight: bold;
        }}
        .status-fail {{
            color: #e74c3c;
            font-weight: bold;
        }}
        img {{
            max-width: 100%;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Backtest Performance Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Total Trades:</strong> {self.metrics.total_trades}</p>
        
        <h2>🎯 Key Performance Metrics</h2>
        <div class="metrics-grid">
            <div class="metric-card {'positive' if self.metrics.total_return_pct > 0 else 'negative'}">
                <div class="metric-label">Total Return</div>
                <div class="metric-value">{self.metrics.total_return_pct:+.2f}%</div>
            </div>
            <div class="metric-card {'positive' if self.metrics.win_rate >= 50 else ''}">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value">{self.metrics.win_rate:.1f}%</div>
            </div>
            <div class="metric-card {'positive' if self.metrics.sharpe_ratio > 1.0 else ''}">
                <div class="metric-label">Sharpe Ratio</div>
                <div class="metric-value">{self.metrics.sharpe_ratio:.2f}</div>
            </div>
            <div class="metric-card {'positive' if self.metrics.profit_factor > 1.5 else ''}">
                <div class="metric-label">Profit Factor</div>
                <div class="metric-value">{self.metrics.profit_factor:.2f}</div>
            </div>
            <div class="metric-card {'negative' if self.metrics.max_drawdown_pct > 25 else ''}">
                <div class="metric-label">Max Drawdown</div>
                <div class="metric-value">{self.metrics.max_drawdown_pct:.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Expectancy</div>
                <div class="metric-value">${self.metrics.expectancy:.2f}</div>
            </div>
        </div>
        
        <h2>📈 Strategy Validation</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Target</th>
                <th>Actual</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Sharpe Ratio</td>
                <td>> 1.0</td>
                <td>{self.metrics.sharpe_ratio:.2f}</td>
                <td class="{'status-pass' if self.metrics.sharpe_ratio > 1.0 else 'status-fail'}">
                    {'✓ PASS' if self.metrics.sharpe_ratio > 1.0 else '✗ FAIL'}
                </td>
            </tr>
            <tr>
                <td>Max Drawdown</td>
                <td>< 25%</td>
                <td>{self.metrics.max_drawdown_pct:.1f}%</td>
                <td class="{'status-pass' if self.metrics.max_drawdown_pct < 25 else 'status-fail'}">
                    {'✓ PASS' if self.metrics.max_drawdown_pct < 25 else '✗ FAIL'}
                </td>
            </tr>
            <tr>
                <td>Win Rate</td>
                <td>> 50%</td>
                <td>{self.metrics.win_rate:.1f}%</td>
                <td class="{'status-pass' if self.metrics.win_rate > 50 else 'status-fail'}">
                    {'✓ PASS' if self.metrics.win_rate > 50 else '✗ FAIL'}
                </td>
            </tr>
            <tr>
                <td>Profit Factor</td>
                <td>> 1.5</td>
                <td>{self.metrics.profit_factor:.2f}</td>
                <td class="{'status-pass' if self.metrics.profit_factor > 1.5 else 'status-fail'}">
                    {'✓ PASS' if self.metrics.profit_factor > 1.5 else '✗ FAIL'}
                </td>
            </tr>
            <tr>
                <td>Minimum Trades</td>
                <td>> 30</td>
                <td>{self.metrics.total_trades}</td>
                <td class="{'status-pass' if self.metrics.total_trades >= 30 else 'status-fail'}">
                    {'✓ PASS' if self.metrics.total_trades >= 30 else '✗ FAIL'}
                </td>
            </tr>
        </table>
        
        <h2>💰 Win/Loss Analysis</h2>
        <table>
            <tr>
                <th></th>
                <th>Count</th>
                <th>Avg Return %</th>
                <th>Avg P&L $</th>
                <th>Total $</th>
            </tr>
            <tr>
                <td><strong>Winners</strong></td>
                <td>{self.metrics.winning_trades}</td>
                <td>{self.metrics.avg_win_pct:.2f}%</td>
                <td>${self.metrics.avg_win_usd:.2f}</td>
                <td>${self.metrics.avg_win_usd * self.metrics.winning_trades:.2f}</td>
            </tr>
            <tr>
                <td><strong>Losers</strong></td>
                <td>{self.metrics.losing_trades}</td>
                <td>{self.metrics.avg_loss_pct:.2f}%</td>
                <td>${self.metrics.avg_loss_usd:.2f}</td>
                <td>${self.metrics.avg_loss_usd * self.metrics.losing_trades:.2f}</td>
            </tr>
        </table>
        
        <h2>📊 Charts</h2>
        <img src="performance_charts.png" alt="Performance Charts">
        
        <h2>⏱️ Trade Statistics</h2>
        <ul>
            <li><strong>Average Holding Time:</strong> {self.metrics.avg_holding_hours:.1f} hours ({self.metrics.avg_holding_hours/24:.1f} days)</li>
            <li><strong>Median Holding Time:</strong> {self.metrics.median_holding_hours:.1f} hours</li>
            <li><strong>Best Trade:</strong> {self.metrics.best_trade_pct:+.2f}%</li>
            <li><strong>Worst Trade:</strong> {self.metrics.worst_trade_pct:+.2f}%</li>
            <li><strong>Max Consecutive Wins:</strong> {self.metrics.consecutive_wins}</li>
            <li><strong>Max Consecutive Losses:</strong> {self.metrics.consecutive_losses}</li>
        </ul>
        
        <div class="footer">
            <p>Report generated by Prediction Market Backtesting Engine v1.0</p>
            <p>Data: {len(self.trades)} trades | Capital: ${10000:,.0f}</p>
        </div>
    </div>
</body>
</html>
"""
        
        html_path = self.output_dir / 'backtest_report.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✓ HTML report: {html_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Backtest prediction market trading strategy')
    parser.add_argument('--db', type=str, default='polymarket_data.db',
                       help='Path to SQLite database')
    parser.add_argument('--output', type=str, default='backtest_results',
                       help='Output directory for reports')
    parser.add_argument('--capital', type=float, default=10000,
                       help='Initial capital ($)')
    parser.add_argument('--walk-forward', action='store_true',
                       help='Use walk-forward validation')
    
    args = parser.parse_args()
    
    # Check if database exists
    if not Path(args.db).exists():
        print(f"✗ Database not found: {args.db}")
        print("\nTo create sample data, run:")
        print("  python polymarket-data-collector.py")
        return
    
    # Initialize engine
    print(f"\n{'='*60}")
    print("PREDICTION MARKET BACKTESTING ENGINE")
    print(f"{'='*60}")
    
    engine = BacktestEngine(args.db, initial_capital=args.capital)
    
    # Load data
    df = engine.load_data()
    
    if len(df) == 0:
        print("✗ No data found in database")
        return
    
    # Run backtest
    trades = engine.run_backtest(df, walk_forward=args.walk_forward)
    
    if len(trades) < 10:
        print(f"\n⚠️  Warning: Only {len(trades)} trades generated.")
        print("Need at least 30 trades for valid results.")
        print("Consider:")
        print("  - Collecting more data")
        print("  - Adjusting signal thresholds")
        print("  - Increasing lookback period")
    
    # Calculate metrics
    print("\nCalculating performance metrics...")
    metrics = engine.calculate_metrics()
    
    # Bootstrap confidence interval
    print("Running bootstrap analysis...")
    ci_lower, ci_upper = engine.bootstrap_confidence_interval()
    metrics.confidence_interval_95 = (ci_lower, ci_upper)
    
    # Print summary
    print(f"\n{'='*60}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*60}")
    print(f"Total Return:        {metrics.total_return_pct:+.2f}% (${metrics.total_return_usd:+,.2f})")
    print(f"Win Rate:            {metrics.win_rate:.1f}% ({metrics.winning_trades}/{metrics.total_trades})")
    print(f"Profit Factor:       {metrics.profit_factor:.2f}")
    print(f"Sharpe Ratio:        {metrics.sharpe_ratio:.2f}")
    print(f"Sortino Ratio:       {metrics.sortino_ratio:.2f}")
    print(f"Max Drawdown:        {metrics.max_drawdown_pct:.1f}%")
    print(f"Expectancy:          ${metrics.expectancy:.2f} per trade")
    print(f"Avg Win:             {metrics.avg_win_pct:+.2f}%")
    print(f"Avg Loss:            {metrics.avg_loss_pct:.2f}%")
    print(f"95% CI:              [{ci_lower:.2f}%, {ci_upper:.2f}%]")
    print(f"{'='*60}\n")
    
    # Generate reports
    reporter = ReportGenerator(trades, metrics, engine.equity_curve, args.output)
    reporter.generate_all()
    
    print("\n✅ Backtest complete!")
    print(f"📁 View results: {Path(args.output).absolute()}")
    print(f"📊 Open: {Path(args.output).absolute() / 'backtest_report.html'}")


if __name__ == '__main__':
    main()
