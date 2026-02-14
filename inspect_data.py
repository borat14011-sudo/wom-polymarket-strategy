#!/usr/bin/env python3
"""
Inspect the data structure to understand field names
"""

import json
from collections import Counter

def load_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    print("Loading dataset...")
    data = load_data('polymarket-monitor/historical-data-scraper/data/backtest_dataset_v1.json')
    
    # Handle different data structures
    if isinstance(data, dict):
        trades = data.get('trades') or data.get('markets') or []
        print(f"Data is a dict with keys: {list(data.keys())}")
    elif isinstance(data, list):
        trades = data
        print("Data is a list")
    
    print(f"Total records: {len(trades)}\n")
    
    if len(trades) > 0:
        print("First record structure:")
        print(json.dumps(trades[0], indent=2))
        print("\n" + "="*80 + "\n")
        
        # Analyze all field names
        all_fields = Counter()
        for trade in trades:
            all_fields.update(trade.keys())
        
        print("All field names (frequency):")
        for field, count in all_fields.most_common():
            print(f"  {field}: {count}")
        
        # Check outcome field variations
        print("\n" + "="*80 + "\n")
        print("Sample outcome values (first 50 unique):")
        outcome_fields = ['outcome', 'resolved', 'result', 'resolution', 'winner']
        for field in outcome_fields:
            values = set()
            for trade in trades[:1000]:  # Sample first 1000
                val = trade.get(field)
                if val is not None:
                    values.add(str(val))
            if values:
                print(f"\n{field}: {list(values)[:50]}")

if __name__ == '__main__':
    main()
