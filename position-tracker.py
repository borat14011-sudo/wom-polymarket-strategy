#!/usr/bin/env python3
"""
Position Tracker for Polymarket Trading System
Real-time position tracking with P&L monitoring, alerts, and historical snapshots.
"""

import sqlite3
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import sys


@dataclass
class Position:
    """Represents an open trading position"""
    position_id: int
    market_id: str
    entry_price: float
    current_price: float
    size: float
    entry_time: str
    last_update: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    sector: Optional[str] = None
    
    @property
    def unrealized_pnl(self) -> float:
        """Calculate unrealized profit/loss"""
        return (self.current_price - self.entry_price) * self.size
    
    @property
    def unrealized_pnl_pct(self) -> float:
        """Calculate unrealized P&L as percentage"""
        if self.entry_price == 0:
            return 0.0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100
    
    @property
    def position_value(self) -> float:
        """Current position value"""
        return self.current_price * self.size
    
    @property
    def time_in_position(self) -> timedelta:
        """How long the position has been open"""
        entry = datetime.fromisoformat(self.entry_time)
        now = datetime.now()
        return now - entry


@dataclass
class ClosedPosition:
    """Represents a closed trading position"""
    position_id: int
    market_id: str
    entry_price: float
    exit_price: float
    size: float
    entry_time: str
    exit_time: str
    realized_pnl: float
    sector: Optional[str] = None


