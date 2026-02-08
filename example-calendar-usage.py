#!/usr/bin/env python3
"""
Market Calendar - Example Usage and Demo
Demonstrates calendar features with sample data
"""

from market_calendar import MarketCalendar
from datetime import datetime, timedelta
import os

def demo_calendar():
    """Demonstrate calendar features"""
    
    print("\n" + "="*80)
    print("  🗓️  MARKET CALENDAR DEMO")
    print("="*80)
    
    # Initialize calendar
    calendar = MarketCalendar()
    
    # Add some sample events
    print("\n📝 Adding sample events...\n")
    
    today = datetime.now()
    
    # Super Bowl
    super_bowl = (today + timedelta(days=9)).date().isoformat()
    calendar.add_event(super_bowl, "Super Bowl LX", "sports", 
                      description="Championship game - high betting volume expected")
    print(f"  ✓ Added: Super Bowl LX ({super_bowl})")
    
    # Federal Reserve announcement
    fed_meeting = (today + timedelta(days=14)).date().isoformat()
    calendar.add_event(fed_meeting, "Federal Reserve Rate Decision", "politics",
                      description="Interest rate announcement - market moving event")
    print(f"  ✓ Added: Fed Rate Decision ({fed_meeting})")
    
    # Crypto event
    crypto_conf = (today + timedelta(days=21)).date().isoformat()
    calendar.add_event(crypto_conf, "Bitcoin Conference 2026", "crypto",
                      description="Major crypto industry event")
    print(f"  ✓ Added: Bitcoin Conference ({crypto_conf})")
    
    # Earnings report
    earnings = (today + timedelta(days=5)).date().isoformat()
    calendar.add_event(earnings, "NVIDIA Q1 Earnings", "business",
                      description="Tech earnings - AI market sentiment indicator")
    print(f"  ✓ Added: NVIDIA Earnings ({earnings})")
    
    # Weekly recurring event
    weekly = (today + timedelta(days=3)).date().isoformat()
    calendar.add_event(weekly, "Weekly Trading Review", "general",
                      recurring="weekly", alert_hours=2)
    print(f"  ✓ Added: Weekly Trading Review ({weekly})")
    
    print("\n" + "-"*80)
    
    # Sync market resolutions (if markets exist)
    print("\n🔄 Syncing market resolutions from database...")
    synced = calendar.sync_market_resolutions()
    print(f"  ✓ Synced {synced} market resolutions")
    
    print("\n" + "-"*80)
    
    # Show today's events
    print("\n📅 TODAY'S EVENTS:")
    print("-"*80)
    events_today = calendar.get_today()
    if events_today:
        for event in events_today:
            print(f"  • {event['event_name']} ({event['category']})")
    else:
        print("  No events today")
    
    # Show this week
    print("\n📆 THIS WEEK:")
    print("-"*80)
    events_week = calendar.get_week()
    print(f"  Total events: {len(events_week)}")
    for event in events_week[:5]:  # Show first 5
        event_date = event['event_date'][:10]
        print(f"  • {event_date}: {event['event_name']}")
    
    # Show expiring markets
    print("\n⚠️  MARKETS EXPIRING SOON (7 days):")
    print("-"*80)
    expiring = calendar.get_expiring_markets(days=7)
    if expiring:
        print(f"  Found {len(expiring)} markets expiring soon:")
        for market in expiring[:3]:  # Show first 3
            question = market['question'][:50]
            days_left = market['days_left']
            print(f"  • {question}... ({days_left:.1f} days left)")
    else:
        print("  ✅ No markets expiring in next 7 days")
    
    # Show alerts
    print("\n🔔 PENDING ALERTS:")
    print("-"*80)
    alerts = calendar.get_pending_alerts()
    if alerts:
        print(f"  {len(alerts)} alerts ready:")
        for alert in alerts[:3]:
            print(f"  • {alert['message']}")
    else:
        print("  No pending alerts")
    
    print("\n" + "="*80)
    print("\n✅ Demo complete!")
    print("\nTry these commands:")
    print("  python market-calendar.py                  # Today's events")
    print("  python market-calendar.py --week           # This week")
    print("  python market-calendar.py --upcoming       # Next 30 days")
    print("  python market-calendar.py --expiring 7     # Expiring markets")
    print("  python market-calendar.py --patterns       # Trading patterns")
    print("  python market-calendar.py --sync           # Sync resolutions")
    print("\n")


