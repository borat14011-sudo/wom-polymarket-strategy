#!/usr/bin/env python3
"""Quick progress check on resume fetcher"""
from pathlib import Path
import json
from datetime import datetime

DATA_DIR = Path("historical-data-scraper/data")

# Find all checkpoints
checkpoints = []
for f in DATA_DIR.glob("prices_checkpoint_*.json"):
    try:
        num = int(f.stem.split('_')[-1])
        size_mb = f.stat().st_size / 1024 / 1024
        modified = datetime.fromtimestamp(f.stat().st_mtime)
        checkpoints.append((num, f, size_mb, modified))
    except:
        pass

checkpoints.sort(key=lambda x: x[0])

print(f"\n{'='*70}")
print(f"FETCH PROGRESS CHECK")
print(f"{'='*70}\n")

if checkpoints:
    print(f"Checkpoints found: {len(checkpoints)}")
    print(f"\nLatest 5 checkpoints:")
    for num, f, size_mb, modified in checkpoints[-5:]:
        age_min = (datetime.now() - modified).total_seconds() / 60
        print(f"  {num:>6,} tokens | {size_mb:>6.1f} MB | {age_min:>4.0f} min ago")
    
    # Check for completion file
    complete_file = DATA_DIR / "prices_complete.json"
    if complete_file.exists():
        size_mb = complete_file.stat().st_size / 1024 / 1024
        modified = datetime.fromtimestamp(complete_file.stat().st_mtime)
        age_min = (datetime.now() - modified).total_seconds() / 60
        print(f"\n[COMPLETE] prices_complete.json exists!")
        print(f"  Size: {size_mb:.1f} MB")
        print(f"  Created: {age_min:.0f} min ago")
    else:
        print(f"\n[IN PROGRESS] No completion file yet")
        print(f"  Latest checkpoint: {checkpoints[-1][0]:,} tokens")
        print(f"  Still fetching...")
else:
    print("No checkpoints found - fetch hasn't started yet")

print(f"\n{'='*70}\n")
