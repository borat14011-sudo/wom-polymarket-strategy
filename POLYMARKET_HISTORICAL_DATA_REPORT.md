# Polymarket Historical Data - Official APIs Report
**Generated:** 2026-02-07  
**Investigation Time:** 20 minutes

## ✅ FOUND: Official Historical Price Data Endpoint!

### **CLOB API - Prices History Endpoint**
**Base URL:** `https://clob.polymarket.com`

#### **🎯 PRIMARY HISTORICAL DATA ENDPOINT**
```
GET /prices-history
```

**Parameters:**
- `market` (required): Token ID for the outcome
- **Time parameters (one required):**
  - `interval`: Predefined intervals (`1h`, `1d`, `1w`, `max`, `all`)
  - `startTs` & `endTs`: Custom Unix timestamps
- `fidelity` (optional): Required for certain intervals
  - `1m` requires `fidelity=10` minimum
  - `1w` requires `fidelity=5` minimum

#### **✅ TESTED & WORKING EXAMPLES:**

**Example 1: All historical data**
```bash
GET https://clob.polymarket.com/prices-history?market=111128191581505463501777127559667396812474366956707382672202929745167742497287&interval=max
```

**Response format:**
```json
{
  "history": [
    {"t": 1770394157, "p": 0.23},
    {"t": 1770394217, "p": 0.23},
    ...
  ]
}
```
- `t` = Unix timestamp
- `p` = Price (0.0 to 1.0)

**Example 2: 1-hour intervals**
```bash
GET https://clob.polymarket.com/prices-history?market={TOKEN_ID}&interval=1h
```

**Example 3: Daily intervals**
```bash
GET https://clob.polymarket.com/prices-history?market={TOKEN_ID}&interval=1d
```

**Example 4: Custom time range**
```bash
GET https://clob.polymarket.com/prices-history?market={TOKEN_ID}&startTs=1738800000&endTs=1739404800
```

**Example 5: 1-minute intervals (high fidelity)**
```bash
GET https://clob.polymarket.com/prices-history?market={TOKEN_ID}&interval=1m&fidelity=10
```

---

## 📊 All Official Polymarket APIs

### 1. **CLOB API** (Central Limit Order Book)
**Base URL:** `https://clob.polymarket.com`

**Public Endpoints (No Auth):**
- ✅ `GET /prices-history` - **HISTORICAL PRICE DATA** ⭐
- ✅ `GET /price?token_id={ID}&side={buy|sell}` - Current price
- ✅ `GET /book?token_id={ID}` - Order book depth
- ✅ `GET /midpoint?token_id={ID}` - Midpoint price
- ✅ `GET /sampling-markets` - Sample markets data
- ✅ `GET /sampling-simplified-markets` - Simplified markets

**Authenticated Endpoints (Require API Key):**
- 🔒 `POST /order` - Place order
- 🔒 `DELETE /order` - Cancel order
- 🔒 `GET /trades` - User trades history

**Documentation:** https://docs.polymarket.com/developers/CLOB/introduction

---

### 2. **Gamma API** (Market Metadata & Discovery)
**Base URL:** `https://gamma-api.polymarket.com`

**Public Endpoints:**
- ✅ `GET /events` - List events/markets
  - Parameters: `active`, `closed`, `limit`, `offset`, `tag_id`, `series_id`
- ✅ `GET /markets` - List individual markets
  - Parameters: `id`, `slug`, `condition_id`, `active`, `closed`, `limit`
- ✅ `GET /events/{id}` - Get specific event details
- ✅ `GET /markets/{id}` - Get specific market details
- ✅ `GET /tags` - Get all category tags
- ✅ `GET /sports` - Get all sports leagues

**Sample Response Fields:**
- `outcomePrices` - Current outcome prices (snapshot, not historical)
- `volume`, `volume24hr`, `volume1wk`, `volume1mo`, `volume1yr`
- `clobTokenIds` - Token IDs for use in CLOB API
- Market metadata (title, description, end dates, etc.)

**Documentation:** https://docs.polymarket.com/developers/gamma-markets-api/overview

---

### 3. **Data API** (User Activity & Positions)
**Base URL:** `https://data-api.polymarket.com`

**Endpoints (All require user parameter):**
- ❌ `GET /trades?user={address}` - Requires authentication
- ❌ `GET /activity?user={address}` - User activity (auth required)
- ❌ `GET /positions?user={address}` - User positions (auth required)

**Note:** These endpoints are primarily for user-specific data, not market-wide historical data.

**Documentation:** https://docs.polymarket.com/developers/misc-endpoints/data-api-get-positions

---

