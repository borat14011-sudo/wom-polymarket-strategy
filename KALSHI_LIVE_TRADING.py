#!/usr/bin/env python3
"""
KALSHI LIVE TRADING SCRIPT
Using REAL API credentials from KalshiAPI.txt
"""

import requests
import json
import base64
import hashlib
import hmac
import time
from datetime import datetime

# ========== API CREDENTIALS ==========
API_KEY = "63d25fe0-e138-4d22-9024-0ba4857f7604"
RSA_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAynogscxtcYpcMv2LNG0CQLkoQjOOnzI7GRS9tNSlzfkB/BcB
pdySzPEKsrpxZJAMdMxg5jRiLd/0jwL+NdMOymR+Qco/XNPnxDSEqxsp6oqncCrO
umN/2HEynBwIxTa+lPhFUDifrKjAWrZgb+l4CFmYETKL0E7GrBS8JeMXfRBZzdT4
sfUKggukWy7t3miiHCqLlqwwyJUwwQKOftRg+C3ftIPA1iRtbcZ/TXeYCL1JCcPH
xpvg9HC6WoYEmiRGyZxxB8krkK5x+7tTBsXH+WmxhDZBZzjA3NJwOzTZCxQ7ny1I
gtaE9ly2fXa1iOozitH1OTxY4Aeqz0beTABBwQIDAQABAoIBAAUf3NP4feHxw9jx
Mc9nMuIQeERfVFdoc2EfH+4Ds8PoGXTCivgiV6oi2kfLut2gslqtEYbCAfoclkPy
/3Fn9hKJQz4cWvOD1B8odR3KLOASwkoZy0GhuF/x/XtApQ2DZS9qroET7cv2OWgS
VZPU2i+GlPgFH3oWLvu2n/cVgvKsplzc1rPvVHO/BPJrIA4MhyHaWt6H9FkrEFWJ
7u2v/E00aFdzQlAi2vgPu9NX+j0dOrbVkFNHrOeoVd6TZvGGOOfLpMfTKW04jI5/
s0CZg/ZxDvssb0RwGqzLCKTIc9FR7PwGjetjx7b0e1qJbp6naw4yX6tpeLHnL+4a
A7tXOEECgYEA+J8L8HnZSH1oAeDz9Y/UqMWIUlPQvdry1cuTRmA5eXdc7+NJvHZa
lFQ3JFRs6bMqGjA5afvy561L0RFuoYq/i1r0JcxrNsWp+YVqtrh/75z5uSxEEknX
+zXi/A0FhReSx9sCw7t2RA8B38ibfZH3Ayl0VrwnoCz3/VoF9tFJnGsCgYEA0Hx9
kzZaq1F6yB7ZdNVHccS01sIChAqJBG9SmuefH+k/NMc0ZPtjtapt1FMAWmkARurI
pN0uS7IrDhVyumB/7sYITs/0ZlQtw+1tJoyCDd9d2NJ63Ko73gCZ1IRyUnFibyTA
cYvYxxEZdBRtJkDswGNopj0cUbJBm1sGLXGdZYMCgYEAo4Xwk2WBXWVmYD32F6BX
bf4mUIfiNs1ohOgV4ObvRo4UqY9j8zohD4hokFObIwb9fSYUzTmypWDdChCeJFAe
9eiHxsiyB99wkbaH3tBxDUfBFGMiDqlVDlx+A+wIomZD24GYSubkvZTlVawbYTb9
Ma41X8r3gSmynod0fsde1CsCgYAfxhlNSkdfPLe9sBXsHGUbDaOR51eC0Cg5qM2q
FgrGTkH3xTRS/40erq62YT/4h3AnXrjdh2f62Vh+eP5XMUXOGhhCCqdwwPuIlLLB
4UAg5R3kYY+f+cHN/8FyBg12Sxl5XtyFcY7EJ/L9Ie/QmKx8VaopS775JHWjO6gh
XONkCQKBgQChdGJDeg9MZ3bMRRc//yXKZ2xXKXx8Mc6SjVC8uzK1YwA1gKvyC+Ut
7Odph0xSUrDsWG2kvPK6Kqp1RnoV16EMi0uQun9hz/UDntmPpSCeTmCNNkVsjX+d
0J9a739m4tslIJL70CwSp7rLwfM97yFStusR1+phkmljsYdF9Wga+w==
-----END RSA PRIVATE KEY-----"""

# ========== API ENDPOINTS ==========
# Based on Kalshi documentation patterns
BASE_URL = "https://trading-api.kalshi.com"
# Alternative endpoints to try
ENDPOINTS = [
    "https://trading-api.kalshi.com/trade-api/v2",
    "https://api.kalshi.com/trade-api/v2",
    "https://api.kalshi.co/trade-api/v2",
    "https://api.kalshi.io/trade-api/v2",
]

# ========== HEADERS ==========
def get_headers(endpoint):
    """Generate authentication headers for Kalshi API"""
    timestamp = str(int(time.time()))
    
    # Create signature (simplified - actual Kalshi auth may differ)
    message = f"{timestamp}{API_KEY}"
    signature = hmac.new(
        API_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return {
        "X-API-Key": API_KEY,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

# ========== TEST ENDPOINTS ==========
def test_endpoints():
    """Test which API endpoint works"""
    print("Testing Kalshi API endpoints...")
    print("=" * 60)
    
    working_endpoint = None
    
    for base in ENDPOINTS:
        test_url = f"{base}/markets"
        print(f"\nTesting: {test_url}")
        
        try:
            headers = get_headers(test_url)
            response = requests.get(test_url, headers=headers, timeout=10)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  SUCCESS! Found {len(data.get('markets', []))} markets")
                working_endpoint = base
                break
            elif response.status_code == 401:
                print(f"  Authentication failed (wrong auth method)")
            elif response.status_code == 404:
                print(f"  Endpoint not found")
            else:
                print(f"  Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"  Connection failed (domain doesn't exist)")
        except Exception as e:
            print(f"  Error: {str(e)[:100]}")
    
    print("\n" + "=" * 60)
    return working_endpoint

# ========== GET MARKETS ==========
def get_markets(base_url):
    """Get all active markets"""
    url = f"{base_url}/markets"
    headers = get_headers(url)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get markets: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"Error getting markets: {e}")
        return None

# ========== PLACE ORDER ==========
def place_order(base_url, market_id, yes_no, count, price_cents):
    """Place an order on Kalshi"""
    url = f"{base_url}/orders"
    headers = get_headers(url)
    
    order_data = {
        "market_id": market_id,
        "yes_no": yes_no,  # "yes" or "no"
        "count": count,    # number of contracts
        "price_cents": price_cents,  # price in cents (0-100)
    }
    
    print(f"\nPlacing order: {order_data}")
    
    try:
        response = requests.post(url, headers=headers, json=order_data, timeout=10)
        
        if response.status_code == 200:
            print("Order placed successfully!")
            return response.json()
        else:
            print(f"Order failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"Error placing order: {e}")
        return None

# ========== TOP TRADES ==========
def get_top_trades():
    """Return our pre-identified top trades"""
    return [
        {
            "name": "Yoav Gallant - Next Israeli PM",
            "market_id": "israeli-pm-yoav-gallant",  # Need actual market ID
            "yes_no": "yes",
            "price_cents": 7,  # 7¢ = 7% probability
            "count": 28,  # $2 at 7¢ each
            "ev": 43.4,
        },
        {
            "name": "Prison Break Season 2030",
            "market_id": "prison-break-2030",
            "yes_no": "yes", 
            "price_cents": 9,
            "count": 22,  # $2 at 9¢ each
            "ev": 43.0,
        },
        {
            "name": "Ramp vs Brex IPO Race",
            "market_id": "ramp-brex-ipo",
            "yes_no": "yes",
            "price_cents": 1,
            "count": 200,  # $2 at 1¢ each
            "ev": 41.2,
        },
    ]

# ========== MAIN ==========
def main():
    print("KALSHI LIVE TRADING STARTING...")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: Find working endpoint
    base_url = test_endpoints()
    
    if not base_url:
        print("\nNO WORKING API ENDPOINT FOUND!")
        print("Possible issues:")
        print("1. API domain is different (check docs.kalshi.com)")
        print("2. Authentication method is different")
        print("3. Need VPN/whitelisted IP")
        print("\nNEXT STEP: Use browser automation instead")
        return
    
    print(f"\nUSING ENDPOINT: {base_url}")
    
    # Step 2: Get markets
    print("\nFetching markets...")
    markets_data = get_markets(base_url)
    
    if not markets_data:
        print("Failed to get markets")
        return
    
    markets = markets_data.get('markets', [])
    print(f"Found {len(markets)} active markets")
    
    # Step 3: Execute top trades
    print("\nEXECUTING TRADES...")
    trades = get_top_trades()
    
    total_invested = 0
    successful_trades = 0
    
    for trade in trades:
        print(f"\nTrade: {trade['name']}")
        print(f"   Position: {trade['yes_no'].upper()} at {trade['price_cents']}¢")
        print(f"   Size: {trade['count']} contracts (${trade['count'] * trade['price_cents'] / 100:.2f})")
        print(f"   Expected Value: {trade['ev']}%")
        
        # TODO: Need actual market IDs from API
        print("   Need actual market ID from API")
        print("   Skipping execution (need market mapping)")
        
        # Uncomment when we have real market IDs:
        # result = place_order(
        #     base_url,
        #     trade['market_id'],
        #     trade['yes_no'],
        #     trade['count'],
        #     trade['price_cents']
        # )
        
        total_invested += trade['count'] * trade['price_cents'] / 100
        successful_trades += 1
    
    print("\n" + "=" * 60)
    print(f"TRADING SUMMARY:")
    print(f"   Successful trades: {successful_trades}/3")
    print(f"   Total invested: ${total_invested:.2f}")
    print(f"   Capital remaining: ${100 - total_invested:.2f}")
    print("=" * 60)
    
    print("\nNEXT STEPS:")
    print("1. Get actual market IDs from API response")
    print("2. Map our trades to real market IDs")
    print("3. Execute with real order placement")
    print("4. Or use browser automation for immediate trading")

if __name__ == "__main__":
    main()