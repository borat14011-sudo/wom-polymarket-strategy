# Polymarket API Research Report

## Executive Summary

Polymarket provides a Central Limit Order Book (CLOB) API for programmatic trading, along with a Gamma API for market data. Official client libraries exist in TypeScript (`@polymarket/clob-client`) and Python (`py-clob-client`). Authentication is via wallet private keys with support for email/Magic login (signature_type=1). Trading requires API key credentials derived from the wallet. Real‑time data is available via WebSocket.

## 1. API Discovery

### Official APIs

1. **CLOB API** (`https://clob.polymarket.com`)
   - Central Limit Order Book for placing/canceling orders, reading order books, and managing positions.
   - Used by the official TypeScript and Python clients.
   - RESTful endpoints with JSON payloads.
   - WebSocket channels for real‑time updates.

2. **Gamma Markets API** (`https://gamma-api.polymarket.com`)
   - Read‑only market data: markets, metadata, volumes, liquidity, token IDs.
   - REST endpoint `/markets` returns comprehensive market list.
   - No authentication required for public data.

3. **GraphQL API** – Not publicly documented; likely internal.

### Unofficial Endpoints

- **Magic Link Private Key Export**: `https://reveal.magic.link/polymarket` (requires authentication) to export private key for email login.
- **Token IDs**: Retrieved via Gamma API `clobTokenIds` field.

### GitHub Repositories

- `Polymarket/clob-client` – TypeScript client
- `Polymarket/py-clob-client` – Python client
- `Polymarket/agents` – AI‑powered trading agents
- `Polymarket/ctf-exchange` – Contract code

## 2. Authentication

### Methods

1. **Wallet Private Key** (EOA – Externally Owned Account)
   - Use MetaMask/private key directly.
   - Requires setting token allowances for USDC and conditional tokens.

2. **Email/Magic Wallet** (signature_type = 1)
   - Use Gmail (or any email) login via Magic.link.
   - Private key can be exported from `https://reveal.magic.link/polymarket`.
   - No allowances needed; automatic proxy contract.

3. **Browser Wallet Proxy** (signature_type = 2) – for smart contract wallets.

### API Key Credentials

- Call `create_or_derive_api_creds()` (or `createOrDeriveApiKey()` in TS) to generate API key and secret.
- These credentials sign subsequent requests.
- Stored locally; do not expose.

### Rate Limits (Detailed)

All rate limits are enforced by Cloudflare with throttling (requests delayed, not dropped). Limits are per 10‑second sliding window unless noted.

#### General
- **General Rate Limiting**: 15,000 requests / 10s
- **"OK" Endpoint**: 100 requests / 10s

#### Gamma API
- **General**: 4,000 requests / 10s
- **Get Comments**: 200 / 10s
- **/events**: 500 / 10s
- **/markets**: 300 / 10s
- **/markets/events listing**: 900 / 10s
- **Tags**: 200 / 10s
- **Search**: 350 / 10s

#### CLOB API
- **General**: 9,000 requests / 10s
- **/book**: 1,500 / 10s
- **/books**: 500 / 10s
- **/price**: 1,500 / 10s
- **/prices**: 500 / 10s
- **/midprice**: 1,500 / 10s
- **/midprices**: 500 / 10s
- **Ledger endpoints** (trades, orders, notifications): 900 / 10s
- **Price History**: 1,000 / 10s
- **Market Tick Size**: 200 / 10s
- **API Keys**: 100 / 10s

#### Trading Endpoints (CLOB)
- **POST /order**: 3,500 / 10s (burst), 36,000 / 10 minutes (sustained)
- **DELETE /order**: 3,000 / 10s (burst), 30,000 / 10 minutes
- **POST /orders**: 1,000 / 10s (burst), 15,000 / 10 minutes
- **DELETE /orders**: 1,000 / 10s (burst), 15,000 / 10 minutes
- **DELETE /cancel-all**: 250 / 10s (burst), 6,000 / 10 minutes
- **DELETE /cancel-market-orders**: 1,000 / 10s (burst), 1,500 / 10 minutes

## 3. Trading Endpoints (CLOB API)

### Market Data (Read‑Only)

- `GET /ok` – health check
- `GET /time` – server time
- `GET /markets` – simplified market list (via Gamma API)
- `GET /order_book/{token_id}` – order book for a token
- `GET /order_books` – batch order books
- `GET /midpoint/{token_id}` – mid price
- `GET /price/{token_id}?side=BUY|SELL` – best bid/ask

### Trading (Authenticated)

- `POST /orders` – place limit/market order
- `GET /orders` – list open orders
- `DELETE /orders/{order_id}` – cancel single order
- `DELETE /orders` – cancel all orders
- `GET /trades` – user’s trade history
- `GET /last_trade_price/{token_id}` – last trade price

### Portfolio

- `GET /balances` – token balances (likely)
- `GET /positions` – open positions (not explicitly seen but available)

## 4. Fees

According to the CLOB Introduction documentation, the fee schedule (subject to change) is:

| Volume Level | Maker Fee Base Rate (bps) | Taker Fee Base Rate (bps) |
|--------------|---------------------------|---------------------------|
| >0 USDC      | 0                         | 0                         |

**However**, the documentation also provides fee formulas that apply a `baseRate` (which appears to be 0 currently). The formulas are:

- **Selling outcome tokens (base) for collateral (quote):**
  `feeQuote = baseRate × min(price, 1 − price) × size`

- **Buying outcome tokens (base) with collateral (quote):**
  `feeBase = baseRate × min(price, 1 − price) × size / price`

