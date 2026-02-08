"""
Database Models and Utilities for PATS
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import logging

from config import DB_CONFIG

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Trade record"""
    id: Optional[int] = None
    market_id: str = ""
    market_slug: str = ""
    side: str = ""  # "yes" or "no"
    entry_price: Decimal = Decimal("0")
    exit_price: Optional[Decimal] = None
    size: Decimal = Decimal("0")
    pnl: Optional[Decimal] = None
    pnl_pct: Optional[Decimal] = None
    signal_id: Optional[int] = None
    status: str = "open"  # "open", "closed", "cancelled"
    strategy: str = ""
    confidence: Decimal = Decimal("0")
    agent_consensus: int = 0
    created_at: datetime = None
    closed_at: Optional[datetime] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class Signal:
    """Trading signal record"""
    id: Optional[int] = None
    market_id: str = ""
    market_slug: str = ""
    market_question: str = ""
    current_probability: Decimal = Decimal("0")
    suggested_side: str = ""
    suggested_size: Decimal = Decimal("0")
    confidence: Decimal = Decimal("0")
    strategy: str = ""
    agent_votes: Dict[str, Any] = None
    agent_consensus_count: int = 0
    technical_score: Decimal = Decimal("0")
    sentiment_score: Decimal = Decimal("0")
    whale_score: Decimal = Decimal("0")
    bot_score: Decimal = Decimal("0")
    news_score: Decimal = Decimal("0")
    risk_score: Decimal = Decimal("0")
    status: str = "pending"  # "pending", "executed", "rejected", "expired"
    execution_price: Optional[Decimal] = None
    trade_id: Optional[int] = None
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.agent_votes is None:
            self.agent_votes = {}
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MarketData:
    """Market snapshot data"""
    id: Optional[int] = None
    market_id: str = ""
    market_slug: str = ""
    question: str = ""
    probability_yes: Decimal = Decimal("0")
    volume_24h: Decimal = Decimal("0")
    liquidity: Decimal = Decimal("0")
    spread: Decimal = Decimal("0")
    best_bid_yes: Decimal = Decimal("0")
    best_ask_yes: Decimal = Decimal("0")
    best_bid_no: Decimal = Decimal("0")
    best_ask_no: Decimal = Decimal("0")
    unique_traders: int = 0
    whale_activity_score: Decimal = Decimal("0")
    bot_activity_score: Decimal = Decimal("0")
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    id: Optional[int] = None
    date: datetime = None
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: Decimal = Decimal("0")
    avg_profit: Decimal = Decimal("0")
    avg_loss: Decimal = Decimal("0")
    profit_factor: Decimal = Decimal("0")
    sharpe_ratio: Decimal = Decimal("0")
    max_drawdown: Decimal = Decimal("0")
    current_drawdown: Decimal = Decimal("0")
    roi_daily: Decimal = Decimal("0")
    roi_weekly: Decimal = Decimal("0")
    roi_monthly: Decimal = Decimal("0")
    roi_all_time: Decimal = Decimal("0")
    bankroll: Decimal = Decimal("0")
    exposure: Decimal = Decimal("0")
    open_positions: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.date is None:
            self.date = datetime.utcnow().date()

