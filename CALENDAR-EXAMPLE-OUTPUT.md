# Market Calendar - Example Output

## 📅 Today's Events View
```
================================================================================
  📅 Today's Events
================================================================================

  📅 2026-02-06 (Friday) - TODAY
  ----------------------------------------------------------------------------
    📌 Weekly Trading Review
       └─ Review open positions and market performance

  📭 No other events today
```

## 📆 This Week's Events
```
================================================================================
  📆 This Week's Events
================================================================================

  📅 2026-02-06 (Friday) - TODAY
  ----------------------------------------------------------------------------
    📌 Weekly Trading Review

  📅 2026-02-09 (Monday) - in 3 days
  ----------------------------------------------------------------------------
    ⚽ Super Bowl LX
       └─ Championship game - high betting volume expected

  📅 2026-02-11 (Wednesday) - in 5 days
  ----------------------------------------------------------------------------
    📌 NVIDIA Q1 Earnings
       └─ Tech earnings - AI market sentiment indicator

  📅 2026-02-13 (Friday) - in 7 days
  ----------------------------------------------------------------------------
    📌 Weekly Trading Review (recurring)
```

## ⚠️ Markets Expiring Soon
```
================================================================================
  ⚠️  Markets Expiring This Week
================================================================================

  🔴 CRITICAL
    Question: Will Bitcoin reach $100,000 by February 10, 2026?
    Resolves: 2026-02-10 15:00 (0.8 days)
    Price: 0.723 | Volume: $342,500

  🟠 HIGH
    Question: Will the Fed raise interest rates in February 2026?
    Resolves: 2026-02-12 14:00 (2.3 days)
    Price: 0.156 | Volume: $1,287,000

  🟡 MEDIUM
    Question: Will Super Bowl LX exceed 120 million viewers?
    Resolves: 2026-02-13 23:59 (6.9 days)
    Price: 0.812 | Volume: $2,450,000
```

## 📊 Trading Pattern Analysis
```
================================================================================
  📊 Trading Pattern Analysis
================================================================================

  📆 Best Days to Trade (by volume):

    1. Wednesday   - Avg Volume: $875,432 | Avg Spread: 0.0245
    2. Thursday    - Avg Volume: $823,156 | Avg Spread: 0.0238
    3. Tuesday     - Avg Volume: $789,234 | Avg Spread: 0.0251

  🕐 Best Hours to Trade (by volume):

    1. 14:00 - Avg Volume: $1,234,567 | Avg Spread: 0.0198
    2. 15:00 - Avg Volume: $1,187,432 | Avg Spread: 0.0203
    3. 13:00 - Avg Volume: $1,098,765 | Avg Spread: 0.0215
    4. 16:00 - Avg Volume: $987,654 | Avg Spread: 0.0228
    5. 10:00 - Avg Volume: $876,543 | Avg Spread: 0.0234

  🏁 Pre-Resolution Behavior (7 days before):

    Avg Volume: $945,678
    Avg Spread: 0.0287
    Avg Price Deviation from 50%: 0.234
    Markets Analyzed: 47

💡 INSIGHTS:
- Trade mid-week (Tue-Thu) for highest volume and tightest spreads
- Peak trading hours: 1-4 PM EST
- Markets deviate significantly from 50/50 as resolution approaches
- Spreads widen 17% in final week before resolution
- Volume increases 23% in final 48 hours
```

## 🔔 Alert System
```
================================================================================
  ⏰ Pending Alerts
================================================================================

  🔔 ⏰ Will Bitcoin reach $100,000 by February 10, 2026? in 24 hours
     Event: Resolution: Will Bitcoin reach $100,000 by February 10, 2026?
     Date: 2026-02-10T15:00:00Z

  🔔 ⏰ Super Bowl LX in 48 hours
     Event: Super Bowl LX
     Date: 2026-02-09T18:30:00Z

  🔔 ⏰ Federal Reserve Rate Decision in 168 hours
     Event: Federal Reserve Rate Decision
     Date: 2026-02-20T14:00:00Z
```

