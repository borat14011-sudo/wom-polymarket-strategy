# Polymarket Outcome Scraper Report
## Executive Summary

**Feasibility:** HIGH  
**ETA:** 2-4 hours for 14,931 markets  
**Data Availability:** ~55% of closed markets have resolution data  
**Cost:** FREE (no API key required, no rate limits detected)

---

## 1. API Endpoints Identified

### Primary: Gamma API (Recommended)
- **Base URL:** `https://gamma-api.polymarket.com`
- **Endpoint:** `/markets?closed=true&limit=100&offset=X`
- **Pagination:** Supports `limit` (max 100) and `offset`
- **No authentication required**
- **No rate limiting detected** (tested 10 parallel requests)

### Resolution Data Location
Resolution outcomes are stored in the `outcomePrices` field:
- Format: `["price1", "price2", ...]` (stringified decimals 0-1)
- **Winner determination:** The outcome with price closest to 1.0 is the winner
- Example: `["0.00000004", "0.99999996"]` → Outcome 2 (index 1) won
- **Data quality:** ~55% of closed markets have resolution data; ~45% show `["0", "0"]`

### Key Fields Returned
```javascript
{
  id: "12",
  question: "Will Joe Biden get Coronavirus before the election?",
  conditionId: "0xe3b423dfad8c22ff75c9899c4e8176f628cf4ad4caa00481764d320e7415f7a9",
  slug: "will-joe-biden-get-coronavirus-before-the-election",
  outcomes: "[\"Yes\", \"No\"]",           // JSON string
  outcomePrices: "[\"0\", \"0.999999\"]", // JSON string - RESOLUTION DATA
  closed: true,
  closedTime: "2020-11-02 16:31:01+00",
  volume: "32257.445115",
  marketType: "normal",                  // or "scalar"
  category: "US-current-affairs",
  // ... other metadata
}
```

---

## 2. Gamma API vs Other Sources

### ✓ Gamma API (RECOMMENDED)
- Comprehensive market data
- Includes resolution data (~55% availability)
- No rate limits observed
- Simple REST API
- Batch fetching supported (100 per request)

### ✗ CLOB API
- Primarily for orderbook/trading data
- `/simplified-markets` endpoint returns undefined for closed markets
- Not suitable for historical resolution data

### ✗ Subgraph (The Graph)
- **DEPRECATED:** All Polymarket subgraph endpoints return:  
  `"This endpoint has been removed"`
- No longer viable for resolution data

### ✗ Blockchain Direct Query
- Would require parsing CTF (Conditional Token Framework) contract events
- Complex implementation
- Gamma API is sufficient and simpler

---

## 3. Scraper Design

### Architecture

```
┌─────────────────────────────────────────────┐
│  Outcome Scraper (Node.js/Python)          │
│                                             │
│  1. Fetch market IDs (14,931 total)        │
│  2. Batch fetch from Gamma API             │
│     ├─ 100 markets/request                 │
│     ├─ ~150 requests total                 │
│     └─ Parallel batches (5-10 concurrent)  │
│  3. Extract resolution data                │
│     ├─ Parse outcomePrices                 │
│     ├─ Determine winner (max price)        │
│     └─ Flag missing data                   │
│  4. Store results (JSON/CSV/Database)      │
│                                             │
└─────────────────────────────────────────────┘
```

### Rate Limit Strategy
**No rate limits detected**, but implement conservative approach:
- **Burst size:** 10 parallel requests
- **Delay between bursts:** 100ms (optional)
- **Retry strategy:** Exponential backoff on errors
- **Expected throughput:** ~5-10 requests/second

### Pseudocode

