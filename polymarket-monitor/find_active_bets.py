"""
Find ACTIVE markets we can bet on RIGHT NOW
Filter out anything that already ended
"""
import json
from datetime import datetime

print("="*80)
print("FINDING ACTIVE MARKETS FOR REAL-TIME PAPER TRADING")
print("="*80)

# Load our 721 opportunities
with open('live_opportunities_snapshot.json', 'r') as f:
    opportunities = json.load(f)

print(f"\nTotal opportunities: {len(opportunities)}")

# Load full market data to check end dates
with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
    all_markets = json.load(f)

print(f"Total markets in dataset: {len(all_markets)}")

# Create lookup by market_id
market_lookup = {m.get('market_id'): m for m in all_markets}

# Filter for FUTURE end dates
print("\n[FILTERING] Looking for markets ending in the future...")

active_opportunities = []
today = datetime.now()

for opp in opportunities:
    market_id = opp.get('market_id')
    
    if market_id in market_lookup:
        market = market_lookup[market_id]
        end_date_str = market.get('end_date')
        
        if end_date_str:
            try:
                # Parse end date (format: 2026-02-10T00:00:00Z or similar)
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                
                # Check if in future
                if end_date > today:
                    opp['end_date'] = end_date_str
                    active_opportunities.append(opp)
            except:
                pass

print(f"\n[RESULT] Found {len(active_opportunities)} active markets")

# Breakdown by strategy
from collections import Counter
strategy_counts = Counter([o['strategy'] for o in active_opportunities])

print(f"\n[BREAKDOWN] By strategy:")
for strategy, count in strategy_counts.most_common():
    print(f"  {strategy:30} {count:4} markets")

# Show top 10 by strategy
print("\n" + "="*80)
print("TOP 10 ACTIVE OPPORTUNITIES (Highest Win Rate)")
print("="*80)

# Sort by expected win rate
active_opportunities.sort(key=lambda o: o['expected_win'], reverse=True)

for i, opp in enumerate(active_opportunities[:10], 1):
    print(f"\n{i}. [{opp['strategy']}] Win: {opp['expected_win']:.1f}%")
    print(f"   {opp['question'][:70]}")
    print(f"   Price: {opp['price']:.4f} | Volume: ${opp['volume']/1000:.0f}K")
    print(f"   End date: {opp.get('end_date', 'Unknown')}")

# Save active opportunities
output_file = 'active_opportunities.json'
with open(output_file, 'w') as f:
    json.dump(active_opportunities, f, indent=2)

print(f"\n[SAVED] {output_file}")
print(f"  {len(active_opportunities)} active markets ready for paper trading")
