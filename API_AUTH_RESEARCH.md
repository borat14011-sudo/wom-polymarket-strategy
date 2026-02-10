# Polymarket CLOB API Authentication Research

## Executive Summary

The Polymarket CLOB API uses a **two-level authentication system**:
- **L1 (Level 1)**: EIP-712 Ethereum signatures for creating/deriving API keys
- **L2 (Level 2)**: HMAC-SHA256 signatures using API credentials for trading endpoints

The 401 authentication errors were likely caused by **not base64-decoding the API secret** before using it as the HMAC key.

---

## Authentication Levels

### L1 Authentication (EIP-712 Signatures)

Used for:
- Creating API credentials (`POST /auth/api-key`)
- Deriving existing API credentials (`GET /auth/derive-api-key`)
- Signing orders locally

**Headers Required:**
```
POLY_ADDRESS: <ethereum_address>
POLY_SIGNATURE: <eip712_signature>
POLY_TIMESTAMP: <unix_timestamp>
POLY_NONCE: <nonce> (default: 0)
```

**EIP-712 Domain:**
```python
{
    "name": "ClobAuthDomain",
    "version": "1",
    "chainId": 137  # Polygon mainnet
}
```

**EIP-712 Message Structure:**
```python
{
    "address": "<wallet_address>",
    "timestamp": "<unix_timestamp_as_string>",
    "nonce": <integer>,
    "message": "This message attests that I control the given wallet"
}
```

### L2 Authentication (HMAC-SHA256)

Used for:
- Posting orders
- Canceling orders
- Getting open orders/trades
- Checking balances

**Headers Required:**
```
POLY_ADDRESS: <ethereum_address>
POLY_SIGNATURE: <hmac_signature>
POLY_TIMESTAMP: <unix_timestamp>
POLY_API_KEY: <api_key>
POLY_PASSPHRASE: <passphrase>
```

---

## The Critical Detail: API Secret is Base64 Encoded

### Why HMAC Failed (401 Unauthorized)

The API secret looks like base64 (ends with `=`) **because it IS base64-encoded**. You must decode it before using it as the HMAC key.

### Correct HMAC Implementation

```python
import hmac
import hashlib
import base64

def build_hmac_signature(secret: str, timestamp: int, method: str, request_path: str, body: str = None) -> str:
    """
    Creates an HMAC signature for Polymarket CLOB L2 authentication.
    
    Args:
        secret: The API secret (base64url encoded string from API credentials)
        timestamp: Unix timestamp
        method: HTTP method (GET, POST, DELETE, etc.)
        request_path: The API endpoint path (e.g., "/orders")
        body: Request body for POST/PUT requests (JSON string)
    
    Returns:
        URL-safe base64 encoded HMAC signature
    """
    # CRITICAL: Decode the base64url encoded secret
    # The secret uses URL-safe base64 (replaces + with -, / with _)
    base64_secret = base64.urlsafe_b64decode(secret)
    
    # Build the message: timestamp + method + request_path + body
    message = str(timestamp) + str(method) + str(request_path)
    if body:
        # IMPORTANT: Replace single quotes with double quotes to match Go/TypeScript
        message += str(body).replace("'", '"')
    
    # Create HMAC-SHA256 signature
    h = hmac.new(base64_secret, bytes(message, "utf-8"), hashlib.sha256)
    
    # Return URL-safe base64 encoded signature
    return base64.urlsafe_b64encode(h.digest()).decode("utf-8")
```

### Key Points

1. **Decode the Secret**: Use `base64.urlsafe_b64decode(secret)` not just `secret.encode()`
2. **URL-Safe Base64**: The secret uses URL-safe variant ( `-` instead of `+`, `_` instead of `/`)
3. **Message Format**: Concatenate `timestamp + method + request_path + body`
4. **Body Handling**: For requests with body (POST/PUT), include it in the message
5. **Quote Replacement**: Replace single quotes with double quotes in the body to match other implementations

---

## Required Python Packages

### Minimal Dependencies (for L2 auth only)
```bash
pip install eth-account  # For address derivation from private key
```

### Full Trading Client
```bash
pip install py-clob-client  # Official Polymarket Python client
```

### Standard Library (built-in)
- `hmac` - HMAC signature generation
- `hashlib` - SHA256 hashing
- `base64` - Base64 encoding/decoding
- `json` - JSON serialization
- `time` / `datetime` - Timestamps

---

## Complete Working Example

