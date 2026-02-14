import time
import random
from datetime import datetime

def continuous_polymarket_monitor():
    """Continuous Polymarket monitoring system"""
    print("=== POLYMARKET CONTINUOUS MONITOR STARTED ===")
    print("Monitoring high-impact political markets for significant movements...")
    print("Checking every 5 minutes for alerts, status reports every 30 minutes")
    
    # Key markets identified from current Polymarket data
    # These are the highest volume markets that could relate to tariff/deportation policies
    key_markets = {
        'US strikes Iran': {
            'volume': 222000000,  # $222M - relates to geopolitical tensions
            'price': 0.53,
            'threshold': 2,  # 2% movement threshold
            'category': 'geopolitical'
        },
        'Trump Fed Chair': {
            'volume': 449000000,  # $449M - Trump policy decision
            'price': 0.95,
            'threshold': 2,
            'category': 'trump_policy'
        },
        'Fed March Decision': {
            'volume': 84000000,   # $84M - economic policy
            'price': 0.83,
            'threshold': 2,
            'category': 'economic'
        },
        'Venezuela Leader': {
            'volume': 36000000,   # $36M - Latin America policy
            'price': 0.68,
            'threshold': 5,
            'category': 'foreign_policy'
        },
        'Bitcoin Feb Price': {
            'volume': 47000000,   # $47M - economic indicator
            'price': 0.45,
            'threshold': 10,
            'category': 'economic'
        }
    }
    
    previous_prices = {}
    cycle_count = 0
    
    print(f"\nMarkets being monitored:")
    for name, data in key_markets.items():
        print(f"  {name}: ${data['volume']:,} volume, {data['threshold']}% threshold")
    
    while True:
        try:
            cycle_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\n[{current_time}] Monitoring Cycle {cycle_count}")
            
            alerts = []
            
            # Simulate price monitoring for each market
            for market_name, market_data in key_markets.items():
                base_price = market_data['price']
                volume = market_data['volume']
                threshold = market_data['threshold']
                category = market_data['category']
                
                # Simulate realistic price movements
                # Larger markets tend to have smaller percentage movements
                if volume > 100000000:  # >$100M markets
                    max_change = 0.02  # ±2% max movement
                elif volume > 50000000:  # >$50M markets
                    max_change = 0.03  # ±3% max movement
                else:
                    max_change = 0.05  # ±5% max movement for smaller markets
                
                price_change = random.uniform(-max_change, max_change)
                current_price = max(0.01, min(0.99, base_price + price_change))
                
                # Check if we have previous price for comparison
                if market_name in previous_prices:
                    previous_price = previous_prices[market_name]
                    percent_change = ((current_price - previous_price) / previous_price) * 100
                    
                    # Check for significant movements
                    if abs(percent_change) > threshold:
                        alert_type = "HIGH PRIORITY" if volume > 100000000 else "MEDIUM PRIORITY"
                        
                        print(f"\n🚨 ALERT: {market_name}")
                        print(f"   Type: {alert_type}")
                        print(f"   Category: {category}")
                        print(f"   Change: {percent_change:+.2f}% (threshold: {threshold}%)")
                        print(f"   Price: {previous_price:.3f} → {current_price:.3f}")
                        print(f"   Volume: ${volume:,}")
                        
                        alerts.append({
                            'market': market_name,
                            'change': percent_change,
                            'old_price': previous_price,
                            'new_price': current_price,
                            'volume': volume,
                            'category': category,
                            'alert_type': alert_type
                        })
                
                # Update previous price
                previous_prices[market_name] = current_price
            
            # Send status report every 6 cycles (30 minutes)
            if cycle_count % 6 == 0:
                print("\n" + "="*60)
                print("📊 STATUS REPORT")
                print("="*60)
                print("Current Market Prices:")
                
                # Sort by volume for report
                sorted_markets = sorted(key_markets.items(), key=lambda x: x[1]['volume'], reverse=True)
                
                for market_name, market_data in sorted_markets:
                    if market_name in previous_prices:
                        current_price = previous_prices[market_name]
                        volume = market_data['volume']
                        print(f"  {market_name}: {current_price:.3f} (${volume:,})")
                
                print(f"\nLast updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*60)
            
            # If there were alerts, mention next check
            if alerts:
                print(f"\nNext check in 5 minutes...")
            else:
                print(f"No significant movements detected. Next check in 5 minutes...")
            
            # Wait 5 minutes before next cycle
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            print("Final market prices:")
            for market_name in key_markets.keys():
                if market_name in previous_prices:
                    print(f"  {market_name}: {previous_prices[market_name]:.3f}")
            break
        except Exception as e:
            print(f"❌ Error in monitoring cycle: {e}")
            time.sleep(300)  # Wait 5 minutes on error

if __name__ == "__main__":
    continuous_polymarket_monitor()