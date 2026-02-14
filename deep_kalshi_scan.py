# -*- coding: utf-8 -*-
"""
Deep Kalshi Scan - Check all existing data files
"""
import json
from datetime import datetime
import sys
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime(2026, 2, 13)

print("=" * 80)
print("DEEP KALSHI DATA SCAN")
print("=" * 80)

# Files to check
files = [
    "kalshi_full_events.json",
    "kalshi_events.json",
    "kalshi_markets_raw.json",
    "kalshi_scan_results.json"
]

all_short_term = []
all_sports = []
categories = {}

for filename in files:
    try:
        filepath = f"C:/Users/Borat/.openclaw/workspace/{filename}"
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        
        print(f"\n### {filename}")
        
        events = []
        if isinstance(data, dict):
            events = data.get('events', data.get('markets', [data]))
        elif isinstance(data, list):
            events = data
        
        print(f"Items: {len(events)}")
        
        for event in events:
            if not isinstance(event, dict):
                continue
                
            title = event.get('title', event.get('question', ''))
            category = event.get('category', 'Other')
            categories[category] = categories.get(category, 0) + 1
            
            # Check for sports/daily keywords
            title_lower = title.lower()
            is_sports = any(kw in title_lower for kw in 
                          ['nba', 'nfl', 'basketball', 'football', 'game', 
                           'score', 'lakers', 'celtics', 'weather', 'temperature'])
            
            if is_sports:
                all_sports.append(title[:70])
            
            # Check markets within event
            markets = event.get('markets', [event])
            for market in markets:
                if not isinstance(market, dict):
                    continue
                    
                close_date = market.get('close_date') or market.get('expiration_date') or market.get('end_date')
                if close_date:
                    try:
                        dt = datetime.fromisoformat(close_date.replace('Z', '+00:00'))
                        dt = dt.replace(tzinfo=None)
                        days = (dt - TODAY).days
                        if 0 <= days <= 7:
                            all_short_term.append({
                                'days': days,
                                'title': market.get('title', title),
                                'ticker': market.get('ticker_name', market.get('ticker', '')),
                                'price': market.get('last_price', 0),
                                'volume': market.get('volume', 0),
                                'category': category
                            })
                    except:
                        pass
    except Exception as e:
        print(f"Error with {filename}: {e}")

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

print(f"\nCategories found:")
for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:15]:
    print(f"  {cat}: {count}")

print(f"\nSports/Daily Markets: {len(all_sports)}")
for s in list(set(all_sports))[:15]:
    print(f"  - {s}")

print(f"\nSHORT-TERM (0-7 days): {len(all_short_term)}")
if all_short_term:
    all_short_term.sort(key=lambda x: x['days'])
    for m in all_short_term[:15]:
        days = m['days']
        title = m['title'][:50]
        price = m['price']
        vol = m['volume']
        print(f"  [{days}d] {title}")
        print(f"       Price: {price}c | Volume: {vol}")
else:
    print("  NO SHORT-TERM MARKETS FOUND")

# Save results
output = {
    "scan_date": "2026-02-13",
    "short_term_markets": len(all_short_term),
    "sports_markets": len(set(all_sports)),
    "categories": categories,
    "opportunities": all_short_term
}

with open("kalshi_deep_scan_results.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, default=str, ensure_ascii=False)

print("\nSaved to kalshi_deep_scan_results.json")