class PositionTracker:
    """
    Real-time position tracking system for Polymarket trading.
    
    Features:
    - Track open positions with real-time P&L
    - Portfolio summary and analytics
    - Alert system for stop loss/take profit
    - Historical snapshots for analysis
    """
    
    def __init__(self, db_path: str = "positions.db", bankroll: float = 10000.0):
        self.db_path = db_path
        self.bankroll = bankroll
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Open positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                position_id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_id TEXT NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL NOT NULL,
                size REAL NOT NULL,
                entry_time TEXT NOT NULL,
                last_update TEXT NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                sector TEXT
            )
        """)
        
        # Closed positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS closed_positions (
                position_id INTEGER PRIMARY KEY,
                market_id TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                size REAL NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT NOT NULL,
                realized_pnl REAL NOT NULL,
                sector TEXT
            )
        """)
        
        # Historical snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_value REAL NOT NULL,
                unrealized_pnl REAL NOT NULL,
                realized_pnl REAL NOT NULL,
                cash_balance REAL NOT NULL,
                position_count INTEGER NOT NULL,
                snapshot_data TEXT NOT NULL
            )
        """)
        
        # Cash balance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cash_balance (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                balance REAL NOT NULL,
                last_update TEXT NOT NULL
            )
        """)
        
        # Initialize cash balance if not exists
        cursor.execute("SELECT balance FROM cash_balance WHERE id = 1")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO cash_balance (id, balance, last_update)
                VALUES (1, ?, ?)
            """, (self.bankroll, datetime.now().isoformat()))
        
        self.conn.commit()
    
    def open_position(
        self,
        market_id: str,
        entry_price: float,
        size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        sector: Optional[str] = None
    ) -> int:
        """
        Open a new position
        
        Args:
            market_id: Unique market identifier
            entry_price: Entry price per share
            size: Number of shares
            stop_loss: Optional stop loss price
            take_profit: Optional take profit price
            sector: Optional sector/category
            
        Returns:
            Position ID
        """
        now = datetime.now().isoformat()
        cost = entry_price * size
        
        # Check if we have enough cash
        cash = self.get_cash_balance()
        if cost > cash:
            raise ValueError(f"Insufficient funds. Need ${cost:.2f}, have ${cash:.2f}")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO positions 
            (market_id, entry_price, current_price, size, entry_time, last_update, 
             stop_loss, take_profit, sector)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (market_id, entry_price, entry_price, size, now, now, 
              stop_loss, take_profit, sector))
        
        position_id = cursor.lastrowid
        
        # Deduct from cash balance
        self._update_cash_balance(cash - cost)
        
        self.conn.commit()
        print(f"✓ Opened position {position_id} for {market_id} @ ${entry_price:.4f} x {size} shares")
        return position_id
    
    def close_position(self, position_id: int, exit_price: float) -> float:
        """
        Close a position and calculate realized P&L
        
        Args:
            position_id: Position to close
            exit_price: Exit price per share
            
        Returns:
            Realized P&L
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE position_id = ?", (position_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"Position {position_id} not found")
        
        pos = self._row_to_position(row)
        realized_pnl = (exit_price - pos.entry_price) * pos.size
        exit_time = datetime.now().isoformat()
        
        # Move to closed positions
        cursor.execute("""
            INSERT INTO closed_positions 
            (position_id, market_id, entry_price, exit_price, size, 
             entry_time, exit_time, realized_pnl, sector)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (position_id, pos.market_id, pos.entry_price, exit_price, pos.size,
              pos.entry_time, exit_time, realized_pnl, pos.sector))
        
        # Delete from open positions
        cursor.execute("DELETE FROM positions WHERE position_id = ?", (position_id,))
        
        # Add proceeds to cash balance
        proceeds = exit_price * pos.size
        cash = self.get_cash_balance()
        self._update_cash_balance(cash + proceeds)
        
        self.conn.commit()
        
        pnl_pct = ((exit_price - pos.entry_price) / pos.entry_price) * 100
        print(f"✓ Closed position {position_id}: P&L ${realized_pnl:+.2f} ({pnl_pct:+.2f}%)")
        return realized_pnl
    
    def update_price(self, position_id: int, current_price: float):
        """Update current price for a position"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE positions 
            SET current_price = ?, last_update = ?
            WHERE position_id = ?
        """, (current_price, datetime.now().isoformat(), position_id))
        self.conn.commit()
    
    def update_prices(self, price_map: Optional[Dict[str, float]] = None):
        """
        Update prices for all positions
        
        Args:
            price_map: Dict of market_id -> current_price
                      If None, prices remain unchanged (manual update needed)
        """
        if not price_map:
            # In real implementation, fetch from Polymarket API
            print("⚠ No price map provided. Use tracker.update_price() for manual updates.")
            return
        
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        for market_id, price in price_map.items():
            cursor.execute("""
                UPDATE positions 
                SET current_price = ?, last_update = ?
                WHERE market_id = ?
            """, (price, now, market_id))
        
        self.conn.commit()
        print(f"✓ Updated prices for {len(price_map)} markets")
    
    def get_position(self, position_id: int) -> Optional[Position]:
        """Get a specific position by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE position_id = ?", (position_id,))
        row = cursor.fetchone()
        return self._row_to_position(row) if row else None
    
    def get_all_positions(self) -> List[Position]:
        """Get all open positions"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM positions ORDER BY entry_time DESC")
        return [self._row_to_position(row) for row in cursor.fetchall()]
    
    def get_cash_balance(self) -> float:
        """Get current cash balance"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT balance FROM cash_balance WHERE id = 1")
        row = cursor.fetchone()
        return row['balance'] if row else self.bankroll
    
    def _update_cash_balance(self, new_balance: float):
        """Update cash balance"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE cash_balance 
            SET balance = ?, last_update = ?
            WHERE id = 1
        """, (new_balance, datetime.now().isoformat()))
    
    def get_summary(self) -> Dict:
        """
        Get comprehensive portfolio summary
        
        Returns:
            Dict with portfolio metrics
        """
        positions = self.get_all_positions()
        cash = self.get_cash_balance()
        
        total_position_value = sum(p.position_value for p in positions)
        unrealized_pnl = sum(p.unrealized_pnl for p in positions)
        
        # Get realized P&L from closed positions
        cursor = self.conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(realized_pnl), 0) as total FROM closed_positions")
        realized_pnl = cursor.fetchone()['total']
        
        total_value = cash + total_position_value
        total_pnl = unrealized_pnl + realized_pnl
        
        # Exposure by sector
        exposure_by_sector = defaultdict(float)
        for p in positions:
            sector = p.sector or "Unknown"
            exposure_by_sector[sector] += p.position_value
        
        return {
            'total_value': total_value,
            'cash_balance': cash,
            'position_value': total_position_value,
            'unrealized_pnl': unrealized_pnl,
            'realized_pnl': realized_pnl,
            'total_pnl': total_pnl,
            'total_pnl_pct': (total_pnl / self.bankroll) * 100 if self.bankroll else 0,
            'position_count': len(positions),
            'exposure_by_sector': dict(exposure_by_sector),
            'bankroll': self.bankroll
        }
    
    def get_pnl_breakdown(self) -> Dict:
        """Get detailed P&L breakdown by position"""
        positions = self.get_all_positions()
        
        breakdown = {
            'open_positions': [],
            'unrealized_total': 0.0
        }
        
        for p in positions:
            breakdown['open_positions'].append({
                'position_id': p.position_id,
                'market_id': p.market_id,
                'entry_price': p.entry_price,
                'current_price': p.current_price,
                'size': p.size,
                'unrealized_pnl': p.unrealized_pnl,
                'unrealized_pnl_pct': p.unrealized_pnl_pct,
                'sector': p.sector
            })
            breakdown['unrealized_total'] += p.unrealized_pnl
        
        # Get closed positions
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM closed_positions 
            ORDER BY exit_time DESC 
            LIMIT 20
        """)
        
        breakdown['closed_positions'] = []
        breakdown['realized_total'] = 0.0
        
        for row in cursor.fetchall():
            breakdown['closed_positions'].append({
                'position_id': row['position_id'],
                'market_id': row['market_id'],
                'entry_price': row['entry_price'],
                'exit_price': row['exit_price'],
                'size': row['size'],
                'realized_pnl': row['realized_pnl'],
                'exit_time': row['exit_time'],
                'sector': row['sector']
            })
            breakdown['realized_total'] += row['realized_pnl']
        
        return breakdown
    
    def check_alerts(self) -> List[Dict]:
        """
        Check for alert conditions
        
        Returns:
            List of alert dictionaries
        """
        positions = self.get_all_positions()
        alerts = []
        
        for p in positions:
            # Stop loss alert
            if p.stop_loss and p.current_price <= p.stop_loss:
                alerts.append({
                    'type': 'STOP_LOSS',
                    'severity': 'HIGH',
                    'position_id': p.position_id,
                    'market_id': p.market_id,
                    'current_price': p.current_price,
                    'trigger_price': p.stop_loss,
                    'message': f"Position {p.position_id} hit stop loss at ${p.current_price:.4f}"
                })
            
            # Approaching stop loss (within 5%)
            elif p.stop_loss and p.current_price <= p.stop_loss * 1.05:
                alerts.append({
                    'type': 'APPROACHING_STOP_LOSS',
                    'severity': 'MEDIUM',
                    'position_id': p.position_id,
                    'market_id': p.market_id,
                    'current_price': p.current_price,
                    'trigger_price': p.stop_loss,
                    'message': f"Position {p.position_id} approaching stop loss"
                })
            
            # Take profit alert
            if p.take_profit and p.current_price >= p.take_profit:
                alerts.append({
                    'type': 'TAKE_PROFIT',
                    'severity': 'HIGH',
                    'position_id': p.position_id,
                    'market_id': p.market_id,
                    'current_price': p.current_price,
                    'trigger_price': p.take_profit,
                    'message': f"Position {p.position_id} hit take profit at ${p.current_price:.4f}"
                })
            
            # Unusual P&L swing (>20% or <-20%)
            if abs(p.unrealized_pnl_pct) > 20:
                severity = 'HIGH' if p.unrealized_pnl_pct < -20 else 'MEDIUM'
                alerts.append({
                    'type': 'UNUSUAL_PNL_SWING',
                    'severity': severity,
                    'position_id': p.position_id,
                    'market_id': p.market_id,
                    'unrealized_pnl_pct': p.unrealized_pnl_pct,
                    'unrealized_pnl': p.unrealized_pnl,
                    'message': f"Position {p.position_id} P&L at {p.unrealized_pnl_pct:+.2f}%"
                })
        
        return alerts
    
    def create_snapshot(self) -> int:
        """
        Create a historical snapshot of current portfolio state
        
        Returns:
            Snapshot ID
        """
        summary = self.get_summary()
        positions = self.get_all_positions()
        
        snapshot_data = {
            'summary': summary,
            'positions': [asdict(p) for p in positions]
        }
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO snapshots 
            (timestamp, total_value, unrealized_pnl, realized_pnl, 
             cash_balance, position_count, snapshot_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            summary['total_value'],
            summary['unrealized_pnl'],
            summary['realized_pnl'],
            summary['cash_balance'],
            summary['position_count'],
            json.dumps(snapshot_data)
        ))
        
        snapshot_id = cursor.lastrowid
        self.conn.commit()
        return snapshot_id
    
    def get_history(self, days: int = 7) -> List[Dict]:
        """
        Get historical snapshots
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of snapshot dictionaries
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM snapshots 
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (cutoff,))
        
        snapshots = []
        for row in cursor.fetchall():
            snapshots.append({
                'snapshot_id': row['snapshot_id'],
                'timestamp': row['timestamp'],
                'total_value': row['total_value'],
                'unrealized_pnl': row['unrealized_pnl'],
                'realized_pnl': row['realized_pnl'],
                'cash_balance': row['cash_balance'],
                'position_count': row['position_count'],
                'data': json.loads(row['snapshot_data'])
            })
        
        return snapshots
    
    def _row_to_position(self, row: sqlite3.Row) -> Position:
        """Convert database row to Position object"""
        return Position(
            position_id=row['position_id'],
            market_id=row['market_id'],
            entry_price=row['entry_price'],
            current_price=row['current_price'],
            size=row['size'],
            entry_time=row['entry_time'],
            last_update=row['last_update'],
            stop_loss=row['stop_loss'],
            take_profit=row['take_profit'],
            sector=row['sector']
        )
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def format_table(headers: List[str], rows: List[List], alignments: Optional[List[str]] = None):
    """Format data as a text table"""
    if not rows:
        return ""
    
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    # Format rows
    alignments = alignments or ['<'] * len(headers)
    separator = "─" * (sum(widths) + len(widths) * 3 + 1)
    
    lines = [separator]
    
    # Header
    header_line = "│ "
    for i, h in enumerate(headers):
        header_line += f"{h:{alignments[i]}{widths[i]}} │ "
    lines.append(header_line.rstrip())
    lines.append(separator)
    
    # Data rows
    for row in rows:
        line = "│ "
        for i, cell in enumerate(row):
            line += f"{str(cell):{alignments[i]}{widths[i]}} │ "
        lines.append(line.rstrip())
    
    lines.append(separator)
    return "\n".join(lines)