def demo_programmatic_usage():
    """Show how to use calendar in Python scripts"""
    
    print("\n" + "="*80)
    print("  🐍 PROGRAMMATIC USAGE EXAMPLES")
    print("="*80 + "\n")
    
    # Initialize
    print("# Initialize calendar")
    print("from market_calendar import MarketCalendar")
    print("calendar = MarketCalendar()\n")
    
    # Add event
    print("# Add a custom event")
    print('event_id = calendar.add_event(')
    print('    event_date="2026-03-15",')
    print('    event_name="March Madness Finals",')
    print('    category="sports",')
    print('    description="NCAA tournament - high volume expected",')
    print('    alert_hours=48')
    print(')\n')
    
    # Get events
    print("# Get today's events")
    print("events = calendar.get_today()")
    print("for event in events:")
    print("    print(f\"{event['event_name']} - {event['category']}\")\n")
    
    # Get expiring
    print("# Check expiring markets")
    print("expiring = calendar.get_expiring_markets(days=7)")
    print("for market in expiring:")
    print("    if market['days_left'] < 2:")
    print("        print(f\"⚠️ URGENT: {market['question']}\")\n")
    
    # Analyze patterns
    print("# Analyze trading patterns")
    print("patterns = calendar.analyze_patterns()")
    print("best_day = patterns['day_of_week'][0]")
    print("print(f\"Best day to trade: {best_day['day']}\")\n")
    
    # Sync
    print("# Sync resolutions")
    print("synced = calendar.sync_market_resolutions()")
    print(f"print(f\"Synced {{synced}} market resolutions\")\n")
    
    print("="*80 + "\n")


def demo_integration_with_trading():
    """Show integration with trading system"""
    
    print("\n" + "="*80)
    print("  🤝 INTEGRATION WITH TRADING SYSTEM")
    print("="*80 + "\n")
    
    print("# Example: Check expiring positions before placing trade")
    print("""
def check_position_risks():
    calendar = MarketCalendar()
    expiring = calendar.get_expiring_markets(days=3)
    
    for market in expiring:
        if market['days_left'] < 1:
            print(f"⚠️  CRITICAL: {market['question']}")
            print(f"   Resolves in {market['days_left']:.1f} days")
            print(f"   Current price: {market['price_yes']:.3f}")
            print(f"   Consider exiting position!\\n")
""")
    
    print("\n# Example: Alert before major events")
    print("""
def pre_event_alert():
    calendar = MarketCalendar()
    alerts = calendar.get_pending_alerts()
    
    for alert in alerts:
        if alert['category'] in ['sports', 'politics']:
            send_telegram_alert(alert['message'])
            calendar.mark_alert_triggered(alert['id'])
""")
    
    print("\n# Example: Optimize trade timing with patterns")
    print("""
def optimize_trade_timing():
    calendar = MarketCalendar()
    patterns = calendar.analyze_patterns()
    
    # Find best time to trade
    best_hours = sorted(patterns['hour_of_day'], 
                       key=lambda x: x['avg_volume'], 
                       reverse=True)[:3]
    
    print("Best hours to trade:")
    for hour_data in best_hours:
        print(f"  {hour_data['hour']:02d}:00 - Volume: ${hour_data['avg_volume']:,.0f}")
""")
    
    print("\n# Example: Pre-resolution strategy")
    print("""
def pre_resolution_strategy(market_id):
    calendar = MarketCalendar()
    patterns = calendar.analyze_patterns()
    
    pre_res = patterns['pre_resolution']
    
    # Markets typically deviate from 50% as resolution approaches
    # Use this to inform your exit strategy
    expected_deviation = pre_res['avg_price_deviation']
    
    print(f"Historical pre-resolution behavior:")
    print(f"  Avg price deviation: {expected_deviation:.3f}")
    print(f"  Avg spread: {pre_res['avg_spread']:.4f}")
""")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    # Run demos
    demo_calendar()
    demo_programmatic_usage()
    demo_integration_with_trading()
    
    print("\n🎉 Great success! Your market calendar is ready.\n")
    print("Next steps:")
    print("  1. Run: python market-calendar.py --sync")
    print("  2. Add your own events: python market-calendar.py --add DATE NAME CATEGORY")
    print("  3. Check patterns: python market-calendar.py --patterns")
    print("  4. Set up cron job to check alerts daily")
    print("\n")
