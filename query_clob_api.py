"""
Polymarket CLOB API Historical Data Query
Attempts to retrieve historical price/trade data from Polymarket's APIs
"""

import requests
import json
import time
from datetime import datetime, timedelta
import csv

class PolymarketHistoricalAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Known Polymarket API endpoints
        self.gamma_api = "https://gamma-api.polymarket.com"
        self.clob_api = "https://clob.polymarket.com"
        self.data_api = "https://data-api.polymarket.com"
        
    def test_endpoints(self):
        """Test which API endpoints are available and what they return"""
        print("🧪 Testing Polymarket API endpoints...\n")
        
        test_market_id = "0x1234567890abcdef"  # Placeholder
        
        endpoints = [
            f"{self.gamma_api}/markets/{test_market_id}",
            f"{self.gamma_api}/markets/{test_market_id}/history",
            f"{self.gamma_api}/prices/{test_market_id}",
            f"{self.clob_api}/markets/{test_market_id}",
            f"{self.clob_api}/prices/{test_market_id}",
            f"{self.clob_api}/book",
            f"{self.data_api}/markets/{test_market_id}",
        ]
        
        for endpoint in endpoints:
            try:
                print(f"Testing: {endpoint}")
                response = self.session.get(endpoint, timeout=10)
                print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"  ✅ Success! Data available")
                    try:
                        data = response.json()
                        print(f"  Keys: {list(data.keys())[:5]}")
                    except:
                        print(f"  Response length: {len(response.text)}")
                else:
                    print(f"  ❌ Failed or not available")
            except Exception as e:
                print(f"  ❌ Error: {e}")
            print()
    
    def get_market_history(self, market_id, start_date=None, end_date=None):
        """
        Try to get historical data for a market
        
        Args:
            market_id: Market condition ID
            start_date: Start datetime (optional)
            end_date: End datetime (optional)
            
        Returns:
            List of price history records or None
        """
        print(f"🔍 Querying historical data for market: {market_id}")
        
        # Try Gamma API first (most likely to have market data)
        try:
            url = f"{self.gamma_api}/markets/{market_id}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                market_data = response.json()
                print(f"  ✅ Got market data from Gamma API")
                
                # Check if there's historical price data
                # This structure is hypothetical and needs to be verified
                if 'priceHistory' in market_data:
                    return market_data['priceHistory']
                elif 'history' in market_data:
                    return market_data['history']
                else:
                    print(f"  ⚠️ No 'priceHistory' field in response")
                    print(f"  Available fields: {list(market_data.keys())}")
            else:
                print(f"  ❌ Gamma API returned {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error querying Gamma API: {e}")
        
        # Try CLOB API
        try:
            # Try getting book snapshots or trades
            url = f"{self.clob_api}/book"
            params = {
                'token_id': market_id,
                # Add time range if API supports it
            }
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                print(f"  ✅ Got data from CLOB API")
                return response.json()
        except Exception as e:
            print(f"  ❌ Error querying CLOB API: {e}")
        
        print(f"  ⚠️ No historical data found via API")
        return None
    
    def get_trade_history(self, token_id, limit=1000):
        """
        Try to get trade history for a market token
        
        This could provide actual transaction timestamps and prices
        """
        print(f"📊 Querying trade history for token: {token_id}")
        
        # Polymarket uses CLOB (Central Limit Order Book)
        # Trades might be available through a trades endpoint
        
        endpoints_to_try = [
            f"{self.clob_api}/trades",
            f"{self.clob_api}/markets/{token_id}/trades",
            f"{self.gamma_api}/trades",
        ]
        
        for endpoint in endpoints_to_try:
            try:
                params = {
                    'market': token_id,
                    'limit': limit
                }
                response = self.session.get(endpoint, params=params, timeout=30)
                
                if response.status_code == 200:
                    trades = response.json()
                    print(f"  ✅ Got {len(trades)} trades from {endpoint}")
                    return trades
            except Exception as e:
                continue
        
        print(f"  ⚠️ No trade history found")
        return None
    
    def construct_price_history_from_trades(self, trades):
        """
        Construct hourly price averages from individual trades
        
        Args:
            trades: List of trade objects
            
        Returns:
            List of {timestamp, yes_price, volume} records
        """
        if not trades:
            return []
        
        print(f"📈 Constructing price history from {len(trades)} trades")
        
        # Group trades by hour
        hourly_data = {}
        
        for trade in trades:
            try:
                # Parse trade timestamp (format may vary)
                timestamp = trade.get('timestamp') or trade.get('created_at')
                price = float(trade.get('price', 0))
                size = float(trade.get('size', 0))
                
                # Parse to datetime
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromtimestamp(timestamp)
                
                # Round to nearest hour
                hour_key = dt.replace(minute=0, second=0, microsecond=0)
                
                if hour_key not in hourly_data:
                    hourly_data[hour_key] = {
                        'prices': [],
                        'volume': 0
                    }
                
                hourly_data[hour_key]['prices'].append(price)
                hourly_data[hour_key]['volume'] += size
                
            except Exception as e:
                print(f"  ⚠️ Could not parse trade: {e}")
                continue
        
        # Calculate hourly averages
        price_history = []
        for hour, data in sorted(hourly_data.items()):
            avg_price = sum(data['prices']) / len(data['prices'])
            price_history.append({
                'timestamp': hour.isoformat(),
                'yes_price': avg_price,
                'volume': data['volume']
            })
        
        print(f"  ✅ Created {len(price_history)} hourly price points")
        return price_history

def main():
    """Test the API client"""
    api = PolymarketHistoricalAPI()
    
    # First, test what endpoints are available
    api.test_endpoints()
    
    print("\n" + "="*70)
    print("Testing with actual market (if available)")
    print("="*70)
    
    # Try with a real market ID (this would need to be populated)
    # test_market_id = "0x..."  # Replace with actual market ID
    
    # For now, just document the findings
    print("\n📝 Next steps:")
    print("1. Get actual market IDs from resolved_markets.json")
    print("2. Test these endpoints with real market IDs")
    print("3. Examine response structure to extract price data")
    print("4. Build scraper based on what endpoints work")

if __name__ == "__main__":
    main()
