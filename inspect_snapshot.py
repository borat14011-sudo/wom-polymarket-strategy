import json

with open('markets_snapshot_20260207_221914.json', 'r', encoding='utf-8') as f:
    lines = []
    for i in range(10):
        line = f.readline()
        if not line:
            break
        lines.append(line)
        print(f"Line {i}: {len(line)} chars")
        print(line[:200])
        try:
            obj = json.loads(line.strip())
            print(f"  Parsed OK, type: {type(obj)}")
            if isinstance(obj, dict):
                print(f"  Keys: {list(obj.keys())}")
        except json.JSONDecodeError as e:
            print(f"  JSON error: {e}")

# Check if file starts with [
with open('markets_snapshot_20260207_221914.json', 'r', encoding='utf-8') as f:
    first_char = f.read(1)
    print(f"\nFirst character: '{first_char}'")
    if first_char == '[':
        print("File appears to be a JSON array")
    else:
        print("File is not a JSON array (likely JSONL)")

# Count total lines
print("\nCounting total lines...")
count = 0
with open('markets_snapshot_20260207_221914.json', 'r', encoding='utf-8') as f:
    for line in f:
        count += 1
print(f"Total lines: {count}")