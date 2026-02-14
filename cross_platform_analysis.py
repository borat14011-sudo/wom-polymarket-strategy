#!/usr/bin/env python3
"""Cross-platform prediction market analysis"""
import json
from datetime import datetime

# Load data
with open('active-markets.json', 'r') as f:
    pm_markets = json.load(f)

with open('kalshi_analysis.json', 'r') as f:
    kalshi_data = json.load(f)

print("=" * 60)
print("CROSS-PLATFORM MARKET ANALYSIS")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# Polymarket Analysis
print("\n[POLYMARKET SUMMARY]")
print(f"Total markets: {len(pm_markets)}")

# Parse and sort by volume
pm_sorted = sorted(pm_markets, key=lambda x: float(x.get('volumeNum', 0) or 0), reverse=True)

print("\n🔥 TOP 10 MARKETS BY VOLUME:")
for i, m in enumerate(pm_sorted[:10], 1):
    try:
        prices = json.loads(m.get('outcomePrices', '["0","0"]'))
        yes_price = float(prices[0]) if prices else 0
        vol = float(m.get('volumeNum', 0) or 0)
        vol_24h = float(m.get('volume24hr', 0) or 0)
        q = m.get('question', 'Unknown')[:60]
        print(f"  {i}. {q}...")
        print(f"     YES: {yes_price:.1%} | Vol: ${vol/1000:.0f}K | 24h: ${vol_24h/1000:.0f}K")
    except:
        pass

# Recent movers - high 24h volume
print("\n⚡ RECENT MOVERS (High 24h Volume):")
movers = sorted(pm_markets, key=lambda x: float(x.get('volume24hr', 0) or 0), reverse=True)[:10]
for m in movers:
    try:
        prices = json.loads(m.get('outcomePrices', '["0","0"]'))
        yes_price = float(prices[0]) if prices else 0
        vol_24h = float(m.get('volume24hr', 0) or 0)
        vol_1wk = float(m.get('volume1wk', 0) or 0)
        q = m.get('question', 'Unknown')[:55]
        
        # Calculate relative activity
        if vol_1wk > 0:
            daily_avg = vol_1wk / 7
            activity_ratio = vol_24h / daily_avg if daily_avg > 0 else 0
        else:
            activity_ratio = 0
            
        if vol_24h > 10000:
            print(f"  • {q}...")
            print(f"    YES: {yes_price:.1%} | 24h Vol: ${vol_24h/1000:.1f}K | Activity: {activity_ratio:.1f}x avg")
    except:
        pass

# Find Buy the Dip candidates - markets with low prices that had high past volume
print("\n📉 BUY THE DIP CANDIDATES (Low price, high historical volume):")
dips = [m for m in pm_markets if m.get('outcomePrices')]
dip_candidates = []
for m in dips:
    try:
        prices = json.loads(m['outcomePrices'])
        yes_price = float(prices[0])
        vol = float(m.get('volumeNum', 0) or 0)
        liq = float(m.get('liquidityNum', 0) or 0)
        
        # Low price (5-20%), decent volume, good liquidity
        if 0.05 <= yes_price <= 0.20 and vol > 50000 and liq > 5000:
            dip_candidates.append({
                'question': m['question'],
                'yes_price': yes_price,
                'volume': vol,
                'liquidity': liq,
                'slug': m.get('slug', '')
            })
    except:
        pass

dip_candidates.sort(key=lambda x: x['volume'], reverse=True)
for d in dip_candidates[:8]:
    print(f"  • {d['question'][:55]}...")
    print(f"    YES: {d['yes_price']:.1%} | Vol: ${d['volume']/1000:.0f}K | Liq: ${d['liquidity']/1000:.1f}K")

# Kalshi Summary
print("\n" + "=" * 60)
print("📊 KALSHI SUMMARY")
print(f"Total markets analyzed: {kalshi_data['summary']['total_markets']}")
print(f"High volume markets: {kalshi_data['summary']['high_volume_count']}")
print(f"Dip opportunities: {kalshi_data['summary']['dip_opportunities_count']}")

# ARBITRAGE OPPORTUNITIES
print("\n" + "=" * 60)
print("🔄 CROSS-PLATFORM COMPARISON")
print("Looking for overlapping markets...")

# Key topics to check across platforms
key_topics = ['bitcoin', 'btc', 'fed', 'rate', 'trump', 'deportation', 'inflation', 'gdp', 'unemployment']

pm_by_topic = {}
for topic in key_topics:
    matches = [m for m in pm_markets if topic.lower() in m.get('question', '').lower()]
    if matches:
        pm_by_topic[topic] = matches

print("\n📈 POLYMARKET TOPIC COVERAGE:")
for topic, markets in pm_by_topic.items():
    if len(markets) > 0:
        print(f"  {topic.upper()}: {len(markets)} markets")
        top = sorted(markets, key=lambda x: float(x.get('volumeNum', 0) or 0), reverse=True)[0]
        try:
            prices = json.loads(top['outcomePrices'])
            print(f"    Top: {top['question'][:50]}... @ {float(prices[0]):.1%}")
        except:
            pass

# Save analysis results
analysis_results = {
    'timestamp': datetime.now().isoformat(),
    'polymarket_count': len(pm_markets),
    'kalshi_count': kalshi_data['summary']['total_markets'],
    'top_movers': [{'question': m['question'], 'vol_24h': float(m.get('volume24hr', 0) or 0)} for m in movers[:5]],
    'dip_candidates': dip_candidates[:5],
    'topics': {k: len(v) for k, v in pm_by_topic.items()}
}

with open('research_market_analysis.json', 'w') as f:
    json.dump(analysis_results, f, indent=2)

print("\n✅ Analysis saved to research_market_analysis.json")
