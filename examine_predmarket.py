import requests
import json

print("Examining predmarket repository for API code...")
print("=" * 60)

# Get the main Python file from predmarket
url = "https://api.github.com/repos/predmarket/predmarket/contents"
try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        contents = response.json()
        
        # Look for main Python files
        python_files = []
        for item in contents:
            name = item.get('name', '')
            if name.endswith('.py'):
                python_files.append(item)
        
        print(f"Found {len(python_files)} Python files:")
        for item in python_files[:10]:
            print(f"  • {item.get('name')} ({item.get('size', 0)} bytes)")
            
        # Check for requirements.txt to see dependencies
        for item in contents:
            if item.get('name') == 'requirements.txt':
                req_url = item.get('download_url')
                if req_url:
                    req_resp = requests.get(req_url, timeout=5)
                    if req_resp.status_code == 200:
                        print("\nDependencies (requirements.txt):")
                        print(req_resp.text)
                break
                
        # Look for API-related files
        print("\nLooking for API/client files...")
        for item in contents:
            name = item.get('name', '').lower()
            if 'api' in name or 'client' in name or 'polymarket' in name:
                print(f"  Found: {item.get('name')}")
                
                # Get file content if it's Python
                if name.endswith('.py'):
                    file_url = item.get('download_url')
                    if file_url:
                        file_resp = requests.get(file_url, timeout=5)
                        if file_resp.status_code == 200:
                            content = file_resp.text
                            print(f"    Preview (first 200 chars):")
                            print(f"    {content[:200]}...")
                            
    else:
        print(f"Error: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Checking for EIP-712 Python libraries...")
print("=" * 60)

# Check known Ethereum Python libraries for EIP-712 support
libraries = {
    "web3.py": "https://web3py.readthedocs.io/",
    "eth-account": "https://eth-account.readthedocs.io/",
    "eth-keys": "https://github.com/ethereum/eth-keys",
    "eth-utils": "https://github.com/ethereum/eth-utils"
}

for lib, url in libraries.items():
    print(f"\n{lib}:")
    print(f"  URL: {url}")
    
    # Check if it supports EIP-712
    if lib == "eth-account":
        print("  ✅ Known to support EIP-712 signing")
        print("  Example: account.sign_typed_data()")
    elif lib == "web3.py":
        print("  ✅ Has EIP-712 support via eth-account")
    else:
        print("  ⚠️  May not have direct EIP-712 support")

print("\n" + "=" * 60)
print("IMPLEMENTATION PLAN:")
print("=" * 60)
print("1. Install eth-account: pip install eth-account")
print("2. Use sign_typed_data() for EIP-712 signatures")
print("3. Combine with HMAC for API key authentication")
print("4. Test with simple API calls first")
print("\nExample EIP-712 structure for Polymarket:")
print("""
{
  "types": {
    "EIP712Domain": [...],
    "Order": [
      {"name": "maker", "type": "address"},
      {"name": "isBuy", "type": "bool"},
      {"name": "limitPrice", "type": "uint256"},
      ...
    ]
  },
  "primaryType": "Order",
  "domain": {...},
  "message": {...}
}
""")