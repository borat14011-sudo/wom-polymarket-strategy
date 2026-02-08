# 🤖 Telegram Alert Bot for Polymarket Trading System

A robust, production-ready Telegram notification system with rich formatting, rate limiting, quiet hours, and interactive buttons.

## ✨ Features

### 📊 Alert Types
- **🚀 BUY Signal** - Market, price, confidence, reasoning
- **📉 SELL Signal** - Same rich format as BUY
- **⚠️ Risk Warning** - Loss tracking, limit alerts
- **🚨 System Alert** - Component health, data staleness
- **📊 Daily Summary** - Performance, P&L, win rate, signals

### 🎨 Message Formatting
- Rich Markdown formatting with emoji
- Inline buttons (Acknowledge, Dismiss, View Details)
- Visual scanning optimized
- Timestamp on every message

### 🌙 Quiet Hours
- Configurable quiet period (default: 11pm-8am)
- Critical alerts bypass quiet hours
- Non-critical alerts queued for morning delivery
- Morning summary of queued messages

### ⏱️ Rate Limiting
- Token bucket algorithm
- Max 30 messages/minute (configurable)
- 2-second cooldown between messages
- Automatic batching and throttling

### ⚙️ Configuration
- YAML-based config (`config.yaml`)
- Interactive setup wizard
- Easy first-time setup

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install requests pyyaml
```

### 2. Setup Bot

Run the interactive setup wizard:

```bash
python telegram-alerts.py --setup
```

The wizard will guide you through:
1. Creating a Telegram bot with @BotFather
2. Getting your chat ID
3. Configuring quiet hours

### 3. Test Connection

```bash
python telegram-alerts.py --test
```

You should receive a test message in Telegram!

## 📖 Usage

### CLI Commands

```bash
# Interactive setup
python telegram-alerts.py --setup

# Send test message
python telegram-alerts.py --test

# Check bot status
python telegram-alerts.py --status

# Send custom message
python telegram-alerts.py --send "Your message here"

# Flush queued messages (run in morning)
python telegram-alerts.py --flush

# Use custom config file
python telegram-alerts.py --config /path/to/config.yaml --test
```

### Python API

#### Basic Usage

```python
from telegram_alerts import TelegramBot

# Initialize bot (reads config.yaml)
bot = TelegramBot()

# Send a BUY signal
bot.send_signal(
    signal_type="BUY",
    market="Bitcoin reaches $100k by March",
    price=0.52,
    confidence="HIGH",
    reasoning="Strong bullish momentum + favorable macro conditions"
)

# Send a SELL signal
bot.send_signal(
    signal_type="SELL",
    market="Ethereum $5k by April",
    price=0.68,
    confidence="MEDIUM",
    reasoning="Price has peaked, declining volume"
)

# Send risk warning
bot.send_risk_warning(
    message="Portfolio approaching daily loss limit!",
    current_loss=450.00,
    limit=500.00,
    critical=True  # Send even during quiet hours
)

# Send system alert
bot.send_system_alert(
    message="Data feed delayed by 15 minutes",
    component="Polymarket API",
    critical=False  # Will queue during quiet hours
)

# Send daily summary
bot.send_daily_summary(
    trades=12,
    pnl="+$347.50",
    win_rate=0.75,
    signals_generated=28
)

# Generic alert
bot.send_alert("Trading bot started successfully!")
```

#### Advanced Usage

```python
# Flush queued messages (call in morning after quiet hours)
messages_sent = bot.flush_queue()
print(f"Sent {messages_sent} queued messages")

# Get bot status
status = bot.get_status()
print(f"Configured: {status['bot_configured']}")
print(f"Quiet hours active: {status['is_quiet_hours']}")
print(f"Queued messages: {status['queued_messages']}")

# Test connection programmatically
if bot.test_connection():
    print("Bot is working!")
```

## 🔧 Configuration

### config.yaml

```yaml
telegram:
  # Get from @BotFather on Telegram
  bot_token: "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
  
  # Your Telegram chat ID (use @userinfobot)
  chat_id: "123456789"

quiet_hours:
  # Enable quiet hours
  enabled: true
  
  # Quiet period (24-hour format)
  start: "23:00"
  end: "08:00"

rate_limit:
  # Maximum messages per minute
  max_per_minute: 30
  
  # Cooldown between messages (seconds)
  cooldown_seconds: 2.0
```

## 🎯 Integration with Trading System

### Example: Main Trading Loop

```python
from telegram_alerts import TelegramBot
import time

bot = TelegramBot()

# Startup notification
bot.send_alert("🚀 Trading bot started!", critical=True)

# Main loop
while True:
    try:
        # Your trading logic here
        signals = analyze_markets()
        
        for signal in signals:
            if signal['action'] == 'BUY':
                bot.send_signal(
                    signal_type="BUY",
                    market=signal['market'],
                    price=signal['price'],
                    confidence=signal['confidence'],
                    reasoning=signal['reasoning']
                )
        
        # Check risk limits
        current_loss = calculate_loss()
        if current_loss > 400:
            bot.send_risk_warning(
                message="Approaching loss limit!",
                current_loss=current_loss,
                limit=500,
                critical=True
            )
        
        time.sleep(60)  # Check every minute
        
    except Exception as e:
        bot.send_system_alert(
            message=f"Trading loop error: {str(e)}",
            component="Main Loop",
            critical=True
        )
