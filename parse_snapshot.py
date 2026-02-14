import ijson
import json

filepath = 'markets_snapshot_20260207_221914.json'

print("Parsing with ijson...")
with open(filepath, 'r', encoding='utf-8') as f:
    # Get top-level keys
    parser = ijson.parse(f)
    for prefix, event, value in parser:
        if prefix == '' and event == 'map_key':
            print(f"Top-level key: {value}")
        # Stop after a few
        if prefix.count('.') > 1:
            break

# Try to load first part of file to see structure
print("\nLoading first 5000 bytes...")
with open(filepath, 'r', encoding='utf-8') as f:
    chunk = f.read(5000)
    # Find where "markets" might start
    if '"markets"' in chunk:
        markets_pos = chunk.find('"markets"')
        print(f'"markets" found at position {markets_pos}')
        print(chunk[markets_pos:markets_pos+200])
    # Print chunk
    print(chunk)

# Try to parse as JSON but limit depth
print("\nTrying to parse entire file (this may take memory)...")
try:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"Successfully loaded JSON")
        print(f"Top-level keys: {list(data.keys())}")
        if 'markets' in data:
            print(f"'markets' is a {type(data['markets'])} with length {len(data['markets'])}")
            # Sample first market
            if len(data['markets']) > 0:
                first = data['markets'][0]
                print(f"First market keys: {list(first.keys())}")
                print(f"Sample: {first.get('question', 'No question')[:100]}")
        if 'metadata' in data:
            print(f"Metadata: {data['metadata']}")
except MemoryError:
    print("Memory error - file too large")
except Exception as e:
    print(f"Error: {e}")