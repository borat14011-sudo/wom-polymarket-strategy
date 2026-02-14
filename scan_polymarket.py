import json
import time
import requests
from datetime import datetime, timedelta

def scan_current_markets():
    """Scan current Polymarket markets for tariff and deportation related markets"""
    print("Scanning current Polymarket markets...")
    
    try:
        # Get current markets from gamma API
        url = "https://gamma-api.polymarket.com/markets"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            markets = response.json()
            print(f"Found {len(markets)} total markets")
            
            # Analyze markets
            current_markets = []
            tariff_markets = []
            deportation_markets = []
            trump_markets = []
            high_volume_markets = []
            
            for market in markets:
                # Only look at active, non-closed markets
                if market.get('active') and not market.get('closed'):
                    current_markets.append(market)
                    
                    question = market.get('question', '').lower()
                    volume = float(market.get('volume', 0))
                    
                    # Check for Trump-related markets
                    if 'trump' in question:
                        trump_markets.append(market)
                    
                    # Check for tariff-related markets
                    if any(keyword in question for keyword in ['tariff', 'tariffs', 'trade war', 'import tax']):
                        tariff_markets.append(market)
                    
                    # Check for deportation/immigration markets
                    if any(keyword in question for keyword in ['deportation', 'deport', 'immigration', 'border', 'migrant']):
                        deportation_markets.append(market)
                    
                    # High volume markets ($250K+)
                    if volume >= 250000:
                        high_volume_markets.append(market)
            
            print(f"\nActive markets: {len(current_markets)}")
            print(f"Trump markets: {len(trump_markets)}")
            print(f"Tariff markets: {len(tariff_markets)}")
            print(f"Deportation markets: {len(deportation_markets)}")
            print(f"High volume markets (>$250K): {len(high_volume_markets)}")
            
            # Display Trump markets (likely to include tariff/deportation policies)
            print("\n" + "="*80)
            print("TRUMP-RELATED MARKETS (Potential Tariff/Deportation Focus)")
            print("="*80)
            
            for market in trump_markets[:10]:  # Show top 10
                question = market.get('question', '')
                volume = float(market.get('volume', 0))
                prices = market.get('outcomePrices', '[]')
                end_date = market.get('endDate', '')
                
                print(f"\nMarket: {question}")
                print(f"Volume: ${volume:,.0f}")
                print(f"Prices: {prices}")
                print(f"End Date: {end_date}")
                print(f"Market ID: {market.get('id')}")
                
                # Parse prices
                try:
                    price_data = json.loads(prices) if isinstance(prices, str) else prices
                    if len(price_data) >= 2:
                        yes_price = float(price_data[0])
                        no_price = float(price_data[1])
                        print(f"YES price: {yes_price:.3f}, NO price: {no_price:.3f}")
                except:
                    pass
            
            # Display tariff markets specifically
            if tariff_markets:
                print("\n" + "="*80)
                print("TARIFF MARKETS")
                print("="*80)
                
                for market in tariff_markets:
                    question = market.get('question', '')
                    volume = float(market.get('volume', 0))
                    prices = market.get('outcomePrices', '[]')
                    
                    print(f"\nMarket: {question}")
                    print(f"Volume: ${volume:,.0f}")
                    print(f"Prices: {prices}")
                    print(f"Market ID: {market.get('id')}")
            
            # Display deportation markets specifically
            if deportation_markets:
                print("\n" + "="*80)
                print("DEPORTATION MARKETS")
                print("="*80)
                
                for market in deportation_markets:
                    question = market.get('question', '')
                    volume = float(market.get('volume', 0))
                    prices = market.get('outcomePrices', '[]')
                    
                    print(f"\nMarket: {question}")
                    print(f"Volume: ${volume:,.0f}")
                    print(f"Prices: {prices}")
                    print(f"Market ID: {market.get('id')}")
            
            # Display high volume markets
            print("\n" + "="*80)
            print("HIGH VOLUME MARKETS (>$250K)")
            print("="*80)
            
            # Sort by volume
            high_volume_sorted = sorted(high_volume_markets, key=lambda x: float(x.get('volume', 0)), reverse=True)
            
            for market in high_volume_sorted[:10]:  # Top 10 by volume
                question = market.get('question', '')
                volume = float(market.get('volume', 0))
                prices = market.get('outcomePrices', '[]')
                category = market.get('category', '')
                
                print(f"\nMarket: {question}")
                print(f"Category: {category}")
                print(f"Volume: ${volume:,.0f}")
                print(f"Prices: {prices}")
                
                # Parse prices
                try:
                    price_data = json.loads(prices) if isinstance(prices, str) else prices
                    if len(price_data) >= 2:
                        yes_price = float(price_data[0])
                        no_price = float(price_data[1])
                        print(f"YES price: {yes_price:.3f}, NO price: {no_price:.3f}")
                except:
                    pass
            
            # Save market data for monitoring
            monitor_data = {
                'timestamp': datetime.now().isoformat(),
                'trump_markets': trump_markets,
                'tariff_markets': tariff_markets,
                'deportation_markets': deportation_markets,
                'high_volume_markets': high_volume_markets[:20]  # Top 20
            }
            
            with open('current_markets.json', 'w') as f:
                json.dump(monitor_data, f, indent=2)
            
            print(f"\nMarket data saved to current_markets.json")
            return monitor_data
            
        else:
            print(f"Failed to get data: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error scanning markets: {e}")
        return None

if __name__ == "__main__":
    scan_current_markets()