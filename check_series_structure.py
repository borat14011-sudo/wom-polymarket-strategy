import json

print("Checking kalshi_series.json structure...")
with open('kalshi_series.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

print(f"Data type: {type(data)}")
print(f"Keys: {list(data.keys())}")

if 'series' in data:
    print(f"\nNumber of series: {len(data['series'])}")
    
    # Search for series related to our markets
    search_terms = ['ACTORSONNYCROCKETT', 'NEXTISRAELPM', 'PERFORMBONDSONG', 'NEXTIRANLEADER', 'XISUCCESSOR']
    
    found_series = []
    for series in data['series']:
        if 'ticker' in series:
            ticker = series['ticker']
            for term in search_terms:
                if term in ticker:
                    found_series.append(series)
                    break
    
    print(f"\nFound {len(found_series)} relevant series:")
    for series in found_series:
        print(f"\nTicker: {series.get('ticker')}")
        print(f"Title: {series.get('title', 'N/A')}")
        print(f"Status: {series.get('status', 'N/A')}")
        
        # Check if there are outcomes
        if 'outcomes' in series:
            outcomes = series['outcomes']
            print(f"Number of outcomes: {len(outcomes)}")
            print("Sample outcomes:")
            for outcome in outcomes[:5]:
                print(f"  - {outcome.get('ticker', 'N/A')}: {outcome.get('title', 'N/A')}")
        print("-" * 50)