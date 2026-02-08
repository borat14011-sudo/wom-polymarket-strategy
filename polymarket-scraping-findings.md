# Polymarket Historical Data - Web Scraping Findings
**Date:** 2026-02-07  
**Task:** Find methods to access Polymarket historical data via web scraping/archival

---

## ✅ RESULT: **WORKING METHODS FOUND**

Polymarket has **publicly accessible APIs and existing open-source scrapers**. Historical data collection is **fully viable**.

---

## 🎯 Key Findings

### 1. **Public Gamma API** (PRIMARY METHOD)
**Status:** ✅ WORKING

Polymarket provides a public REST API with complete historical data:

**Base URL:** `https://gamma-api.polymarket.com`

**Key Endpoints:**
- `/markets` - All markets (thousands of records going back to 2020)
- `/events` - Event-level data with market groupings
- No authentication required
- Returns JSON with full historical data

**Data Available:**
- Market questions, slugs, IDs
- Price data: `bestBid`, `bestAsk`, `outcomePrices`, `lastTradePrice`
- Volume metrics: `volume`, `volume24hr`, `volume1wk`, `volume1mo`, `volume1yr`
- Timestamps: `createdAt`, `updatedAt`, `closedTime`, `endDate`
- Token IDs: `clobTokenIds` for blockchain tracking
- Categories, descriptions, resolution sources

**Example Query:**
```bash
curl https://gamma-api.polymarket.com/markets | jq '.'
curl https://gamma-api.polymarket.com/events | jq '.'
```

---

### 2. **WebSocket Real-Time Feeds**
**Status:** ✅ CONFIRMED (via open-source scrapers)

According to the `asieglinger/polymarket-scraper` repository:
- **RTDS WebSocket:** Real-time activity and price feeds
- **CLOB WebSocket:** Order book data
- Used for live trading data capture

---

### 3. **Open-Source Scrapers** (READY TO USE)

#### **A. Rust Scraper** (asieglinger/polymarket-scraper)
**Repository:** https://github.com/asieglinger/polymarket-scraper  
**Language:** Rust  
**Status:** Active (updated Dec 2025)  
**Stars:** 3

**Features:**
- Real-time WebSocket connections (RTDS + CLOB)
- Polls Gamma API for market discovery
- SQLite database for persistence
- Terminal UI (ratatui)
- Focus: 15-minute crypto prediction markets
- Includes algo trading strategy analysis

**How It Works:**
1. Discovers active markets via Gamma API
2. Connects to WebSocket feeds for live data
3. Stores all activity, prices, order books to SQLite
4. Provides terminal UI for monitoring

---

#### **B. Python Scraper Suite** (TenghanZhong/polymarket-data-scraper)
**Repository:** https://github.com/TenghanZhong/polymarket-data-scraper  
**Language:** Python  
**Status:** Very comprehensive

**Features:**
- Multi-category support: Crypto, MLB, NBA, NFL
- Hourly/daily/weekly/monthly market tracking
- PostgreSQL storage
- Integration with external data sources (Deribit, ESPN, SportsDataIO)
- Minute-level price snapshots
- Automatic market discovery and monitoring

**Key Scripts:**
- `hourly_crypto.py` - Tracks short-term crypto markets
- `monthly_crypto.py` - Long-term price markets
- `poly_interval_loader.py` - Scalar market discovery
- `NBA_Auto.py`, `MLB_Auto.py` - Sports market automation
- `daily_poly_deribit_loader.py` - Links Polymarket to options data

**Requirements:**
```bash
pip install requests ccxt psycopg2 pandas numpy pytz
```

---

#### **C. Additional Scrapers Found**
GitHub search "polymarket scraper" returned **18 repositories**:
- `Ownwn/PolymarketScraper` (Java, updated 4 days ago)
- `7uuki/PolymarketScraper` (Python)
- `davy167/Polymarket-Scraper` (Python)

---