```

### Example: Daily Summary (Cron Job)

```python
# Run this once per day (e.g., via cron at 5pm)
from telegram_alerts import TelegramBot

bot = TelegramBot()

# Gather stats
trades = get_today_trades()
pnl = calculate_daily_pnl()
win_rate = calculate_win_rate()
signals = count_signals()

# Send summary
bot.send_daily_summary(
    trades=trades,
    pnl=f"{'+' if pnl > 0 else ''}{pnl:.2f}",
    win_rate=win_rate,
    signals_generated=signals
)
```

### Example: Morning Flush (Cron Job)

```python
# Run every morning at 8:30am to flush queued messages
from telegram_alerts import TelegramBot

bot = TelegramBot()
count = bot.flush_queue()
print(f"Flushed {count} messages from queue")
```

## 📝 Demo Script

Run the included demo to see all alert types:

```bash
# Demo all alert types
python telegram_demo.py

# Simulate trading loop
python telegram_demo.py --loop
```

## 🛠️ How to Get Telegram Credentials

### 1. Create Bot with @BotFather

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow prompts to name your bot
5. Copy the **bot token** (looks like `1234567890:ABCdef...`)

### 2. Get Your Chat ID

**Method 1: @userinfobot**
1. Search for `@userinfobot` on Telegram
2. Send `/start`
3. Copy your **chat ID** (looks like `123456789`)

**Method 2: getUpdates API**
1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Look for `"chat":{"id": YOUR_CHAT_ID}`

### 3. Test Your Setup

```bash
python telegram-alerts.py --setup
# Enter your token and chat ID when prompted
```

## 🔒 Security Notes

- **Never commit `config.yaml`** to version control!
- Add `config.yaml` to `.gitignore`
- Use environment variables in production:

```python
import os
from telegram_alerts import TelegramBot

# Override config with env vars
bot = TelegramBot()
bot.token = os.environ.get('TELEGRAM_BOT_TOKEN')
bot.chat_id = os.environ.get('TELEGRAM_CHAT_ID')
```

## 📊 Message Queue

Messages sent during quiet hours are queued to `telegram_queue.json`:

```json
[
  {
    "message": "Alert text...",
    "buttons": [...],
    "queued_at": "2026-02-06T03:30:00"
  }
]
```

Flush the queue manually or via cron:

```bash
python telegram-alerts.py --flush
```

## 🐛 Troubleshooting

### "Missing telegram credentials"

Run the setup wizard:
```bash
python telegram-alerts.py --setup
```

### "Failed to send message"

1. Check your internet connection
2. Verify bot token is correct
3. Ensure chat ID is correct
4. Make sure you've sent `/start` to your bot

### Rate limit errors

The bot automatically handles rate limiting, but if you see errors:
- Reduce `max_per_minute` in config.yaml
- Increase `cooldown_seconds`

### Messages not received

1. Check you're using correct chat ID
2. Ensure bot hasn't been blocked
3. Test with: `python telegram-alerts.py --test`

## 📦 File Structure

```
.
├── telegram-alerts.py        # Main bot module + CLI
├── telegram_demo.py           # Demo/example script
├── config.yaml                # Your configuration (create with --setup)
├── config.yaml.example        # Example configuration
├── telegram_queue.json        # Message queue (auto-created)
└── TELEGRAM_BOT_README.md     # This file
```

## 🎓 Tips & Best Practices

1. **Test first!** Always run `--test` after setup
2. **Use critical flag wisely** - Only for urgent alerts
3. **Flush queue daily** - Set up a cron job for 8am
4. **Monitor rate limits** - Check `--status` regularly
5. **Batch similar alerts** - Don't spam yourself
6. **Use confidence levels** - HIGH/MEDIUM/LOW for signals
7. **Add reasoning** - Context helps decision-making

## 📈 Advanced Features

### Custom Config Path

```python
bot = TelegramBot(config_path="/path/to/custom/config.yaml")
```

### Check if Quiet Hours

```python
if bot._is_quiet_hours():
    print("Shh, it's quiet time")
```

### Manual Queue Management

```python
# Add to queue
bot.queue.add("Custom message", buttons=[...])

# Check queue
count = bot.queue.count()

# Get all queued messages
messages = bot.queue.get_all()

# Clear queue
bot.queue.clear()
```

## 🚀 Production Deployment

### Systemd Service (Linux)

Create `/etc/systemd/system/trading-bot.service`:

```ini
[Unit]
Description=Polymarket Trading Bot
After=network.target

[Service]
Type=simple
User=trader
WorkingDirectory=/home/trader/trading-bot
ExecStart=/usr/bin/python3 /home/trader/trading-bot/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Cron Jobs

```cron
# Flush queue every morning at 8:30am
30 8 * * * cd /path/to/bot && python telegram-alerts.py --flush

# Daily summary at 5pm
0 17 * * * cd /path/to/bot && python daily_summary.py
```

## 📄 License

Great success! 🎉

---

**Questions? Issues? Improvements?**

This bot is designed to be simple, reliable, and production-ready. Enjoy! 🚀
