import json
import sys

def main():
    with open('../markets_snapshot_20260207_221914.json', 'r', encoding='utf-8') as f:
        # Try to load entire file (might be memory heavy)
        # Instead, read first 10k characters and see structure
        chunk = f.read(10000)
        # Find first complete JSON object
        # Assume it's a list
        if chunk.startswith('['):
            # Parse as array up to where?
            # Let's just load whole file with incremental parser
            pass
        print(chunk[:500])
        # Try to parse as JSON lines?
        # Let's check if it's a JSON array
        lines = chunk.split('\n')
        print(f"First line length: {len(lines[0])}")
        print(f"First line: {lines[0][:200]}")

if __name__ == '__main__':
    main()