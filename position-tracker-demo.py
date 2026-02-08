#!/usr/bin/env python3
"""
Demo script for Position Tracker
Shows programmatic usage examples
"""

from position_tracker import PositionTracker
import time

def demo():
    print("=" * 70)
    print("Position Tracker Demo - Polymarket Trading System")
    print("=" * 70)
    
    # Initialize tracker with $10,000 bankroll
    tracker = PositionTracker(db_path="demo_positions.db", bankroll=10000.0)
    
    print("\n1️⃣  Opening Positions...")
    print("-" * 70)
    
    # Open some positions
    pos1 = tracker.open_position(
        market_id="will-bitcoin-hit-100k-2024",
        entry_price=0.52,
        size=1000,
        stop_loss=0.40,
        take_profit=0.75,
        sector="Crypto"
    )
    
    pos2 = tracker.open_position(
        market_id="trump-wins-2024",
        entry_price=0.48,
        size=500,
        stop_loss=0.35,
        take_profit=0.80,
        sector="Politics"
    )
    
    pos3 = tracker.open_position(
        market_id="ai-breakthrough-2024",
        entry_price=0.65,
        size=750,
        stop_loss=0.50,
        take_profit=0.90,
        sector="Technology"
    )
    
    # Show all positions
    print("\n2️⃣  Current Positions:")
    print("-" * 70)
    positions = tracker.get_all_positions()
    for p in positions:
        print(f"  Position #{p.position_id}: {p.market_id}")
        print(f"    Entry: ${p.entry_price:.4f} | Size: {p.size} shares")
        print(f"    Value: ${p.position_value:.2f} | P&L: ${p.unrealized_pnl:+.2f}")
    
    # Update prices (simulate market movement)
    print("\n3️⃣  Simulating Price Changes...")
    print("-" * 70)
    tracker.update_price(pos1, 0.58)  # Bitcoin position up
    tracker.update_price(pos2, 0.45)  # Trump position down slightly
    tracker.update_price(pos3, 0.72)  # AI position up
    print("  ✓ Prices updated")
    
    # Check for alerts
    print("\n4️⃣  Checking Alerts...")
    print("-" * 70)
    alerts = tracker.check_alerts()
    if alerts:
        for alert in alerts:
            emoji = "🚨" if alert['severity'] == 'HIGH' else "⚡"
            print(f"  {emoji} {alert['message']}")
    else:
        print("  ✓ No alerts at this time")
    
    # Show portfolio summary
    print("\n5️⃣  Portfolio Summary:")
    print("-" * 70)
    summary = tracker.get_summary()
    print(f"  Total Value:     ${summary['total_value']:,.2f}")
    print(f"  Cash Balance:    ${summary['cash_balance']:,.2f}")
    print(f"  Position Value:  ${summary['position_value']:,.2f}")
    print(f"  Unrealized P&L:  ${summary['unrealized_pnl']:+,.2f} ({summary['total_pnl_pct']:+.2f}%)")
    print(f"  Open Positions:  {summary['position_count']}")
    
    print(f"\n  Exposure by Sector:")
    for sector, value in summary['exposure_by_sector'].items():
        pct = (value / summary['total_value']) * 100
        print(f"    {sector:>12}: ${value:>8,.2f} ({pct:>5.1f}%)")
    
    # Create a snapshot
    print("\n6️⃣  Creating Portfolio Snapshot...")
    print("-" * 70)
    snapshot_id = tracker.create_snapshot()
    print(f"  ✓ Snapshot #{snapshot_id} created")
    
    # Close one position
    print("\n7️⃣  Closing Position...")
    print("-" * 70)
    realized_pnl = tracker.close_position(pos2, 0.47)  # Close Trump position at slight loss
    print(f"  Position #{pos2} closed")
    print(f"  Realized P&L: ${realized_pnl:+.2f}")
    
    # Final summary
    print("\n8️⃣  Final Portfolio State:")
    print("-" * 70)
    summary = tracker.get_summary()
    print(f"  Total Value:     ${summary['total_value']:,.2f}")
    print(f"  Cash Balance:    ${summary['cash_balance']:,.2f}")
    print(f"  Unrealized P&L:  ${summary['unrealized_pnl']:+,.2f}")
    print(f"  Realized P&L:    ${summary['realized_pnl']:+,.2f}")
    print(f"  Total P&L:       ${summary['total_pnl']:+,.2f} ({summary['total_pnl_pct']:+.2f}%)")
    
    # P&L breakdown
    print("\n9️⃣  P&L Breakdown:")
    print("-" * 70)
    breakdown = tracker.get_pnl_breakdown()
    
    print("  Open Positions:")
    for p in breakdown['open_positions']:
        print(f"    #{p['position_id']} {p['market_id'][:35]}")
        print(f"      P&L: ${p['unrealized_pnl']:+.2f} ({p['unrealized_pnl_pct']:+.2f}%)")
    
    print(f"\n  Closed Positions:")
    for p in breakdown['closed_positions']:
        print(f"    #{p['position_id']} {p['market_id'][:35]}")
        print(f"      Realized P&L: ${p['realized_pnl']:+.2f}")
    
    print("\n" + "=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("  • Run: python position-tracker.py --help")
    print("  • View positions: python position-tracker.py --db demo_positions.db")
    print("  • Check summary: python position-tracker.py --db demo_positions.db --summary")
    print("  • See P&L: python position-tracker.py --db demo_positions.db --pnl")
    
    tracker.close()

if __name__ == '__main__':
    demo()
