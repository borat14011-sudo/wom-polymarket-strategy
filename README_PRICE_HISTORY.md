# Price History Reconstruction System

## Overview

This system reconstructs historical price data for Polymarket markets that resolved between **October 2025 and February 2026**. The data is critical for backtesting trading strategies and replaying historical trades.

## Quick Start

### 1. Install Dependencies
```bash
pip install requests beautifulsoup4 lxml
```

### 2. Fetch Market List
```bash
python identify_resolved_markets.py
```

This queries the Polymarket API and creates:
- `resolved_markets_oct2025_feb2026.json` - Full details
- `resolved_markets_simple.csv` - Quick reference

### 3. Test Data Sources
```bash
# Test API endpoints
python query_clob_api.py

# Test Wayback Machine (edit script with actual market slugs first)
python scrape_wayback.py
```

### 4. Run Collection
Based on test results, choose your approach:

**Option A: API Collection** (if APIs have historical data)
```python
# Edit and run query_clob_api.py with market list
```

**Option B: Wayback Collection** (if Wayback has good coverage)
```python
# Edit scrape_wayback.py with market list
# Run with rate limiting
```

**Option C: Hybrid** (recommended)
```python
# Run both methods and combine results
```

## File Structure

```
price_history_reconstruction/
│
├── README_PRICE_HISTORY.md              # This file
├── PRICE_HISTORY_RECONSTRUCTION_STATUS.md  # Status report
├── price_history_reconstruction_plan.md    # Detailed strategy
│
├── identify_resolved_markets.py         # Step 1: Get market list
├── query_clob_api.py                    # Method 2: API queries
├── scrape_wayback.py                    # Method 1: Wayback scraping
│
├── resolved_markets_oct2025_feb2026.json   # Output from step 1
├── resolved_markets_simple.csv             # Output from step 1
│
└── price_history.csv                    # FINAL OUTPUT
```

## Output Format

Final CSV (`price_history.csv`):

```csv
market_id,timestamp,yes_price,volume
0x1234...,2025-10-15T08:00:00Z,0.52,125000
0x1234...,2025-10-15T09:00:00Z,0.53,127500
0x5678...,2025-10-16T10:00:00Z,0.67,89000
```

**Columns:**
- `market_id`: Polymarket market condition ID (hex string starting with 0x)
- `timestamp`: ISO 8601 datetime with timezone (UTC)
- `yes_price`: Probability of YES outcome (float between 0.0 and 1.0)
- `volume`: 24-hour trading volume in USD (float)

## Data Collection Methods

### Method 1: Wayback Machine ⏰
**Status**: Implemented in `scrape_wayback.py`

Uses Internet Archive to find archived Polymarket pages:
1. Queries CDX API for snapshots
2. Downloads archived HTML
3. Extracts JSON data from page (`__NEXT_DATA__`)
4. Parses price and volume

**Pros**: Official snapshots, reliable timestamps  
**Cons**: May have gaps, slow (rate-limited)

**Rate Limit**: 5 seconds between requests (to be respectful)

### Method 2: Polymarket APIs 🔌
**Status**: Implemented in `query_clob_api.py`

Queries Polymarket's public APIs:
- Gamma API: `https://gamma-api.polymarket.com`
- CLOB API: `https://clob.polymarket.com`
- Data API: `https://data-api.polymarket.com`

**Pros**: Fast, official data  
**Cons**: Historical endpoints may not exist

### Method 3: Archived Datasets 📚
**Status**: Manual search required

Search for existing datasets:
- GitHub repositories
- Kaggle datasets
- Hugging Face datasets
- Research papers with data

**Keywords**: `polymarket historical prices`, `polymarket dataset oct 2025`

### Method 4: Social Media Screenshots 📱
**Status**: Manual collection

For critical gaps:
1. Twitter Advanced Search
2. Find posts with price screenshots
3. OCR to extract prices
4. Manually record

**Use only for**: High-volume markets with data gaps

## Usage Examples

### Example 1: Check Market Coverage

```python
import pandas as pd

# Load resolved markets
markets = pd.read_csv('resolved_markets_simple.csv')
print(f"Total markets: {len(markets)}")
print(f"Total volume: ${markets['volume'].sum():,.2f}")

# Top 10 by volume
top_markets = markets.nlargest(10, 'volume')
print(top_markets[['question', 'volume']])
```

### Example 2: Scrape Specific Market

