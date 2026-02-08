#!/usr/bin/env python3
"""
Audit Trail System for Polymarket Trading
Compliance-ready logging with hash chain integrity verification
"""

import sqlite3
import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import csv
import sys


class AuditLog:
    """
    Immutable audit logging system with hash chain verification
    """
    
    def __init__(self, db_path: str = "audit_trail.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database with audit_events table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create audit_events table with hash chain
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                market TEXT,
                data TEXT NOT NULL,
                previous_hash TEXT,
                hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for fast queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_market ON audit_events(market)")
        
        conn.commit()
        conn.close()
    
    def _get_previous_hash(self) -> Optional[str]:
        """Get hash of the most recent event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM audit_events ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def _compute_hash(self, timestamp: str, event_type: str, data: str, previous_hash: Optional[str]) -> str:
        """Compute SHA-256 hash for event"""
        hash_input = f"{timestamp}|{event_type}|{data}|{previous_hash or ''}"
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    def _log_event(self, event_type: str, market: Optional[str], data: Dict[str, Any]):
        """Internal method to log an event with hash chain"""
        timestamp = datetime.utcnow().isoformat() + "Z"
        data_json = json.dumps(data, sort_keys=True)
        previous_hash = self._get_previous_hash()
        event_hash = self._compute_hash(timestamp, event_type, data_json, previous_hash)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_events (timestamp, event_type, market, data, previous_hash, hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, event_type, market, data_json, previous_hash, event_hash))
        
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        
        return event_id, event_hash
    
    # === Event Logging Methods ===
    
    def log_signal(self, market_id: str, signal_type: str, params: Dict[str, Any]) -> int:
        """Log a trading signal generation"""
        data = {
            "market_id": market_id,
            "signal_type": signal_type,
            "params": params
        }
        event_id, _ = self._log_event("SIGNAL_GENERATED", market_id, data)
        return event_id
    
    def log_trade(self, position_id: str, action: str, market_id: str, 
                  price: Optional[float] = None, size: Optional[float] = None,
                  signal_id: Optional[int] = None, pnl: Optional[float] = None,
                  reason: Optional[str] = None) -> int:
        """Log position opened or closed"""
        event_type = f"POSITION_{action.upper()}"
        data = {
            "position_id": position_id,
            "action": action,
            "market_id": market_id
        }
        
        if price is not None:
            data["price"] = price
        if size is not None:
            data["size"] = size
        if signal_id is not None:
            data["signal_id"] = signal_id
        if pnl is not None:
            data["pnl"] = pnl
        if reason is not None:
            data["reason"] = reason
        
        event_id, _ = self._log_event(event_type, market_id, data)
        return event_id
    
    def log_risk_limit(self, limit_type: str, value: float, market: Optional[str] = None) -> int:
        """Log risk limit hit"""
        data = {
            "limit_type": limit_type,
            "value": value
        }
        event_id, _ = self._log_event("RISK_LIMIT_HIT", market, data)
        return event_id
    
    def log_config_change(self, field: str, old_value: Any, new_value: Any) -> int:
        """Log configuration change"""
        data = {
            "field": field,
            "old_value": old_value,
            "new_value": new_value
        }
        event_id, _ = self._log_event("CONFIG_CHANGED", None, data)
        return event_id
    
    def log_system_event(self, action: str, details: Optional[Dict[str, Any]] = None) -> int:
        """Log system start/stop/restart"""
        event_type = f"SYSTEM_{action.upper()}"
        data = details or {}
        event_id, _ = self._log_event(event_type, None, data)
        return event_id
    
    # === Query Methods ===
    
    def query(self, 
              start_date: Optional[str] = None,
              end_date: Optional[str] = None,
              event_type: Optional[str] = None,
              market: Optional[str] = None,
              search: Optional[str] = None,
              limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query audit events with filters
        
        Args:
            start_date: ISO format date string (YYYY-MM-DD)
            end_date: ISO format date string (YYYY-MM-DD)
            event_type: Filter by event type
            market: Filter by market (partial match)
            search: Full-text search in data
            limit: Maximum number of results
        
        Returns:
            List of event dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT id, timestamp, event_type, market, data, previous_hash, hash FROM audit_events WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            # Include the entire end date
            query += " AND timestamp < ?"
            params.append(f"{end_date}T23:59:59.999Z")
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type.upper())
        
        if market:
            query += " AND market LIKE ?"
            params.append(f"%{market}%")
        
        if search:
            query += " AND data LIKE ?"
            params.append(f"%{search}%")
        
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        events = []
        for row in results:
            event = {
                "id": row[0],
                "timestamp": row[1],
                "event_type": row[2],
                "market": row[3],
                "data": json.loads(row[4]),
                "previous_hash": row[5],
                "hash": row[6]
            }
            events.append(event)
        
        return events
    
    # === Integrity Verification ===
    
    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify hash chain integrity
        
        Returns:
            Dictionary with verification results
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, event_type, data, previous_hash, hash FROM audit_events ORDER BY id")
        events = cursor.fetchall()
        conn.close()
        
        if not events:
            return {
                "valid": True,
                "total_events": 0,
                "message": "No events to verify"
            }
        
        errors = []
        previous_hash = None
        
        for event in events:
            event_id, timestamp, event_type, data, stored_prev_hash, stored_hash = event
            
            # Verify previous hash matches
            if stored_prev_hash != previous_hash:
                errors.append({
                    "id": event_id,
                    "error": "Previous hash mismatch",
                    "expected": previous_hash,
                    "found": stored_prev_hash
                })
            
            # Recompute hash
            computed_hash = self._compute_hash(timestamp, event_type, data, stored_prev_hash)
            
            if computed_hash != stored_hash:
                errors.append({
                    "id": event_id,
                    "error": "Hash verification failed",
                    "expected": computed_hash,
                    "found": stored_hash
                })
            
            previous_hash = stored_hash
        
        result = {
            "valid": len(errors) == 0,
            "total_events": len(events),
            "verified_events": len(events) - len(errors),
            "errors": errors
        }
        
        if errors:
            result["message"] = f"⚠️ TAMPERING DETECTED: {len(errors)} events failed verification"
        else:
            result["message"] = f"✓ All {len(events)} events verified successfully"
        
        return result
    
    # === Export Methods ===
    
    def export_json(self, output_path: str, **query_params):
        """Export query results to JSON"""
        events = self.query(**query_params)
        
        with open(output_path, 'w') as f:
            json.dump(events, f, indent=2)
        
        return len(events)
    
    def export_csv(self, output_path: str, **query_params):
        """Export query results to CSV"""
        events = self.query(**query_params)
        
        if not events:
            with open(output_path, 'w') as f:
                f.write("No events found\n")
            return 0
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            # Flatten data for CSV
            fieldnames = ['id', 'timestamp', 'event_type', 'market', 'hash', 'previous_hash']
            
            # Add data fields
            data_fields = set()
            for event in events:
                data_fields.update(event['data'].keys())
            
            fieldnames.extend(sorted(data_fields))
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in events:
                row = {
                    'id': event['id'],
                    'timestamp': event['timestamp'],
                    'event_type': event['event_type'],
                    'market': event['market'] or '',
                    'hash': event['hash'],
                    'previous_hash': event['previous_hash'] or ''
                }
                # Flatten data fields
                for key, value in event['data'].items():
                    if isinstance(value, (dict, list)):
                        row[key] = json.dumps(value)
                    else:
                        row[key] = value
                
                writer.writerow(row)
        
        return len(events)
    
    def export_html(self, output_path: str, **query_params):
        """Export query results to HTML report"""
        events = self.query(**query_params)
        
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Audit Trail Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .stats {
            color: #666;
            font-size: 14px;
        }
        .event {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .event-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        .event-type {
            font-weight: bold;
            color: #0066cc;
        }
        .timestamp {
            color: #666;
            font-size: 13px;
        }
        .market {
            color: #666;
            font-size: 13px;
            margin-top: 5px;
        }
        .data {
            background: #f9f9f9;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            overflow-x: auto;
        }
        .hash {
            margin-top: 10px;
            font-size: 11px;
            color: #999;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Audit Trail Report</h1>
        <div class="stats">
            Generated: {generated_time}<br>
            Total Events: {total_events}
        </div>
    </div>
"""
        
        html = html.format(
            generated_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            total_events=len(events)
        )
        
        for event in events:
            market_html = f'<div class="market">Market: {event["market"]}</div>' if event.get('market') else ''
            
            html += f"""
    <div class="event">
        <div class="event-header">
            <div>
                <div class="event-type">{event['event_type']}</div>
                {market_html}
            </div>
            <div class="timestamp">{event['timestamp']}</div>
        </div>
        <div class="data">{json.dumps(event['data'], indent=2)}</div>
        <div class="hash">Hash: {event['hash']}</div>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return len(events)


def main():
    """CLI interface for audit trail system"""
    parser = argparse.ArgumentParser(
        description='Audit Trail System for Polymarket Trading',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python audit-trail.py                              # Show recent events
  python audit-trail.py --range 2026-02-01 2026-02-06
  python audit-trail.py --type signal
  python audit-trail.py --market "bitcoin"
  python audit-trail.py --search "BUY"
  python audit-trail.py --verify                     # Verify integrity
  python audit-trail.py --export audit.csv
  python audit-trail.py --export report.html --range 2026-02-01 2026-02-06
        """
    )
    
    parser.add_argument('--db', default='audit_trail.db', help='Database path')
    parser.add_argument('--range', nargs=2, metavar=('START', 'END'), help='Date range (YYYY-MM-DD)')
    parser.add_argument('--type', dest='event_type', help='Filter by event type')
    parser.add_argument('--market', help='Filter by market')
    parser.add_argument('--search', help='Full-text search')
    parser.add_argument('--limit', type=int, default=100, help='Maximum results (default: 100)')
    parser.add_argument('--verify', action='store_true', help='Verify hash chain integrity')
    parser.add_argument('--export', metavar='FILE', help='Export to file (JSON/CSV/HTML based on extension)')
    
    args = parser.parse_args()
    
    audit = AuditLog(args.db)
    
    # Verify integrity
    if args.verify:
        print("🔍 Verifying audit trail integrity...\n")
        result = audit.verify_integrity()
        
        print(result['message'])
        print(f"\nTotal events: {result['total_events']}")
        print(f"Verified: {result['verified_events']}")
        
        if not result['valid']:
            print(f"\n⚠️  ERRORS DETECTED:\n")
            for error in result['errors']:
                print(f"Event ID {error['id']}: {error['error']}")
                print(f"  Expected: {error.get('expected', 'N/A')}")
                print(f"  Found: {error.get('found', 'N/A')}\n")
            sys.exit(1)
        
        sys.exit(0)
    
    # Build query parameters
    query_params = {
        'limit': args.limit
    }
    
    if args.range:
        query_params['start_date'] = args.range[0]
        query_params['end_date'] = args.range[1]
    
    if args.event_type:
        query_params['event_type'] = args.event_type
    
    if args.market:
        query_params['market'] = args.market
    
    if args.search:
        query_params['search'] = args.search
    
    # Export
    if args.export:
        export_path = args.export
        ext = Path(export_path).suffix.lower()
        
        print(f"📤 Exporting to {export_path}...")
        
        if ext == '.json':
            count = audit.export_json(export_path, **query_params)
        elif ext == '.csv':
            count = audit.export_csv(export_path, **query_params)
        elif ext in ['.html', '.htm']:
            count = audit.export_html(export_path, **query_params)
        else:
            print(f"❌ Unsupported format: {ext}")
            print("Supported formats: .json, .csv, .html")
            sys.exit(1)
        
        print(f"✓ Exported {count} events to {export_path}")
        sys.exit(0)
    
    # Query and display
    events = audit.query(**query_params)
    
    if not events:
        print("No events found.")
        sys.exit(0)
    
    print(f"📋 Audit Trail - Showing {len(events)} events:\n")
    print("=" * 80)
    
    for event in events:
        print(f"\n[{event['id']}] {event['event_type']}")
        print(f"Timestamp: {event['timestamp']}")
        
        if event.get('market'):
            print(f"Market: {event['market']}")
        
        print(f"Data: {json.dumps(event['data'], indent=2)}")
        print(f"Hash: {event['hash'][:16]}...{event['hash'][-16:]}")
        print("-" * 80)


if __name__ == '__main__':
    main()
