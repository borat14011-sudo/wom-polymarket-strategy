# 🔌 Integrating the CLI with Real Trading System

This guide shows how to connect `trading-cli.py` to your actual Polymarket trading system.

---

## 🎯 Overview

The CLI is currently using **mock data** from these functions:
- `get_system_status()` - System health and uptime
- `get_active_signals()` - Trading signals
- `get_portfolio()` - Portfolio and positions
- `get_recent_trades()` - Trade history
- `get_performance_data()` - Performance metrics

**To go live:** Replace these functions with real data sources.

---

## 📊 Integration Points

### 1. System Status

**Current (Mock):**
```python
def get_system_status() -> Dict:
    return {
        'running': True,
        'uptime': 3600 * 12,
        'components': {
            'Data Collector': 'healthy',
            'Signal Generator': 'healthy',
            ...
        },
        'last_update': datetime.now()
    }
```

**Real Integration:**
```python
def get_system_status() -> Dict:
    """Get real system status from your trading system"""
    # Option 1: API call
    response = requests.get('http://localhost:8000/api/status')
    return response.json()
    
    # Option 2: Check running processes
    import psutil
    processes = {
        'Data Collector': check_process('data_collector'),
        'Signal Generator': check_process('signal_gen'),
        ...
    }
    
    # Option 3: Read from shared state file
    with open('system_state.json', 'r') as f:
        return json.load(f)
```

---

### 2. Active Signals

**Current (Mock):**
```python
def get_active_signals() -> List[Dict]:
    return [
        {
            'market': 'Trump wins 2024',
            'signal': 'BUY',
            'confidence': 0.82,
            'price': 0.45,
            'target': 0.55,
            'trend': 'up',
            'volume_surge': 245
        },
        ...
    ]
```

**Real Integration:**
```python
def get_active_signals() -> List[Dict]:
    """Get real signals from your signal generator"""
    # Option 1: Database query
    import sqlite3
    conn = sqlite3.connect('trading.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT market, signal, confidence, price, target, trend, volume_surge
        FROM signals
        WHERE active = 1
        ORDER BY confidence DESC
    ''')
    rows = cursor.fetchall()
    return [dict(zip(['market', 'signal', 'confidence', ...], row)) for row in rows]
    
    # Option 2: API call
    response = requests.get('http://localhost:8000/api/signals')
    return response.json()['signals']
    
    # Option 3: Read from signal file
    with open('signals.json', 'r') as f:
        data = json.load(f)
        return [s for s in data if s['active']]
```

---

### 3. Portfolio

**Current (Mock):**
```python
def get_portfolio() -> Dict:
    return {
        'balance': 10000.00,
        'positions': [...],
        'total_pnl': -300,
        'day_pnl': 150,
        'win_rate': 0.58
    }
```

**Real Integration:**
```python
def get_portfolio() -> Dict:
    """Get real portfolio from Polymarket or your system"""
    # Option 1: Polymarket API
    from polymarket_api import Client
    client = Client(api_key=os.getenv('POLYMARKET_API_KEY'))
    
    balance = client.get_balance()
    positions = client.get_positions()
    
    # Calculate P&L
    total_pnl = sum(p['unrealized_pnl'] for p in positions)
    
    return {
        'balance': balance,
        'positions': positions,
        'total_pnl': total_pnl,
        ...
    }
    
    # Option 2: Your own tracking database
    conn = sqlite3.connect('trading.db')
    cursor = conn.cursor()
    
    # Get balance
    cursor.execute('SELECT balance FROM account WHERE id = 1')
    balance = cursor.fetchone()[0]
    
    # Get positions
    cursor.execute('''
        SELECT market, shares, avg_price, current_price, 
               (current_price - avg_price) * shares as pnl
        FROM positions
        WHERE shares > 0
    ''')
    positions = [dict(zip(['market', 'shares', ...], row)) for row in cursor.fetchall()]
    
    return {
        'balance': balance,
        'positions': positions,
        ...
    }
```

---

### 4. Recent Trades

**Current (Mock):**
```python
def get_recent_trades() -> List[Dict]:
    base_time = datetime.now()
    return [
        {
            'time': base_time - timedelta(minutes=5),
            'market': 'Trump wins 2024',
            'action': 'BUY',
            ...
        },
        ...
    ]
```

**Real Integration:**
```python
def get_recent_trades() -> List[Dict]:
    """Get real trade history"""
    # Database query
    conn = sqlite3.connect('trading.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, market, action, shares, price, pnl
        FROM trades
        ORDER BY timestamp DESC
        LIMIT 20
    ''')
    
    trades = []
    for row in cursor.fetchall():
        trades.append({
            'time': datetime.fromisoformat(row[0]),
            'market': row[1],
            'action': row[2],
            'shares': row[3],
            'price': row[4],
            'pnl': row[5]
        })
    
    return trades
```

---

### 5. Performance Data

**Current (Mock):**
```python
def get_performance_data() -> Dict:
    import random
    prices = [10000]
    for _ in range(100):
        prices.append(prices[-1] + random.uniform(-200, 250))
    
    return {
        'prices': prices,
        'total_return': (prices[-1] - prices[0]) / prices[0],
        ...
    }
```

