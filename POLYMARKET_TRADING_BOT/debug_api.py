"""
Polymarket API Authentication Debugger
Tests multiple authentication approaches to diagnose issues
"""

import requests
import hmac
import hashlib
import base64
import time
import json

# Credentials
API_KEY = "019c3ee6-4d56-73fc-a7a2-e5db22b94340"
API_SECRET = "IZe8jb-on6PKYZYlG74Al-sTYeuEVPbFqH78e0f0xso="
PASSPHRASE = "b4736af6a2ef790b2034e258da2e296de866c60b4afe9ab707d3697b5c28b51f"

# Base URLs to test
BASE_URLS = [
    "https://clob.polymarket.com",
    "https://gamma-api.polymarket.com",
    "https://api.polymarket.com"
]

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_result(test_name, success, details=""):
    status = "[OK]" if success else "[FAIL]"
    print(f"  {status} - {test_name}")
    if details:
        print(f"         {details}")

# Test 1: Public endpoints (no auth required)
def test_public_endpoints():
    print_section("TEST 1: Public Endpoints (No Auth)")
    
    results = []
    for base in BASE_URLS:
        try:
            url = f"{base}/markets"
            response = requests.get(url, timeout=10)
            success = response.status_code == 200
            results.append((base, success, response.status_code))
            print_result(f"GET {url}", success, f"Status: {response.status_code}")
            if success:
                data = response.json()
                print(f"         Markets count: {len(data) if isinstance(data, list) else 'N/A'}")
        except Exception as e:
            results.append((base, False, str(e)))
            print_result(f"GET {base}/markets", False, f"Error: {e}")
    
    return results

# Test 2: API Key validation endpoint
def test_api_key_validation():
    print_section("TEST 2: API Key Validation")
    
    for base in BASE_URLS:
        try:
            url = f"{base}/auth/api-key"
            response = requests.get(url, timeout=5)
            print_result(f"GET {url}", response.status_code == 200, f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"         Response: {response.text[:100]}")
        except Exception as e:
            print_result(f"GET {url}", False, f"Error: {e}")

