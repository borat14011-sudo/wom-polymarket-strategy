# Polymarket Complete API Reference

**Investigation Date:** February 6, 2026  
**Status:** Comprehensive reverse engineering completed

## Executive Summary

Polymarket has **5 major API systems** that are publicly accessible:
1. **CLOB API** - Central Limit Order Book (trading, orderbook, prices)
2. **Gamma API** - Market metadata and discovery
3. **Data API** - Historical data, user positions, activity
4. **WebSocket APIs** - Real-time updates (2 types)
5. **GraphQL (Subgraph)** - Blockchain data indexing

## 1. CLOB API (Central Limit Order Book)

**Base URL:** `https://clob.polymarket.com`

### Purpose
Order management, live prices, and orderbook data for trading.

### Key Endpoints

#### Market Data
```bash
GET /markets
# Returns all markets with trading data
# Response: Array of market objects with token IDs, conditions, etc.

GET /sampling-markets
# Returns sampled market data

GET /sampling-simplified-markets?limit=N
# Simplified market list
```

#### Pricing
```bash
GET /price?token_id={TOKEN_ID}&side={BUY|SELL}
# Get current price for a specific token
# Requires: token_id, side (BUY or SELL)

GET /midpoint?token_id={TOKEN_ID}
# Get midpoint price
# Returns: { price: "0.XX" } or error if no orderbook exists

GET /book?token_id={TOKEN_ID}
# Get full orderbook (bids/asks)
```

#### Trading (Requires Authentication)
```bash
POST /order
# Place a new order
# Requires: Authentication headers

DELETE /order
# Cancel an existing order
# Requires: Authentication headers

GET /orders?market={CONDITION_ID}
# Get orders for a market
```

### Example CLOB Request
```bash
curl "https://clob.polymarket.com/markets" | jq '.[0]'
```

### Authentication
CLOB API uses signature-based authentication for write operations (placing/canceling orders). Public read endpoints don't require auth.

**Documentation:** https://docs.polymarket.com/developers/CLOB/authentication

---

## 2. Gamma API (Market Discovery)

**Base URL:** `https://gamma-api.polymarket.com`

### Purpose
Market metadata, event discovery, categorization, and volume tracking.

### Key Endpoints

#### Events
```bash
GET /events?limit={N}&active={true|false}
# List all events (groups of markets)
# Parameters:
#   - limit: Number of results
#   - active: Filter by active status
#   - closed: Filter by closed status
#   - slug: Filter by event slug

GET /events/{event_id}
# Get specific event details

GET /events?slug={SLUG}
# Search events by slug
# Example: slug=us-strikes-iran-by
```

#### Markets
```bash
GET /markets?limit={N}&active={true|false}&closed={false}
# List markets
# Parameters:
#   - limit: Number of results  
#   - active: Active markets only
#   - closed: Include/exclude closed markets
#   - offset: Pagination offset

GET /markets/{market_id}
# Get specific market details
```

### Real-World Example: Finding Iran Strike Markets

```bash
curl "https://gamma-api.polymarket.com/events?slug=us-strikes-iran-by"
```

**Response Structure:**
```json
{
  "id": "114242",
  "ticker": "us-strikes-iran-by",
  "slug": "us-strikes-iran-by", 
  "title": "US strikes Iran by...?",
  "description": "Market description...",
  "active": true,
  "closed": false,
  "featured": true,
  "restricted": true,
  "liquidity": 1026328.18,
  "volume": 185353887.73,
  "volume24hr": 6536348.40,
  "markets": [
    {
      "id": "1294628",
      "question": "US strikes Iran by February 5, 2026?",
      "conditionId": "0x3bed62b...",
      "slug": "us-strikes-iran-by-february-5-2026",
      "endDate": "2026-02-05T00:00:00Z",
      "volume": "4461531.49",
      "active": true,
      "closed": true,
      "clobTokenIds": ["29763...", "36321..."]
    }
  ],
  "tags": [
    {"label": "Geopolitics", "slug": "geopolitics"},
    {"label": "Iran", "slug": "iran"}
  ]
}
```

### Why Iran Markets ARE Accessible

The Iran strike markets **ARE showing in active markets** - they're just grouped under an event structure. Each event (like "US strikes Iran by...?") contains multiple individual markets for different dates.

**Key Finding:** Markets may appear "missing" if you search individual `/markets` endpoint, but they're accessible via:
1. Event-level queries: `/events?slug=us-strikes-iran-by`
2. Direct market queries: `/markets?condition_id={ID}`
3. Searching with proper filters (active=true, etc.)

---

## 3. Data API (Historical & User Data)

**Base URL:** `https://data-api.polymarket.com`

