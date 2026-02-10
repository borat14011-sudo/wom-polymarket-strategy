import requests
import json

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

def get_markets():
    url = f"{GAMMA_API}/markets"
    params = {"limit": 500, "active": True, "closed": False}
    
    try:
        response = requests.get(url, params=params, timeout=60)
        return response.json()
    except:
        return []

def search_markets(keyword):
    """Search markets by keyword"""
    markets = get_markets()
    results = []
    
    for m in markets:
        q = m.get('question', '').lower()
        desc = m.get('description', '').lower()
        
        if keyword.lower() in q or keyword.lower() in desc:
            results.append({
                'question': m.get('question'),
                'volume': m.get('volume'),
                'slug': m.get('marketSlug', 'N/A'),
                'id': m.get('id')
            })
    
    return results

if __name__ == "__main__":
    keywords = ['chiefs', 'eagles', 'mahomes', 'hurts', 'nfl', 'football', 'bowl']
    
    for kw in keywords:
        print(f"\n{'='*60}")
        print(f"Searching for: '{kw}'")
        print('='*60)
        
        results = search_markets(kw)
        print(f"Found {len(results)} markets:")
        
        for r in results[:10]:
            print(f"  • {r['question'][:70]}...")
            print(f"    Slug: {r['slug']}")
            print()
