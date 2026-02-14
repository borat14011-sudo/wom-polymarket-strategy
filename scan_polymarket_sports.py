#!/usr/bin/env python3
"""
Polymarket Short-Term Scanner with Sports Focus
Feb 13, 2026
"""

import requests
import json
from datetime import datetime, timedelta

TODAY = datetime(2026, 2, 13)
SEVEN_DAYS = TODAY + timedelta(days=7)

print("POLYMARKET SHORT-TERM SCANNER")
print("=" * 70)

# Polymarket CLOB API
url = "https://clob.polymarket.com/markets"
params = {"active": "true", "limit": 500}

try:
    response = requests.get(url, params=params, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        markets = response.json()
        print(f"Total active markets: {len(markets)}")
        
        short_term = []
        sports = []
        
        # Sports keywords
        sports_kw = ["nba", "nfl", "basketball", "football", "lakers", "celtics", 
                    "warriors", "knicks", "bulls", "heat", "bucks", "nets", "76ers",
                    "super bowl", "championship", "playoffs", "mvp", "game", "score"]
        
        for m in markets:
            end_date = m.get("end_date_iso") or m.get("expiration_time")
            question = m.get("question", "")
            
            # Check for sports
            q_lower = question.lower()
            is_sports = any(kw in q_lower for kw in sports_kw)
            
            if is_sports:
                sports.append({
                    "q": question[:100],
                    "end": end_date,
                    "price": m.get("last_trade_price"),
                    "volume": m.get("volume", 0)
                })
            
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                    end_dt = end_dt.replace(tzinfo=None)
                    days_until = (end_dt - TODAY).days
                    
                    if 0 <= days_until <= 7:
                        price = float(m.get("last_trade_price") or 0.5)
                        volume = float(m.get("volume") or 0)
                        
                        # Calculate IRR
                        if 0 < price < 1:
                            roi = (1 - price) / price * 100
                            irr = ((1 + (1-price)/price) ** (365/max(days_until, 1)) - 1) * 100
                        else:
                            roi = 0
                            irr = 0
                        
                        short_term.append({
                            "question": question,
                            "days": days_until,
                            "price": price,
                            "volume": volume,
                            "roi": roi,
                            "irr": irr,
                            "end": end_date,
                            "is_sports": is_sports
                        })
                except:
                    pass
        
        print(f"\nSports-related markets found: {len(sports)}")
        print("-" * 70)
        for s in sports[:15]:
            print(f"  - {s['q']}")
            print(f"    End: {s['end']} | Price: {s['price']}")
        
        print(f"\n\nSHORT-TERM (0-7 days): {len(short_term)} markets")
        print("=" * 70)
        
        # Sort by days, then by IRR
        short_term.sort(key=lambda x: (x["days"], -x["irr"]))
        
        for i, m in enumerate(short_term[:20], 1):
            star = "[SPORTS]" if m["is_sports"] else ""
            print(f"\n{i}. [{m['days']}d] {m['question'][:70]}")
            print(f"   Price: {m['price']:.2f} ({int(m['price']*100)}c) | Volume: ${m['volume']:,.0f}")
            print(f"   ROI: {m['roi']:.0f}% | IRR: {m['irr']:.0f}% {star}")
        
        # Save results
        results = {
            "scan_date": "2026-02-13",
            "platform": "Polymarket",
            "total_markets": len(markets),
            "sports_markets": len(sports),
            "short_term_markets": len(short_term),
            "opportunities": short_term[:30],
            "sports_list": sports[:20]
        }
        
        with open("polymarket_short_term_scan.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n\nSaved to polymarket_short_term_scan.json")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
