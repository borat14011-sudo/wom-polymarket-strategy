import requests
import json

print("Searching GitHub for Polymarket API repositories...")
print("=" * 60)

# Search GitHub for Polymarket API repositories
url = 'https://api.github.com/search/repositories'
params = {
    'q': 'polymarket api',
    'sort': 'updated',
    'order': 'desc',
    'per_page': 10
}

try:
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_count']} repositories")
        print()
        
        for i, item in enumerate(data['items'][:8], 1):
            print(f"{i}. {item['name']}")
            print(f"   Description: {item.get('description', 'No description')}")
            print(f"   Stars: {item['stargazers_count']}")
            print(f"   Updated: {item['updated_at'][:10]}")
            print(f"   URL: {item['html_url']}")
            
            # Check for Cloudflare mentions in README
            readme_url = f"https://api.github.com/repos/{item['full_name']}/readme"
            try:
                readme_resp = requests.get(readme_url, timeout=5)
                if readme_resp.status_code == 200:
                    readme_content = readme_resp.json().get('content', '')
                    import base64
                    decoded = base64.b64decode(readme_content).decode('utf-8', errors='ignore').lower()
                    if 'cloudflare' in decoded or 'cf' in decoded or 'workaround' in decoded:
                        print(f"   ⚠️  Mentions Cloudflare/workaround")
            except:
                pass
            print()
    else:
        print(f'GitHub API error: {response.status_code}')
except Exception as e:
    print(f'Error: {e}')

print("\n" + "=" * 60)
print("Searching for specific Cloudflare bypass discussions...")

# Search for Cloudflare specific issues
search_terms = [
    "polymarket cloudflare bypass",
    "polymarket api 403",
    "polymarket rate limiting",
    "polymarket authentication",
    "polymarket eip-712"
]

for term in search_terms:
    print(f"\nSearching: {term}")
    params['q'] = term
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['items']:
                for item in data['items'][:2]:
                    print(f"  • {item['name']} - {item['html_url']}")
    except:
        pass