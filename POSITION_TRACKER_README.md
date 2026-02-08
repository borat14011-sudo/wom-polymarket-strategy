# Position Tracker - Polymarket Trading System

Real-time position tracking module for Polymarket trading with P&L monitoring, alerts, and historical analysis.

## Features

✅ **Position Management**
- Track open positions with real-time P&L
- Market ID, entry/current prices, position size
- Time in position tracking
- Stop loss and take profit levels

✅ **Portfolio Analytics**
- Total portfolio value and cash balance
- Unrealized and realized P&L
- Exposure breakdown by sector
- Performance metrics

✅ **Alert System**
- Stop loss warnings
- Take profit notifications
- Unusual P&L swing detection (±20%)

✅ **Historical Tracking**
- Portfolio snapshots for analysis
- Position history with timestamps
- P&L attribution over time

✅ **Dual Interface**
- CLI for quick operations
- Python API for programmatic use

## Installation

No dependencies required - uses Python standard library only!

```bash
# Just make sure you're using Python 3.7+
python --version
```

## Quick Start

### CLI Usage

```bash
# List all positions
python position-tracker.py

# Open a new position
python position-tracker.py --add MARKET_ID 0.52 1000 --stop-loss 0.40 --take-profit 0.75 --sector Crypto

# Close a position
python position-tracker.py --close 1 0.58

# Update price for a position
python position-tracker.py --update-price 1 0.60

# Portfolio summary
python position-tracker.py --summary

# P&L breakdown
python position-tracker.py --pnl

# Historical snapshots
python position-tracker.py --history --history-days 7

# Check alerts
python position-tracker.py --alerts

# Create snapshot
python position-tracker.py --snapshot

# Custom database
python position-tracker.py --db my_portfolio.db --bankroll 50000
```

### Programmatic Usage

```python
from position_tracker import PositionTracker

# Initialize tracker
tracker = PositionTracker(db_path="positions.db", bankroll=10000.0)

# Open a position
position_id = tracker.open_position(
    market_id="will-bitcoin-hit-100k-2024",
    entry_price=0.52,
    size=1000,
    stop_loss=0.40,
    take_profit=0.75,
    sector="Crypto"
)

# Update price manually
tracker.update_price(position_id, 0.58)

# Or update multiple positions at once
price_map = {
    "will-bitcoin-hit-100k-2024": 0.58,
    "trump-wins-2024": 0.45,
    "ai-breakthrough-2024": 0.72
}
tracker.update_prices(price_map)

# Get all positions
positions = tracker.get_all_positions()
for pos in positions:
    print(f"{pos.market_id}: ${pos.unrealized_pnl:+.2f}")

# Get portfolio summary
summary = tracker.get_summary()
print(f"Total Value: ${summary['total_value']:,.2f}")
print(f"Total P&L: ${summary['total_pnl']:+.2f}")

# Check for alerts
alerts = tracker.check_alerts()
for alert in alerts:
    if alert['severity'] == 'HIGH':
        print(f"🚨 {alert['message']}")

# Close a position
realized_pnl = tracker.close_position(position_id, exit_price=0.58)
print(f"Realized P&L: ${realized_pnl:+.2f}")

# Create snapshot for historical tracking
snapshot_id = tracker.create_snapshot()

# Get historical data
history = tracker.get_history(days=7)
for snapshot in history:
    print(f"{snapshot['timestamp']}: ${snapshot['total_value']:,.2f}")

# P&L breakdown
breakdown = tracker.get_pnl_breakdown()
print(f"Unrealized: ${breakdown['unrealized_total']:+.2f}")
print(f"Realized: ${breakdown['realized_total']:+.2f}")

# Don't forget to close
tracker.close()
```

## Demo

Run the demo script to see it in action:

```bash
python position-tracker-demo.py
```

This will:
1. Create a demo portfolio with $10,000
2. Open 3 positions in different sectors
3. Simulate price changes
4. Check alerts
5. Show portfolio summary
6. Create a snapshot
7. Close a position
8. Display final P&L breakdown

## Database Schema

### `positions` table
- `position_id`: Unique ID (auto-increment)
- `market_id`: Market identifier
- `entry_price`: Entry price per share
- `current_price`: Current price per share
- `size`: Number of shares
- `entry_time`: When position was opened (ISO format)
- `last_update`: Last price update time
- `stop_loss`: Optional stop loss price
- `take_profit`: Optional take profit price
- `sector`: Optional sector/category

### `closed_positions` table
- `position_id`: Position ID (from positions table)
- `market_id`: Market identifier
- `entry_price`: Entry price
- `exit_price`: Exit price
- `size`: Number of shares
- `entry_time`: When opened
- `exit_time`: When closed
- `realized_pnl`: Realized profit/loss
- `sector`: Optional sector

### `snapshots` table
- `snapshot_id`: Unique ID
- `timestamp`: Snapshot time
- `total_value`: Total portfolio value
- `unrealized_pnl`: Unrealized P&L
- `realized_pnl`: Realized P&L
- `cash_balance`: Cash balance
- `position_count`: Number of open positions
- `snapshot_data`: JSON with full portfolio state

### `cash_balance` table
- `id`: Always 1 (singleton)
- `balance`: Current cash balance
- `last_update`: Last update time

## Position Object

```python
@dataclass
class Position:
    position_id: int
    market_id: str
    entry_price: float
    current_price: float
    size: float
    entry_time: str
    last_update: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    sector: Optional[str] = None
    
    # Computed properties
    unrealized_pnl: float          # (current_price - entry_price) * size
    unrealized_pnl_pct: float      # P&L as percentage
    position_value: float          # current_price * size
    time_in_position: timedelta    # How long position has been open
```

## Alert Types

