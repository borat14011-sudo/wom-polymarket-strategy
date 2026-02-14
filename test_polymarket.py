import json
import time
import requests
from datetime import datetime, timedelta

def test_polymarket_connection():
    """Test connection to Polymarket API and get current markets"""
    print("Testing Polymarket API connection...")
    
    try:
        # Test the API endpoint
        url = "https://clob.polymarket.com/markets?limit=50"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Successfully connected! Found {len(data.get('data', []))} markets")
            
            # Look for tariff and deportation markets
            tariff_markets = []
            deportation_markets = []
            high_volume_markets = []
            
            for market in data.get('data', []):
                if not market.get('active') or market.get('closed'):
                    continue
                    
                question = market.get('question', '').lower()
                volume = market.get('volume', 0)
                
                # Check for tariff-related markets
                if any(keyword in question for keyword in ['tariff', 'tariffs', 'trade war']):
                    tariff_markets.append({
                        'question': market['question'],
                        'volume': volume,
                        'price': market['tokens'][0]['price'] if market.get('tokens') else 0
                    })
                
                # Check for deportation-related markets
                if any(keyword in question for keyword in ['deportation', 'deport', 'immigration']):
                    deportation_markets.append({
                        'question': market['question'],
                        'volume': volume,
                        'price': market['tokens'][0]['price'] if market.get('tokens') else 0
                    })
                
                # High volume markets ($1M+)
                if volume >= 1000000:
                    high_volume_markets.append({
                        'question': market['question'],
                        'volume': volume,
                        'price': market['tokens'][0]['price'] if market.get('tokens') else 0
                    })
            
            print(f"\nFound {len(tariff_markets)} tariff markets:")
            for market in tariff_markets[:3]:
                print(f"  - {market['question'][:80]}...")
                print(f"    Volume: ${market['volume']:,}, Price: {market['price']:.3f}")
            
            print(f"\nFound {len(deportation_markets)} deportation markets:")
            for market in deportation_markets[:3]:
                print(f"  - {market['question'][:80]}...")
                print(f"    Volume: ${market['volume']:,}, Price: {market['price']:.3f}")
            
            print(f"\nFound {len(high_volume_markets)} high-volume markets:")
            for market in high_volume_markets[:5]:
                print(f"  - {market['question'][:80]}...")
                print(f"    Volume: ${market['volume']:,}, Price: {market['price']:.3f}")
            
            return True
        else:
            print(f"Failed to connect: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error testing connection: {e}")
        return False

if __name__ == "__main__":
    test_polymarket_connection()