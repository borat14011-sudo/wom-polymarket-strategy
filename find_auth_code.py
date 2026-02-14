import requests
import json

print("Finding authentication code in Polymarket repositories...")
print("=" * 60)

# Search for authentication in the Rust client
search_url = "https://api.github.com/search/code"
params = {
    'q': 'eip712+repo:Polymarket/rs-clob-client',
    'per_page': 5
}

try:
    response = requests.get(search_url, params=params, timeout=10)
    if response.status_code == 200:
        results = response.json()
        print(f"Found {results.get('total_count', 0)} files mentioning EIP712")
        
        for item in results.get('items', [])[:3]:
            print(f"\nFile: {item.get('name')}")
            print(f"Path: {item.get('path')}")
            print(f"URL: {item.get('html_url')}")
            
            # Get file content
            file_url = item.get('download_url')
            if file_url:
                file_resp = requests.get(file_url, timeout=5)
                if file_resp.status_code == 200:
                    content = file_resp.text
                    # Find lines with EIP712
                    lines = content.split('\n')
                    eip_lines = []
                    for i, line in enumerate(lines):
                        if 'eip712' in line.lower() or 'eip-712' in line.lower():
                            eip_lines.append((i+1, line.strip()))
                    
                    if eip_lines:
                        print("EIP-712 references:")
                        for line_num, line in eip_lines[:3]:
                            print(f"  Line {line_num}: {line[:80]}")
    else:
        print(f"Search error: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Searching for Python implementations...")
print("=" * 60)

# Search for Python Polymarket clients
params['q'] = 'polymarket+python+client+language:python'
try:
    response = requests.get(search_url, params=params, timeout=10)
    if response.status_code == 200:
        results = response.json()
        print(f"Found {results.get('total_count', 0)} Python Polymarket clients")
        
        for item in results.get('items', [])[:5]:
            print(f"\nRepository: {item.get('repository', {}).get('full_name')}")
            print(f"File: {item.get('name')}")
            print(f"Description: {item.get('repository', {}).get('description', 'No description')}")
            print(f"Stars: {item.get('repository', {}).get('stargazers_count', 0)}")
            print(f"URL: {item.get('html_url')}")
            
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Checking documentation for API authentication...")
print("=" * 60)

# Try to find API documentation
try:
    # Check if there's a /api endpoint on docs
    docs_response = requests.get("https://docs.polymarket.com/api", timeout=10)
    if docs_response.status_code == 200:
        print("Found /api documentation endpoint")
        # Check for authentication info
        content = docs_response.text.lower()
        if 'authentication' in content:
            print("Contains authentication documentation")
    else:
        print(f"/api endpoint: {docs_response.status_code}")
        
    # Try common documentation paths
    paths = ['/rest-api', '/graphql', '/clob-api', '/gamma-api', '/developers']
    for path in paths:
        try:
            resp = requests.get(f"https://docs.polymarket.com{path}", timeout=5)
            if resp.status_code == 200:
                print(f"Found documentation at {path}")
        except:
            pass
            
except Exception as e:
    print(f"Error: {e}")