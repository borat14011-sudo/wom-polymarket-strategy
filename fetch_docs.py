import requests
import re

print("Fetching Polymarket API documentation...")
print("=" * 60)

url = "https://docs.polymarket.com"
try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        content = response.text
        
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if title_match:
            print(f"Title: {title_match.group(1)}")
        
        # Look for API sections
        print("\nSearching for API documentation...")
        
        # Check for common documentation frameworks
        if "swagger" in content.lower():
            print("Found Swagger/OpenAPI documentation")
        if "redoc" in content.lower():
            print("Found ReDoc documentation")
        if "postman" in content.lower():
            print("Found Postman documentation")
        
        # Search for authentication info
        auth_keywords = ["authentication", "auth", "api key", "eip-712", "eip712", "signature", "hmac"]
        print("\nAuthentication mentions:")
        for keyword in auth_keywords:
            if keyword in content.lower():
                count = content.lower().count(keyword)
                print(f"  {keyword}: {count} mentions")
        
        # Search for API endpoints
        print("\nAPI endpoint patterns found:")
        endpoint_patterns = [
            r"/api/",
            r"/v[0-9]/",
            r"clob",
            r"gamma",
            r"order",
            r"trade",
            r"market"
        ]
        
        for pattern in endpoint_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"  {pattern}: {len(matches)} mentions")
        
        # Extract JavaScript/JSON data that might contain API info
        print("\nLooking for API configuration in scripts...")
        script_tags = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
        for i, script in enumerate(script_tags[:3]):
            if "api" in script.lower() or "endpoint" in script.lower():
                print(f"  Script {i+1} contains API references")
                # Extract URLs
                urls = re.findall(r'https?://[^\s\"\']+', script)
                for url in urls[:3]:
                    if "polymarket" in url:
                        print(f"    {url}")
        
        # Check for Next.js data
        if "__NEXT_DATA__" in content:
            print("\nFound Next.js application data")
            # Try to extract the JSON data
            next_data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', content, re.DOTALL)
            if next_data_match:
                try:
                    import json
                    next_data = json.loads(next_data_match.group(1))
                    print("  Successfully parsed Next.js data")
                    # Look for API info in props
                    if "props" in next_data:
                        print("  Contains props data")
                except:
                    print("  Could not parse Next.js data")
                    
    else:
        print(f"Error: Status code {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Checking for GitHub repositories with working API examples...")
print("=" * 60)

# Search GitHub for working Polymarket API implementations
search_terms = [
    "polymarket-clob-client",
    "polymarket-api-python",
    "polymarket-sdk",
    "polymarket-eip712"
]

import json
import base64

for term in search_terms:
    print(f"\nSearching GitHub for: {term}")
    api_url = f"https://api.github.com/search/repositories?q={term}&sort=updated&order=desc"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data["items"]:
                for item in data["items"][:2]:
                    print(f"  • {item['name']}")
                    print(f"    Description: {item.get('description', 'No description')}")
                    print(f"    Stars: {item['stargazers_count']}")
                    print(f"    URL: {item['html_url']}")
                    
                    # Check if it's a client/SDK
                    if "client" in item['name'].lower() or "sdk" in item['name'].lower():
                        print(f"    ⭐ Likely API client/SDK")
            else:
                print(f"  No repositories found")
    except Exception as e:
        print(f"  Error: {e}")