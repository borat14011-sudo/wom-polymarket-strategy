# DATA QUALITY REPORT - 2024

## Summary Statistics

- **Total markets scanned**: 20
- **2024 resolved markets found**: 0
- **Markets with price data**: 0
- **Markets without price data**: 0
- **Coverage**: NaN%

## Price Data Quality

- **Total price points collected**: 0
- **Average points per market**: NaN

## Data Gaps

Markets without price history data typically fall into these categories:
1. **API endpoint not found** - Price history endpoint doesn't exist or has changed
2. **Low-volume markets** - May not have sufficient trading activity for timeseries
3. **Very old markets** - Historical data may not be retained

## Query the Database

```sql
-- List all 2024 markets with price data
SELECT m.market_id, m.question, m.volume, dq.price_count
FROM markets m
JOIN data_quality dq ON m.market_id = dq.market_id
WHERE dq.has_price_data = 1
ORDER BY m.volume DESC;

-- Markets missing price data
SELECT m.market_id, m.question, m.volume, dq.error
FROM markets m
JOIN data_quality dq ON m.market_id = dq.market_id
WHERE dq.has_price_data = 0
ORDER BY m.volume DESC;

-- Price history for a specific market
SELECT timestamp, price, volume
FROM price_history
WHERE market_id = 'YOUR_MARKET_ID'
ORDER BY timestamp;
```

## Issues Encountered

None

## Next Steps

1. ✓ Database created: **historical_2024.db**
2. Review markets without price data (see SQL queries above)
3. Consider alternate data sources for missing markets
4. Use this data for backtesting and analysis

---
Generated: 2026-02-07T12:51:08.146Z
