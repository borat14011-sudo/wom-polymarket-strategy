# System Architecture

Visual overview of the Polymarket Monitor system.

## 🏗️ Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     POLYMARKET MONITOR SYSTEM                   │
│                     (monitor_daemon.py)                         │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ Every 60 minutes
             │
             ▼
    ┌────────────────────────────────────────┐
    │  MONITORING CYCLE                      │
    │                                        │
    │  1. Scrape  →  2. Calculate  →  3. Alert│
    └────┬────────────────┬─────────────┬────┘
         │                │             │
         ▼                ▼             ▼
┌────────────────┐ ┌──────────────┐ ┌─────────────────┐
│  SCRAPER       │ │  CALCULATOR  │ │   ALERTER       │
│                │ │              │ │                 │
│ Polymarket API │ │ RVR & ROC    │ │ Telegram via    │
│ ↓              │ │ Analysis     │ │ OpenClaw        │
│ Market Data    │ │ ↓            │ │ ↓               │
│ ↓              │ │ Signals      │ │ Notifications   │
└────────┬───────┘ └──────┬───────┘ └────────┬────────┘
         │                │                  │
         │                │                  │
         └────────────────┼──────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   DATABASE    │
                  │   (SQLite)    │
                  │               │
                  │ • market_     │
                  │   snapshots   │
                  │ • signals     │
                  └───────────────┘
```

## 🔄 Data Flow

### Phase 1: Data Collection (Scraper)
```
Polymarket API
    ↓
[GET /markets?limit=50&order=volume24hr]
    ↓
JSON Response
    ↓
Parse: {market_id, name, price, volume, liquidity}
    ↓
INSERT INTO market_snapshots
    ↓
Database Updated
```

### Phase 2: Signal Detection (Calculator)
```
Database Query
    ↓
SELECT last 24h of data per market
    ↓
For each market:
    ├─ Calculate RVR = current_vol / avg_24h_vol
    ├─ Calculate ROC = (current_price - price_12h) / price_12h * 100
    └─ If RVR > 2.5 AND |ROC| > 8%
        ↓
        NEW SIGNAL FOUND
        ↓
        INSERT INTO signals
```

### Phase 3: Alert Delivery (Alerter)
```
SELECT * FROM signals WHERE alerted = 0
    ↓
For each signal:
    ├─ Format message
    ├─ openclaw message send --channel telegram --target @user
    └─ UPDATE signals SET alerted = 1
```

## 📊 Database Schema

```sql
┌─────────────────────────────────────────┐
│         market_snapshots                │
├─────────────────────────────────────────┤
│ id          INTEGER PK                  │
│ market_id   TEXT                        │
│ name        TEXT                        │
│ price       REAL        [0.0 - 1.0]     │
│ volume      REAL        [USD]           │
│ liquidity   REAL        [USD]           │
│ timestamp   INTEGER     [Unix epoch]    │
└─────────────────────────────────────────┘
             │
             │ One-to-Many
             ▼
┌─────────────────────────────────────────┐
│            signals                      │
├─────────────────────────────────────────┤
│ id          INTEGER PK                  │
│ market_id   TEXT        FK → markets    │
│ market_name TEXT                        │
│ rvr         REAL        [ratio]         │
│ roc         REAL        [percent]       │
│ price       REAL        [0.0 - 1.0]     │
│ volume      REAL        [USD]           │
│ timestamp   INTEGER     [Unix epoch]    │
│ alerted     INTEGER     [0 or 1]        │
└─────────────────────────────────────────┘
```

## ⚙️ Configuration System

```
config.py (user editable)
    ↓
    ├─→ monitor_daemon.py (schedules, logging)
    ├─→ polymarket_scraper.py (API settings)
    ├─→ rvr_calculator.py (thresholds)
    └─→ telegram_alerter.py (target user)

All components have fallback defaults if config.py missing
```

## 🔁 Scheduling System

```
monitor_daemon.py starts
    ↓
schedule.every(60).minutes.do(monitoring_cycle)
    ↓
    ┌─────────────────────────────────┐
    │  Loop every 60 seconds:         │
    │    schedule.run_pending()       │
    │    sleep(60)                    │
    └─────────────────────────────────┘
                  │
                  │ When 60 min elapsed
                  ▼
            monitoring_cycle()
                  │
                  ├─→ scrape_and_store()
                  ├─→ calculate_signals()
                  └─→ send_alerts()
```

## 🧹 Cleanup System

```
schedule.every().day.at("03:00").do(daily_cleanup)
    ↓
At 3:00 AM daily:
    ↓
DELETE FROM market_snapshots WHERE timestamp < (now - 7 days)
DELETE FROM signals WHERE timestamp < (now - 7 days)
    ↓
