import requests

# Check current Iran market price
response = requests.get('https://gamma-api.polymarket.com/events', params={
    'limit': 100,
    'offset': 0,
    'closed': 'false'
})

markets = response.json()

# Find Iran market
for market in markets:
    title = market.get('title', '').lower()
    if 'iran' in title and 'strike' in title:
        print(f"Market: {market['title']}")
        print(f"Slug: {market.get('slug', 'N/A')}")
        
        # Get market outcomes
        for m in market.get('markets', []):
            question = m.get('question', '')
            prices = m.get('outcomePrices', [])
            print(f"  {question}: {prices}")
        
        print(f"Volume: ${market.get('volume', 0):,.2f}")
        print(f"End date: {market.get('endDate', 'N/A')}")
        print()
