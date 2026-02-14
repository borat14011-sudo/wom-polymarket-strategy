# Polymarket Data Fetch - Summary Report
**Fetched:** 2026-02-12 20:42 PST  
**Source:** https://gamma-api.polymarket.com/markets?limit=200&closed=false  
**Saved to:** polymarket_latest.json

## Summary Statistics
- **Total open markets fetched:** 200
- **Data file size:** 1,047,192 bytes (~1MB)
- **Timestamp:** Data fetched at 2026-02-13T04:42:44.649Z

## Top 5 Markets by Volume

### 1. Chelsea Clinton - 2028 Democratic Nomination
- **Volume:** 35,661,421.77
- **Current Prices:** Yes: 0.0075 (0.75%), No: 0.9925 (99.25%)
- **Liquidity:** 1,040,657.11
- **Market ID:** (See JSON file for full details)

### 2. Indiana Pacers - 2026 NBA Finals
- **Volume:** 31,589,817.72
- **Current Prices:** Yes: 0.0015 (0.15%), No: 0.9985 (99.85%)
- **Liquidity:** 503,416.39

### 3. Memphis Grizzlies - 2026 NBA Finals
- **Volume:** 30,536,368.85
- **Current Prices:** Yes: 0.0015 (0.15%), No: 0.9985 (99.85%)
- **Liquidity:** 1,023,388.72

### 4. Zohran Mamdani - 2028 Democratic Nomination
- **Volume:** 29,276,026.98
- **Current Prices:** Yes: 0.0105 (1.05%), No: 0.9895 (98.95%)
- **Liquidity:** 211,298.47

### 5. George Clooney - 2028 Democratic Nomination
- **Volume:** 29,012,342.27
- **Current Prices:** Yes: 0.0075 (0.75%), No: 0.9925 (99.25%)
- **Liquidity:** 1,268,249.52

## Data Structure
The JSON file contains 200 market objects with the following key fields for each:
- `id`: Market identifier
- `question`: Market question
- `slug`: URL-friendly identifier
- `outcomePrices`: Current prices for outcomes (typically ["Yes", "No"] prices)
- `volume`: Total trading volume
- `liquidity`: Market liquidity
- `active`: Boolean indicating if market is active
- `closed`: Boolean indicating if market is closed
- `endDate`: Market resolution date
- `description`: Detailed market description
- `volume24hr`, `volume1wk`, `volume1mo`, `volume1yr`: Time-based volume metrics

## Notes
- All markets are open (`closed=false`)
- Prices are represented as strings in array format
- Volume and liquidity are string representations of decimal numbers
- The data includes comprehensive market details suitable for analysis