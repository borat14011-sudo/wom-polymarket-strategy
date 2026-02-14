# Kalshi Trading Bot Setup Guide

## 🏆 Why Kalshi?

Kalshi is the **ONLY** US-LEGAL prediction market exchange, regulated by the CFTC (Commodity Futures Trading Commission). No VPN needed for US users!

| Feature | Kalshi | Polymarket |
|---------|--------|------------|
| **US Legal** | ✅ Yes (CFTC regulated) | ❌ No (US blocked) |
| **Currency** | USD (real dollars) | USDC (crypto) |
| **VPN Needed** | ❌ No | ✅ Required for US |
| **KYC Required** | Yes | Limited |
| **Trading Fees** | Quadratic (see below) | 0% most markets |
| **API Access** | Full REST + WebSocket | REST + CLOB |
| **Official SDK** | ✅ kalshi-python | Community only |

---

## 📋 Quick Start Checklist

1. [ ] Create Kalshi account at https://kalshi.com
2. [ ] Complete identity verification (KYC)
3. [ ] Fund your account (ACH, wire, or debit card)
4. [ ] Generate API keys (Account & Security → API Keys)
5. [ ] Install dependencies: `pip install kalshi-python requests cryptography websockets`
6. [ ] Run the trading bot!

---

## 🔑 Getting API Credentials

### Step 1: Log in to Kalshi
- **Production:** https://kalshi.com
- **Demo (paper trading):** https://demo.kalshi.com

### Step 2: Navigate to API Keys
`Account & Security → API Keys → Create Key`

### Step 3: Save Your Credentials
You'll receive:
- **Private Key:** Downloaded as a `.key` file (PEM format)
- **API Key ID:** UUID displayed on screen (e.g., `a952bcbe-ec3b-4b5b-b8f9-11dae589608c`)

⚠️ **IMPORTANT:** Store your private key securely! Never commit it to Git.

---

## 🌐 API Endpoints

### Base URLs
| Environment | REST API | WebSocket |
|-------------|----------|-----------|
| **Production** | `https://api.elections.kalshi.com/trade-api/v2` | `wss://api.elections.kalshi.com/trade-api/ws/v2` |
| **Demo** | `https://demo-api.kalshi.co/trade-api/v2` | `wss://demo-api.kalshi.co/trade-api/ws/v2` |

### Key Endpoints

#### Public (No Auth Required)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/markets` | GET | List all markets |
| `/markets/{ticker}` | GET | Get specific market |
| `/markets/{ticker}/orderbook` | GET | Get orderbook |
| `/series` | GET | List market series |
| `/events` | GET | List events |
| `/exchange/status` | GET | Exchange status |