class DatabaseManager:
    """SQLite database manager"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_CONFIG.DB_PATH
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Trades table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {DB_CONFIG.TRADES_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    market_id TEXT NOT NULL,
                    market_slug TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price TEXT NOT NULL,
                    exit_price TEXT,
                    size TEXT NOT NULL,
                    pnl TEXT,
                    pnl_pct TEXT,
                    signal_id INTEGER,
                    status TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    agent_consensus INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    closed_at TIMESTAMP,
                    notes TEXT
                )
            """)
            
            # Signals table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {DB_CONFIG.SIGNALS_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    market_id TEXT NOT NULL,
                    market_slug TEXT NOT NULL,
                    market_question TEXT NOT NULL,
                    current_probability TEXT NOT NULL,
                    suggested_side TEXT NOT NULL,
                    suggested_size TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    agent_votes TEXT,
                    agent_consensus_count INTEGER NOT NULL,
                    technical_score TEXT NOT NULL,
                    sentiment_score TEXT NOT NULL,
                    whale_score TEXT NOT NULL,
                    bot_score TEXT NOT NULL,
                    news_score TEXT NOT NULL,
                    risk_score TEXT NOT NULL,
                    status TEXT NOT NULL,
                    execution_price TEXT,
                    trade_id INTEGER,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Market data table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {DB_CONFIG.MARKET_DATA_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    market_id TEXT NOT NULL,
                    market_slug TEXT NOT NULL,
                    question TEXT NOT NULL,
                    probability_yes TEXT NOT NULL,
                    volume_24h TEXT NOT NULL,
                    liquidity TEXT NOT NULL,
                    spread TEXT NOT NULL,
                    best_bid_yes TEXT NOT NULL,
                    best_ask_yes TEXT NOT NULL,
                    best_bid_no TEXT NOT NULL,
                    best_ask_no TEXT NOT NULL,
                    unique_traders INTEGER NOT NULL,
                    whale_activity_score TEXT NOT NULL,
                    bot_activity_score TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL
                )
            """)
            
            # Performance table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {DB_CONFIG.PERFORMANCE_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    total_trades INTEGER NOT NULL,
                    winning_trades INTEGER NOT NULL,
                    losing_trades INTEGER NOT NULL,
                    win_rate TEXT NOT NULL,
                    avg_profit TEXT NOT NULL,
                    avg_loss TEXT NOT NULL,
                    profit_factor TEXT NOT NULL,
                    sharpe_ratio TEXT NOT NULL,
                    max_drawdown TEXT NOT NULL,
                    current_drawdown TEXT NOT NULL,
                    roi_daily TEXT NOT NULL,
                    roi_weekly TEXT NOT NULL,
                    roi_monthly TEXT NOT NULL,
                    roi_all_time TEXT NOT NULL,
                    bankroll TEXT NOT NULL,
                    exposure TEXT NOT NULL,
                    open_positions INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL
                )
            """)
            
            # Create indexes
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_trades_market ON {DB_CONFIG.TRADES_TABLE}(market_id)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_trades_status ON {DB_CONFIG.TRADES_TABLE}(status)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_signals_status ON {DB_CONFIG.SIGNALS_TABLE}(status)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON {DB_CONFIG.MARKET_DATA_TABLE}(timestamp)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_performance_date ON {DB_CONFIG.PERFORMANCE_TABLE}(date)")
            
            logger.info("Database initialized successfully")
    
    def save_trade(self, trade: Trade) -> int:
        """Save trade to database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {DB_CONFIG.TRADES_TABLE} 
                (market_id, market_slug, side, entry_price, exit_price, size, pnl, pnl_pct,
                 signal_id, status, strategy, confidence, agent_consensus, created_at, closed_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.market_id, trade.market_slug, trade.side, str(trade.entry_price),
                str(trade.exit_price) if trade.exit_price else None, str(trade.size),
                str(trade.pnl) if trade.pnl else None, str(trade.pnl_pct) if trade.pnl_pct else None,
                trade.signal_id, trade.status, trade.strategy, str(trade.confidence),
                trade.agent_consensus, trade.created_at, trade.closed_at, trade.notes
            ))
            return cursor.lastrowid
    
    def update_trade(self, trade: Trade):
        """Update existing trade"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE {DB_CONFIG.TRADES_TABLE}
                SET exit_price = ?, pnl = ?, pnl_pct = ?, status = ?, closed_at = ?, notes = ?
                WHERE id = ?
            """, (
                str(trade.exit_price) if trade.exit_price else None,
                str(trade.pnl) if trade.pnl else None,
                str(trade.pnl_pct) if trade.pnl_pct else None,
                trade.status, trade.closed_at, trade.notes, trade.id
            ))
    
    def save_signal(self, signal: Signal) -> int:
        """Save signal to database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {DB_CONFIG.SIGNALS_TABLE}
                (market_id, market_slug, market_question, current_probability, suggested_side,
                 suggested_size, confidence, strategy, agent_votes, agent_consensus_count,
                 technical_score, sentiment_score, whale_score, bot_score, news_score, risk_score,
                 status, execution_price, trade_id, created_at, expires_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal.market_id, signal.market_slug, signal.market_question,
                str(signal.current_probability), signal.suggested_side, str(signal.suggested_size),
                str(signal.confidence), signal.strategy, json.dumps(signal.agent_votes),
                signal.agent_consensus_count, str(signal.technical_score), str(signal.sentiment_score),
                str(signal.whale_score), str(signal.bot_score), str(signal.news_score),
                str(signal.risk_score), signal.status, str(signal.execution_price) if signal.execution_price else None,
                signal.trade_id, signal.created_at, signal.expires_at, json.dumps(signal.metadata)
            ))
            return cursor.lastrowid
    
    def update_signal(self, signal: Signal):
        """Update existing signal"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE {DB_CONFIG.SIGNALS_TABLE}
                SET status = ?, execution_price = ?, trade_id = ?
                WHERE id = ?
            """, (signal.status, str(signal.execution_price) if signal.execution_price else None,
                  signal.trade_id, signal.id))
    
    def save_market_data(self, data: MarketData) -> int:
        """Save market snapshot"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {DB_CONFIG.MARKET_DATA_TABLE}
                (market_id, market_slug, question, probability_yes, volume_24h, liquidity,
                 spread, best_bid_yes, best_ask_yes, best_bid_no, best_ask_no, unique_traders,
                 whale_activity_score, bot_activity_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.market_id, data.market_slug, data.question, str(data.probability_yes),
                str(data.volume_24h), str(data.liquidity), str(data.spread), str(data.best_bid_yes),
                str(data.best_ask_yes), str(data.best_bid_no), str(data.best_ask_no),
                data.unique_traders, str(data.whale_activity_score), str(data.bot_activity_score),
                data.timestamp
            ))
            return cursor.lastrowid
    
    def save_performance(self, metrics: PerformanceMetrics) -> int:
        """Save performance metrics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT OR REPLACE INTO {DB_CONFIG.PERFORMANCE_TABLE}
                (date, total_trades, winning_trades, losing_trades, win_rate, avg_profit,
                 avg_loss, profit_factor, sharpe_ratio, max_drawdown, current_drawdown,
                 roi_daily, roi_weekly, roi_monthly, roi_all_time, bankroll, exposure,
                 open_positions, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.date, metrics.total_trades, metrics.winning_trades, metrics.losing_trades,
                str(metrics.win_rate), str(metrics.avg_profit), str(metrics.avg_loss),
                str(metrics.profit_factor), str(metrics.sharpe_ratio), str(metrics.max_drawdown),
                str(metrics.current_drawdown), str(metrics.roi_daily), str(metrics.roi_weekly),
                str(metrics.roi_monthly), str(metrics.roi_all_time), str(metrics.bankroll),
                str(metrics.exposure), metrics.open_positions, metrics.timestamp
            ))
            return cursor.lastrowid
    
    def get_open_trades(self) -> List[Trade]:
        """Get all open trades"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {DB_CONFIG.TRADES_TABLE} WHERE status = 'open'")
            rows = cursor.fetchall()
            return [self._row_to_trade(row) for row in rows]
    
    def get_trades_by_date_range(self, start: datetime, end: datetime) -> List[Trade]:
        """Get trades within date range"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {DB_CONFIG.TRADES_TABLE} 
                WHERE created_at >= ? AND created_at <= ?
            """, (start, end))
            rows = cursor.fetchall()
            return [self._row_to_trade(row) for row in rows]
    
    def get_performance_history(self, days: int = 30) -> List[PerformanceMetrics]:
        """Get performance history"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {DB_CONFIG.PERFORMANCE_TABLE}
                WHERE date >= date('now', '-{days} days')
                ORDER BY date DESC
            """)
            rows = cursor.fetchall()
            return [self._row_to_performance(row) for row in rows]
    
    def _row_to_trade(self, row: sqlite3.Row) -> Trade:
        """Convert row to Trade object"""
        return Trade(
            id=row['id'],
            market_id=row['market_id'],
            market_slug=row['market_slug'],
            side=row['side'],
            entry_price=Decimal(row['entry_price']),
            exit_price=Decimal(row['exit_price']) if row['exit_price'] else None,
            size=Decimal(row['size']),
            pnl=Decimal(row['pnl']) if row['pnl'] else None,
            pnl_pct=Decimal(row['pnl_pct']) if row['pnl_pct'] else None,
            signal_id=row['signal_id'],
            status=row['status'],
            strategy=row['strategy'],
            confidence=Decimal(row['confidence']),
            agent_consensus=row['agent_consensus'],
            created_at=datetime.fromisoformat(row['created_at']),
            closed_at=datetime.fromisoformat(row['closed_at']) if row['closed_at'] else None,
            notes=row['notes'] or ""
        )
    
    def _row_to_performance(self, row: sqlite3.Row) -> PerformanceMetrics:
        """Convert row to PerformanceMetrics object"""
        return PerformanceMetrics(
            id=row['id'],
            date=datetime.fromisoformat(row['date']).date(),
            total_trades=row['total_trades'],
            winning_trades=row['winning_trades'],
            losing_trades=row['losing_trades'],
            win_rate=Decimal(row['win_rate']),
            avg_profit=Decimal(row['avg_profit']),
            avg_loss=Decimal(row['avg_loss']),
            profit_factor=Decimal(row['profit_factor']),
            sharpe_ratio=Decimal(row['sharpe_ratio']),
            max_drawdown=Decimal(row['max_drawdown']),
            current_drawdown=Decimal(row['current_drawdown']),
            roi_daily=Decimal(row['roi_daily']),
            roi_weekly=Decimal(row['roi_weekly']),
            roi_monthly=Decimal(row['roi_monthly']),
            roi_all_time=Decimal(row['roi_all_time']),
            bankroll=Decimal(row['bankroll']),
            exposure=Decimal(row['exposure']),
            open_positions=row['open_positions'],
            timestamp=datetime.fromisoformat(row['timestamp'])
        )
    
    def cleanup_old_data(self):
        """Remove old data based on retention policy"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Clean market data older than retention period
            cursor.execute(f"""
                DELETE FROM {DB_CONFIG.MARKET_DATA_TABLE}
                WHERE timestamp < datetime('now', '-{DB_CONFIG.RAW_DATA_RETENTION_DAYS} days')
            """)
            
            # Clean old signals
            cursor.execute(f"""
                DELETE FROM {DB_CONFIG.SIGNALS_TABLE}
                WHERE status IN ('rejected', 'expired')
                AND created_at < datetime('now', '-{DB_CONFIG.RAW_DATA_RETENTION_DAYS} days')
            """)
            
            logger.info(f"Cleaned up old data. Rows affected: {cursor.rowcount}")

# Global database manager instance
db_manager = DatabaseManager()
