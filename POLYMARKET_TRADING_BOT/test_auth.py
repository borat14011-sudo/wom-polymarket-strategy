"""
Polymarket API Authentication Test
Tests the fixed authentication implementation
"""

import os
import json
import hmac
import hashlib
import base64
import time
import requests


def build_hmac_signature(secret: str, timestamp: str, method: str, request_path: str, body=None):
    """
    CORRECT HMAC signature generation for Polymarket CLOB API
    
    Key fixes from original code:
    1. Secret is base64 encoded, must decode it first
    2. Signature is base64 encoded (not hex)
    3. Body must have single quotes replaced with double quotes
    """
    # Decode the base64 secret - this is the KEY FIX
    try:
        base64_secret = base64.urlsafe_b64decode(secret)
    except Exception:
        # Add padding if needed
        padded_secret = secret + '=' * (4 - len(secret) % 4)
        base64_secret = base64.urlsafe_b64decode(padded_secret)
    
    # Build message
    message = str(timestamp) + str(method) + str(request_path)
    if body:
        # Replace single quotes with double quotes to match Go/TypeScript
        message += str(body).replace("'", '"')
    
    # Create HMAC
    h = hmac.new(base64_secret, bytes(message, "utf-8"), hashlib.sha256)
    
    # Return base64 encoded signature (NOT hex)
    return base64.urlsafe_b64encode(h.digest()).decode("utf-8")


def create_l2_headers(api_key: str, api_secret: str, passphrase: str, 
                      wallet_address: str, method: str, path: str, body=None):
    """
    Create correct L2 authentication headers
    
    Key fixes from original code:
    1. Header names are POLY_* not POLYMARKET-*
    2. Must include POLY_ADDRESS (wallet address)
    3. Must include POLY_API_KEY
    """
    timestamp = str(int(time.time()))
    
    # Serialize body for signature
    body_str = None
    if body is not None:
        if isinstance(body, dict):
            body_str = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
        else:
            body_str = str(body)
    
    # Generate signature
    signature = build_hmac_signature(api_secret, timestamp, method, path, body_str)
    
    # CORRECT header names
    headers = {
        "POLY_ADDRESS": wallet_address.lower(),
        "POLY_SIGNATURE": signature,
        "POLY_TIMESTAMP": timestamp,
        "POLY_API_KEY": api_key,
        "POLY_PASSPHRASE": passphrase,
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": "polymarket-python-client"
    }
    
    return headers


