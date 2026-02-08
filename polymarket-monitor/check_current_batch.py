import requests
r = requests.get('https://gamma-api.polymarket.com/markets', 
                params={'limit': 5, 'closed': True, 'offset': 0})
markets = r.json()
print("Sample of markets at offset 0 (most recent closed):")
for m in markets:
    print(f"  {m.get('startDate', 'N/A')[:10]} - {m.get('question', 'N/A')[:60]}")