#### Authenticated
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/portfolio/balance` | GET | Your balance |
| `/portfolio/positions` | GET | Your positions |
| `/portfolio/orders` | GET/POST | List/Create orders |
| `/portfolio/orders/{id}` | GET/DELETE | Get/Cancel order |
| `/portfolio/fills` | GET | Your fills/trades |

---

## 🔐 Authentication

Kalshi uses RSA-PSS signatures for authentication. Every authenticated request requires 3 headers:

| Header | Description |
|--------|-------------|
| `KALSHI-ACCESS-KEY` | Your API Key ID |
| `KALSHI-ACCESS-TIMESTAMP` | Current Unix timestamp in **milliseconds** |
| `KALSHI-ACCESS-SIGNATURE` | RSA-PSS signature (base64 encoded) |

### Signature Creation
```python
message = f"{timestamp}{method}{path_without_query}"
# Sign with RSA-PSS + SHA256
# Encode as base64
```

---

## 📝 Order Parameters

### Create Order Request
```json
{
  "ticker": "MARKET-TICKER",
  "action": "buy",           // "buy" or "sell"
  "side": "yes",             // "yes" or "no"
  "count": 10,               // Number of contracts
  "type": "limit",           // "limit" or "market"
  "yes_price": 50,           // Price in cents (1-99)
  "client_order_id": "uuid"  // For deduplication
}
```

### Order Types
- **Limit:** Specify exact price, order rests in book
- **Market:** Execute at best available price
- **Fill or Kill (FoK):** All or nothing
- **IOC (Immediate or Cancel):** Fill what you can, cancel rest

### Price Notes
- Prices are in **cents** (1-99)
- `yes_price` + `no_price` = 100
- If you want to buy YES at 60¢, someone else is selling YES at 60¢ (or buying NO at 40¢)

---

## 💰 Kalshi Fees

Kalshi uses a **quadratic fee model** that scales with contract count and price:

```
Fee = FEE_MULTIPLIER × contracts × price × (100 - price)
```

### Fee Characteristics
- Fees are **highest at 50¢** (maximum uncertainty)
- Fees are **lowest near 0¢ or 100¢** (high certainty)
- Typical fee multiplier: varies by series
- Check `/series/fee_changes` endpoint for current rates

### Example Fee Calculation
- 10 contracts at 50¢, multiplier 0.00025:
  - Fee = 0.00025 × 10 × 50 × 50 = **$0.625**
- 10 contracts at 90¢, multiplier 0.00025:
  - Fee = 0.00025 × 10 × 90 × 10 = **$0.225**

---

## 📊 WebSocket Channels

### Public Channels (No Auth)
| Channel | Description |
|---------|-------------|
| `ticker` | Price/volume updates for all markets |
| `trade` | Trade executions |
| `market_lifecycle_v2` | Market status changes |
| `multivariate` | Multivariate market updates |

### Private Channels (Auth Required)
| Channel | Description |
|---------|-------------|
| `orderbook_delta` | Orderbook updates |
| `fill` | Your fills |
| `market_positions` | Your position updates |
| `order_group_updates` | Order group status |

### Subscribe Message
```json
{
  "id": 1,
  "cmd": "subscribe",
  "params": {
    "channels": ["ticker", "orderbook_delta"],
    "market_ticker": "MARKET-TICKER"
  }
}
```

---

## 🆚 Kalshi vs Polymarket Detailed Comparison

### Legal Status
| Aspect | Kalshi | Polymarket |
|--------|--------|------------|
| US Access | ✅ Legal | ❌ Blocked (uses VPN/crypto) |
| Regulation | CFTC regulated exchange | Unregulated |
| KYC | Full identity verification | Limited/Optional |
| Tax Reporting | Provides 1099 forms | You handle it |

### Trading
| Aspect | Kalshi | Polymarket |
|--------|--------|------------|
| Currency | USD | USDC (Polygon) |
| Settlement | USD to bank | USDC to wallet |
| Deposit Methods | ACH, Wire, Debit | Crypto only |
| Contract Size | $1 per contract | $1 per share |

### Fees
| Aspect | Kalshi | Polymarket |
|--------|--------|------------|
| Trading Fee | Quadratic (varies) | 0% most markets |
| Withdrawal | Free | Gas fees |
| Deposit | Free | Gas/exchange fees |

### API
| Aspect | Kalshi | Polymarket |
|--------|--------|------------|
| Official SDK | ✅ kalshi-python | ❌ Community |
| Auth Method | RSA-PSS signatures | API key + wallet signing |
| WebSocket | ✅ Full support | ✅ Full support |
| Rate Limits | 10 req/sec | 40 req/sec |

### Market Coverage
| Category | Kalshi | Polymarket |
|----------|--------|------------|
| Politics | ✅ | ✅ |
| Economics | ✅ | ✅ |
| Weather | ✅ | Limited |
| Sports | ✅ | ✅ |
| Crypto Prices | Limited | ✅ |
| Pop Culture | Some | ✅ |

---

## 🚀 Using the Official SDK

The `kalshi-python` package simplifies everything:

```python
from kalshi_python import Configuration, KalshiClient

# Configure
config = Configuration(
    host="https://api.elections.kalshi.com/trade-api/v2"
)

# Load your private key
with open("kalshi-key.key", "r") as f:
    config.private_key_pem = f.read()
config.api_key_id = "your-api-key-id"

# Initialize client
client = KalshiClient(config)

# Get balance
balance = client.get_balance()
print(f"Balance: ${balance.balance / 100:.2f}")

# Get markets
markets = client.get_markets(status="open", limit=10)
for m in markets.markets:
    print(f"{m.ticker}: {m.title} - Yes: {m.yes_bid}¢")

# Place order
order = client.create_order(
    ticker="MARKET-TICKER",
    action="buy",
    side="yes",
    count=1,
    type="limit",
    yes_price=50
)
print(f"Order placed: {order.order.order_id}")
```

---

## ⚠️ Risk Warnings

1. **Real Money:** Kalshi involves real USD. Only trade what you can afford to lose.
2. **Market Risk:** Prediction markets can move rapidly on news.
3. **Liquidity Risk:** Some markets have thin orderbooks.
4. **Settlement Risk:** Contracts settle at $0 or $1 - no partial outcomes.
5. **API Risk:** Bot errors can result in unintended trades. Always use the demo environment first!

---

## 📚 Resources

- **API Documentation:** https://docs.kalshi.com
- **Developer Agreement:** https://kalshi.com/developer-agreement
- **Discord:** https://discord.gg/kalshi
- **Demo Environment:** https://demo.kalshi.com
- **Status Page:** Check exchange hours and status

---

## 🎯 Trading Strategy Ideas

1. **Arbitrage:** Compare odds across sources (news, polls, other markets)
2. **Market Making:** Provide liquidity, earn the spread
3. **Event-Driven:** Trade on scheduled events (Fed meetings, earnings)
4. **Statistical:** Use historical data to find mispriced markets
5. **News Trading:** React quickly to breaking news

---

*Happy Trading! 🎲📈*
