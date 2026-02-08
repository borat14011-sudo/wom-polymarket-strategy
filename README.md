# Polymarket Live Market Data System

🚀 **Complete solution for Wom's trading operation** - Extract live 2025 market data from Polymarket using multiple methods since the free API only provides historical data.

## ⚡ Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browser (for automation)
playwright install chromium

# Run complete system
python run.py full
```

## 📋 System Overview

This system solves the **CRITICAL PROBLEM**: Polymarket's free API (CLOB) only returns historical markets (2022-2023). Current 2025 markets require:
- ✅ **Web Scraping** (included)
- ✅ **Browser Automation** (included) 
- ❌ API Key (not available)

## 🎯 Features

### Data Extraction Methods
1. **HTTP Web Scraping** - Fast, lightweight extraction
2. **Browser Automation** - JavaScript-rendered content (Playwright)
3. **API Testing** - Test all endpoints automatically
4. **Live Monitoring** - Continuous price tracking

### Capabilities
- ✅ Extract ALL current 2025 prediction markets
- ✅ Live price tracking and alerts
- ✅ Volume and liquidity monitoring
- ✅ Price change detection (>5%)
- ✅ Volume spike detection (>50%)
- ✅ Historical data storage
- ✅ Category filtering (politics, crypto, sports, economics, tech)
- ✅ Performance metrics and reporting

## 📂 File Structure

```
polymarket-system/
├── run.py                    # Main execution script
├── polymarket_monitor.py     # Live monitoring system
├── web_scraper.py           # HTTP-based web scraper
├── browser_automation.py    # Playwright browser automation
├── market_fetcher.py        # Market data fetching
├── api_client.py           # API client with rate limiting
├── market_parser.py        # Market data parsing/filtering
├── test_apis.py           # API endpoint testing
├── utils.py               # Utilities (logging, storage, alerts)
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Usage

### 1. Test API Endpoints
```bash
python run.py test
```
Tests all known Polymarket endpoints and reports which ones work.

### 2. Scrape Current Markets
```bash
# Basic scraping
python run.py scrape

# Save to specific file
python run.py scrape --output my_markets.json

# Use browser automation (more reliable)
python run.py browser
```

### 3. Start Live Monitoring
```bash
# Default: 60-second intervals
python run.py monitor

# Custom interval (30 seconds)
python run.py monitor --interval 30

# Run for specific duration (2 hours)
python run.py monitor --duration 120
```

### 4. Run Complete System
```bash
python run.py full
```
Runs: API testing → Market scraping → Live monitoring

## 📊 Output Files

### Scraped Data
- `polymarket_2025_*.json` - Current 2025 markets
- `api_test_results.json` - API endpoint test results

### Monitoring Data
- `market_data/latest_2025_markets.json` - Latest market snapshot
- `market_data/all_markets_*.json` - All markets by timestamp
- `market_data/monitor_state.json` - Monitor configuration
- `market_history/` - Historical price data
- `alerts/` - Generated alerts
- `polymarket_monitor_*.log` - System logs

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Monitoring
CHECK_INTERVAL_SECONDS = 60
ALERT_THRESHOLD_PRICE_CHANGE = 0.05  # 5%
MAX_MARKETS_TO_MONITOR = 100

# Filtering
MIN_VOLUME_THRESHOLD = 1000
MIN_LIQUIDITY_THRESHOLD = 500

# Categories
WATCHLIST_CATEGORIES = ['politics', 'crypto', 'sports', 'economics', 'technology']
```

## 🎓 How It Works

### The Problem
- **Polymarket CLOB API**: Returns 1000 markets, but all are historical (2022-2023)
- **Current 2025 markets**: Not accessible via free API
- **Solution**: Scrape directly from polymarket.com website

### The Solution
1. **HTTP Scraping** attempts to fetch from public endpoints
2. **Browser Automation** loads the actual website and extracts React/Next.js data
3. **Data Parsing** filters for 2025 markets and extracts prices, volumes, etc.
4. **Live Monitoring** continuously tracks changes and generates alerts

## 📈 Sample Output

```
================================================================================
📊 POLYMARKET MONITOR - UPDATE #1
================================================================================
Total Markets: 1,247
2025 Markets: 89
Last Update: 2025-02-08 12:15:32

🏆 TOP 2025 MARKETS BY VOLUME:
 1. $12,450,000 | Will Trump win 2025 GOP nomination?
 2. $8,230,000 | Bitcoin price at end of 2025?
 3. $5,100,000 | Ethereum ETF approval in 2025?
 4. $3,450,000 | 2025 Super Bowl winner?
 5. $2,890,000 | Fed rate cuts in 2025?

📁 CATEGORY BREAKDOWN:
   politics: 34 markets
   crypto: 28 markets
   sports: 15 markets
   economics: 12 markets
================================================================================
```

## 🚨 Alert System

Automatic alerts for:
- **Price Changes** > 5%
- **Volume Spikes** > 50%
- **New Markets** detected
- **Market Closures**

Example:
```
🚨 PRICE ALERT: Will Bitcoin hit $100K in 2025? - Change: 7.23% ($0.45 → $0.52)
📈 VOLUME ALERT: Ethereum ETF approval - Change: 156.3%
🆕 NEW MARKETS: 3 new 2025 markets detected
```

## 🛠️ Advanced Usage

### Python API
```python
import asyncio
from web_scraper import PolymarketWebScraper

async def get_markets():
    async with PolymarketWebScraper() as scraper:
        markets = await scraper.scrape_all_markets()
        markets_2025 = scraper.filter_2025_markets(markets)
        return markets_2025

markets = asyncio.run(get_markets())
```

### Custom Filtering
```python
from market_parser import MarketParser

parser = MarketParser()
# Filter by category
crypto_markets = [m for m in markets if parser.categorize_market(m) == 'crypto']
# Filter by volume
high_volume = parser.filter_by_criteria(markets, min_volume=10000)
```

## ⚠️ Important Notes

1. **Rate Limiting**: Built-in rate limiting to avoid being blocked
2. **Browser Required**: For best results, use browser automation
3. **Data Freshness**: Website scraping provides ~1-5 minute delayed data
4. **Legal**: Comply with Polymarket's Terms of Service

## 🐛 Troubleshooting

### No markets found
```bash
# Try browser automation (more reliable)
python run.py browser
```

### Playwright not found
```bash
pip install playwright
playwright install chromium
```

### Permission errors
```bash
# On Linux/Mac
chmod +x run.py
./run.py full
```

## 📞 Support

For Wom's trading operation:
1. Run `python run.py full` to start
2. Check `market_data/latest_2025_markets.json` for current data
3. Monitor `polymarket_monitor_*.log` for system status
4. Review alerts in `alerts/` directory

## 📄 License

Private use for Wom's trading operation.

## 🙏 Credits

Built for Wom's Polymarket trading system.
Emergency build: 2026-02-08