def cmd_list(tracker: PositionTracker):
    """List all open positions"""
    positions = tracker.get_all_positions()
    
    if not positions:
        print("No open positions.")
        return
    
    rows = []
    for p in positions:
        time_held = str(p.time_in_position).split('.')[0]  # Remove microseconds
        rows.append([
            p.position_id,
            p.market_id[:30],
            f"${p.entry_price:.4f}",
            f"${p.current_price:.4f}",
            f"{p.size:.2f}",
            f"${p.unrealized_pnl:+.2f}",
            f"{p.unrealized_pnl_pct:+.2f}%",
            time_held
        ])
    
    headers = ["ID", "Market", "Entry", "Current", "Size", "P&L ($)", "P&L (%)", "Time"]
    alignments = ['>', '<', '>', '>', '>', '>', '>', '>']
    
    print("\n📊 Open Positions")
    print(format_table(headers, rows, alignments))
    
    # Check alerts
    alerts = tracker.check_alerts()
    if alerts:
        print("\n⚠️  Active Alerts:")
        for alert in alerts:
            emoji = "🚨" if alert['severity'] == 'HIGH' else "⚡"
            print(f"  {emoji} {alert['message']}")


def cmd_summary(tracker: PositionTracker):
    """Show portfolio summary"""
    summary = tracker.get_summary()
    
    print("\n💼 Portfolio Summary")
    print("═" * 60)
    print(f"Total Value:       ${summary['total_value']:>12,.2f}")
    print(f"Cash Balance:      ${summary['cash_balance']:>12,.2f}")
    print(f"Position Value:    ${summary['position_value']:>12,.2f}")
    print(f"─" * 60)
    print(f"Unrealized P&L:    ${summary['unrealized_pnl']:>+12,.2f}")
    print(f"Realized P&L:      ${summary['realized_pnl']:>+12,.2f}")
    print(f"Total P&L:         ${summary['total_pnl']:>+12,.2f}  ({summary['total_pnl_pct']:+.2f}%)")
    print(f"─" * 60)
    print(f"Open Positions:    {summary['position_count']:>12}")
    print(f"Starting Bankroll: ${summary['bankroll']:>12,.2f}")
    
    if summary['exposure_by_sector']:
        print(f"\n📂 Exposure by Sector:")
        for sector, value in sorted(summary['exposure_by_sector'].items(), 
                                    key=lambda x: x[1], reverse=True):
            pct = (value / summary['total_value']) * 100 if summary['total_value'] else 0
            print(f"  {sector:>15}: ${value:>10,.2f}  ({pct:>5.1f}%)")


