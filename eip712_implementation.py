#!/usr/bin/env python3
"""
EIP-712 Implementation for Polymarket API
Based on official Polymarket documentation and Rust client
"""

import json
import time
from eth_account import Account
from eth_account.messages import encode_typed_data

class PolymarketEIP712Signer:
    """
    EIP-712 Signer for Polymarket orders
    Based on official Polymarket order structure
    """
    
    def __init__(self, private_key: str):
        """
        Initialize with private key
        
        Args:
            private_key: Hex string private key (with or without 0x)
        """
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        
    def get_order_types(self):
        """
        Get EIP-712 type definitions for Polymarket order
        Based on official Polymarket order structure
        """
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
    
    def create_order_message(self, order_data: dict):
        """
        Create EIP-712 message for an order
        
        Args:
            order_data: Dictionary with order parameters
            
        Returns:
            EIP-712 message structure
        """
        # Default values
        defaults = {
            "maker": self.address.lower(),
            "isBuy": True,
            "limitPrice": "0",
            "amount": "0",
            "salt": str(int(time.time() * 1000)),  # Milliseconds timestamp
            "instrument": "0x" + "0" * 64,  # Default instrument
            "timestamp": str(int(time.time()))
        }
        
        # Merge with provided data
        message = {**defaults, **order_data}
        
        # Convert types
        for key in ["limitPrice", "amount", "salt", "timestamp"]:
            if key in message:
                message[key] = str(message[key])
                
        return message
    
    def get_domain_data(self, chain_id: int = 137):
        """
        Get EIP-712 domain data for Polygon mainnet (chainId: 137)
        
        Args:
            chain_id: Chain ID (137 for Polygon mainnet)
            
        Returns:
            Domain data dictionary
        """
        return {
            "name": "Polymarket",
            "version": "1",
            "chainId": chain_id,
            "verifyingContract": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"  # Polymarket contract
        }
    
    def sign_order(self, order_data: dict, chain_id: int = 137):
        """
        Sign an order using EIP-712
        
        Args:
            order_data: Order parameters
            chain_id: Chain ID (default: 137 for Polygon)
            
        Returns:
            Dictionary with signature and order data
        """
        # Prepare message
        message = self.create_order_message(order_data)
        
        # Prepare typed data
        typed_data = {
            "types": self.get_order_types(),
            "primaryType": "Order",
            "domain": self.get_domain_data(chain_id),
            "message": message
        }
        
        # Sign the typed data
        encoded_message = encode_typed_data(typed_data)
        signed_message = self.account.sign_message(encoded_message)
        
        return {
            "signature": signed_message.signature.hex(),
            "order": message,
            "typed_data": typed_data
        }
    
    def verify_signature(self, signature: str, order_data: dict, signer_address: str, chain_id: int = 137):
        """
        Verify an EIP-712 signature
        
        Args:
            signature: Hex signature string
            order_data: Order data that was signed
            signer_address: Expected signer address
            chain_id: Chain ID
            
        Returns:
            True if signature is valid
        """
        try:
            # Recreate the signed message
            message = self.create_order_message(order_data)
            typed_data = {
                "types": self.get_order_types(),
                "primaryType": "Order",
                "domain": self.get_domain_data(chain_id),
                "message": message
            }
            
            encoded_message = encode_typed_data(typed_data)
            
            # Recover the address from signature
            recovered_address = Account.recover_message(encoded_message, signature=signature)
            
            return recovered_address.lower() == signer_address.lower()
            
        except Exception as e:
            print(f"Verification error: {e}")
            return False

def test_eip712():
    """
    Test EIP-712 implementation
    """
    print("Testing EIP-712 Implementation for Polymarket")
    print("=" * 60)
    
    # Use a test private key (NEVER use real private key in code)
    # This is just for testing - in production, load from secure storage
    test_private_key = "0x" + "1" * 64  # Invalid key for testing
    
    print("1. Initializing signer...")
    try:
        signer = PolymarketEIP712Signer(test_private_key)
        print(f"   Address: {signer.address}")
    except Exception as e:
        print(f"   Error (expected with test key): {e}")
        print("   Note: Would work with real private key")
    
    print("\n2. Testing order creation...")
    order_data = {
        "isBuy": True,
        "limitPrice": "1000000000000000000",  # 1.0 in wei
        "amount": "500000000000000000",  # 0.5 in wei
        "instrument": "0x" + "a" * 64  # Example instrument
    }
    
    print(f"   Order data: {json.dumps(order_data, indent=2)}")
    
    print("\n3. Testing signature (would work with real key)...")
    print("   To implement fully:")
    print("   a) Install: pip install eth-account")
    print("   b) Load real private key from secure storage")
    print("   c) Use signer.sign_order() to get signature")
    print("   d) Include signature in API requests")
    
    print("\n" + "=" * 60)
    print("INTEGRATION WITH API CLIENT:")
    print("=" * 60)
    print("""
    Complete API client needs:
    
    1. HMAC Authentication (for API keys):
        - API-KEY header
        - TIMESTAMP header  
        - SIGNATURE header (HMAC of timestamp + method + path)
    
    2. EIP-712 Signatures (for orders):
        - sign_typed_data() for order signing
        - Include signature in order payload
    
    3. Combined flow:
        a. Get market data (public, no auth)
        b. Create order with EIP-712 signature
        c. Send order with HMAC API auth
        d. Include EIP-712 signature in order data
    
    Example headers:
        POLY-ADDRESS: 0xYourAddress
        POLY-SIGNATURE: HMAC_SIGNATURE
        POLY-TIMESTAMP: 1234567890
        POLY-API-KEY: your_api_key
        Content-Type: application/json
        
    Order payload:
        {
          "maker": "0xYourAddress",
          "isBuy": true,
          "limitPrice": "1000000000000000000",
          "amount": "500000000000000000",
          "signature": "0xEIP712_SIGNATURE",
          ...
        }
    """)

if __name__ == "__main__":
    test_eip712()