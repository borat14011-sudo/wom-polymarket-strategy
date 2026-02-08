import requests
import json

# Check for Iran strike market
r = requests.get('https://gamma-api.polymarket.com/events', params={'limit': 100, 'closed': 'false'})
markets = r.json()

print("=== SEARCHING FOR IRAN STRIKE MARKET ===")
found = False
for market in markets:
    title = market.get('title', '').lower()
    if 'iran' in title and ('strike' in title or 'strikes' in title):
        found = True
        print(f"\nMarket: {market['title']}")
        print(f"Slug: {market.get('slug', 'N/A')}")
        
        # Get outcomes
        for m in market.get('markets', []):
            question = m.get('question', '')
            prices = m.get('outcomePrices', [])
            print(f"  Question: {question}")
            print(f"  Prices: {prices}")
        
        print(f"Volume: ${market.get('volume', 0):,.2f}")
        print(f"End date: {market.get('endDate', 'N/A')}")
        break

if not found:
    print("Iran strike market not found in active markets")
    print("\n=== Checking closed markets ===")
    
    r2 = requests.get('https://gamma-api.polymarket.com/events', params={'limit': 100, 'closed': 'true'})
    closed = r2.json()
    
    for market in closed:
        title = market.get('title', '').lower()
        if 'iran' in title and ('strike' in title or 'strikes' in title):
            print(f"\nFOUND IN CLOSED: {market['title']}")
            print(f"End date: {market.get('endDate', 'N/A')}")
            
            # Check outcomes
            for m in market.get('markets', []):
                question = m.get('question', '')
                outcome = m.get('outcome', 'N/A')
                print(f"  {question}: RESOLVED {outcome}")
            break
