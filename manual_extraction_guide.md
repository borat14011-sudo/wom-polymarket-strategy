# Manual Wayback Machine Extraction Guide

If automated scraping is challenging, here's how to manually extract key market data:

## Step 1: Find Key Snapshots

Go to: https://web.archive.org/web/*/polymarket.com

Key dates to check:
- **2024-06-01**: Early election markets
- **2024-09-01**: Pre-election buildup
- **2024-10-15**: Late October (debate season)
- **2024-11-05**: Election day
- **2024-11-06**: Post-election
- **2024-12-01**: Post-resolution
- **2025-01-01**: New year markets

## Step 2: Extract Data from Each Snapshot

For each snapshot, open Browser DevTools (F12) and:

### Method 1: Find __NEXT_DATA__

1. Go to Sources tab
2. Search for `__NEXT_DATA__`
3. Copy the entire JSON object
4. Save to file: `snapshot_YYYYMMDD.json`

### Method 2: Network Tab

1. Refresh the archived page
2. Go to Network tab → Fetch/XHR
3. Look for API calls to:
   - `/api/markets`
   - `/clob/`
   - GraphQL endpoints
4. Copy response JSON

### Method 3: Console Extraction

Paste this in console:

```javascript
// Extract Next.js data
const nextData = JSON.parse(document.getElementById('__NEXT_DATA__').textContent);
console.log(JSON.stringify(nextData, null, 2));

// Look for market data in props
const markets = nextData?.props?.pageProps?.markets || [];
console.log(markets);

// Export to file
const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(nextData, null, 2));
const downloadAnchor = document.createElement('a');
downloadAnchor.setAttribute("href", dataStr);
downloadAnchor.setAttribute("download", "polymarket_data.json");
document.body.appendChild(downloadAnchor);
downloadAnchor.click();
downloadAnchor.remove();
```

## Step 3: Extract Specific Markets

Target URLs to check:
- Trump markets: Search for "trump" in archive
- Presidential election: `/event/presidential-election-2024`
- Bitcoin price: `/event/bitcoin-price-*`
- Crypto markets: `/event/eth-*`, `/event/crypto-*`

## Step 4: Organize Data

Create a spreadsheet with columns:
- Date/Time
- Market Name
- Yes Price
- No Price
- Volume (24h)
- Total Volume
- Liquidity
- Resolved (True/False)
- Resolution Outcome

## Step 5: Key Markets to Track

### Presidential Election 2024
- "Will Donald Trump win the 2024 Presidential Election?"
- "2024 US Presidential Election Winner"

### State-by-State
- Pennsylvania winner
- Michigan winner
- Arizona winner
- etc.

### Policy Markets
- "Will Trump pardon himself?"
- "Will there be a peaceful transition?"

### Crypto Markets
- "Bitcoin to $100k by end of 2024"
- "Ethereum to $5k by end of 2024"

## Quick Analysis

Once you have snapshots from multiple dates:

1. **Price Movement**: Track how "Yes" probability changed over time
2. **Volume Spikes**: Note dates with high volume (news events)
3. **Resolution Accuracy**: Compare final prices to actual outcomes
4. **Market Efficiency**: How quickly did markets react to news?

## Example: Trump Election Market

| Date | Yes Price | Volume 24h | Event |
|------|-----------|------------|-------|
| 2024-06-01 | 0.45 | $50K | Early campaign |
| 2024-09-01 | 0.48 | $200K | Debate season |
| 2024-10-15 | 0.52 | $500K | Polls tighten |
| 2024-11-05 | 0.58 | $2M | Election day |
| 2024-11-06 | 0.99 | $5M | Trump wins |

## Tools to Help

- **jq**: Command-line JSON processor
- **Pandas**: Python data analysis
- **Excel/Google Sheets**: Manual data entry
- **Tableau/Power BI**: Visualization

## Alternative Data Sources

If Wayback Machine is incomplete:

1. **Twitter/X Archives**: Search for Polymarket screenshots
2. **Reddit r/Polymarket**: Community discussions with price mentions
3. **Discord/Telegram**: Polymarket community archives
4. **Third-party trackers**: Some sites archived Polymarket data
5. **Blockchain**: Resolution transactions on Polygon