def cmd_pnl(tracker: PositionTracker):
    """Show P&L breakdown"""
    breakdown = tracker.get_pnl_breakdown()
    
    print("\n💰 P&L Breakdown")
    print("═" * 60)
    
    # Open positions
    if breakdown['open_positions']:
        print("\n📈 Open Positions:")
        rows = []
        for p in breakdown['open_positions']:
            rows.append([
                p['position_id'],
                p['market_id'][:25],
                f"${p['unrealized_pnl']:+.2f}",
                f"{p['unrealized_pnl_pct']:+.2f}%"
            ])
        
        headers = ["ID", "Market", "Unrealized P&L", "P&L %"]
        alignments = ['>', '<', '>', '>']
        print(format_table(headers, rows, alignments))
        print(f"Total Unrealized: ${breakdown['unrealized_total']:+.2f}")
    
    # Recent closed positions
    if breakdown['closed_positions']:
        print("\n📊 Recent Closed Positions (Last 20):")
        rows = []
        for p in breakdown['closed_positions']:
            pnl_pct = ((p['exit_price'] - p['entry_price']) / p['entry_price']) * 100
            exit_time = datetime.fromisoformat(p['exit_time']).strftime('%Y-%m-%d %H:%M')
            rows.append([
                p['position_id'],
                p['market_id'][:25],
                f"${p['realized_pnl']:+.2f}",
                f"{pnl_pct:+.2f}%",
                exit_time
            ])
        
        headers = ["ID", "Market", "Realized P&L", "P&L %", "Closed At"]
        alignments = ['>', '<', '>', '>', '<']
        print(format_table(headers, rows, alignments))
        print(f"Total Realized: ${breakdown['realized_total']:+.2f}")


