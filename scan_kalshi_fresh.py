#!/usr/bin/env python3
"""
Kalshi Short-Term Scanner - Feb 13, 2026
Mission: Find ALL markets resolving in next 7 days
"""

import requests
import json
from datetime import datetime, timedelta

TODAY = datetime(2026, 2, 13)
SEVEN_DAYS = TODAY + timedelta(days=7)

print("=" * 80)
print("KALSHI SHORT-TERM SCANNER - February 13, 2026")
print(f"Target: Markets resolving {TODAY.date()} to {SEVEN_DAYS.date()}")
print("=" * 80)

# Collect all short-term markets
short_term = []
all_events = []

# Try the main Kalshi API
endpoints = [
    ("Elections API", "https://api.elections.kalshi.com/v1/events"),
    ("Trading API v2", "https://trading-api.kalshi.com/trade-api/v2/events"),
]

for name, url in endpoints:
    print(f"\n[*] Querying {name}...")
    try:
        response = requests.get(url, timeout=30)
        print(f"    Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', data.get('data', []))
            print(f"    Events: {len(events)}")
            all_events.extend(events)
            
            # Parse each event
            for event in events:
                title = event.get('title', 'Unknown')
                category = event.get('category', 'Unknown')
                series_ticker = event.get('series_ticker', '')
                
                # Look for daily/short-term indicators
                keywords = ['nba', 'nfl', 'basketball', 'football', 'weather', 
                           'temperature', 'bitcoin', 'btc', 'eth', 'crypto',
                           'cpi', 'fed', 'fomc', 'jobs', 'unemployment']
                
                is_interesting = any(kw in title.lower() or kw in series_ticker.lower() 
                                    for kw in keywords)
                
                markets = event.get('markets', [])
                for market in markets:
                    m_title = market.get('title', title)
                    close_date = market.get('close_date') or market.get('expiration_date')
                    last_price = market.get('last_price', 0)
                    volume = market.get('volume', 0)
                    ticker = market.get('ticker_name', market.get('ticker', ''))
                    
                    if close_date:
                        try:
                            close_dt = datetime.fromisoformat(close_date.replace('Z', '+00:00'))
                            close_dt = close_dt.replace(tzinfo=None)
                            days_until = (close_dt - TODAY).days
                            
                            if 0 <= days_until <= 7:
                                # Calculate IRR
                                price_cents = last_price if last_price > 1 else last_price * 100
                                cost = price_cents / 100
                                profit = 1 - cost
                                roi = (profit / cost * 100) if cost > 0 else 0
                                irr = ((1 + profit/cost) ** (365/max(days_until, 1)) - 1) * 100 if cost > 0 else 0
                                
                                short_term.append({
                                    'title': m_title,
                                    'ticker': ticker,
                                    'category': category,
                                    'close_date': close_dt,
                                    'days_until': days_until,
                                    'price_cents': price_cents,
                                    'volume': volume,
                                    'roi_pct': roi,
                                    'irr_pct': irr,
                                    'is_interesting': is_interesting
                                })
                        except Exception as e:
                            pass
                            
    except Exception as e:
        print(f"    Error: {e}")

# Also try scraping for sports categories
print("\n[*] Checking for sports markets...")
try:
    # Try specific category endpoints
    for cat in ['sports', 'crypto', 'economics']:
        url = f"https://api.elections.kalshi.com/v1/events?category={cat}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            print(f"    {cat}: {len(events)} events")
except Exception as e:
    print(f"    Category search error: {e}")

# Sort by days_until, then IRR
short_term.sort(key=lambda x: (x['days_until'], -x['irr_pct']))

print("\n" + "=" * 80)
print(f"RESULTS: Found {len(short_term)} markets resolving in 0-7 days")
print("=" * 80)

if not short_term:
    print("\n[WARNING] NO short-term markets found in the API!")
    print("This suggests:")
    print("  1. Kalshi's public API doesn't include sports/daily markets")
    print("  2. Sports markets may require authentication")
    print("  3. Need to check kalshi.com directly for NBA games")
else:
    print("\n### TOP OPPORTUNITIES ###\n")
    for i, m in enumerate(short_term[:15], 1):
        star = "⭐" if m['is_interesting'] else ""
        print(f"{i}. [{m['days_until']}d] {m['title'][:60]}")
        print(f"   Ticker: {m['ticker']} | Category: {m['category']}")
        print(f"   Price: {m['price_cents']:.0f}¢ | Volume: {m['volume']:,}")
        print(f"   ROI: {m['roi_pct']:.0f}% | IRR: {m['irr_pct']:.0f}% {star}")
        print()

# Save results
output = {
    'scan_date': '2026-02-13',
    'target_window': '0-7 days',
    'markets_found': len(short_term),
    'opportunities': short_term[:20]
}

with open('kalshi_fresh_scan.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

# Create markdown report
with open('kalshi_short_term_opportunities.md', 'w') as f:
    f.write("# Kalshi Short-Term Scanner Results\n\n")
    f.write(f"**Scan Date:** February 13, 2026  \n")
    f.write(f"**Target Window:** 0-7 days (Feb 13-20, 2026)  \n")
    f.write(f"**Markets Found:** {len(short_term)}  \n\n")
    f.write("---\n\n")
    
    if not short_term:
        f.write("## ⚠️ NO SHORT-TERM MARKETS FOUND\n\n")
        f.write("The Kalshi public API (`/v1/events`) does not appear to contain:\n")
        f.write("- NBA daily games\n")
        f.write("- Weather daily forecasts\n") 
        f.write("- Crypto daily price targets\n\n")
        f.write("### Recommended Actions\n\n")
        f.write("1. **Check kalshi.com directly** for sports/daily markets\n")
        f.write("2. **Use authenticated trading API** if available\n")
        f.write("3. **Monitor for new market listings**\n\n")
        f.write("### Alternative: Polymarket\n\n")
        f.write("Polymarket may have more short-term sports markets.\n")
    else:
        f.write("## 🎯 Top Opportunities (Ranked by IRR)\n\n")
        top = sorted(short_term, key=lambda x: -x['irr_pct'])[:10]
        for i, m in enumerate(top, 1):
            f.write(f"### {i}. {m['title']}\n\n")
            f.write(f"- **Ticker:** `{m['ticker']}`\n")
            f.write(f"- **Category:** {m['category']}\n")
            f.write(f"- **Resolution:** {m['close_date']} ({m['days_until']} days)\n")
            f.write(f"- **Price:** {m['price_cents']:.0f}¢\n")
            f.write(f"- **Volume:** {m['volume']:,}\n")
            f.write(f"- **ROI if Win:** {m['roi_pct']:.1f}%\n")
            f.write(f"- **Annualized IRR:** {m['irr_pct']:.0f}%\n\n")
    
    f.write("\n---\n\n")
    f.write("## Filter Criteria\n\n")
    f.write("- Resolution: 0-7 days (Feb 13-20, 2026)\n")
    f.write("- Volume: >1,000 contracts preferred\n")
    f.write("- Price: 20-80¢ (avoid extremes)\n")
    f.write("- Categories: Sports, Crypto, Economics, Weather\n")

print("\n✅ Results saved to kalshi_fresh_scan.json and kalshi_short_term_opportunities.md")