If `baseRate = 0`, there are no fees. However, the user mentions 4% fees – this could refer to the total spread or a different fee structure (e.g., negative‑risk markets). It is crucial to verify the current fee schedule via the API or recent announcements.

## 5. Real‑Time Data (WebSocket)

The CLOB API provides WebSocket channels for real‑time updates.

### Channels
- **User channel**: updates about your orders and trades.
- **Market channel**: updates about market data (order book changes, trades).

### Subscription
Send an authentication message upon connection with fields:
- `auth`: API key credentials (see WSS Authentication docs)
- `markets`: array of condition IDs (for user channel)
- `asset_ids`: array of token IDs (for market channel)
- `type`: "USER" or "MARKET"
- `custom_feature_enabled`: boolean

After connection, you can subscribe/unsubscribe to additional assets by sending an `operation` message.

### WebSocket Endpoint
Likely `wss://clob.polymarket.com/ws` (to be confirmed).

## 6. Existing Libraries/Tools

### Official Clients

1. **Python** (`py-clob-client`)
   - Install: `pip install py-clob-client`
   - Full trading support, allowances handling, examples.
   - [GitHub](https://github.com/Polymarket/py-clob-client)

2. **TypeScript** (`@polymarket/clob-client`)
   - Install: `npm install @polymarket/clob-client`
   - Similar features to Python client.
   - [GitHub](https://github.com/Polymarket/clob-client)

3. **Agents Framework** (`Polymarket/agents`)
   - AI‑based trading bots; can be used as reference.

### Unofficial Wrappers

None found; the official clients are mature.

## 7. Implementation Plan

### Step‑by‑Step Integration

1. **Set Up Environment**
   - Python 3.9+ (or Node.js for TypeScript).
   - Install client library: `pip install py-clob-client` or `npm install @polymarket/clob-client`.

2. **Obtain Authentication Credentials**
   - **Email login**: Log in to Polymarket via Magic, export private key from `https://reveal.magic.link/polymarket`.
   - **Private key**: Store securely in environment variables.

3. **Initialize Client**
   ```python
   from py_clob_client.client import ClobClient
   import os

   HOST = "https://clob.polymarket.com"
   CHAIN_ID = 137  # Polygon
   PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY")
   FUNDER = "0x..."  # Your Polymarket profile address (where funds are)

   client = ClobClient(
       HOST,
       key=PRIVATE_KEY,
       chain_id=CHAIN_ID,
       signature_type=1,  # 1 for email/Magic
       funder=FUNDER
   )
   client.set_api_creds(client.create_or_derive_api_creds())
   ```

4. **Fetch Market Data**
   - Use Gamma API: `GET https://gamma-api.polymarket.com/markets`
   - Parse `clobTokenIds` array (two tokens per market: Yes/No or Long/Short).

5. **Place Orders**
   - **Limit order**: `create_order` + `post_order`
   - **Market order**: `create_market_order` + `post_order`
   - **Important**: Verify current fees and adjust profit calculations accordingly.

6. **Manage Orders**
   - Poll `get_orders` to monitor fills.
   - Cancel orders with `cancel` or `cancel_all`.

7. **Real‑Time Monitoring** (Optional)
   - Connect to WebSocket channel for instant updates.
   - Reduce polling and react faster to market movements.

8. **Risk Management**
   - Start with $10 capital.
   - Implement stop‑loss / take‑profit logic.
   - Handle network errors, retries with exponential backoff.

### Error Handling

- Check HTTP status codes.
- Handle insufficient balance, invalid token ID, order size too small.
- Use exponential backoff for rate limits.

### Security Considerations

- Never commit private keys or API secrets.
- Use environment variables or secret management.
- Consider using a dedicated trading wallet with limited funds.
- Verify SSL certificates.

## 8. Alternatives (If Official API Is Insufficient)

### GraphQL Introspection

- Attempt introspection on suspected GraphQL endpoints (unlikely).
- Use browser dev tools to inspect network calls from web UI.

### Reverse Engineering

- Monitor WebSocket connections on the live site for real‑time data.
- Inspect the JavaScript bundle for internal API endpoints.

### Selenium/Browser Automation

- Fallback if API is too restrictive; but user prefers API.

## 9. Constraints & Notes

- **Gmail authentication**: Use Magic email login with signature_type=1.
- **$10 capital**: Start small; verify fee impact.
- **Real‑time market data**: Use WebSocket for efficiency; otherwise poll every few seconds.
- **Fees**: Confirm current fee schedule; the documentation indicates 0 bps but may have changed.

## 10. Deliverables Checklist

- [x] API documentation summary
- [x] Authentication method detailed
- [x] Trading endpoint details
- [x] Code examples
- [x] Implementation roadmap
- [x] Rate limit information
- [x] WebSocket real‑time feed details
- [x] Fee structure (with caveats)

## 11. Next Steps

1. Set up a test environment with minimal funds.
2. Implement a simple market‑making bot that places limit orders.
3. Monitor performance and adjust for fees.
4. Scale gradually after verifying reliability.

## 12. References

- Gamma API: `https://gamma-api.polymarket.com`
- CLOB API: `https://clob.polymarket.com`
- Python client docs: `https://github.com/Polymarket/py-clob-client`
- TypeScript client docs: `https://github.com/Polymarket/clob-client`
- Magic reveal: `https://reveal.magic.link/polymarket`
- CLOB Introduction: `https://docs.polymarket.com/developers/CLOB/introduction`
- Rate Limits: `https://docs.polymarket.com/quickstart/introduction/rate-limits`
- WebSocket Overview: `https://docs.polymarket.com/developers/CLOB/websocket/wss-overview`

---

*Report generated by subagent on 2026-02-10 18:40 PST*