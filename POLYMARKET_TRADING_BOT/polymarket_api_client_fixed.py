"""
Polymarket API Client - FIXED VERSION v2
Corrected headers: POLY_* not POLYMARKET_*
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


class PolymarketAPIClient:
    """
    Fixed API client for Polymarket CLOB API
    """
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str, wallet_address: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.wallet_address = wallet_address.lower() if wallet_address else ""
        self.base_url = "https://clob.polymarket.com"
        
    def _build_signature(self, timestamp: str, method: str, path: str, body: str = None) -> str:
        """
        Build HMAC signature with correct base64 handling
        """
        # Decode base64url secret
        try:
            secret_bytes = base64.urlsafe_b64decode(self.api_secret)
        except Exception:
            padded = self.api_secret + '=' * (4 - len(self.api_secret) % 4)
            secret_bytes = base64.urlsafe_b64decode(padded)
        
        # Build message
        message = str(timestamp) + str(method) + str(path)
        if body:
            # Replace single quotes with double quotes
            message += str(body).replace("'", '"')
        
        # Create HMAC
        h = hmac.new(secret_bytes, message.encode('utf-8'), hashlib.sha256)
        
        # Return base64url encoded signature
        return base64.urlsafe_b64encode(h.digest()).decode('utf-8')
    
    def _get_headers(self, method: str, path: str, body: Any = None) -> Dict[str, str]:
        """
        Create correct L2 authentication headers
        KEY FIX: Use POLY_* not POLYMARKET_*
        """
        timestamp = str(int(time.time()))
        
        # Serialize body
        body_str = None
        if body is not None:
            if isinstance(body, dict):
                body_str = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
            else:
                body_str = str(body)
        
        # Generate signature
        signature = self._build_signature(timestamp, method, path, body_str)
        
        # CORRECT header names (POLY_* not POLYMARKET_*)
        headers = {
            "POLY_ADDRESS": self.wallet_address,
            "POLY_SIGNATURE": signature,
            "POLY_TIMESTAMP": timestamp,
            "POLY_API_KEY": self.api_key,
            "POLY_PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": "polymarket-python-client"
        }
        return headers
    
    def _make_request(self, method: str, path: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated API request"""
        url = urljoin(self.base_url, path)
        headers = self._get_headers(method, path, body)
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=body, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text[:500]}")
            raise
    
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        return self._make_request("GET", "/balance-allowance")
    
    def get_markets(self) -> Dict[str, Any]:
        """Get markets"""
        return self._make_request("GET", "/markets")
    
    def place_order(self, token_id: str, side: str, price: float, size: float) -> Dict[str, Any]:
        """Place order"""
        body = {
            "tokenId": token_id,
            "side": side,
            "price": price,
            "size": size
        }
        return self._make_request("POST", "/order", body)
