#!/usr/bin/env python3
"""
Trade Journal - Professional trading journal and analytics for Polymarket
Tracks trades, performance, psychology, and generates insights.
"""

import sqlite3
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

# Try to import optional dependencies
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


@dataclass
class TradeEntry:
    """Trade entry data"""
    market_id: str
    market_name: str
    price: float
    size: float
    signal: str
    confidence: float  # 0-100
    category: str  # crypto, politics, sports
    strategy: str  # hype, momentum, mean-reversion
    notes: Optional[str] = None
    emotion: Optional[str] = None  # calm, excited, anxious, fomo, revenge
    entry_timestamp: Optional[str] = None


@dataclass
class TradeExit:
    """Trade exit data"""
    exit_price: float
    exit_timestamp: Optional[str] = None
    notes: Optional[str] = None


class Journal:
    """Professional trading journal with analytics and insights"""
    
    def __init__(self, db_path: str = "polymarket_trades.db"):
        """Initialize journal with database connection"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
    
    def _init_db(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_id TEXT NOT NULL,
                market_name TEXT NOT NULL,
                
                -- Entry
                entry_timestamp TEXT NOT NULL,
                entry_price REAL NOT NULL,
                size REAL NOT NULL,
                signal TEXT NOT NULL,
                confidence REAL NOT NULL,
                category TEXT NOT NULL,
                strategy TEXT NOT NULL,
                entry_notes TEXT,
                emotion TEXT,
                
                -- Exit
                exit_timestamp TEXT,
                exit_price REAL,
                pnl REAL,
                pnl_percent REAL,
                exit_notes TEXT,
                
                -- Tags
                outcome TEXT,  -- win, loss, scratch
                quality TEXT,  -- good, bad, lucky, unlucky
                
                -- Behavioral flags
                is_fomo INTEGER DEFAULT 0,
                is_revenge INTEGER DEFAULT 0,
                is_overtrading INTEGER DEFAULT 0,
                
                -- Metadata
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entry_timestamp ON trades(entry_timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON trades(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_strategy ON trades(strategy)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcome ON trades(outcome)")
        
        self.conn.commit()
    
    def log_entry(self, market_id: str, price: float, size: float, signal: str,
                  confidence: float, category: str, strategy: str,
                  market_name: Optional[str] = None, notes: Optional[str] = None,
                  emotion: Optional[str] = None, entry_timestamp: Optional[str] = None) -> int:
        """
        Log a trade entry
        
        Returns:
            trade_id: ID of the newly created trade
        """
        if entry_timestamp is None:
            entry_timestamp = datetime.now().isoformat()
        
        if market_name is None:
            market_name = market_id
        
        # Detect FOMO and revenge trading from emotion
        is_fomo = 1 if emotion and 'fomo' in emotion.lower() else 0
        is_revenge = 1 if emotion and 'revenge' in emotion.lower() else 0
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO trades (
                market_id, market_name, entry_timestamp, entry_price, size,
                signal, confidence, category, strategy, entry_notes, emotion,
                is_fomo, is_revenge
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            market_id, market_name, entry_timestamp, price, size,
            signal, confidence, category, strategy, notes, emotion,
            is_fomo, is_revenge
        ))
        
        self.conn.commit()
        trade_id = cursor.lastrowid
        
        # Check for overtrading
        self._check_overtrading(trade_id, entry_timestamp)
        
        return trade_id
    
    def log_exit(self, trade_id: int, price: float, notes: Optional[str] = None,
                 exit_timestamp: Optional[str] = None):
        """Log trade exit and calculate P&L"""
        if exit_timestamp is None:
            exit_timestamp = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        
        # Get trade entry data
        cursor.execute("SELECT entry_price, size FROM trades WHERE id = ?", (trade_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"Trade {trade_id} not found")
        
        entry_price = row['entry_price']
        size = row['size']
        
        # Calculate P&L
        pnl = (price - entry_price) * size
        pnl_percent = ((price - entry_price) / entry_price) * 100
        
        # Determine outcome
        if abs(pnl_percent) < 1:
            outcome = 'scratch'
        elif pnl > 0:
            outcome = 'win'
        else:
            outcome = 'loss'
        
        # Update trade
        cursor.execute("""
            UPDATE trades SET
                exit_timestamp = ?,
                exit_price = ?,
                pnl = ?,
                pnl_percent = ?,
                outcome = ?,
                exit_notes = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            exit_timestamp, price, pnl, pnl_percent, outcome, notes,
            datetime.now().isoformat(), trade_id
        ))
        
        self.conn.commit()
    
    def tag_trade(self, trade_id: int, quality: Optional[str] = None,
                  outcome: Optional[str] = None, **flags):
        """Tag a trade with quality assessment and behavioral flags"""
        cursor = self.conn.cursor()
        
        updates = []
        params = []
        
        if quality:
            updates.append("quality = ?")
            params.append(quality)
        
        if outcome:
            updates.append("outcome = ?")
            params.append(outcome)
        
        for flag, value in flags.items():
            if flag in ['is_fomo', 'is_revenge', 'is_overtrading']:
                updates.append(f"{flag} = ?")
                params.append(1 if value else 0)
        
        if updates:
            params.append(datetime.now().isoformat())
            params.append(trade_id)
            
            cursor.execute(f"""
                UPDATE trades SET
                    {', '.join(updates)},
                    updated_at = ?
                WHERE id = ?
            """, params)
            
            self.conn.commit()
    
    def _check_overtrading(self, trade_id: int, timestamp: str):
        """Detect overtrading patterns (>10 trades in 4 hours)"""
        cursor = self.conn.cursor()
        
        dt = datetime.fromisoformat(timestamp)
        four_hours_ago = (dt - timedelta(hours=4)).isoformat()
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM trades
            WHERE entry_timestamp > ?
        """, (four_hours_ago,))
        
        count = cursor.fetchone()['count']
        
        if count > 10:
            cursor.execute("""
                UPDATE trades SET is_overtrading = 1
                WHERE id = ?
            """, (trade_id,))
            self.conn.commit()
    
    def get_trades(self, limit: int = 50, closed_only: bool = False,
                   category: Optional[str] = None, strategy: Optional[str] = None,
                   start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Get trades with optional filters"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM trades WHERE 1=1"
        params = []
        
        if closed_only:
            query += " AND exit_timestamp IS NOT NULL"
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if strategy:
            query += " AND strategy = ?"
            params.append(strategy)
        
        if start_date:
            query += " AND entry_timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND entry_timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY entry_timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_analytics(self, days: Optional[int] = None) -> Dict[str, Any]:
        """Calculate comprehensive performance analytics"""
        cursor = self.conn.cursor()
        
        # Date filter
        date_filter = ""
        params = []
        if days:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            date_filter = "AND entry_timestamp >= ?"
            params.append(since)
        
        # Overall stats
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN outcome = 'scratch' THEN 1 ELSE 0 END) as scratches,
                AVG(CASE WHEN outcome = 'win' THEN pnl ELSE NULL END) as avg_win,
                AVG(CASE WHEN outcome = 'loss' THEN pnl ELSE NULL END) as avg_loss,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl,
                MAX(pnl) as best_trade,
                MIN(pnl) as worst_trade,
                SUM(CASE WHEN is_fomo = 1 THEN 1 ELSE 0 END) as fomo_trades,
                SUM(CASE WHEN is_revenge = 1 THEN 1 ELSE 0 END) as revenge_trades,
                SUM(CASE WHEN is_overtrading = 1 THEN 1 ELSE 0 END) as overtrading_count
            FROM trades
            WHERE exit_timestamp IS NOT NULL {date_filter}
        """, params)
        
        overall = dict(cursor.fetchone())
        
        # Calculate win rate and expectancy
        total = overall['total_trades'] or 1
        wins = overall['wins'] or 0
        losses = overall['losses'] or 0
        
        overall['win_rate'] = (wins / total * 100) if total > 0 else 0
        overall['loss_rate'] = (losses / total * 100) if total > 0 else 0
        
        avg_win = overall['avg_win'] or 0
        avg_loss = abs(overall['avg_loss'] or 0)
        win_rate = overall['win_rate'] / 100
        
        overall['expectancy'] = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        # By category
        cursor.execute(f"""
            SELECT 
                category,
                COUNT(*) as trades,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl
            FROM trades
            WHERE exit_timestamp IS NOT NULL {date_filter}
            GROUP BY category
        """, params)
        
        by_category = {}
        for row in cursor.fetchall():
            row = dict(row)
            category = row['category']
            row['win_rate'] = (row['wins'] / row['trades'] * 100) if row['trades'] > 0 else 0
            by_category[category] = row
        
        # By strategy
        cursor.execute(f"""
            SELECT 
                strategy,
                COUNT(*) as trades,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl
            FROM trades
            WHERE exit_timestamp IS NOT NULL {date_filter}
            GROUP BY strategy
        """, params)
        
        by_strategy = {}
        for row in cursor.fetchall():
            row = dict(row)
            strategy = row['strategy']
            row['win_rate'] = (row['wins'] / row['trades'] * 100) if row['trades'] > 0 else 0
            by_strategy[strategy] = row
        
        # By time of day
        cursor.execute(f"""
            SELECT 
                CAST(strftime('%H', entry_timestamp) AS INTEGER) as hour,
                COUNT(*) as trades,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
                AVG(pnl) as avg_pnl
            FROM trades
            WHERE exit_timestamp IS NOT NULL {date_filter}
            GROUP BY hour
        """, params)
        
        by_hour = {}
        for row in cursor.fetchall():
            row = dict(row)
            hour = row['hour']
            row['win_rate'] = (row['wins'] / row['trades'] * 100) if row['trades'] > 0 else 0
            by_hour[hour] = row
        
        # By quality tag
        cursor.execute(f"""
            SELECT 
                quality,
                COUNT(*) as trades,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
                AVG(pnl) as avg_pnl
            FROM trades
            WHERE exit_timestamp IS NOT NULL AND quality IS NOT NULL {date_filter}
            GROUP BY quality
        """, params)
        
        by_quality = {}
        for row in cursor.fetchall():
            row = dict(row)
            quality = row['quality']
            row['win_rate'] = (row['wins'] / row['trades'] * 100) if row['trades'] > 0 else 0
            by_quality[quality] = row
        
        # Best and worst days
        cursor.execute(f"""
            SELECT 
                DATE(entry_timestamp) as date,
                COUNT(*) as trades,
                SUM(pnl) as daily_pnl
            FROM trades
            WHERE exit_timestamp IS NOT NULL {date_filter}
            GROUP BY date
            ORDER BY daily_pnl DESC
        """, params)
        
        daily_pnl = [dict(row) for row in cursor.fetchall()]
        best_days = daily_pnl[:5] if daily_pnl else []
        worst_days = daily_pnl[-5:][::-1] if len(daily_pnl) > 0 else []
        
        return {
            'overall': overall,
            'by_category': by_category,
            'by_strategy': by_strategy,
            'by_hour': by_hour,
            'by_quality': by_quality,
            'best_days': best_days,
            'worst_days': worst_days
        }
    
    def get_insights(self) -> List[str]:
        """Generate trading insights and identify patterns"""
        analytics = self.get_analytics()
        insights = []
        
        overall = analytics['overall']
        
        # Overall performance
        if overall['total_trades'] > 0:
            win_rate = overall['win_rate']
            
            if win_rate > 60:
                insights.append(f"🎯 Strong win rate: {win_rate:.1f}% - You're doing great!")
            elif win_rate > 50:
                insights.append(f"✅ Profitable win rate: {win_rate:.1f}%")
            elif win_rate > 40:
                insights.append(f"⚠️ Low win rate: {win_rate:.1f}% - Review your strategy")
            else:
                insights.append(f"🚨 Critical win rate: {win_rate:.1f}% - Major strategy review needed")
            
            # Expectancy
            expectancy = overall['expectancy']
            if expectancy > 0:
                insights.append(f"💰 Positive expectancy: ${expectancy:.2f} per trade")
            else:
                insights.append(f"⚠️ Negative expectancy: ${expectancy:.2f} per trade - Not sustainable!")
        
        # Behavioral issues
        fomo_trades = overall.get('fomo_trades', 0)
        revenge_trades = overall.get('revenge_trades', 0)
        overtrading = overall.get('overtrading_count', 0)
        
        if fomo_trades > 0:
            insights.append(f"🚨 FOMO detected: {fomo_trades} trades - Work on patience!")
        
        if revenge_trades > 0:
            insights.append(f"😤 Revenge trading: {revenge_trades} trades - Take breaks after losses!")
        
        if overtrading > 0:
            insights.append(f"📊 Overtrading: {overtrading} instances - Quality > Quantity!")
        
        # Category performance
        by_category = analytics['by_category']
        if by_category:
            best_category = max(by_category.items(), key=lambda x: x[1]['win_rate'])
            worst_category = min(by_category.items(), key=lambda x: x[1]['win_rate'])
            
            insights.append(f"🏆 Best category: {best_category[0]} ({best_category[1]['win_rate']:.1f}% win rate)")
            insights.append(f"❌ Worst category: {worst_category[0]} ({worst_category[1]['win_rate']:.1f}% win rate)")
        
        # Strategy performance
        by_strategy = analytics['by_strategy']
        if by_strategy:
            best_strategy = max(by_strategy.items(), key=lambda x: x[1]['total_pnl'])
            insights.append(f"💡 Most profitable strategy: {best_strategy[0]} (${best_strategy[1]['total_pnl']:.2f})")
        
        # Time of day
        by_hour = analytics['by_hour']
        if by_hour:
            best_hour = max(by_hour.items(), key=lambda x: x[1]['win_rate'])
            worst_hour = min(by_hour.items(), key=lambda x: x[1]['win_rate'])
            
            insights.append(f"⏰ Best trading hour: {best_hour[0]}:00 ({best_hour[1]['win_rate']:.1f}% win rate)")
            insights.append(f"😴 Worst trading hour: {worst_hour[0]}:00 ({worst_hour[1]['win_rate']:.1f}% win rate)")
        
        # Win/loss ratio
        avg_win = overall.get('avg_win', 0)
        avg_loss = abs(overall.get('avg_loss', 0))
        
        if avg_win > 0 and avg_loss > 0:
            ratio = avg_win / avg_loss
            if ratio > 2:
                insights.append(f"💪 Excellent win/loss ratio: {ratio:.2f}:1")
            elif ratio > 1.5:
                insights.append(f"✅ Good win/loss ratio: {ratio:.2f}:1")
            elif ratio < 1:
                insights.append(f"⚠️ Poor win/loss ratio: {ratio:.2f}:1 - Winners too small or losers too big")
        
        return insights
    
    def generate_daily_report(self, date: Optional[str] = None) -> str:
        """Generate daily journal summary"""
        if date is None:
            date = datetime.now().date().isoformat()
        
        cursor = self.conn.cursor()
        
        # Get trades for the day
        cursor.execute("""
            SELECT * FROM trades
            WHERE DATE(entry_timestamp) = ?
            ORDER BY entry_timestamp
        """, (date,))
        
        trades = [dict(row) for row in cursor.fetchall()]
        
        if not trades:
            return f"No trades on {date}"
        
        # Calculate daily stats
        closed_trades = [t for t in trades if t['exit_timestamp'] is not None]
        total_pnl = sum(t['pnl'] or 0 for t in closed_trades)
        wins = sum(1 for t in closed_trades if t['outcome'] == 'win')
        losses = sum(1 for t in closed_trades if t['outcome'] == 'loss')
        
        report = f"📊 Daily Trading Journal - {date}\n"
        report += "=" * 60 + "\n\n"
        
        report += f"Trades: {len(trades)} ({len(closed_trades)} closed)\n"
        report += f"P&L: ${total_pnl:.2f}\n"
        report += f"Win Rate: {(wins / len(closed_trades) * 100) if closed_trades else 0:.1f}%\n"
        report += f"W/L: {wins}/{losses}\n\n"
        
        report += "Trades:\n"
        report += "-" * 60 + "\n"
        
        for trade in trades:
            status = "OPEN" if trade['exit_timestamp'] is None else trade['outcome'].upper()
            pnl_str = f"${trade['pnl']:.2f}" if trade['pnl'] is not None else "N/A"
            
            report += f"\n[{trade['id']}] {trade['market_name'][:40]}\n"
            report += f"  Entry: ${trade['entry_price']:.3f} @ {trade['entry_timestamp'][:16]}\n"
            report += f"  Signal: {trade['signal']} | Strategy: {trade['strategy']} | Category: {trade['category']}\n"
            report += f"  Confidence: {trade['confidence']:.0f}% | Emotion: {trade['emotion'] or 'N/A'}\n"
            
            if trade['exit_timestamp']:
                report += f"  Exit: ${trade['exit_price']:.3f} @ {trade['exit_timestamp'][:16]}\n"
                report += f"  P&L: {pnl_str} ({trade['pnl_percent']:.2f}%) | {status}\n"
            else:
                report += f"  Status: {status}\n"
            
            if trade['entry_notes']:
                report += f"  Notes: {trade['entry_notes']}\n"
        
        return report
    
    def generate_weekly_report(self) -> str:
        """Generate weekly review"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        analytics = self.get_analytics(days=7)
        insights = self.get_insights()
        
        report = f"📈 Weekly Trading Review\n"
        report += f"{start_date.date()} to {end_date.date()}\n"
        report += "=" * 60 + "\n\n"
        
        overall = analytics['overall']
        
        report += "Performance Summary:\n"
        report += f"  Total Trades: {overall['total_trades']}\n"
        report += f"  Win Rate: {overall['win_rate']:.1f}%\n"
        report += f"  Total P&L: ${overall['total_pnl'] or 0:.2f}\n"
        report += f"  Average P&L: ${overall['avg_pnl'] or 0:.2f}\n"
        report += f"  Best Trade: ${overall['best_trade'] or 0:.2f}\n"
        report += f"  Worst Trade: ${overall['worst_trade'] or 0:.2f}\n"
        report += f"  Expectancy: ${overall['expectancy']:.2f}\n\n"
        
        report += "By Category:\n"
        for cat, stats in analytics['by_category'].items():
            report += f"  {cat}: {stats['win_rate']:.1f}% WR, ${stats['total_pnl']:.2f} P&L ({stats['trades']} trades)\n"
        
        report += "\nBy Strategy:\n"
        for strat, stats in analytics['by_strategy'].items():
            report += f"  {strat}: {stats['win_rate']:.1f}% WR, ${stats['total_pnl']:.2f} P&L ({stats['trades']} trades)\n"
        
        report += "\n🎯 Key Insights:\n"
        for insight in insights:
            report += f"  {insight}\n"
        
        report += "\nBest Days:\n"
        for day in analytics['best_days'][:3]:
            report += f"  {day['date']}: ${day['daily_pnl']:.2f} ({day['trades']} trades)\n"
        
        report += "\nWorst Days:\n"
        for day in analytics['worst_days'][:3]:
            report += f"  {day['date']}: ${day['daily_pnl']:.2f} ({day['trades']} trades)\n"
        
        return report
    
    def export_html(self, output_path: str, days: Optional[int] = 30):
        """Export journal to HTML with charts"""
        if not PLOTLY_AVAILABLE:
            return "Error: plotly not installed. Run: pip install plotly"
        
        analytics = self.get_analytics(days=days)
        insights = self.get_insights()
        
        # Create equity curve
        cursor = self.conn.cursor()
        date_filter = ""
        params = []
        
        if days:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            date_filter = "WHERE entry_timestamp >= ?"
            params.append(since)
        
        cursor.execute(f"""
            SELECT entry_timestamp, pnl
            FROM trades
            {date_filter}
            ORDER BY entry_timestamp
        """, params)
        
        trades = cursor.fetchall()
        
        if not trades:
            return "No trades to export"
        
        # Calculate cumulative P&L
        timestamps = []
        cumulative_pnl = []
        running_pnl = 0
        
        for trade in trades:
            if trade['pnl'] is not None:
                timestamps.append(trade['entry_timestamp'])
                running_pnl += trade['pnl']
                cumulative_pnl.append(running_pnl)
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Equity Curve',
                'Win Rate by Category',
                'P&L by Strategy',
                'Trades by Hour',
                'Trade Outcomes',
                'Quality Distribution'
            ),
            specs=[
                [{'type': 'scatter', 'colspan': 2}, None],
                [{'type': 'bar'}, {'type': 'bar'}],
                [{'type': 'pie'}, {'type': 'pie'}]
            ]
        )
        
        # Equity curve
        fig.add_trace(
            go.Scatter(x=timestamps, y=cumulative_pnl, mode='lines', name='P&L',
                      line=dict(color='green' if running_pnl > 0 else 'red')),
            row=1, col=1
        )
        
        # Win rate by category
        if analytics['by_category']:
            categories = list(analytics['by_category'].keys())
            win_rates = [analytics['by_category'][c]['win_rate'] for c in categories]
            
            fig.add_trace(
                go.Bar(x=categories, y=win_rates, name='Win Rate'),
                row=2, col=1
            )
        
        # P&L by strategy
        if analytics['by_strategy']:
            strategies = list(analytics['by_strategy'].keys())
            pnls = [analytics['by_strategy'][s]['total_pnl'] for s in strategies]
            
            fig.add_trace(
                go.Bar(x=strategies, y=pnls, name='P&L'),
                row=2, col=2
            )
        
        # Trade outcomes pie
        overall = analytics['overall']
        fig.add_trace(
            go.Pie(labels=['Wins', 'Losses', 'Scratches'],
                  values=[overall['wins'], overall['losses'], overall['scratches']]),
            row=3, col=1
        )
        
        # Quality distribution pie
        if analytics['by_quality']:
            qualities = list(analytics['by_quality'].keys())
            counts = [analytics['by_quality'][q]['trades'] for q in qualities]
            
            fig.add_trace(
                go.Pie(labels=qualities, values=counts),
                row=3, col=2
            )
        
        fig.update_layout(
            title_text=f"Trading Journal - Last {days} Days" if days else "Trading Journal - All Time",
            showlegend=False,
            height=1200
        )
        
        # Generate HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Trading Journal</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                .stat-card {{
                    background: white;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .stat-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                }}
                .stat-label {{
                    font-size: 12px;
                    color: #7f8c8d;
                    margin-top: 5px;
                }}
                .insights {{
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .insight {{
                    padding: 10px;
                    margin: 5px 0;
                    background: #ecf0f1;
                    border-radius: 3px;
                }}
                .positive {{ color: #27ae60; }}
                .negative {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Trading Journal</h1>
                <p>Period: Last {days} days</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value {('positive' if overall['total_pnl'] and overall['total_pnl'] > 0 else 'negative')}">
                        ${overall['total_pnl'] or 0:.2f}
                    </div>
                    <div class="stat-label">Total P&L</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-value">{overall['win_rate']:.1f}%</div>
                    <div class="stat-label">Win Rate</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-value">{overall['total_trades']}</div>
                    <div class="stat-label">Total Trades</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-value {('positive' if overall['expectancy'] > 0 else 'negative')}">
                        ${overall['expectancy']:.2f}
                    </div>
                    <div class="stat-label">Expectancy</div>
                </div>
            </div>
            
            <div class="insights">
                <h2>🎯 Key Insights</h2>
                {''.join(f'<div class="insight">{insight}</div>' for insight in insights)}
            </div>
            
            {fig.to_html(include_plotlyjs='cdn', div_id='charts')}
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html)
        
        return f"Report exported to {output_path}"
    
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description='Trade Journal - Professional trading journal for Polymarket')
    parser.add_argument('--db', default='polymarket_trades.db', help='Database path')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add trade
    add_parser = subparsers.add_parser('add', help='Add trade interactively')
    
    # Review trades
    review_parser = subparsers.add_parser('review', help='Review recent trades')
    review_parser.add_argument('--limit', type=int, default=10, help='Number of trades')
    review_parser.add_argument('--category', help='Filter by category')
    review_parser.add_argument('--strategy', help='Filter by strategy')
    
    # Analytics
    analytics_parser = subparsers.add_parser('analytics', help='Performance analytics')
    analytics_parser.add_argument('--days', type=int, help='Last N days')
    
    # Report
    report_parser = subparsers.add_parser('report', help='Generate report')
    report_parser.add_argument('type', choices=['daily', 'weekly', 'monthly'], help='Report type')
    report_parser.add_argument('--date', help='Date for daily report (YYYY-MM-DD)')
    
    # Export
    export_parser = subparsers.add_parser('export', help='Export to HTML')
    export_parser.add_argument('output', help='Output HTML file')
    export_parser.add_argument('--days', type=int, default=30, help='Last N days')
    
    # Insights
    insights_parser = subparsers.add_parser('insights', help='Generate insights')
    
    # Tag trade
    tag_parser = subparsers.add_parser('tag', help='Tag a trade')
    tag_parser.add_argument('trade_id', type=int, help='Trade ID')
    tag_parser.add_argument('--quality', choices=['good', 'bad', 'lucky', 'unlucky'], help='Quality tag')
    tag_parser.add_argument('--outcome', choices=['win', 'loss', 'scratch'], help='Outcome override')
    
    # Exit trade
    exit_parser = subparsers.add_parser('exit', help='Close a trade')
    exit_parser.add_argument('trade_id', type=int, help='Trade ID')
    exit_parser.add_argument('price', type=float, help='Exit price')
    exit_parser.add_argument('--notes', help='Exit notes')
    
    args = parser.parse_args()
    
    journal = Journal(args.db)
    
    try:
        if args.command == 'add':
            # Interactive trade entry
            print("📝 Add New Trade")
            print("-" * 60)
            
            market_id = input("Market ID: ")
            market_name = input("Market Name: ")
            price = float(input("Entry Price: "))
            size = float(input("Size: "))
            signal = input("Signal (e.g., hype, momentum, value): ")
            confidence = float(input("Confidence (0-100): "))
            category = input("Category (crypto/politics/sports): ")
            strategy = input("Strategy (hype/momentum/mean-reversion): ")
            notes = input("Notes (optional): ") or None
            emotion = input("Emotion (calm/excited/anxious/fomo/revenge): ") or None
            
            trade_id = journal.log_entry(
                market_id=market_id,
                market_name=market_name,
                price=price,
                size=size,
                signal=signal,
                confidence=confidence,
                category=category,
                strategy=strategy,
                notes=notes,
                emotion=emotion
            )
            
            print(f"\n✅ Trade #{trade_id} logged successfully!")
        
        elif args.command == 'exit':
            journal.log_exit(args.trade_id, args.price, args.notes)
            print(f"✅ Trade #{args.trade_id} closed successfully!")
        
        elif args.command == 'tag':
            journal.tag_trade(args.trade_id, quality=args.quality, outcome=args.outcome)
            print(f"✅ Trade #{args.trade_id} tagged successfully!")
        
        elif args.command == 'review':
            trades = journal.get_trades(
                limit=args.limit,
                category=args.category,
                strategy=args.strategy,
                closed_only=False
            )
            
            if not trades:
                print("No trades found")
                return
            
            print("\n📋 Recent Trades")
            print("=" * 100)
            
            for trade in trades:
                status = "OPEN" if trade['exit_timestamp'] is None else trade['outcome'].upper()
                pnl_str = f"${trade['pnl']:.2f}" if trade['pnl'] is not None else "N/A"
                
                print(f"\n[{trade['id']}] {trade['market_name']}")
                print(f"  Entry: ${trade['entry_price']:.3f} | Size: {trade['size']:.0f} | {trade['entry_timestamp'][:16]}")
                print(f"  Signal: {trade['signal']} | Strategy: {trade['strategy']} | Category: {trade['category']}")
                print(f"  Confidence: {trade['confidence']:.0f}% | Emotion: {trade['emotion'] or 'N/A'}")
                
                if trade['exit_timestamp']:
                    print(f"  Exit: ${trade['exit_price']:.3f} | P&L: {pnl_str} ({trade['pnl_percent']:.2f}%) | {status}")
                else:
                    print(f"  Status: {status}")
        
        elif args.command == 'analytics':
            analytics = journal.get_analytics(days=args.days)
            
            print("\n📊 Performance Analytics")
            print("=" * 60)
            
            overall = analytics['overall']
            
            print("\nOverall Performance:")
            print(f"  Total Trades: {overall['total_trades']}")
            print(f"  Win Rate: {overall['win_rate']:.1f}%")
            print(f"  Total P&L: ${overall['total_pnl'] or 0:.2f}")
            print(f"  Average P&L: ${overall['avg_pnl'] or 0:.2f}")
            print(f"  Best Trade: ${overall['best_trade'] or 0:.2f}")
            print(f"  Worst Trade: ${overall['worst_trade'] or 0:.2f}")
            print(f"  Expectancy: ${overall['expectancy']:.2f}")
            
            print("\n📂 By Category:")
            for cat, stats in analytics['by_category'].items():
                print(f"  {cat}: {stats['win_rate']:.1f}% WR | ${stats['total_pnl']:.2f} P&L | {stats['trades']} trades")
            
            print("\n🎯 By Strategy:")
            for strat, stats in analytics['by_strategy'].items():
                print(f"  {strat}: {stats['win_rate']:.1f}% WR | ${stats['total_pnl']:.2f} P&L | {stats['trades']} trades")
            
            print("\n⏰ Best Trading Hours:")
            hours_sorted = sorted(analytics['by_hour'].items(), key=lambda x: x[1]['win_rate'], reverse=True)
            for hour, stats in hours_sorted[:5]:
                print(f"  {hour:02d}:00 - {stats['win_rate']:.1f}% WR | ${stats['avg_pnl']:.2f} avg | {stats['trades']} trades")
            
            print("\n🏆 Best Days:")
            for day in analytics['best_days'][:5]:
                print(f"  {day['date']}: ${day['daily_pnl']:.2f} ({day['trades']} trades)")
            
            print("\n❌ Worst Days:")
            for day in analytics['worst_days'][:5]:
                print(f"  {day['date']}: ${day['daily_pnl']:.2f} ({day['trades']} trades)")
            
            # Behavioral
            if overall['fomo_trades'] or overall['revenge_trades'] or overall['overtrading_count']:
                print("\n⚠️ Behavioral Issues:")
                if overall['fomo_trades']:
                    print(f"  FOMO Trades: {overall['fomo_trades']}")
                if overall['revenge_trades']:
                    print(f"  Revenge Trades: {overall['revenge_trades']}")
                if overall['overtrading_count']:
                    print(f"  Overtrading Instances: {overall['overtrading_count']}")
        
        elif args.command == 'report':
            if args.type == 'daily':
                report = journal.generate_daily_report(args.date)
            elif args.type == 'weekly':
                report = journal.generate_weekly_report()
            else:
                report = "Monthly report not yet implemented"
            
            print(report)
        
        elif args.command == 'export':
            result = journal.export_html(args.output, days=args.days)
            print(result)
        
        elif args.command == 'insights':
            insights = journal.get_insights()
            
            print("\n🎯 Trading Insights")
            print("=" * 60)
            
            for insight in insights:
                print(f"  {insight}")
        
        else:
            # Default: show today's journal
            report = journal.generate_daily_report()
            print(report)
    
    finally:
        journal.close()


if __name__ == '__main__':
    main()
