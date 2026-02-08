#!/usr/bin/env python3
"""Quick status check of data collection"""
import json
from pathlib import Path

DATA_DIR = Path("historical-data-scraper/data")

# Check checkpoint files
checkpoint_files = sorted(DATA_DIR.glob("prices_checkpoint_*.json"))
print("DATA COLLECTION STATUS\n")
print(f"Checkpoint files found: {len(checkpoint_files)}")

if checkpoint_files:
    # Load latest checkpoint
    latest = checkpoint_files[-1]
    print(f"Latest checkpoint: {latest.name}")
    print(f"Size: {latest.stat().st_size / 1024 / 1024:.1f} MB")
    
    with open(latest) as f:
        data = json.load(f)
    
    total_tokens = len(data)
    success = len([d for d in data if d.get('success')])
    failed = total_tokens - success
    
    print(f"\nTokens fetched: {total_tokens:,}")
    print(f"  [OK] Success: {success:,} ({success/total_tokens*100:.1f}%)")
    print(f"  [FAIL] Failed: {failed:,} ({failed/total_tokens*100:.1f}%)")
    
    # Check if backtest dataset exists
    dataset_file = DATA_DIR / "backtest_dataset.json"
    if dataset_file.exists():
        print(f"\n[OK] Backtest dataset exists!")
        print(f"   Size: {dataset_file.stat().st_size / 1024 / 1024:.1f} MB")
        
        # Quick peek
        with open(dataset_file) as f:
            dataset = json.load(f)
        print(f"   Markets: {len(dataset):,}")
        
        if dataset:
            # Sample one market
            sample = dataset[0]
            print(f"\nSample market:")
            print(f"   Question: {sample.get('question', 'N/A')[:80]}...")
            print(f"   Volume: ${sample.get('volume', 0):,.0f}")
            print(f"   Price points: {len(sample.get('price_history', []))}")
    else:
        print(f"\n[WARN] Backtest dataset not built yet")
        print(f"   Need to run: Step 2 (build_analysis_dataset)")
else:
    print("No checkpoint files found - need to start fresh")

print("\n" + "="*60)
