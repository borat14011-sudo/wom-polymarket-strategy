import requests
import json
import base64

print("Getting authentication example from rs-clob-client...")
print("=" * 60)

# Get the authenticated client example
url = "https://api.github.com/repos/Polymarket/rs-clob-client/contents/examples/clob/authenticated_client.rs"
try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        file_data = response.json()
        content = base64.b64decode(file_data.get('content', '')).decode('utf-8', errors='ignore')
        
        print("Authenticated Client Example:")
        print("-" * 40)
        print(content[:1000])  # First 1000 chars
        
        # Analyze the authentication
        print("\n" + "=" * 60)
        print("Authentication Analysis:")
        print("=" * 60)
        
        lines = content.split('\n')
        auth_lines = []
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['private_key', 'signer', 'wallet', 'eip', '712', 'auth', 'authenticate']):
                auth_lines.append((i+1, line.strip()))
        
        if auth_lines:
            print("Found authentication-related lines:")
            for line_num, line in auth_lines[:10]:
                print(f"  Line {line_num}: {line}")
        else:
            print("No clear authentication lines found")
            
        # Look for API key usage
        print("\nAPI Key Usage:")
        api_key_lines = [line for line in lines if 'api_key' in line.lower() or 'api-key' in line.lower()]
        for line in api_key_lines[:5]:
            print(f"  {line.strip()}")
            
    else:
        print(f"File not found: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Checking for Python implementation...")
print("=" * 60)

# Search for Python implementation in the repo
search_url = "https://api.github.com/repos/Polymarket/rs-clob-client/git/trees/main?recursive=1"
try:
    response = requests.get(search_url, timeout=10)
    if response.status_code == 200:
        tree_data = response.json()
        
        # Look for Python files or bindings
        python_files = []
        for item in tree_data.get('tree', []):
            if item.get('path', '').endswith('.py'):
                python_files.append(item)
            elif 'python' in item.get('path', '').lower():
                python_files.append(item)
        
        if python_files:
            print(f"Found {len(python_files)} Python-related files:")
            for item in python_files[:5]:
                print(f"  • {item.get('path')}")
        else:
            print("No Python files found in Rust client")
            
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Searching for official Python SDK...")
print("=" * 60)

# Check poly-sdk repository
sdk_url = "https://api.github.com/repos/Polymarket/poly-sdk"
try:
    response = requests.get(sdk_url, timeout=10)
    if response.status_code == 200:
        sdk = response.json()
        print(f"SDK Repository: {sdk.get('name')}")
        print(f"Description: {sdk.get('description')}")
        print(f"Language: {sdk.get('language')}")
        
        # Get SDK contents
        contents_url = f"{sdk_url}/contents"
        contents_resp = requests.get(contents_url, timeout=5)
        if contents_resp.status_code == 200:
            contents = contents_resp.json()
            print("\nSDK Contents:")
            for item in contents[:10]:
                print(f"  • {item.get('name')} ({item.get('type')})")
                
except Exception as e:
    print(f"Error: {e}")