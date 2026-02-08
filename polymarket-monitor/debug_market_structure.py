"""
Debug: Check actual structure of markets in polymarket_complete.json
"""
import json

print("[DEBUG] Market structure in polymarket_complete.json")

with open('historical-data-scraper/data/polymarket_complete.json', 'r') as f:
    events = json.load(f)

print(f"Total events: {len(events)}")

# Find a closed event
closed_events = [e for e in events if e.get('closed') == True]
print(f"Closed events: {len(closed_events)}")

if closed_events:
    sample_event = closed_events[0]
    
    print(f"\n[CLOSED EVENT SAMPLE]")
    print(f"Title: {sample_event.get('title', 'N/A')[:80]}")
    print(f"Closed: {sample_event.get('closed')}")
    print(f"Event keys: {list(sample_event.keys())}")
    
    markets = sample_event.get('markets', [])
    print(f"\nMarkets in this event: {len(markets)}")
    
    if markets:
        sample_market = markets[0]
        print(f"\n[MARKET SAMPLE]")
        print(f"Market keys: {list(sample_market.keys())}")
        
        for key in sample_market.keys():
            value = sample_market[key]
            if isinstance(value, (str, int, float, bool)) or value is None:
                print(f"  {key}: {value}")
            elif isinstance(value, list):
                print(f"  {key}: [list of {len(value)} items]")
            elif isinstance(value, dict):
                print(f"  {key}: {{dict with {len(value)} keys}}")
        
        # Check all possible outcome fields
        print(f"\n[OUTCOME FIELDS]")
        print(f"  outcome: {sample_market.get('outcome')}")
        print(f"  resolved: {sample_market.get('resolved')}")
        print(f"  resolution: {sample_market.get('resolution')}")
        print(f"  settled: {sample_market.get('settled')}")
        print(f"  closed: {sample_market.get('closed')}")
        print(f"  active: {sample_market.get('active')}")
        
# Check if we need to look at a different structure
print(f"\n[CHECKING DIFFERENT EVENTS]")
for i in range(min(5, len(closed_events))):
    event = closed_events[i]
    markets = event.get('markets', [])
    
    if markets:
        m = markets[0]
        outcome_found = False
        
        # Check various outcome fields
        for field in ['outcome', 'resolved', 'resolution', 'settled', 'winning_outcome']:
            if m.get(field) is not None:
                print(f"\nEvent {i}: Found outcome in '{field}' field")
                print(f"  Value: {m.get(field)}")
                print(f"  Question: {m.get('question', m.get('title', 'N/A'))[:70]}")
                outcome_found = True
                break
        
        if not outcome_found:
            print(f"\nEvent {i}: No outcome field found")
            print(f"  Market keys: {list(m.keys())}")
