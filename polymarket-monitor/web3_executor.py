"""
Polymarket Web3 Trade Execution Module
Handles order submission and tracking on Polymarket's CLOB via Polygon network
"""

import os
import time
import logging
from typing import Dict, Optional, Tuple, Literal
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.messages import encode_structured_data
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Network(Enum):
    """Supported networks"""
    MAINNET = "mainnet"
    TESTNET = "testnet"


class OrderSide(Enum):
    """Order side types"""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class OrderResult:
    """Result of an order submission"""
    success: bool
    order_id: Optional[str] = None
    tx_hash: Optional[str] = None
    error: Optional[str] = None
    gas_used: Optional[int] = None
    confirmation_block: Optional[int] = None


@dataclass
class NetworkConfig:
    """Network-specific configuration"""
    rpc_url: str
    chain_id: int
    ctf_exchange: str
    collateral_token: str
    clob_api: str


# Polymarket contract addresses and endpoints
NETWORK_CONFIGS = {
    Network.MAINNET: NetworkConfig(
        rpc_url=os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com"),
        chain_id=137,
        ctf_exchange="0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",  # CTF Exchange on Polygon
        collateral_token="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDC on Polygon
        clob_api="https://clob.polymarket.com"
    ),
    Network.TESTNET: NetworkConfig(
        rpc_url=os.getenv("AMOY_RPC_URL", "https://rpc-amoy.polygon.technology"),
        chain_id=80002,  # Polygon Amoy testnet
        ctf_exchange="0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",  # Update with testnet address
        collateral_token="0x9c4e1703476e875070ee25b56a58b008cfb8fa78",  # Mock USDC
        clob_api="https://clob-testnet.polymarket.com"
    )
}

# CTF Exchange ABI (minimal - key functions only)
CTF_EXCHANGE_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "withdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "getBalance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# ERC20 ABI (minimal)
ERC20_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]


