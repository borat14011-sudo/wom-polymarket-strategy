import requests
import json

# Try CLOB API with proper pagination
try:
    print('=== Testing CLOB API ===')
    r = requests.get('https://clob.polymarket.com/markets?active=true&limit=100', timeout=15)
    print(f'Status: {r.status_code}')
    data = r.json()
    print(f'Keys: {list(data.keys())}')
    
    markets = data.get('data', [])
    print(f'Markets count: {len(markets)}')
    
    print('\n=== CURRENT MARKETS ===')
    for m in markets[:20]:
        question = m.get('question', 'N/A')
        end = m.get('end_date_iso', 'N/A')
        print(f'- {question[:70]}')
        print(f'  Ends: {end}')
        
except Exception as e:
    import traceback
    print(f'Error: {e}')
    traceback.print_exc()
