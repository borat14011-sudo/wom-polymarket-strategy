"""
Peek at events_raw.json structure without loading entire 2.5 GB
"""
import json

filepath = 'historical-data-scraper/data/events_raw.json'

print("[PEEK] events_raw.json (2.5 GB)")
print("Reading first few lines...")

with open(filepath, 'r') as f:
    # Read first character to check format
    first_char = f.read(1)
    f.seek(0)
    
    if first_char == '[':
        # It's a JSON array
        print("Format: JSON array")
        
        # Try to read first complete object
        bracket_count = 0
        buffer = ""
        
        for char in f.read(50000):  # Read first 50KB
            buffer += char
            if char == '{':
                bracket_count += 1
            elif char == '}':
                bracket_count -= 1
                
                if bracket_count == 0 and len(buffer) > 10:
                    # We have a complete object
                    try:
                        obj = json.loads(buffer.strip().strip(','))
                        print(f"\nFirst object keys: {list(obj.keys())}")
                        print(f"Sample question: {obj.get('question', 'N/A')[:80]}")
                        print(f"Sample outcome: {obj.get('outcome', 'N/A')}")
                        print(f"Has outcome field: {'outcome' in obj}")
                        break
                    except:
                        pass
    
    elif first_char == '{':
        print("Format: JSON object (dict)")
        
        # Read first 10KB to get a sense
        f.seek(0)
        sample = f.read(10000)
        print(f"First 500 chars: {sample[:500]}")
    
    else:
        print(f"Unknown format, first char: {first_char}")