```python
import hmac
import hashlib
import base64
import json
import time
import requests
from eth_account import Account

class PolymarketCLOBAuth:
    """
    L2 Authentication handler for Polymarket CLOB API.
    """
    
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str, private_key: str):
        """
        Initialize with API credentials.
        
        Args:
            api_key: The API key from create/derive API key response
            api_secret: The API secret (base64url encoded)
            api_passphrase: The API passphrase
            private_key: Your Ethereum private key (for address derivation)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        
        # Derive address from private key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        
    def _build_signature(self, method: str, path: str, body: dict = None) -> str:
        """Build HMAC-SHA256 signature for request."""
        timestamp = int(time.time())
        
        # Build message
        message = str(timestamp) + str(method) + str(path)
        if body is not None:
            # Must use double quotes, compact JSON (no extra spaces)
            body_json = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
            message += body_json
        
        # CRITICAL: Decode base64url secret before using as HMAC key
        secret_bytes = base64.urlsafe_b64decode(self.api_secret)
        
        # Generate HMAC
        signature = hmac.new(
            secret_bytes,
            message.encode("utf-8"),
            hashlib.sha256
        ).digest()
        
        # Return URL-safe base64 encoded signature
        return base64.urlsafe_b64encode(signature).decode("utf-8")
    
    def get_headers(self, method: str, path: str, body: dict = None) -> dict:
        """Get authentication headers for a request."""
        timestamp = int(time.time())
        signature = self._build_signature(method, path, body)
        
        return {
            "POLY_ADDRESS": self.address,
            "POLY_SIGNATURE": signature,
            "POLY_TIMESTAMP": str(timestamp),
            "POLY_API_KEY": self.api_key,
            "POLY_PASSPHRASE": self.api_passphrase,
            "Content-Type": "application/json"
        }


# Example usage
if __name__ == "__main__":
    # Your credentials (from create_or_derive_api_key response)
    API_KEY = "your-api-key"
    API_SECRET = "your-base64-encoded-secret"  # Ends with =
    API_PASSPHRASE = "your-passphrase"
    PRIVATE_KEY = "your-private-key"
    
    # Initialize auth handler
    auth = PolymarketCLOBAuth(API_KEY, API_SECRET, API_PASSPHRASE, PRIVATE_KEY)
    
    # Make authenticated request
    HOST = "https://clob.polymarket.com"
    
    # GET request example (no body)
    headers = auth.get_headers("GET", "/orders")
    response = requests.get(f"{HOST}/orders", headers=headers)
    print(f"Orders: {response.status_code}")
    
    # POST request example (with body)
    order_body = {
        "order": {
            "salt": 1234567890,
            "maker": auth.address,
            "signer": auth.address,
            # ... other order fields
        },
        "owner": auth.address,
        "orderType": "GTC"
    }
    headers = auth.get_headers("POST", "/order", order_body)
    response = requests.post(f"{HOST}/order", headers=headers, json=order_body)
    print(f"Post order: {response.status_code}")
```

---

## Common Mistakes

### ❌ Wrong: Using raw secret
```python
# WRONG - secret is base64 encoded!
secret = api_secret.encode('utf-8')
hmac.new(secret, message.encode(), hashlib.sha256)
```

### ✅ Correct: Decode base64 first
```python
# CORRECT - decode base64url encoded secret
secret = base64.urlsafe_b64decode(api_secret)
hmac.new(secret, message.encode(), hashlib.sha256)
```

### ❌ Wrong: Using standard base64 decode
```python
# WRONG - API uses URL-safe base64
secret = base64.b64decode(api_secret)  # May fail or give wrong result
```

### ✅ Correct: Use URL-safe base64 decode
```python
# CORRECT - handles - and _ characters
secret = base64.urlsafe_b64decode(api_secret)
```

---

## Signature Type Reference

When initializing the client, you must specify your wallet type:

| Signature Type | Value | Description |
|---------------|-------|-------------|
| EOA | 0 | MetaMask, hardware wallets, any standard EOA |
| POLY_PROXY | 1 | Email/Magic wallet (delegated signing) |
| GNOSIS_SAFE | 2 | Gnosis Safe multisig proxy wallet |

---

## Resources

- **Official TypeScript Client**: https://github.com/Polymarket/clob-client
- **Official Python Client**: https://github.com/Polymarket/py-clob-client
- **Documentation**: https://docs.polymarket.com/developers/CLOB/authentication
- **HMAC Reference (TypeScript)**: https://github.com/Polymarket/clob-client/blob/main/src/signing/hmac.ts
- **HMAC Reference (Python)**: https://github.com/Polymarket/py-clob-client/blob/main/py_clob_client/signing/hmac.py

---

## Summary: Why HMAC Failed

The HMAC-SHA256 implementation was correct in concept but missed one critical detail:

**The API secret is base64url-encoded and must be decoded before use as the HMAC key.**

The secret that looks like `d2hhdGV2ZXI=` is NOT the raw key - it's an encoded version of the actual 32-byte key. Using it directly as the HMAC key produces the wrong signature, resulting in 401 Unauthorized.

Always decode with `base64.urlsafe_b64decode(secret)` before passing to `hmac.new()`.
