import time
import random
from datetime import datetime

def continuous_monitor():
    """Continuous market monitoring with simulated data"""
    print("=== POLYMARKET CONTINUOUS MONITOR STARTED ===")
    print("Monitoring high-impact political markets...")
    
    # Key markets we're monitoring based on current Polymarket data
    key_markets = {
        'US strikes Iran': {'volume': 222000000, 'price': 0.53, 'threshold': 2},
        'Trump Fed Chair': {'volume': 449000000, 'price': 0.95, 'threshold': 2},
        'Venezuela Leader': {'volume': 36000000, 'price': 0.68, 'threshold': 5},
        'Bitcoin Feb Price': {'volume': 47000000, 'price': 0.45, 'threshold': 10},
        'Fed March Decision': {'volume': 84000000, 'price': 0.83, 'threshold': 2}
    }
    
    previous_prices = {}
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\n[{current_time}] Cycle {cycle_count}")
            
            # Simulate price monitoring
            alerts = []
            
            for market_name, market_data in key_markets.items():
                base_price = market_data['price']
                volume = market_data['volume']
                threshold = market_data['threshold']
                
                # Simulate small price movements
                price_change = random.uniform(-0.03, 0.03)  # ±3% max movement
                current_price = max(0.01, min(0.99, base_price + price_change))
                
                # Check if we have previous price for comparison
                if market_name in previous_prices:
                    prev_price = previous_prices[market_name]
                    percent_change = ((current_price - prev_price) / prev_price) * 100
                    
                    # Check for significant movements
                    if abs(percent_change) > threshold:
                        alert_type = "HIGH IMPACT" if volume > 100000000 else "MEDIUM IMPACT"
                        print(f"🚨 ALERT: {market_name}")
                        print(f"   Change: {percent_change:+.2f}% (threshold: {threshold}%)")
                        print(f"   Price: {prev_price:.3f} → {current_price:.3f}")
                        print(f"   Volume: ${volume:,}")
                        alerts.append({
                            'market': market_name,
                            'change': percent_change,
                            'old_price': prev_price,
                            'new_price': current_price,
                            'volume': volume,
                            'type': alert_type
                        })
                
                # Update previous price
                previous_prices[market_name] = current_price
            
            # Send status report every 6 cycles (30 minutes)
            if cycle_count % 6 == 0:
                print("\n📊 STATUS REPORT")
                print("=" * 50)
                print("Current Market Prices:")
                for market_name in key_markets.keys():
                    if market_name in previous_prices:
                        price = previous_prices[market_name]
                        volume = key_markets[market_name]['volume']
                        print(f"  {market_name}: {price:.3f} (${volume:,})")
            
            # Wait 5 minutes for next cycle
            print(f"Waiting 5 minutes for next cycle...")
            time.sleep(300)  # 5 minutes
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(300)  # Wait 5 minutes on error

if __name__ == "__main__":
    continuous_monitor()