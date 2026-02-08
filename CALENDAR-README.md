# 🗓️ Market Event Calendar - Polymarket Trading System

Complete event tracking and calendar management for Polymarket trading. Track market resolutions, key events, trading patterns, and position risks.

## 🚀 Quick Start

```bash
# Initialize (sync market resolutions)
python market-calendar.py --sync

# View today's events
python market-calendar.py

# View this week
python market-calendar.py --week

# Check expiring markets (7 days)
python market-calendar.py --expiring 7

# Analyze trading patterns
python market-calendar.py --patterns
```

## 📋 Features

### 1. **Event Tracking**
- ✅ Market resolution dates (auto-synced from database)
- ✅ Key dates (elections, sports, earnings, conferences)
- ✅ Custom events (manual entries)
- ✅ Recurring events (weekly, monthly reviews)

### 2. **Alert System**
- ⏰ Multi-level alerts (24h, 48h, 7 days before events)
- 🔔 Pending alert tracking
- 📱 Integration-ready (Telegram, email, etc.)
- ✅ Alert triggering/acknowledgment

### 3. **Calendar Views**
- 📅 Today's events
- 📆 This week's events
- 🗓️ Upcoming events (30 days)
- 📊 Mini calendar with event markers
- ⚠️ Expiring markets with risk levels

### 4. **Position Management**
- 🎯 List positions expiring soon
- 🚨 Risk alerts (critical, high, medium, low)
- 💡 Suggested exit strategies
- ⏱️ Days-to-resolution tracking

### 5. **Pattern Analysis**
- 📈 Best days to trade (by volume)
- 🕐 Best hours to trade (by volume)
- 🏁 Pre-resolution behavior patterns
- 📊 Volume and spread analysis
- 🔍 Historical pattern learning

### 6. **Integration**
- 🐍 Python API for programmatic use
- 🗄️ SQLite integration (existing database)
- 🤖 Bot-friendly (trading automation)
- 📡 Alert webhook support

## 📚 Usage Examples

### CLI Commands

```bash
# Today's events
python market-calendar.py

# This week's events
python market-calendar.py --week

# Upcoming events (30 days)
python market-calendar.py --upcoming

# Add custom event
python market-calendar.py --add "2026-02-15" "Super Bowl" "sports"

# Markets expiring in 7 days
python market-calendar.py --expiring 7

# Trading pattern analysis
python market-calendar.py --patterns

# Sync market resolutions
python market-calendar.py --sync

# View pending alerts
python market-calendar.py --alerts

# Week view with mini calendar
python market-calendar.py --week --mini
```

### Python API

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

# Get this week's events
events = calendar.get_week()

# Get upcoming events (30 days)
events = calendar.get_upcoming(days=30)

# Get expiring markets
expiring = calendar.get_expiring_markets(days=7)

# Analyze patterns
patterns = calendar.analyze_patterns()

# Sync market resolutions
synced = calendar.sync_market_resolutions()

# Get pending alerts
alerts = calendar.get_pending_alerts()

# Mark alert as triggered
calendar.mark_alert_triggered(alert_id)
```

## 🎯 Integration Examples

### 1. Pre-Trade Risk Check

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
    
    return True, "✅ OK to trade"
```

### 2. Daily Alert System

```python
def daily_alert_check():
    """Run as cron job"""
    calendar = MarketCalendar()
    alerts = calendar.get_pending_alerts()
    
    for alert in alerts:
        send_telegram(f"🔔 {alert['message']}")
        calendar.mark_alert_triggered(alert['id'])
```

### 3. Pattern-Based Trading

```python
def should_trade_now():
    calendar = MarketCalendar()
    patterns = calendar.analyze_patterns()
    
    # Get current time patterns
    now = datetime.now()
    hour_data = patterns['hour_of_day'][now.hour]
    
    # Check if high-volume period
    avg_volume = sum(p['avg_volume'] for p in patterns['hour_of_day']) / 24
    
    if hour_data['avg_volume'] > avg_volume * 1.2:
        return True, "🟢 HIGH activity - great time to trade!"
    else:
        return False, "🔴 LOW activity - consider waiting"
```

### 4. Pre-Resolution Exit Strategy

```python
def check_exit_strategy(market_id):
    calendar = MarketCalendar()
    expiring = calendar.get_expiring_markets(days=30)
    
    market = next((m for m in expiring if m['market_id'] == market_id), None)
    
    if not market:
        return "Market not found"
    
    days_left = market['days_left']
    
    if days_left < 1:
        return "🔴 CRITICAL: Exit NOW!"
    elif days_left < 3:
        return "🟠 HIGH: Consider exiting soon"
    elif days_left < 7:
        return "🟡 MEDIUM: Monitor closely"
    else:
        return "🟢 LOW: No immediate concerns"
```

## 📊 Database Schema

The calendar integrates with your existing `polymarket_data.db` and adds these tables:

### `calendar_events`
Stores all events (manual and auto-synced)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| event_date | TEXT | Event date (ISO format) |
| event_name | TEXT | Event name |
| category | TEXT | Category (sports, politics, crypto, etc.) |
| description | TEXT | Event description |
| market_id | TEXT | Associated market (if any) |
| event_type | TEXT | Type (manual, resolution, recurring) |
| alert_hours | INTEGER | Alert lead time |
| recurring | TEXT | Recurrence pattern |
| created_at | TIMESTAMP | Created timestamp |