```python
from scrape_wayback import WaybackScraper

scraper = WaybackScraper()

# Scrape a specific market
price_data = scraper.scrape_market(
    market_slug='presidential-election-winner-2024',
    market_id='0x1234567890abcdef',
    output_file='price_history.csv'
)

print(f"Extracted {len(price_data)} price points")
```

### Example 3: Query API for Market

```python
from query_clob_api import PolymarketHistoricalAPI

api = PolymarketHistoricalAPI()

# Try to get historical data
history = api.get_market_history('0x1234567890abcdef')

if history:
    print(f"Got {len(history)} historical records")
else:
    print("No API data available - use Wayback instead")
```

## Validation

Before considering data complete, validate:

```python
import pandas as pd

# Load price history
df = pd.read_csv('price_history.csv')

# Validation checks
assert df['yes_price'].between(0, 1).all(), "Prices must be 0-1"
assert (df['volume'] >= 0).all(), "Volume must be non-negative"
assert df['timestamp'].is_monotonic_increasing, "Timestamps must be sorted"
assert not df.duplicated(['market_id', 'timestamp']).any(), "No duplicates"

print("✅ All validation checks passed")
```

## Performance Estimates

### Wayback Machine Scraping
- Rate limit: 1 request per 5 seconds
- Snapshots per market: 10-50 (estimated)
- Time per market: 1-5 minutes
- Total for 100 markets: 2-8 hours

### API Querying
- Rate limit: Unknown (test first)
- Time per market: <1 second
- Total for 100 markets: <2 minutes

### Manual Collection (Twitter)
- Time per market: 10-30 minutes
- Recommended: Top 10-20 markets only

## Troubleshooting

### "No snapshots found" for a market

**Cause**: Internet Archive didn't crawl that market, or market slug is wrong

**Solutions**:
1. Try alternative slug format
2. Search Wayback manually: `https://web.archive.org/web/*/polymarket.com/event/*`
3. Use API method instead
4. Skip market if low volume

### "Could not extract price data"

**Cause**: HTML structure changed or JSON parsing failed

**Solutions**:
1. Download snapshot manually and inspect HTML
2. Update regex patterns in `scrape_wayback.py`
3. Try different extraction method

### "API returns 403/429"

**Cause**: Rate limiting or authentication required

**Solutions**:
1. Add delays between requests
2. Check if API key required
3. Use Wayback method instead

## Best Practices

### 1. Prioritize by Volume
- Scrape high-volume markets first
- Top 20 markets often represent 80% of volume

### 2. Incremental Saves
- Scripts save to CSV after each market
- Safe to interrupt and resume

### 3. Version Control
- Commit data files regularly
- Tag major milestones

### 4. Documentation
- Document data source for each market
- Note any manual adjustments

## Data Quality Tiers

### Tier 1: High Quality ⭐⭐⭐
- 20+ data points per market
- Data spacing < 6 hours
- From official sources (API or Wayback)

### Tier 2: Acceptable ⭐⭐
- 10-20 data points per market
- Data spacing < 12 hours
- Mix of sources

### Tier 3: Minimal ⭐
- 5-10 data points per market
- Gaps up to 24 hours
- May include interpolation

### Tier 4: Insufficient ❌
- <5 data points
- Large gaps
- Not suitable for backtesting

**Goal**: 80% of markets at Tier 2 or above

## FAQ

### Q: How many markets should we expect?
**A**: Unknown until API query. Estimate: 50-200 markets in the Oct 2025 - Feb 2026 window.

### Q: How long will this take?
**A**: 1-5 days depending on method:
- API only: 1 day
- Wayback only: 3-5 days
- Hybrid: 2-4 days

### Q: What if we can't get data for a market?
**A**: Focus on coverage. 80% of markets is acceptable. Prioritize high-volume markets.

### Q: Can we interpolate missing data?
**A**: Only for small gaps (<4 hours) and document it clearly. Never interpolate large gaps.

### Q: What timezone should timestamps use?
**A**: UTC (Coordinated Universal Time). ISO 8601 format with 'Z' suffix.

## Support

For issues or questions:
1. Check `PRICE_HISTORY_RECONSTRUCTION_STATUS.md` for current status
2. Review `price_history_reconstruction_plan.md` for detailed methodology
3. Contact main agent with specific questions

## License

This code is part of the Polymarket analysis project. Use responsibly and respect API rate limits.

---

**Last Updated**: 2026-02-06  
**Version**: 1.0  
**Subagent**: price-history-reconstruction
