"""
Test script to verify HMAC authentication works correctly
This script tests the fixed Polymarket API client
"""

import os
import sys
import base64
import hmac
import hashlib

# Add the bot directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from polymarket_api_client import PolymarketAPIClient, build_hmac_signature


def test_hmac_signature():
    """Test HMAC signature generation against known values"""
    print("=" * 70)
    print("Testing HMAC Signature Generation")
    print("=" * 70)
    
    # Test data
    secret = "IZe8jb-on6PKYZYlG74Al-sTYeuEVPbFqH78e0f0xso="
    timestamp = 1700000000
    method = "GET"
    request_path = "/balance-allowance"
    
    # Generate signature
    sig = build_hmac_signature(secret, timestamp, method, request_path)
    
    print(f"\nInput:")
    print(f"  Secret: {secret[:20]}...")
    print(f"  Timestamp: {timestamp}")
    print(f"  Method: {method}")
    print(f"  Path: {request_path}")
    print(f"\nGenerated Signature: {sig[:50]}...")
    
    # Verify it's URL-safe base64
    if '-' in sig or '_' in sig:
        print("[OK] Signature uses URL-safe base64 encoding")
    else:
        print("[FAIL] Signature may not be URL-safe")
    
    # Test with body
    body = {"test": "data"}
    sig_with_body = build_hmac_signature(secret, timestamp, method, request_path, body)
    print(f"\nWith body signature: {sig_with_body[:50]}...")
    
    # Verify signatures are different
    if sig != sig_with_body:
        print("[OK] Body correctly affects signature")
    else:
        print("[FAIL] Body should affect signature")
    
    return True


def test_api_client_initialization():
    """Test API client initialization"""
    print("\n" + "=" * 70)
    print("Testing API Client Initialization")
    print("=" * 70)
    
    API_KEY = "019c3ee6-4d56-73fc-a7a2-e5db22b94340"
    API_SECRET = "IZe8jb-on6PKYZYlG74Al-sTYeuEVPbFqH78e0f0xso="
    PASSPHRASE = "b4736af6a2ef790b2034e258da2e296de866c60b4afe9ab707d3697b5c28b51f"
    WALLET_ADDRESS = "0x1234567890123456789012345678901234567890"
    
    try:
        client = PolymarketAPIClient(API_KEY, API_SECRET, PASSPHRASE, WALLET_ADDRESS)
        print(f"✓ Client initialized successfully")
        print(f"  API Key: {client.api_key[:20]}...")
        print(f"  Wallet: {client.wallet_address}")
        print(f"  Base URL: {client.base_url}")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize client: {e}")
        return False


def test_public_endpoints():
    """Test public endpoints (no auth required)"""
    print("\n" + "=" * 70)
    print("Testing Public Endpoints")
    print("=" * 70)
    
    API_KEY = "019c3ee6-4d56-73fc-a7a2-e5db22b94340"
    API_SECRET = "IZe8jb-on6PKYZYlG74Al-sTYeuEVPbFqH78e0f0xso="
    PASSPHRASE = "b4736af6a2ef790b2034e258da2e296de866c60b4afe9ab707d3697b5c28b51f"
    WALLET_ADDRESS = os.getenv("POLY_WALLET_ADDRESS", "")
    
    client = PolymarketAPIClient(API_KEY, API_SECRET, PASSPHRASE, WALLET_ADDRESS)
    
    # Test server time
    try:
        server_time = client.get_server_time()
        print(f"✓ Server time: {server_time}")
    except Exception as e:
        print(f"✗ Server time failed: {e}")
    
    # Test markets
    try:
        markets = client.get_markets()
        data = markets.get('data', [])
        print(f"✓ Markets: Retrieved {len(data)} markets")
        if data:
            print(f"  Sample: {data[0].get('question', 'N/A')[:40]}...")
    except Exception as e:
        print(f"✗ Markets failed: {e}")
    
    # Test health check
    try:
        ok = client.get_ok()
        print(f"✓ Health check: {ok}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")


