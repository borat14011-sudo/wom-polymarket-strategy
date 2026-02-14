import json

# Check Polymarket structure
with open('polymarket_latest.json', encoding='utf-8') as f:
    pm = json.load(f)
print('=== POLYMARKET STRUCTURE ===')
print(f'Type: {type(pm)}')
if isinstance(pm, list):
    print(f'Length: {len(pm)}')
    if pm:
        print(f'First item keys: {list(pm[0].keys())[:15]}')
        title = pm[0].get('question', pm[0].get('title', 'N/A'))
        print(f'Sample title: {title[:60]}')
        print(f'Sample price: {pm[0].get("outcomePrices", "N/A")}')
else:
    print(f'Keys: {list(pm.keys())[:10]}')
    if 'data' in pm:
        print(f'data length: {len(pm["data"])}')

print()

# Check Kalshi structure
with open('kalshi_latest.json', encoding='utf-8') as f:
    k = json.load(f)
print('=== KALSHI STRUCTURE ===')
print(f'Type: {type(k)}')
if isinstance(k, dict):
    print(f'Keys: {list(k.keys())[:10]}')
    events = k.get('events', [])
    print(f'Events count: {len(events)}')
    if events:
        print(f'First event keys: {list(events[0].keys())[:15]}')
        print(f'Sample title: {events[0].get("title", "N/A")[:60]}')
        markets = events[0].get('markets', [])
        print(f'Markets in first event: {len(markets)}')
        if markets:
            print(f'Market keys: {list(markets[0].keys())[:10]}')
else:
    print(f'Length: {len(k)}')
