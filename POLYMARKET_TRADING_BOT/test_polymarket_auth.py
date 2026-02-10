#!/usr/bin/env python3
"""
Polymarket Authentication Test Script

This script attempts multiple authentication methods against Polymarket's API
to determine which method works correctly with the provided credentials.

Usage:
    python test_polymarket_auth.py

Environment Variables Required:
    POLYMARKET_API_KEY - Your Polymarket API key
    POLYMARKET_API_SECRET - Your Polymarket API secret
"""

import os
import sys
import time
import json
import base64
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple

import requests

# Configuration
API_KEY = os.getenv("POLYMARKET_API_KEY", "")
API_SECRET = os.getenv("POLYMARKET_API_SECRET", "")

# Polymarket API endpoints
BASE_URL = "https://clob.polymarket.com"
TEST_ENDPOINT = "/balance-allowances"

# ANSI colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def log_info(msg: str):
    print(f"{BLUE}[INFO]{RESET} {msg}")


def log_success(msg: str):
    print(f"{GREEN}[SUCCESS]{RESET} {msg}")


def log_error(msg: str):
    print(f"{RED}[ERROR]{RESET} {msg}")


def log_warning(msg: str):
    print(f"{YELLOW}[WARNING]{RESET} {msg}")


def log_attempt(method_name: str, attempt_num: int):
    print(f"\n{'='*60}")
    print(f"ATTEMPT {attempt_num}: {method_name}")
    print(f"{'='*60}")


def test_auth_method(method_name: str, headers: Dict[str, str], params: Optional[Dict] = None, 
                     use_post: bool = False, body: Optional[Dict] = None) -> Tuple[bool, int, str]:
    """
    Test an authentication method against the balance-allowance endpoint.
    
    Returns: (success: bool, status_code: int, response_text: str)
    """
    url = f"{BASE_URL}{TEST_ENDPOINT}"
    
    try:
        if use_post and body:
            response = requests.post(url, headers=headers, json=body, timeout=10)
        else:
            response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            return True, response.status_code, response.text[:200]
        else:
            return False, response.status_code, response.text[:200]
    except Exception as e:
        return False, 0, str(e)