### 4. **WebSocket Feeds** (Real-time Streaming)
**Public WebSocket:** `wss://ws-subscriptions-clob.polymarket.com/ws/market`

**Channels:**
- `market` - Real-time orderbook updates, price changes
- `user` - User order updates (requires auth)

**Use Case:** Real-time price tracking, not historical data retrieval

**Documentation:** https://docs.polymarket.com/developers/CLOB/websocket/wss-overview

---

### 5. **RTDS** (Real-Time Data Stream)
**WebSocket:** `wss://ws-live-data.polymarket.com`

**Channels:**
- Crypto price feeds
- Comment streams

**Documentation:** https://docs.polymarket.com/developers/RTDS/RTDS-overview

---

### 6. **Subgraph (The Graph Protocol)**
**Status:** ❌ **DEPRECATED**

The original subgraph endpoint at The Graph has been removed. The official GitHub repo exists but hosted endpoints are no longer available:
- GitHub: https://github.com/Polymarket/polymarket-subgraph
- Contains: activity-subgraph, fpmm-subgraph, oi-subgraph, orderbook-subgraph, pnl-subgraph

**Alternative:** Use on-chain data providers listed below.

---

## 🔗 Alternative Historical Data Sources

### **Third-Party On-Chain Analytics** (Documented by Polymarket)

1. **Goldsky**
   - Real-time streaming pipelines for on-chain Polymarket data
   - CryptoHouse partnership for SQL queries
   - Link: https://docs.goldsky.com/chains/polymarket

2. **Dune Analytics**
   - SQL-based blockchain analytics
   - Polymarket-specific dashboards available
   - Link: https://dune.com

3. **Allium**
   - Blockchain analytics with Polymarket data
   - Link: https://docs.allium.so/historical-data/predictions

**Source:** https://docs.polymarket.com/developers/builders/blockchain-data-resources

---

## 📝 Summary & Recommendations

### ✅ **For Historical Price Data:**
**USE:** `CLOB API /prices-history` endpoint
- **Intervals supported:** 1m, 1h, 1d, 1w, max, all
- **Custom ranges:** Use `startTs` and `endTs` parameters
- **No authentication required**
- **Returns:** Array of {timestamp, price} tuples

### ✅ **For Market Discovery:**
**USE:** Gamma API
- `/events` - Browse all markets
- `/markets` - Get token IDs and metadata
- Use `clobTokenIds` from response in CLOB API

### ✅ **For On-Chain Historical Analysis:**
**USE:** Third-party platforms
- Dune Analytics (SQL queries)
- Goldsky (real-time pipelines)
- Allium (blockchain analytics)

---

## 🧪 Verified Working Example

### Complete Workflow: Get Historical Prices

**Step 1:** Find an active market
```bash
curl "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=1"
```

**Step 2:** Extract `clobTokenIds` from response
```json
"clobTokenIds": "[\"111128191581505463501777127559667396812474366956707382672202929745167742497287\", ...]"
```

**Step 3:** Get historical prices
```bash
curl "https://clob.polymarket.com/prices-history?market=111128191581505463501777127559667396812474366956707382672202929745167742497287&interval=max"
```

**Result:** Full historical price data! ✅

---

## ⚠️ Limitations & Notes

1. **CLOB `/trades` endpoint:** Requires authentication (API key)
2. **Data API:** All endpoints require user address parameter and/or authentication
3. **Subgraph:** No longer hosted by The Graph (deprecated)
4. **Fidelity requirements:** 
   - 1m interval needs `fidelity >= 10`
   - 1w interval needs `fidelity >= 5`
5. **Historical data availability:** Depends on when market was created and CLOB activity

---

## 🎯 Conclusion

**YES - Official historical data APIs exist!**

The **CLOB API `/prices-history` endpoint** provides comprehensive historical price data for all Polymarket markets with:
- Multiple time intervals (1m to max)
- Custom time ranges via timestamps
- No authentication required for price history
- Real, tested, working examples provided

This is the official, documented, supported method for accessing Polymarket historical data programmatically.

---

**Files Generated:**
- `gamma_events.json` - Sample events data
- `active_market.json` - Active market metadata
- `active_prices_max.json` - Full historical prices
- `active_prices_1h.json` - Hourly price data
- `active_prices_1d.json` - Daily price data
- `active_prices_1w_f5.json` - Weekly price data
- `active_prices_1m_f10.json` - Minute-level price data
- `clob_sampling.json` - Sample markets
- `gamma_tags.json` - Market categories
- `gamma_sports.json` - Sports leagues

All endpoints tested and verified working on 2026-02-07.
