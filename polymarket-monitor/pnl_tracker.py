"""
Real-Time P&L Tracking System for Polymarket Trading
Production-grade module with comprehensive performance analytics

Features:
- Real-time position tracking (open and closed)
- Unrealized and realized P&L calculation
- Performance metrics (Win Rate, ROI, Sharpe Ratio)
- Strategy-level analytics
- Daily/weekly reporting
- Export to CSV/JSON
- Beautiful console output
- SQLite persistence
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import csv
import logging
from collections import defaultdict
import statistics
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich import box
import time

logger = logging.getLogger(__name__)
console = Console()

DB_PATH = "polymarket_data.db"
GAMMA_API = "https://gamma-api.polymarket.com"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Position:
    """Represents an open or closed trading position"""
    trade_id: int
    market_id: str
    market_name: str
    side: str  # YES or NO
    entry_price: float
    position_size: float
    entry_time: int
    stop_loss: float
    take_profit: Optional[float]
    
    # Current state
    current_price: Optional[float] = None
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    
    # Exit data (for closed positions)
    status: str = "OPEN"
    exit_price: Optional[float] = None
    exit_time: Optional[int] = None
    exit_reason: Optional[str] = None
    realized_pnl: float = 0.0
    realized_pnl_pct: float = 0.0
    
    # Metadata
    rvr_ratio: Optional[float] = None
    strategy: str = "default"
    days_to_resolution: Optional[int] = None
    
    def is_open(self) -> bool:
        return self.status == "OPEN"
    
    def current_value(self) -> float:
        """Calculate current position value"""
        if self.current_price is None:
            return self.position_size * self.entry_price
        return self.position_size * self.current_price
    
    def initial_value(self) -> float:
        """Calculate initial position value"""
        return self.position_size * self.entry_price


@dataclass
class PerformanceMetrics:
    """Performance statistics for a portfolio or strategy"""
    total_trades: int
    open_positions: int
    closed_positions: int
    
    # P&L
    total_realized_pnl: float
    total_unrealized_pnl: float
    total_pnl: float
    
    # Win metrics
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # Return metrics
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    profit_factor: float
    
    # ROI
    total_capital_deployed: float
    roi: float
    
    # Risk metrics
    sharpe_ratio: float
    max_drawdown: float
    
    # Strategy breakdown
    strategy_breakdown: Dict[str, dict]
    
    # Time-based
    avg_hold_time_hours: float
    
    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# DATABASE SCHEMA EXTENSIONS
# ============================================================================

def init_pnl_tables():
    """Initialize P&L tracking tables (extends existing schema)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Add strategy column to paper_trades if not exists
    cursor.execute("""
        SELECT COUNT(*) FROM pragma_table_info('paper_trades')
        WHERE name='strategy'
    """)
    
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            ALTER TABLE paper_trades ADD COLUMN strategy TEXT DEFAULT 'default'
        """)
        logger.info("Added 'strategy' column to paper_trades")
    
    # Daily P&L snapshots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pnl_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date TEXT NOT NULL,
            snapshot_time INTEGER NOT NULL,
            
            total_positions INTEGER DEFAULT 0,
            open_positions INTEGER DEFAULT 0,
            closed_positions INTEGER DEFAULT 0,
            
            total_capital_deployed REAL DEFAULT 0.0,
            total_position_value REAL DEFAULT 0.0,
            
            realized_pnl REAL DEFAULT 0.0,
            unrealized_pnl REAL DEFAULT 0.0,
            total_pnl REAL DEFAULT 0.0,
            
            win_rate REAL DEFAULT 0.0,
            roi REAL DEFAULT 0.0,
            sharpe_ratio REAL DEFAULT 0.0,
            max_drawdown REAL DEFAULT 0.0,
            
            UNIQUE(snapshot_date)
        )
    """)
    
    # Strategy performance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_name TEXT NOT NULL,
            period_start TEXT NOT NULL,
            period_end TEXT NOT NULL,
            
            total_trades INTEGER DEFAULT 0,
            win_rate REAL DEFAULT 0.0,
            avg_roi REAL DEFAULT 0.0,
            total_pnl REAL DEFAULT 0.0,
            sharpe_ratio REAL DEFAULT 0.0,
            
            UNIQUE(strategy_name, period_start, period_end)
        )
    """)
    
    # Trade tags/metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id INTEGER NOT NULL,
            tag_key TEXT NOT NULL,
            tag_value TEXT NOT NULL,
            FOREIGN KEY (trade_id) REFERENCES paper_trades(id)
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pnl_snapshots_date 
        ON pnl_snapshots(snapshot_date)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_strategy_perf 
        ON strategy_performance(strategy_name, period_start)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_trade_tags 
        ON trade_tags(trade_id, tag_key)
    """)
    
    conn.commit()
    conn.close()
    
    logger.info("P&L tracking tables initialized")
    console.print("[green]✓[/green] P&L database schema initialized")


