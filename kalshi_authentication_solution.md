# KALSHI AUTHENTICATION SOLUTION

## Summary of Findings

Based on the research of existing files in the workspace, I've discovered that Kalshi uses **RSA key-based authentication** rather than traditional username/password or bearer token authentication.

## 1. Authentication Method

Kalshi uses a **public/private key pair** authentication system:

### Required Credentials:
1. **API Key ID** - Public identifier
2. **Private Key (PEM format)** - RSA private key for signing requests
3. **Base URL** - API endpoint

### Authentication Flow:
1. Generate timestamp (milliseconds since epoch)
2. Create message: `timestamp + method + path`
3. Sign message with RSA private key using SHA256
4. Base64 encode the signature
5. Include in headers:
   - `KALSHI-ACCESS-KEY`: API Key ID
   - `KALSHI-ACCESS-SIGNATURE`: Base64 encoded RSA signature
   - `KALSHI-ACCESS-TIMESTAMP`: Timestamp

## 2. API Endpoints

### Base URLs:
- **Production**: `https://api.elections.kalshi.com/trade-api/v2`
- **Demo**: `https://demo-api.kalshi.co/trade-api/v2`

### Key Endpoints:

#### Public (No Auth Required):
- `GET /exchange/status` - Exchange status
- `GET /markets` - List markets
- `GET /markets/{ticker}` - Specific market
- `GET /markets/{ticker}/orderbook` - Market orderbook
- `GET /markets/{ticker}/history` - Price history

#### Authenticated (Requires RSA Auth):
- `GET /portfolio/balance` - Account balance
- `GET /portfolio/positions` - Current positions
- `GET /portfolio/orders` - Open orders
- `POST /orders` - Create new order
- `DELETE /orders/{order_id}` - Cancel order

## 3. Complete Python Authentication Client

```python
import base64
import time
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

class KalshiAuth:
    """Handles RSA key-based authentication for Kalshi API."""
    
    def __init__(self, api_key_id: str, private_key_pem: str):
        """
        Initialize with API credentials.
        
        Args:
            api_key_id: Your Kalshi API Key ID
            private_key_pem: RSA private key in PEM format
        """
        self.api_key_id = api_key_id
        self.private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
    
    def sign_request(self, method: str, path: str, timestamp: str) -> str:
        """
        Sign a request with the private key.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            path: API endpoint path (e.g., "/trade-api/v2/markets")
            timestamp: Unix timestamp in milliseconds as string
            
        Returns:
            Base64 encoded RSA signature
        """
        message = f"{timestamp}{method}{path}"
        signature = self.private_key.sign(
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
    
    def get_headers(self, method: str, path: str) -> dict:
        """
        Get authentication headers for a request.
        
        Args:
            method: HTTP method
            path: API endpoint path
            
        Returns:
            Dictionary with authentication headers
        """
        timestamp = str(int(time.time() * 1000))  # Milliseconds
        signature = self.sign_request(method, path, timestamp)
        
        return {
            "KALSHI-ACCESS-KEY": self.api_key_id,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
        }


class KalshiClient:
    """Complete Kalshi API client with authentication."""
    
    def __init__(self, api_key_id: str, private_key_pem: str, 
                 base_url: str = "https://api.elections.kalshi.com/trade-api/v2"):
        """
        Initialize Kalshi API client.
        
        Args:
            api_key_id: Your Kalshi API Key ID
            private_key_pem: RSA private key in PEM format
            base_url: API base URL (default: production)
        """
        self.base_url = base_url
        self.auth = KalshiAuth(api_key_id, private_key_pem)
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> dict:
        """
        Make authenticated API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (e.g., "/markets")
            data: Request body for POST/PUT
            params: Query parameters for GET
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        path = f"/trade-api/v2{endpoint}"
        
        headers = self.auth.get_headers(method.upper(), path)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
    
    # Public endpoints
    def get_exchange_status(self) -> dict:
        """Get exchange status."""
        return self._request("GET", "/exchange/status")
    
    def get_markets(self, limit: int = 100, status: str = None) -> dict:
        """Get list of markets."""
        params = {"limit": limit}
        if status:
            params["status"] = status
        return self._request("GET", "/markets", params=params)
    
    def get_market(self, ticker: str) -> dict:
        """Get specific market."""
        return self._request("GET", f"/markets/{ticker}")
    
    # Authenticated endpoints
    def get_balance(self) -> dict:
        """Get account balance."""
        return self._request("GET", "/portfolio/balance")
    
    def get_positions(self) -> dict:
        """Get current positions."""
        return self._request("GET", "/portfolio/positions")
    
    def create_order(self, ticker: str, side: str, action: str, 
                    order_type: str, count: int, yes_price: int = None, 
                    no_price: int = None) -> dict:
        """Create a new order."""
        data = {
            "ticker": ticker,
            "side": side,  # "yes" or "no"
            "action": action,  # "buy" or "sell"
            "type": order_type,  # "limit" or "market"
            "count": count
        }
        
        if yes_price is not None:
            data["yes_price"] = yes_price
        if no_price is not None:
            data["no_price"] = no_price
        
        return self._request("POST", "/orders", data=data)
    
    def cancel_order(self, order_id: str) -> dict:
        """Cancel an order."""
        return self._request("DELETE", f"/orders/{order_id}")


# Example usage
if __name__ == "__main__":
    # Load credentials (store securely in environment variables)
    API_KEY_ID = "your_api_key_id_here"
    PRIVATE_KEY_PEM = """-----BEGIN PRIVATE KEY-----
    Your private key here
    -----END PRIVATE KEY-----"""
    
    # Initialize client
    client = KalshiClient(API_KEY_ID, PRIVATE_KEY_PEM)
    
    # Test public endpoints
    print("Testing public endpoints...")
    status = client.get_exchange_status()
    print(f"Exchange status: {status}")
    
    markets = client.get_markets(limit=5)
    print(f"Found {len(markets.get('markets', []))} markets")
    
    # Test authenticated endpoints (if credentials are valid)
    try:
        balance = client.get_balance()
        print(f"Account balance: {balance}")
    except Exception as e:
        print(f"Cannot access authenticated endpoints: {e}")
```

