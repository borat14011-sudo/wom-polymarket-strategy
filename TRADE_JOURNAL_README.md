# 📊 Trade Journal - Professional Trading Journal for Polymarket

A comprehensive trade journaling and analysis system with psychological tracking, performance analytics, and automated insights.

## 🎯 Features

### 1. **Complete Trade Tracking**
- Entry timestamp, market, price, size
- Exit timestamp, price, P&L calculation
- Signal that triggered the trade
- Confidence level (0-100)
- Personal notes and reasoning

### 2. **Trade Tagging & Categorization**
- **Category:** crypto, politics, sports
- **Strategy:** hype, momentum, mean-reversion
- **Outcome:** win, loss, scratch (auto-calculated)
- **Quality:** good trade, bad trade, lucky, unlucky
- **Emotion tracking:** calm, excited, anxious, fomo, revenge

### 3. **Performance Analytics**
- Win rate by category, strategy, time of day
- Average winner vs average loser
- Expectancy calculation (edge estimation)
- Win/loss ratio
- Best and worst trading days
- P&L tracking and cumulative equity curve

### 4. **Behavioral Analysis** 🧠
- **FOMO detection:** Automatic flagging of FOMO trades
- **Revenge trading detection:** Identifies emotional trading
- **Overtrading patterns:** Detects >10 trades in 4 hours
- **Emotion tracking:** Monitor your psychological state
- **Quality assessment:** Tag trades as good/bad/lucky/unlucky

### 5. **Learning System**
- Review past trades
- Identify repeating mistakes
- Track improvement over time
- AI-generated insights and recommendations

### 6. **Professional Reports**
- Daily journal summary
- Weekly performance review
- Monthly reports
- HTML export with interactive charts (Plotly)
- Visual equity curves and analytics

---

## 🚀 Installation

```bash
# Core module (no dependencies)
pip install sqlite3  # Built into Python

# Optional: For rich CLI output
pip install rich

# Optional: For HTML reports with charts
pip install plotly
```

---

## 💻 CLI Usage

### View Today's Journal
```bash
python trade-journal.py
```

### Add Trade Interactively
```bash
python trade-journal.py add
```
**Example prompts:**
```
Market ID: btc-100k-by-eoy
Market Name: Bitcoin to $100,000 by End of Year
Entry Price: 0.52
Size: 100
Signal: hype
Confidence (0-100): 75
Category (crypto/politics/sports): crypto
Strategy (hype/momentum/mean-reversion): momentum
Notes (optional): Strong momentum after ETF approval
Emotion (calm/excited/anxious/fomo/revenge): excited
```

### Close a Trade
```bash
python trade-journal.py exit 5 0.68 --notes "Target reached"
```

### Review Recent Trades
```bash
python trade-journal.py review
python trade-journal.py review --limit 20
python trade-journal.py review --category crypto
python trade-journal.py review --strategy momentum
```

### Performance Analytics
```bash
python trade-journal.py analytics
python trade-journal.py analytics --days 30
```

**Output includes:**
- Overall win rate and P&L
- Expectancy calculation
- Performance by category
- Performance by strategy
- Best trading hours
- Best/worst trading days
- Behavioral flags (FOMO, revenge trading)

### Trading Insights
```bash
python trade-journal.py insights
```

**Example insights:**
```
🎯 Strong win rate: 65.2% - You're doing great!
💰 Positive expectancy: $12.34 per trade
🏆 Best category: crypto (72.1% win rate)
❌ Worst category: sports (38.5% win rate)
💡 Most profitable strategy: momentum ($245.67)
⏰ Best trading hour: 14:00 (78.3% win rate)
😴 Worst trading hour: 23:00 (31.2% win rate)
⚠️ FOMO detected: 3 trades - Work on patience!
```

### Generate Reports
```bash
# Daily report
python trade-journal.py report daily
python trade-journal.py report daily --date 2026-02-05

# Weekly review
python trade-journal.py report weekly
```

### Export to HTML
```bash
python trade-journal.py export journal.html
python trade-journal.py export journal.html --days 30
```

**HTML report includes:**
- Interactive equity curve
- Win rate by category
- P&L by strategy
- Trade outcomes pie chart
- Quality distribution
- Key insights and statistics

### Tag Trades
```bash
python trade-journal.py tag 5 --quality good
python trade-journal.py tag 12 --quality lucky
python trade-journal.py tag 8 --outcome win
```