class PolymarketExecutor:
    """
    Main executor class for Polymarket trading operations
    """
    
    def __init__(
        self,
        private_key: str,
        network: Network = Network.MAINNET,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize the executor
        
        Args:
            private_key: Private key for signing transactions (with or without 0x prefix)
            network: Network to use (mainnet or testnet)
            max_retries: Maximum number of retries for failed transactions
            retry_delay: Delay between retries in seconds
        """
        self.network = network
        self.config = NETWORK_CONFIGS[network]
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.config.rpc_url))
        
        # Add PoA middleware for Polygon
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Verify connection
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {network.value} network")
        
        logger.info(f"Connected to {network.value} network (Chain ID: {self.config.chain_id})")
        
        # Setup account
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        
        logger.info(f"Using account: {self.address}")
        
        # Initialize contracts
        self.ctf_exchange = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.config.ctf_exchange),
            abi=CTF_EXCHANGE_ABI
        )
        
        self.collateral = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.config.collateral_token),
            abi=ERC20_ABI
        )
        
    def get_balance(self) -> Dict[str, float]:
        """
        Get account balances
        
        Returns:
            Dict with MATIC and USDC balances
        """
        try:
            # Get MATIC balance
            matic_balance = self.w3.eth.get_balance(self.address)
            matic_balance = float(self.w3.from_wei(matic_balance, 'ether'))
            
            # Get USDC balance
            usdc_balance = self.collateral.functions.balanceOf(self.address).call()
            usdc_balance = float(usdc_balance) / 1e6  # USDC has 6 decimals
            
            return {
                "matic": matic_balance,
                "usdc": usdc_balance,
                "address": self.address
            }
        except Exception as e:
            logger.error(f"Error fetching balances: {e}")
            return {"matic": 0.0, "usdc": 0.0, "address": self.address}
    
    def _estimate_gas_price(self) -> int:
        """
        Estimate optimal gas price with buffer
        
        Returns:
            Gas price in Wei
        """
        try:
            base_fee = self.w3.eth.gas_price
            # Add 10% buffer for faster confirmation
            gas_price = int(base_fee * 1.1)
            logger.info(f"Estimated gas price: {self.w3.from_wei(gas_price, 'gwei')} Gwei")
            return gas_price
        except Exception as e:
            logger.error(f"Error estimating gas: {e}")
            # Fallback to 50 Gwei
            return self.w3.to_wei(50, 'gwei')
    
    def _send_transaction_with_retry(
        self,
        transaction: Dict,
        operation_name: str
    ) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Send transaction with automatic retry logic
        
        Args:
            transaction: Transaction dict
            operation_name: Name of operation for logging
            
        Returns:
            Tuple of (success, tx_hash, block_number)
        """
        for attempt in range(self.max_retries):
            try:
                # Get latest nonce
                nonce = self.w3.eth.get_transaction_count(self.address, 'pending')
                transaction['nonce'] = nonce
                
                # Estimate gas
                try:
                    gas_estimate = self.w3.eth.estimate_gas(transaction)
                    transaction['gas'] = int(gas_estimate * 1.2)  # 20% buffer
                except Exception as e:
                    logger.warning(f"Gas estimation failed: {e}, using default")
                    transaction['gas'] = 300000
                
                # Set gas price
                transaction['gasPrice'] = self._estimate_gas_price()
                
                # Sign transaction
                signed_txn = self.w3.eth.account.sign_transaction(
                    transaction,
                    private_key=self.account.key
                )
                
                # Send transaction
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                tx_hash_hex = tx_hash.hex()
                
                logger.info(f"{operation_name} transaction sent: {tx_hash_hex}")
                
                # Wait for confirmation
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                
                if receipt['status'] == 1:
                    logger.info(f"{operation_name} confirmed in block {receipt['blockNumber']}")
                    return True, tx_hash_hex, receipt['blockNumber']
                else:
                    logger.error(f"{operation_name} transaction failed")
                    return False, tx_hash_hex, None
                    
            except Exception as e:
                logger.error(f"{operation_name} attempt {attempt + 1}/{self.max_retries} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"{operation_name} failed after {self.max_retries} attempts")
                    return False, None, None
        
        return False, None, None
    
    def approve_collateral(self, amount: Optional[float] = None) -> bool:
        """
        Approve CTF Exchange to spend collateral (USDC)
        
        Args:
            amount: Amount to approve (None for unlimited)
            
        Returns:
            True if successful
        """
        try:
            if amount is None:
                # Unlimited approval
                approve_amount = 2**256 - 1
            else:
                approve_amount = int(amount * 1e6)  # Convert to USDC decimals
            
            # Check current allowance
            current_allowance = self.collateral.functions.allowance(
                self.address,
                self.config.ctf_exchange
            ).call()
            
            if current_allowance >= approve_amount:
                logger.info("Sufficient allowance already exists")
                return True
            
            # Build approval transaction
            transaction = self.collateral.functions.approve(
                self.config.ctf_exchange,
                approve_amount
            ).build_transaction({
                'from': self.address,
                'chainId': self.config.chain_id
            })
            
            success, tx_hash, _ = self._send_transaction_with_retry(
                transaction,
                "Approval"
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error approving collateral: {e}")
            return False
    
    def create_limit_order(
        self,
        token_id: str,
        side: OrderSide,
        price: float,
        size: float,
        expiration: Optional[int] = None
    ) -> OrderResult:
        """
        Create a limit order via Polymarket CLOB API
        
        Args:
            token_id: CTF token ID to trade
            side: BUY or SELL
            price: Price per share (0-1)
            size: Number of shares
            expiration: Order expiration timestamp (None for 30 days)
            
        Returns:
            OrderResult with order details
        """
        try:
            # Validate inputs
            if not 0 < price < 1:
                return OrderResult(
                    success=False,
                    error="Price must be between 0 and 1"
                )
            
            if size <= 0:
                return OrderResult(
                    success=False,
                    error="Size must be positive"
                )
            
            # Calculate expiration (default 30 days)
            if expiration is None:
                expiration = int(time.time()) + (30 * 24 * 60 * 60)
            
            # Build order payload
            order_payload = {
                "maker": self.address,
                "taker": "0x0000000000000000000000000000000000000000",
                "tokenId": token_id,
                "makerAmount": str(int(size * 1e6)),  # Convert to USDC decimals
                "takerAmount": str(int(size * price * 1e6)),
                "side": side.value,
                "feeRateBps": "0",
                "nonce": str(int(time.time() * 1000)),
                "signer": self.address,
                "expiration": str(expiration),
                "signatureType": 0  # EOA signature
            }
            
            # Create EIP-712 signature
            order_hash = self._create_order_signature(order_payload)
            order_payload["signature"] = order_hash
            
            # Submit order to CLOB API
            response = requests.post(
                f"{self.config.clob_api}/order",
                json=order_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Order created successfully: {result.get('orderID')}")
                
                return OrderResult(
                    success=True,
                    order_id=result.get('orderID'),
                    tx_hash=None,  # CLOB orders don't have immediate tx hash
                    gas_used=0
                )
            else:
                error_msg = f"CLOB API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return OrderResult(
                    success=False,
                    error=error_msg
                )
                
        except Exception as e:
            logger.error(f"Error creating limit order: {e}")
            return OrderResult(
                success=False,
                error=str(e)
            )
    
    def _create_order_signature(self, order: Dict) -> str:
        """
        Create EIP-712 signature for order
        
        Args:
            order: Order payload
            
        Returns:
            Signature hex string
        """
        # EIP-712 domain for Polymarket
        domain_data = {
            "name": "Polymarket CTF Exchange",
            "version": "1",
            "chainId": self.config.chain_id,
            "verifyingContract": self.config.ctf_exchange
        }
        
        # Order type structure
        message_types = {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"}
            ],
            "Order": [
                {"name": "maker", "type": "address"},
                {"name": "taker", "type": "address"},
                {"name": "tokenId", "type": "uint256"},
                {"name": "makerAmount", "type": "uint256"},
                {"name": "takerAmount", "type": "uint256"},
                {"name": "side", "type": "uint8"},
                {"name": "feeRateBps", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
                {"name": "signer", "type": "address"},
                {"name": "expiration", "type": "uint256"}
            ]
        }
        
        # Encode and sign
        structured_data = {
            "types": message_types,
            "primaryType": "Order",
            "domain": domain_data,
            "message": order
        }
        
        encoded_data = encode_structured_data(structured_data)
        signed_message = self.account.sign_message(encoded_data)
        
        return signed_message.signature.hex()
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """
        Get status of an order from CLOB API
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Order status dict or None
        """
        try:
            response = requests.get(
                f"{self.config.clob_api}/order/{order_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching order status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching order status: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> OrderResult:
        """
        Cancel an existing order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            OrderResult with cancellation details
        """
        try:
            payload = {
                "orderID": order_id,
                "signer": self.address
            }
            
            # Create signature for cancellation
            # (Simplified - actual implementation may vary)
            
            response = requests.delete(
                f"{self.config.clob_api}/order",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Order {order_id} cancelled successfully")
                return OrderResult(success=True, order_id=order_id)
            else:
                error_msg = f"Cancellation failed: {response.status_code}"
                logger.error(error_msg)
                return OrderResult(success=False, error=error_msg)
                
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return OrderResult(success=False, error=str(e))
    
    def get_market_orders(self, token_id: str) -> Optional[Dict]:
        """
        Get all orders for a specific market
        
        Args:
            token_id: Token ID to query
            
        Returns:
            Order book data or None
        """
        try:
            response = requests.get(
                f"{self.config.clob_api}/book",
                params={"token_id": token_id},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching market orders: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching market orders: {e}")
            return None


# Convenience functions
def create_executor(
    private_key: str,
    network: str = "mainnet",
    max_retries: int = 3
) -> PolymarketExecutor:
    """
    Create a PolymarketExecutor instance
    
    Args:
        private_key: Private key for signing
        network: "mainnet" or "testnet"
        max_retries: Max retry attempts
        
    Returns:
        PolymarketExecutor instance
    """
    net = Network.MAINNET if network.lower() == "mainnet" else Network.TESTNET
    return PolymarketExecutor(private_key, net, max_retries)


# Example usage
if __name__ == "__main__":
    # Example: Create executor and place order
    # NEVER commit real private keys!
    
    private_key = os.getenv("PRIVATE_KEY", "your_private_key_here")
    
    # Initialize executor
    executor = create_executor(private_key, network="mainnet")
    
    # Check balances
    balances = executor.get_balance()
    print(f"Balances: {balances}")
    
    # Approve collateral (one-time setup)
    # executor.approve_collateral()
    
    # Place a limit order
    # result = executor.create_limit_order(
    #     token_id="123456789",
    #     side=OrderSide.BUY,
    #     price=0.55,
    #     size=10.0
    # )
    # 
    # if result.success:
    #     print(f"Order placed! ID: {result.order_id}")
    #     
    #     # Check order status
    #     status = executor.get_order_status(result.order_id)
    #     print(f"Order status: {status}")
    # else:
    #     print(f"Order failed: {result.error}")
