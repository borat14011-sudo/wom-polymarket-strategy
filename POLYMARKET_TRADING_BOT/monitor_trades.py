#!/usr/bin/env python3
"""
Continuous Trade Monitoring
Alerts you when high-value opportunities appear
"""

import schedule
import time
from datetime import datetime
from trade_alerts import PolymarketAlerts

def check_trades():
    """Check for best trades and alert"""
    alerts = PolymarketAlerts()
    opportunities = alerts.find_best_trades(min_score=5)  # Only STRONG trades
    
    if opportunities:
        print(f"\n🔔 {len(opportunities)} STRONG trade opportunities found!")
        for opp in opportunities[:3]:  # Top 3
            alerts.send_alert(opp)
    else:
        print(f"[{datetime.now()}] No strong trades found. Checking again later...")

def main():
    print("=" * 60)
    print("POLYMARKET TRADE ALERT SYSTEM")
    print("=" * 60)
    print("\nMonitoring for high-value trades...")
    print("Checks every hour for opportunities score 5+\n")
    
    # Check immediately
    check_trades()
    
    # Schedule hourly checks
    schedule.every(1).hours.do(check_trades)
    
    print("\n⏰ Running... (Press Ctrl+C to stop)\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped. Good luck trading!")

if __name__ == "__main__":
    main()
