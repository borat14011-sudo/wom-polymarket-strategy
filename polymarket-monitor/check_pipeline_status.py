#!/usr/bin/env python3
"""Quick status checker for pipeline"""
from pathlib import Path
import json

DATA_DIR = Path("historical-data-scraper/data")
OUTPUT_DIR = Path("backtest-results")

print("PIPELINE STATUS CHECK")
print("="*60)

# Check for checkpoints
checkpoints = sorted(DATA_DIR.glob("prices_checkpoint_*.json"))
if checkpoints:
    latest = checkpoints[-1]
    with open(latest) as f:
        data = json.load(f)
    success = len([r for r in data if r.get('success')])
    print(f"Latest checkpoint: {latest.name}")
    print(f"  Tokens fetched: {len(data):,}")
    print(f"  Successful: {success:,} ({success/len(data)*100:.1f}%)")
else:
    print("No checkpoints yet - pipeline starting...")

# Check completion
if (OUTPUT_DIR / "PIPELINE_COMPLETE.txt").exists():
    print("\n[COMPLETE] Pipeline finished!")
    with open(OUTPUT_DIR / "PIPELINE_COMPLETE.txt") as f:
        print(f.read())
else:
    print("\n[IN PROGRESS] Pipeline still running...")

print("="*60)
