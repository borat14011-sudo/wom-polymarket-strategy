#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('polymarket_backtest.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    '✓': '[OK]',
    '✗': '[FAIL]',
    '⚠': '[WARNING]',
    '✅': '[OK]',
    '❌': '[FAIL]'
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('polymarket_backtest.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all Unicode characters")