# ============================================================================
# PRICE FETCHING
# ============================================================================

class PriceFetcher:
    """Fetch real-time prices from Polymarket API"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 60  # seconds
        self.last_fetch = {}
    
    def get_current_price(self, market_id: str, side: str = "YES") -> Optional[float]:
        """
        Get current market price with caching
        
        Args:
            market_id: Polymarket market ID
            side: YES or NO
            
        Returns:
            Current price as float, or None if unavailable
        """
        cache_key = f"{market_id}_{side}"
        
        # Check cache
        if cache_key in self.cache:
            if time.time() - self.last_fetch.get(cache_key, 0) < self.cache_ttl:
                return self.cache[cache_key]
        
        try:
            # Fetch from API
            url = f"{GAMMA_API}/markets/{market_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract price based on side
                if side == "YES":
                    price = float(data.get('tokens', [{}])[0].get('price', 0))
                else:  # NO
                    price = 1.0 - float(data.get('tokens', [{}])[0].get('price', 0))
                
                # Update cache
                self.cache[cache_key] = price
                self.last_fetch[cache_key] = time.time()
                
                return price
            
        except Exception as e:
            logger.error(f"Error fetching price for {market_id}: {e}")
        
        return None
    
    def get_bulk_prices(self, market_ids: List[str]) -> Dict[str, float]:
        """Fetch prices for multiple markets efficiently"""
        prices = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"[cyan]Fetching prices for {len(market_ids)} markets...", 
                total=len(market_ids)
            )
            
            for market_id in market_ids:
                price = self.get_current_price(market_id)
                if price is not None:
                    prices[market_id] = price
                progress.advance(task)
        
        return prices


# ============================================================================
# P&L TRACKER CORE
# ============================================================================

class PnLTracker:
    """Main P&L tracking engine"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.price_fetcher = PriceFetcher()
        init_pnl_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ========================================================================
    # POSITION LOADING
    # ========================================================================
    
    def get_open_positions(self) -> List[Position]:
        """Load all open positions from database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM paper_trades
            WHERE status = 'OPEN'
            ORDER BY entry_time DESC
        """)
        
        positions = []
        for row in cursor.fetchall():
            pos = Position(
                trade_id=row['id'],
                market_id=row['market_id'],
                market_name=row['market_name'],
                side=row['side'],
                entry_price=row['entry_price'],
                position_size=row['position_size'],
                entry_time=row['entry_time'],
                stop_loss=row['stop_loss'],
                take_profit=row.get('take_profit_1'),
                status=row['status'],
                rvr_ratio=row.get('rvr_ratio'),
                strategy=row.get('strategy', 'default'),
                days_to_resolution=row.get('days_to_resolution')
            )
            positions.append(pos)
        
        conn.close()
        return positions
    
    def get_closed_positions(self, days: int = 30) -> List[Position]:
        """Load closed positions from database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
        
        cursor.execute("""
            SELECT * FROM paper_trades
            WHERE status != 'OPEN' AND entry_time >= ?
            ORDER BY exit_time DESC
        """, (cutoff,))
        
        positions = []
        for row in cursor.fetchall():
            pos = Position(
                trade_id=row['id'],
                market_id=row['market_id'],
                market_name=row['market_name'],
                side=row['side'],
                entry_price=row['entry_price'],
                position_size=row['position_size'],
                entry_time=row['entry_time'],
                stop_loss=row['stop_loss'],
                take_profit=row.get('take_profit_1'),
                status=row['status'],
                exit_price=row.get('exit_price'),
                exit_time=row.get('exit_time'),
                exit_reason=row.get('exit_reason'),
                realized_pnl=row.get('pnl_dollars', 0.0),
                realized_pnl_pct=row.get('pnl_percent', 0.0),
                rvr_ratio=row.get('rvr_ratio'),
                strategy=row.get('strategy', 'default'),
                days_to_resolution=row.get('days_to_resolution')
            )
            positions.append(pos)
        
        conn.close()
        return positions
    
    # ========================================================================
    # REAL-TIME P&L UPDATES
    # ========================================================================
    
    def update_position_prices(self, positions: List[Position]) -> List[Position]:
        """Update current prices for all positions"""
        
        # Get unique market IDs
        market_ids = list(set(pos.market_id for pos in positions))
        
        # Bulk fetch prices
        prices = self.price_fetcher.get_bulk_prices(market_ids)
        
        # Update positions
        for pos in positions:
            if pos.market_id in prices:
                pos.current_price = prices[pos.market_id]
                
                # Calculate unrealized P&L
                if pos.current_price is not None:
                    price_change = pos.current_price - pos.entry_price
                    pos.unrealized_pnl = price_change * pos.position_size
                    
                    if pos.entry_price > 0:
                        pos.unrealized_pnl_pct = (price_change / pos.entry_price) * 100
        
        return positions
    
    def save_position_tick(self, position: Position):
        """Save a position price tick to database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO paper_position_ticks 
            (trade_id, timestamp, current_price, pnl_unrealized, pnl_pct)
            VALUES (?, ?, ?, ?, ?)
        """, (
            position.trade_id,
            int(time.time()),
            position.current_price,
            position.unrealized_pnl,
            position.unrealized_pnl_pct
        ))
        
        conn.commit()
        conn.close()
    
    # ========================================================================
    # PERFORMANCE METRICS
    # ========================================================================
    
    def calculate_metrics(
        self,
        open_positions: List[Position],
        closed_positions: List[Position]
    ) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        
        # Basic counts
        total_trades = len(open_positions) + len(closed_positions)
        
        # P&L calculations
        total_unrealized = sum(pos.unrealized_pnl for pos in open_positions)
        total_realized = sum(pos.realized_pnl for pos in closed_positions)
        total_pnl = total_unrealized + total_realized
        
        # Win/loss analysis
        winning_trades = [p for p in closed_positions if p.realized_pnl > 0]
        losing_trades = [p for p in closed_positions if p.realized_pnl < 0]
        
        win_rate = (
            len(winning_trades) / len(closed_positions) * 100
            if closed_positions else 0.0
        )
        
        avg_win = (
            statistics.mean([p.realized_pnl for p in winning_trades])
            if winning_trades else 0.0
        )
        
        avg_loss = (
            statistics.mean([p.realized_pnl for p in losing_trades])
            if losing_trades else 0.0
        )
        
        largest_win = max([p.realized_pnl for p in winning_trades], default=0.0)
        largest_loss = min([p.realized_pnl for p in losing_trades], default=0.0)
        
        # Profit factor
        total_wins = sum(p.realized_pnl for p in winning_trades)
        total_losses = abs(sum(p.realized_pnl for p in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Capital deployed
        total_capital = sum(pos.initial_value() for pos in open_positions)
        total_capital += sum(pos.initial_value() for pos in closed_positions)
        
        # ROI
        roi = (total_pnl / total_capital * 100) if total_capital > 0 else 0.0
        
        # Sharpe ratio (simplified - using trade returns)
        if len(closed_positions) > 1:
            returns = [p.realized_pnl_pct for p in closed_positions]
            avg_return = statistics.mean(returns)
            std_return = statistics.stdev(returns)
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Max drawdown calculation
        max_drawdown = self._calculate_max_drawdown(closed_positions)
        
        # Strategy breakdown
        strategy_breakdown = self._calculate_strategy_breakdown(
            open_positions, closed_positions
        )
        
        # Average hold time
        hold_times = [
            (p.exit_time - p.entry_time) / 3600  # hours
            for p in closed_positions if p.exit_time
        ]
        avg_hold_time = statistics.mean(hold_times) if hold_times else 0.0
        
        return PerformanceMetrics(
            total_trades=total_trades,
            open_positions=len(open_positions),
            closed_positions=len(closed_positions),
            total_realized_pnl=total_realized,
            total_unrealized_pnl=total_unrealized,
            total_pnl=total_pnl,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            profit_factor=profit_factor,
            total_capital_deployed=total_capital,
            roi=roi,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            strategy_breakdown=strategy_breakdown,
            avg_hold_time_hours=avg_hold_time
        )
    
    def _calculate_max_drawdown(self, closed_positions: List[Position]) -> float:
        """Calculate maximum drawdown from peak equity"""
        if not closed_positions:
            return 0.0
        
        # Sort by exit time
        sorted_positions = sorted(
            [p for p in closed_positions if p.exit_time],
            key=lambda x: x.exit_time
        )
        
        # Calculate running equity
        equity = 0.0
        peak = 0.0
        max_dd = 0.0
        
        for pos in sorted_positions:
            equity += pos.realized_pnl
            peak = max(peak, equity)
            drawdown = peak - equity
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def _calculate_strategy_breakdown(
        self,
        open_positions: List[Position],
        closed_positions: List[Position]
    ) -> Dict[str, dict]:
        """Break down performance by strategy"""
        
        strategy_stats = defaultdict(lambda: {
            'total_trades': 0,
            'open_positions': 0,
            'closed_positions': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'avg_roi': 0.0
        })
        
        # Process open positions
        for pos in open_positions:
            strategy = pos.strategy or 'default'
            strategy_stats[strategy]['total_trades'] += 1
            strategy_stats[strategy]['open_positions'] += 1
            strategy_stats[strategy]['total_pnl'] += pos.unrealized_pnl
        
        # Process closed positions
        strategy_closed = defaultdict(list)
        for pos in closed_positions:
            strategy = pos.strategy or 'default'
            strategy_stats[strategy]['total_trades'] += 1
            strategy_stats[strategy]['closed_positions'] += 1
            strategy_stats[strategy]['total_pnl'] += pos.realized_pnl
            strategy_closed[strategy].append(pos)
        
        # Calculate win rates and ROI
        for strategy, positions in strategy_closed.items():
            if positions:
                wins = [p for p in positions if p.realized_pnl > 0]
                strategy_stats[strategy]['win_rate'] = (
                    len(wins) / len(positions) * 100
                )
                strategy_stats[strategy]['avg_roi'] = statistics.mean([
                    p.realized_pnl_pct for p in positions
                ])
        
        return dict(strategy_stats)
    
    # ========================================================================
    # SNAPSHOTS & HISTORY
    # ========================================================================
    
    def save_daily_snapshot(self, metrics: PerformanceMetrics):
        """Save daily P&L snapshot"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT OR REPLACE INTO pnl_snapshots
            (snapshot_date, snapshot_time, total_positions, open_positions, 
             closed_positions, realized_pnl, unrealized_pnl, total_pnl,
             win_rate, roi, sharpe_ratio, max_drawdown)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            today,
            int(time.time()),
            metrics.total_trades,
            metrics.open_positions,
            metrics.closed_positions,
            metrics.total_realized_pnl,
            metrics.total_unrealized_pnl,
            metrics.total_pnl,
            metrics.win_rate,
            metrics.roi,
            metrics.sharpe_ratio,
            metrics.max_drawdown
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Saved daily snapshot for {today}")
    
    def get_historical_snapshots(self, days: int = 30) -> List[dict]:
        """Get historical P&L snapshots"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT * FROM pnl_snapshots
            WHERE snapshot_date >= ?
            ORDER BY snapshot_date ASC
        """, (cutoff,))
        
        snapshots = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return snapshots
    
    # ========================================================================
    # EXPORT FUNCTIONS
    # ========================================================================
    
    def export_to_csv(
        self,
        filename: str,
        include_open: bool = True,
        include_closed: bool = True
    ):
        """Export positions to CSV"""
        
        positions = []
        
        if include_open:
            positions.extend(self.get_open_positions())
        
        if include_closed:
            positions.extend(self.get_closed_positions())
        
        if not positions:
            console.print("[yellow]No positions to export[/yellow]")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'trade_id', 'market_name', 'side', 'entry_price', 'current_price',
                'position_size', 'entry_time', 'exit_time', 'status',
                'unrealized_pnl', 'realized_pnl', 'pnl_pct', 'strategy'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for pos in positions:
                writer.writerow({
                    'trade_id': pos.trade_id,
                    'market_name': pos.market_name,
                    'side': pos.side,
                    'entry_price': pos.entry_price,
                    'current_price': pos.current_price or pos.exit_price,
                    'position_size': pos.position_size,
                    'entry_time': datetime.fromtimestamp(pos.entry_time).isoformat(),
                    'exit_time': datetime.fromtimestamp(pos.exit_time).isoformat() if pos.exit_time else '',
                    'status': pos.status,
                    'unrealized_pnl': pos.unrealized_pnl if pos.is_open() else 0,
                    'realized_pnl': pos.realized_pnl,
                    'pnl_pct': pos.unrealized_pnl_pct if pos.is_open() else pos.realized_pnl_pct,
                    'strategy': pos.strategy
                })
        
        console.print(f"[green]✓[/green] Exported {len(positions)} positions to {filename}")
    
    def export_to_json(self, filename: str, metrics: PerformanceMetrics):
        """Export full P&L report to JSON"""
        
        open_positions = self.get_open_positions()
        closed_positions = self.get_closed_positions()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics.to_dict(),
            'open_positions': [asdict(pos) for pos in open_positions],
            'closed_positions': [asdict(pos) for pos in closed_positions],
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        console.print(f"[green]✓[/green] Exported full report to {filename}")
    
    # ========================================================================
    # BEAUTIFUL CONSOLE OUTPUT
    # ========================================================================
    
    def print_dashboard(self):
        """Print beautiful P&L dashboard to console"""
        
        console.clear()
        console.print("\n")
        console.print(Panel.fit(
            "[bold cyan]📊 POLYMARKET P&L TRACKER[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
        
        # Load data
        open_positions = self.get_open_positions()
        closed_positions = self.get_closed_positions()
        
        # Update prices
        open_positions = self.update_position_prices(open_positions)
        
        # Calculate metrics
        metrics = self.calculate_metrics(open_positions, closed_positions)
        
        # Performance summary
        self._print_performance_summary(metrics)
        console.print()
        
        # Open positions table
        if open_positions:
            self._print_open_positions(open_positions)
            console.print()
        
        # Recent closed positions
        if closed_positions:
            recent_closed = sorted(
                closed_positions,
                key=lambda x: x.exit_time or 0,
                reverse=True
            )[:10]
            self._print_closed_positions(recent_closed)
            console.print()
        
        # Strategy breakdown
        if metrics.strategy_breakdown:
            self._print_strategy_breakdown(metrics.strategy_breakdown)
            console.print()
        
        # Save snapshot
        self.save_daily_snapshot(metrics)
    
    def _print_performance_summary(self, metrics: PerformanceMetrics):
        """Print performance summary panel"""
        
        # Color coding for P&L
        pnl_color = "green" if metrics.total_pnl >= 0 else "red"
        realized_color = "green" if metrics.total_realized_pnl >= 0 else "red"
        unrealized_color = "green" if metrics.total_unrealized_pnl >= 0 else "red"
        
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")
        
        table.add_row(
            "Total P&L",
            f"[{pnl_color}]${metrics.total_pnl:,.2f}[/{pnl_color}]"
        )
        table.add_row(
            "  ├─ Realized",
            f"[{realized_color}]${metrics.total_realized_pnl:,.2f}[/{realized_color}]"
        )
        table.add_row(
            "  └─ Unrealized",
            f"[{unrealized_color}]${metrics.total_unrealized_pnl:,.2f}[/{unrealized_color}]"
        )
        table.add_row("", "")
        table.add_row("ROI", f"[bold]{metrics.roi:,.2f}%[/bold]")
        table.add_row("Win Rate", f"{metrics.win_rate:.1f}%")
        table.add_row("Profit Factor", f"{metrics.profit_factor:.2f}")
        table.add_row("Sharpe Ratio", f"{metrics.sharpe_ratio:.2f}")
        table.add_row("", "")
        table.add_row("Total Trades", str(metrics.total_trades))
        table.add_row("  ├─ Open", str(metrics.open_positions))
        table.add_row("  └─ Closed", str(metrics.closed_positions))
        table.add_row("", "")
        table.add_row("Avg Win", f"[green]${metrics.avg_win:,.2f}[/green]")
        table.add_row("Avg Loss", f"[red]${metrics.avg_loss:,.2f}[/red]")
        table.add_row("Max Drawdown", f"[red]${metrics.max_drawdown:,.2f}[/red]")
        
        console.print(Panel(
            table,
            title="[bold]Performance Summary[/bold]",
            border_style="blue"
        ))
    
    def _print_open_positions(self, positions: List[Position]):
        """Print open positions table"""
        
        table = Table(
            title="[bold]Open Positions[/bold]",
            box=box.ROUNDED,
            show_lines=True
        )
        
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Market", style="white", max_width=30)
        table.add_column("Side", justify="center", width=6)
        table.add_column("Entry", justify="right", width=10)
        table.add_column("Current", justify="right", width=10)
        table.add_column("Size", justify="right", width=8)
        table.add_column("P&L", justify="right", width=12)
        table.add_column("P&L %", justify="right", width=10)
        table.add_column("Strategy", width=12)
        
        for pos in positions:
            # Color coding
            side_color = "green" if pos.side == "YES" else "red"
            pnl_color = "green" if pos.unrealized_pnl >= 0 else "red"
            
            current_price = f"${pos.current_price:.3f}" if pos.current_price else "---"
            
            table.add_row(
                str(pos.trade_id),
                pos.market_name[:30],
                f"[{side_color}]{pos.side}[/{side_color}]",
                f"${pos.entry_price:.3f}",
                current_price,
                f"${pos.position_size:.0f}",
                f"[{pnl_color}]${pos.unrealized_pnl:+,.2f}[/{pnl_color}]",
                f"[{pnl_color}]{pos.unrealized_pnl_pct:+.2f}%[/{pnl_color}]",
                pos.strategy
            )
        
        console.print(table)
    
    def _print_closed_positions(self, positions: List[Position]):
        """Print recent closed positions table"""
        
        table = Table(
            title="[bold]Recent Closed Positions[/bold]",
            box=box.ROUNDED
        )
        
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Market", style="white", max_width=30)
        table.add_column("Side", justify="center", width=6)
        table.add_column("Entry", justify="right", width=10)
        table.add_column("Exit", justify="right", width=10)
        table.add_column("P&L", justify="right", width=12)
        table.add_column("P&L %", justify="right", width=10)
        table.add_column("Exit Reason", width=15)
        
        for pos in positions:
            # Color coding
            side_color = "green" if pos.side == "YES" else "red"
            pnl_color = "green" if pos.realized_pnl >= 0 else "red"
            
            exit_price = f"${pos.exit_price:.3f}" if pos.exit_price else "---"
            
            table.add_row(
                str(pos.trade_id),
                pos.market_name[:30],
                f"[{side_color}]{pos.side}[/{side_color}]",
                f"${pos.entry_price:.3f}",
                exit_price,
                f"[{pnl_color}]${pos.realized_pnl:+,.2f}[/{pnl_color}]",
                f"[{pnl_color}]{pos.realized_pnl_pct:+.2f}%[/{pnl_color}]",
                pos.exit_reason or "---"
            )
        
        console.print(table)
    
    def _print_strategy_breakdown(self, breakdown: Dict[str, dict]):
        """Print strategy performance breakdown"""
        
        table = Table(
            title="[bold]Strategy Breakdown[/bold]",
            box=box.ROUNDED
        )
        
        table.add_column("Strategy", style="cyan")
        table.add_column("Total", justify="right")
        table.add_column("Open", justify="right")
        table.add_column("Closed", justify="right")
        table.add_column("Win Rate", justify="right")
        table.add_column("Avg ROI", justify="right")
        table.add_column("Total P&L", justify="right")
        
        for strategy, stats in sorted(breakdown.items()):
            pnl_color = "green" if stats['total_pnl'] >= 0 else "red"
            
            table.add_row(
                strategy,
                str(stats['total_trades']),
                str(stats['open_positions']),
                str(stats['closed_positions']),
                f"{stats['win_rate']:.1f}%",
                f"{stats['avg_roi']:.2f}%",
                f"[{pnl_color}]${stats['total_pnl']:+,.2f}[/{pnl_color}]"
            )
        
        console.print(table)


# ============================================================================
# REPORTING FUNCTIONS
# ============================================================================

def generate_daily_report(tracker: PnLTracker, output_file: Optional[str] = None):
    """Generate comprehensive daily P&L report"""
    
    open_positions = tracker.get_open_positions()
    closed_positions = tracker.get_closed_positions(days=1)  # Today's closed
    
    open_positions = tracker.update_position_prices(open_positions)
    metrics = tracker.calculate_metrics(open_positions, closed_positions)
    
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append(f"DAILY P&L REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 70)
    report_lines.append("")
    report_lines.append(f"Total P&L: ${metrics.total_pnl:,.2f}")
    report_lines.append(f"  Realized:   ${metrics.total_realized_pnl:,.2f}")
    report_lines.append(f"  Unrealized: ${metrics.total_unrealized_pnl:,.2f}")
    report_lines.append("")
    report_lines.append(f"Open Positions: {metrics.open_positions}")
    report_lines.append(f"Closed Today: {len(closed_positions)}")
    report_lines.append(f"Win Rate: {metrics.win_rate:.1f}%")
    report_lines.append(f"ROI: {metrics.roi:.2f}%")
    report_lines.append("")
    report_lines.append("Strategy Breakdown:")
    for strategy, stats in metrics.strategy_breakdown.items():
        report_lines.append(f"  {strategy}: {stats['total_trades']} trades, ${stats['total_pnl']:+,.2f}")
    report_lines.append("")
    report_lines.append("=" * 70)
    
    report_text = "\n".join(report_lines)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_text)
        console.print(f"[green]✓[/green] Daily report saved to {output_file}")
    else:
        console.print(report_text)
    
    return report_text


def generate_weekly_report(tracker: PnLTracker, output_file: Optional[str] = None):
    """Generate comprehensive weekly P&L report"""
    
    open_positions = tracker.get_open_positions()
    closed_positions = tracker.get_closed_positions(days=7)
    
    open_positions = tracker.update_position_prices(open_positions)
    metrics = tracker.calculate_metrics(open_positions, closed_positions)
    
    # Get historical snapshots
    snapshots = tracker.get_historical_snapshots(days=7)
    
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append(f"WEEKLY P&L REPORT - {datetime.now().strftime('%Y-%m-%d')}")
    report_lines.append("=" * 70)
    report_lines.append("")
    report_lines.append("OVERALL PERFORMANCE")
    report_lines.append("-" * 70)
    report_lines.append(f"Total P&L: ${metrics.total_pnl:,.2f}")
    report_lines.append(f"ROI: {metrics.roi:.2f}%")
    report_lines.append(f"Win Rate: {metrics.win_rate:.1f}% ({metrics.winning_trades}W / {metrics.losing_trades}L)")
    report_lines.append(f"Profit Factor: {metrics.profit_factor:.2f}")
    report_lines.append(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
    report_lines.append(f"Max Drawdown: ${metrics.max_drawdown:,.2f}")
    report_lines.append(f"Avg Hold Time: {metrics.avg_hold_time_hours:.1f} hours")
    report_lines.append("")
    report_lines.append("TRADES THIS WEEK")
    report_lines.append("-" * 70)
    report_lines.append(f"Total: {len(closed_positions)}")
    report_lines.append(f"Average Win: ${metrics.avg_win:,.2f}")
    report_lines.append(f"Average Loss: ${metrics.avg_loss:,.2f}")
    report_lines.append(f"Largest Win: ${metrics.largest_win:,.2f}")
    report_lines.append(f"Largest Loss: ${metrics.largest_loss:,.2f}")
    report_lines.append("")
    report_lines.append("STRATEGY PERFORMANCE")
    report_lines.append("-" * 70)
    for strategy, stats in sorted(metrics.strategy_breakdown.items()):
        report_lines.append(f"{strategy}:")
        report_lines.append(f"  Trades: {stats['total_trades']}")
        report_lines.append(f"  Win Rate: {stats['win_rate']:.1f}%")
        report_lines.append(f"  Avg ROI: {stats['avg_roi']:.2f}%")
        report_lines.append(f"  Total P&L: ${stats['total_pnl']:+,.2f}")
        report_lines.append("")
    
    if snapshots:
        report_lines.append("DAILY PROGRESSION")
        report_lines.append("-" * 70)
        for snap in snapshots:
            report_lines.append(
                f"{snap['snapshot_date']}: "
                f"P&L ${snap['total_pnl']:,.2f} | "
                f"Win Rate {snap['win_rate']:.1f}% | "
                f"ROI {snap['roi']:.2f}%"
            )
    
    report_lines.append("")
    report_lines.append("=" * 70)
    
    report_text = "\n".join(report_lines)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_text)
        console.print(f"[green]✓[/green] Weekly report saved to {output_file}")
    else:
        console.print(report_text)
    
    return report_text


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Polymarket P&L Tracker")
    parser.add_argument(
        'command',
        choices=['dashboard', 'daily', 'weekly', 'export-csv', 'export-json', 'init'],
        help='Command to execute'
    )
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--days', '-d', type=int, default=30, help='Days of history')
    
    args = parser.parse_args()
    
    tracker = PnLTracker()
    
    if args.command == 'init':
        init_pnl_tables()
        console.print("[green]✓[/green] P&L tracking system initialized")
    
    elif args.command == 'dashboard':
        tracker.print_dashboard()
    
    elif args.command == 'daily':
        generate_daily_report(tracker, args.output)
    
    elif args.command == 'weekly':
        generate_weekly_report(tracker, args.output)
    
    elif args.command == 'export-csv':
        filename = args.output or f"pnl_export_{datetime.now().strftime('%Y%m%d')}.csv"
        tracker.export_to_csv(filename)
    
    elif args.command == 'export-json':
        filename = args.output or f"pnl_export_{datetime.now().strftime('%Y%m%d')}.json"
        open_positions = tracker.get_open_positions()
        closed_positions = tracker.get_closed_positions(args.days)
        open_positions = tracker.update_position_prices(open_positions)
        metrics = tracker.calculate_metrics(open_positions, closed_positions)
        tracker.export_to_json(filename, metrics)


if __name__ == "__main__":
    main()
