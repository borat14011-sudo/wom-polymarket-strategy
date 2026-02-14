import requests
import json
import base64

print("Examining official Polymarket rs-clob-client...")
print("=" * 60)

# Get the Rust client repository
url = "https://api.github.com/repos/Polymarket/rs-clob-client"
try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        repo = response.json()
        print(f"Repository: {repo.get('name', 'N/A')}")
        print(f"Description: {repo.get('description', 'No description')}")
        print(f"Stars: {repo.get('stargazers_count', 0)}")
        print(f"Language: {repo.get('language', 'N/A')}")
        print(f"URL: {repo.get('html_url', 'N/A')}")
        
        # Get README
        readme_url = f"{url}/readme"
        readme_resp = requests.get(readme_url, timeout=5)
        if readme_resp.status_code == 200:
            readme_data = readme_resp.json()
            content = readme_data.get('content', '')
            decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
            
            print("\nREADME Analysis:")
            print("-" * 40)
            
            # Look for key information
            decoded_lower = decoded.lower()
            
            if 'eip-712' in decoded_lower or 'eip712' in decoded_lower:
                print("[OK] Mentions EIP-712 authentication")
                
            if 'authentication' in decoded_lower:
                print("[OK] Mentions authentication")
                
            if 'api key' in decoded_lower:
                print("[OK] Mentions API keys")
                
            if 'signature' in decoded_lower:
                print("[OK] Mentions signatures")
                
            # Show installation/usage section
            lines = decoded.split('\n')
            print("\nKey sections found:")
            for i, line in enumerate(lines):
                if any(section in line.lower() for section in ['# usage', '# example', '# installation', '# auth']):
                    print(f"  Line {i+1}: {line.strip()}")
                    
        # Get repository contents to find authentication code
        print("\n" + "=" * 60)
        print("Looking for authentication implementation...")
        
        contents_url = f"{url}/contents"
        contents_resp = requests.get(contents_url, timeout=5)
        if contents_resp.status_code == 200:
            contents = contents_resp.json()
            
            # Look for authentication-related files
            auth_files = []
            for item in contents:
                name_lower = item.get('name', '').lower()
                if any(term in name_lower for term in ['auth', 'sign', 'eip', 'wallet', 'key']):
                    auth_files.append(item)
            
            if auth_files:
                print(f"Found {len(auth_files)} authentication-related files:")
                for item in auth_files:
                    print(f"  • {item.get('name')} ({item.get('type')})")
                    
                    # Get file content if it's a Rust file
                    if item.get('name', '').endswith('.rs'):
                        file_url = item.get('download_url')
                        if file_url:
                            file_resp = requests.get(file_url, timeout=5)
                            if file_resp.status_code == 200:
                                content = file_resp.text
                                # Look for EIP-712
                                if 'eip712' in content.lower() or 'eip-712' in content.lower():
                                    print(f"    -> Contains EIP-712 implementation")
                                # Look for signing functions
                                if 'sign' in content.lower():
                                    print(f"    -> Contains signing functions")
            else:
                print("No authentication files found in root")
                
        # Check for examples directory
        print("\n" + "=" * 60)
        print("Looking for examples...")
        
        examples_url = f"{url}/contents/examples"
        examples_resp = requests.get(examples_url, timeout=5)
        if examples_resp.status_code == 200:
            examples = examples_resp.json()
            print(f"Found {len(examples)} example files:")
            for example in examples[:5]:
                print(f"  • {example.get('name')}")
        else:
            print("No examples directory found")
            
    else:
        print(f"Error: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Checking for Python SDK...")
print("=" * 60)

# Check for poly-sdk
sdk_url = "https://api.github.com/repos/Polymarket/poly-sdk"
try:
    response = requests.get(sdk_url, timeout=10)
    if response.status_code == 200:
        sdk = response.json()
        print(f"SDK: {sdk.get('name', 'N/A')}")
        print(f"Description: {sdk.get('description', 'No description')}")
        print(f"Language: {sdk.get('language', 'N/A')}")
        print(f"URL: {sdk.get('html_url', 'N/A')}")
        
        # Check if it's Python
        if sdk.get('language', '').lower() == 'python':
            print("[OK] Python SDK found!")
        else:
            print(f"Note: SDK is in {sdk.get('language', 'unknown')}")
            
except Exception as e:
    print(f"Error checking SDK: {e}")