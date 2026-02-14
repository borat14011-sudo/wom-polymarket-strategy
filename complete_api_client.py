#!/usr/bin/env python3
"""
Complete Polymarket API Client with HMAC + EIP-712 Authentication
Based on official documentation and working implementations
"""

import os
import json
import time
import hmac
import hashlib
import base64
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urljoin

# Try to import EIP-712 signer (optional)
try:
    from eth_account import Account
    from eth_account.messages import encode_typed_data
    EIP712_AVAILABLE = True
except ImportError:
    EIP712_AVAILABLE = False
    print("Note: eth-account not installed. EIP-712 signing disabled.")
    print("Install: pip install eth-account")

class PolymarketCompleteClient:
    """
    Complete Polymarket API Client with proper authentication
    
    Authentication layers:
    1. Level 1: API Key + HMAC signature (for API access)
    2. Level 2: EIP-712 signatures (for order signing)
    """
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str, 
                 wallet_address: str, private_key: Optional[str] = None):
        """
        Initialize client with credentials
        
        Args:
            api_key: Polymarket API key
            api_secret: Base64url encoded API secret
            passphrase: API passphrase
            wallet_address: Polygon wallet address (0x...)
            private_key: Optional private key for EIP-712 signing
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.wallet_address = wallet_address.lower()
        self.private_key = private_key
        
        # Base URLs
        self.clob_base_url = "https://clob.polymarket.com"
        self.gamma_base_url = "https://gamma-api.polymarket.com"
        
        # Initialize EIP-712 signer if private key provided
        self.signer = None
        if private_key and EIP712_AVAILABLE:
            try:
                self.signer = Account.from_key(private_key)
                print(f"EIP-712 signer initialized for {self.signer.address}")
            except Exception as e:
                print(f"Warning: Could not initialize EIP-712 signer: {e}")
    
    # ===== HMAC AUTHENTICATION =====
    
    def _build_hmac_signature(self, timestamp: int, method: str, path: str, body: Any = None) -> str:
        """
        Build HMAC signature for API authentication
        
        Args:
            timestamp: Unix timestamp
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            body: Request body (optional)
            
        Returns:
            Base64url encoded HMAC signature
        """
        # Decode base64url secret
        secret_clean = self.api_secret.replace('-', '+').replace('_', '/')
        padding = 4 - len(secret_clean) % 4
        if padding != 4:
            secret_clean += '=' * padding
        
        secret_bytes = base64.b64decode(secret_clean)
        
        # Build message
        message = str(timestamp) + method.upper() + path
        if body is not None:
            # Ensure consistent JSON serialization
            if isinstance(body, dict):
                message += json.dumps(body, separators=(',', ':'))
            else:
                message += str(body)
        
        # Create HMAC-SHA256
        signature = hmac.new(
            secret_bytes,
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Return URL-safe base64
        return base64.urlsafe_b64encode(signature).decode('utf-8')
    
    def _get_auth_headers(self, method: str, path: str, body: Any = None) -> Dict[str, str]:
        """
        Get authentication headers for API request
        
        Returns:
            Dictionary of headers
        """
        timestamp = int(datetime.now().timestamp())
        signature = self._build_hmac_signature(timestamp, method, path, body)
        
        return {
            "POLY-ADDRESS": self.wallet_address,
            "POLY-SIGNATURE": signature,
            "POLY-TIMESTAMP": str(timestamp),
            "POLY-API-KEY": self.api_key,
            "POLY-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }
    
    # ===== EIP-712 ORDER SIGNING =====
    
    def _get_order_types(self):
        """Get EIP-712 type definitions for Polymarket order"""
        return {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"}
            ],
            "Order": [
                {"name": "maker", "type": "address"},
                {"name": "isBuy", "type": "bool"},
                {"name": "limitPrice", "type": "uint256"},
                {"name": "amount", "type": "uint256"},
                {"name": "salt", "type": "uint256"},
                {"name": "instrument", "type": "bytes32"},
                {"name": "timestamp", "type": "uint256"}
            ]
        }
    
    def _get_domain_data(self, chain_id: int = 137):
        """Get EIP-712 domain data for Polygon"""
        return {
            "name": "Polymarket",
            "version": "1",
            "chainId": chain_id,
            "verifyingContract": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"  # Polymarket contract
        }
    
    def sign_order_eip712(self, order_data: dict, chain_id: int = 137) -> Optional[Dict]:
        """
        Sign an order using EIP-712
        
        Args:
            order_data: Order parameters
            chain_id: Chain ID (137 for Polygon)
            
        Returns:
            Dictionary with signature and order, or None if failed
        """
        if not self.signer or not EIP712_AVAILABLE:
            print("Error: EIP-712 signing not available")
            print("Install: pip install eth-account")
            return None
        
        try:
            # Prepare message with defaults
            defaults = {
                "maker": self.wallet_address,
                "isBuy": True,
                "limitPrice": "0",
                "amount": "0",
                "salt": str(int(time.time() * 1000)),
                "instrument": "0x" + "0" * 64,
                "timestamp": str(int(time.time()))
            }
            
            message = {**defaults, **order_data}
            
            # Ensure string values
            for key in ["limitPrice", "amount", "salt", "timestamp"]:
                if key in message:
                    message[key] = str(message[key])
            
            # Create typed data
            typed_data = {
                "types": self._get_order_types(),
                "primaryType": "Order",
                "domain": self._get_domain_data(chain_id),
                "message": message
            }
            
            # Sign
            encoded_message = encode_typed_data(typed_data)
            signed = self.signer.sign_message(encoded_message)
            
            return {
                "signature": signed.signature.hex(),
                "order": message,
                "typed_data": typed_data
            }
            
        except Exception as e:
            print(f"EIP-712 signing error: {e}")
            return None
    
    # ===== API METHODS =====
    
    def request(self, method: str, endpoint: str, data: Any = None, 
                use_auth: bool = True, base_url: str = None) -> Dict:
        """
        Make API request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            use_auth: Use authentication headers
            base_url: Base URL (defaults to CLOB)
            
        Returns:
            Response JSON
        """
        if base_url is None:
            base_url = self.clob_base_url
        
        url = urljoin(base_url, endpoint)
        
        headers = {}
        if use_auth:
            headers = self._get_auth_headers(method, endpoint, data)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                timeout=30
            )
            
            # Check for Cloudflare errors
            if response.status_code == 403:
                print("Warning: 403 Forbidden - Cloudflare protection")
                if 'cf-ray' in response.headers:
                    print(f"Cloudflare Ray ID: {response.headers['cf-ray']}")
            
            response.raise_for_status()
            
            if response.text:
                return response.json()
            else:
                return {"status": "success", "message": "No content"}
                
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response: {response.text[:500] if response.text else 'No response'}")
            raise
        except Exception as e:
            print(f"Request error: {e}")
            raise
    
    # ===== PUBLIC ENDPOINTS =====
    
    def get_markets(self, limit: int = 100) -> Dict:
        """Get list of markets (public)"""
        return self.request("GET", f"/markets?limit={limit}", use_auth=False)
    
    def get_market(self, market_id: str) -> Dict:
        """Get specific market details (public)"""
        return self.request("GET", f"/markets/{market_id}", use_auth=False)
    
    def get_order_book(self, market_id: str) -> Dict:
        """Get order book for market (public)"""
        return self.request("GET", f"/orderbook/{market_id}", use_auth=False)
    
    # ===== AUTHENTICATED ENDPOINTS =====
    
    def get_balance(self) -> Dict:
        """Get user balance (authenticated)"""
        return self.request("GET", "/balances")
    
    def get_orders(self, status: str = "open") -> Dict:
        """Get user orders (authenticated)"""
        return self.request("GET", f"/orders?status={status}")
    
    def place_order(self, order_data: Dict) -> Dict:
        """
        Place a new order (authenticated + EIP-712 signed)
        
        Args:
            order_data: Order parameters including EIP-712 signature
            
        Returns:
            Order response
        """
        # If order doesn't have signature, try to sign it
        if "signature" not in order_data and self.signer:
            signed = self.sign_order_eip712(order_data)
            if signed:
                order_data["signature"] = signed["signature"]
                # Merge signed order data
                order_data.update(signed["order"])
        
        return self.request("POST", "/orders", order_data)
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order (authenticated)"""
        return self.request("DELETE", f"/orders/{order_id}")

