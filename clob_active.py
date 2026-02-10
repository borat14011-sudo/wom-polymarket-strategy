import requests
import json
from datetime import datetime, timezone

# Try CLOB API with active filter
try:
    print('=== Testing CLOB API - Active Markets Only ===')
    r = requests.get('https://clob.polymarket.com/markets?active=true&closed=false&limit=100', timeout=15)
    print(f'Status: {r.status_code}')
    data = r.json()
    
    markets = data.get('data', [])
    print(f'Total markets: {len(markets)}')
    
    now = datetime.now(timezone.utc)
    
    # Filter for markets ending in future
    active_markets = []
    for m in markets:
        end_str = m.get('end_date_iso', '')
        try:
            if end_str:
                end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                if end > now:
                    active_markets.append(m)
        except:
            pass
    
    print(f'Future markets: {len(active_markets)}')
    
    print('\n=== ACTIVE FUTURE MARKETS ===')
    for m in active_markets[:15]:
        question = m.get('question', 'N/A')
        end = m.get('end_date_iso', 'N/A')
        volume = m.get('volume', '0')
        print(f'- {question[:70]}')
        print(f'  Ends: {end} | Volume: ${float(volume):,.0f}')
        
except Exception as e:
    import traceback
    print(f'Error: {e}')
    traceback.print_exc()
