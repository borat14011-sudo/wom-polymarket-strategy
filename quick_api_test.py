import requests
import json

# Try the newer CLOB API
r = requests.get('https://gamma-api.polymarket.com/markets?limit=100&active=true&sort=volume&order=desc', timeout=15)
print('Status:', r.status_code)
data = r.json()
print('Markets count:', len(data))

# Print questions to see if they're current
print('\n=== CURRENT ACTIVE MARKETS ===')
for m in data[:15]:
    print(f'- {m.get("question", "N/A")[:70]}')
    print(f'  End: {m.get("endDate", "N/A")}')
