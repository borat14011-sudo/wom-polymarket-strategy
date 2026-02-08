import requests

response = requests.get(
    'https://gamma-api.polymarket.com/markets',
    params={'limit': 20, 'active': True, 'closed': False},
    timeout=10
)

print(f"Status: {response.status_code}")
markets = response.json()
print(f"Found {len(markets)} markets with closed=False\n")

for i, m in enumerate(markets, 1):
    question = m.get('question', 'Unknown')
    print(f"{i}. {question}")
    if 'iran' in question.lower():
        print(f"   ^^ IRAN MARKET FOUND! ^^")
