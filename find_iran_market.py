import requests
import json

print("Searching for Iran strike markets...")
print()

# Try closed=True
response = requests.get('https://gamma-api.polymarket.com/markets', params={'limit': 300, 'closed': True})
markets = response.json()

iran_strike = [m for m in markets if 'iran' in m.get('question', '').lower() and 'strike' in m.get('question', '').lower()]

if iran_strike:
    print(f"Found {len(iran_strike)} closed Iran strike markets:")
    for m in iran_strike[:5]:
        print(f"  - {m.get('question', 'N/A')}")
else:
    print("No closed Iran strike markets found")

print()
print("Trying active markets...")

# Try without closed parameter
response2 = requests.get('https://clob.polymarket.com/markets')
all_markets = response2.json()

iran_all = [m for m in all_markets if m and isinstance(m, dict) and 'iran' in str(m.get('question', '')).lower() and 'strike' in str(m.get('question', '')).lower()]

if iran_all:
    print(f"Found {len(iran_all)} Iran strike markets:")
    for m in iran_all[:5]:
        print(f"  - {m.get('question', 'N/A')}")
        
print()
print("Current Iran market may have been resolved/removed from active listings")
