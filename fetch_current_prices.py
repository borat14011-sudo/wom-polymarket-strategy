#!/usr/bin/env python3
"""Quick fetch of key markets for Kaizen Research Cycle #57"""
import requests
import json
from datetime import datetime

print(f'=== KAIZEN RESEARCH CYCLE #57 ===')
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} PST')
print()

# Fetch Trump deportation markets
try:
    url = 'https://gamma-api.polymarket.com/events?search=trump+deport&active=true&limit=10'
    resp = requests.get(url, timeout=15)
    if resp.status_code == 200:
        events = resp.json()
        print(f'[OK] Deportation events found: {len(events)}')
        for e in events:
            title = e.get('title', 'N/A')
            print(f"\nEvent: {title}")
            markets = e.get('markets', [])
            for m in markets:
                group = m.get('groupItemTitle', 'N/A')
                prices = m.get('outcomePrices', 'N/A')
                volume = m.get('volume', 0)
                print(f"  {group}: {prices} (Vol: ${volume:,.0f})")
    else:
        print(f'[ERROR] API Error: {resp.status_code}')
except Exception as e:
    print(f'[ERROR] {e}')

print("\n" + "="*50)

# Fetch Elon markets
try:
    url = 'https://gamma-api.polymarket.com/events?search=elon+tweet&active=true&limit=10'
    resp = requests.get(url, timeout=15)
    if resp.status_code == 200:
        events = resp.json()
        print(f'[OK] Elon events found: {len(events)}')
        for e in events:
            title = e.get('title', 'N/A')
            print(f"\nEvent: {title}")
            markets = e.get('markets', [])
            for m in markets[:5]:
                group = m.get('groupItemTitle', 'N/A')
                prices = m.get('outcomePrices', 'N/A')
                print(f"  {group}: {prices}")
    else:
        print(f'[ERROR] API Error: {resp.status_code}')
except Exception as e:
    print(f'[ERROR] {e}')

print('\n=== SCAN COMPLETE ===')