### Purpose
Historical price data, user positions, trading activity, and analytics.

### Key Endpoints

#### Historical Prices
```bash
GET /prices?market={CONDITION_ID}&interval={INTERVAL}&startTs={UNIX}&endTs={UNIX}
# Get historical price data
# Parameters:
#   - market: Market condition ID
#   - interval: 1m, 5m, 1h, 1d, max
#   - startTs: Start timestamp (Unix)
#   - endTs: End timestamp (Unix)

# Example:
curl "https://data-api.polymarket.com/prices?market=0x64b14a09a6cf9dc02b840bc83f4dcfd41ca6108544c47ecabc6e5d00bc15fd2e&interval=max"
```

#### User Data
```bash
GET /positions?user={ADDRESS}
# Get user's current positions

GET /activity?user={ADDRESS}
# Get user's trading activity

GET /trades?market={CONDITION_ID}
# Get trade history for a market
```

### Working Example
```bash
# Get daily price history for a market
curl "https://data-api.polymarket.com/prices?market=0x64b14a09a6cf9dc02b840bc83f4dcfd41ca6108544c47ecabc6e5d00bc15fd2e&interval=1d&startTs=1704067200&endTs=1735689600"
```

---

## 4. WebSocket APIs (Real-Time Data)

Polymarket has **TWO separate WebSocket services**:

### 4A. CLOB WebSocket (Orderbook Updates)

**URL:** `wss://ws-subscriptions-clob.polymarket.com/ws/`

**Purpose:** Real-time orderbook updates, order status, and market data.

#### Channels
- **market**: Public orderbook and price updates
- **user**: Authenticated user order status updates

#### Subscription Message
```json
{
  "auth": {
    // Authentication data (for user channel)
  },
  "markets": ["CONDITION_ID_1", "CONDITION_ID_2"],
  "assets_ids": ["TOKEN_ID_1", "TOKEN_ID_2"],
  "type": "MARKET",  // or "USER"
  "custom_feature_enabled": false
}
```

#### Subscribe/Unsubscribe
```json
{
  "assets_ids": ["TOKEN_ID"],
  "operation": "subscribe"  // or "unsubscribe"
}
```

**Documentation:** https://docs.polymarket.com/developers/CLOB/websocket/wss-overview

### 4B. RTDS (Real-Time Data Stream)

**URL:** `wss://ws-live-data.polymarket.com`

**Purpose:** Low-latency crypto price feeds and comment streams.

#### Available Topics
- **crypto_prices**: Real-time cryptocurrency prices
- **comments**: Comment events and reactions

#### Message Structure
```json
{
  "topic": "crypto_prices",
  "type": "update",
  "timestamp": 1707268800000,
  "payload": {
    // Topic-specific data
  }
}
```

#### Subscription
```json
{
  "action": "subscribe",
  "subscriptions": [
    {
      "topic": "crypto_prices",
      "type": "update",
      "filters": "BTC",
      "gamma_auth": {
        "address": "0x..."
      }
    }
  ]
}
```

#### Heartbeat
Send PING messages every ~5 seconds to maintain connection.

**Documentation:** https://docs.polymarket.com/developers/RTDS/RTDS-overview

---

## 5. GraphQL API (Subgraph)

**Type:** The Graph Protocol Subgraph  
**Purpose:** Blockchain data indexing with GraphQL queries

### Subgraph Endpoints

Polymarket maintains multiple subgraphs for different data:

1. **polymarket-subgraph** - Main market data
2. **activity-subgraph** - Trading activity
3. **fpmm-subgraph** - Fixed Product Market Maker data
4. **oi-subgraph** - Open interest
5. **orderbook-subgraph** - Order book data
6. **pnl-subgraph** - Profit/Loss tracking
7. **sports-oracle-subgraph** - Sports market oracle

### Source Code
**GitHub:** https://github.com/Polymarket/polymarket-subgraph

### Example Schema Queries

```graphql
query TokenIdConditions {
  tokenIdConditions {
    id
    condition
    complement
  }
}

query Markets {
  markets(first: 10) {
    id
    question
    outcomes
    volume
    liquidity
  }
}

query UserPositions {
  user(id: "0x...") {
    positions {
      market {
        question
      }
      amount
    }
  }
}
```

### Hosting Options
- Self-hosted via The Graph Node
- Goldsky deployment
- Public hosted endpoints (if available)

**Note:** The exact public GraphQL endpoint URL may vary. Check official documentation or deploy your own instance.

---

## API Rate Limits

**Reference:** https://docs.polymarket.com/quickstart/introduction/rate-limits

- Public endpoints have rate limiting
- Authenticated users may have higher limits
- Consider implementing exponential backoff for production use

