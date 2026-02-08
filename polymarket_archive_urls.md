# Polymarket Wayback Machine Archive URLs

## Summary

From the Wayback Machine CDX API, we found **500+ archived event pages** from 2024-2025.

## Key Snapshots to Check

### Homepage Snapshots (2024)

Major dates with archived polymarket.com homepage:

- **2024-01-04**: https://web.archive.org/web/20240104114404/https://polymarket.com/
- **2024-06-01**: https://web.archive.org/web/20240601023548/https://polymarket.com/
- **2024-09-01**: Early September (pre-election)
- **2024-11-05**: https://web.archive.org/web/20241105022844/https://polymarket.com/ (Election Day!)
- **2024-11-06**: Post-election
- **2025-01-01**: New year markets

### Event Pages Available

The CDX query returned 500+ unique event pages. Sample event patterns found:

#### Price Prediction Markets
- `/event/$0.05` through `/event/$4.0` - Various price levels
- `/event/0.001` through `/event/0.10` - Probability levels

#### To Find Specific Markets

Use this CDX API URL pattern:
```
https://web.archive.org/cdx/search/cdx?url=polymarket.com/event/*KEYWORD*&from=2024&to=2025&output=json&filter=statuscode:200
```

Replace `*KEYWORD*` with:
- `*trump*` - Trump-related markets
- `*election*` - Election markets
- `*bitcoin*` or `*btc*` - Bitcoin price markets
- `*eth*` - Ethereum markets
- `*harris*` - Kamala Harris markets

## Manual Data Collection Strategy

### Priority Markets to Extract

1. **Presidential Election 2024**
   - Main Trump vs Biden/Harris market
   - State-by-state predictions
   - Electoral college markets

2. **Bitcoin Price Predictions**
   - "Bitcoin to $100k by end of 2024"
   - "Bitcoin to $50k" 
   - Monthly price targets

3. **Ethereum Price Predictions**
   - ETH price targets
   - ETH vs BTC performance

4. **Political Events**
   - Debate outcomes
   - Primary results
   - Policy predictions

### Key Dates to Sample

For each major market, check these dates:

- **Early 2024** (Jan-Mar): Baseline prices
- **Mid 2024** (Jun-Aug): Primary season
- **Late 2024** (Sep-Oct): Pre-election
- **Nov 5, 2024**: Election day
- **Nov 6-7, 2024**: Post-election settlement
- **Dec 2024**: Post-resolution
- **Early 2025**: New markets

### Data Points to Extract

For each snapshot:
1. **Market Question**: Full text
2. **Yes Price**: Probability (0-1 or 0-100%)
3. **No Price**: Complement probability  
4. **Volume 24h**: Last 24 hours trading volume ($)
5. **Total Volume**: Cumulative volume ($)
6. **Liquidity**: Available liquidity ($)
7. **Open Interest**: Total outstanding positions
8. **Resolution Status**: Open/Resolved
9. **Resolution Outcome**: Yes/No (if resolved)
10. **Resolution Date**: When market closed

## Using Browser DevTools

When visiting an archived page:

1. **Open DevTools** (F12)
2. **Go to Console**
3. **Paste this code**:

```javascript
// Extract Next.js data
try {
  const nextDataScript = document.getElementById('__NEXT_DATA__');
  if (nextDataScript) {
    const data = JSON.parse(nextDataScript.textContent);
    
    // Log the market data
    const market = data?.props?.pageProps?.market;
    if (market) {
      console.log('Market:', market.question || market.title);
      console.log('Prices:', market.outcomePrices);
      console.log('Volume:', market.volume);
      console.log('Liquidity:', market.liquidity);
      console.log('Resolved:', market.resolved);
      console.log('Full data:', market);
      
      // Download as JSON
      const blob = new Blob([JSON.stringify(market, null, 2)], {type: 'application/json'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'market_data.json';
      a.click();
    } else {
      console.log('Market data not found in expected location');
      console.log('Available data:', data);
    }
  } else {
    console.log('__NEXT_DATA__ not found');
  }
} catch (e) {
  console.error('Error:', e);
}
```

4. **Copy the output** or download the JSON file

## Example Data Structure

Expected JSON structure from archived pages:

```json
{
  "question": "Will Donald Trump win the 2024 Presidential Election?",
  "slug": "presidential-election-2024-trump",
  "outcomePrices": ["0.58", "0.42"],
  "outcomes": ["Yes", "No"],
  "volume": "125000000",
  "volume24hr": "5000000",
  "liquidity": "2000000",
  "resolved": true,
  "resolvedOutcome": "Yes",
  "closedAt": "2024-11-06T12:00:00Z"
}
```

## Building the Dataset

### CSV Format

Create a CSV with these columns:

```csv
market_id,date,timestamp,question,yes_price,no_price,volume_24h,total_volume,liquidity,resolved,outcome,notes
pres-2024,2024-06-01,20240601120000,"Trump wins 2024",0.45,0.55,50000,1000000,200000,FALSE,,"Early campaign"
pres-2024,2024-11-05,20241105120000,"Trump wins 2024",0.58,0.42,5000000,125000000,2000000,FALSE,,"Election day"
pres-2024,2024-11-06,20241106120000,"Trump wins 2024",0.99,0.01,8000000,135000000,100000,TRUE,Yes,"Resolved"
```

### Python Analysis

Once you have the CSV:

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('polymarket_historical.csv')
df['date'] = pd.to_datetime(df['date'])

# Filter for specific market
trump = df[df['market_id'] == 'pres-2024']

# Plot price over time
plt.figure(figsize=(12, 6))
plt.plot(trump['date'], trump['yes_price'], marker='o')
plt.title('Trump 2024 Election Market Price')
plt.xlabel('Date')
plt.ylabel('Yes Price (Probability)')
plt.grid(True)
plt.savefig('trump_price_history.png')

# Calculate volatility
trump['price_change'] = trump['yes_price'].diff()
print(f"Average daily change: {trump['price_change'].mean():.4f}")
print(f"Max single-day change: {trump['price_change'].max():.4f}")
```

## Alternative: Direct API Access

If the Wayback Machine is incomplete, consider:

1. **Polymarket Subgraph**: Query historical on-chain data
2. **Dune Analytics**: Pre-built dashboards with Polymarket data
3. **Twitter Bots**: Some bots archived daily prices
4. **Community Archives**: Discord/Telegram may have screenshots

## Contact for Historical Data

- **Polymarket Discord**: Community members may have archives
- **Prediction Market Reddit**: r/Polymarket, r/PredictionMarkets
- **Researchers**: Academic researchers may have collected data

## Rate Limiting

When scraping Wayback Machine:
- Wait 2-3 seconds between requests
- Limit to 10-20 requests per minute
- Use CDX API for bulk queries instead of direct page fetches

## Legal & Ethical Notes

- Wayback Machine data is publicly accessible
- Respect archive.org's terms of service
- Don't overload their servers
- Archived data is for research/analysis purposes
- Original data belongs to Polymarket