**Real Integration:**
```python
def get_performance_data() -> Dict:
    """Get real performance metrics"""
    # Get historical portfolio values
    conn = sqlite3.connect('trading.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, portfolio_value
        FROM portfolio_history
        ORDER BY timestamp ASC
    ''')
    
    data = cursor.fetchall()
    prices = [row[1] for row in data]
    
    # Calculate metrics
    total_return = (prices[-1] - prices[0]) / prices[0]
    
    # Calculate Sharpe ratio
    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
    avg_return = sum(returns) / len(returns)
    std_return = (sum((r - avg_return)**2 for r in returns) / len(returns)) ** 0.5
    sharpe_ratio = avg_return / std_return if std_return > 0 else 0
    
    # Max drawdown
    peak = prices[0]
    max_dd = 0
    for price in prices:
        if price > peak:
            peak = price
        dd = (peak - price) / peak
        if dd > max_dd:
            max_dd = dd
    
    return {
        'prices': prices,
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': -max_dd,
        ...
    }
```

---

## 🏗️ Architecture Options

### Option 1: Direct Database Access
**Best for:** Standalone CLI accessing same database as trading system

```python
# trading-cli.py
import sqlite3

def get_data():
    conn = sqlite3.connect('/path/to/trading.db')
    # ... queries ...
    return data
```

**Pros:** Simple, fast, no network overhead  
**Cons:** Tight coupling, concurrent access issues

---

### Option 2: REST API
**Best for:** Distributed system, multiple clients

```python
# trading-cli.py
import requests

API_BASE = 'http://localhost:8000/api'

def get_system_status():
    response = requests.get(f'{API_BASE}/status')
    return response.json()
```

**Pros:** Clean separation, scalable, secure  
**Cons:** Network overhead, API maintenance

---

### Option 3: Shared Files (JSON/CSV)
**Best for:** Simple setups, file-based workflows

```python
# trading-cli.py
import json

def get_portfolio():
    with open('data/portfolio.json', 'r') as f:
        return json.load(f)
```

**Pros:** Simple, no dependencies  
**Cons:** File locking, not real-time

---

### Option 4: Message Queue (Redis/RabbitMQ)
**Best for:** Real-time updates, pub/sub patterns

```python
# trading-cli.py
import redis

r = redis.Redis(host='localhost', port=6379)

def get_active_signals():
    signals_json = r.get('active_signals')
    return json.loads(signals_json) if signals_json else []
```

**Pros:** Real-time, scalable  
**Cons:** Additional infrastructure

---

## 📁 Example Project Structure

```
polymarket-trading/
│
├── trading-cli.py          # This CLI (display layer)
├── trading_engine.py       # Core trading logic
├── data_collector.py       # Market data collection
├── signal_generator.py     # Signal detection
├── risk_manager.py         # Risk controls
│
├── data/
│   ├── trading.db          # SQLite database
│   ├── signals.json        # Current signals
│   └── config.json         # System configuration
│
├── api/
│   └── server.py           # REST API (optional)
│
└── logs/
    └── trading-system.log
```

---

## 🔄 Real-Time Updates

### Auto-Refresh Dashboard

Add to `display_dashboard()`:

```python
def display_dashboard(auto_refresh=False, interval=30):
    """Display dashboard with optional auto-refresh"""
    
    while True:
        clear_screen()
        
        # ... display dashboard ...
        
        if not auto_refresh:
            break
        
        # Wait with countdown
        for remaining in range(interval, 0, -1):
            sys.stdout.write(f'\r  Refreshing in {remaining}s... (Press Ctrl+C to stop)')
            sys.stdout.flush()
            time.sleep(1)
```

Usage:
```bash
python trading-cli.py status --auto-refresh
```

---

## 🔐 Environment Variables

Store sensitive config in `.env`:

```bash
# .env
POLYMARKET_API_KEY=your_key_here
DATABASE_PATH=/path/to/trading.db
API_BASE_URL=http://localhost:8000
```

Load in Python:

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('POLYMARKET_API_KEY')
DB_PATH = os.getenv('DATABASE_PATH', 'trading.db')
```

---

## ✅ Quick Integration Checklist

- [ ] Choose architecture (API / DB / Files)
- [ ] Replace `get_system_status()` with real data
- [ ] Replace `get_active_signals()` with real signals
- [ ] Replace `get_portfolio()` with real positions
- [ ] Replace `get_recent_trades()` with trade history
- [ ] Replace `get_performance_data()` with real metrics
- [ ] Add error handling for connection failures
- [ ] Add authentication if using API
- [ ] Test with real data
- [ ] Add logging
- [ ] Set up auto-refresh (optional)
- [ ] Deploy!

---

## 🎯 Next Steps

1. **Start simple:** Replace one function at a time
2. **Test incrementally:** Verify each integration works
3. **Add error handling:** Network fails, DB locks, etc.
4. **Enhance UI:** Add more charts, filters, sorting
5. **Add features:** Export reports, alerts, notifications
6. **Scale up:** Move to API when needed

---

**Great success!** 🚀

Now you have a beautiful CLI that can display your real trading data!
