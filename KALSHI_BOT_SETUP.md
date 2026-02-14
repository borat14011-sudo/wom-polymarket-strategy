# Kalshi Trading Bot - Setup Guide

A Python trading bot for Kalshi prediction markets using a "Buy the Dip" strategy.

## Features

- 🔐 **RSA Key Authentication** - Secure API access
- 📝 **Paper Trading Mode** - Test without real money (default)
- 📉 **Buy the Dip Strategy** - Automatically buy when prices drop
- 📊 **Position Tracking** - Monitor your holdings
- 📋 **Comprehensive Logging** - File and console logs
- ⚙️ **Configurable Parameters** - Customize strategy behavior

## Quick Start

### 1. Install Dependencies

```bash
pip install requests cryptography
```

Or install the official Kalshi SDK (optional, for more features):
```bash
pip install kalshi-python
```

### 2. Get API Credentials

1. Go to [Kalshi](https://kalshi.com) and create an account
2. Navigate to **Settings** → **API** or visit [kalshi.com/account/api](https://kalshi.com/account/api)
3. Generate an API key pair:
   - **API Key ID** - A unique identifier (e.g., `abc123-def456-...`)
   - **Private Key** - An RSA private key (download the `.pem` file)

⚠️ **Important**: Save your private key immediately! You cannot download it again.

### 3. Configure the Bot

**Option A: Environment Variables (Recommended)**

```bash
# Required for live trading
export KALSHI_API_KEY_ID="your-api-key-id-here"
export KALSHI_PRIVATE_KEY_PATH="path/to/kalshi_private_key.pem"

# Optional settings
export KALSHI_PAPER_TRADING="true"  # Set to "false" for live trading
export KALSHI_MIN_DIP_PERCENT="0.15"  # 15% price drop to trigger buy
export KALSHI_MAX_BUY_PRICE="50"  # Max price 50 cents
export KALSHI_ORDER_SIZE="10"  # Buy 10 contracts per trade
export KALSHI_POLL_INTERVAL="30"  # Check every 30 seconds
```

**Option B: Edit `kalshi_config.py` directly**

```python
API_KEY_ID = "your-api-key-id-here"
PRIVATE_KEY_PATH = "kalshi_private_key.pem"
```

### 4. Run the Bot

```bash
# Paper trading mode (SAFE - no real money)
python kalshi_trading_bot.py

# Run once and exit
python kalshi_trading_bot.py --once

# Check exchange status
python kalshi_trading_bot.py --status

# List active markets
python kalshi_trading_bot.py --markets

# LIVE trading (⚠️ REAL MONEY)
python kalshi_trading_bot.py --live
```

## Configuration Options

### Strategy Settings

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `KALSHI_MIN_DIP_PERCENT` | `0.15` | Minimum price drop % to trigger buy (0.15 = 15%) |
| `KALSHI_MAX_BUY_PRICE` | `50` | Maximum buy price in cents ($0.50) |
| `KALSHI_MIN_BUY_PRICE` | `5` | Minimum buy price in cents ($0.05) |
| `KALSHI_ORDER_SIZE` | `10` | Number of contracts per order |
| `KALSHI_MAX_POSITION` | `100` | Maximum contracts per market |
| `KALSHI_MAX_CAPITAL` | `10000` | Maximum total capital in cents ($100) |

### Execution Settings

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `KALSHI_POLL_INTERVAL` | `30` | Seconds between market scans |
| `KALSHI_PAPER_TRADING` | `true` | Enable paper trading mode |
| `KALSHI_LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `KALSHI_LOG_FILE` | `kalshi_bot.log` | Log file path |

## How It Works

### Buy the Dip Strategy

1. **Scan Markets** - Fetches all active Kalshi markets
2. **Track Prices** - Maintains price history for each market
3. **Detect Dips** - Identifies markets where price dropped significantly
4. **Filter Signals** - Only buys if:
   - Price dropped ≥ MIN_DIP_PERCENT
   - Current price is between MIN_BUY_PRICE and MAX_BUY_PRICE
   - Position limit not exceeded
   - Capital limit not exceeded
5. **Execute Orders** - Places limit orders at current ask price
6. **Repeat** - Continues scanning at POLL_INTERVAL

### Paper Trading Mode

Paper trading simulates orders without using real money:
- Starts with $100 virtual balance
- Tracks positions and P&L
- Logs all "trades" for review
- Perfect for testing before going live

## API Reference

### Kalshi API v2

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/exchange/status` | GET | Check if exchange is active |
| `/markets` | GET | List all markets |
| `/markets/{ticker}` | GET | Get specific market |
| `/markets/{ticker}/orderbook` | GET | Get market orderbook |
| `/portfolio/balance` | GET | Get account balance |
| `/portfolio/positions` | GET | Get open positions |
| `/portfolio/orders` | GET | Get orders |
| `/portfolio/orders` | POST | Create new order |
| `/portfolio/orders/{id}` | DELETE | Cancel order |

**Base URL**: `https://api.elections.kalshi.com/trade-api/v2`

### Authentication

Kalshi uses RSA key-based authentication:

1. Generate a timestamp (milliseconds since epoch)
2. Create message: `{timestamp}{METHOD}{path}`
3. Sign with RSA-SHA256 using your private key
4. Include headers:
   - `KALSHI-ACCESS-KEY`: Your API key ID
   - `KALSHI-ACCESS-SIGNATURE`: Base64-encoded signature
   - `KALSHI-ACCESS-TIMESTAMP`: The timestamp used

## Fee Structure

Kalshi fees (as of 2024):
- **Trading Fee**: ~3% of winnings (not on contract purchase)
- **Withdrawal Fee**: None for standard methods
- **No deposit fees**

Example: Buy YES at $0.30, contract settles to $1.00
- Your profit: $0.70
- Fee: ~$0.02 (3% of $0.70)
- Net profit: $0.68

## Safety Features

- 🛡️ **Paper Trading Default** - Won't use real money unless explicitly enabled
- 🔒 **Position Limits** - Prevents over-concentration in single markets
- 💰 **Capital Limits** - Won't exceed maximum deployment
- ⚠️ **Live Trading Confirmation** - Requires typing "CONFIRM" to proceed
- 📝 **Comprehensive Logging** - All actions are logged

## Troubleshooting

### "Private key file not found"
- Ensure `kalshi_private_key.pem` exists in the correct path
- Check `KALSHI_PRIVATE_KEY_PATH` environment variable

### "API request failed: 401"
- Verify your API key ID is correct
- Ensure the private key matches the API key
- Check that your API key hasn't been revoked

### "No markets fetched"
- Check your internet connection
- Verify Kalshi exchange is active: `python kalshi_trading_bot.py --status`

### "No buy signals"
- Lower `KALSHI_MIN_DIP_PERCENT` to detect smaller dips
- Increase `KALSHI_MAX_BUY_PRICE` to consider higher-priced markets
- Check if the markets you want are active

## Example Output

```
==================================================
🤖 KALSHI TRADING BOT STARTING
   Mode: PAPER TRADING
==================================================
✅ Connected to Kalshi - Trading ACTIVE
📊 Fetched 847 markets
🎯 Found 3 buy signals!
   • KXNBA-26FEB12-LAL: Price dropped 18.2% (price: 42¢)
   • WEATHER-NYC-SNOW: Price dropped 22.1% (price: 15¢)
📝 PAPER ORDER: BUY 10x KXNBA-26FEB12-LAL yes @ 42¢
   Balance: $95.80 | PnL: $0.00
✨ Executed 2 orders
----------------------------------------
💰 Balance: $95.80
📈 P&L: $0.00
📦 Positions: 2
   • KXNBA-26FEB12-LAL yes: 10 @ 42¢
   • WEATHER-NYC-SNOW yes: 10 @ 15¢
😴 Sleeping 30s until next iteration...
```

## Disclaimer

⚠️ **IMPORTANT**: This bot is for educational purposes. Trading prediction markets involves risk. Never trade with money you can't afford to lose. Past performance does not indicate future results.

## License

MIT License - Use at your own risk.
