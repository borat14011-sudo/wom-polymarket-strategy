# Kalshi API vs Polymarket Research Report

**Research Date:** February 9, 2026  
**Purpose:** Compare automated trading capabilities between Kalshi and Polymarket

---

## Executive Summary

Both Kalshi and Polymarket offer prediction market APIs for automated trading, but they differ significantly in architecture, regulatory status, and technical implementation. **Polymarket currently has the superior API infrastructure** for automated trading, with more mature SDKs, better documentation, and higher liquidity. Kalshi is CFTC-regulated (US) but has less accessible API documentation and appears to have fewer third-party SDKs.

---

## 1. Kalshi API Features

### REST API
- **Availability:** ✅ Available (trading-api.readme.io)
- **Documentation Quality:** ⚠️ Limited public access - requires authentication to view full docs
- **Base URL:** `https://trading-api.readme.io/reference/`

### WebSocket Support
- **Status:** ✅ Available
- **Purpose:** Real-time market data and order updates
- **Limitation:** Documentation not publicly accessible

### Authentication Method
- **Type:** Login-based authentication with session tokens
- **Endpoint:** `POST /trade_api/v2/login`
- **Security:** Requires valid Kalshi account credentials

### Rate Limits
- **Status:** ⚠️ Not publicly documented
- **Assumption:** Standard rate limiting applies (typical for financial APIs)

### Python SDK Availability
- **Official SDK:** ❌ No official Python SDK found
- **Third-party:** ⚠️ Some community packages exist but not well-maintained
- **PyPI Package:** `kalshi-trade` exists but limited information available

### Documentation Quality
- **Score:** ⭐⭐ (2/5)
- **Issues:**
  - Documentation behind authentication wall
  - No public API explorer readily available
  - Limited examples for automated trading

---

## 2. Polymarket API Features

### REST API
- **Availability:** ✅ Fully Available
- **Endpoints:**
  - Gamma API: `https://gamma-api.polymarket.com` (market data)
  - CLOB API: `https://clob.polymarket.com` (trading)
  - Data API: `https://data-api.polymarket.com` (positions, history)
- **Documentation Quality:** ⭐⭐⭐⭐ (4/5) - Comprehensive, well-organized

### WebSocket Support
- **Status:** ✅ Fully Available
- **URL:** `wss://ws-subscriptions-clob.polymarket.com`
- **Channels:**
  - User channel (personal orders/trades)
  - Market channel (orderbook updates)
- **Features:** Subscribe/unsubscribe to asset IDs dynamically

### Authentication Method
- **Type:** Two-level authentication (L1 and L2)
- **L1 Authentication:** EIP-712 message signing with private key
- **L2 Authentication:** HMAC-SHA256 with API credentials
- **Process:**
  1. Sign message with private key → Get API credentials
  2. Use API credentials for subsequent requests
- **Security:** Non-custodial, user keeps private key

### Rate Limits
- **General CLOB:** 15,000 requests / 10 seconds
- **Market Data:** 1,500 requests / 10 seconds (orderbook)
- **Trading (POST /order):** 3,500 requests / 10 seconds (burst), 36,000 / 10 minutes (sustained)
- **Gamma API:** 4,000 requests / 10 seconds
- **Well-documented:** ✅ Yes

### Python SDK Availability
- **Official SDK:** ✅ `py-clob-client` 
- **Installation:** `pip install py-clob-client`
- **Features:**
  - TypeScript and Python clients
  - Full trading functionality
  - Order management
  - Market data retrieval
- **GitHub:** https://github.com/Polymarket/py-clob-client

### Documentation Quality
- **Score:** ⭐⭐⭐⭐⭐ (5/5)
- **Strengths:**
  - Clear quickstart guides
  - Authentication examples
  - Rate limit tables
  - WebSocket documentation
  - Market maker guides

---

## 3. Market Comparison

