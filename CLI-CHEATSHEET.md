# 🚀 Polymarket Trading CLI - Quick Reference Card

## 📱 Commands

```bash
# Interactive menu
python trading-cli.py

# Quick commands
python trading-cli.py status       # Dashboard view
python trading-cli.py signals      # Trading signals
python trading-cli.py portfolio    # Your positions
python trading-cli.py trades       # Trade history
python trading-cli.py pnl          # Performance metrics
python trading-cli.py start        # Start system
python trading-cli.py stop         # Stop system
```

---

## 🎨 Color Guide

| Color | Meaning | Example |
|-------|---------|---------|
| 🟢 Green | Success, Profit, BUY | `✓ Order filled` |
| 🔴 Red | Error, Loss, SELL | `✗ Connection lost` |
| 🟡 Yellow | Warning, HOLD | `⚠ High volatility` |
| 🔵 Blue | Info | `Portfolio updated` |
| 🔷 Cyan | Headers | `SYSTEM STATUS` |
| ⚫ Gray | Timestamps | `2024-02-06 05:52` |

---

## 📊 Signal Types

| Signal | Meaning | Color |
|--------|---------|-------|
| **BUY** | Strong upward momentum | 🟢 Green |
| **SELL** | Strong downward pressure | 🔴 Red |
| **HOLD** | No clear signal, wait | 🟡 Yellow |

---

## 🎯 Key Features

### Progress Bar
```
Loading ████████░░░░░░░░ 65% (65/100) ETA: 5s
```

### Spinner
```
⠋ Connecting to API...
```

### Chart
```
11000 ┤        ●
10500 ┤      ●│●
10000 ┤●●●●●│││●
      └───────────
```

### Sparkline
```
▂▃▄▅▅▆▇███████
```

### Table
```
┌────────┬────────┐
│ Market │ Signal │
├────────┼────────┤
│ Trump  │ BUY    │
└────────┴────────┘
```

---

## 💡 Quick Tips

1. **See full dashboard:** `python trading-cli.py status`
2. **Check signals:** Press `4` in menu or run with `signals` argument
3. **Monitor P&L:** Press `5` in menu for portfolio view
4. **View charts:** Press `6` for performance analysis
5. **Exit anytime:** Press `0` or `Ctrl+C`

---

## 🔧 Code Structure

```python
# Import and use colors
from trading_cli import Colors, colorize, success, error, warning

# Color text
print(success("Profit!"))        # Green
print(error("Loss!"))            # Red
print(warning("Caution!"))       # Yellow

# Progress bar
from trading_cli import ProgressBar
progress = ProgressBar(100, "Loading")
progress.update(50)  # 50%

# Spinner
from trading_cli import Spinner
spinner = Spinner("Processing")
spinner.start()
time.sleep(2)
spinner.stop("Done!")

# Charts
from trading_cli import ascii_line_chart, ascii_sparkline
chart = ascii_line_chart([100, 110, 105, 120], width=40, height=10)
sparkline = ascii_sparkline([100, 110, 105, 120], width=20)

# Tables
from trading_cli import format_table
headers = ['Name', 'Value']
rows = [['Item 1', '100'], ['Item 2', '200']]
table = format_table(headers, rows)
```

---

## 📂 Files

| File | Purpose |
|------|---------|
| `trading-cli.py` | Main application |
| `CLI-README.md` | User guide |
| `CLI-DEMO.md` | Visual examples |
| `CLI-INTEGRATION.md` | Integration guide |
| `CLI-SUMMARY.md` | Completion report |
| `CLI-CHEATSHEET.md` | This quick reference |

---

## 🎓 Menu Options

```
[1] 📊 System Status    - Full dashboard with charts
[2] 🚀 Start System     - Start trading (with animation)
[3] 🛑 Stop System      - Stop trading (with confirmation)
[4] 📈 View Signals     - Active trading opportunities
[5] 💰 Portfolio        - Positions and P&L
[6] 📉 Performance      - Charts and metrics
[7] ⚙️  Settings        - Configuration view
[8] 📝 Logs             - Recent system logs
[9] ❓ Help             - Documentation
[0] 🚪 Exit             - Quit application
```

---

## 🔌 Integration Quick Start

**Step 1:** Open `trading-cli.py`

**Step 2:** Find these functions:
```python
get_system_status()     # Line ~XXX
get_active_signals()    # Line ~XXX
get_portfolio()         # Line ~XXX
get_recent_trades()     # Line ~XXX
get_performance_data()  # Line ~XXX
```

**Step 3:** Replace with your data sources:
```python
def get_portfolio():
    # Your code here
    response = requests.get('http://localhost:8000/api/portfolio')
    return response.json()
```

**Step 4:** Test!

---

## 🚦 Status Indicators

| Icon | Meaning |
|------|---------|
| ● Green | Healthy/Running |
| ● Yellow | Warning |
| ● Red | Critical/Error |
| ✓ | Success |
| ✗ | Failure |
| ↗ | Trending up |
| ↘ | Trending down |
| → | Flat/Sideways |

---

## 🎯 Use Cases

### Morning Check
```bash
python trading-cli.py status
```
See overnight performance and system health

### Signal Alert
```bash
python trading-cli.py signals
```
Check for new trading opportunities

### End of Day
```bash
python trading-cli.py pnl
```
Review daily performance

### Quick Position Check
```bash
python trading-cli.py portfolio
```
See current P&L

---

## 💻 System Requirements

- **Python:** 3.6 or higher
- **OS:** Windows 10+, macOS, Linux
- **Terminal:** Any with ANSI color support
- **Dependencies:** None! (stdlib only)

---

## 🐛 Troubleshooting

### No colors?
```bash
# Windows: Use Windows Terminal
# Or enable ANSI:
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1
```

### Layout broken?
- Resize terminal to at least 80 columns wide

### Encoding errors?
```bash
export PYTHONIOENCODING=utf-8  # Mac/Linux
$env:PYTHONIOENCODING="utf-8"  # Windows PowerShell
```

---

## 🎉 That's It!

**Start:** `python trading-cli.py`

**Explore:** Try all menu options

**Integrate:** Replace mock data with real data

**Profit:** Great success! 🚀

---

**Need more help?**
- Full guide: `CLI-README.md`
- Visual examples: `CLI-DEMO.md`
- Integration: `CLI-INTEGRATION.md`