def attempt_1_basic_header_auth():
    """
    ATTEMPT 1: Basic Header Authentication
    
    Try standard API key/secret in headers with various formats:
    - X-API-KEY / X-API-SECRET
    - api-key / api-secret
    - Authorization header with Basic auth
    """
    log_attempt("Basic Header Authentication", 1)
    
    methods_to_try = [
        # Method 1a: X-API-KEY and X-API-SECRET headers
        {
            "headers": {
                "X-API-KEY": API_KEY,
                "X-API-SECRET": API_SECRET,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "X-API-KEY / X-API-SECRET headers"
        },
        # Method 1b: api-key and api-secret headers (lowercase)
        {
            "headers": {
                "api-key": API_KEY,
                "api-secret": API_SECRET,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "api-key / api-secret headers (lowercase)"
        },
        # Method 1c: Polymarket-specific headers
        {
            "headers": {
                "POLYMARKET-API-KEY": API_KEY,
                "POLYMARKET-API-SECRET": API_SECRET,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "POLYMARKET-API-KEY / POLYMARKET-API-SECRET headers"
        },
        # Method 1d: Basic authentication
        {
            "headers": {
                "Authorization": f"Basic {base64.b64encode(f'{API_KEY}:{API_SECRET}'.encode()).decode()}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "Basic Authentication header"
        },
    ]
    
    for method in methods_to_try:
        log_info(f"Trying: {method['name']}")
        success, status, response = test_auth_method(method['name'], method['headers'])
        
        if success:
            log_success(f"SUCCESS with: {method['name']}")
            log_info(f"Response: {response}")
            return True, method['headers'], "header"
        else:
            log_warning(f"Failed (status {status}): {response[:100]}")
    
    return False, None, None


def attempt_2_timestamp_signed_auth():
    """
    ATTEMPT 2: Timestamp-based Signed Authentication
    
    Many APIs require signing requests with HMAC using:
    - Current timestamp
    - API Key
    - Signature = HMAC(timestamp + API_KEY, SECRET)
    """
    log_attempt("Timestamp-based Signed Authentication (HMAC)", 2)
    
    timestamp = str(int(time.time()))
    
    methods_to_try = [
        # Method 2a: Standard HMAC-SHA256 signature
        {
            "headers": {
                "X-API-KEY": API_KEY,
                "X-TIMESTAMP": timestamp,
                "X-SIGNATURE": hmac.new(
                    API_SECRET.encode(),
                    f"{timestamp}{API_KEY}".encode(),
                    hashlib.sha256
                ).hexdigest(),
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "HMAC-SHA256(timestamp + api_key)"
        },
        # Method 2b: HMAC with just timestamp
        {
            "headers": {
                "X-API-KEY": API_KEY,
                "X-TIMESTAMP": timestamp,
                "X-SIGNATURE": hmac.new(
                    API_SECRET.encode(),
                    timestamp.encode(),
                    hashlib.sha256
                ).hexdigest(),
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "HMAC-SHA256(timestamp)"
        },
        # Method 2c: Hex signature
        {
            "headers": {
                "X-API-KEY": API_KEY,
                "X-TIMESTAMP": timestamp,
                "X-SIGNATURE-HEX": hmac.new(
                    API_SECRET.encode(),
                    timestamp.encode(),
                    hashlib.sha256
                ).hexdigest(),
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "HMAC-SHA256 with hex signature"
        },
        # Method 2d: ISO timestamp
        {
            "headers": {
                "X-API-KEY": API_KEY,
                "X-TIMESTAMP": datetime.now(timezone.utc).isoformat(),
                "X-SIGNATURE": hmac.new(
                    API_SECRET.encode(),
                    timestamp.encode(),
                    hashlib.sha256
                ).hexdigest(),
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "HMAC with ISO timestamp"
        },
    ]
    
    for method in methods_to_try:
        log_info(f"Trying: {method['name']}")
        success, status, response = test_auth_method(method['name'], method['headers'])
        
        if success:
            log_success(f"SUCCESS with: {method['name']}")
            log_info(f"Response: {response}")
            return True, method['headers'], "hmac"
        else:
            log_warning(f"Failed (status {status}): {response[:100]}")
    
    return False, None, None


def attempt_3_ethereum_eip712_signing():
    """
    ATTEMPT 3: EIP-712 Ethereum Message Signing
    
    If the API secret is actually an Ethereum private key, we need to:
    1. Decode the base64 private key
    2. Create an Ethereum account
    3. Sign an EIP-712 typed data message or standard message
    4. Include the signature in the request
    
    NOTE: Requires eth-account library: pip install eth-account
    """
    log_attempt("EIP-712 Ethereum Message Signing", 3)
    
    try:
        from eth_account import Account
        from eth_account.messages import encode_defunct, encode_structured_data
    except ImportError:
        log_warning("eth-account library not installed. Run: pip install eth-account")
        return False, None, None
    
    # Try to decode the secret as base64 private key
    try:
        decoded_secret = base64.b64decode(API_SECRET)
        private_key_hex = decoded_secret.hex()
        log_info(f"Decoded secret to hex: {private_key_hex[:10]}...")
    except Exception as e:
        log_warning(f"Could not decode secret as base64: {e}")
        # Try using the secret directly as hex private key
        private_key_hex = API_SECRET
        log_info(f"Using secret directly as private key")
    
    # Try to create Ethereum account
    try:
        account = Account.from_key(private_key_hex)
        address = account.address
        log_info(f"Derived Ethereum address: {address}")
    except Exception as e:
        log_error(f"Could not create account from private key: {e}")
        return False, None, None
    
    timestamp = str(int(time.time()))
    
    # EIP-712 Domain and Message
    domain = {
        "name": "Polymarket",
        "version": "1",
    }
    
    message_types = {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
        ],
        "Authentication": [
            {"name": "timestamp", "type": "uint256"},
            {"name": "address", "type": "address"},
        ],
    }
    
    message_data = {
        "timestamp": int(timestamp),
        "address": address,
    }
    
    methods_to_try = [
        # Method 3a: Standard message signing
        {
            "headers": {
                "X-API-KEY": API_KEY,
                "X-ADDRESS": address,
                "X-TIMESTAMP": timestamp,
                "X-SIGNATURE": account.sign_message(encode_defunct(text=f"Polymarket Auth {timestamp}")).signature.hex(),
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "Standard message signing"
        },
        # Method 3b: EIP-712 structured data signing
        {
            "headers": {
                "X-API-KEY": API_KEY,
                "X-ADDRESS": address,
                "X-TIMESTAMP": timestamp,
                "X-SIGNATURE": account.sign_message(
                    encode_structured_data({
                        "types": message_types,
                        "domain": domain,
                        "primaryType": "Authentication",
                        "message": message_data
                    })
                ).signature.hex(),
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "EIP-712 structured data signing"
        },
        # Method 3c: Signature in body (POST request)
        {
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "body": {
                "apiKey": API_KEY,
                "address": address,
                "timestamp": int(timestamp),
                "signature": account.sign_message(encode_defunct(text=f"Polymarket Auth {timestamp}")).signature.hex()
            },
            "name": "POST with signature in body",
            "use_post": True
        },
    ]
    
    for method in methods_to_try:
        log_info(f"Trying: {method['name']}")
        
        if method.get("use_post"):
            success, status, response = test_auth_method(
                method['name'], 
                method['headers'], 
                use_post=True, 
                body=method.get("body")
            )
        else:
            success, status, response = test_auth_method(method['name'], method['headers'])
        
        if success:
            log_success(f"SUCCESS with: {method['name']}")
            log_info(f"Response: {response}")
            return True, method['headers'], "ethereum"
        else:
            log_warning(f"Failed (status {status}): {response[:100]}")
    
    return False, None, None


def attempt_4_jwt_token_auth():
    """
    ATTEMPT 4: JWT Token Exchange
    
    Some APIs require exchanging API credentials for a JWT token first.
    """
    log_attempt("JWT Token Exchange", 4)
    
    # Try various auth endpoints that might issue JWT tokens
    auth_endpoints = [
        "/auth/token",
        "/api/auth/token",
        "/v1/auth/token",
        "/authenticate",
        "/auth",
        "/login",
    ]
    
    for endpoint in auth_endpoints:
        url = f"{BASE_URL}{endpoint}"
        log_info(f"Trying auth endpoint: {url}")
        
        # Try POST with credentials in body
        try:
            response = requests.post(url, json={
                "apiKey": API_KEY,
                "apiSecret": API_SECRET
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data or "accessToken" in data:
                    token = data.get("token") or data.get("accessToken")
                    log_success(f"Got JWT token from {endpoint}")
                    
                    # Test the token
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                    
                    success, status, response_text = test_auth_method("JWT Bearer Token", headers)
                    if success:
                        log_success("JWT token authentication SUCCESS")
                        return True, headers, "jwt"
        except Exception as e:
            log_warning(f"Auth endpoint {endpoint} failed: {e}")
    
    # Also try creating our own JWT if secret is a JWT secret
    try:
        import jwt
        log_info("Trying to create self-signed JWT...")
        
        payload = {
            "apiKey": API_KEY,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        token = jwt.encode(payload, API_SECRET, algorithm="HS256")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        success, status, response = test_auth_method("Self-signed JWT", headers)
        if success:
            log_success("Self-signed JWT authentication SUCCESS")
            return True, headers, "jwt"
    except ImportError:
        log_warning("PyJWT library not installed. Run: pip install pyjwt")
    except Exception as e:
        log_warning(f"Self-signed JWT failed: {e}")
    
    return False, None, None


def attempt_5_request_body_auth():
    """
    ATTEMPT 5: Request Body Authentication
    
    Try sending credentials in the POST request body instead of headers.
    """
    log_attempt("Request Body Authentication", 5)
    
    timestamp = str(int(time.time()))
    
    methods_to_try = [
        # Method 5a: Simple key/secret in body
        {
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "body": {
                "apiKey": API_KEY,
                "apiSecret": API_SECRET
            },
            "name": "key/secret in POST body"
        },
        # Method 5b: With timestamp and signature
        {
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "body": {
                "apiKey": API_KEY,
                "timestamp": timestamp,
                "signature": hmac.new(
                    API_SECRET.encode(),
                    f"{timestamp}{API_KEY}".encode(),
                    hashlib.sha256
                ).hexdigest()
            },
            "name": "key + timestamp + HMAC in POST body"
        },
        # Method 5c: Nested auth object
        {
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "body": {
                "auth": {
                    "apiKey": API_KEY,
                    "apiSecret": API_SECRET
                }
            },
            "name": "Nested auth object in POST body"
        },
    ]
    
    for method in methods_to_try:
        log_info(f"Trying: {method['name']}")
        success, status, response = test_auth_method(
            method['name'], 
            method['headers'], 
            use_post=True, 
            body=method['body']
        )
        
        if success:
            log_success(f"SUCCESS with: {method['name']}")
            log_info(f"Response: {response}")
            return True, method['headers'], "body"
        else:
            log_warning(f"Failed (status {status}): {response[:100]}")
    
    return False, None, None


def attempt_6_swapped_credentials():
    """
    ATTEMPT 6: Swapped Credentials
    
    Maybe the key and secret are swapped - try using secret as key and vice versa.
    """
    log_attempt("Swapped Credentials", 6)
    
    methods_to_try = [
        # Method 6a: Basic headers swapped
        {
            "headers": {
                "X-API-KEY": API_SECRET,
                "X-API-SECRET": API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "Swapped X-API-KEY / X-API-SECRET"
        },
        # Method 6b: Swapped lowercase headers
        {
            "headers": {
                "api-key": API_SECRET,
                "api-secret": API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "Swapped lowercase headers"
        },
        # Method 6c: Just the secret as key (no secret header)
        {
            "headers": {
                "X-API-KEY": API_SECRET,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "Secret only as X-API-KEY"
        },
        # Method 6d: Just the key as key (no secret header)
        {
            "headers": {
                "X-API-KEY": API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "name": "Key only as X-API-KEY (no secret)"
        },
    ]
    
    for method in methods_to_try:
        log_info(f"Trying: {method['name']}")
        success, status, response = test_auth_method(method['name'], method['headers'])
        
        if success:
            log_success(f"SUCCESS with: {method['name']}")
            log_info(f"Response: {response}")
            return True, method['headers'], "swapped"
        else:
            log_warning(f"Failed (status {status}): {response[:100]}")
    
    return False, None, None


def attempt_7_query_param_auth():
    """
    ATTEMPT 7: Query Parameter Authentication
    
    Try sending credentials as URL query parameters.
    """
    log_attempt("Query Parameter Authentication", 7)
    
    methods_to_try = [
        # Method 7a: Key/secret as query params
        {
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "params": {
                "apiKey": API_KEY,
                "apiSecret": API_SECRET
            },
            "name": "key/secret as query params"
        },
        # Method 7b: Key only as query param
        {
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "params": {
                "api_key": API_KEY
            },
            "name": "api_key as query param"
        },
        # Method 7c: Token as query param
        {
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "params": {
                "token": API_SECRET
            },
            "name": "token as query param"
        },
    ]
    
    for method in methods_to_try:
        log_info(f"Trying: {method['name']}")
        
        try:
            url = f"{BASE_URL}{TEST_ENDPOINT}"
            response = requests.get(url, headers=method['headers'], params=method['params'], timeout=10)
            
            if response.status_code == 200:
                log_success(f"SUCCESS with: {method['name']}")
                log_info(f"Response: {response.text[:200]}")
                return True, method['headers'], "query"
            else:
                log_warning(f"Failed (status {response.status_code}): {response.text[:100]}")
        except Exception as e:
            log_warning(f"Error: {e}")
    
    return False, None, None


def attempt_8_session_cookie_auth():
    """
    ATTEMPT 8: Session/Cookie Authentication
    
    Try establishing a session and using cookies for authentication.
    """
    log_attempt("Session/Cookie Authentication", 8)
    
    session = requests.Session()
    
    # Try to hit an auth/login endpoint first
    login_endpoints = [
        "/auth/login",
        "/api/login",
        "/login",
        "/auth",
        "/authenticate",
    ]
    
    for endpoint in login_endpoints:
        login_url = f"{BASE_URL}{endpoint}"
        log_info(f"Trying login at: {login_url}")
        
        try:
            # Try POST with credentials
            login_response = session.post(login_url, json={
                "apiKey": API_KEY,
                "apiSecret": API_SECRET
            }, timeout=10)
            
            log_info(f"Login response: {login_response.status_code}")
            
            # Now try the test endpoint with the session
            test_response = session.get(
                f"{BASE_URL}{TEST_ENDPOINT}",
                headers={"Accept": "application/json"},
                timeout=10
            )
            
            if test_response.status_code == 200:
                log_success(f"SUCCESS with session authentication via {endpoint}")
                log_info(f"Response: {test_response.text[:200]}")
                return True, dict(session.headers), "session"
            else:
                log_warning(f"Session auth failed (status {test_response.status_code})")
                
        except Exception as e:
            log_warning(f"Session auth error: {e}")
    
    return False, None, None


def save_working_config(method_name: str, headers: Dict[str, str], auth_type: str):
    """Save the working authentication configuration to a file."""
    config = {
        "auth_type": auth_type,
        "method_name": method_name,
        "base_url": BASE_URL,
        "headers": headers,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python_example": f"""
# Working Polymarket Authentication Code
import requests

BASE_URL = "{BASE_URL}"
HEADERS = {json.dumps(headers, indent=4)}

# Example: Get balance allowance
response = requests.get(f"{{BASE_URL}}/balance-allowances", headers=HEADERS)
print(response.json())
"""
    }
    
    with open("POLYMARKET_TRADING_BOT/working_auth_config.json", "w") as f:
        json.dump(config, f, indent=4)
    
    log_success("Saved working auth config to POLYMARKET_TRADING_BOT/working_auth_config.json")


def print_final_summary(success: bool, method_name: str = None, headers: Dict = None, auth_type: str = None):
    """Print final summary of test results."""
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    if success:
        print(f"\n{GREEN}✅ AUTHENTICATION SUCCESSFUL{RESET}")
        print(f"\nWorking Method: {method_name}")
        print(f"Auth Type: {auth_type}")
        print(f"\nWorking Headers:")
        for key, value in headers.items():
            # Mask sensitive values
            if "secret" in key.lower() or "signature" in key.lower():
                display_value = value[:10] + "..." if len(value) > 10 else value
            else:
                display_value = value
            print(f"  {key}: {display_value}")
        
        print(f"\n{BLUE}Working configuration saved to: POLYMARKET_TRADING_BOT/working_auth_config.json{RESET}")
        
        print(f"\n{GREEN}Example Python Code:{RESET}")
        print("-" * 50)
        print(f"""
import requests

BASE_URL = "{BASE_URL}"
HEADERS = {json.dumps(headers, indent=4)}

# Test the connection
response = requests.get(f"{{BASE_URL}}/balance-allowances", headers=HEADERS)
if response.status_code == 200:
    print("Success! Balance:", response.json())
else:
    print(f"Error: {{response.status_code}}")
""")
        print("-" * 50)
    else:
        print(f"\n{RED}❌ ALL AUTHENTICATION METHODS FAILED{RESET}")
        print("\nPossible issues:")
        print("  - Invalid or expired API credentials")
        print("  - API key/secret not properly configured")
        print("  - Network connectivity issues")
        print("  - API endpoint may have changed")
        print("  - Missing required Python libraries (eth-account, pyjwt)")
    
    print("\n" + "="*70)


def main():
    """Main function to run all authentication attempts."""
    print("="*70)
    print("POLYMARKET AUTHENTICATION TEST")
    print("="*70)
    print(f"API Key: {API_KEY[:10] + '...' if API_KEY else 'NOT SET'}")
    print(f"API Secret: {'SET (hidden)' if API_SECRET else 'NOT SET'}")
    print(f"Test Endpoint: {BASE_URL}{TEST_ENDPOINT}")
    print("="*70)
    
    # Check if credentials are set
    if not API_KEY or not API_SECRET:
        log_error("API credentials not set!")
        print("\nPlease set environment variables:")
        print("  export POLYMARKET_API_KEY='your-api-key'")
        print("  export POLYMARKET_API_SECRET='your-api-secret'")
        sys.exit(1)
    
    # Try each authentication method in order
    auth_attempts = [
        ("Basic Header Auth", attempt_1_basic_header_auth),
        ("Timestamp Signed Auth", attempt_2_timestamp_signed_auth),
        ("Ethereum EIP-712 Signing", attempt_3_ethereum_eip712_signing),
        ("JWT Token Auth", attempt_4_jwt_token_auth),
        ("Request Body Auth", attempt_5_request_body_auth),
        ("Swapped Credentials", attempt_6_swapped_credentials),
        ("Query Parameter Auth", attempt_7_query_param_auth),
        ("Session/Cookie Auth", attempt_8_session_cookie_auth),
    ]
    
    for method_name, attempt_func in auth_attempts:
        success, headers, auth_type = attempt_func()
        
        if success:
            save_working_config(method_name, headers, auth_type)
            print_final_summary(True, method_name, headers, auth_type)
            sys.exit(0)
    
    # If we get here, no method worked
    print_final_summary(False)
    sys.exit(1)


if __name__ == "__main__":
    main()