| Feature | Kalshi | Polymarket |
|---------|--------|------------|
| **Regulation** | CFTC-regulated (US) | Unregulated (crypto-based) |
| **Settlement** | USD (traditional) | USDC (crypto) |
| **Blockchain** | None (traditional) | Polygon (Ethereum L2) |
| **Geographic Restrictions** | US only | Global (with some restrictions) |
| **Volume** | Lower | Higher (world's largest prediction market) |
| **Liquidity** | Moderate | High |
| **Market Types** | Economic, Weather, Events, Sports | Politics, Crypto, Sports, Culture, Tech |

### Kalshi Markets
- Economics (inflation, jobs, Fed rates)
- Weather (temperature, rainfall)
- Financial indices (S&P 500)
- Political events (regulated)
- Sports (limited)

### Polymarket Markets
- Politics (elections, policy outcomes)
- Crypto (price predictions, events)
- Sports (extensive coverage)
- Culture (awards, trends)
- Tech (AI, product launches)
- Geopolitical events

### Volume Comparison
- **Kalshi:** Smaller volume, growing but limited by US-only access
- **Polymarket:** World's largest prediction market by volume, global user base

### Fee Structure

| Platform | Maker Fee | Taker Fee |
|----------|-----------|-----------|
| **Kalshi** | ~0% (varies) | ~0% (varies) |
| **Polymarket** | 0 bps (0%) | 0 bps (0%) |

**Note:** Polymarket currently has zero trading fees for all users.

---

## 4. Automated Trading Feasibility

### Kalshi

| Capability | Status | Notes |
|------------|--------|-------|
| Place orders via API | ✅ Yes | Supported |
| Check balances | ✅ Yes | Supported |
| Real-time market data | ✅ Yes | Via WebSocket |
| Order types | ⚠️ Limited | Market and limit orders |
| Testnet/Sandbox | ❌ Unknown | Not publicly documented |
| Cancel orders | ✅ Yes | Supported |
| Get order status | ✅ Yes | Supported |

### Polymarket

| Capability | Status | Notes |
|------------|--------|-------|
| Place orders via API | ✅ Yes | Full support |
| Check balances | ✅ Yes | Via Data API |
| Real-time market data | ✅ Yes | WebSocket + REST |
| Order types | ✅ Extensive | GTC, FOK, market, limit |
| Testnet/Sandbox | ❌ No | Production only |
| Cancel orders | ✅ Yes | Individual or all |
| Get order status | ✅ Yes | Real-time updates |
| Position tracking | ✅ Yes | Full history available |

### Order Types Comparison

**Kalshi:**
- Market orders
- Limit orders
- (Limited public documentation)

**Polymarket:**
- Market orders
- Limit orders (GTC - Good Till Canceled)
- Fill-or-Kill (FOK)
- Limit orders with tick size specifications
- Batch orders supported

---

## 5. Pros vs Cons

### Kalshi Advantages

✅ **Regulatory Compliance**
- CFTC-regulated (legally operates in US)
- Traditional financial structure
- USD settlement (no crypto needed)

✅ **US Accessibility**
- Available to US residents
- No crypto wallet required
- Traditional banking integration

✅ **Market Variety**
- Unique economic indicators
- Weather markets
- Financial markets

### Kalshi Disadvantages

❌ **API Accessibility**
- Documentation behind auth wall
- No official Python SDK
- Limited third-party tools

❌ **Geographic Limitations**
- US-only access
- Smaller user base

❌ **Lower Liquidity**
- Smaller volumes
- Wider spreads on some markets

### Polymarket Advantages

✅ **Superior API Infrastructure**
- Comprehensive documentation
- Official Python & TypeScript SDKs
- WebSocket support
- Well-defined rate limits

✅ **High Liquidity**
- World's largest prediction market
- Tight spreads
- High volume

✅ **Global Access**
- International user base
- No geographic restrictions (mostly)
- 24/7 market availability

✅ **Market Variety**
- Extensive political markets
- Crypto-native markets
- Sports, culture, tech

✅ **Zero Fees**
- No maker/taker fees
- Cost-efficient for high-frequency

✅ **Non-Custodial**
- You control your funds
- No counterparty risk
- Blockchain settlement

### Polymarket Disadvantages

❌ **Regulatory Uncertainty**
- Not regulated by CFTC
- Crypto settlement required
- Legal gray area in some jurisdictions

❌ **Crypto Requirements**
- Must hold USDC
- Need Polygon wallet
- Gas fees for some operations

❌ **US Accessibility**
- Not available to US residents (mostly)
- Requires VPN for US access

---

## 6. Recommendation

### Winner: Polymarket

**For automated trading, Polymarket is the clear winner** due to:

1. **Better API Infrastructure:** Mature SDKs, comprehensive docs, WebSocket support
2. **Higher Liquidity:** Better execution, tighter spreads
3. **Zero Fees:** More profitable for high-frequency strategies
4. **Global Markets:** Access to worldwide events

### When to Choose Kalshi:

- You're in the US and need regulatory compliance
- You prefer traditional USD settlement
- You trade economic indicators/weather markets
- You need CFTC-regulated platform

### When to Choose Polymarket:

- You want the best automated trading infrastructure
- You need high liquidity and volume
- You're outside the US
- You want zero trading fees
- You need extensive political/crypto markets
- You're comfortable with crypto settlement

---

## 7. Implementation Guide (Polymarket)

Since Polymarket is recommended, here's a quick start:

### Prerequisites
1. Python 3.9+
2. Polygon wallet with private key
3. USDC on Polygon network

### Installation
```bash
pip install py-clob-client
```

### Basic Implementation

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

# Configuration
HOST = "https://clob.polymarket.com"
CHAIN_ID = 137  # Polygon mainnet
PRIVATE_KEY = "your-private-key"
FUNDER = "your-wallet-address"

# Initialize client
client = ClobClient(
    host=HOST,
    key=PRIVATE_KEY,
    chain_id=CHAIN_ID,
    signature_type=0,  # 0=EOA, 1=Magic/Email, 2=Gnosis Safe
    funder=FUNDER
)

# Create API credentials
client.set_api_creds(client.create_or_derive_api_key())

# Get market data
midpoint = client.get_midpoint(token_id)
orderbook = client.get_order_book(token_id)

# Place a limit order
order = OrderArgs(
    token_id="your-token-id",
    price=0.65,
    size=100,
    side=BUY
)
signed_order = client.create_order(order)
response = client.post_order(signed_order, OrderType.GTC)

# Check open orders
open_orders = client.get_orders()

# Cancel order
client.cancel(order_id)
```

### Key Considerations

1. **Token Allowances:** EOA/MetaMask users must set token allowances before trading
2. **Signature Types:** Choose correct signature type based on wallet
3. **Tick Size:** Markets have different tick sizes (0.01, 0.001, etc.)
4. **Rate Limits:** Respect 3,500 orders/10s burst limit

---

## 8. Honest Limitations

### Kalshi Limitations:
- API docs not publicly accessible
- No well-maintained Python SDK
- Lower liquidity
- US-only access
- Limited market variety compared to Polymarket

### Polymarket Limitations:
- No sandbox/testnet for testing
- Crypto wallet complexity
- Not available to US residents
- Smart contract risk
- Gas fees for on-chain operations

---

## Conclusion

**For automated trading development, choose Polymarket.** It offers superior API infrastructure, better documentation, official SDKs, higher liquidity, and zero fees. The crypto requirement is a trade-off for significantly better automation capabilities.

**Choose Kalshi only if:**
- You need CFTC-regulated markets
- You're US-based and want USD settlement
- You specifically need Kalshi's unique markets (economic indicators, weather)

For serious automated trading, Polymarket's infrastructure advantage outweighs its regulatory complexity.

---

*Report generated for automated trading strategy evaluation.*
