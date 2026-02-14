import requests
url = 'https://gamma-api.polymarket.com/markets'
params = {'limit': 10, 'active': True}
response = requests.get(url, params=params, timeout=10)
markets = response.json()

print('Sample market fields:')
if markets:
    m = markets[0]
    print(f"  closed: {m.get('closed')} (type: {type(m.get('closed'))})")
    print(f"  active: {m.get('active')} (type: {type(m.get('active'))})")
    print(f"  archived: {m.get('archived')} (type: {type(m.get('archived'))})")
    print(f"  question: {m.get('question', 'N/A')[:50]}...")
