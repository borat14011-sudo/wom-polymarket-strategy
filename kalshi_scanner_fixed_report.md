# Kalshi Prediction Market Scanner Report

**Scan Date:** 2026-02-13 15:05 PST
**Markets Found:** 0
**Resolution Window:** 2026-02-13 to 2026-02-20

---

## No Markets Found

No markets found matching the criteria:
- Resolution within 7 days
- Volume > 500 contracts
- Price between 20-80¢

### Possible Reasons:
1. Most Kalshi markets are long-term (politics, climate)
2. Short-term markets may have already resolved
3. Current API endpoint may not include all market types
4. Need authentication for certain market categories

## Scanner Configuration

- **API Endpoint:** `https://api.elections.kalshi.com/trade-api/v2`
- **Authentication:** Bearer token
- **Retry Logic:** Exponential backoff (3 retries)
- **Timeout:** 30 seconds per request
- **Pagination:** Supports cursor-based pagination