Keep database under 50 MB
```

## 🔐 External Dependencies

```
┌──────────────────────────────────────────────────┐
│  EXTERNAL SERVICES                               │
├──────────────────────────────────────────────────┤
│                                                  │
│  Polymarket Gamma API                            │
│  https://gamma-api.polymarket.com                │
│  ├─ Public, no auth required                     │
│  ├─ Rate limited (respectful scraping)           │
│  └─ Returns JSON market data                     │
│                                                  │
│  OpenClaw Message Tool                           │
│  openclaw message send ...                       │
│  ├─ Requires OpenClaw CLI installed              │
│  ├─ Requires Telegram configured                 │
│  └─ Sends via user's Telegram account            │
│                                                  │
└──────────────────────────────────────────────────┘
```

## 📦 Python Dependencies

```
┌─────────────────────────────────────────┐
│  Standard Library (built-in)            │
├─────────────────────────────────────────┤
│  • sqlite3      (database)              │
│  • logging      (logs)                  │
│  • datetime     (timestamps)            │
│  • subprocess   (openclaw calls)        │
│  • time         (delays)                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  External (pip install)                 │
├─────────────────────────────────────────┤
│  • requests     (HTTP API calls)        │
│  • schedule     (cron-like scheduling)  │
└─────────────────────────────────────────┘
```

## 🚦 Signal Detection Algorithm

```
Input: Market M with historical data H

1. Get current snapshot:
   current = latest(H)
   
2. Calculate RVR:
   historical_volumes = [h.volume for h in H[:-1]]
   avg_volume = mean(historical_volumes)
   rvr = current.volume / avg_volume

3. Calculate ROC:
   price_12h_ago = H[timestamp ≈ now - 12h].price
   roc = (current.price - price_12h_ago) / price_12h_ago * 100

4. Check criteria:
   IF rvr >= 2.5 AND abs(roc) >= 8.0:
       SIGNAL DETECTED
       └─→ Insert into signals table
   ELSE:
       No signal

5. Anti-spam check:
   IF signal exists for M in last 6 hours:
       Skip (don't spam repeats)
```

## 📱 Alert Format

```
Input: Signal S

Format:
┌──────────────────────────────────────────┐
│ 🚨 POLYMARKET SIGNAL                     │
│                                          │
│ 📊 Market: {S.market_name}               │
│                                          │
│ 📈 RVR: {S.rvr:.2f}x                     │
│ 📉 ROC: {S.roc:+.1f}%                    │
│ 💰 Price: {S.price * 100:.1f}%           │
│ 💵 Volume: ${S.volume formatted}         │
│                                          │
│ ⏰ {S.timestamp formatted}                │
└──────────────────────────────────────────┘

Example:
┌──────────────────────────────────────────┐
│ 🚨 POLYMARKET SIGNAL                     │
│                                          │
│ 📊 Market: Will Bitcoin hit $100k?       │
│                                          │
│ 📈 RVR: 3.45x                            │
│ 📉 ROC: +12.3%                           │
│ 💰 Price: 67.5%                          │
│ 💵 Volume: $2.4M                         │
│                                          │
│ ⏰ 2026-02-06 14:30:15                   │
└──────────────────────────────────────────┘

Sent via:
openclaw message send \
  --channel telegram \
  --target @MoneyManAmex \
  --message <formatted above>
```

## 🛡️ Error Handling

```
Every function wrapped in try/except:

┌────────────────────────────────────────┐
│  Component Error Isolation             │
├────────────────────────────────────────┤
│                                        │
│  Scraper fails?                        │
│  └─→ Log error, continue to next cycle │
│      (use old data for calculation)    │
│                                        │
│  Calculator fails?                     │
│  └─→ Log error, skip alerting          │
│      (try again next cycle)            │
│                                        │
│  Alerter fails?                        │
│  └─→ Log error, mark as unalerted      │
│      (retry next cycle)                │
│                                        │
│  Database fails?                       │
│  └─→ Log error, abort cycle            │
│      (critical, needs investigation)   │
│                                        │
└────────────────────────────────────────┘

Daemon never crashes - logs errors and continues
```

## 📈 Performance Characteristics

```
┌─────────────────────────────────────────────┐
│  Resource Usage                             │
├─────────────────────────────────────────────┤
│  CPU:     < 1% average (spikes during calc) │
│  Memory:  50-100 MB                         │
│  Disk:    1-2 MB/day (auto-cleanup)         │
│  Network: 1-5 MB/hour (API requests)        │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Timing                                     │
├─────────────────────────────────────────────┤
│  Cycle duration:  5-15 seconds              │
│  ├─ Scrape:       2-5 seconds               │
│  ├─ Calculate:    1-3 seconds               │
│  └─ Alert:        1-5 seconds               │
│                                             │
│  Idle time:       59m 45s per hour          │
│  Active time:     15s per hour              │
│  Efficiency:      99.6% idle               │
└─────────────────────────────────────────────┘
```

## 🔄 State Management

```
System is STATELESS except for database:

┌──────────────────────────────────────────┐
│  No in-memory state carried between      │
│  cycles - all state in SQLite DB         │
│                                          │
│  Benefits:                               │
│  ✓ Restart safe                          │
│  ✓ Crash safe                            │
│  ✓ Can query externally                  │
│  ✓ Easy to debug                         │
│  ✓ No memory leaks                       │
└──────────────────────────────────────────┘
```

---

**Architecture principles:**
- **Modularity**: Each component is independent
- **Fault tolerance**: Errors don't crash the system
- **Statelessness**: All state in database
- **Simplicity**: No complex dependencies
- **Observability**: Extensive logging