## 📅 Mini Calendar View
```
  February 2026
  ---------------------------
  Mo Tu We Th Fr Sa Su
               6* 7  8
   9* 10 11*12 13 14 15*
  16 17 18 19 20*21 22
  23 24 25 26 27 28

  * = Event scheduled
```

## 🐍 Programmatic Usage Example

```python
from market_calendar import MarketCalendar

# Initialize
calendar = MarketCalendar()

# Add event
event_id = calendar.add_event(
    event_date="2026-02-15",
    event_name="Super Bowl",
    category="sports",
    description="High betting volume expected",
    alert_hours=48
)

# Get today's events
events = calendar.get_today()
for event in events:
    print(f"{event['event_name']} - {event['category']}")

# Check expiring markets
expiring = calendar.get_expiring_markets(days=7)
for market in expiring:
    if market['days_left'] < 2:
        print(f"⚠️ URGENT: {market['question']}")
        print(f"   Resolves in {market['days_left']:.1f} days")

# Analyze patterns
patterns = calendar.analyze_patterns()
best_days = patterns['day_of_week']
print(f"Best day to trade: {best_days[0]['day']}")

# Sync market resolutions
synced = calendar.sync_market_resolutions()
print(f"Synced {synced} market resolutions")

# Get pending alerts
alerts = calendar.get_pending_alerts()
for alert in alerts:
    print(f"🔔 {alert['message']}")
    calendar.mark_alert_triggered(alert['id'])
```

## 🎯 Integration Examples

### 1. Pre-Trade Position Check
```python
def check_before_trade(market_id):
    calendar = MarketCalendar()
    expiring = calendar.get_expiring_markets(days=7)
    
    for market in expiring:
        if market['market_id'] == market_id:
            days_left = market['days_left']
            
            if days_left < 1:
                return False, "❌ Market resolves in <24h - too risky!"
            elif days_left < 3:
                return True, "⚠️ WARNING: Market resolves in 3 days"
            else:
                return True, "✅ OK to trade"
    
    return True, "✅ No resolution concerns"

# Usage
can_trade, message = check_before_trade("bitcoin-100k")
print(message)
```

### 2. Daily Alert System
```python
def daily_alert_check():
    """Run this as a cron job daily"""
    calendar = MarketCalendar()
    alerts = calendar.get_pending_alerts()
    
    for alert in alerts:
        # Send to Telegram
        send_telegram(
            f"🔔 {alert['message']}\n"
            f"Event: {alert['event_name']}\n"
            f"Date: {alert['event_date']}"
        )
        
        # Mark as sent
        calendar.mark_alert_triggered(alert['id'])
```

### 3. Pattern-Based Trading
```python
def should_trade_now():
    """Check if current time is optimal for trading"""
    calendar = MarketCalendar()
    patterns = calendar.analyze_patterns()
    
    now = datetime.now()
    current_hour = now.hour
    current_day = now.strftime('%A')
    
    # Get hour pattern
    hour_patterns = {p['hour']: p for p in patterns['hour_of_day']}
    current_hour_data = hour_patterns.get(current_hour, {})
    
    # Get day pattern
    day_patterns = {p['day']: p for p in patterns['day_of_week']}
    current_day_data = day_patterns.get(current_day, {})
    
    # Calculate score
    hour_volume = current_hour_data.get('avg_volume', 0)
    day_volume = current_day_data.get('avg_volume', 0)
    
    avg_hour_volume = sum(p['avg_volume'] for p in patterns['hour_of_day']) / 24
    avg_day_volume = sum(p['avg_volume'] for p in patterns['day_of_week']) / 7
    
    hour_score = hour_volume / avg_hour_volume if avg_hour_volume else 1
    day_score = day_volume / avg_day_volume if avg_day_volume else 1
    
    total_score = (hour_score + day_score) / 2
    
    if total_score > 1.2:
        return True, "🟢 HIGH activity period - great time to trade!"
    elif total_score > 0.8:
        return True, "🟡 NORMAL activity - OK to trade"
    else:
        return False, "🔴 LOW activity - consider waiting"

# Usage
should_trade, reason = should_trade_now()
print(reason)
```

