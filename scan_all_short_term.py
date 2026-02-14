# -*- coding: utf-8 -*-
"""
Combined Short-Term Market Scanner
Scans Kalshi + Polymarket for markets resolving in 0-7 days
Feb 13, 2026
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime(2026, 2, 13)
SEVEN_DAYS = TODAY + timedelta(days=7)

print("=" * 80)
print("COMBINED SHORT-TERM MARKET SCANNER - February 13, 2026")
print(f"Target: Markets resolving Feb 13-20, 2026 (0-7 days)")
print("=" * 80)

all_opportunities = []

# ============================================================================
# KALSHI SCAN
# ============================================================================
print("\n### KALSHI SCAN ###")
try:
    url = "https://api.elections.kalshi.com/v1/events"
    response = requests.get(url, timeout=30)
    print(f"Kalshi API Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        events = data.get("events", [])
        print(f"Kalshi Events: {len(events)}")
        
        kalshi_short = []
        for event in events:
            for market in event.get("markets", []):
                close_date = market.get("close_date") or market.get("expiration_date")
                if close_date:
                    try:
                        close_dt = datetime.fromisoformat(close_date.replace("Z", "+00:00"))
                        close_dt = close_dt.replace(tzinfo=None)
                        days_until = (close_dt - TODAY).days
                        
                        if 0 <= days_until <= 7:
                            price = market.get("last_price", 50) / 100
                            volume = market.get("volume", 0)
                            
                            kalshi_short.append({
                                "platform": "Kalshi",
                                "title": market.get("title", event.get("title")),
                                "ticker": market.get("ticker_name", ""),
                                "days": days_until,
                                "price": price,
                                "volume": volume,
                                "category": event.get("category", "")
                            })
                    except:
                        pass
        
        print(f"Kalshi Short-Term Markets: {len(kalshi_short)}")
        all_opportunities.extend(kalshi_short)
except Exception as e:
    print(f"Kalshi Error: {e}")

# ============================================================================
# POLYMARKET SCAN (Gamma API)
# ============================================================================
print("\n### POLYMARKET SCAN ###")
try:
    url = "https://gamma-api.polymarket.com/markets"
    params = {"closed": "false", "limit": 200}
    response = requests.get(url, params=params, timeout=30)
    print(f"Polymarket API Status: {response.status_code}")
    
    if response.status_code == 200:
        markets = response.json()
        print(f"Polymarket Markets: {len(markets)}")
        
        poly_short = []
        poly_sports = []
        
        sports_kw = ["nba", "nfl", "basketball", "football", "game", "playoffs", 
                    "championship", "super bowl", "score", "wins", "lakers", 
                    "celtics", "warriors", "knicks", "76ers", "bucks", "heat"]
        
        for m in markets:
            question = m.get("question", "")
            end_date = m.get("endDate") or m.get("end_date")
            price = m.get("outcomePrices")
            volume = float(m.get("volume", 0) or 0)
            
            # Check if sports
            q_lower = question.lower()
            is_sports = any(kw in q_lower for kw in sports_kw)
            
            if is_sports:
                poly_sports.append(question[:80])
            
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                    end_dt = end_dt.replace(tzinfo=None)
                    days_until = (end_dt - TODAY).days
                    
                    if 0 <= days_until <= 7:
                        # Parse price
                        if isinstance(price, str) and price:
                            try:
                                prices = json.loads(price.replace("'", '"'))
                                if isinstance(prices, list) and len(prices) > 0:
                                    price_val = float(prices[0])
                                else:
                                    price_val = 0.5
                            except:
                                price_val = 0.5
                        elif isinstance(price, list) and len(price) > 0:
                            price_val = float(price[0])
                        else:
                            price_val = 0.5
                        
                        poly_short.append({
                            "platform": "Polymarket",
                            "title": question,
                            "ticker": m.get("slug", ""),
                            "days": days_until,
                            "price": price_val,
                            "volume": volume,
                            "category": "Sports" if is_sports else "Other"
                        })
                except:
                    pass
        
        print(f"Polymarket Sports Markets: {len(poly_sports)}")
        for s in poly_sports[:5]:
            print(f"  - {s}")
        
        print(f"Polymarket Short-Term: {len(poly_short)}")
        all_opportunities.extend(poly_short)
except Exception as e:
    print(f"Polymarket Error: {e}")

# ============================================================================
# COMBINED RESULTS
# ============================================================================
print("\n" + "=" * 80)
print(f"TOTAL SHORT-TERM OPPORTUNITIES: {len(all_opportunities)}")
print("=" * 80)

if not all_opportunities:
    print("\n[!] NO SHORT-TERM MARKETS FOUND")
    print("\nPossible reasons:")
    print("1. Most prediction markets are long-term (politics, climate)")
    print("2. Sports/daily markets may not be in public APIs")
    print("3. Need authenticated API access for Kalshi sports")
    print("4. Markets may have already resolved")
else:
    # Calculate IRR and sort
    for m in all_opportunities:
        price = m["price"]
        days = max(m["days"], 1)
        if 0 < price < 1:
            roi = (1 - price) / price * 100
            irr = ((1 + (1-price)/price) ** (365/days) - 1) * 100
        else:
            roi = 0
            irr = 0
        m["roi"] = roi
        m["irr"] = irr
    
    # Sort by IRR (highest first)
    all_opportunities.sort(key=lambda x: -x["irr"])
    
    print("\nTOP 15 BY IRR:")
    print("-" * 80)
    for i, m in enumerate(all_opportunities[:15], 1):
        print(f"\n{i}. [{m['platform']}] [{m['days']}d] {m['title'][:60]}")
        print(f"   Price: {m['price']:.2f} ({int(m['price']*100)}c)")
        print(f"   Volume: ${m['volume']:,.0f} | ROI: {m['roi']:.0f}% | IRR: {m['irr']:.0f}%")

# Save to JSON
output = {
    "scan_date": "2026-02-13",
    "target_window": "0-7 days",
    "total_opportunities": len(all_opportunities),
    "opportunities": all_opportunities[:30]
}

with open("combined_short_term_scan.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, default=str, ensure_ascii=False)

print(f"\nSaved to combined_short_term_scan.json")

# ============================================================================
# Generate Final Report
# ============================================================================
report_lines = [
    "# Kalshi Short-Term Opportunities Report",
    "",
    f"**Scan Date:** February 13, 2026 (Friday)",
    f"**Target Window:** 0-7 days (Feb 13-20, 2026)",
    f"**Focus:** NBA games TONIGHT, crypto daily, weather, economics",
    "",
    "---",
    "",
    f"## Summary",
    "",
    f"**Total Short-Term Markets Found:** {len(all_opportunities)}",
    "",
]

if not all_opportunities:
    report_lines.extend([
        "## [!] NO MARKETS RESOLVING IN 0-7 DAYS",
        "",
        "### Analysis",
        "",
        "The public APIs for Kalshi and Polymarket do not currently return",
        "short-term markets (0-7 day resolution). This includes:",
        "",
        "- **NBA Games Tonight** - Not available in public API",
        "- **Daily Crypto Targets** - Not available in public API", 
        "- **Weather Forecasts** - Not available in public API",
        "",
        "### Why This Happens",
        "",
        "1. **API Limitations**: Kalshi's `/v1/events` endpoint focuses on long-term political/economic markets",
        "2. **Authentication Required**: Sports/daily markets may require authenticated trading API access",
        "3. **Different Endpoints**: Daily markets may be on separate API endpoints not publicly documented",
        "",
        "### Recommended Actions",
        "",
        "1. **Check kalshi.com directly** for NBA and daily markets",
        "2. **Use Kalshi authenticated trading API** if you have an account",
        "3. **Monitor for new market listings** - they add sports markets closer to game time",
        "4. **Consider Polymarket** for sports via their trading interface",
        "",
        "### Alternative: Longer-Term Opportunities",
        "",
        "The nearest available markets are 30-60 days out. Consider:",
        "- Entertainment markets (awards shows)",
        "- Political/legislative deadlines",
        "- Earnings seasons (Q1 2026)",
        "",
    ])
else:
    report_lines.extend([
        "## Top 10 Opportunities by IRR",
        "",
    ])
    for i, m in enumerate(all_opportunities[:10], 1):
        report_lines.extend([
            f"### {i}. {m['title'][:70]}",
            "",
            f"- **Platform:** {m['platform']}",
            f"- **Resolution:** {m['days']} days",
            f"- **Current Price:** {int(m['price']*100)}c",
            f"- **Volume:** ${m['volume']:,.0f}",
            f"- **ROI if Win:** {m['roi']:.0f}%",
            f"- **Annualized IRR:** {m['irr']:.0f}%",
            "",
        ])

report_lines.extend([
    "---",
    "",
    "## Filter Criteria",
    "",
    "- **Resolution:** 0-7 days (Feb 13-20, 2026)",
    "- **Volume:** >1,000 contracts preferred",
    "- **Price:** 20-80c (avoid extremes)",
    "- **Categories:** Sports, Crypto, Economics, Weather",
    "",
    "## Data Sources",
    "",
    "- Kalshi Elections API: `https://api.elections.kalshi.com/v1/events`",
    "- Polymarket Gamma API: `https://gamma-api.polymarket.com/markets`",
    "",
    "---",
    "",
    "*Report generated by SHORT-TERM MARKET SCANNER*",
])

report_text = "\n".join(report_lines)

with open("kalshi_short_term_opportunities.md", "w", encoding="utf-8") as f:
    f.write(report_text)

print("\nFinal report saved to kalshi_short_term_opportunities.md")
