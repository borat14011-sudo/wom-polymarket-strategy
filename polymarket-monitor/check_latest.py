#!/usr/bin/env python3
"""Check the actual latest checkpoint"""
import json
from pathlib import Path

DATA_DIR = Path("historical-data-scraper/data")

# Find the highest numbered checkpoint
checkpoints = []
for f in DATA_DIR.glob("prices_checkpoint_*.json"):
    try:
        num = int(f.stem.split('_')[-1])
        checkpoints.append((num, f))
    except:
        pass

if checkpoints:
    checkpoints.sort(key=lambda x: x[0])
    latest_num, latest_file = checkpoints[-1]
    
    print(f"Latest checkpoint: {latest_num:,} tokens")
    print(f"File: {latest_file.name}")
    print(f"Size: {latest_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    print("\nLoading data...")
    with open(latest_file) as f:
        data = json.load(f)
    
    total = len(data)
    success = len([d for d in data if d.get('success')])
    has_prices = len([d for d in data if d.get('success') and len(d.get('prices', [])) > 0])
    
    print(f"\nTotal tokens: {total:,}")
    print(f"Success: {success:,} ({success/total*100:.1f}%)")
    print(f"With price data: {has_prices:,} ({has_prices/total*100:.1f}%)")
    
    # Sample a successful one
    successful = [d for d in data if d.get('success') and d.get('prices')]
    if successful:
        sample = successful[0]
        print(f"\nSample token: {sample['token_id']}")
        print(f"Price points: {len(sample['prices'])}")
        if sample['prices']:
            first_price = sample['prices'][0]
            print(f"First timestamp: {first_price.get('t', 'N/A')}")
