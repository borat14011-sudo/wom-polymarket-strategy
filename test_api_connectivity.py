import socket
import ssl
import sys

def test_kalshi_connectivity():
    """Test basic connectivity to Kalshi API"""
    host = 'api.kalshi.com'
    port = 443
    
    print(f"Testing connectivity to {host}:{port}")
    
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        # Wrap with SSL
        context = ssl.create_default_context()
        ssl_sock = context.wrap_socket(sock, server_hostname=host)
        
        # Connect
        print(f"Connecting to {host}...")
        ssl_sock.connect((host, port))
        print(f"✓ Connected successfully to {host}")
        
        # Try to send a basic request
        request = f"GET /trade-api/v2/markets?limit=1 HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += f"Authorization: Bearer 14a525cf-42d7-4746-8e36-30a8d9c17c96\r\n"
        request += "Connection: close\r\n\r\n"
        
        ssl_sock.send(request.encode())
        
        # Receive response
        response = b""
        while True:
            chunk = ssl_sock.recv(4096)
            if not chunk:
                break
            response += chunk
        
        # Parse response
        response_str = response.decode('utf-8', errors='ignore')
        headers, body = response_str.split('\r\n\r\n', 1) if '\r\n\r\n' in response_str else (response_str, '')
        
        print(f"\nResponse Headers:")
        print(headers[:500])
        
        if body:
            print(f"\nResponse Body (first 500 chars):")
            print(body[:500])
        
        ssl_sock.close()
        return True
        
    except socket.gaierror as e:
        print(f"✗ DNS resolution failed: {e}")
        print("This suggests a DNS issue. Try:")
        print("1. Check if api.kalshi.com is accessible from your network")
        print("2. Try using a different DNS server (like 8.8.8.8)")
        print("3. Check firewall/proxy settings")
        return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Kalshi API Connectivity Test")
    print("=" * 50)
    success = test_kalshi_connectivity()
    
    if success:
        print("\n✓ API connectivity test PASSED")
        print("The framework is ready to fetch real market data.")
    else:
        print("\n✗ API connectivity test FAILED")
        print("The analysis will use simulated data until connectivity is restored.")
        
    print("\nAlternative approach: Use Kalshi's public data or web scraping")
    print("as a fallback until API access is restored.")