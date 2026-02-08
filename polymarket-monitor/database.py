"""
Database setup and management for Polymarket monitor
"""
import sqlite3
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

DB_PATH = "polymarket_data.db"

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Market snapshots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            volume REAL NOT NULL,
            liquidity REAL,
            timestamp INTEGER NOT NULL
        )
    """)
    
    # Create index for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_market_timestamp 
        ON market_snapshots(market_id, timestamp)
    """)
    
    # Signals table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id TEXT NOT NULL,
            market_name TEXT NOT NULL,
            rvr REAL NOT NULL,
            roc REAL NOT NULL,
            price REAL NOT NULL,
            volume REAL NOT NULL,
            timestamp INTEGER NOT NULL,
            alerted INTEGER DEFAULT 0
        )
    """)
    
    # Create index for checking duplicates
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_signals_market_time 
        ON signals(market_id, timestamp)
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def insert_market_snapshot(market_id, name, price, volume, liquidity):
    """Insert a market snapshot into the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = int(datetime.now().timestamp())
    
    cursor.execute("""
        INSERT INTO market_snapshots (market_id, name, price, volume, liquidity, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (market_id, name, price, volume, liquidity, timestamp))
    
    conn.commit()
    conn.close()


def get_market_history(market_id, hours=24):
    """Get historical data for a market"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_time = int((datetime.now() - timedelta(hours=hours)).timestamp())
    
    cursor.execute("""
        SELECT price, volume, timestamp
        FROM market_snapshots
        WHERE market_id = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    """, (market_id, cutoff_time))
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows


def insert_signal(market_id, market_name, rvr, roc, price, volume):
    """Insert a new signal"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = int(datetime.now().timestamp())
    
    cursor.execute("""
        INSERT INTO signals (market_id, market_name, rvr, roc, price, volume, timestamp, alerted)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
    """, (market_id, market_name, rvr, roc, price, volume, timestamp))
    
    signal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return signal_id


def mark_signal_alerted(signal_id):
    """Mark a signal as alerted"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE signals SET alerted = 1 WHERE id = ?
    """, (signal_id,))
    
    conn.commit()
    conn.close()


def get_unalerted_signals():
    """Get all signals that haven't been alerted yet"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, market_id, market_name, rvr, roc, price, volume, timestamp
        FROM signals
        WHERE alerted = 0
        ORDER BY timestamp DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows


def check_recent_signal(market_id, hours=6):
    """Check if we already alerted for this market recently (avoid spam)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_time = int((datetime.now() - timedelta(hours=hours)).timestamp())
    
    cursor.execute("""
        SELECT COUNT(*) FROM signals
        WHERE market_id = ? AND timestamp >= ?
    """, (market_id, cutoff_time))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0


def cleanup_old_data(days=7):
    """Delete data older than specified days"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp())
    
    cursor.execute("""
        DELETE FROM market_snapshots WHERE timestamp < ?
    """, (cutoff_time,))
    
    deleted_snapshots = cursor.rowcount
    
    cursor.execute("""
        DELETE FROM signals WHERE timestamp < ?
    """, (cutoff_time,))
    
    deleted_signals = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    logger.info(f"Cleaned up {deleted_snapshots} old snapshots and {deleted_signals} old signals")
    
    return deleted_snapshots, deleted_signals
