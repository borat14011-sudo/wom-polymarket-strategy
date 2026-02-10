#!/usr/bin/env python3
"""
Live Paper Trading Dashboard System
Real-time monitoring and trade execution for Polymarket paper trading
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Paper trading position"""
    trade_id: str
    market_slug: str
    market_name: str
    position: str  # YES or NO
    entry_price: float
    size_usd: float
    shares: float
    entry_time: str
    status: str  # PENDING, OPEN, CLOSED
    
    # Calculated fields
    current_price: Optional[float] = None
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0


@dataclass
class TradeExecution:
    """Trade execution record"""
    trade_id: str
    market_slug: str
    side: str
    price: float
    size_usd: float
    timestamp: str
    status: str
    notes: str


class PaperTradingDashboard:
    """
    Live Paper Trading Dashboard
    
    Features:
    - Real-time P&L tracking
    - Position monitoring
    - Trade execution logging
    - Risk alerts
    - Daily reporting
    """
    
    def __init__(self, config_path: str = "paper_trading_config_live.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.db_path = "paper_trading_live.db"
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[TradeExecution] = []
        self._init_database()
        
    def _load_config(self) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            raise
    
    def _init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                trade_id TEXT PRIMARY KEY,
                market_slug TEXT NOT NULL,
                market_name TEXT NOT NULL,
                position TEXT NOT NULL,
                entry_price REAL NOT NULL,
                size_usd REAL NOT NULL,
                shares REAL NOT NULL,
                entry_time TEXT NOT NULL,
                current_price REAL,
                unrealized_pnl REAL DEFAULT 0.0,
                unrealized_pnl_pct REAL DEFAULT 0.0,
                status TEXT DEFAULT 'PENDING'
            )
        """)
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT NOT NULL,
                market_slug TEXT NOT NULL,
                side TEXT NOT NULL,
                price REAL NOT NULL,
                size_usd REAL NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT
            )
        """)
        
        # Daily snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_value REAL NOT NULL,
                cash_balance REAL NOT NULL,
                position_value REAL NOT NULL,
                unrealized_pnl REAL NOT NULL,
                realized_pnl REAL NOT NULL,
                position_count INTEGER NOT NULL
            )
        """)
        
        self.conn.commit()
        logger.info("Database initialized successfully")
    
    def execute_trade(self, trade_id: str, actual_entry_price: Optional[float] = None) -> bool:
        """
        Execute a prepared trade
        
        Args:
            trade_id: ID of the prepared trade
            actual_entry_price: Actual price executed (if different from expected)
            
        Returns:
            True if successful
        """
        # Find trade in prepared trades
        prepared_trade = None
        for trade in self.config['prepared_trades']:
            if trade['trade_id'] == trade_id:
                prepared_trade = trade
                break
        
        if not prepared_trade:
            logger.error(f"Trade {trade_id} not found in prepared trades")
            return False
        
        if prepared_trade['status'] != 'READY_TO_EXECUTE':
            logger.warning(f"Trade {trade_id} is not ready to execute (status: {prepared_trade['status']})")
            return False
        
        # Calculate entry price and shares
        if prepared_trade['position'] == 'NO':
            entry_price = actual_entry_price or (1.0 - prepared_trade['implied_prob'])
        else:
            entry_price = actual_entry_price or prepared_trade['implied_prob']
        
        size_usd = prepared_trade['size_usd']
        shares = size_usd / entry_price if entry_price > 0 else 0
        
        # Create position
        position = Position(
            trade_id=trade_id,
            market_slug=prepared_trade['market_slug'],
            market_name=prepared_trade['market'],
            position=prepared_trade['position'],
            entry_price=entry_price,
            size_usd=size_usd,
            shares=shares,
            entry_time=datetime.now().isoformat(),
            status='OPEN',
            current_price=entry_price
        )
        
        # Save to database
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO positions 
            (trade_id, market_slug, market_name, position, entry_price, size_usd, shares, entry_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            position.trade_id, position.market_slug, position.market_name,
            position.position, position.entry_price, position.size_usd,
            position.shares, position.entry_time, position.status
        ))
        
        # Log trade
        cursor.execute("""
            INSERT INTO trades (trade_id, market_slug, side, price, size_usd, timestamp, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade_id, prepared_trade['market_slug'], 
            f"BUY_{prepared_trade['position']}",
            entry_price, size_usd, datetime.now().isoformat(),
            'EXECUTED', f"Expected edge: {prepared_trade['edge_pct']}%"
        ))
        
        self.conn.commit()
        self.positions[trade_id] = position
        
        # Update config
        prepared_trade['status'] = 'EXECUTED'
        prepared_trade['execution_time'] = datetime.now().isoformat()
        prepared_trade['actual_entry_price'] = entry_price
        self._save_config()
        
        # Update portfolio cash
        self.config['portfolio']['cash'] -= size_usd
        self.config['portfolio']['allocated'] += size_usd
        self._save_config()
        
        logger.info(f"✅ Trade {trade_id} executed: {prepared_trade['market']}")
        logger.info(f"   Position: {prepared_trade['position']} | Size: ${size_usd:.2f} | Price: ${entry_price:.4f}")
        
        return True
    
    def execute_all_prepared(self) -> Dict[str, bool]:
        """Execute all prepared trades that are ready"""
        results = {}
        for trade in self.config['prepared_trades']:
            if trade['status'] == 'READY_TO_EXECUTE':
                success = self.execute_trade(trade['trade_id'])
                results[trade['trade_id']] = success
        return results
    
    def update_prices(self, price_updates: Dict[str, float]):
        """
        Update current prices for positions
        
        Args:
            price_updates: Dict of market_slug -> current_price
        """
        cursor = self.conn.cursor()
        
        for trade_id, position in self.positions.items():
            if position.market_slug in price_updates:
                new_price = price_updates[position.market_slug]
                position.current_price = new_price
                
                # Calculate P&L
                if position.position == 'YES':
                    position.unrealized_pnl = (new_price - position.entry_price) * position.shares
                else:  # NO position
                    position.unrealized_pnl = ((1 - new_price) - position.entry_price) * position.shares
                
                if position.entry_price > 0:
                    position.unrealized_pnl_pct = (position.unrealized_pnl / position.size_usd) * 100
                
                # Update database
                cursor.execute("""
                    UPDATE positions 
                    SET current_price = ?, unrealized_pnl = ?, unrealized_pnl_pct = ?
                    WHERE trade_id = ?
                """, (new_price, position.unrealized_pnl, position.unrealized_pnl_pct, trade_id))
        
        self.conn.commit()
        self._update_portfolio_value()
    
    def _update_portfolio_value(self):
        """Recalculate total portfolio value"""
        total_unrealized = sum(p.unrealized_pnl for p in self.positions.values())
        position_value = sum(p.size_usd for p in self.positions.values())
        
        self.config['portfolio']['total_value'] = (
            self.config['portfolio']['cash'] + 
            position_value + 
            total_unrealized
        )
        self.config['portfolio']['total_pnl'] = total_unrealized
        
        if self.config['initial_capital'] > 0:
            self.config['portfolio']['total_roi'] = (
                total_unrealized / self.config['initial_capital']
            ) * 100
        
        self._save_config()
    
    def get_dashboard(self) -> Dict:
        """Generate current dashboard data"""
        positions_list = []
        for p in self.positions.values():
            positions_list.append({
                'trade_id': p.trade_id,
                'market': p.market_name[:40],
                'position': p.position,
                'entry': f"${p.entry_price:.4f}",
                'current': f"${p.current_price:.4f}" if p.current_price else "N/A",
                'size': f"${p.size_usd:.2f}",
                'pnl': f"${p.unrealized_pnl:+.2f}",
                'pnl_pct': f"{p.unrealized_pnl_pct:+.2f}%"
            })
        
        # Get prepared trades
        prepared = []
        for t in self.config['prepared_trades']:
            prepared.append({
                'trade_id': t['trade_id'],
                'market': t['market'][:40],
                'position': t['position'],
                'size': f"${t['size_usd']:.2f}",
                'edge': f"{t['edge_pct']:.2f}%",
                'ev': f"{t['expected_value_pct']:.1f}%",
                'status': t['status']
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system_status': 'ACTIVE',
            'portfolio': {
                'initial_capital': f"${self.config['initial_capital']:.2f}",
                'cash': f"${self.config['portfolio']['cash']:.2f}",
                'allocated': f"${self.config['portfolio']['allocated']:.2f}",
                'total_value': f"${self.config['portfolio']['total_value']:.2f}",
                'total_pnl': f"${self.config['portfolio']['total_pnl']:+.2f}",
                'total_roi': f"{self.config['portfolio']['total_roi']:+.2f}%"
            },
            'open_positions': positions_list,
            'prepared_trades': prepared,
            'risk_metrics': {
                'exposure_pct': f"{(self.config['portfolio']['allocated'] / self.config['initial_capital'] * 100):.1f}%",
                'cash_reserve_pct': f"{(self.config['portfolio']['cash'] / self.config['initial_capital'] * 100):.1f}%",
                'positions_count': len(self.positions),
                'kill_switch': 'ARMED' if self.config['risk_management']['enable_kill_switch'] else 'DISABLED'
            }
        }
    
    def create_snapshot(self):
        """Create daily portfolio snapshot"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO snapshots 
            (timestamp, total_value, cash_balance, position_value, unrealized_pnl, realized_pnl, position_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            self.config['portfolio']['total_value'],
            self.config['portfolio']['cash'],
            self.config['portfolio']['allocated'],
            self.config['portfolio']['total_pnl'],
            0.0,  # Realized P&L tracking not implemented yet
            len(self.positions)
        ))
        self.conn.commit()
        logger.info("Portfolio snapshot created")
    
    def check_alerts(self) -> List[Dict]:
        """Check for risk alerts"""
        alerts = []
        
        # Daily loss limit check
        daily_loss_pct = abs(self.config['portfolio']['total_roi'])
        if daily_loss_pct > self.config['risk_management']['max_daily_loss_pct']:
            alerts.append({
                'level': 'CRITICAL',
                'type': 'DAILY_LOSS_LIMIT',
                'message': f"Daily loss limit exceeded: {daily_loss_pct:.2f}%",
                'action': 'HALT_TRADING'
            })
        
        # Circuit breaker check
        if daily_loss_pct > self.config['risk_management']['circuit_breaker_pct']:
            alerts.append({
                'level': 'EMERGENCY',
                'type': 'CIRCUIT_BREAKER',
                'message': f"Circuit breaker triggered: {daily_loss_pct:.2f}%",
                'action': 'EMERGENCY_HALT'
            })
        
        # Cash reserve check
        cash_reserve_pct = (self.config['portfolio']['cash'] / self.config['initial_capital']) * 100
        if cash_reserve_pct < self.config['risk_management']['min_cash_reserve_pct']:
            alerts.append({
                'level': 'WARNING',
                'type': 'LOW_CASH_RESERVE',
                'message': f"Cash reserve below minimum: {cash_reserve_pct:.1f}%",
                'action': 'REDUCE_EXPOSURE'
            })
        
        # Position-level alerts
        for trade_id, position in self.positions.items():
            if position.unrealized_pnl_pct < -20:
                alerts.append({
                    'level': 'HIGH',
                    'type': 'POSITION_STOP_LOSS',
                    'message': f"Position {trade_id} down {position.unrealized_pnl_pct:.1f}%",
                    'action': 'REVIEW_POSITION'
                })
        
        return alerts
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def print_dashboard(self):
        """Print formatted dashboard to console"""
        dash = self.get_dashboard()
        
        print("\n" + "="*80)
        print("LIVE PAPER TRADING DASHBOARD")
        print("="*80)
        print(f"Timestamp: {dash['timestamp']}")
        print(f"System Status: {dash['system_status']}")
        print("-"*80)
        
        print("\n[PORTFOLIO SUMMARY]")
        print(f"   Initial Capital: {dash['portfolio']['initial_capital']}")
        print(f"   Cash Balance:    {dash['portfolio']['cash']}")
        print(f"   Allocated:       {dash['portfolio']['allocated']}")
        print(f"   Total Value:     {dash['portfolio']['total_value']}")
        print(f"   Total P&L:       {dash['portfolio']['total_pnl']}")
        print(f"   Total ROI:       {dash['portfolio']['total_roi']}")
        
        print("\n[RISK METRICS]")
        for key, value in dash['risk_metrics'].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        if dash['open_positions']:
            print("\n[OPEN POSITIONS]")
            for pos in dash['open_positions']:
                print(f"   {pos['trade_id']}: {pos['market'][:45]}")
                print(f"      Position: {pos['position']} | Entry: {pos['entry']} | Current: {pos['current']}")
                print(f"      Size: {pos['size']} | P&L: {pos['pnl']} ({pos['pnl_pct']})")
        
        if dash['prepared_trades']:
            print("\n[PREPARED TRADES]")
            for trade in dash['prepared_trades']:
                status_symbol = "[DONE]" if trade['status'] == "EXECUTED" else "[PENDING]"
                print(f"   {status_symbol} {trade['trade_id']}: {trade['market'][:45]}")
                print(f"      Position: {trade['position']} | Size: {trade['size']} | Edge: {trade['edge']} | Status: {trade['status']}")
        
        # Check and display alerts
        alerts = self.check_alerts()
        if alerts:
            print("\n[ACTIVE ALERTS]")
            for alert in alerts:
                symbol = "[!]" if alert['level'] in ['CRITICAL', 'EMERGENCY'] else "[?]"
                print(f"   {symbol} [{alert['level']}] {alert['message']}")
                print(f"      Action: {alert['action']}")
        else:
            print("\n[OK] No active alerts")
        
        print("\n" + "="*80)
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
            logger.info("Dashboard connection closed")


def main():
    """Main entry point for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Live Paper Trading Dashboard')
    parser.add_argument('--execute', metavar='TRADE_ID', help='Execute a specific trade')
    parser.add_argument('--execute-all', action='store_true', help='Execute all prepared trades')
    parser.add_argument('--dashboard', action='store_true', help='Show dashboard')
    parser.add_argument('--snapshot', action='store_true', help='Create portfolio snapshot')
    parser.add_argument('--alerts', action='store_true', help='Check for alerts')
    
    args = parser.parse_args()
    
    dashboard = PaperTradingDashboard()
    
    try:
        if args.execute:
            dashboard.execute_trade(args.execute)
            dashboard.print_dashboard()
        elif args.execute_all:
            results = dashboard.execute_all_prepared()
            print("\nExecution Results:")
            for trade_id, success in results.items():
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"   {trade_id}: {status}")
            dashboard.print_dashboard()
        elif args.snapshot:
            dashboard.create_snapshot()
            print("✅ Snapshot created")
        elif args.alerts:
            alerts = dashboard.check_alerts()
            if alerts:
                print("\n🚨 Active Alerts:")
                for alert in alerts:
                    print(f"   [{alert['level']}] {alert['message']}")
            else:
                print("✅ No alerts")
        else:
            dashboard.print_dashboard()
    finally:
        dashboard.close()


if __name__ == '__main__':
    main()
