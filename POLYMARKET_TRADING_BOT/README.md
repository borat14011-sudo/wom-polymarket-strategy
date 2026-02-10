# Polymarket Trading Bot

An automated trading bot for Polymarket using Playwright browser automation. This bot can log in, check balances, find markets, and execute trades based on configurable strategy parameters.

## Features

- ✅ **Automated Login** - Secure email/password authentication
- ✅ **Balance Checking** - Verify funds before trading
- ✅ **Market Discovery** - Find and navigate to target markets
- ✅ **Trade Execution** - Buy YES/NO positions at target prices
- ✅ **Price Validation** - Only trade when price is within tolerance
- ✅ **Comprehensive Logging** - All activity logged to files
- ✅ **Error Handling** - Retries with exponential backoff
- ✅ **Secure Credentials** - Environment-based configuration

## Strategy Configuration

The bot comes pre-configured with the following strategy:

| Parameter | Value |
|-----------|-------|
| Market | MicroStrategy 500K BTC Dec 31 |
| Action | BUY NO |
| Target Price | 83.5¢ (0.835) |
| Position Size | $8.00 |
| Price Tolerance | ±0.5¢ |

## Installation

### 1. Clone or Download

```bash
cd POLYMARKET_TRADING_BOT
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers

```bash
playwright install chromium
```

### 4. Configure Credentials

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your Polymarket credentials:

```env
POLYMARKET_EMAIL=your_email@example.com
POLYMARKET_PASSWORD=your_password
```

⚠️ **Security Note**: Never commit the `.env` file to version control. It's already in `.gitignore`.

## Usage

### Run the Bot

```bash
python trading_bot.py
```

### Run in Non-Headless Mode (See Browser)

Edit `.env` and add:

```env
HEADLESS=false
```

### Custom Strategy (Optional)

You can override the default strategy via environment variables:

```env
TARGET_MARKET=Different Market Name
TRADE_ACTION=BUY_YES
TARGET_PRICE=0.450
POSITION_SIZE=50.00
```

## File Structure

```
POLYMARKET_TRADING_BOT/
├── trading_bot.py      # Main bot script
├── config.py           # Strategy and bot configuration
├── requirements.txt    # Python dependencies
├── .env.example        # Template for credentials
├── .env                # Your credentials (create this)
├── README.md           # This file
└── logs/               # Log files created here
    └── trading_bot_YYYYMMDD_HHMMSS.log
```

## Configuration Options

### Bot Settings (in `.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `POLYMARKET_EMAIL` | - | Your Polymarket login email |
| `POLYMARKET_PASSWORD` | - | Your Polymarket login password |
| `HEADLESS` | `true` | Run browser without GUI |
| `LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `MAX_RETRIES` | `3` | Number of retry attempts for operations |
| `RETRY_DELAY` | `5` | Base delay between retries (seconds) |

### Trading Settings (in `config.py` or `.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `TARGET_MARKET` | "MicroStrategy 500K BTC Dec 31" | Market to trade on |
| `TRADE_ACTION` | "BUY_NO" | Action: BUY_YES or BUY_NO |
| `TARGET_PRICE` | `0.835` | Target price (83.5¢ = 0.835) |
| `POSITION_SIZE` | `8.00` | Amount to trade in USD |

## How It Works

1. **Initialize** - Launches browser (headless by default)
2. **Login** - Authenticates with provided credentials
3. **Check Balance** - Verifies sufficient funds
4. **Find Market** - Searches for and navigates to target market
5. **Get Prices** - Reads current YES/NO prices
6. **Validate** - Checks if current price is within tolerance of target
7. **Execute** - Submits trade if conditions are met
8. **Verify** - Confirms trade execution

## Logging

All bot activity is logged to:
- Console (stdout) - for real-time monitoring
- File (`logs/trading_bot_*.log`) - for historical records

Log files include timestamps, log levels, and detailed messages.

## Safety Features

- **Price Tolerance**: Only trades when current price is within ±0.5¢ of target
- **Minimum Balance Check**: Ensures sufficient funds before trading
- **Retry Logic**: Automatically retries failed operations
- **Secure Credentials**: Credentials never stored in code
- **No Hardcoded Secrets**: All sensitive data from environment variables

## Troubleshooting

### Bot can't find login fields

Polymarket may have updated their UI. Check the selectors in `trading_bot.py` and update them to match the current page structure.

### Trade not executing

- Check that the market is still active
- Verify your balance is sufficient
- Ensure the current price is within tolerance of target price
- Run with `HEADLESS=false` to see what's happening

### Timeout errors

Increase timeout values in `config.py`:

```python
implicit_wait: int = 20  # Increase from 10
page_load_timeout: int = 60  # Increase from 30
```

### Captcha or verification

If Polymarket presents a captcha, the bot will pause. You may need to:
1. Run in non-headless mode (`HEADLESS=false`)
2. Complete the captcha manually
3. Let the bot continue

## Important Disclaimers

⚠️ **Use at your own risk.** This bot is for educational purposes. Cryptocurrency prediction markets involve significant financial risk.

⚠️ **Test first.** Run with small amounts and verify behavior before trading larger positions.

⚠️ **Monitor execution.** While the bot has safety features, market conditions can change rapidly.

⚠️ **Compliance.** Ensure automated trading complies with Polymarket's Terms of Service.

## License

MIT License - Use at your own discretion.

## Support

For issues or questions, check the logs in the `logs/` directory first for detailed error messages.
