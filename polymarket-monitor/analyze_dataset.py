#!/usr/bin/env python3
"""
Analyze the dataset to optimize fetch strategy
"""
import json
from collections import Counter
from datetime import datetime

print("Loading data...")
with open('historical-data-scraper/data/polymarket_complete.json') as f:
    data = json.load(f)

print(f"\n{'='*60}")
print(f"DATASET ANALYSIS")
print(f"{'='*60}\n")

# Basic stats
print(f"Total events: {len(data):,}")

# Count markets and tokens
total_markets = 0
total_tokens = 0
volumes = []
active_events = 0
closed_events = 0

for event in data:
    markets = event.get('markets', [])
    total_markets += len(markets)
    
    volume = event.get('volume', 0)
    if volume is not None and volume != 0:
        try:
            volume = float(volume)
            volumes.append(volume)
        except (ValueError, TypeError):
            pass
    
    if event.get('closed'):
        closed_events += 1
    if event.get('active'):
        active_events += 1
    
    for market in markets:
        token_ids = market.get('clob_token_ids', '[]')
        if isinstance(token_ids, str):
            try:
                token_ids = json.loads(token_ids)
                total_tokens += len(token_ids)
            except:
                pass

print(f"Total markets: {total_markets:,}")
print(f"Total tokens: {total_tokens:,}")
print(f"Active events: {active_events:,}")
print(f"Closed events: {closed_events:,}")

# Volume analysis
if volumes:
    volumes.sort(reverse=True)
    print(f"\n{'='*60}")
    print(f"VOLUME DISTRIBUTION")
    print(f"{'='*60}\n")
    print(f"Total markets with volume: {len(volumes):,}")
    print(f"Total volume: ${sum(volumes):,.0f}")
    print(f"Average volume: ${sum(volumes)/len(volumes):,.0f}")
    print(f"Median volume: ${volumes[len(volumes)//2]:,.0f}")
    print(f"Top volume: ${volumes[0]:,.0f}")
    
    # Volume thresholds
    thresholds = [1000, 10000, 100000, 1000000]
    print(f"\nMarkets by volume threshold:")
    for threshold in thresholds:
        count = len([v for v in volumes if v >= threshold])
        pct = count / len(volumes) * 100
        print(f"  >${threshold:,}: {count:,} markets ({pct:.1f}%)")

# Date range
dates = []
for event in data:
    start = event.get('start_date')
    if start:
        try:
            dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            dates.append(dt)
        except:
            pass

if dates:
    dates.sort()
    print(f"\n{'='*60}")
    print(f"DATE RANGE")
    print(f"{'='*60}\n")
    print(f"Earliest: {dates[0].strftime('%Y-%m-%d')}")
    print(f"Latest: {dates[-1].strftime('%Y-%m-%d')}")
    print(f"Span: {(dates[-1] - dates[0]).days} days")

# Estimate fetch time
print(f"\n{'='*60}")
print(f"FETCH STRATEGY RECOMMENDATIONS")
print(f"{'='*60}\n")

# Full fetch
rate_per_sec = 50  # Conservative with 50 concurrent
total_time_sec = total_tokens / rate_per_sec
print(f"Full fetch ({total_tokens:,} tokens):")
print(f"  Estimated time: {total_time_sec/3600:.1f} hours @ {rate_per_sec}/sec")
print(f"  Estimated data size: ~{total_tokens * 50 / 1024 / 1024:.0f} MB")

# Volume-filtered fetch
high_vol_events = len([v for v in volumes if v >= 1000])
estimated_tokens = high_vol_events * (total_tokens / len(data))
filtered_time_sec = estimated_tokens / rate_per_sec

print(f"\nFiltered fetch (volume > $1,000):")
print(f"  Events: {high_vol_events:,} ({high_vol_events/len(data)*100:.1f}%)")
print(f"  Estimated tokens: {estimated_tokens:,.0f}")
print(f"  Estimated time: {filtered_time_sec/3600:.1f} hours @ {rate_per_sec}/sec")
print(f"  Estimated data size: ~{estimated_tokens * 50 / 1024 / 1024:.0f} MB")

# Super filtered
super_vol_events = len([v for v in volumes if v >= 10000])
super_tokens = super_vol_events * (total_tokens / len(data))
super_time_sec = super_tokens / rate_per_sec

print(f"\nSuper filtered (volume > $10,000):")
print(f"  Events: {super_vol_events:,} ({super_vol_events/len(data)*100:.1f}%)")
print(f"  Estimated tokens: {super_tokens:,.0f}")
print(f"  Estimated time: {super_time_sec/60:.1f} minutes @ {rate_per_sec}/sec")
print(f"  Estimated data size: ~{super_tokens * 50 / 1024 / 1024:.0f} MB")

print(f"\n{'='*60}")
print(f"RECOMMENDATION: Start with $10K+ volume markets")
print(f"This captures the most liquid/active markets for strategy testing")
print(f"Can always expand later if needed")
print(f"{'='*60}\n")
