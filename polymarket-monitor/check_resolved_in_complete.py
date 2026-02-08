"""
Check polymarket_complete.json for resolved markets
This is the 488 MB file - should have resolved outcomes
"""
import json
import os

print("[CHECK] polymarket_complete.json")
filepath = 'historical-data-scraper/data/polymarket_complete.json'

if not os.path.exists(filepath):
    print(f"File not found: {filepath}")
    exit()

size_mb = os.path.getsize(filepath) / 1024 / 1024
print(f"Size: {size_mb:.0f} MB")

print("\n[LOAD] Loading (this may take 30-60 seconds)...")

with open(filepath, 'r') as f:
    data = json.load(f)

print(f"Type: {type(data)}")

if isinstance(data, dict):
    print(f"Keys: {list(data.keys())[:10]}")
    
    # Check if it's a dict of markets
    if len(data) > 0:
        first_key = list(data.keys())[0]
        first_value = data[first_key]
        
        print(f"\nFirst key: {first_key}")
        print(f"First value type: {type(first_value)}")
        
        if isinstance(first_value, dict):
            print(f"First value keys: {list(first_value.keys())}")
            print(f"Sample question: {first_value.get('question', 'N/A')[:80]}")
            print(f"Sample outcome: {first_value.get('outcome', 'N/A')}")
            print(f"Sample closed: {first_value.get('closed', 'N/A')}")

elif isinstance(data, list):
    print(f"List length: {len(data)}")
    
    if data:
        print(f"\nSample entry keys: {list(data[0].keys())}")
        print(f"Sample question: {data[0].get('question', 'N/A')[:80]}")
        print(f"Sample outcome: {data[0].get('outcome', 'N/A')}")
        print(f"Sample closed: {data[0].get('closed', 'N/A')}")
        
        # Count resolved
        resolved = [m for m in data if m.get('closed') == True or m.get('outcome') is not None]
        print(f"\nResolved markets: {len(resolved)}/{len(data)} ({len(resolved)/len(data)*100:.1f}%)")
        
        if resolved:
            print(f"\nSample resolved market:")
            sample = resolved[0]
            print(f"  Question: {sample.get('question', 'N/A')[:80]}")
            print(f"  Outcome: {sample.get('outcome')}")
            print(f"  Closed: {sample.get('closed')}")
