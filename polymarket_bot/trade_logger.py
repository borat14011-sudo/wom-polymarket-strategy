"""
Trade Logger for Polymarket Trading Bot
Logs all trades to SQLite database
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import time

@dataclass
class TradeRecord:
    """Represents a trade record for logging"""
    timestamp: str
    market: str
    token_id: str
    side: str  # "BUY" or "SELL"
    price: float
    size: float
    cost: float
    order_id: str
    status: str  # "PENDING", "FILLED", "CANCELLED", "EXPIRED"
    resolution: Optional[str] = None  # "YES", "NO", or None if unresolved
    pnl: Optional[float] = None  # Profit/loss in USDC
    notes: Optional[str] = None

class TradeLogger:
    """Manages trade logging to SQLite database"""
    
    def __init__(self, db_path: str = "trades.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create trades table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            market TEXT NOT NULL,
            token_id TEXT NOT NULL,
            side TEXT NOT NULL,
            price REAL NOT NULL,
            size REAL NOT NULL,
            cost REAL NOT NULL,
            order_id TEXT NOT NULL,
            status TEXT NOT NULL,
            resolution TEXT,
            pnl REAL,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON trades(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_id ON trades(order_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON trades(status)')
        
        conn.commit()
        conn.close()
        
        print(f"Database initialized at {self.db_path}")
    
    def log_trade(self, trade: TradeRecord) -> int:
        """
        Log a trade to the database
        
        Args:
            trade: TradeRecord object
            
        Returns:
            trade_id: The ID of the inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO trades 
            (timestamp, market, token_id, side, price, size, cost, order_id, status, resolution, pnl, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.timestamp,
                trade.market,
                trade.token_id,
                trade.side,
                trade.price,
                trade.size,
                trade.cost,
                trade.order_id,
                trade.status,
                trade.resolution,
                trade.pnl,
                trade.notes
            ))
            
            trade_id = cursor.lastrowid
            conn.commit()
            
            print(f"Trade logged: ID={trade_id}, Order={trade.order_id}, Status={trade.status}")
            return trade_id
            
        except sqlite3.Error as e:
            print(f"Error logging trade: {e}")
            conn.rollback()
            return -1
        finally:
            conn.close()
    
    def update_trade_status(self, order_id: str, status: str, notes: Optional[str] = None) -> bool:
        """Update the status of a trade"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if notes:
                cursor.execute('''
                UPDATE trades 
                SET status = ?, notes = COALESCE(?, notes)
                WHERE order_id = ?
                ''', (status, notes, order_id))
            else:
                cursor.execute('''
                UPDATE trades 
                SET status = ?
                WHERE order_id = ?
                ''', (status, order_id))
            
            rows_updated = cursor.rowcount
            conn.commit()
            
            if rows_updated > 0:
                print(f"Trade {order_id} status updated to {status}")
                return True
            else:
                print(f"No trade found with order_id {order_id}")
                return False
                
        except sqlite3.Error as e:
            print(f"Error updating trade status: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_trade_resolution(self, order_id: str, resolution: str, pnl: float) -> bool:
        """Update trade with resolution and P&L"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE trades 
            SET resolution = ?, pnl = ?
            WHERE order_id = ?
            ''', (resolution, pnl, order_id))
            
            rows_updated = cursor.rowcount
            conn.commit()
            
            if rows_updated > 0:
                print(f"Trade {order_id} resolved: {resolution}, P&L=${pnl:.4f}")
                return True
            else:
                print(f"No trade found with order_id {order_id}")
                return False
                
        except sqlite3.Error as e:
            print(f"Error updating trade resolution: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_trade(self, order_id: str) -> Optional[Dict]:
        """Get a specific trade by order ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM trades WHERE order_id = ?', (order_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
                
        except sqlite3.Error as e:
            print(f"Error fetching trade: {e}")
            return None
        finally:
            conn.close()
    
    def get_open_trades(self) -> List[Dict]:
        """Get all open (pending) trades"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT * FROM trades 
            WHERE status IN ('PENDING', 'PARTIALLY_FILLED')
            ORDER BY timestamp DESC
            ''')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
                
        except sqlite3.Error as e:
            print(f"Error fetching open trades: {e}")
            return []
        finally:
            conn.close()
    
    def get_trade_stats(self) -> Dict[str, Any]:
        """Get trading statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        try:
            # Total trades
            cursor.execute('SELECT COUNT(*) FROM trades')
            stats['total_trades'] = cursor.fetchone()[0]
            
            # Open trades
            cursor.execute('SELECT COUNT(*) FROM trades WHERE status IN ("PENDING", "PARTIALLY_FILLED")')
            stats['open_trades'] = cursor.fetchone()[0]
            
            # Closed trades
            cursor.execute('SELECT COUNT(*) FROM trades WHERE status IN ("FILLED", "CANCELLED", "EXPIRED")')
            stats['closed_trades'] = cursor.fetchone()[0]
            
            # Total P&L
            cursor.execute('SELECT SUM(pnl) FROM trades WHERE pnl IS NOT NULL')
            total_pnl = cursor.fetchone()[0]
            stats['total_pnl'] = total_pnl if total_pnl else 0.0
            
            # Win rate
            cursor.execute('SELECT COUNT(*) FROM trades WHERE pnl > 0')
            winning_trades = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM trades WHERE pnl IS NOT NULL')
            resolved_trades = cursor.fetchone()[0]
            
            if resolved_trades > 0:
                stats['win_rate'] = (winning_trades / resolved_trades) * 100
            else:
                stats['win_rate'] = 0.0
            
            # Average P&L per trade
            if resolved_trades > 0:
                stats['avg_pnl'] = stats['total_pnl'] / resolved_trades
            else:
                stats['avg_pnl'] = 0.0
            
            # Recent trades
            cursor.execute('''
            SELECT timestamp, market, side, price, size, pnl 
            FROM trades 
            ORDER BY timestamp DESC 
            LIMIT 5
            ''')
            
            recent_trades = []
            for row in cursor.fetchall():
                recent_trades.append({
                    'timestamp': row[0],
                    'market': row[1],
                    'side': row[2],
                    'price': row[3],
                    'size': row[4],
                    'pnl': row[5]
                })
            
            stats['recent_trades'] = recent_trades
            
        except sqlite3.Error as e:
            print(f"Error calculating trade stats: {e}")
        
        finally:
            conn.close()
        
        return stats
    
    def export_to_csv(self, filepath: str = "trades_export.csv") -> bool:
        """Export all trades to CSV file"""
        import csv
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM trades')
            rows = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(column_names)
                writer.writerows(rows)
            
            print(f"Exported {len(rows)} trades to {filepath}")
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
        finally:
            conn.close()
    
    def print_stats(self):
        """Print trading statistics"""
        stats = self.get_trade_stats()
        
        print("\n" + "="*60)
        print("TRADING STATISTICS")
        print("="*60)
        
        print(f"\nTotal Trades: {stats['total_trades']}")
        print(f"Open Trades: {stats['open_trades']}")
        print(f"Closed Trades: {stats['closed_trades']}")
        print(f"\nTotal P&L: ${stats['total_pnl']:.4f}")
        print(f"Average P&L per Trade: ${stats['avg_pnl']:.4f}")
        print(f"Win Rate: {stats['win_rate']:.1f}%")
        
        if stats['recent_trades']:
            print(f"\nRecent Trades:")
            for trade in stats['recent_trades']:
                pnl_str = f"${trade['pnl']:.4f}" if trade['pnl'] is not None else "Pending"
                print(f"  {trade['timestamp']}: {trade['market'][:40]}... {trade['side']} @ ${trade['price']} ({trade['size']} shares) P&L: {pnl_str}")

def create_trade_record_from_order(market: str, token_id: str, side: str, 
                                  price: float, size: float, order_id: str) -> TradeRecord:
    """Helper function to create a TradeRecord from order details"""
    return TradeRecord(
        timestamp=datetime.utcnow().isoformat(),
        market=market,
        token_id=token_id,
        side=side,
        price=price,
        size=size,
        cost=price * size,
        order_id=order_id,
        status="PENDING"
    )

if __name__ == "__main__":
    # Test the logger
    logger = TradeLogger("test_trades.db")
    
    # Create a test trade
    test_trade = TradeRecord(
        timestamp=datetime.utcnow().isoformat(),
        market="Test Market: Will X happen?",
        token_id="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        side="BUY",
        price=0.15,
        size=1.33,  # $0.20 cost
        cost=0.1995,
        order_id="test_order_123",
        status="PENDING"
    )
    
    # Log the test trade
    trade_id = logger.log_trade(test_trade)
    print(f"Test trade logged with ID: {trade_id}")
    
    # Print stats
    logger.print_stats()