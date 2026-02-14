# Kalshi Browser Scraper - Manual Execution Guide

## Overview
This guide provides step-by-step instructions to manually scrape Kalshi market data when browser automation fails. The goal is to bypass broken DNS/API by using the Chrome browser directly.

## Prerequisites
1. Google Chrome browser installed
2. OpenClaw Chrome extension installed and enabled
3. Kalshi account (logged in)

## Step 1: Attach Chrome Extension
1. Open Chrome browser
2. Navigate to any tab (e.g., about:blank)
3. Click the OpenClaw Browser Relay toolbar icon (looks like a claw)
4. Verify the badge turns ON (usually shows "1" or similar)

## Step 2: Navigate to Kalshi
1. Go to https://kalshi.com
2. Log in if not already logged in
3. Wait for the page to fully load

## Step 3: Find Top 10 Markets
Kalshi typically displays markets on the homepage or in a "Markets" section. Look for:
- "Trending Markets" or "Popular Markets"
- "Browse Markets" section
- Search bar to find specific markets

Common top markets include:
- Will [candidate] win the 2024 election?
- Will inflation exceed X%?
- Will [sports team] win the championship?
- Will [economic indicator] reach X level?

## Step 4: Extract Real-Time Prices
For each market, note:
1. **Market Title**: e.g., "Will inflation exceed 3% in 2024?"
2. **Yes Price**: Current price for "Yes" outcome (0-100¢)
3. **No Price**: Current price for "No" outcome (0-100¢)
4. **Volume**: Number of contracts traded
5. **Open Interest**: Total contracts outstanding

## Step 5: Verify Liquidity
Check these indicators:
1. **Bid-Ask Spread**: Difference between highest bid and lowest ask
   - Tight spread (<5¢) = good liquidity
   - Wide spread (>10¢) = poor liquidity
2. **Order Book Depth**: Number of contracts at each price level
3. **Recent Trades**: Frequency and size of recent trades

## Step 6: Create Executable Trade Links
Kalshi trade URLs follow this pattern:
```
https://kalshi.com/markets/[market-ticker]
```

Example trade actions:
1. **Buy Yes**: Navigate to market page → Click "Buy Yes" → Enter quantity → Confirm
2. **Buy No**: Navigate to market page → Click "Buy No" → Enter quantity → Confirm
3. **Sell Position**: Go to portfolio → Find position → Click "Sell"

## Manual Data Collection Template
```markdown
| Market | Yes Price | No Price | Volume | Open Interest | Spread | Liquidity |
|--------|-----------|----------|--------|---------------|--------|-----------|
| Market 1 | 65¢ | 35¢ | 1,234 | 5,678 | 2¢ | Good |
| Market 2 | 42¢ | 58¢ | 567 | 2,345 | 5¢ | Medium |
| Market 3 | 78¢ | 22¢ | 890 | 4,567 | 1¢ | Excellent |
```

## Troubleshooting
1. **Page won't load**: Check internet connection, try incognito mode
2. **Login issues**: Clear cookies, reset password
3. **Extension not working**: Restart Chrome, reinstall extension
4. **Data not updating**: Refresh page, check for JavaScript errors

## Alternative Methods
If browser automation fails completely:
1. **Use Kalshi mobile app** (if available)
2. **Screen capture** and use OCR tools
3. **Manual API calls** using browser DevTools Network tab
4. **Python requests** with saved cookies (advanced)

## Safety Notes
- Only trade with risk capital you can afford to lose
- Verify all prices before executing trades
- Double-check order quantities and prices
- Keep records of all trades for tax purposes

## Next Steps
Once you've attached the Chrome extension tab, the automated scraper can:
1. Automatically navigate to kalshi.com
2. Extract market data using DOM parsing
3. Calculate liquidity metrics
4. Generate clickable trade links
5. Export data to CSV/JSON format
```

Now let me check if there are any existing files in the workspace that might help with this task.

<｜DSML｜function_calls>
<｜DSML｜invoke name="exec">
<｜DSML｜parameter name="command" string="true">dir /b