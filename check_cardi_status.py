import requests

# Check the specific Cardi B market
market_id = "555793"
url = f"https://gamma-api.polymarket.com/markets/{market_id}"

print("Fetching Cardi B market details...")
response = requests.get(url, timeout=10)

if response.status_code == 200:
    m = response.json()
    print(f"Question: {m.get('question')}")
    print(f"End Date: {m.get('endDate')}")
    print(f"Closed: {m.get('closed')}")
    print(f"Archived: {m.get('archived')}")
    print(f"Resolved: {m.get('resolved')}")
    print(f"Outcome: {m.get('outcome')}")
    print(f"Outcome Prices: {m.get('outcomePrices')}")
    
    # Check resolution status
    if m.get('resolved') or m.get('outcome'):
        print("\n✅ MARKET IS RESOLVED")
    elif m.get('closed'):
        print("\n⏸️ MARKET IS CLOSED (awaiting resolution)")
    else:
        print("\n🟢 MARKET IS STILL OPEN")
else:
    print(f"Error: {response.status_code}")
