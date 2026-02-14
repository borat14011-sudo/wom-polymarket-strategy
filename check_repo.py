import requests
import json
import base64

print("Checking polymarket-python-infrastructure repository...")
print("=" * 60)

# Get the polymarket-python-infrastructure repo
url = 'https://api.github.com/repos/perpetual-s/polymarket-python-infrastructure'
try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        repo = response.json()
        print(f"Repository: {repo.get('name', 'N/A')}")
        print(f"Description: {repo.get('description', 'No description')}")
        print(f"Stars: {repo.get('stargazers_count', 0)}")
        print(f"Updated: {repo.get('updated_at', 'N/A')[:10]}")
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
            
            # Check for key terms
            decoded_lower = decoded.lower()
            
            if 'cloudflare' in decoded_lower:
                print("✅ Mentions Cloudflare")
                # Extract context
                lines = decoded.split('\n')
                for i, line in enumerate(lines):
                    if 'cloudflare' in line.lower():
                        print(f"   Line {i+1}: {line.strip()}")
            
            if 'eip-712' in decoded_lower or 'eip712' in decoded_lower:
                print("✅ Mentions EIP-712 authentication")
                
            if 'auth' in decoded_lower or 'authentication' in decoded_lower:
                print("✅ Mentions authentication")
                
            if '403' in decoded or 'forbidden' in decoded_lower:
                print("⚠️  Mentions 403/forbidden errors")
                
            if 'workaround' in decoded_lower or 'bypass' in decoded_lower:
                print("🚀 Mentions workaround/bypass")
                
            # Check file structure
            contents_url = f"{url}/contents"
            contents_resp = requests.get(contents_url, timeout=5)
            if contents_resp.status_code == 200:
                contents = contents_resp.json()
                print("\nKey files in repository:")
                for item in contents:
                    if item['type'] == 'file' and item['name'].endswith('.py'):
                        print(f"  • {item['name']}")
                        
        # Check issues for Cloudflare discussions
        issues_url = f"{url}/issues"
        issues_params = {'state': 'all', 'per_page': 5}
        issues_resp = requests.get(issues_url, params=issues_params, timeout=5)
        if issues_resp.status_code == 200:
            issues = issues_resp.json()
            cloudflare_issues = []
            for issue in issues:
                if 'cloudflare' in issue.get('title', '').lower() or 'cloudflare' in issue.get('body', '').lower():
                    cloudflare_issues.append(issue)
            
            if cloudflare_issues:
                print(f"\n⚠️  Found {len(cloudflare_issues)} issues mentioning Cloudflare:")
                for issue in cloudflare_issues[:3]:
                    print(f"  • #{issue['number']}: {issue['title']}")
                    print(f"    URL: {issue['html_url']}")
                    
    else:
        print(f"Error: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")