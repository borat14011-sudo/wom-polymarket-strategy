import requests
import json

print("Exploring polymarket-python-infrastructure repository structure...")
print("=" * 60)

# Get repository contents
url = 'https://api.github.com/repos/perpetual-s/polymarket-python-infrastructure/contents'
try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        contents = response.json()
        
        print("Python files found:")
        print("-" * 40)
        
        python_files = []
        for item in contents:
            if item['type'] == 'file' and item['name'].endswith('.py'):
                python_files.append(item)
                print(f"  {item['name']} ({item['size']} bytes)")
        
        print(f"\nTotal Python files: {len(python_files)}")
        
        # Look for authentication/API related files
        print("\nLooking for authentication/API files:")
        print("-" * 40)
        
        auth_keywords = ['auth', 'api', 'client', 'sign', 'eip', 'wallet', 'order', 'trade']
        for item in python_files:
            name_lower = item['name'].lower()
            if any(keyword in name_lower for keyword in auth_keywords):
                print(f"\n🔐 {item['name']}:")
                
                # Get file content
                file_url = item['download_url']
                file_resp = requests.get(file_url, timeout=5)
                if file_resp.status_code == 200:
                    content = file_resp.text
                    
                    # Look for Cloudflare mentions
                    if 'cloudflare' in content.lower() or 'cf' in content.lower():
                        print("   ⚠️  Mentions Cloudflare")
                    
                    # Look for authentication code
                    auth_patterns = ['eip-712', 'eip712', 'sign_message', 'signTypedData', 'personal_sign']
                    for pattern in auth_patterns:
                        if pattern in content:
                            print(f"   ✅ Contains {pattern}")
                    
                    # Look for API endpoints
                    if 'polymarket.com' in content or 'gamma' in content.lower():
                        print("   🌐 Contains API endpoints")
                    
                    # Show first few relevant lines
                    lines = content.split('\n')
                    relevant_lines = []
                    for i, line in enumerate(lines[:20]):
                        if any(keyword in line.lower() for keyword in ['def ', 'class ', 'import ', 'from ', '#']):
                            relevant_lines.append(f"   {i+1:3d}: {line[:80]}")
                    
                    if relevant_lines:
                        print("\n   First relevant lines:")
                        for line in relevant_lines[:5]:
                            print(line)
                            
        # Check for requirements.txt or dependencies
        print("\n" + "=" * 60)
        print("Checking dependencies...")
        
        for item in contents:
            if item['name'] in ['requirements.txt', 'pyproject.toml', 'setup.py']:
                print(f"\n📦 Found {item['name']}:")
                file_url = item['download_url']
                file_resp = requests.get(file_url, timeout=5)
                if file_resp.status_code == 200:
                    print(file_resp.text[:500])
                    
except Exception as e:
    print(f"Error: {e}")