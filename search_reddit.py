import requests
import json

print("Searching for Polymarket API discussions on Reddit...")
print("=" * 60)

# Try to find Reddit discussions about Polymarket API issues
# Using Pushshift API (unofficial Reddit search)
search_url = "https://api.pushshift.io/reddit/search/submission"
params = {
    'q': 'polymarket api',
    'size': 10,
    'sort': 'desc',
    'sort_type': 'created_utc'
}

try:
    response = requests.get(search_url, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        posts = data.get('data', [])
        
        print(f"Found {len(posts)} Reddit posts about Polymarket API")
        print()
        
        for i, post in enumerate(posts[:5], 1):
            title = post.get('title', 'No title')
            subreddit = post.get('subreddit', 'unknown')
            created = post.get('created_utc', 0)
            url = f"https://reddit.com{post.get('permalink', '')}"
            
            print(f"{i}. {title}")
            print(f"   Subreddit: r/{subreddit}")
            print(f"   URL: {url}")
            
            # Check for Cloudflare mentions in selftext
            selftext = post.get('selftext', '').lower()
            if 'cloudflare' in selftext or 'cf' in selftext:
                print("   ⚠️  Mentions Cloudflare")
            if '403' in selftext or 'forbidden' in selftext:
                print("   ⚠️  Mentions 403/forbidden")
            if 'workaround' in selftext or 'bypass' in selftext:
                print("   🚀 Mentions workaround")
            print()
            
    else:
        print(f"Pushshift API error: {response.status_code}")
        
except Exception as e:
    print(f"Error accessing Pushshift: {e}")

print("\n" + "=" * 60)
print("Checking for specific Cloudflare discussions...")

# Search for Cloudflare specific
params['q'] = 'polymarket cloudflare'
try:
    response = requests.get(search_url, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        posts = data.get('data', [])
        
        if posts:
            print(f"\nFound {len(posts)} posts about Polymarket + Cloudflare:")
            for post in posts[:3]:
                print(f"\n• {post.get('title', 'No title')}")
                print(f"  r/{post.get('subreddit', 'unknown')}")
                print(f"  URL: https://reddit.com{post.get('permalink', '')}")
                
                # Show snippet of discussion
                selftext = post.get('selftext', '')
                if selftext:
                    # Find Cloudflare mention
                    import re
                    cloudflare_match = re.search(r'.{0,100}cloudflare.{0,100}', selftext, re.IGNORECASE)
                    if cloudflare_match:
                        print(f"  Snippet: {cloudflare_match.group()}...")
        else:
            print("No specific Cloudflare discussions found.")
            
except Exception as e:
    print(f"Error: {e}")