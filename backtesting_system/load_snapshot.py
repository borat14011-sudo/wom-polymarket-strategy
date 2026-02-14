import json
import pandas as pd
import sys
from pathlib import Path

def load_partial_snapshot(limit=1000):
    """Load first N records from the large snapshot file."""
    filepath = Path('../markets_snapshot_20260207_221914.json')
    print(f"Loading {limit} records from {filepath}...")
    
    # Since file is a JSON array, we can parse incrementally
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        # Read the opening bracket
        char = f.read(1)
        if char != '[':
            print("Expected '[' at start of file")
            return None
        
        count = 0
        while count < limit:
            line = ''
            while True:
                c = f.read(1)
                if not c:
                    break
                line += c
                if c == '}':
                    # Check if next char is ',' or ']'
                    next_c = f.read(1)
                    if next_c == ',' or next_c == ']':
                        # End of object
                        line += next_c
                        break
                    else:
                        # Continue reading
                        line += next_c
                        continue
            if not line:
                break
            # Try to parse the object (including trailing comma or bracket)
            if line.endswith(','):
                line = line[:-1]
            elif line.endswith(']'):
                line = line[:-1]
            try:
                obj = json.loads(line)
                data.append(obj)
                count += 1
            except json.JSONDecodeError as e:
                print(f"Failed to parse line: {line[:100]}...")
                print(f"Error: {e}")
                break
    print(f"Loaded {len(data)} records")
    return pd.DataFrame(data)

if __name__ == '__main__':
    df = load_partial_snapshot(100)
    if df is not None:
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df[['id', 'question', 'volume', 'liquidity']].head())
        
        # Check for price history fields
        print("\nChecking for price history fields...")
        sample = df.iloc[0]
        for key in sample.keys():
            if 'price' in key.lower():
                print(f"  {key}: {type(sample[key])}")