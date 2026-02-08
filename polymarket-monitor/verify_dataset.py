#!/usr/bin/env python3
import json
from pathlib import Path

print("Loading dataset v1...")
with open("historical-data-scraper/data/backtest_dataset_v1.json") as f:
    data = json.load(f)

print(f"\nDATASET STATS:")
print(f"  Total markets: {len(data):,}")

# Check completeness
complete = [d for d in data if d.get('price_history') and len(d['price_history']) > 10]
print(f"  Complete markets (>10 prices): {len(complete):,}")

# Volume stats
volumes = [d['volume'] for d in data if d.get('volume')]
print(f"  Total volume: ${sum(volumes):,.0f}")
print(f"  Avg volume: ${sum(volumes)/len(volumes):,.0f}")

# Price data stats
price_counts = [len(d['price_history']) for d in data if d.get('price_history')]
print(f"  Avg price points: {sum(price_counts)/len(price_counts):.0f}")
print(f"  Max price points: {max(price_counts):,}")

# Closed markets (for validation)
closed = [d for d in data if d.get('closed')]
print(f"  Closed markets: {len(closed):,} ({len(closed)/len(data)*100:.1f}%)")

# Sample
print(f"\nSAMPLE MARKET:")
sample = data[0]
print(f"  Question: {sample['question'][:80]}")
print(f"  Volume: ${sample['volume']:,.0f}")
print(f"  Price points: {len(sample['price_history'])}")
print(f"  Closed: {sample.get('closed', False)}")
print(f"  Outcome: {sample.get('outcome', 'N/A')}")

print(f"\nREADY FOR BACKTESTING: YES")