1. **STOP_LOSS** (HIGH severity)
   - Triggered when current price ≤ stop loss price
   - Immediate action recommended

2. **APPROACHING_STOP_LOSS** (MEDIUM severity)
   - Triggered when current price ≤ stop loss * 1.05
   - Warning to monitor position

3. **TAKE_PROFIT** (HIGH severity)
   - Triggered when current price ≥ take profit price
   - Consider closing position to lock in gains

4. **UNUSUAL_PNL_SWING** (HIGH/MEDIUM severity)
   - Triggered when unrealized P&L > ±20%
   - HIGH if loss > 20%, MEDIUM if gain > 20%

## Example Workflows

### Daily Trading Workflow

```python
# Morning: Initialize tracker
tracker = PositionTracker()

# Check overnight changes
tracker.update_prices(get_latest_prices())  # Your price fetching function
alerts = tracker.check_alerts()
summary = tracker.get_summary()

# Open new positions based on analysis
tracker.open_position("new-market-id", 0.45, 500, stop_loss=0.35, take_profit=0.65)

# Create morning snapshot
tracker.create_snapshot()

# Throughout the day: Monitor positions
tracker.update_prices(get_latest_prices())
breakdown = tracker.get_pnl_breakdown()

# Close profitable positions
for alert in tracker.check_alerts():
    if alert['type'] == 'TAKE_PROFIT':
        tracker.close_position(alert['position_id'], alert['current_price'])

# Evening: End of day snapshot
tracker.create_snapshot()
tracker.close()
```

### Risk Management

```python
# Check positions approaching stop loss
alerts = tracker.check_alerts()
for alert in alerts:
    if alert['type'] == 'APPROACHING_STOP_LOSS':
        pos = tracker.get_position(alert['position_id'])
        # Decide: tighten stop, close early, or hold
        
# Monitor sector exposure
summary = tracker.get_summary()
for sector, exposure in summary['exposure_by_sector'].items():
    exposure_pct = (exposure / summary['total_value']) * 100
    if exposure_pct > 30:  # More than 30% in one sector
        print(f"⚠️ High exposure to {sector}: {exposure_pct:.1f}%")
```

### Performance Analysis

```python
# Weekly review
history = tracker.get_history(days=7)
if len(history) >= 2:
    start = history[-1]
    end = history[0]
    
    value_change = end['total_value'] - start['total_value']
    value_change_pct = (value_change / start['total_value']) * 100
    
    print(f"Week Performance: ${value_change:+.2f} ({value_change_pct:+.2f}%)")

# Best/worst positions
breakdown = tracker.get_pnl_breakdown()
open_positions = sorted(breakdown['open_positions'], 
                       key=lambda x: x['unrealized_pnl_pct'], 
                       reverse=True)

print("Top 3 Performers:")
for p in open_positions[:3]:
    print(f"  {p['market_id']}: {p['unrealized_pnl_pct']:+.2f}%")

print("Bottom 3 Performers:")
for p in open_positions[-3:]:
    print(f"  {p['market_id']}: {p['unrealized_pnl_pct']:+.2f}%")
```

## Integration with Polymarket API

To integrate with real Polymarket data, add a price update function:

```python
import requests

def fetch_polymarket_prices(market_ids):
    """Fetch current prices from Polymarket API"""
    # Example - adjust based on actual Polymarket API
    price_map = {}
    for market_id in market_ids:
        response = requests.get(f"https://api.polymarket.com/markets/{market_id}")
        data = response.json()
        price_map[market_id] = data['current_price']
    return price_map

# Use in tracker
positions = tracker.get_all_positions()
market_ids = [p.market_id for p in positions]
prices = fetch_polymarket_prices(market_ids)
tracker.update_prices(prices)
```

## Tips & Best Practices

1. **Regular Snapshots**: Create snapshots at consistent intervals (e.g., daily) for trend analysis
2. **Alert Monitoring**: Check alerts before making new trades
3. **Sector Diversification**: Monitor `exposure_by_sector` to avoid over-concentration
4. **Risk Management**: Always set stop losses when opening positions
5. **P&L Attribution**: Review closed positions to learn from wins and losses
6. **Cash Management**: Keep sufficient cash balance for new opportunities
7. **Database Backups**: Regularly backup your positions database

## Troubleshooting

**"Insufficient funds" error when opening position:**
- Check cash balance: `tracker.get_cash_balance()`
- Close some positions or reduce position size

**Positions not showing current prices:**
- Prices don't auto-update - call `tracker.update_prices()` or `tracker.update_price()`
- Integrate with Polymarket API for real-time updates

**Database locked error:**
- Make sure only one instance is accessing the database
- Call `tracker.close()` when done

## Advanced Features

### Custom Alert Logic

Extend the `check_alerts()` method for custom conditions:

```python
# Example: Alert on positions held too long
def check_time_alerts(tracker):
    positions = tracker.get_all_positions()
    alerts = []
    for p in positions:
        if p.time_in_position > timedelta(days=30):
            alerts.append({
                'type': 'POSITION_AGING',
                'message': f"Position {p.position_id} held for {p.time_in_position.days} days"
            })
    return alerts
```

### Batch Operations

```python
# Close all positions in a sector
positions = tracker.get_all_positions()
for p in positions:
    if p.sector == "Politics":
        tracker.close_position(p.position_id, p.current_price)

# Close all losing positions
for p in positions:
    if p.unrealized_pnl < 0:
        tracker.close_position(p.position_id, p.current_price)
```

## License

MIT - Use however you want!

## Support

For issues or questions, check:
- Database schema in this README
- Demo script: `position-tracker-demo.py`
- Code comments in `position-tracker.py`

---

**Great success!** 🎉

Built for serious Polymarket traders who want real-time position tracking and risk management.