# Test 3: Authentication Method 1 - Standard HMAC-SHA256
def test_auth_method_1_standard_hmac():
    print_section("TEST 3: Auth Method 1 - Standard HMAC-SHA256")
    
    timestamp = str(int(time.time()))
    message = timestamp + "GET" + "/balance-allowance"
    
    # Method 1A: Direct HMAC with base64 secret
    try:
        signature = hmac.new(
            API_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'POLYMARKET-API-KEY': API_KEY,
            'POLYMARKET-SIGNATURE': signature,
            'POLYMARKET-TIMESTAMP': timestamp,
            'POLYMARKET-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        url = "https://clob.polymarket.com/balance-allowance"
        response = requests.get(url, headers=headers, timeout=10)
        
        success = response.status_code == 200
        print_result("Method 1A: Direct HMAC + hex digest", success, 
                    f"Status: {response.status_code}")
        if not success:
            print(f"         Response: {response.text[:150]}")
    except Exception as e:
        print_result("Method 1A: Direct HMAC + hex digest", False, f"Error: {e}")
    
    # Method 1B: HMAC with base64 decoded secret
    try:
        secret_bytes = base64.b64decode(API_SECRET)
        signature = hmac.new(
            secret_bytes,
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'POLYMARKET-API-KEY': API_KEY,
            'POLYMARKET-SIGNATURE': signature,
            'POLYMARKET-TIMESTAMP': timestamp,
            'POLYMARKET-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        url = "https://clob.polymarket.com/balance-allowance"
        response = requests.get(url, headers=headers, timeout=10)
        
        success = response.status_code == 200
        print_result("Method 1B: Base64 decoded secret + hex digest", success,
                    f"Status: {response.status_code}")
        if not success:
            print(f"         Response: {response.text[:150]}")
    except Exception as e:
        print_result("Method 1B: Base64 decoded secret + hex digest", False, f"Error: {e}")

# Test 4: Authentication Method 2 - Base64 encoded signature
def test_auth_method_2_base64_sig():
    print_section("TEST 4: Auth Method 2 - Base64 Encoded Signatures")
    
    timestamp = str(int(time.time()))
    message = timestamp + "GET" + "/balance-allowance"
    
    # Method 2A: HMAC with base64 encoded signature
    try:
        signature = hmac.new(
            API_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        headers = {
            'POLYMARKET-API-KEY': API_KEY,
            'POLYMARKET-SIGNATURE': signature_b64,
            'POLYMARKET-TIMESTAMP': timestamp,
            'POLYMARKET-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        url = "https://clob.polymarket.com/balance-allowance"
        response = requests.get(url, headers=headers, timeout=10)
        
        success = response.status_code == 200
        print_result("Method 2A: HMAC + base64 encoded signature", success,
                    f"Status: {response.status_code}")
        if not success:
            print(f"         Response: {response.text[:150]}")
    except Exception as e:
        print_result("Method 2A: HMAC + base64 encoded signature", False, f"Error: {e}")
    
    # Method 2B: Decoded secret + base64 signature
    try:
        secret_bytes = base64.b64decode(API_SECRET)
        signature = hmac.new(
            secret_bytes,
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        headers = {
            'POLYMARKET-API-KEY': API_KEY,
            'POLYMARKET-SIGNATURE': signature_b64,
            'POLYMARKET-TIMESTAMP': timestamp,
            'POLYMARKET-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        url = "https://clob.polymarket.com/balance-allowance"
        response = requests.get(url, headers=headers, timeout=10)
        
        success = response.status_code == 200
        print_result("Method 2B: Decoded secret + base64 signature", success,
                    f"Status: {response.status_code}")
        if not success:
            print(f"         Response: {response.text[:150]}")
    except Exception as e:
        print_result("Method 2B: Decoded secret + base64 signature", False, f"Error: {e}")

# Test 5: Header variations
def test_header_variations():
    print_section("TEST 5: Header Name Variations")
    
    timestamp = str(int(time.time()))
    message = timestamp + "GET" + "/balance-allowance"
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    header_sets = [
        # Set 1: POLYMARKET-* (uppercase with dashes)
        {
            'POLYMARKET-API-KEY': API_KEY,
            'POLYMARKET-SIGNATURE': signature,
            'POLYMARKET-TIMESTAMP': timestamp,
            'POLYMARKET-PASSPHRASE': PASSPHRASE,
        },
        # Set 2: Polymarket-* (title case)
        {
            'Polymarket-Api-Key': API_KEY,
            'Polymarket-Signature': signature,
            'Polymarket-Timestamp': timestamp,
            'Polymarket-Passphrase': PASSPHRASE,
        },
        # Set 3: polymarket-* (lowercase)
        {
            'polymarket-api-key': API_KEY,
            'polymarket-signature': signature,
            'polymarket-timestamp': timestamp,
            'polymarket-passphrase': PASSPHRASE,
        },
        # Set 4: X-Polymarket-* 
        {
            'X-Polymarket-Api-Key': API_KEY,
            'X-Polymarket-Signature': signature,
            'X-Polymarket-Timestamp': timestamp,
            'X-Polymarket-Passphrase': PASSPHRASE,
        },
    ]
    
    url = "https://clob.polymarket.com/balance-allowance"
    
    for i, headers in enumerate(header_sets, 1):
        try:
            headers['Content-Type'] = 'application/json'
            response = requests.get(url, headers=headers, timeout=10)
            
            header_preview = list(headers.keys())[0]
            success = response.status_code == 200
            print_result(f"Header Set {i}: {header_preview}", success,
                        f"Status: {response.status_code}")
            if success:
                print(f"         Headers: {list(headers.keys())}")
        except Exception as e:
            print_result(f"Header Set {i}", False, f"Error: {e}")

# Test 6: Message format variations
def test_message_formats():
    print_section("TEST 6: Message Format Variations")
    
    timestamp = str(int(time.time()))
    
    # Different message formats to try
    message_formats = [
        ("timestamp+GET+path", timestamp + "GET" + "/balance-allowance"),
        ("timestamp+method+path", f"{timestamp}GET/balance-allowance"),
        ("timestamp|GET|path", f"{timestamp}|GET|/balance-allowance"),
        ("json format", json.dumps({"timestamp": timestamp, "method": "GET", "path": "/balance-allowance"})),
        ("just timestamp", timestamp),
    ]
    
    url = "https://clob.polymarket.com/balance-allowance"
    
    for format_name, message in message_formats:
        try:
            signature = hmac.new(
                API_SECRET.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                'POLYMARKET-API-KEY': API_KEY,
                'POLYMARKET-SIGNATURE': signature,
                'POLYMARKET-TIMESTAMP': timestamp,
                'POLYMARKET-PASSPHRASE': PASSPHRASE,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            success = response.status_code == 200
            print_result(f"Format: {format_name}", success,
                        f"Status: {response.status_code}")
            if not success:
                print(f"         Message: {message[:50]}...")
        except Exception as e:
            print_result(f"Format: {format_name}", False, f"Error: {e}")

# Test 7: Timestamp format variations
def test_timestamp_formats():
    print_section("TEST 7: Timestamp Format Variations")
    
    timestamp_formats = [
        ("Unix seconds (int)", str(int(time.time()))),
        ("Unix millis", str(int(time.time() * 1000))),
        ("Unix seconds float", str(time.time())),
        ("ISO 8601", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
    ]
    
    url = "https://clob.polymarket.com/balance-allowance"
    
    for format_name, timestamp in timestamp_formats:
        try:
            message = timestamp + "GET" + "/balance-allowance"
            signature = hmac.new(
                API_SECRET.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                'POLYMARKET-API-KEY': API_KEY,
                'POLYMARKET-SIGNATURE': signature,
                'POLYMARKET-TIMESTAMP': timestamp,
                'POLYMARKET-PASSPHRASE': PASSPHRASE,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            success = response.status_code == 200
            print_result(f"Timestamp: {format_name}", success,
                        f"Status: {response.status_code}")
        except Exception as e:
            print_result(f"Timestamp: {format_name}", False, f"Error: {e}")

# Test 8: Try alternative endpoints
def test_alternative_endpoints():
    print_section("TEST 8: Alternative Endpoints")
    
    timestamp = str(int(time.time()))
    message = timestamp + "GET" + "/user/balance"
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'POLYMARKET-API-KEY': API_KEY,
        'POLYMARKET-SIGNATURE': signature,
        'POLYMARKET-TIMESTAMP': timestamp,
        'POLYMARKET-PASSPHRASE': PASSPHRASE,
        'Content-Type': 'application/json'
    }
    
    endpoints = [
        "/user/balance",
        "/account/balance",
        "/balances",
        "/portfolio/balance",
        "/api/v1/balance",
    ]
    
    for endpoint in endpoints:
        try:
            url = f"https://clob.polymarket.com{endpoint}"
            response = requests.get(url, headers=headers, timeout=10)
            
            print_result(f"GET {endpoint}", response.status_code == 200,
                        f"Status: {response.status_code}")
        except Exception as e:
            print_result(f"GET {endpoint}", False, f"Error: {e}")

# Test 9: CLOB specific endpoints
def test_clob_endpoints():
    print_section("TEST 9: CLOB Specific Endpoints")
    
    # Try getting API info
    try:
        url = "https://clob.polymarket.com/"
        response = requests.get(url, timeout=5)
        print_result("GET / (root)", response.status_code == 200,
                    f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"         Response: {response.text[:200]}")
    except Exception as e:
        print_result("GET / (root)", False, f"Error: {e}")
    
    # Try getting orderbook
    try:
        url = "https://clob.polymarket.com/orderbook/0x1234567890abcdef1234567890abcdef12345678"
        response = requests.get(url, timeout=5)
        print_result("GET /orderbook/{token}", response.status_code in [200, 404],
                    f"Status: {response.status_code}")
    except Exception as e:
        print_result("GET /orderbook/{token}", False, f"Error: {e}")

# Test 10: Print debug info
def print_debug_info():
    print_section("DEBUG INFO")
    print(f"  API Key: {API_KEY[:20]}...{API_KEY[-8:]}")
    print(f"  API Secret length: {len(API_SECRET)}")
    print(f"  API Secret format: {'base64' if is_base64(API_SECRET) else 'plain'}")
    print(f"  Passphrase length: {len(PASSPHRASE)}")
    print(f"  Current timestamp: {int(time.time())}")

def is_base64(s):
    try:
        decoded = base64.b64decode(s)
        return len(decoded) > 0
    except:
        return False

# Run all tests
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  POLYMARKET API AUTHENTICATION DEBUGGER")
    print("=" * 60)
    
    print_debug_info()
    test_public_endpoints()
    test_api_key_validation()
    test_auth_method_1_standard_hmac()
    test_auth_method_2_base64_sig()
    test_header_variations()
    test_message_formats()
    test_timestamp_formats()
    test_alternative_endpoints()
    test_clob_endpoints()
    
    print_section("TESTS COMPLETE")
    print("\n  Check the results above to identify working combinations.")
    print("  Look for ✅ PASS markers to find successful auth methods.\n")