---

## Complete Endpoint Summary Table

| API | Base URL | Purpose | Auth Required | Real-time |
|-----|----------|---------|---------------|-----------|
| CLOB | https://clob.polymarket.com | Trading, orderbook, prices | Trading only | No |
| Gamma | https://gamma-api.polymarket.com | Market discovery, metadata | No | No |
| Data | https://data-api.polymarket.com | Historical data, positions | No | No |
| CLOB WS | wss://ws-subscriptions-clob.polymarket.com/ws/ | Live orderbook updates | User channel only | Yes |
| RTDS WS | wss://ws-live-data.polymarket.com | Crypto prices, comments | Some topics | Yes |
| Subgraph | Various/Self-hosted | Blockchain data via GraphQL | No | Near real-time |

---

## Working Code Examples

### 1. Get Iran Strike Event with All Markets

```bash
curl -s "https://gamma-api.polymarket.com/events?slug=us-strikes-iran-by" | jq '.'
```

### 2. Get Active Markets Only

```bash
curl -s "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=10" | jq '.[] | {id, question, volume}'
```

### 3. Get Historical Prices

```bash
curl -s "https://data-api.polymarket.com/prices?market=0x3bed62b0b7e3eb52c1f0d8a5d11edad1f74989038fc1cae2889cdbe96a248dfe&interval=max" | jq '.'
```

### 4. Get Current Price from CLOB

```bash
# Note: Requires valid token_id from an active market
curl -s "https://clob.polymarket.com/midpoint?token_id=29763725280755533853228704213586000655160583839125347030858041807759211842058"
```

### 5. Check Data API Health

```bash
curl -s "https://data-api.polymarket.com/" 
# Returns: {"data":"OK"}
```

---

## Why Iran Markets Weren't Initially Found

The investigation revealed that Iran strike markets **ARE accessible**, but appeared missing due to:

1. **Event-based structure**: Markets are grouped under events, not always individually listed
2. **Filtering requirements**: Need `active=true` or search by event slug
3. **Date-based markets**: Each date has a separate market within the parent event
4. **Closed markets**: Many Iran strike markets already closed (past dates) - need to include closed=true or search at event level

**Solution:** Always search via event slug or parent event ID to see all related markets:
```bash
curl "https://gamma-api.polymarket.com/events?slug=us-strikes-iran-by"
```

---

## Additional Resources

### Official Documentation
- Main docs: https://docs.polymarket.com
- CLOB API: https://docs.polymarket.com/developers/CLOB/introduction
- Gamma API: https://docs.polymarket.com/developers/gamma-markets-api/overview
- WebSocket: https://docs.polymarket.com/developers/CLOB/websocket/wss-overview
- Endpoints reference: https://docs.polymarket.com/quickstart/reference/endpoints

### GitHub Repositories
- CLOB Client (TypeScript): https://github.com/Polymarket/clob-client
- CLOB Client (Python): https://github.com/Polymarket/py-clob-client
- Subgraph: https://github.com/Polymarket/polymarket-subgraph
- CTF Exchange: https://github.com/Polymarket/ctf-exchange
- AI Agents: https://github.com/Polymarket/agents

### Smart Contracts
- Conditional Tokens: https://github.com/gnosis/conditional-tokens-contracts
- Market Makers: https://github.com/gnosis/conditional-tokens-market-makers
- Neg-Risk Adapter: https://github.com/Polymarket/neg-risk-ctf-adapter

---

## Key Technical Details

### Token ID Structure
- Markets use `conditionId` (condition identifier)
- Each outcome has a `token_id` (ERC-1155 token)
- CLOB operations use token IDs
- Gamma uses condition IDs

### Data Flow
1. **Gamma API** → Discover markets and get metadata
2. **CLOB API** → Get live prices and orderbook
3. **Data API** → Get historical prices and analytics
4. **WebSocket** → Subscribe to real-time updates
5. **Subgraph** → Query blockchain data and complex aggregations

### Market States
- `active: true` - Market is live and trading
- `closed: true` - Market closed, no more trading
- `archived: true` - Market archived
- `resolved: true` - Market has been resolved with outcome

---

## Conclusion

Polymarket has a **comprehensive and well-structured API surface** with:
- ✅ REST APIs (CLOB, Gamma, Data)
- ✅ WebSocket feeds (CLOB WS, RTDS)
- ✅ GraphQL via Subgraph
- ✅ Historical data endpoints
- ✅ Real-time price feeds

**All Iran strike markets are fully accessible** via the Gamma API using event-based queries.

**Last Updated:** February 6, 2026  
**Investigated By:** Subagent polymarket-api-reverse-engineer
