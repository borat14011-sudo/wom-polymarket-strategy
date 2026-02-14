#!/usr/bin/env python3
"""Quick Kaizen scan - Feb 9, 6:30 PM PST"""
import requests
import json
from datetime import datetime

print('=== KAIZEN RESEARCH SCAN #30 ===')
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} PST')
print()

# Fetch active markets
try:
    url = 'https://gamma-api.polymarket.com/events?limit=100&active=true&order=volume&ascending=false'
    resp = requests.get(url, timeout=15)
    if resp.status_code == 200:
        markets = resp.json()
        print(f'[OK] Markets fetched: {len(markets)}')
        
        # Search for key markets
        elon_count = 0
        trump_count = 0
        btc_count = 0
        high_volume = []
        
        for m in markets:
            title = m.get('title', '').lower()
            vol = m.get('volume', 0)
            if 'elon' in title or 'doge' in title or 'musk' in title:
                elon_count += 1
                print(f'  ELON: {m.get("title", "")[:60]}... (${vol:,.0f})')
            if 'trump' in title or 'deport' in title:
                trump_count += 1
                print(f'  TRUMP: {m.get("title", "")[:60]}... (${vol:,.0f})')
            if 'bitcoin' in title or 'btc' in title or 'mstr' in title or 'microstrategy' in title:
                btc_count += 1
            if vol > 500000:
                high_volume.append((m.get('title', '')[:40], vol))
        
        print(f'\n[SUMMARY] Elon/Musk markets: {elon_count}')
        print(f'[SUMMARY] Trump markets: {trump_count}')
        print(f'[SUMMARY] BTC/MSTR markets: {btc_count}')
        print(f'[SUMMARY] High volume (>$500K): {len(high_volume)}')
        for t, v in high_volume[:5]:
            print(f'   - {t}... (${v:,.0f})')
    else:
        print(f'[ERROR] API Error: {resp.status_code}')
except Exception as e:
    print(f'[ERROR] {e}')

print('\n=== SCAN COMPLETE ===')
