#!/usr/bin/env python3
"""
Find a working Python example of Polymarket API
"""

import requests
import json

print("Searching for working Polymarket Python API example...")
print("=" * 60)

# Known working repositories
known_repos = [
    "perpetual-s/polymarket-python-infrastructure",
    "therealaleph/polymarket-arbitrage-bot", 
    "predmarket/predmarket",
    "0xessential/polymarket-bot"
]

for repo in known_repos:
    print(f"\nChecking: {repo}")
    url = f"https://api.github.com/repos/{repo}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            repo_data = response.json()
            print(f"  Description: {repo_data.get('description', 'No description')}")
            print(f"  Stars: {repo_data.get('stargazers_count', 0)}")
            print(f"  Language: {repo_data.get('language', 'Unknown')}")
            print(f"  Updated: {repo_data.get('updated_at', 'Unknown')[:10]}")
            
            # Check for Python files
            contents_url = f"{url}/contents"
            contents_resp = requests.get(contents_url, timeout=5)
            if contents_resp.status_code == 200:
                contents = contents_resp.json()
                python_files = [item for item in contents if item.get('name', '').endswith('.py')]
                if python_files:
                    print(f"  Python files: {len(python_files)}")
                    
                    # Look for API/client files
                    for item in python_files[:3]:
                        name = item.get('name', '')
                        if 'api' in name.lower() or 'client' in name.lower():
                            print(f"    • {name} (likely API client)")
                            
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "=" * 60)
print("Checking predmarket repository (most promising)...")
print("=" * 60)

# Check predmarket which might have working API
predmarket_url = "https://api.github.com/repos/predmarket/predmarket/contents"
try:
    response = requests.get(predmarket_url, timeout=10)
    if response.status_code == 200:
        contents = response.json()
        
        print("Files in predmarket:")
        for item in contents[:15]:
            name = item.get('name', '')
            file_type = item.get('type', '')
            print(f"  {name} ({file_type})")
            
        # Look for API directory
        api_dir = None
        for item in contents:
            if item.get('type') == 'dir' and 'api' in item.get('name', '').lower():
                api_dir = item
                break
                
        if api_dir:
            print(f"\nFound API directory: {api_dir.get('name')}")
            # Get API directory contents
            api_url = api_dir.get('url')
            api_resp = requests.get(api_url, timeout=5)
            if api_resp.status_code == 200:
                api_contents = api_resp.json()
                print("API directory contents:")
                for item in api_contents[:10]:
                    print(f"  • {item.get('name')}")
                    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Quick test: Check if we can find EIP-712 Python implementation")
print("=" * 60)

# Search for EIP-712 Python implementation
search_terms = [
    "eip712 python",
    "eip-712 signature python",
    "typed data signing python",
    "eth_signTypedData python"
]

for term in search_terms:
    print(f"\nSearching: {term}")
    # This would normally use web search, but we'll check known libraries
    known_libs = ["eth-account", "web3.py", "eth-keys", "eth-utils"]
    for lib in known_libs:
        print(f"  Check {lib} for EIP-712 support")

print("\n" + "=" * 60)
print("RECOMMENDATION:")
print("=" * 60)
print("1. Check predmarket repository for working API code")
print("2. Look at eth-account or web3.py for EIP-712 implementation")
print("3. Test with simple curl commands first")
print("4. Compare our HMAC implementation with official Rust client")