import re

with open('find_actual_opportunities.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all edge_percent calculations
pattern = r"'edge_percent': \(edge / (yes_price|no_price)\) \* 100"
replacement = r"'edge_percent': (edge / \1) * 100 if \1 > 0 else 0"

content = re.sub(pattern, replacement, content)

with open('find_actual_opportunities.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed edge_percent calculations")