def test_client():
    """Test the complete API client"""
    print("Testing Complete Polymarket API Client")
    print("=" * 60)
    
    # Load credentials from environment
    load_dotenv = False
    try:
        from dotenv import load_dotenv as load_env
        load_env('POLYMARKET_TRADING_BOT/.env.api')
        load_dotenv = True
    except ImportError:
        print("Note: python-dotenv not installed")
    
    if load_dotenv:
        api_key = os.getenv('POLYMARKET_API_KEY')
        api_secret = os.getenv('POLYMARKET_API_SECRET')
        passphrase = os.getenv('POLYMARKET_PASSPHRASE')
        wallet_address = os.getenv('POLYMARKET_WALLET_ADDRESS')
        private_key = os.getenv('POLYMARKET_PRIVATE_KEY')  # Never store in plain text!
    else:
        # Use dummy values for testing
        api_key = "test_key"
        api_secret = "test_secret"
        passphrase = "test_passphrase"
        wallet_address = "0x" + "0" * 40
        private_key = None
    
    print("1. Initializing client...")
    client = PolymarketCompleteClient(
        api_key=api_key,
        api_secret=api_secret,
        passphrase=passphrase,
        wallet_address=wallet_address,
        private_key=private_key
    )
    
    print(f"   Wallet: {client.wallet_address}")
    print(f"   EIP-712: {'Available' if client.signer else 'Not available'}")
    
    print("\n2. Testing public endpoints...")
    try:
        markets = client.get_markets(limit=5)
        print(f"   Got {len(markets.get('markets', []))} markets")
    except Exception as e:
        print(f"   Error (may be expected): {e}")
    
    print("\n3. Testing authenticated endpoints...")
    print("   Note: Will fail without valid credentials")
    
    print("\n" + "=" * 60)
    print("SETUP INSTRUCTIONS:")
    print("=" * 60)
    print("""
    1. Install dependencies:
        pip install requests eth-account python-dotenv
    
    2. Create .env.api with:
        POLYMARKET_API_KEY=your_api_key
        POLYMARKET_API_SECRET=your_base64url_secret
        POLYMARKET_PASSPHRASE=your_passphrase
        POLYMARKET_WALLET_ADDRESS=0xYourAddress
        # Optional for EIP-712:
        POLYMARKET_PRIVATE_KEY=0xYourPrivateKey
    
    3. Get API credentials from Polymarket:
        - Go to Polymarket website
        - Account → API Keys
        - Generate new API key
    
    4. Test with:
        client = PolymarketCompleteClient(...)
        markets = client.get_markets()
        print(markets)
    """)
    
    print("\nTROUBLESHOOTING:")
    print("-" * 40)
    print("403 Forbidden: Cloudflare protection")
    print("   Solution: Use real browser first to establish session")
    print("401 Unauthorized: Invalid HMAC signature")
    print("   Solution: Check timestamp sync and secret encoding")
    print("EIP-712 errors: Invalid order structure")
    print("   Solution: Check official order schema")

if __name__ == "__main__":
    test_client()