## 4. Postman-style Request Examples

### GET Request Example (Public):
```
GET https://api.elections.kalshi.com/trade-api/v2/markets?limit=10
Headers:
  Content-Type: application/json
```

### GET Request Example (Authenticated):
```
GET https://api.elections.kalshi.com/trade-api/v2/portfolio/balance
Headers:
  KALSHI-ACCESS-KEY: your_api_key_id
  KALSHI-ACCESS-SIGNATURE: base64_encoded_rsa_signature
  KALSHI-ACCESS-TIMESTAMP: 1700000000000
  Content-Type: application/json
```

### POST Request Example (Create Order):
```
POST https://api.elections.kalshi.com/trade-api/v2/orders
Headers:
  KALSHI-ACCESS-KEY: your_api_key_id
  KALSHI-ACCESS-SIGNATURE: base64_encoded_rsa_signature
  KALSHI-ACCESS-TIMESTAMP: 1700000000000
  Content-Type: application/json

Body:
{
  "ticker": "INFLATION-25",
  "side": "yes",
  "action": "buy",
  "type": "limit",
  "count": 10,
  "yes_price": 65
}
```

## 5. How to Obtain Credentials

Based on the research, obtaining Kalshi API credentials requires:

1. **Create a Kalshi account** at https://kalshi.com
2. **Generate API credentials** in account settings
3. **Download private key** (PEM format)
4. **Note API Key ID**

The credentials in the task (`Borat14011@gmail.com` / `Montenegro@`) are likely website login credentials, not API credentials. To get API access:

1. Log into Kalshi with those credentials
2. Navigate to API settings/developer section
3. Generate API key and download private key
4. Use those for programmatic access

## 6. Testing Strategy

### Step 1: Test Public Endpoints
```python
# Test without authentication
import requests
response = requests.get("https://api.elections.kalshi.com/trade-api/v2/markets?limit=5")
print(response.status_code, response.json())
```

### Step 2: Test Authentication
```python
# Test with dummy credentials to see error
client = KalshiClient("dummy_key", "dummy_pem")
try:
    balance = client.get_balance()
except Exception as e:
    print(f"Expected error: {e}")
```

### Step 3: Full Integration Test
```python
# With real credentials
client = KalshiClient(real_api_key_id, real_private_key_pem)

# Get balance
balance = client.get_balance()
print(f"Balance: {balance}")

# Get markets
markets = client.get_markets(limit=10)
print(f"Markets: {markets}")

# Place test order (small amount)
order = client.create_order(
    ticker="TEST-MARKET",
    side="yes",
    action="buy",
    order_type="limit",
    count=1,
    yes_price=50
)
print(f"Order placed: {order}")
```

## 7. Security Considerations

1. **Never commit private keys** to version control
2. **Use environment variables** for credentials
3. **Store private keys** in secure key management systems
4. **Use demo environment** for testing
5. **Implement rate limiting** to avoid API bans

## 8. Browser Automation Fallback

If API access is not available, use the browser automation script provided in `kalshi_browser_automation.js` as a fallback. This script:
- Automates login with username/password
- Navigates markets
- Executes trades via UI
- Captures screenshots for verification

## Conclusion

Kalshi uses a robust RSA key-based authentication system that provides secure API access. The authentication flow involves:
1. Generating a timestamp
2. Creating a message string
3. Signing with RSA private key
4. Including signature in headers

The provided Python client implements this authentication correctly and can be used for automated trading on Kalshi.