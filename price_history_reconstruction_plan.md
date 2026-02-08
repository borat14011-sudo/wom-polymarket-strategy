# Price History Reconstruction Plan
## Resolved Markets (Oct 2025 - Feb 2026)

### Objective
Reconstruct complete price histories for all resolved markets from October 2025 through February 2026 to enable accurate backtesting and trade replay.

### Output Format
CSV file: `price_history.csv` with columns:
- `market_id` - Polymarket market ID
- `timestamp` - Unix timestamp or ISO 8601 datetime
- `yes_price` - YES probability (0-1)
- `volume` - 24-hour trading volume

### Data Collection Methods

#### Method 1: Wayback Machine Snapshots
**Target**: Polymarket market pages archived by Internet Archive
**Approach**:
1. Use Wayback Machine CDX API to find snapshots
2. For each market, query: `http://web.archive.org/cdx/search/cdx?url=polymarket.com/event/{slug}&output=json&from=20251001&to=20260228`
3. Download HTML snapshots for each timestamp
4. Parse JSON data from embedded script tags (market data is often in `__NEXT_DATA__` or API responses)
5. Extract price, volume, timestamp

**Pros**: Official snapshots, reliable timestamps
**Cons**: May have gaps (not hourly coverage), slow API

**Implementation**:
```python
import requests
from datetime import datetime

def get_wayback_snapshots(market_slug):
    cdx_url = f"http://web.archive.org/cdx/search/cdx"
    params = {
        'url': f'polymarket.com/event/{market_slug}',
        'output': 'json',
        'from': '20251001',
        'to': '20260228',
        'filter': 'statuscode:200'
    }
    response = requests.get(cdx_url, params=params)
    snapshots = response.json()[1:]  # Skip header
    
    price_data = []
    for snapshot in snapshots:
        timestamp_str = snapshot[1]  # YYYYMMDDHHmmss format
        snapshot_url = f"http://web.archive.org/web/{timestamp_str}/{snapshot[2]}"
        
        # Download and parse snapshot
        html = requests.get(snapshot_url).text
        # Extract price from JSON in page
        # ...
        
    return price_data
```

#### Method 2: Polymarket CLOB API Historical Data
**Target**: Direct API for historical orderbook/trades
**Approach**:
1. Check if Polymarket's CLOB (Central Limit Order Book) API has historical endpoints
2. Query: `https://clob.polymarket.com/prices?market={market_id}&start={timestamp}&end={timestamp}`
3. Alternative: Check for archived trade history endpoints

**Pros**: Most accurate, high resolution
**Cons**: May not be available for old markets, API rate limits

**API Endpoints to try**:
- `https://clob.polymarket.com/markets/{market_id}`
- `https://gamma-api.polymarket.com/markets/{market_id}`
- `https://data-api.polymarket.com/`  (check for historical data service)

#### Method 3: Archived Chart Data
**Target**: Third-party archives or cached chart data
**Approach**:
1. Search GitHub for Polymarket scrapers/archives
2. Check if anyone published historical datasets
3. Look for data science projects that archived prices
4. Check Kaggle, Hugging Face datasets

**Search queries**:
- `site:github.com polymarket historical data`
- `site:kaggle.com polymarket prices`
- `"polymarket" "price history" filetype:csv`

#### Method 4: Twitter/Social Media Screenshots
**Target**: Posts with price screenshots from traders
**Approach**:
1. Search Twitter for market-specific posts with screenshots
2. Use Twitter Advanced Search: `polymarket "{market_title}" since:2025-10-01 until:2026-02-28 (price OR chart)`
3. OCR screenshots to extract prices and timestamps
4. Manually verify and record

**Pros**: Can fill specific gaps
**Cons**: Very labor-intensive, sparse data

### Implementation Workflow

#### Phase 1: Data Discovery (Day 1)
1. **Identify all resolved markets** in the Oct 2025 - Feb 2026 timeframe
   - Query Polymarket API for resolved markets
   - Filter by close date in range
   - Export market IDs and slugs

2. **Test data availability** across all methods
   - Sample 10 markets
   - Try each method
   - Assess coverage and quality

#### Phase 2: Automated Collection (Days 2-3)
1. **Wayback Machine scraper**
   - Iterate through all market slugs
   - Download snapshots
   - Parse and store price data
   - Handle rate limits (5 second delays)

2. **CLOB API historical queries**
   - Test if historical data available
   - Batch query all markets
   - Combine with Wayback data

3. **GitHub/Kaggle search**
   - Find existing datasets
   - Download and integrate

#### Phase 3: Gap Filling (Day 4)
1. **Identify gaps** in coverage
   - Markets with <10 data points
   - Long periods (>24h) without data

2. **Manual collection** for critical markets
   - Twitter search for high-volume markets
   - OCR screenshots if necessary

3. **Interpolation** (only as last resort)
   - Linear interpolation for small gaps (<4 hours)
   - Document all interpolated points

#### Phase 4: Validation & Export (Day 5)
1. **Data quality checks**
   - Prices always between 0 and 1
   - Volume non-negative
   - Timestamps in chronological order
   - No duplicates

2. **Cross-validation**
   - Compare multiple sources where available
   - Flag discrepancies

3. **Export final CSV**
   ```csv
   market_id,timestamp,yes_price,volume
   0x1234...,2025-10-01T12:00:00Z,0.65,45000
   0x1234...,2025-10-01T13:00:00Z,0.66,47000
   ```

### Code Structure

```
price_history_reconstruction/
├── scrape_wayback.py           # Wayback Machine scraper
├── query_clob_api.py           # CLOB API queries
├── search_archives.py          # GitHub/Kaggle search
├── twitter_screenshots.py      # Twitter search & OCR
├── combine_sources.py          # Merge all data sources
├── validate_and_export.py      # Quality checks & CSV export
├── data/
│   ├── wayback_snapshots/      # Raw Wayback data
│   ├── clob_api_responses/     # API responses
│   ├── external_datasets/      # Downloaded archives
│   └── price_history.csv       # FINAL OUTPUT
└── logs/
    └── reconstruction.log
```

### Success Criteria
- ✅ At least 80% of markets have price data
- ✅ At least 10 data points per market
- ✅ Median data point spacing < 6 hours
- ✅ All data validated (prices 0-1, no negative volumes)
- ✅ Documentation of data sources for each market

### Risks & Mitigation
1. **Risk**: Wayback Machine may not have frequent snapshots
   - **Mitigation**: Combine multiple sources, accept lower resolution

2. **Risk**: CLOB API may not provide historical data
   - **Mitigation**: Rely on Wayback + manual collection

3. **Risk**: Some markets may have no data at all
   - **Mitigation**: Document missing markets, focus on high-volume ones first

### Timeline
- Day 1: Market discovery + method testing
- Days 2-3: Automated scraping (Wayback + API)
- Day 4: Gap filling + manual collection
- Day 5: Validation + export

### Next Steps
1. Create list of all resolved markets (Oct 2025 - Feb 2026)
2. Test Wayback Machine API on 5 sample markets
3. Test CLOB API for historical data availability
4. Begin automated scraping