---

## 🐍 Programmatic Usage

### Basic Integration

```python
from trade_journal import Journal

# Initialize journal
journal = Journal()  # Uses default DB: polymarket_trades.db
# Or specify custom DB:
# journal = Journal("my_trades.db")

# Log trade entry
trade_id = journal.log_entry(
    market_id="btc-100k-eoy",
    market_name="Bitcoin to $100,000 by End of Year",
    price=0.52,
    size=100,
    signal="hype",
    confidence=75,
    category="crypto",
    strategy="momentum",
    notes="Strong momentum after ETF approval",
    emotion="excited"
)

print(f"Trade #{trade_id} logged")

# Log trade exit
journal.log_exit(
    trade_id=trade_id,
    price=0.68,
    notes="Target reached, took profit"
)

print(f"Trade #{trade_id} closed with profit")
```

### Advanced Analytics

```python
from trade_journal import Journal

journal = Journal()

# Get comprehensive analytics
analytics = journal.get_analytics(days=30)

# Overall performance
overall = analytics['overall']
print(f"Win Rate: {overall['win_rate']:.1f}%")
print(f"Total P&L: ${overall['total_pnl']:.2f}")
print(f"Expectancy: ${overall['expectancy']:.2f}")
print(f"Average Winner: ${overall['avg_win']:.2f}")
print(f"Average Loser: ${overall['avg_loss']:.2f}")

# By category
for category, stats in analytics['by_category'].items():
    print(f"{category}: {stats['win_rate']:.1f}% WR, ${stats['total_pnl']:.2f}")

# By strategy
for strategy, stats in analytics['by_strategy'].items():
    print(f"{strategy}: {stats['win_rate']:.1f}% WR, ${stats['total_pnl']:.2f}")

# Best trading hours
for hour, stats in analytics['by_hour'].items():
    print(f"{hour:02d}:00 - {stats['win_rate']:.1f}% WR")
```

### Automated Insights

```python
from trade_journal import Journal

journal = Journal()

# Get AI-generated insights
insights = journal.get_insights()

for insight in insights:
    print(insight)

# Example output:
# 🎯 Strong win rate: 65.2% - You're doing great!
# 💰 Positive expectancy: $12.34 per trade
# 🚨 FOMO detected: 3 trades - Work on patience!
# 🏆 Best category: crypto (72.1% win rate)
# 💡 Most profitable strategy: momentum ($245.67)
```

### Query Trades

```python
from trade_journal import Journal

journal = Journal()

# Get recent trades
trades = journal.get_trades(limit=10)

# Get only closed trades
closed_trades = journal.get_trades(closed_only=True)

# Filter by category
crypto_trades = journal.get_trades(category="crypto")

# Filter by strategy
momentum_trades = journal.get_trades(strategy="momentum")

# Filter by date range
recent_trades = journal.get_trades(
    start_date="2026-02-01",
    end_date="2026-02-07"
)

# Process trades
for trade in trades:
    print(f"[{trade['id']}] {trade['market_name']}")
    print(f"  P&L: ${trade['pnl']:.2f}")
    print(f"  Win Rate: {trade['outcome']}")
```

### Tag Trades

```python
from trade_journal import Journal

journal = Journal()

# Tag trade quality
journal.tag_trade(trade_id=5, quality="good")
journal.tag_trade(trade_id=12, quality="lucky")

# Override outcome
journal.tag_trade(trade_id=8, outcome="win")

# Set behavioral flags
journal.tag_trade(trade_id=15, is_fomo=True)
journal.tag_trade(trade_id=23, is_revenge=True)
```

### Generate Reports

```python
from trade_journal import Journal

journal = Journal()

# Daily report
daily = journal.generate_daily_report()
print(daily)

# Daily report for specific date
daily = journal.generate_daily_report(date="2026-02-05")
print(daily)

# Weekly review
weekly = journal.generate_weekly_report()
print(weekly)

# Export HTML report
journal.export_html("report.html", days=30)
```

---

## 🗄️ Database Schema