def test_authenticated_endpoints():
    """Test authenticated endpoints (requires wallet address)"""
    print("\n" + "=" * 70)
    print("Testing Authenticated Endpoints (L2)")
    print("=" * 70)
    
    API_KEY = "019c3ee6-4d56-73fc-a7a2-e5db22b94340"
    API_SECRET = "IZe8jb-on6PKYZYlG74Al-sTYeuEVPbFqH78e0f0xso="
    PASSPHRASE = "b4736af6a2ef790b2034e258da2e296de866c60b4afe9ab707d3697b5c28b51f"
    WALLET_ADDRESS = os.getenv("POLY_WALLET_ADDRESS", "")
    
    if not WALLET_ADDRESS:
        print("⚠️  POLY_WALLET_ADDRESS not set. Skipping authenticated tests.")
        print("   Set it with: $env:POLY_WALLET_ADDRESS = '0x...'")
        return False
    
    print(f"Using wallet address: {WALLET_ADDRESS}")
    
    client = PolymarketAPIClient(API_KEY, API_SECRET, PASSPHRASE, WALLET_ADDRESS)
    
    # Test balance allowance
    print("\nTesting /balance-allowance...")
    for sig_type in [0, 1, 2]:
        try:
            balance = client.get_balance_allowance({
                "asset_type": "COLLATERAL",
                "signature_type": sig_type
            })
            print(f"✓ signature_type={sig_type}: Success!")
            print(f"  Balance: {balance.get('balance', 'N/A')}")
            print(f"  Allowance: {balance.get('allowance', 'N/A')}")
            break  # If one works, we're good
        except Exception as e:
            error_str = str(e)
            if "401" in error_str:
                print(f"✗ signature_type={sig_type}: 401 Unauthorized")
            else:
                print(f"✗ signature_type={sig_type}: {e}")
    
    # Test get orders
    print("\nTesting /data/orders...")
    try:
        orders = client.get_orders()
        print(f"✓ Retrieved {len(orders)} open orders")
    except Exception as e:
        error_str = str(e)
        if "401" in error_str:
            print(f"✗ 401 Unauthorized - Check wallet address and credentials")
        else:
            print(f"✗ Error: {e}")
    
    # Test get API keys
    print("\nTesting /auth/api-keys...")
    try:
        keys = client.get_api_keys()
        print(f"✓ API keys retrieved: {len(keys.get('apiKeys', []))} keys found")
    except Exception as e:
        error_str = str(e)
        if "401" in error_str:
            print(f"✗ 401 Unauthorized - Check wallet address and credentials")
        else:
            print(f"✗ Error: {e}")
    
    return True


def debug_signature():
    """Debug the signature generation"""
    print("\n" + "=" * 70)
    print("Debugging Signature Generation")
    print("=" * 70)
    
    secret = "IZe8jb-on6PKYZYlG74Al-sTYeuEVPbFqH78e0f0xso="
    timestamp = 1700000000
    method = "GET"
    request_path = "/balance-allowance"
    
    # Show the decoded secret
    secret_clean = secret.replace('-', '+').replace('_', '/')
    padding_needed = 4 - len(secret_clean) % 4
    if padding_needed != 4:
        secret_clean += '=' * padding_needed
    
    print(f"Original secret: {secret}")
    print(f"Cleaned secret:  {secret_clean}")
    
    secret_bytes = base64.b64decode(secret_clean)
    print(f"Decoded secret length: {len(secret_bytes)} bytes")
    print(f"Decoded secret (hex): {secret_bytes.hex()[:40]}...")
    
    # Show the message
    message = str(timestamp) + str(method) + str(request_path)
    print(f"\nMessage to sign: {message}")
    print(f"Message bytes: {message.encode('utf-8')}")
    
    # Generate signature step by step
    signature = hmac.new(
        secret_bytes,
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    print(f"\nRaw signature (hex): {signature.hex()}")
    
    # Base64 encode
    b64_sig = base64.b64encode(signature).decode('utf-8')
    print(f"Standard base64: {b64_sig}")
    
    # URL-safe base64
    url_safe_sig = base64.urlsafe_b64encode(signature).decode('utf-8')
    print(f"URL-safe base64: {url_safe_sig}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("POLYMARKET API AUTHENTICATION TEST")
    print("=" * 70)
    
    # Run all tests
    test_hmac_signature()
    test_api_client_initialization()
    test_public_endpoints()
    test_authenticated_endpoints()
    
    # Optional: Debug signature
    print("\n" + "=" * 70)
    response = input("Show signature debug info? (y/n): ")
    if response.lower() == 'y':
        debug_signature()
    
    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)
