"""
Paper Trading Database Schema
All tables and utilities for forward paper trading system
"""

import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DB_PATH = "polymarket_data.db"


def init_paper_trading_tables():
    """Initialize all paper trading tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Paper trades table - main tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id TEXT NOT NULL,
            market_name TEXT NOT NULL,
            side TEXT NOT NULL,
            entry_price REAL NOT NULL,
            position_size REAL NOT NULL,
            entry_time INTEGER NOT NULL,
            
            stop_loss REAL NOT NULL,
            take_profit_1 REAL,
            take_profit_2 REAL,
            take_profit_3 REAL,
            
            rvr_ratio REAL,
            roc_24h_pct REAL,
            days_to_resolution INTEGER,
            orderbook_depth REAL,
            
            status TEXT DEFAULT 'OPEN',
            exit_price REAL,
            exit_time INTEGER,
            exit_reason TEXT,
            pnl_dollars REAL DEFAULT 0.0,
            pnl_percent REAL DEFAULT 0.0,
            
            resolved INTEGER DEFAULT 0,
            resolution_outcome TEXT,
            resolution_time INTEGER,
            trade_correct INTEGER,
            theoretical_edge REAL,
            actual_edge REAL
        )
    """)
    
    # Position ticks - price movements
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_position_ticks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            current_price REAL NOT NULL,
            pnl_unrealized REAL NOT NULL,
            pnl_pct REAL NOT NULL,
            market_volume_24h REAL,
            orderbook_depth REAL,
            FOREIGN KEY (trade_id) REFERENCES paper_trades(id)
        )
    """)
    
    # Market resolutions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_resolutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id TEXT UNIQUE NOT NULL,
            market_name TEXT NOT NULL,
            resolution_time INTEGER NOT NULL,
            resolution_outcome TEXT NOT NULL,
            final_yes_price REAL,
            final_no_price REAL,
            total_volume REAL,
            resolution_source TEXT,
            num_paper_trades INTEGER DEFAULT 0,
            num_correct_trades INTEGER DEFAULT 0,
            avg_roi REAL
        )
    """)
    
    # Validation metrics snapshots
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS validation_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date TEXT NOT NULL UNIQUE,
            
            total_trades INTEGER DEFAULT 0,
            total_resolved INTEGER DEFAULT 0,
            total_open INTEGER DEFAULT 0,
            
            win_rate REAL,
            avg_roi REAL,
            total_pnl REAL,
            
            yes_side_win_rate REAL,
            no_side_win_rate REAL,
            politics_win_rate REAL,
            crypto_win_rate REAL,
            
            depth_filter_effective REAL,
            trend_filter_effective REAL,
            rvr_filter_effective REAL,
            
            theoretical_edge REAL,
            realized_edge REAL,
            edge_gap REAL
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_paper_trades_status ON paper_trades(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_paper_trades_market ON paper_trades(market_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticks_trade ON paper_position_ticks(trade_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticks_time ON paper_position_ticks(timestamp)")
    
    conn.commit()
    conn.close()
    
    logger.info("Paper trading tables initialized successfully")
    print("[OK] Paper trading database initialized")


if __name__ == "__main__":
    init_paper_trading_tables()
