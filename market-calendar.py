#!/usr/bin/env python3
"""
Market Event Calendar - Polymarket Trading System
Track market resolutions, key events, and trading patterns

Usage:
    python market-calendar.py                      # Today's events
    python market-calendar.py --week               # This week
    python market-calendar.py --upcoming           # Next 30 days
    python market-calendar.py --add "2026-02-15" "Super Bowl" "sports"
    python market-calendar.py --expiring 7         # Markets resolving in 7 days
    python market-calendar.py --patterns           # Show trading patterns
    python market-calendar.py --positions          # Show position risks
"""

import sqlite3
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import os

# Configuration
DB_PATH = "polymarket_data.db"
ALERT_HOURS = [24, 48, 168]  # Alert 24h, 48h, 7 days before resolution

class MarketCalendar:
    """Market event tracking and calendar management"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize calendar tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calendar events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_date TEXT NOT NULL,
                event_name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                market_id TEXT,
                event_type TEXT DEFAULT 'manual',
                alert_hours INTEGER DEFAULT 24,
                recurring TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (market_id) REFERENCES markets(market_id)
            )
        ''')
        
        # Event alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                alert_time TIMESTAMP,
                triggered INTEGER DEFAULT 0,
                message TEXT,
                FOREIGN KEY (event_id) REFERENCES calendar_events(id)
            )
        ''')
        
        # Trading patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                day_of_week INTEGER,
                hour_of_day INTEGER,
                market_category TEXT,
                avg_volume REAL,
                avg_price_change REAL,
                avg_spread REAL,
                sample_count INTEGER,
                confidence_score REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Position risks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS position_risks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_id TEXT,
                position_size REAL,
                entry_price REAL,
                current_price REAL,
                days_to_resolution INTEGER,
                risk_level TEXT,
                suggested_action TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (market_id) REFERENCES markets(market_id)
            )
        ''')
        
        # Indexes for fast queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_calendar_date 
            ON calendar_events(event_date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_patterns_type 
            ON trading_patterns(pattern_type, market_category)
        ''')
        
        conn.commit()
        conn.close()
    
    def add_event(self, event_date: str, event_name: str, category: str = "general", 
                  description: str = "", market_id: str = None, event_type: str = "manual",
                  alert_hours: int = 24, recurring: str = None) -> int:
        """Add calendar event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO calendar_events 
            (event_date, event_name, category, description, market_id, event_type, alert_hours, recurring)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (event_date, event_name, category, description, market_id, event_type, alert_hours, recurring))
        
        event_id = cursor.lastrowid
        
        # Create alerts
        self._create_alerts(cursor, event_id, event_date, alert_hours, event_name)
        
        conn.commit()
        conn.close()
        
        return event_id
    
    def _create_alerts(self, cursor, event_id: int, event_date: str, alert_hours: int, event_name: str):
        """Create alert entries for an event"""
        try:
            event_dt = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
            
            for hours in ALERT_HOURS:
                if hours <= alert_hours:
                    alert_time = event_dt - timedelta(hours=hours)
                    message = f"⏰ {event_name} in {hours} hours"
                    
                    cursor.execute('''
                        INSERT INTO event_alerts (event_id, alert_time, message)
                        VALUES (?, ?, ?)
                    ''', (event_id, alert_time.isoformat(), message))
        except:
            pass
    
    def sync_market_resolutions(self) -> int:
        """Sync resolution dates from markets table to calendar"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get markets with end times
        cursor.execute('''
            SELECT market_id, question, category, end_time 
            FROM markets 
            WHERE end_time IS NOT NULL 
            AND resolved = 0
        ''')
        
        markets = cursor.fetchall()
        synced = 0
        
        for market_id, question, category, end_time in markets:
            # Check if event already exists
            cursor.execute('''
                SELECT id FROM calendar_events 
                WHERE market_id = ? AND event_type = 'resolution'
            ''', (market_id,))
            
            if cursor.fetchone() is None:
                # Add resolution event
                self.add_event(
                    event_date=end_time,
                    event_name=f"Resolution: {question[:60]}",
                    category=category or "unknown",
                    market_id=market_id,
                    event_type="resolution",
                    alert_hours=168  # Alert 7 days before
                )
                synced += 1
        
        conn.close()
        return synced
    
    def get_events(self, start_date: Optional[str] = None, 
                   end_date: Optional[str] = None,
                   event_type: Optional[str] = None,
                   category: Optional[str] = None) -> List[Dict]:
        """Get events within date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM calendar_events WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND event_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND event_date <= ?"
            params.append(end_date)
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY event_date ASC"
        
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        events = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return events
    
    def get_today(self) -> List[Dict]:
        """Get today's events"""
        today = datetime.now().date().isoformat()
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
        return self.get_events(start_date=today, end_date=tomorrow)
    
    def get_week(self) -> List[Dict]:
        """Get this week's events"""
        today = datetime.now().date().isoformat()
        next_week = (datetime.now().date() + timedelta(days=7)).isoformat()
        return self.get_events(start_date=today, end_date=next_week)
    
    def get_upcoming(self, days: int = 30) -> List[Dict]:
        """Get upcoming events"""
        today = datetime.now().date().isoformat()
        future = (datetime.now().date() + timedelta(days=days)).isoformat()
        return self.get_events(start_date=today, end_date=future)
    
    def get_expiring_markets(self, days: int = 7) -> List[Dict]:
        """Get markets expiring within X days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        future_date = (datetime.now() + timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT m.*, 
                   (julianday(m.end_time) - julianday('now')) as days_left,
                   s.price_yes, s.volume_24h
            FROM markets m
            LEFT JOIN (
                SELECT market_id, price_yes, volume_24h
                FROM snapshots
                WHERE (market_id, timestamp) IN (
                    SELECT market_id, MAX(timestamp)
                    FROM snapshots
                    GROUP BY market_id
                )
            ) s ON m.market_id = s.market_id
            WHERE m.end_time IS NOT NULL
            AND m.end_time <= ?
            AND m.resolved = 0
            ORDER BY m.end_time ASC
        ''', (future_date,))
        
        columns = [desc[0] for desc in cursor.description]
        markets = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return markets
    
    def analyze_patterns(self, category: Optional[str] = None) -> Dict:
        """Analyze trading patterns from historical data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Day of week patterns
        cursor.execute('''
            SELECT 
                CAST(strftime('%w', timestamp) AS INTEGER) as day_of_week,
                AVG(volume_24h) as avg_volume,
                AVG(spread) as avg_spread,
                COUNT(*) as sample_count
            FROM snapshots
            WHERE timestamp >= datetime('now', '-30 days')
            GROUP BY day_of_week
            ORDER BY day_of_week
        ''')
        
        day_patterns = []
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        for row in cursor.fetchall():
            day_of_week, avg_volume, avg_spread, sample_count = row
            day_patterns.append({
                'day': days[day_of_week],
                'avg_volume': avg_volume or 0,
                'avg_spread': avg_spread or 0,
                'sample_count': sample_count
            })
        
        # Hour of day patterns
        cursor.execute('''
            SELECT 
                CAST(strftime('%H', timestamp) AS INTEGER) as hour_of_day,
                AVG(volume_24h) as avg_volume,
                AVG(spread) as avg_spread,
                COUNT(*) as sample_count
            FROM snapshots
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY hour_of_day
            ORDER BY hour_of_day
        ''')
        
        hour_patterns = []
        for row in cursor.fetchall():
            hour_of_day, avg_volume, avg_spread, sample_count = row
            hour_patterns.append({
                'hour': hour_of_day,
                'avg_volume': avg_volume or 0,
                'avg_spread': avg_spread or 0,
                'sample_count': sample_count
            })
        
        # Pre-resolution behavior (7 days before resolution)
        cursor.execute('''
            SELECT 
                AVG(s.volume_24h) as avg_volume,
                AVG(s.spread) as avg_spread,
                AVG(ABS(s.price_yes - 0.5)) as avg_price_deviation,
                COUNT(DISTINCT s.market_id) as market_count
            FROM snapshots s
            JOIN markets m ON s.market_id = m.market_id
            WHERE m.end_time IS NOT NULL
            AND julianday(m.end_time) - julianday(s.timestamp) <= 7
            AND julianday(m.end_time) - julianday(s.timestamp) >= 0
        ''')
        
        pre_resolution = cursor.fetchone()
        pre_resolution_stats = {
            'avg_volume': pre_resolution[0] or 0,
            'avg_spread': pre_resolution[1] or 0,
            'avg_price_deviation': pre_resolution[2] or 0,
            'market_count': pre_resolution[3] or 0
        }
        
        conn.close()
        
        return {
            'day_of_week': day_patterns,
            'hour_of_day': hour_patterns,
            'pre_resolution': pre_resolution_stats
        }
    
    def get_pending_alerts(self) -> List[Dict]:
        """Get alerts that should trigger now"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, e.event_name, e.event_date, e.category
            FROM event_alerts a
            JOIN calendar_events e ON a.event_id = e.id
            WHERE a.triggered = 0
            AND datetime(a.alert_time) <= datetime('now')
            ORDER BY a.alert_time ASC
        ''')
        
        columns = [desc[0] for desc in cursor.description]
        alerts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return alerts
    
    def mark_alert_triggered(self, alert_id: int):
        """Mark an alert as triggered"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE event_alerts 
            SET triggered = 1 
            WHERE id = ?
        ''', (alert_id,))
        
        conn.commit()
        conn.close()


# ============================================================================
# ASCII Calendar Display
# ============================================================================

def print_calendar_header(title: str):
    """Print calendar header"""
    width = 80
    print("\n" + "=" * width)
    print(f"  {title}".ljust(width))
    print("=" * width + "\n")


def print_event_list(events: List[Dict], title: str = "Events"):
    """Print events in a formatted list"""
    print_calendar_header(title)
    
    if not events:
        print("  📭 No events found\n")
        return
    
    # Group by date
    by_date = defaultdict(list)
    for event in events:
        event_date = event['event_date'][:10]  # Get YYYY-MM-DD part
        by_date[event_date].append(event)
    
    # Print by date
    for date in sorted(by_date.keys()):
        date_obj = datetime.fromisoformat(date)
        day_name = date_obj.strftime('%A')
        
        # Calculate days from now
        days_diff = (date_obj.date() - datetime.now().date()).days
        
        if days_diff == 0:
            day_label = "TODAY"
        elif days_diff == 1:
            day_label = "TOMORROW"
        elif days_diff == -1:
            day_label = "YESTERDAY"
        elif days_diff > 0:
            day_label = f"in {days_diff} days"
        else:
            day_label = f"{abs(days_diff)} days ago"
        
        print(f"  📅 {date} ({day_name}) - {day_label}")
        print("  " + "-" * 76)
        
        for event in by_date[date]:
            event_type = event.get('event_type', 'manual')
            category = event.get('category', 'general')
            name = event.get('event_name', 'Unnamed event')
            
            # Icon based on type
            if event_type == 'resolution':
                icon = '🏁'
            elif category == 'sports':
                icon = '⚽'
            elif category in ['politics', 'Politics']:
                icon = '🗳️'
            elif category in ['crypto', 'Crypto']:
                icon = '₿'
            else:
                icon = '📌'
            
            print(f"    {icon} {name}")
            
            if event.get('description'):
                desc = event['description'][:70]
                print(f"       └─ {desc}")
        
        print()


def print_expiring_markets(markets: List[Dict], title: str = "Markets Expiring Soon"):
    """Print expiring markets with risk indicators"""
    print_calendar_header(title)
    
    if not markets:
        print("  ✅ No markets expiring soon\n")
        return
    
    for market in markets:
        question = market.get('question', 'Unknown')[:60]
        days_left = market.get('days_left', 0)
        price = market.get('price_yes', 0)
        volume = market.get('volume_24h', 0)
        
        # Risk level based on days left
        if days_left < 1:
            risk = "🔴 CRITICAL"
        elif days_left < 3:
            risk = "🟠 HIGH"
        elif days_left < 7:
            risk = "🟡 MEDIUM"
        else:
            risk = "🟢 LOW"
        
        print(f"  {risk}")
        print(f"    Question: {question}")
        print(f"    Resolves: {market.get('end_time', 'Unknown')[:16]} ({days_left:.1f} days)")
        print(f"    Price: {price:.3f} | Volume: ${volume:,.0f}")
        print()


def print_patterns(patterns: Dict):
    """Print trading pattern analysis"""
    print_calendar_header("📊 Trading Pattern Analysis")
    
    # Best days to trade
    print("  📆 Best Days to Trade (by volume):\n")
    day_patterns = sorted(patterns['day_of_week'], key=lambda x: x['avg_volume'], reverse=True)
    
    for i, day_data in enumerate(day_patterns[:3], 1):
        day = day_data['day']
        vol = day_data['avg_volume']
        spread = day_data['avg_spread']
        print(f"    {i}. {day:10s} - Avg Volume: ${vol:,.0f} | Avg Spread: {spread:.4f}")
    
    # Best hours to trade
    print("\n  🕐 Best Hours to Trade (by volume):\n")
    hour_patterns = sorted(patterns['hour_of_day'], key=lambda x: x['avg_volume'], reverse=True)
    
    for i, hour_data in enumerate(hour_patterns[:5], 1):
        hour = hour_data['hour']
        vol = hour_data['avg_volume']
        spread = hour_data['avg_spread']
        time_label = f"{hour:02d}:00"
        print(f"    {i}. {time_label} - Avg Volume: ${vol:,.0f} | Avg Spread: {spread:.4f}")
    
    # Pre-resolution behavior
    print("\n  🏁 Pre-Resolution Behavior (7 days before):\n")
    pre_res = patterns['pre_resolution']
    print(f"    Avg Volume: ${pre_res['avg_volume']:,.0f}")
    print(f"    Avg Spread: {pre_res['avg_spread']:.4f}")
    print(f"    Avg Price Deviation from 50%: {pre_res['avg_price_deviation']:.3f}")
    print(f"    Markets Analyzed: {pre_res['market_count']}")
    
    print()


def print_mini_calendar(year: int, month: int, events: List[Dict]):
    """Print a mini ASCII calendar with event markers"""
    import calendar as cal
    
    # Get calendar
    month_cal = cal.monthcalendar(year, month)
    month_name = cal.month_name[month]
    
    # Parse events for this month
    event_dates = set()
    for event in events:
        try:
            event_date = datetime.fromisoformat(event['event_date'].replace('Z', '+00:00'))
            if event_date.year == year and event_date.month == month:
                event_dates.add(event_date.day)
        except:
            pass
    
    # Print header
    print(f"\n  {month_name} {year}".center(28))
    print("  " + "-" * 27)
    print("  Mo Tu We Th Fr Sa Su")
    
    # Print weeks
    for week in month_cal:
        week_str = "  "
        for day in week:
            if day == 0:
                week_str += "   "
            else:
                if day in event_dates:
                    week_str += f"{day:2d}*"
                else:
                    week_str += f"{day:2d} "
        print(week_str)
    
    print()


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Market Event Calendar for Polymarket Trading",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--week', action='store_true', help='Show this week\'s events')
    parser.add_argument('--upcoming', action='store_true', help='Show upcoming events (30 days)')
    parser.add_argument('--expiring', type=int, metavar='DAYS', help='Show markets expiring in N days')
    parser.add_argument('--patterns', action='store_true', help='Show trading patterns')
    parser.add_argument('--sync', action='store_true', help='Sync market resolutions to calendar')
    parser.add_argument('--add', nargs=3, metavar=('DATE', 'NAME', 'CATEGORY'), 
                       help='Add event: --add "2026-02-15" "Super Bowl" "sports"')
    parser.add_argument('--alerts', action='store_true', help='Show pending alerts')
    parser.add_argument('--mini', action='store_true', help='Show mini calendar view')
    
    args = parser.parse_args()
    
    calendar = MarketCalendar()
    
    # Add event
    if args.add:
        date, name, category = args.add
        event_id = calendar.add_event(date, name, category)
        print(f"\n✓ Event added (ID: {event_id})")
        print(f"  Date: {date}")
        print(f"  Name: {name}")
        print(f"  Category: {category}\n")
        return
    
    # Sync resolutions
    if args.sync:
        synced = calendar.sync_market_resolutions()
        print(f"\n✓ Synced {synced} market resolutions to calendar\n")
        return
    
    # Show alerts
    if args.alerts:
        alerts = calendar.get_pending_alerts()
        print_calendar_header("⏰ Pending Alerts")
        
        if not alerts:
            print("  ✅ No pending alerts\n")
        else:
            for alert in alerts:
                print(f"  🔔 {alert['message']}")
                print(f"     Event: {alert['event_name']}")
                print(f"     Date: {alert['event_date']}")
                print()
        return
    
    # Show patterns
    if args.patterns:
        patterns = calendar.analyze_patterns()
        print_patterns(patterns)
        return
    
    # Show expiring markets
    if args.expiring:
        markets = calendar.get_expiring_markets(days=args.expiring)
        print_expiring_markets(markets, f"Markets Expiring in {args.expiring} Days")
        return
    
    # Show week
    if args.week:
        events = calendar.get_week()
        print_event_list(events, "This Week's Events")
        
        if args.mini:
            now = datetime.now()
            print_mini_calendar(now.year, now.month, events)
        return
    
    # Show upcoming
    if args.upcoming:
        events = calendar.get_upcoming(days=30)
        print_event_list(events, "Upcoming Events (30 Days)")
        
        if args.mini:
            now = datetime.now()
            print_mini_calendar(now.year, now.month, events)
        return
    
    # Default: show today
    events = calendar.get_today()
    print_event_list(events, "📅 Today's Events")
    
    # Also show upcoming resolutions (7 days)
    markets = calendar.get_expiring_markets(days=7)
    if markets:
        print_expiring_markets(markets, "⚠️  Markets Expiring This Week")


if __name__ == "__main__":
    main()
