# Polymarket CLOB API Reference

Complete API reference for the Polymarket Central Limit Order Book (CLOB) system.

---

## Table of Contents

1. [Base URLs](#base-urls)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Rate Limits](#rate-limits)
6. [Error Codes](#error-codes)
7. [Best Practices](#best-practices)

---

## Base URLs

| API | Base URL | Description |
|-----|----------|-------------|
| **CLOB API** | `https://clob.polymarket.com` | Order management, prices, orderbooks |
| **Gamma API** | `https://gamma-api.polymarket.com` | Market discovery, metadata, events |
| **Data API** | `https://data-api.polymarket.com` | User positions, activity, history |
| **CLOB WebSocket** | `wss://ws-subscriptions-clob.polymarket.com/ws/` | Orderbook updates, order status |
| **RTDS** | `wss://ws-live-data.polymarket.com` | Low-latency crypto prices, comments |

### Network Details

- **Chain ID**: 137 (Polygon mainnet)
- **No Testnet**: Polymarket does not currently provide a testnet endpoint. Testing should be done with small amounts on mainnet.

---

## Authentication

Polymarket CLOB uses two levels of authentication:

### L1 Authentication (Wallet/Private Key)

L1 authentication uses the wallet's private key to sign an EIP-712 message used in the request header. It proves ownership and control over the private key.

**Required Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `POLY_ADDRESS` | Yes | Polygon signer address |
| `POLY_SIGNATURE` | Yes | CLOB EIP-712 signature |
| `POLY_TIMESTAMP` | Yes | Current UNIX timestamp (seconds) |
| `POLY_NONCE` | Yes | Nonce (default: 0) |

**EIP-712 Signing Example:**

```typescript
// TypeScript reference implementation:
// https://github.com/Polymarket/clob-client/blob/main/src/signing/eip712.ts

// Python reference implementation:
// https://github.com/Polymarket/py-clob-client/blob/main/py_clob_client/signing/eip712.py
```

**L1 Endpoints:**
- `POST /auth/api-key` - Create new API credentials
- `GET /auth/derive-api-key` - Derive existing API credentials

**Response:**
```json
{
  "apiKey": "550e8400-e29b-41d4-a716-446655440000",
  "secret": "base64EncodedSecretString",
  "passphrase": "randomPassphraseString"
}
```

### L2 Authentication (API Credentials)

L2 uses the API credentials (apiKey, secret, passphrase) generated from L1 authentication. Requests are signed using HMAC-SHA256.

**Required Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `POLY_ADDRESS` | Yes | Polygon signer address |
| `POLY_SIGNATURE` | Yes | HMAC-SHA256 signature for request |
| `POLY_TIMESTAMP` | Yes | Current UNIX timestamp (seconds) |
| `POLY_API_KEY` | Yes | User's API apiKey value |
| `POLY_PASSPHRASE` | Yes | User's API passphrase value |

**HMAC-SHA256 Signing:**

```typescript
// TypeScript reference:
// https://github.com/Polymarket/clob-client/blob/main/src/signing/hmac.ts

// Python reference:
// https://github.com/Polymarket/py-clob-client/blob/main/py_clob_client/signing/hmac.py
```

### Signature Types

When initializing the client, you must specify your wallet signatureType:

| Signature Type | Value | Description |
|----------------|-------|-------------|
| **EOA** | 0 | Standard Ethereum wallet (MetaMask, hardware wallets). Funder is the EOA address and will need POL to pay gas. |
| **POLY_PROXY** | 1 | Email/Magic wallet (delegated signing). Must export PK from reveal.magic.link/polymarket |
| **GNOSIS_SAFE** | 2 | Gnosis Safe multisig proxy wallet (most common for browser wallet connections) |

### Funder Address

The `funder` address is the actual address that holds your funds (USDC) on Polymarket. When using proxy wallets (email wallets like Magic or browser extension wallets), the signing key differs from the address holding the funds.

---

## Endpoints

### Public Endpoints (No Authentication Required)

#### Server Status

```
GET /
```
Check API status.

**Response:**
```json
{
  "status": "ok"
}
```

---

```
GET /time
```
Get server timestamp.

**Response:**
```json
1707340800
```

---

#### Markets

```
GET /markets?next_cursor={cursor}
```
List all markets with pagination.

**Parameters:**
- `next_cursor` (optional): Pagination cursor

**Response:**
```json
{
  "data": [...],
  "next_cursor": "...",
  "has_more": true
}
```

---

```
GET /markets/{condition_id}
```
Get specific market details by condition ID.

**Response:** Market object with condition details, token IDs, and metadata.

---

```
GET /simplified-markets?next_cursor={cursor}
```
Get simplified market data.

---

```
GET /sampling-markets?next_cursor={cursor}
```
Get sampling market data.

---

```
GET /sampling-simplified-markets?next_cursor={cursor}
```
Get simplified sampling market data.

---

#### Order Book

```
GET /book?token_id={token_id}
```
Get order book for a specific token.

**Parameters:**
- `token_id` (required): The token ID (from Gamma API)

**Response:**
```json
{
  "market": "0x...",
  "bids": [
    {
      "price": "0.65",
      "size": "100"
    }
  ],
  "asks": [
    {
      "price": "0.66",
      "size": "100"
    }
  ]
}
```

---

```
POST /books
```
Get multiple order books in a single request.

**Request Body:**
```json
[
  { "token_id": "0x..." },
  { "token_id": "0x..." }
]
```

---

#### Prices

```
GET /price?token_id={token_id}&side={BUY|SELL}
```
Get current price for a token.

**Parameters:**
- `token_id` (required): Token ID
- `side` (required): `BUY` or `SELL`

**Response:**
```json
{
  "price": "0.65"
}
```

---

```
POST /prices
```
Get multiple prices in a single request.

---

```
GET /midpoint?token_id={token_id}
```
Get midpoint price (average of best bid and ask).

**Response:**
```json
{
  "mid": "0.655"
}
```

---

```
POST /midpoints
```
Get multiple midpoints in a single request.

---

```
GET /spread?token_id={token_id}
```
Get bid-ask spread for a token.

---

```
POST /spreads
```
Get multiple spreads in a single request.

---

```
GET /last-trade-price?token_id={token_id}
```
Get last traded price for a token.

---

```
POST /last-trades-prices
```
Get multiple last trade prices in a single request.

---

```
GET /prices-history?token_id={token_id}&interval={interval}&start_ts={start}&end_ts={end}
```
Get historical price data.

---

#### Market Metadata

```
GET /tick-size?token_id={token_id}
```
Get minimum tick size for a market.

**Response:**
```json
{
  "minimum_tick_size": "0.001"
}
```

---

```
GET /neg-risk?token_id={token_id}
```
Check if market is negative risk.

**Response:**
```json
{
  "neg_risk": false
}
```

---

```
GET /fee-rate?token_id={token_id}
```
Get fee rate for a market.

**Response:**
```json
{
  "base_fee": 0
}
```

---

```
GET /live-activity/events/{condition_id}
```
Get live trade events for a market.

---

### L1 Authenticated Endpoints

```
POST /auth/api-key
```
Create new API credentials.

**Headers:** L1 Authentication headers required

---

```
GET /auth/derive-api-key
```
Derive existing API credentials.

**Headers:** L1 Authentication headers required

---

### L2 Authenticated Endpoints

#### Account Management

```
GET /auth/api-keys
```
List all API keys for the user.

**Headers:** L2 Authentication headers required

---

```
DELETE /auth/api-key
```
Delete current API key.

---

```
GET /auth/ban-status/closed-only
```
Check if account is in closed-only mode.

---

#### Balance & Allowance

```
GET /balance-allowance?token_id={token_id}&side={BUY|SELL}
```
Check balance and allowance.

**Headers:** L2 Authentication headers required

**Response:**
```json
{
  "balance": "1000.00",
  "allowance": "500.00"
}
```

---

```
POST /balance-allowance/update
```
Update token allowance (for EOA wallets).

**Request Body:**
```json
{
  "token_id": "0x...",
  "amount": "1000"
}
```

---

#### Orders

```
POST /order
```
Place a single order.

**Headers:** L2 Authentication headers required

**Request Body (Limit Order):**
```json
{
  "order": {
    "salt": "1234567890",
    "maker": "0x...",
    "signer": "0x...",
    "taker": "0x...",
    "tokenId": "0x...",
    "makerAmount": "1000000",
    "takerAmount": "1538461",
    "expiration": "0",
    "nonce": "0",
    "feeRateBps": "0",
    "side": "BUY",
    "signatureType": 1,
    "signature": "0x..."
  },
  "owner": "0x...",
  "orderType": "GTC"
}
```

**Order Types:**
- `GTC` - Good Till Cancelled
- `FOK` - Fill Or Kill
- `IOC` - Immediate Or Cancel

**Response:**
```json
{
  "orderID": "0x...",
  "status": "live",
  "transactionHash": "0x...",
  "success": true
}
```

---

```
POST /orders
```
Place multiple orders in a single request.

**Rate Limit:** 100/10s burst, 25/min sustained

---

```
DELETE /order/{order_id}
```
Cancel a specific order.

**Rate Limit:** 300/10s burst, 50/min sustained

---

```
DELETE /orders
```
Cancel multiple orders.

**Rate Limit:** 100/10s burst, 25/min sustained

---

```
DELETE /cancel-all
```
Cancel all open orders.

**Rate Limit:** 25/10s burst, 10/min sustained

---

```
DELETE /cancel-market-orders
```
Cancel all orders for specific markets.

**Request Body:**
```json
{
  "marketIds": ["0x...", "0x..."]
}
```

---

#### Order Data

```
GET /data/orders?token_id={token_id}&status={status}
```
List user's open orders.

**Parameters:**
- `token_id` (optional): Filter by token
- `status` (optional): `OPEN`, `FILLED`, `CANCELLED`

**Response:**
```json
{
  "data": [
    {
      "id": "0x...",
      "status": "OPEN",
      "price": "0.65",
      "size": "100",
      "side": "BUY",
      "tokenId": "0x...",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "next_cursor": "..."
}
```

---

```
GET /data/order/{order_id}
```
Get details of a specific order.

---

```
GET /data/trades?token_id={token_id}
```
Get user's trade history.

**Response:**
```json
{
  "data": [
    {
      "id": "0x...",
      "orderId": "0x...",
      "price": "0.65",
      "size": "100",
      "side": "BUY",
      "tokenId": "0x...",
      "createdAt": "2024-01-01T00:00:00Z",
      "transactionHash": "0x..."
    }
  ]
}
```

---

```
GET /order-scoring?order_id={order_id}
```
Check if an order is scoring (rewards eligible).

---

```
POST /orders-scoring
```
Check scoring status for multiple orders.

---

#### Notifications

```
GET /notifications
```
Get user notifications.

---

```
DELETE /notifications
```
Drop/clear notifications.

---

#### Rewards

```
GET /rewards/user?date={YYYY-MM-DD}
```
Get earnings for user for a specific day.

---

```
GET /rewards/user/total?date={YYYY-MM-DD}
```
Get total earnings for user.

---

```
GET /rewards/user/percentages
```
Get liquidity reward percentages.

---

```
GET /rewards/markets/current
```
Get current rewards markets.

---

```
GET /rewards/markets/{market_id}
```
Get rewards for specific market.

---

```
GET /rewards/user/markets
```
Get user's reward earnings percentages.

---

### Builder Endpoints (Optional)

```
GET /builder/trades
```
Get trades for builder attribution.

```
POST /auth/builder-api-key
```
Create builder API key.

```
GET /auth/builder-api-key
```
Get builder API keys.

```
DELETE /auth/builder-api-key
```
Revoke builder API key.

---

## Request/Response Formats

### Order Structure

```typescript
interface Order {
  salt: string;           // Random salt for uniqueness
  maker: string;          // Maker address
  signer: string;         // Signer address
  taker: string;          // Taker address (usually zero address)
  tokenId: string;        // Token ID (from Gamma API)
  makerAmount: string;    // Amount in base units
  takerAmount: string;    // Amount in base units
  expiration: string;     // Expiration timestamp (0 for no expiry)
  nonce: string;          // Order nonce
  feeRateBps: string;     // Fee rate in basis points
  side: "BUY" | "SELL";   // Order side
  signatureType: number;  // 0=EOA, 1=POLY_PROXY, 2=GNOSIS_SAFE
  signature: string;      // EIP-712 signature
}
```

### Market Data Structure (Gamma API)

Key fields from `/markets`:

```typescript
interface Market {
  id: string;                    // Market ID
  conditionId: string;           // Condition ID for CLOB
  question: string;              // Market question
  slug: string;                  // URL slug
  description: string;           // Market description
  outcomes: string;              // JSON array of outcomes
  outcomePrices: string;         // JSON array of prices
  volume: string;                // Total volume
  volume24hr: number;            // 24h volume
  liquidity: string;             // Liquidity
  category: string;              // Category
  endDate: string;               // Resolution date
  active: boolean;               // Is active
  closed: boolean;               // Is closed
  clobTokenIds: string;          // JSON array of token IDs
  enableOrderBook: boolean;      // CLOB enabled
  orderPriceMinTickSize: number; // Minimum price tick
  orderMinSize: number;          // Minimum order size
  negRisk: boolean;              // Negative risk market
}
```

### Token IDs

Token IDs are unique identifiers for each outcome in a market. Get them from:
- Gamma API `/markets` → `clobTokenIds` field
- Market condition ID can be used to derive token IDs

---

## Rate Limits

All rate limits are enforced using Cloudflare's throttling system. Excess requests are queued rather than rejected.

### General Limits

| Endpoint | Limit | Notes |
|----------|-------|-------|
| General | 15,000 req / 10s | Throttle over max |
| OK Endpoint | 100 req / 10s | Health check limit |

### CLOB API Limits

#### Public Endpoints

| Endpoint | Limit | Notes |
|----------|-------|-------|
| General | 9,000 req / 10s | Throttle over max |
| `/book` | 1,500 req / 10s | Orderbook data |
| `/books` | 500 req / 10s | Batch orderbooks |
| `/price` | 1,500 req / 10s | Price data |
| `/prices` | 500 req / 10s | Batch prices |
| `/midpoint` | 1,500 req / 10s | Midpoint price |
| `/midpoints` | 500 req / 10s | Batch midpoints |

#### Authenticated Endpoints

| Endpoint | Burst Limit | Sustained Limit |
|----------|-------------|-----------------|
| `GET /balance-allowance` | 200 / 10s | - |
| `POST /balance-allowance/update` | 50 / 10s | - |
| `POST /order` | 3,500 / 10s (500/s) | 3,600 / 10 min (60/s) |
| `DELETE /order` | 3,000 / 10s (300/s) | 3,000 / 10 min (50/s) |
| `POST /orders` | 1,000 / 10s (100/s) | 1,500 / 10 min (25/s) |
| `DELETE /orders` | 1,000 / 10s (100/s) | 1,500 / 10 min (25/s) |
| `DELETE /cancel-all` | 250 / 10s (25/s) | 600 / 10 min (10/s) |
| `DELETE /cancel-market-orders` | 1,000 / 10s (100/s) | 1,500 / 10 min (25/s) |
| Ledger (`/orders`, `/trades`) | 900 / 10s | - |
| `/data/orders` | 500 / 10s | - |
| `/data/trades` | 500 / 10s | - |
| `/notifications` | 125 / 10s | - |
| `/auth/api-key*` | 100 / 10s | - |

### Gamma API Limits

| Endpoint | Limit |
|----------|-------|
| General | 4,000 / 10s |
| `/events` | 500 / 10s |
| `/markets` | 300 / 10s |
| Markets listing | 900 / 10s |
| Search | 350 / 10s |
| Tags | 200 / 10s |

### Data API Limits

| Endpoint | Limit |
|----------|-------|
| General | 1,000 / 10s |
| `/trades` | 200 / 10s |
| `/positions` | 150 / 10s |
| `/closed-positions` | 150 / 10s |

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | Success |
| 400 | Bad Request | Invalid parameters, missing fields |
| 401 | Unauthorized | Invalid authentication headers |
| 403 | Forbidden | Geographic restriction, insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Maintenance or outage |

### Common Error Messages

| Error | Description | Solution |
|-------|-------------|----------|
| `Invalid signature` | L1 or L2 signature incorrect | Check signing implementation |
| `Timestamp too old` | POLY_TIMESTAMP expired | Use current timestamp |
| `Insufficient balance` | Not enough USDC or tokens | Check balances |
| `Insufficient allowance` | Token allowance too low | Call `/balance-allowance/update` |
| `Invalid price` | Price doesn't respect tick size | Round to valid tick size |
| `Order too small` | Below minimum size | Increase order size |
| `Market closed` | Market no longer accepting orders | Check market status |
| `Rate limit exceeded` | Too many requests | Implement backoff |

---

## Best Practices

### 1. Authentication Flow

```typescript
// 1. Initialize client with signer only (L1)
const client = new ClobClient(HOST, CHAIN_ID, signer);

// 2. Create or derive API credentials
const apiCreds = await client.createOrDeriveApiKey();

// 3. Reinitialize with full credentials (L2)
const tradingClient = new ClobClient(
  HOST,
  CHAIN_ID,
  signer,
  apiCreds,
  signatureType,  // 0, 1, or 2
  funderAddress   // Your funding address
);
```

### 2. Using Official Clients

**TypeScript:**
```bash
npm install @polymarket/clob-client
```

**Python:**
```bash
pip install py-clob-client
```

### 3. Getting Token IDs

```typescript
// From Gamma API
const markets = await fetch('https://gamma-api.polymarket.com/markets');
const market = markets.data[0];
const tokenIds = JSON.parse(market.clobTokenIds);
```

### 4. Tick Sizes

Always respect the market's tick size:

```typescript
const tickSize = await client.getTickSize(tokenId);
// Round price to nearest tick
const validPrice = Math.round(price / tickSize) * tickSize;
```

### 5. Rate Limiting

- Use batch endpoints (`/books`, `/prices`, `/midpoints`) when fetching multiple markets
- Implement exponential backoff for 429 errors
- Cache tick sizes and negRisk status per token

### 6. EOA Wallet Setup

If using MetaMask or hardware wallet (signatureType=0):

1. Set token allowances before trading:
   ```typescript
   await client.updateBalanceAllowance({
     token_id: tokenId,
     amount: "1000000000" // Large approval
   });
   ```

2. Keep POL tokens for gas fees

### 7. Error Handling

```typescript
try {
  const order = await client.createAndPostOrder(orderArgs, orderOptions);
} catch (error) {
  if (error.status === 429) {
    // Backoff and retry
    await sleep(1000);
  } else if (error.message.includes('insufficient allowance')) {
    // Update allowance
    await client.updateBalanceAllowance(params);
  }
}
```

### 8. Order Validation

Before placing orders:
- Verify `token_id` is valid
- Check `market.active && !market.closed`
- Ensure price is within 0.001 - 0.999 (for binary markets)
- Respect minimum order size

---

## Official Resources

- **TypeScript Client:** https://github.com/Polymarket/clob-client
- **Python Client:** https://github.com/Polymarket/py-clob-client
- **Documentation:** https://docs.polymarket.com
- **Exchange Contract:** https://github.com/Polymarket/ctf-exchange

---

*Last Updated: February 2025*
