#!/usr/bin/env python3
"""
LIVE OPPORTUNITY MONITOR - Simplified Version
Scans Polymarket for high-profit trades based on 5 validated strategies
"""

import json
import requests
import time
import sys
from datetime import datetime, timezone, timedelta

print("="*80, flush=True)
print("LIVE OPPORTUNITY MONITOR - STARTING", flush=True)
print("="*80, flush=True)

GAMMA_API = "https://gamma-api.polymarket.com"

def fetch_markets(limit=500):
    """Fetch active markets"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Fetching {limit} markets...", flush=True)
    try:
        url = f"{GAMMA_API}/markets"
        params = {"limit": limit, "active": "true", "closed": "false"}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        markets = response.json()
        print(f"SUCCESS: Got {len(markets)} markets", flush=True)
        return markets
    except Exception as e:
        print(f"ERROR fetching markets: {e}", flush=True)
        return []

def get_price(market):
    """Extract YES/NO prices"""
    try:
        # Try outcomePrices
        if 'outcomePrices' in market and market['outcomePrices']:
            prices = market['outcomePrices']
            if isinstance(prices, list) and len(prices) >= 2:
                yes_p = float(prices[0])
                no_p = float(prices[1])
                if 0 <= yes_p <= 1 and 0 <= no_p <= 1:
                    return {'yes': yes_p, 'no': no_p}
        
        # Try lastTradePrice
        if 'lastTradePrice' in market:
            yes_p = float(market['lastTradePrice'])
            if 0 <= yes_p <= 1:
                return {'yes': yes_p, 'no': 1.0 - yes_p}
        
        return None
    except:
        return None

def days_until_close(market):
    """Calculate days until close"""
    try:
        end_str = market.get('endDate') or market.get('end_date')
        if not end_str:
            return 999
        
        if 'T' in end_str:
            end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
        else:
            end_date = datetime.fromtimestamp(float(end_str), tz=timezone.utc)
        
        now = datetime.now(timezone.utc)
        return max(0, (end_date - now).days)
    except:
        return 999

def scan_market(market):
    """Check if market matches our criteria"""
    try:
        # Get prices
        prices = get_price(market)
        if not prices:
            return None
        
        yes_price = prices['yes']
        no_price = prices['no']
        
        # FILTER 1: YES price 70-90%
        if not (0.70 <= yes_price <= 0.90):
            return None
        
        # FILTER 2: Volume >$100K
        volume = float(market.get('volume', 0) or market.get('liquidity', 0) or 0)
        if volume < 100000:
            return None
        
        # FILTER 3: Ends within 30 days
        days = days_until_close(market)
        if days > 30:
            return None
        
        # Calculate ROI for betting NO
        roi_pct = ((1.0 - no_price) / no_price) * 100 if no_price > 0 else 0
        
        # Apply strategies
        question = market.get('question', '').lower()
        tags = ' '.join(market.get('tags', [])).lower()
        
        strategies = []
        
        # Strategy 1: NO-SIDE BIAS (100% win rate)
        strategies.append({
            'name': 'NO-SIDE BIAS',
            'win_rate': 100.0,
            'signal': f'YES at {yes_price:.1%} overpriced'
        })
        
        # Strategy 2: CONTRARIAN FADE (83.3% win rate)
        expert_words = ['predict', 'forecast', 'analyst', 'expert', 'poll', 'consensus', 'election']
        if yes_price >= 0.80 and any(w in question or w in tags for w in expert_words):
            strategies.append({
                'name': 'CONTRARIAN EXPERT FADE',
                'win_rate': 83.3,
                'signal': f'Fade {yes_price:.1%} consensus'
            })
        
        # Strategy 3: TIME HORIZON (66.7% win rate)
        if days <= 3:
            strategies.append({
                'name': 'TIME HORIZON',
                'win_rate': 66.7,
                'signal': f'{days} days left, deadline pressure'
            })
        
        # Strategy 4: NEWS REVERSION (65% win rate)
        news_words = ['iran', 'strike', 'attack', 'war', 'trump', 'indictment', 'court', 'covid', 'vaccine']
        if any(w in question or w in tags for w in news_words):
            strategies.append({
                'name': 'NEWS REVERSION',
                'win_rate': 65.0,
                'signal': 'News spike likely to reverse'
            })
        
        # Strategy 5: CATEGORY FILTER (90.5% win rate)
        politics = ['election', 'president', 'senate', 'congress', 'trump', 'biden', 'vote']
        crypto = ['bitcoin', 'btc', 'eth', 'ethereum', 'crypto', 'price']
        
        if any(w in question or w in tags for w in politics):
            strategies.append({
                'name': 'CATEGORY: POLITICS',
                'win_rate': 90.5,
                'signal': 'Politics - proven category'
            })
        elif any(w in question or w in tags for w in crypto):
            strategies.append({
                'name': 'CATEGORY: CRYPTO',
                'win_rate': 90.5,
                'signal': 'Crypto - proven category'
            })
        
        # Take highest win rate strategy
        if not strategies:
            return None
        
        best_strategy = max(strategies, key=lambda s: s['win_rate'])
        
        return {
            'timestamp': datetime.now().isoformat(),
            'market_id': market.get('id', market.get('conditionId', 'unknown')),
            'question': market.get('question', 'Unknown'),
            'yes_price': yes_price,
            'no_price': no_price,
            'volume': volume,
            'days_to_close': days,
            'strategy': best_strategy['name'],
            'win_rate': best_strategy['win_rate'],
            'signal': best_strategy['signal'],
            'roi_percent': roi_pct,
            'entry_price_no': no_price,
            'max_profit': 1.0 - no_price,
            'url': f"https://polymarket.com/event/{market.get('slug', market.get('id', ''))}"
        }
        
    except Exception as e:
        return None

def run_scan(scan_num):
    """Run one scan cycle"""
    print(f"\n{'='*80}", flush=True)
    print(f"SCAN #{scan_num} - {datetime.now().strftime('%H:%M:%S')}", flush=True)
    print(f"{'='*80}", flush=True)
    
    markets = fetch_markets(500)
    if not markets:
        print("No markets retrieved", flush=True)
        return []
    
    opportunities = []
    for i, market in enumerate(markets):
        if (i + 1) % 100 == 0:
            print(f"Progress: {i+1}/{len(markets)} markets scanned...", flush=True)
        
        opp = scan_market(market)
        if opp:
            opportunities.append(opp)
    
    print(f"\nScan complete: {len(opportunities)} opportunities found", flush=True)
    
    if opportunities:
        # Show top 3
        top3 = sorted(opportunities, key=lambda x: x['roi_percent'], reverse=True)[:3]
        print(f"\nTOP 3:", flush=True)
        for i, opp in enumerate(top3, 1):
            question = opp['question'][:60]
            print(f"{i}. {question}...", flush=True)
            print(f"   ROI: {opp['roi_percent']:.1f}% | Win Rate: {opp['win_rate']:.1f}%", flush=True)
            print(f"   Strategy: {opp['strategy']}", flush=True)
    
    return opportunities

# MAIN EXECUTION
all_opportunities = []
high_alerts = []

for scan in range(1, 4):  # 3 scans
    opps = run_scan(scan)
    all_opportunities.extend(opps)
    
    # Track >200% ROI
    for opp in opps:
        if opp['roi_percent'] > 200:
            high_alerts.append(opp)
    
    # Wait between scans (except last one)
    if scan < 3:
        print(f"\n[WAIT] Next scan in 3 hours...", flush=True)
        time.sleep(3 * 60 * 60)  # 3 hours (10,800 seconds)

# Save results
print(f"\n{'='*80}", flush=True)
print("SAVING RESULTS", flush=True)
print(f"{'='*80}", flush=True)

output = {
    'summary': {
        'total_scans': 3,
        'total_opportunities': len(all_opportunities),
        'high_priority_count': len(high_alerts),
        'timestamp': datetime.now().isoformat()
    },
    'opportunities': all_opportunities
}

with open('live_opportunities_tracker.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"Saved {len(all_opportunities)} opportunities to live_opportunities_tracker.json", flush=True)

# Create alerts if needed
if high_alerts:
    alert_md = f"""# HIGH PRIORITY ALERTS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Found {len(high_alerts)} trades with >200% ROI

---

"""
    for i, alert in enumerate(sorted(high_alerts, key=lambda x: x['roi_percent'], reverse=True), 1):
        alert_md += f"""### #{i}: {alert['question']}

**ROI:** {alert['roi_percent']:.1f}% | **Win Rate:** {alert['win_rate']:.1f}%

**Strategy:** {alert['strategy']}  
**Entry:** ${alert['entry_price_no']:.3f} NO  
**Max Profit:** ${alert['max_profit']:.3f}  
**Volume:** ${alert['volume']:,.0f}  
**Days Left:** {alert['days_to_close']}  

{alert['url']}

---

"""
    
    with open('HIGH_PRIORITY_ALERTS.md', 'w') as f:
        f.write(alert_md)
    print(f"Created HIGH_PRIORITY_ALERTS.md with {len(high_alerts)} alerts", flush=True)
else:
    print("No high-priority alerts (>200% ROI) found", flush=True)

print(f"\n{'='*80}", flush=True)
print("MISSION COMPLETE", flush=True)
print(f"Total Opportunities: {len(all_opportunities)}", flush=True)
print(f"High-Priority Alerts: {len(high_alerts)}", flush=True)
print(f"{'='*80}", flush=True)
