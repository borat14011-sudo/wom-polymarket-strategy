# Polymarket Trading Bot

A simple, working trading bot for Polymarket prediction markets.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- Polymarket account with Magic Link (Google/Email login)
- At least $10 USDC on Polygon in your Polymarket wallet

### 2. Get Your Credentials

**A. Private Key:**
1. Go to https://reveal.magic.link/polymarket
2. Export your private key
3. **SECURELY SAVE IT** - this gives full access to your funds

**B. Funder Address:**
1. Log into polymarket.com
2. Go to Settings → Wallet
3. Copy your wallet address (starts with `0x...`)

**C. Make a Manual Trade:**
- Make at least one $0.20 trade on the website first
- This activates API permissions for your account

### 3. Installation

```bash
# Clone or create the bot directory
cd polymarket_bot

# Install dependencies
pip install -r requirements.txt
```

### 4. Configuration

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your credentials
# Use a text editor to fill in:
# POLYMARKET_PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
# POLYMARKET_FUNDER_ADDRESS=0xYOUR_FUNDER_ADDRESS_HERE
```

### 5. Run the Bot

```bash
# Test the bot components
python main.py
# Choose option 3: Test components only

# Run one trade cycle
python main.py
# Choose option 1: Run once (immediate)

# Run scheduled (every 30 minutes)
python main.py  
# Choose option 2: Run scheduled
```

## 📁 Project Structure

```
polymarket_bot/
├── config.py              # Configuration and env loading
├── market_scanner.py      # Fetch markets, find opportunities
├── order_manager.py       # Place, check, cancel orders
├── risk_manager.py        # Position sizing, exposure checks
├── trade_logger.py        # SQLite logging of every trade
├── main.py               # Main loop: scan → evaluate → trade → log
├── .env                  # NEVER commit this (credentials)
├── .env.example          # Template for .env
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 How It Works

### Trading Cycle
1. **Scan Markets** - Fetch active markets with > $1000 daily volume
2. **Check Risk** - Verify position limits aren't exceeded
3. **Evaluate** - Apply simple strategy (example: buy NO < 20%)
4. **Place Orders** - $0.20 limit orders using official SDK
5. **Log Everything** - SQLite database tracks all trades

### Risk Management
- Max $0.20 per trade
- Max $2.50 total exposure  
- Max 3 concurrent positions
- 12% stop loss per position
- 15% drawdown circuit breaker

### Current Strategy (Example)
The bot currently implements a simple strategy:
- Buy NO positions when price < 20¢ (20% probability)
- $0.20 position size per trade
- Good Till Cancelled (GTC) limit orders

**Replace this with your actual strategy** in `main.py` `execute_trade_cycle()` method.

## ⚠️ Important Notes

### Security
- **NEVER commit `.env` to version control**
- Use different API keys for testing vs production
- Consider using a separate wallet for bot trading
- Monitor your bot regularly

### Limitations
- This is educational software
- Test with small amounts first ($0.20 trades)
- Polymarket API may change without notice
- No guarantee of profitability

### Troubleshooting

**"Invalid api key" or 401 errors:**
1. Make sure you've made at least one manual trade on the website
2. Verify private key from https://reveal.magic.link/polymarket
3. Check funder address matches your Polymarket wallet

**Import errors:**
```bash
# Reinstall with pinned versions
pip uninstall py-clob-client web3
pip install py-clob-client==0.34.5 web3==6.14.0
```

**Balance not showing:**
- The bot may need to make its first trade before balance is visible
- Check your wallet on polymarket.com directly

## 📊 Trade Logging

All trades are logged to `trades.db` (SQLite) with:
- Timestamp
- Market question
- Token ID
- Side (BUY/SELL)
- Price and size
- Order ID
- Status and P&L

View trades:
```python
from trade_logger import TradeLogger
logger = TradeLogger()
logger.print_stats()
```

## 🔄 Next Steps

1. **Paper trade first** - Run the bot without real money
2. **Develop your strategy** - Replace the example strategy
3. **Add more features** - Stop losses, take profits, etc.
4. **Deploy to VPS** - For 24/7 operation when ready

## 📚 Resources

- [Polymarket API Docs](https://docs.polymarket.com)
- [py-clob-client GitHub](https://github.com/Polymarket/py-clob-client)
- [Magic Link Private Key Reveal](https://reveal.magic.link/polymarket)

## ⚖️ Disclaimer

This software is for educational purposes only. Trading prediction markets involves risk of loss. Only trade with money you can afford to lose. The authors are not responsible for any losses incurred.

---

**Remember:** $10 is tuition, not capital. Focus on building a working system first, profits second.