def cmd_history(tracker: PositionTracker, days: int = 7):
    """Show historical snapshots"""
    snapshots = tracker.get_history(days)
    
    if not snapshots:
        print(f"No snapshots found in the last {days} days.")
        print("Tip: Use tracker.create_snapshot() to capture portfolio state")
        return
    
    print(f"\n📅 Portfolio History (Last {days} Days)")
    print("═" * 80)
    
    rows = []
    for s in snapshots:
        timestamp = datetime.fromisoformat(s['timestamp']).strftime('%Y-%m-%d %H:%M')
        rows.append([
            timestamp,
            f"${s['total_value']:,.2f}",
            f"${s['unrealized_pnl']:+.2f}",
            f"${s['realized_pnl']:+.2f}",
            s['position_count']
        ])
    
    headers = ["Timestamp", "Total Value", "Unrealized P&L", "Realized P&L", "Positions"]
    alignments = ['<', '>', '>', '>', '>']
    print(format_table(headers, rows, alignments))


def main():
    parser = argparse.ArgumentParser(
        description="Position Tracker for Polymarket Trading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python position-tracker.py                          # List all positions
  python position-tracker.py --add MARKET123 0.52 100 # Open position
  python position-tracker.py --close 1 0.58           # Close position #1
  python position-tracker.py --summary                # Portfolio summary
  python position-tracker.py --pnl                    # P&L breakdown
  python position-tracker.py --history                # Historical snapshots
  python position-tracker.py --alerts                 # Check alerts
  python position-tracker.py --snapshot               # Create snapshot
        """
    )
    
    parser.add_argument('--db', default='positions.db', help='Database path')
    parser.add_argument('--bankroll', type=float, default=10000.0, help='Starting bankroll')
    
    # Commands
    parser.add_argument('--add', nargs=3, metavar=('MARKET_ID', 'PRICE', 'SIZE'),
                       help='Open new position')
    parser.add_argument('--close', nargs=2, metavar=('POSITION_ID', 'PRICE'),
                       help='Close position')
    parser.add_argument('--update-price', nargs=2, metavar=('POSITION_ID', 'PRICE'),
                       help='Update position price')
    parser.add_argument('--summary', action='store_true', help='Show portfolio summary')
    parser.add_argument('--pnl', action='store_true', help='Show P&L breakdown')
    parser.add_argument('--history', action='store_true', help='Show historical snapshots')
    parser.add_argument('--history-days', type=int, default=7, help='Days of history to show')
    parser.add_argument('--alerts', action='store_true', help='Check for alerts')
    parser.add_argument('--snapshot', action='store_true', help='Create portfolio snapshot')
    
    # Optional position parameters
    parser.add_argument('--stop-loss', type=float, help='Stop loss price')
    parser.add_argument('--take-profit', type=float, help='Take profit price')
    parser.add_argument('--sector', help='Position sector/category')
    
    args = parser.parse_args()
    
    # Initialize tracker
    tracker = PositionTracker(db_path=args.db, bankroll=args.bankroll)
    
    try:
        # Execute commands
        if args.add:
            market_id, price, size = args.add
            tracker.open_position(
                market_id=market_id,
                entry_price=float(price),
                size=float(size),
                stop_loss=args.stop_loss,
                take_profit=args.take_profit,
                sector=args.sector
            )
            cmd_list(tracker)
        
        elif args.close:
            position_id, price = args.close
            tracker.close_position(int(position_id), float(price))
            cmd_summary(tracker)
        
        elif args.update_price:
            position_id, price = args.update_price
            tracker.update_price(int(position_id), float(price))
            print(f"✓ Updated position {position_id} price to ${float(price):.4f}")
        
        elif args.summary:
            cmd_summary(tracker)
        
        elif args.pnl:
            cmd_pnl(tracker)
        
        elif args.history:
            cmd_history(tracker, args.history_days)
        
        elif args.alerts:
            alerts = tracker.check_alerts()
            if alerts:
                print("\n⚠️  Active Alerts:")
                for alert in alerts:
                    emoji = "🚨" if alert['severity'] == 'HIGH' else "⚡"
                    print(f"  {emoji} [{alert['type']}] {alert['message']}")
            else:
                print("\n✓ No active alerts")
        
        elif args.snapshot:
            snapshot_id = tracker.create_snapshot()
            print(f"✓ Created snapshot #{snapshot_id}")
        
        else:
            # Default: list positions
            cmd_list(tracker)
    
    finally:
        tracker.close()


if __name__ == '__main__':
    main()
