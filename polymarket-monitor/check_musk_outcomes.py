"""
Check if our Musk paper trades already resolved
These markets were for Jan 30 - Feb 6, 2026 (YESTERDAY!)
"""
import json

# Load our 721 opportunities
with open('live_opportunities_snapshot.json', 'r') as f:
    opportunities = json.load(f)

print("="*80)
print("CHECKING MUSK PAPER TRADES (Jan 30 - Feb 6, 2026)")
print("="*80)

# Find our 5 Musk trades
musk_trades = [
    "0-19 tweets",
    "20-39 tweets", 
    "200-219 tweets",
    "520-539 tweets",
    "540-559 tweets"
]

print(f"\nSearching for our 5 Musk markets in 721 opportunities...\n")

found_markets = []

for opp in opportunities:
    if opp.get('strategy') == 'MUSK_FADE_EXTREMES':
        question = opp.get('question', '')
        
        # Check if it's one of our targets
        for trade_desc in musk_trades:
            if trade_desc in question and "January 30 to February 6" in question:
                found_markets.append(opp)
                print(f"Found: {question[:70]}")
                print(f"  Current price: {opp.get('price', 'N/A'):.4f}")
                print(f"  Volume: ${opp.get('volume', 0)/1000:.0f}K")
                print(f"  Market ID: {opp.get('market_id')}")
                print()
                break

print(f"\nTotal found: {len(found_markets)}/5")

if len(found_markets) < 5:
    print("\nNOTE: These markets ended Feb 6 (yesterday)")
    print("      They likely already resolved!")
    print("      Need to check Polymarket API for outcomes")

# Check in historical data
print("\n" + "="*80)
print("CHECKING IN 17K ACTIVE MARKETS")
print("="*80)

with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
    markets = json.load(f)

print(f"Loaded {len(markets)} markets")

musk_jan30_feb6 = []

for m in markets:
    question = m.get('question', '')
    
    if 'musk' in question.lower() and 'January 30 to February 6' in question:
        musk_jan30_feb6.append(m)

print(f"\nFound {len(musk_jan30_feb6)} Musk markets for Jan 30 - Feb 6")

if musk_jan30_feb6:
    print("\nSample markets:")
    for m in musk_jan30_feb6[:10]:
        q = m.get('question')
        prices = m.get('price_history', [])
        latest_price = prices[-1]['p'] if prices else None
        
        print(f"\n  {q[:75]}")
        print(f"    Latest price: {latest_price:.4f if latest_price else 'N/A'}")
        print(f"    Price snapshots: {len(prices)}")
        
        # Check if extreme range
        if '0-19' in q or '20-39' in q or '200-219' in q or '520-539' in q or '540-559' in q:
            print(f"    ✓ MATCHES OUR TRADE")
