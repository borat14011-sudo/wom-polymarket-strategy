import requests
import json

# The event slug from the URL: polymarket.com/event/us-strikes-iran-by
event_slug = "us-strikes-iran-by"

# Try gamma API with event endpoint
print("Fetching Iran strike event directly...")
print("=" * 60)

try:
    # Try events endpoint
    url = f"https://gamma-api.polymarket.com/events/{event_slug}"
    response = requests.get(url, timeout=10)
    
    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    
    if response.ok:
        event_data = response.json()
        print(f"\nEvent found!")
        print(f"Title: {event_data.get('title', 'Unknown')}")
        print(f"Description: {event_data.get('description', 'N/A')[:100]}")
        
        # Get markets within this event
        markets = event_data.get('markets', [])
        print(f"\nMarkets in this event: {len(markets)}")
        
        for market in markets:
            question = market.get('question', 'Unknown')
            outcomes = market.get('outcomePrices', [])
            
            if len(outcomes) >= 2:
                yes_price = float(outcomes[0])
                no_price = float(outcomes[1])
                
                print(f"\n  Market: {question}")
                print(f"    YES: {yes_price*100:.1f}%")
                print(f"    NO: {no_price*100:.1f}%")
                
                # Check if this is the Feb 13 market
                if 'february 13' in question.lower() or 'feb 13' in question.lower():
                    print(f"    *** THIS IS OUR POSITION ***")
                    print(f"    Entry: 12.0%")
                    print(f"    Current: {yes_price*100:.1f}%")
                    print(f"    P&L: ${((yes_price - 0.12) / 0.12 * 4.20):+.2f} ({((yes_price - 0.12) / 0.12 * 100):+.1f}%)")
        
        # Save full response for inspection
        with open('iran_event_data.json', 'w') as f:
            json.dump(event_data, f, indent=2)
        print(f"\nFull data saved to iran_event_data.json")
        
    else:
        print(f"ERROR: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