### `event_alerts`
Tracks alert triggers

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| event_id | INTEGER | Event reference |
| alert_time | TIMESTAMP | When to trigger |
| triggered | INTEGER | Has triggered (0/1) |
| message | TEXT | Alert message |

### `trading_patterns`
Stores pattern analysis results

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| pattern_type | TEXT | Pattern type |
| day_of_week | INTEGER | Day (0-6) |
| hour_of_day | INTEGER | Hour (0-23) |
| market_category | TEXT | Market category |
| avg_volume | REAL | Average volume |
| avg_price_change | REAL | Average price change |
| avg_spread | REAL | Average spread |
| sample_count | INTEGER | Sample size |
| confidence_score | REAL | Confidence level |
| last_updated | TIMESTAMP | Last update |

### `position_risks`
Position risk tracking

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| market_id | TEXT | Market reference |
| position_size | REAL | Position size |
| entry_price | REAL | Entry price |
| current_price | REAL | Current price |
| days_to_resolution | INTEGER | Days left |
| risk_level | TEXT | Risk level |
| suggested_action | TEXT | Suggested action |
| updated_at | TIMESTAMP | Last update |

## 🔧 Configuration

### Database Path
Default: `polymarket_data.db` in current directory

```python
calendar = MarketCalendar(db_path="/custom/path/data.db")
```

### Alert Hours
Default: [24, 48, 168] (1 day, 2 days, 7 days)

Modify in `market-calendar.py`:
```python
ALERT_HOURS = [24, 48, 168]  # Your custom hours
```

### Categories
Common categories:
- `sports` - Sports events (Super Bowl, March Madness, etc.)
- `politics` - Political events (elections, Fed meetings, etc.)
- `crypto` - Crypto events (conferences, launches, etc.)
- `business` - Business events (earnings, product launches, etc.)
- `general` - General events

## 🤖 Automation

### Cron Job Examples

```bash
# Check alerts daily at 9 AM
0 9 * * * cd /path/to/workspace && python market-calendar.py --alerts

# Sync market resolutions every 6 hours
0 */6 * * * cd /path/to/workspace && python market-calendar.py --sync

# Weekly pattern analysis (Monday 10 AM)
0 10 * * 1 cd /path/to/workspace && python market-calendar.py --patterns

# Daily summary (8 AM)
0 8 * * * cd /path/to/workspace && python market-calendar.py --week
```

### Integration with Trading Bot

```python
# In your trading bot main loop
def trading_loop():
    calendar = MarketCalendar()
    
    while True:
        # Check alerts
        alerts = calendar.get_pending_alerts()
        for alert in alerts:
            handle_alert(alert)
        
        # Check expiring positions
        expiring = calendar.get_expiring_markets(days=3)
        for market in expiring:
            if market['days_left'] < 1:
                exit_position(market['market_id'])
        
        # Sync resolutions
        calendar.sync_market_resolutions()
        
        # Your trading logic here
        execute_trades()
        
        time.sleep(3600)  # Run every hour
```

## 📈 Pattern Analysis Insights

The pattern analyzer provides:

1. **Day-of-Week Patterns**
   - Which days have highest volume
   - Which days have tightest spreads
   - Sample size for confidence

2. **Hour-of-Day Patterns**
   - Peak trading hours
   - Volume distribution throughout day
   - Spread variations by time

3. **Pre-Resolution Behavior**
   - Typical volume changes
   - Spread widening patterns
   - Price deviation from 50%
   - Market count for statistical significance

Use this data to:
- Optimize trade entry timing
- Avoid low-liquidity periods
- Plan exits before resolution volatility
- Understand market dynamics

## 🎨 Output Examples

See `CALENDAR-EXAMPLE-OUTPUT.md` for detailed output examples including:
- Today's events view
- Weekly calendar
- Expiring markets with risk levels
- Pattern analysis reports
- Alert notifications
- Mini calendar view

## 🛠️ Troubleshooting

### No markets syncing?
```bash
# Check if markets table has data
python -c "import sqlite3; conn = sqlite3.connect('polymarket_data.db'); print(len(conn.execute('SELECT * FROM markets').fetchall()))"

# Run data collector first
python polymarket-data-collector.py
```

### Alerts not triggering?
```bash
# Check alert table
python market-calendar.py --alerts

# Verify event dates are in future
python market-calendar.py --upcoming
```

### Pattern analysis empty?
```bash
# Need historical data first
# Run data collector for several days
python polymarket-data-collector.py
```

## 📝 Notes

- **Auto-sync**: Run `--sync` periodically to update market resolutions
- **Recurring events**: Not fully implemented yet (placeholder)
- **Alert delivery**: Alerts tracked in DB, delivery integration needed
- **Position risks**: Manual position tracking recommended
- **Pattern confidence**: Requires 7+ days of data for reliability

## 🎉 Great Success!

Your market calendar is ready to use! Start with:

```bash
python market-calendar.py --sync
python market-calendar.py --week
python market-calendar.py --expiring 7
```

For questions or issues, check the example files:
- `example-calendar-usage.py` - Demos and examples
- `CALENDAR-EXAMPLE-OUTPUT.md` - Sample outputs

Happy trading! 📈
