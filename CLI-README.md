# 🚀 Polymarket Hype Trading System - CLI

**Beautiful, colorful, interactive command-line interface** for your Polymarket trading system!

## ✨ Features

### 🎨 **Rich Visual Experience**
- **Color-coded output** - Green for success, red for errors, yellow for warnings
- **Progress bars** - With percentage, ETA, and color gradients
- **Animated spinners** - For loading operations
- **ASCII charts** - Line charts and sparklines for trends
- **Beautiful tables** - With Unicode box-drawing characters
- **Emoji indicators** - Visual status markers

### 📊 **Comprehensive Dashboard**
- Real-time system status
- Component health monitoring  
- Portfolio summary with P&L
- Active trading signals
- Performance charts
- Trade history

### 🎯 **Dual Interface**
1. **Interactive Menu** - Navigate with numbers
2. **Quick Commands** - Direct CLI access

---

## 🚀 Quick Start

### Interactive Mode
```bash
python trading-cli.py
```
Opens the main menu with all options.

### Direct Commands
```bash
python trading-cli.py status      # System dashboard
python trading-cli.py signals     # Active signals
python trading-cli.py portfolio   # Your positions
python trading-cli.py trades      # Recent trades
python trading-cli.py pnl         # Performance metrics
python trading-cli.py start       # Start trading
python trading-cli.py stop        # Stop trading
```

---

## 📸 What It Looks Like

**See `CLI-DEMO.md` for full visual examples!**

### Main Menu
```
  ════════════════════════════════════════════════════════════
        🚀 POLYMARKET HYPE TRADING SYSTEM
  ════════════════════════════════════════════════════════════

  [1] 📊 System Status
  [2] 🚀 Start System
  [3] 🛑 Stop System
  [4] 📈 View Signals
  ...
```

### Dashboard with Charts
```
  PORTFOLIO VALUE
 11500 ┤                    ●
 11000 ┤                  ●│
 10500 ┤          ●●●●●●●││
 10000 ┤    ●●●●●│││││││││
  9500 ┤●●●●││││││││││││││
       └─────────────────────
```

### Color-Coded Signals
- **🟢 BUY** - Strong upward momentum
- **🔴 SELL** - Strong downward pressure  
- **🟡 HOLD** - Wait for clearer signal

---

## 🎨 Color System

| Color  | Usage |
|--------|-------|
| 🟢 Green | Success, profits, healthy, BUY |
| 🔴 Red | Errors, losses, critical, SELL |
| 🟡 Yellow | Warnings, caution, HOLD |
| 🔵 Blue | Info, neutral data |
| 🔷 Cyan | Headers, highlights |
| ⚫ Gray | Timestamps, secondary |

---

## 📦 Installation

**No dependencies required!** Uses only Python standard library.

### Requirements
- Python 3.6+
- Terminal with ANSI color support (most modern terminals)

### Works On
- ✅ Windows 10/11 (PowerShell, CMD, Windows Terminal)
- ✅ macOS (Terminal, iTerm2)
- ✅ Linux (any terminal)

---

## 🎮 Usage Guide

### 1️⃣ **System Status**
View complete dashboard with:
- Component health
- Portfolio balance & P&L
- Active signals
- Performance chart

```bash
python trading-cli.py status
```

### 2️⃣ **Trading Signals**
See all active trading opportunities:
```bash
python trading-cli.py signals
```

Table shows:
- Market name
- Signal (BUY/SELL/HOLD)
- Confidence level
- Price & target
- Volume surge
- Trend direction

### 3️⃣ **Portfolio**
Check your positions:
```bash
python trading-cli.py portfolio
```

Shows:
- Balance
- Total P&L (all-time)
- Today's P&L
- Win rate
- Position details

### 4️⃣ **Recent Trades**
View trade history:
```bash
python trading-cli.py trades
```

### 5️⃣ **Performance**
Detailed analytics:
```bash
python trading-cli.py pnl
```

Includes:
- Total return %
- Sharpe ratio
- Max drawdown
- Win rate
- Historical chart
- Sparkline trends

### 6️⃣ **Start/Stop System**
```bash
python trading-cli.py start   # With progress indicators
python trading-cli.py stop    # With confirmation prompt
```

---

## 🔧 Customization

### Mock Data
Currently uses **demo data** for display. To connect to real trading system:

1. Replace mock functions in `trading-cli.py`:
   - `get_system_status()`
   - `get_active_signals()`
   - `get_portfolio()`
   - `get_recent_trades()`
   - `get_performance_data()`

2. Connect to your actual data sources:
   - API calls
   - Database queries
   - File reads
   - Real-time websockets

### Configuration
Add settings via `config.json`:
```json
{
  "max_position_size": 2500,
  "risk_per_trade": 0.025,
  "stop_loss": 0.15,
  "take_profit": 0.25,
  "min_confidence": 0.65,
  "auto_trade": true
}
```

---

## 🎯 Key Components

### Color Utilities
```python
success("Profit!")      # Green
error("Loss!")          # Red  
warning("Caution!")     # Yellow
info("Note:")           # Blue
header("SECTION")       # Cyan bold
```

### Progress Bar
```python
progress = ProgressBar(100, prefix="Loading")
for i in range(100):
    progress.update(i)
```

### Spinner
```python
spinner = Spinner("Processing")
spinner.start()
# ... do work ...
spinner.stop("Done!")
```

### Tables
```python
headers = ['Name', 'Value', 'Status']
rows = [
    ['Item 1', '100', success('OK')],
    ['Item 2', '50', error('FAIL')]
]
table = format_table(headers, rows)
```

### Charts
```python
# Line chart
chart = ascii_line_chart(data, width=60, height=10)

# Sparkline
trend = ascii_sparkline(prices, width=20)
```

---

## 🐛 Troubleshooting

### Colors Not Showing
**Windows:** Use Windows Terminal or enable ANSI in CMD:
```cmd
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1
```

### Encoding Errors
Set UTF-8 encoding:
```bash
export PYTHONIOENCODING=utf-8  # Linux/Mac
$env:PYTHONIOENCODING="utf-8"  # Windows PowerShell
```

### Layout Issues
Resize terminal to at least **80 columns wide** for best display.

---

## 🎉 Examples

**See `CLI-DEMO.md` for:**
- Full dashboard screenshot
- All menu options
- Signal tables
- Portfolio views
- Performance charts
- Logs display

---

## 📝 License

Part of the Polymarket Hype Trading System.

---

## 🙌 Credits

Built with:
- Python standard library only
- ANSI escape codes for colors
- Unicode box-drawing characters
- No external dependencies

**Great success!** 🚀