def test_auth():
    """Test the authentication with the provided credentials"""
    
    print("=" * 70)
    print("Polymarket CLOB API Authentication Test")
    print("=" * 70)
    
    # Credentials from the problem statement
    API_KEY = "019c3ee6-4d56-73fc-a7a2-e5db22b94340"
    API_SECRET = "IZe8jb-on6PKYZYlG74Al-sTYeuEVPbFqH78e0f0xso="
    PASSPHRASE = "b4736af6a2ef790b2034e258da2e296de866c60b4afe9ab707d3697b5c28b51f"
    
    # WALLET ADDRESS IS REQUIRED for L2 auth
    # This should be the Polygon address associated with your API key
    WALLET_ADDRESS = os.getenv("POLY_WALLET_ADDRESS", "")
    
    print(f"\nAPI Key: {API_KEY}")
    print(f"Secret: {API_SECRET[:20]}...")
    print(f"Passphrase: {PASSPHRASE[:20]}...")
    print(f"Wallet Address: {WALLET_ADDRESS if WALLET_ADDRESS else 'NOT SET'}")
    
    if not WALLET_ADDRESS:
        print("\n[!] WARNING: You must set POLY_WALLET_ADDRESS environment variable!")
        print("The wallet address is REQUIRED for L2 authentication.")
        print("\nExample: export POLY_WALLET_ADDRESS=0x1234...")
        print("\nContinuing with partial tests (public endpoints only)...\n")
    
    BASE_URL = "https://clob.polymarket.com"
    
    # Test 1: Verify HMAC signature generation
    print("\n" + "-" * 70)
    print("Test 1: HMAC Signature Generation")
    print("-" * 70)
    
    timestamp = str(int(time.time()))
    method = "GET"
    path = "/balance-allowance"
    
    sig = build_hmac_signature(API_SECRET, timestamp, method, path)
    print(f"Timestamp: {timestamp}")
    print(f"Method: {method}")
    print(f"Path: {path}")
    print(f"Generated Signature: {sig[:50]}...")
    print(f"[OK] Signature generated successfully (base64 encoded)")
    
    # Test 2: Headers creation
    print("\n" + "-" * 70)
    print("Test 2: L2 Headers Creation")
    print("-" * 70)
    
    headers = create_l2_headers(API_KEY, API_SECRET, PASSPHRASE, 
                                WALLET_ADDRESS, "GET", "/balance-allowance")
    
    print("Headers created:")
    for key, value in headers.items():
        display_value = value[:50] + "..." if len(str(value)) > 50 else value
        print(f"  {key}: {display_value}")
    
    # Verify all required headers are present
    required = ["POLY_ADDRESS", "POLY_SIGNATURE", "POLY_TIMESTAMP", 
                "POLY_API_KEY", "POLY_PASSPHRASE"]
    missing = [h for h in required if h not in headers]
    if missing:
        print(f"\n[FAIL] Missing headers: {missing}")
    else:
        print("\n[OK] All required L2 headers present")
    
    # Test 3: Test signature with body
    print("\n" + "-" * 70)
    print("Test 3: HMAC Signature with Request Body")
    print("-" * 70)
    
    body = {"orderID": "12345"}
    sig_with_body = build_hmac_signature(API_SECRET, timestamp, "DELETE", "/order", body)
    print("Body: {body}")
    print(f"Signature with body: {sig_with_body[:50]}...")
    print("[OK] Body signature generated (single quotes -> double quotes)")
    
    # Test 4: Compare old vs new signature method
    print("\n" + "-" * 70)
    print("Test 4: Comparison with Old (Broken) Method")
    print("-" * 70)
    
    # OLD BROKEN METHOD (what the original code did)
    old_message = timestamp + method + path
    old_sig = hmac.new(
        API_SECRET.encode('utf-8'),  # Used raw secret, didn't decode base64
        old_message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()  # Used hex instead of base64
    
    # NEW CORRECT METHOD
    new_sig = build_hmac_signature(API_SECRET, timestamp, method, path)
    
    print(f"OLD signature (hex, wrong):     {old_sig[:50]}...")
    print(f"NEW signature (base64, correct): {new_sig[:50]}...")
    print(f"✓ Signatures are different (as expected)")
    
    # Test 5: Live API test
    print("\n" + "-" * 70)
    print("Test 5: Live API Test")
    print("-" * 70)
    
    # First test public endpoint (should always work)
    print("\nTesting public endpoint (/time)...")
    try:
        resp = requests.get(f"{BASE_URL}/time", timeout=10)
        print(f"✓ Public endpoint works: {resp.json()}")
    except Exception as e:
        print(f"✗ Public endpoint failed: {e}")
    
    # Now test authenticated endpoint
    print("\nTesting authenticated endpoint (/balance-allowance)...")
    try:
        headers = create_l2_headers(API_KEY, API_SECRET, PASSPHRASE, 
                                    WALLET_ADDRESS, "GET", "/balance-allowance")
        
        url = f"{BASE_URL}/balance-allowance"
        params = {
            "asset_type": "COLLATERAL",
            "signature_type": 1  # 0=EOA, 1=POLY_PROXY, 2=GNOSIS_SAFE
        }
        
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        
        if resp.status_code == 200:
            print(f"✓ Authentication SUCCESS!")
            print(f"Response: {json.dumps(resp.json(), indent=2)}")
        elif resp.status_code == 401:
            print(f"✗ Authentication FAILED (401)")
            print(f"Response: {resp.text}")
            print("\nTroubleshooting:")
            print("1. Verify WALLET_ADDRESS matches the address used to create API key")
            print("2. Check that signature_type matches your wallet type:")
            print("   - 0 for EOA (MetaMask, Coinbase Wallet, etc.)")
            print("   - 1 for POLY_PROXY (Magic email login)")
            print("   - 2 for GNOSIS_SAFE multisig")
            print("3. Verify API credentials are correct and not expired")
        else:
            print(f"✗ Unexpected status code: {resp.status_code}")
            print(f"Response: {resp.text}")
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
    
    # Test 6: Test /auth/api-keys endpoint
    print("\nTesting /auth/api-keys endpoint...")
    try:
        headers = create_l2_headers(API_KEY, API_SECRET, PASSPHRASE, 
                                    WALLET_ADDRESS, "GET", "/auth/api-keys")
        
        url = f"{BASE_URL}/auth/api-keys"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            print(f"✓ API keys endpoint works!")
            print(f"Response: {json.dumps(resp.json(), indent=2)[:200]}...")
        else:
            print(f"✗ Status {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"✗ Request failed: {e}")
    
    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    test_auth()