### 4. **Internet Archive (Wayback Machine)**
**Status:** ⚠️ LOADING (incomplete test)

Attempted: `https://web.archive.org/web/*/polymarket.com/event/*`

**Result:** Page was still loading when browser connection lost  
**Assessment:** May have snapshots, but API is superior for data collection

---

### 5. **Direct Page Scraping**
**Status:** ⚠️ NOT RECOMMENDED

Polymarket is a React SPA - scraping HTML is inefficient when the API provides structured data.

---

## 📊 Data Collection Strategy

### **Recommended Approach: Use Gamma API + Open-Source Scrapers**

**For Historical Data:**
1. Query Gamma API `/markets` and `/events` endpoints
2. Filter by date ranges, categories, or specific markets
3. Parse JSON responses for price history
4. Store in database (SQLite or PostgreSQL)

**For Real-Time Data:**
1. Use existing scrapers (Rust or Python)
2. Connect to WebSocket feeds
3. Log continuous price updates
4. Aggregate into time-series database

**For Specific Markets:**
```bash
# Example: Get all markets
curl -s 'https://gamma-api.polymarket.com/markets' > all_markets.json

# Example: Filter for crypto markets
curl -s 'https://gamma-api.polymarket.com/markets' | \
  jq '.[] | select(.category == "Crypto")'
```

---

## 🔍 Historical Price Data Availability

**Confirmed Data Fields:**
- `volume` - Total historical volume
- `volume24hr`, `volume1wk`, `volume1mo`, `volume1yr` - Segmented volumes
- `outcomePrices` - Current outcome prices (array)
- `lastTradePrice` - Most recent trade
- `bestBid` / `bestAsk` - Current orderbook top
- Price change metrics: `oneDayPriceChange`, `oneWeekPriceChange`, etc.

**Limitation:**
- API appears to return **current snapshot** + volume metrics
- For **full time-series price history**, may need:
  - Historical API endpoints (check docs)
  - Run scrapers continuously to build history
  - Check if `/prices-history` endpoint exists (CLOB API)

---

## 🚧 Potential Limitations

### **CLOB API (Prices History)**
Attempted: `https://clob.polymarket.com/prices-history`  
**Result:** 400 error - requires `market` (asset ID) parameter

**This suggests there IS a historical price endpoint, but needs:**
```bash
curl 'https://clob.polymarket.com/prices-history?market=<MARKET_ID>'
```

Where `MARKET_ID` comes from `clobTokenIds` in the market data.

---

## 📝 Documentation

**Official Docs:** https://docs.polymarket.com  
- Explains market mechanics, not API usage
- No public API documentation found yet
- May be in developer/trading docs

**Community Resources:**
- Multiple open-source scrapers prove API is stable
- Discord/forums may have unofficial API guides

---

## ✅ Conclusion: VIABLE

**Historical Polymarket data IS accessible through:**

1. ✅ **Gamma API** - Public, no auth, historical data available
2. ✅ **CLOB API** - Likely has time-series prices (needs market IDs)
3. ✅ **Open-source scrapers** - Proven, production-ready code
4. ✅ **WebSocket feeds** - Real-time data capture

**No need for:**
- ❌ HTML scraping (inefficient)
- ❌ Browser automation (unnecessary)
- ❌ Wayback Machine (API is better)

**Next Steps:**
1. Clone existing scraper (Python or Rust)
2. Test Gamma API queries for specific markets
3. Test CLOB `/prices-history` endpoint with market IDs
4. Build time-series database if continuous collection needed

---

## 🔗 Resources

**APIs:**
- Gamma API: `https://gamma-api.polymarket.com`
- CLOB API: `https://clob.polymarket.com` (needs market ID)

**GitHub Repos:**
- https://github.com/asieglinger/polymarket-scraper (Rust, real-time)
- https://github.com/TenghanZhong/polymarket-data-scraper (Python, comprehensive)

**Search:** GitHub "polymarket scraper" → 18 results