### 4. Pre-Resolution Exit Strategy
```python
def check_exit_strategy(market_id):
    """Suggest exit timing based on patterns"""
    calendar = MarketCalendar()
    patterns = calendar.analyze_patterns()
    expiring = calendar.get_expiring_markets(days=30)
    
    # Find the market
    market = next((m for m in expiring if m['market_id'] == market_id), None)
    
    if not market:
        return "Market not found or already resolved"
    
    days_left = market['days_left']
    current_price = market['price_yes']
    
    # Historical pre-resolution behavior
    pre_res = patterns['pre_resolution']
    typical_deviation = pre_res['avg_price_deviation']
    typical_spread = pre_res['avg_spread']
    
    if days_left < 1:
        return "🔴 CRITICAL: Exit NOW! Market resolves in <24h"
    
    elif days_left < 3:
        # High volatility period
        if abs(current_price - 0.5) > 0.3:
            return "🟠 HIGH: Strong price signal - consider holding to capture value"
        else:
            return "🟠 HIGH: Price uncertain - consider exiting to reduce risk"
    
    elif days_left < 7:
        # Entering pre-resolution period
        spread_warning = " (spreads widening)" if typical_spread > 0.025 else ""
        return f"🟡 MEDIUM: Entering pre-resolution period{spread_warning}"
    
    else:
        return "🟢 LOW: Plenty of time - no immediate concerns"

# Usage
strategy = check_exit_strategy("bitcoin-100k")
print(strategy)
```

## 📋 CLI Commands Reference

```bash
# View today's events
python market-calendar.py

# View this week
python market-calendar.py --week

# View upcoming events (30 days)
python market-calendar.py --upcoming

# Add custom event
python market-calendar.py --add "2026-02-15" "Super Bowl" "sports"

# Check expiring markets (7 days)
python market-calendar.py --expiring 7

# View trading patterns
python market-calendar.py --patterns

# Sync market resolutions
python market-calendar.py --sync

# View pending alerts
python market-calendar.py --alerts

# Mini calendar view
python market-calendar.py --week --mini
```

## 🔧 Setup & Configuration

### 1. Initialize Database
```bash
python market-calendar.py --sync
```

### 2. Add Important Events
```bash
python market-calendar.py --add "2026-02-09" "Super Bowl LX" "sports"
python market-calendar.py --add "2026-02-20" "Fed Meeting" "politics"
python market-calendar.py --add "2026-03-15" "March Madness Finals" "sports"
```

### 3. Set Up Daily Alerts (Cron)
```bash
# Check alerts daily at 9 AM
0 9 * * * cd /path/to/workspace && python market-calendar.py --alerts
```

### 4. Weekly Pattern Analysis
```bash
# Analyze patterns every Monday
0 10 * * 1 cd /path/to/workspace && python market-calendar.py --patterns
```

## 🎉 Great Success!

Your market calendar is ready! Key features:

✅ Track market resolutions automatically
✅ Add custom events (elections, sports, earnings)
✅ Alert system (24h, 48h, 7 days before events)
✅ Pattern analysis (best days/hours to trade)
✅ Position risk management (expiring markets)
✅ Beautiful ASCII calendar views
✅ Python API for integration
✅ CLI interface for quick checks
✅ SQLite storage (integrated with existing database)
✅ Recurring event support

Next steps:
1. Sync your markets: `python market-calendar.py --sync`
2. Add key events for your trading strategy
3. Set up daily alert checks
4. Integrate with your trading bot
5. Use pattern analysis to optimize entry/exit timing