The journal uses SQLite with the following schema:

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT NOT NULL,
    market_name TEXT NOT NULL,
    
    -- Entry
    entry_timestamp TEXT NOT NULL,
    entry_price REAL NOT NULL,
    size REAL NOT NULL,
    signal TEXT NOT NULL,
    confidence REAL NOT NULL,
    category TEXT NOT NULL,
    strategy TEXT NOT NULL,
    entry_notes TEXT,
    emotion TEXT,
    
    -- Exit
    exit_timestamp TEXT,
    exit_price REAL,
    pnl REAL,
    pnl_percent REAL,
    exit_notes TEXT,
    
    -- Tags
    outcome TEXT,  -- win, loss, scratch
    quality TEXT,  -- good, bad, lucky, unlucky
    
    -- Behavioral flags
    is_fomo INTEGER DEFAULT 0,
    is_revenge INTEGER DEFAULT 0,
    is_overtrading INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📈 Key Metrics Explained

### Win Rate
Percentage of trades that were profitable.
```
Win Rate = (Winning Trades / Total Trades) × 100
```

### Expectancy
Average amount you can expect to win (or lose) per trade. This is your "edge."
```
Expectancy = (Win Rate × Average Win) - (Loss Rate × Average Loss)
```

**Interpretation:**
- Positive expectancy = Long-term profitable system
- Negative expectancy = Losing money over time
- Goal: Maximize expectancy through better trade selection

### Win/Loss Ratio
How big your average winner is compared to your average loser.
```
Win/Loss Ratio = Average Winner / Average Loser
```

**Interpretation:**
- Ratio > 2:1 = Excellent (big winners, small losers)
- Ratio > 1.5:1 = Good
- Ratio < 1:1 = Poor (losers bigger than winners)

### P&L (Profit & Loss)
```
P&L = (Exit Price - Entry Price) × Size
P&L % = ((Exit Price - Entry Price) / Entry Price) × 100
```

---

## 🧠 Behavioral Analysis Features

### FOMO Detection
- **Trigger:** When emotion is marked as "fomo"
- **Warning:** Indicates impulsive trading due to fear of missing out
- **Solution:** Wait for better setups, avoid chasing

### Revenge Trading Detection
- **Trigger:** When emotion is marked as "revenge"
- **Warning:** Trading to "get back" losses (emotional decision)
- **Solution:** Take breaks after losses, stick to strategy

### Overtrading Detection
- **Trigger:** >10 trades in 4 hours
- **Warning:** Excessive trading reduces quality
- **Solution:** Quality over quantity, wait for A+ setups

### Emotion Tracking
Track your emotional state for each trade:
- **calm** ✅ - Ideal trading state
- **excited** ⚠️ - Be careful of overconfidence
- **anxious** ⚠️ - May lead to premature exits
- **fomo** 🚨 - High risk of poor decisions
- **revenge** 🚨 - Emotional trading, take a break

---

## 📊 Example Analytics Output

```
📊 Performance Analytics
============================================================

Overall Performance:
  Total Trades: 45
  Win Rate: 64.4%
  Total P&L: $1,245.67
  Average P&L: $27.68
  Best Trade: $156.34
  Worst Trade: -$67.89
  Expectancy: $23.45
  Average Winner: $45.23
  Average Loser: -$28.91
  Win/Loss Ratio: 1.56:1

📂 By Category:
  crypto      :  68.2% WR | $ 856.34 P&L | 22 trades
  politics    :  61.5% WR | $ 312.45 P&L | 13 trades
  sports      :  50.0% WR | $  76.88 P&L | 10 trades

🎯 By Strategy:
  momentum        :  72.7% WR | $ 678.90 P&L | 22 trades
  hype            :  58.8% WR | $ 423.12 P&L | 17 trades
  mean-reversion  :  50.0% WR | $ 143.65 P&L |  6 trades

⏰ Best Trading Hours:
  14:00 - 78.6% WR | $42.34 avg |  8 trades
  10:00 - 71.4% WR | $38.12 avg |  7 trades
  16:00 - 66.7% WR | $31.45 avg |  9 trades

🏆 Best Days:
  2026-02-05: $ 234.56 (5 trades)
  2026-02-03: $ 189.23 (7 trades)
  2026-02-01: $ 156.78 (4 trades)

❌ Worst Days:
  2026-02-04: $ -89.34 (6 trades)
  2026-02-02: $ -45.67 (3 trades)

⚠️ Behavioral Issues:
  FOMO Trades: 3
  Revenge Trades: 1
  Overtrading Instances: 2
```

---

## 🎯 Trading Insights Examples

The journal automatically generates actionable insights:

```
🎯 Strong win rate: 64.4% - You're doing great!
💰 Positive expectancy: $23.45 per trade
🏆 Best category: crypto (68.2% win rate)
❌ Worst category: sports (50.0% win rate)
💡 Most profitable strategy: momentum ($678.90)
⏰ Best trading hour: 14:00 (78.6% win rate)
😴 Worst trading hour: 22:00 (33.3% win rate)
💪 Excellent win/loss ratio: 1.56:1
🚨 FOMO detected: 3 trades - Work on patience!
😤 Revenge trading: 1 trade - Take breaks after losses!
```

---

## 🔧 Integration with Polymarket Trading System

### Automatic Trade Logging

```python
from trade_journal import Journal

class PolymarketTrader:
    def __init__(self):
        self.journal = Journal()
    
    def execute_trade(self, signal):
        # Execute trade on Polymarket
        order = self.place_order(signal)
        
        # Log in journal
        trade_id = self.journal.log_entry(
            market_id=order.market_id,
            market_name=order.market_name,
            price=order.price,
            size=order.size,
            signal=signal.type,
            confidence=signal.confidence,
            category=signal.category,
            strategy=signal.strategy,
            notes=signal.reasoning
        )
        
        # Store trade_id for exit logging
        self.active_trades[order.id] = trade_id
    
    def close_trade(self, order_id, exit_price):
        # Get journal trade_id
        trade_id = self.active_trades[order_id]
        
        # Log exit
        self.journal.log_exit(
            trade_id=trade_id,
            price=exit_price
        )
        
        # Get analytics
        analytics = self.journal.get_analytics()
        print(f"Win Rate: {analytics['overall']['win_rate']:.1f}%")
```

### Performance Monitoring

```python
from trade_journal import Journal

journal = Journal()

# Check performance before trading
analytics = journal.get_analytics(days=7)

# If having a bad week, reduce position sizes or take a break
if analytics['overall']['win_rate'] < 50:
    print("⚠️ Win rate below 50% this week - Review strategy!")

# Check for behavioral issues
insights = journal.get_insights()
if any('FOMO' in i for i in insights):
    print("🚨 FOMO detected - Take a break!")

# Track improvement
monthly_analytics = journal.get_analytics(days=30)
weekly_analytics = journal.get_analytics(days=7)

if weekly_analytics['overall']['win_rate'] > monthly_analytics['overall']['win_rate']:
    print("📈 Improving! Keep it up!")
```

---

## 🎓 Best Practices

### 1. **Log Every Trade**
- No exceptions - log wins AND losses
- Be honest with emotion tracking
- Write notes about your reasoning

### 2. **Review Regularly**
- Daily: Review today's trades
- Weekly: Check analytics and insights
- Monthly: Deep dive into patterns

### 3. **Tag Your Trades**
- Mark "good" trades (followed your plan, regardless of outcome)
- Mark "bad" trades (broke rules, even if you won)
- Separate process from outcome

### 4. **Learn from Patterns**
- What categories/strategies work best for YOU?
- What time of day are you sharpest?
- What emotions lead to losses?

### 5. **Track Psychology**
- Log your emotional state honestly
- Identify FOMO and revenge trading
- Take breaks when needed

### 6. **Focus on Expectancy**
- Win rate is nice, but expectancy is king
- A 40% win rate with 3:1 ratio is profitable
- Track and optimize your edge

---

## 🚀 Quick Start

1. **Install dependencies** (optional):
   ```bash
   pip install rich plotly
   ```

2. **Log your first trade**:
   ```bash
   python trade-journal.py add
   ```

3. **Close the trade**:
   ```bash
   python trade-journal.py exit 1 0.68
   ```

4. **View analytics**:
   ```bash
   python trade-journal.py analytics
   ```

5. **Get insights**:
   ```bash
   python trade-journal.py insights
   ```

6. **Export report**:
   ```bash
   python trade-journal.py export report.html
   ```

---

## 📝 Files Created

- `trade-journal.py` - Main journal module and CLI
- `trade-journal-example.py` - Example with sample trades
- `polymarket_trades.db` - SQLite database (auto-created)

---

## 🎯 Great Success!

Your trade journal is ready. Start logging trades, track your performance, and become a better trader through data-driven insights!

Remember: **The goal isn't to win every trade. The goal is to have a positive expectancy and improve over time.**

Happy trading! 🚀
