#!/usr/bin/env python3
"""
Demo script for Audit Trail System
Shows usage examples and tests all functionality
"""

from audit_trail import AuditLog
import json
import os

def demo():
    """Demonstrate audit trail functionality"""
    
    # Use a demo database
    demo_db = "audit_demo.db"
    
    # Clean up old demo database
    if os.path.exists(demo_db):
        os.remove(demo_db)
    
    print("=" * 80)
    print("AUDIT TRAIL SYSTEM DEMO")
    print("=" * 80)
    
    # Initialize audit log
    audit = AuditLog(demo_db)
    print("\n✓ Initialized audit log database")
    
    # 1. Log system start
    print("\n1. Logging system start...")
    audit.log_system_event("START", {"version": "1.0.0", "environment": "production"})
    
    # 2. Log configuration change
    print("2. Logging configuration change...")
    audit.log_config_change(
        field="max_position_size",
        old_value=1000,
        new_value=1500
    )
    
    # 3. Log trading signals
    print("3. Logging trading signals...")
    signal_id = audit.log_signal(
        market_id="bitcoin-price-feb-2026",
        signal_type="BUY",
        params={
            "indicator": "moving_average_cross",
            "confidence": 0.85,
            "target_price": 0.65
        }
    )
    print(f"   Signal ID: {signal_id}")
    
    audit.log_signal(
        market_id="eth-above-3000",
        signal_type="SELL",
        params={
            "indicator": "rsi_overbought",
            "confidence": 0.72,
            "target_price": 0.45
        }
    )
    
    # 4. Log position opened
    print("4. Logging position opened...")
    audit.log_trade(
        position_id="pos_001",
        action="OPEN",
        market_id="bitcoin-price-feb-2026",
        price=0.52,
        size=500,
        signal_id=signal_id
    )
    
    # 5. Log position closed
    print("5. Logging position closed...")
    audit.log_trade(
        position_id="pos_001",
        action="CLOSE",
        market_id="bitcoin-price-feb-2026",
        price=0.67,
        size=500,
        pnl=75.0,
        reason="Take profit target reached"
    )
    
    # 6. Log risk limit hit
    print("6. Logging risk limit hit...")
    audit.log_risk_limit(
        limit_type="max_daily_loss",
        value=250.0,
        market="eth-above-3000"
    )
    
    # 7. Query recent events
    print("\n" + "=" * 80)
    print("QUERYING EVENTS")
    print("=" * 80)
    
    print("\n📋 All recent events:")
    events = audit.query(limit=10)
    for event in events:
        print(f"  [{event['id']}] {event['event_type']} - {event['timestamp']}")
    
    print("\n📋 Filter by event type (SIGNAL_GENERATED):")
    signals = audit.query(event_type="SIGNAL_GENERATED")
    for event in signals:
        print(f"  [{event['id']}] {event['data']['market_id']} - {event['data']['signal_type']}")
    
    print("\n📋 Filter by market (bitcoin):")
    bitcoin_events = audit.query(market="bitcoin")
    for event in bitcoin_events:
        print(f"  [{event['id']}] {event['event_type']} - {event['market']}")
    
    # 8. Verify integrity
    print("\n" + "=" * 80)
    print("INTEGRITY VERIFICATION")
    print("=" * 80)
    
    result = audit.verify_integrity()
    print(f"\n{result['message']}")
    print(f"Total events: {result['total_events']}")
    print(f"Verified events: {result['verified_events']}")
    
    if not result['valid']:
        print("\n⚠️ ERRORS:")
        for error in result['errors']:
            print(f"  Event {error['id']}: {error['error']}")
    
    # 9. Export examples
    print("\n" + "=" * 80)
    print("EXPORT EXAMPLES")
    print("=" * 80)
    
    print("\n📤 Exporting to JSON...")
    count = audit.export_json("audit_export.json", limit=50)
    print(f"✓ Exported {count} events to audit_export.json")
    
    print("\n📤 Exporting to CSV...")
    count = audit.export_csv("audit_export.csv", limit=50)
    print(f"✓ Exported {count} events to audit_export.csv")
    
    print("\n📤 Exporting to HTML...")
    count = audit.export_html("audit_export.html", limit=50)
    print(f"✓ Exported {count} events to audit_export.html")
    
    # 10. Show integration example
    print("\n" + "=" * 80)
    print("INTEGRATION EXAMPLE")
    print("=" * 80)
    
    print("""
# In your trading bot:

from audit_trail import AuditLog

# Initialize once
audit = AuditLog()

# Log system start
audit.log_system_event("START", {"version": "1.0.0"})

# When generating signals
signal_id = audit.log_signal(
    market_id="bitcoin-price-feb-2026",
    signal_type="BUY",
    params={"confidence": 0.85}
)

# When opening positions
audit.log_trade(
    position_id="pos_001",
    action="OPEN",
    market_id="bitcoin-price-feb-2026",
    price=0.52,
    size=500,
    signal_id=signal_id
)

# When closing positions
audit.log_trade(
    position_id="pos_001",
    action="CLOSE",
    market_id="bitcoin-price-feb-2026",
    price=0.67,
    pnl=75.0,
    reason="Take profit"
)

# Verify integrity periodically
result = audit.verify_integrity()
if not result['valid']:
    print("⚠️ TAMPERING DETECTED!")

# Query events
events = audit.query(
    start_date="2026-02-01",
    end_date="2026-02-06",
    event_type="SIGNAL_GENERATED"
)
    """)
    
    print("\n" + "=" * 80)
    print("CLI USAGE EXAMPLES")
    print("=" * 80)
    
    print("""
# Show recent events
python audit-trail.py

# Filter by date range
python audit-trail.py --range 2026-02-01 2026-02-06

# Filter by event type
python audit-trail.py --type SIGNAL_GENERATED

# Filter by market
python audit-trail.py --market "bitcoin"

# Full-text search
python audit-trail.py --search "BUY"

# Verify integrity
python audit-trail.py --verify

# Export to CSV
python audit-trail.py --export audit.csv

# Export to HTML with filters
python audit-trail.py --export report.html --range 2026-02-01 2026-02-06

# Export to JSON
python audit-trail.py --export audit.json --type POSITION_OPEN
    """)
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE!")
    print("=" * 80)
    print(f"\nDemo database: {demo_db}")
    print("Exported files: audit_export.json, audit_export.csv, audit_export.html")
    print("\nGreat success! 🎉")


if __name__ == '__main__':
    demo()
