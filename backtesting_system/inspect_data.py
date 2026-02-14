#!/usr/bin/env python3
"""
Inspect the available data files to understand structure and quality.
"""
import json
import pandas as pd
import sys
from pathlib import Path
import gzip

def inspect_active_markets():
    print("=== Active Markets ===")
    with open('active-markets.json', 'r') as f:
        data = json.load(f)
    print(f"Timestamp: {data['timestamp']}")
    print(f"Number of markets: {len(data['markets'])}")
    # Show first market keys
    if data['markets']:
        first = data['markets'][0]
        print(f"Keys in market: {list(first.keys())[:20]}...")
        print(f"Sample market ID: {first.get('id')}")
        print(f"Question: {first.get('question')[:100]}...")

def inspect_resolved_markets():
    print("\n=== Resolved Markets ===")
    # Load first few records
    with open('polymarket_resolved_markets.json', 'r') as f:
        # This file is large, read first 10 records
        data = json.load(f)
    print(f"Total resolved markets: {len(data)}")
    print(f"First record keys: {list(data[0].keys())}")
    df = pd.DataFrame(data[:10])
    print("\nFirst 10 records:")
    print(df[['market_id', 'question', 'winner', 'final_prices']])

def inspect_backtest_results():
    print("\n=== Backtest Results ===")
    df = pd.read_csv('backtest_results.csv')
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Strategies: {df['strategy'].unique()}")
    print(f"Date range: {df['entry_date'].min()} to {df['exit_date'].max()}")
    print("\nSummary statistics:")
    print(df['pnl'].describe())

def inspect_snapshot():
    print("\n=== Market Snapshot (Partial) ===")
    # The snapshot is 89.5 MB, too large to load entirely quickly
    # We'll read first few lines to understand structure
    import ijson  # incremental JSON parser
    try:
        import ijson
        with open('markets_snapshot_20260207_221914.json', 'r') as f:
            # Parse first object
            parser = ijson.items(f, 'item')
            count = 0
            for obj in parser:
                print(f"First object keys: {list(obj.keys())}")
                # Show sample
                print(f"Sample market: {obj.get('id')} - {obj.get('question', '')[:50]}...")
                count += 1
                if count >= 3:
                    break
    except ImportError:
        print("ijson not installed, skipping detailed inspection")
        # Fallback: read first 1000 chars
        with open('markets_snapshot_20260207_221914.json', 'r') as f:
            first_chunk = f.read(2000)
            print(f"First 2000 chars: {first_chunk[:500]}...")

if __name__ == '__main__':
    inspect_active_markets()
    inspect_resolved_markets()
    inspect_backtest_results()
    inspect_snapshot()