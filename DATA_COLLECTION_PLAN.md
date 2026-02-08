# 2-Year Historical Data Collection Plan
## Target: Feb 2024 - Feb 2026 Polymarket Data

### Executive Summary
Build a robust system to collect 2 years of Polymarket historical data with 4 daily price samples per market, targeting 10K+ markets with full price histories.

### Data Requirements
- **Date Range**: Feb 1, 2024 - Feb 7, 2026 (24 months, ~730 days)
- **Price Sampling**: 4 per day (00:00, 06:00, 12:00, 18:00 UTC)
- **Target Markets**: 10,000+ markets
- **Data Points per Market**: ~2,920 (730 days × 4 prices)
- **Total Data Points**: ~29.2 million price samples

### Data Sources Analysis

#### 1. Gamma API (Primary) ✅
- **Endpoint**: `https://gamma-api.polymarket.com/markets`
- **Capabilities**:
  - Market metadata (question, category, dates, volume)
  - Current prices and basic stats
  - Filtering by date (end_date_min, etc.)
  - Pagination support
- **Limitations**:
  - No direct historical price access
  - Current prices only

#### 2. CLOB API (Secondary) ⚠️
- **Endpoint**: `https://clob.polymarket.com/`
- **Status**: Direct price-history endpoints return 404
- **Alternative**: May need to use GitHub scraper approaches

#### 3. GitHub Scrapers (Implementation Reference) ✅
- **apoideas/polymarket-historical-data**:
  - Uses `polymarket-apis` Python package
  - Configurable date ranges and intervals
  - Proven to work for historical data
  - Limitation: Only markets opened+closed in range
  
- **benjiminii/polymarket-scrape**:
  - Async scraper with rate limiting
  - Parquet storage (efficient)
  - DuckDB analytics built-in
  - Full price history collection

### Implementation Strategy

#### Phase 1: Setup & Testing (30 min)
1. Install `polymarket-apis` package
2. Test API access for historical prices
3. Verify date range filtering works
4. Test sample market with full price history

#### Phase 2: Core Collector (2 hours)
1. Market fetcher:
   - Fetch all markets from Feb 2024+
   - Filter by volume threshold (>$1000)
   - Save metadata (ID, question, category, dates, volume, outcome)
   
2. Price history collector:
   - For each market, get hourly prices
   - Downsample to 4/day (00:00, 06:00, 12:00, 18:00 UTC)
   - Handle gaps in data gracefully
   
3. Checkpointing:
   - Save progress every 100 markets
   - Resume from last checkpoint
   - Atomic writes to prevent corruption

4. Rate limiting:
   - Exponential backoff on errors
   - Configurable delay between requests
   - Respect API limits (estimate: 10 req/sec max)

#### Phase 3: Data Quality & Storage (1 hour)
1. Validation:
   - Check date ranges
   - Verify price counts
   - Detect missing data
   
2. Storage formats:
   - **JSON**: `historical_2yr_dataset.json` (full detail)
   - **Parquet**: `historical_2yr_dataset.parquet` (efficient queries)
   - **CSV**: Individual files per category
   
3. Metadata:
   - Market taxonomy by category
   - Coverage statistics
   - Data quality report

### Time Estimates

#### Optimistic (Best Case): 3-4 hours
- API works perfectly
- No rate limiting issues
- 10K markets @ 2 sec each = ~5.5 hours fetch time
- Parallel processing: ~2 hours actual

#### Realistic (Expected): 6-8 hours
- Some API issues
- Rate limiting delays
- Need retries and error handling
- Checkpointing overhead

#### Pessimistic (Worst Case): 12-24 hours
- Major API limitations
- Need to use alternative approaches
- Manual intervention required
- Data quality issues

### Success Metrics
- ✅ 10,000+ markets collected
- ✅ 80%+ markets have full 2-year price history
- ✅ 4 prices per day maintained
- ✅ All resolved markets have outcomes
- ✅ Coverage report shows distribution by category/month

### Deliverables
1. **Dataset Files**:
   - `historical_2yr_dataset.json` - Full dataset
   - `historical_2yr_dataset.parquet` - Optimized format
   - `markets_by_category.csv` - Market taxonomy
   - `coverage_report.json` - Statistics

2. **Code**:
   - `collector.py` - Main data collector
   - `config.py` - Configuration
   - `checkpoints/` - Progress saves

3. **Documentation**:
   - `DATA_SCHEMA.md` - Data structure
   - `COLLECTION_LOG.md` - Collection run details
   - `COVERAGE_REPORT.md` - Analysis of coverage

### Risk Mitigation
1. **API Rate Limits**: Exponential backoff + checkpointing
2. **Missing Data**: Track coverage, flag incomplete markets
3. **API Changes**: Fallback to alternative endpoints
4. **Storage**: Stream to disk, don't hold in memory
5. **Time Overrun**: Can pause/resume anytime via checkpoints

### Next Steps
1. ✅ Complete API exploration
2. ⏳ Install polymarket-apis package
3. ⏳ Build core collector
4. ⏳ Test on 100 markets
5. ⏳ Full collection run
6. ⏳ Generate reports