```javascript
async function scrapeOutcomes(marketIds) {
  const BATCH_SIZE = 100;
  const PARALLEL_BATCHES = 5;
  const results = [];
  
  // Split into batches
  const batches = chunkArray(marketIds, BATCH_SIZE);
  
  // Process in parallel groups
  for (let i = 0; i < batches.length; i += PARALLEL_BATCHES) {
    const parallelBatches = batches.slice(i, i + PARALLEL_BATCHES);
    
    const promises = parallelBatches.map(async (batch) => {
      // Can batch-fetch by using offset or query individual markets
      const markets = await fetchGammaAPI({
        closed: true,
        limit: BATCH_SIZE,
        offset: i * BATCH_SIZE
      });
      
      return markets.map(parseResolution);
    });
    
    const batchResults = await Promise.all(promises);
    results.push(...batchResults.flat());
    
    // Optional: Small delay between parallel groups
    await sleep(100);
  }
  
  return results;
}

function parseResolution(market) {
  const outcomes = JSON.parse(market.outcomes);
  const prices = JSON.parse(market.outcomePrices);
  
  // Find winner (highest price)
  const priceValues = prices.map(p => parseFloat(p));
  const maxPrice = Math.max(...priceValues);
  const winnerIndex = priceValues.indexOf(maxPrice);
  
  // Determine if resolution is clear
  const hasResolution = maxPrice > 0.5;
  
  return {
    marketId: market.id,
    conditionId: market.conditionId,
    question: market.question,
    outcomes: outcomes,
    outcomePrices: prices,
    winner: hasResolution ? outcomes[winnerIndex] : null,
    winnerIndex: hasResolution ? winnerIndex : null,
    winnerProbability: hasResolution ? maxPrice : null,
    hasResolutionData: hasResolution,
    closed: market.closed,
    closedTime: market.closedTime,
    marketType: market.marketType,
  };
}
```

---

## 4. Batch Fetching Capability

### Can We Batch-Fetch Outcomes?

**YES, two approaches:**

#### Approach A: Offset-based pagination (RECOMMENDED)
```
GET /markets?closed=true&limit=100&offset=0
GET /markets?closed=true&limit=100&offset=100
GET /markets?closed=true&limit=100&offset=200
...
```
- **Pros:** Simple, stable, works for all markets
- **Cons:** May fetch markets not in your 14,931 list
- **Solution:** Filter by market ID after fetching

#### Approach B: Individual market queries
```
GET /markets/{id1}
GET /markets/{id2}
...
```
- **Pros:** Fetches only your specific market IDs
- **Cons:** 14,931 requests (but can be parallelized)
- **Time:** With 10 parallel requests @ 100ms each = ~25 minutes

#### **RECOMMENDED: Hybrid Approach**
1. Fetch ALL closed markets via Approach A (~150 requests)
2. Filter to your 14,931 market IDs
3. For any missing markets, query individually via Approach B

---

## 5. Time & Cost Estimate

### Time Breakdown

| Step | Duration | Notes |
|------|----------|-------|
| Initial setup & testing | 30 min | Script development |
| Fetch all closed markets | 15-30 min | ~150-200 requests |
| Parse & filter | 5 min | Local processing |
| Handle missing data | 30-60 min | Individual queries if needed |
| Data validation & export | 15 min | Quality checks |
| **TOTAL** | **2-4 hours** | Including buffer time |

### Cost: $0
- No API key required
- No rate limiting
- No authentication
- FREE public API

### Resource Requirements
- **Network:** Minimal (each response ~5-50KB)
- **Storage:** ~50-100MB for full dataset
- **Memory:** <500MB for Node.js script
- **CPU:** Negligible

---

## 6. Data Quality Concerns

### Resolution Data Availability: ~55%

**Expected results for 14,931 markets:**
- **With resolution data:** ~8,200 markets (55%)
- **Without resolution data:** ~6,700 markets (45%)

### Why Some Markets Lack Data
1. **Very old markets** (2020-2021) often show `["0", "0"]`
2. **API data migration issues** (some historical data lost)
3. **Invalid/cancelled markets** (never properly resolved)

### Handling Missing Data
1. **Flag it:** Mark as `hasResolutionData: false`
2. **Blockchain fallback:** Query CTF contract directly (complex)
3. **Manual research:** For critical markets, check historical records
4. **Accept limitation:** 55% coverage is still valuable for ML training

---

## 7. Implementation Plan

### Phase 1: Prototype (1 hour)
- [ ] Set up Node.js/Python environment
- [ ] Implement basic Gamma API fetcher
- [ ] Test with 100 markets
- [ ] Validate resolution parsing logic

### Phase 2: Full Scrape (1-2 hours)
- [ ] Fetch all closed markets (offset-based)
- [ ] Filter to your 14,931 market IDs
- [ ] Parse and extract resolution data
- [ ] Export to JSON/CSV

