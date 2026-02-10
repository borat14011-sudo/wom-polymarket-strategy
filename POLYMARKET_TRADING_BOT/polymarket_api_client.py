"""
Polymarket API Client - FIXED VERSION v2.0
Based on official py-clob-client implementation
Proper HMAC authentication following Polymarket's reference implementation
"""

import os
import json
import hmac
import hashlib
import base64
import time
import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin
from datetime import datetime


# Header names for Polymarket CLOB API
POLY_ADDRESS = "POLY_ADDRESS"
POLY_SIGNATURE = "POLY_SIGNATURE"
POLY_TIMESTAMP = "POLY_TIMESTAMP"
POLY_API_KEY = "POLY_API_KEY"
POLY_PASSPHRASE = "POLY_PASSPHRASE"


def build_hmac_signature(secret: str, timestamp, method: str, request_path: str, body=None) -> str:
    """
    Builds HMAC signature exactly like the official py-clob-client
    
    Args:
        secret: Base64url encoded API secret
        timestamp: Unix timestamp (int or string)
        method: HTTP method (GET, POST, DELETE)
        request_path: API endpoint path
        body: Optional request body
    
    Returns:
        URL-safe base64 encoded HMAC signature
    """
    # Decode base64url secret to bytes
    # Handle both base64url and standard base64
    secret_clean = secret.replace('-', '+').replace('_', '/')
    # Add padding if needed
    padding_needed = 4 - len(secret_clean) % 4
    if padding_needed != 4:
        secret_clean += '=' * padding_needed
    
    secret_bytes = base64.b64decode(secret_clean)
    
    # Build message: timestamp + method + path + body
    message = str(timestamp) + str(method) + str(request_path)
    if body is not None:
        # NOTE: Necessary to replace single quotes with double quotes
        # to generate the same hmac message as go and typescript
        message += str(body).replace("'", '"')
    
    # Create HMAC-SHA256
    signature = hmac.new(
        secret_bytes,
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    # Return URL-safe base64 encoded signature
    return base64.urlsafe_b64encode(signature).decode('utf-8')


class PolymarketAPIClient:
    """
    Professional API client for Polymarket CLOB API with correct L2 authentication
    Based on official py-clob-client implementation
    """
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str, wallet_address: str):
        """
        Initialize API client with L2 credentials
        
        Args:
            api_key: Your Polymarket API key
            api_secret: Your Polymarket API secret (base64url encoded)
            passphrase: Your API passphrase
            wallet_address: Your Polygon wallet address (required for L2 auth)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.wallet_address = wallet_address.lower() if wallet_address else ""
        self.base_url = "https://clob.polymarket.com"
        
    def _create_level_2_headers(self, method: str, request_path: str, body: Any = None) -> Dict[str, str]:
        """
        Create Level 2 authentication headers following official implementation
        """
        timestamp = int(datetime.now().timestamp())
        
        # Serialize body for signature if provided
        body_for_sig = None
        if body is not None:
            if isinstance(body, dict):
                body_for_sig = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
            else:
                body_for_sig = str(body)
        
        # Generate HMAC signature
        signature = build_hmac_signature(
            self.api_secret,
            timestamp,
            method,
            request_path,
            body_for_sig
        )
        
        headers = {
            POLY_ADDRESS: self.wallet_address,
            POLY_SIGNATURE: signature,
            POLY_TIMESTAMP: str(timestamp),
            POLY_API_KEY: self.api_key,
            POLY_PASSPHRASE: self.passphrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "polymarket-python-client/2.0"
        }
        return headers
    
    def _make_request(self, method: str, path: str, body: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        """
        Make authenticated API request
        """
        url = urljoin(self.base_url, path)
        headers = self._create_level_2_headers(method, path, body)
        
        # Serialize body for request
        data = None
        if body is not None:
            data = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, data=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, data=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Print response info for debugging
            if response.status_code != 200:
                print(f"API Error {response.status_code}: {response.text}")
            
            response.raise_for_status()
            
            # Return JSON if possible, else text
            try:
                return response.json()
            except ValueError:
                return response.text
                
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {e}")
            raise
    
    # ========== Public Endpoints (no auth required) ==========
    
    def get_server_time(self) -> int:
        """Get current server timestamp"""
        url = f"{self.base_url}/time"
        response = requests.get(url, timeout=10)
        return response.json()
    
    def get_ok(self) -> Any:
        """Health check"""
        url = f"{self.base_url}/"
        response = requests.get(url, timeout=10)
        return response.json()
    
    def get_markets(self) -> Dict[str, Any]:
        """Get list of available markets"""
        url = f"{self.base_url}/markets"
        response = requests.get(url, timeout=10)
        return response.json()
    
    def get_market(self, condition_id: str) -> Dict[str, Any]:
        """Get details for specific market by condition ID"""
        url = f"{self.base_url}/markets/{condition_id}"
        response = requests.get(url, timeout=10)
        return response.json()
    
    def get_order_book(self, token_id: str) -> Dict[str, Any]:
        """Get order book for market by token ID"""
        url = f"{self.base_url}/book?token_id={token_id}"
        response = requests.get(url, timeout=10)
        return response.json()
    
    def get_midpoint(self, token_id: str) -> Dict[str, Any]:
        """Get midpoint price for a token"""
        url = f"{self.base_url}/midpoint?token_id={token_id}"
        response = requests.get(url, timeout=10)
        return response.json()
    
    def get_price(self, token_id: str, side: str) -> Dict[str, Any]:
        """Get price for a token (BUY or SELL side)"""
        url = f"{self.base_url}/price?token_id={token_id}&side={side}"
        response = requests.get(url, timeout=10)
        return response.json()
    
    def get_last_trade_price(self, token_id: str) -> Dict[str, Any]:
        """Get last trade price for a token"""
        url = f"{self.base_url}/last-trade-price?token_id={token_id}"
        response = requests.get(url, timeout=10)
        return response.json()
    
    def get_tick_size(self, token_id: str) -> str:
        """Get minimum tick size for a token"""
        url = f"{self.base_url}/tick-size?token_id={token_id}"
        response = requests.get(url, timeout=10)
        result = response.json()
        return str(result.get("minimum_tick_size", "0.01"))
    
    def get_neg_risk(self, token_id: str) -> bool:
        """Check if market is negative risk"""
        url = f"{self.base_url}/neg-risk?token_id={token_id}"
        response = requests.get(url, timeout=10)
        result = response.json()
        return result.get("neg_risk", False)
    
    # ========== L2 Authenticated Endpoints ==========
    
    def get_balance_allowance(self, params: Dict = None) -> Dict[str, Any]:
        """
        Get account balance and allowance
        
        Args:
            params: Dict with optional keys:
                - asset_type: "COLLATERAL" for USDC or "CONDITIONAL" for outcome tokens
                - token_id: Token ID (required for CONDITIONAL type)
                - signature_type: 0 for EOA, 1 for POLY_PROXY (Magic login), 2 for GNOSIS_SAFE
        """
        if params is None:
            params = {}
        
        # Build query string manually to match exact format
        query_parts = []
        if "asset_type" in params:
            query_parts.append(f"asset_type={params['asset_type']}")
        if "token_id" in params:
            query_parts.append(f"token_id={params['token_id']}")
        if "signature_type" in params:
            query_parts.append(f"signature_type={params['signature_type']}")
        
        path = "/balance-allowance"
        if query_parts:
            path += "?" + "&".join(query_parts)
        
        return self._make_request("GET", path)
    
    def get_orders(self, market: str = None, asset_id: str = None) -> list:
        """
        Get list of your open orders
        
        Args:
            market: Optional market condition ID to filter
            asset_id: Optional asset/token ID to filter
        """
        params = {}
        if market:
            params["market"] = market
        if asset_id:
            params["asset_id"] = asset_id
            
        result = self._make_request("GET", "/data/orders", params=params)
        return result.get("data", []) if isinstance(result, dict) else result
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get specific order by ID"""
        return self._make_request("GET", f"/data/order/{order_id}")
    
    def get_trades(self, market: str = None, asset_id: str = None) -> list:
        """
        Get your trade history
        
        Args:
            market: Optional market condition ID to filter
            asset_id: Optional asset/token ID to filter
        """
        params = {}
        if market:
            params["market"] = market
        if asset_id:
            params["asset_id"] = asset_id
            
        result = self._make_request("GET", "/data/trades", params=params)
        return result.get("data", []) if isinstance(result, dict) else result
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an open order by ID"""
        body = {"orderID": order_id}
        return self._make_request("DELETE", "/order", body=body)
    
    def cancel_all_orders(self) -> Dict[str, Any]:
        """Cancel all open orders"""
        return self._make_request("DELETE", "/cancel-all")
    
    def cancel_orders(self, order_ids: list) -> Dict[str, Any]:
        """Cancel multiple orders by their IDs"""
        return self._make_request("DELETE", "/orders", body=order_ids)
    
    def get_api_keys(self) -> Dict[str, Any]:
        """Get API keys associated with this account"""
        return self._make_request("GET", "/auth/api-keys")
    
    def update_balance_allowance(self, params: Dict = None) -> Dict[str, Any]:
        """
        Update account balance and allowance
        """
        if params is None:
            params = {}
        
        # Build query string manually
        query_parts = []
        if "asset_type" in params:
            query_parts.append(f"asset_type={params['asset_type']}")
        if "token_id" in params:
            query_parts.append(f"token_id={params['token_id']}")
        if "signature_type" in params:
            query_parts.append(f"signature_type={params['signature_type']}")
        
        path = "/balance-allowance/update"
        if query_parts:
            path += "?" + "&".join(query_parts)
        
        return self._make_request("GET", path)


# ========== Test Script ==========

if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("Polymarket API Client - Authentication Test (FIXED VERSION)")
    print("=" * 70)
    
    # Credentials from the problem statement
    API_KEY = "019c3ee6-4d56-73fc-a7a2-e5db22b94340"
    API_SECRET = "IZe8jb-on6PKYZYlG74Al-sTYeuEVPbFqH78e0f0xso="
    PASSPHRASE = "b4736af6a2ef790b2034e258da2e296de866c60b4afe9ab707d3697b5c28b51f"
    
    # You MUST provide your wallet address for L2 authentication
    WALLET_ADDRESS = os.getenv("POLY_WALLET_ADDRESS", "")
    
    if not WALLET_ADDRESS:
        print("\n⚠️  WARNING: POLY_WALLET_ADDRESS environment variable not set!")
        print("For L2 authentication, you need to provide your Polygon wallet address.")
        print("This is the address that was used when creating the API key.")
        print("\nSet it via:")
        print("  Windows: $env:POLY_WALLET_ADDRESS = '0x...'")
        print("  Linux/Mac: export POLY_WALLET_ADDRESS='0x...'")
        print("\nAttempting to test with empty address (will likely fail)...")
    else:
        print(f"\n✓ Using wallet address: {WALLET_ADDRESS}")
    
    # Initialize client
    client = PolymarketAPIClient(API_KEY, API_SECRET, PASSPHRASE, WALLET_ADDRESS)
    
    # Test 1: Get server time (public endpoint)
    print("\n" + "-" * 70)
    print("Test 1: Getting server time (public endpoint)...")
    print("-" * 70)
    try:
        server_time = client.get_server_time()
        print(f"✓ Server time: {server_time}")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 2: Get markets (public endpoint)
    print("\n" + "-" * 70)
    print("Test 2: Getting markets (public endpoint)...")
    print("-" * 70)
    try:
        markets = client.get_markets()
        data = markets.get('data', [])
        print(f"✓ Retrieved {len(data)} markets")
        if data:
            print(f"  Sample market: {data[0].get('question', 'N/A')[:50]}...")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 3: Get balance (L2 authenticated endpoint)
    print("\n" + "-" * 70)
    print("Test 3: Getting balance (L2 authenticated endpoint)...")
    print("-" * 70)
    try:
        balance = client.get_balance_allowance({
            "asset_type": "COLLATERAL",
            "signature_type": 1
        })
        print(f"✓ Balance response:")
        print(json.dumps(balance, indent=2))
    except Exception as e:
        print(f"✗ Failed: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your WALLET_ADDRESS is correct and matches the API key")
        print("   The wallet address must be the one used when creating the API key.")
        print("2. Ensure signature_type matches your wallet type:")
        print("   - 0 for EOA (MetaMask, etc.)")
        print("   - 1 for POLY_PROXY (Magic email login)")
        print("   - 2 for GNOSIS_SAFE")
        print("3. Check that your API credentials are correct and not expired")
    
    # Test 4: Get orders (L2 authenticated endpoint)
    print("\n" + "-" * 70)
    print("Test 4: Getting orders (L2 authenticated endpoint)...")
    print("-" * 70)
    try:
        orders = client.get_orders()
        print(f"✓ Retrieved {len(orders)} open orders")
        if orders:
            print(f"  First order: {orders[0].get('id', 'N/A')}")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 5: Get API keys (L2 authenticated endpoint)
    print("\n" + "-" * 70)
    print("Test 5: Getting API keys (L2 authenticated endpoint)...")
    print("-" * 70)
    try:
        keys = client.get_api_keys()
        print(f"✓ API keys response:")
        print(json.dumps(keys, indent=2))
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)
    
    # Summary
    print("\nSUMMARY:")
    if WALLET_ADDRESS:
        print("Wallet address is set. L2 authentication should work.")
        print("\nIf you're still getting 401 errors:")
        print("1. Double-check the wallet address matches your API key")
        print("2. Try different signature_type values (0, 1, or 2)")
        print("3. Verify API credentials haven't expired")
    else:
        print("⚠️  WALLET_ADDRESS is required for L2 authentication!")
        print("Please set the POLY_WALLET_ADDRESS environment variable.")
