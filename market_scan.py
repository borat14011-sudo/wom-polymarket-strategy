import requests
import json

# Get active markets
try:
    r = requests.get('https://gamma-api.polymarket.com/markets?limit=100&active=true', timeout=15)
    data = r.json()
    print(f'Total markets returned: {len(data)}')
    
    # Print first market structure
    if data:
        print('\n=== SAMPLE MARKET STRUCTURE ===')
        print(json.dumps(data[0], indent=2)[:1500])
    
    # Sort by volume
    markets = sorted(data, key=lambda x: float(x.get('volume', 0) or 0), reverse=True)[:20]
    
    print('\n=== TOP 20 MARKETS BY VOLUME ===')
    for i, m in enumerate(markets):
        question = m.get('question', 'N/A')[:60]
        vol = float(m.get('volume', 0) or 0) / 1e6
        print(f"{i+1:2}. {question}... | ${vol:.1f}M")
    
    # Search for deportation markets
    print('\n=== DEPORTATION MARKETS ===')
    deport = [m for m in data if 'deport' in m.get('question', '').lower()]
    print(f"Found {len(deport)} deportation markets")
    for m in deport[:10]:
        print(f"- {m.get('question', 'N/A')}")
        print(f"  Volume: ${float(m.get('volume', 0))/1e6:.2f}M")
    
    # Search for Elon/DOGE markets  
    print('\n=== ELON/DOGE/MUSK MARKETS ===')
    elon = [m for m in data if any(kw in m.get('question', '').lower() for kw in ['elon', 'doge', 'musk'])]
    print(f"Found {len(elon)} Elon/DOGE/Musk markets")
    for m in elon[:10]:
        print(f"- {m.get('question', 'N/A')}")
        print(f"  Volume: ${float(m.get('volume', 0))/1e6:.2f}M")
        
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