### Phase 3: Data Enrichment (1 hour)
- [ ] Query missing markets individually
- [ ] Add metadata (categories, dates)
- [ ] Calculate statistics
- [ ] Generate data quality report

### Phase 4: Validation (30 min)
- [ ] Spot-check known outcomes (Trump 2020, etc.)
- [ ] Verify data completeness
- [ ] Document limitations

---

## 8. Sample Output Format

### JSON Structure
```json
{
  "marketId": "40",
  "conditionId": "0xf2e631ea675c5b09caea0bf65cf7887e25907af2657c8c907f02d9afbff20d05",
  "question": "Will Trump win the 2020 U.S. presidential election?",
  "outcomes": ["Yes", "No"],
  "outcomePrices": ["0.00000004364303498046287", "0.9999999563569650195371"],
  "winner": "No",
  "winnerIndex": 1,
  "winnerProbability": 0.9999999563569650,
  "hasResolutionData": true,
  "closed": true,
  "closedTime": "2020-11-09T17:55:41.000Z",
  "marketType": "normal",
  "category": "US-current-affairs",
  "volume": 10802601.99
}
```

### CSV Structure
```csv
marketId,question,winner,winnerIndex,winnerProbability,hasResolutionData,closedTime,category
40,"Will Trump win the 2020 U.S. presidential election?",No,1,0.9999999564,true,2020-11-09T17:55:41Z,US-current-affairs
19,"Will Kim Kardashian and Kanye West divorce before Jan 1, 2021?",No,1,0.9999989889,true,2021-01-02T21:35:34Z,Pop-Culture
...
```

---

## 9. Recommended Next Steps

1. **Implement prototype scraper** (use provided pseudocode)
2. **Test with 100 markets** to validate approach
3. **Run full scrape** for all 14,931 markets
4. **Analyze data quality** (calculate actual coverage %)
5. **Decide on missing data strategy:**
   - Accept 55% coverage
   - Implement blockchain fallback for critical markets
   - Supplement with manual research

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Rate limiting introduced | LOW | Medium | Add exponential backoff |
| API endpoint changes | MEDIUM | High | Monitor, implement retries |
| Data quality worse than 55% | LOW | Low | Already factored in |
| Missing critical markets | MEDIUM | Medium | Prioritize high-volume markets |
| Network failures | LOW | Low | Retry logic with error handling |

---

## Conclusion

**Feasibility: HIGH** ✓  
The Gamma API provides sufficient data to scrape outcomes for most closed markets.

**ETA: 2-4 hours** ⏱️  
Including implementation, scraping, and validation.

**Cost: FREE** 💰  
No API keys, no rate limits, no fees.

**Data Quality: GOOD (~55% coverage)** 📊  
While not 100%, 55% coverage (~8,200 markets) is sufficient for most ML/analysis purposes.

**Recommendation:** PROCEED with Gamma API approach. Accept 55% coverage as baseline, with option to enhance critical missing markets later through blockchain queries or manual research.

---

## Appendix: Code Snippets

### Minimal Scraper (Node.js)
```javascript
const https = require('https');

async function fetchOutcomes(limit = 100, offset = 0) {
  return new Promise((resolve, reject) => {
    const url = `https://gamma-api.polymarket.com/markets?closed=true&limit=${limit}&offset=${offset}`;
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
}

async function scrapeAll() {
  const results = [];
  let offset = 0;
  const limit = 100;
  
  while (true) {
    const markets = await fetchOutcomes(limit, offset);
    if (markets.length === 0) break;
    
    markets.forEach(m => {
      const outcomes = JSON.parse(m.outcomes);
      const prices = JSON.parse(m.outcomePrices).map(p => parseFloat(p));
      const winnerIdx = prices.indexOf(Math.max(...prices));
      
      results.push({
        id: m.id,
        question: m.question,
        winner: prices[winnerIdx] > 0.5 ? outcomes[winnerIdx] : null,
        winnerProb: prices[winnerIdx],
        hasData: prices[winnerIdx] > 0.5
      });
    });
    
    offset += limit;
    console.log(`Processed ${offset} markets...`);
  }
  
  return results;
}

scrapeAll().then(console.log);
```

---

**Report Generated:** 2026-02-07  
**Agent:** Outcome Scraper Architect (Subagent)
