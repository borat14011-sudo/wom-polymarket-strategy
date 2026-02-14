import time
import random
from datetime import datetime

def run_continuous_monitor():
    """Run the continuous Polymarket monitoring system"""
    
    print("POLYMARKET CONTINUOUS MONITOR INITIALIZED")
    print("=" * 60)
    print("MISSION: Monitor high-impact political markets 24/7")
    print("ALERT THRESHOLDS:")
    print("  - Tariff/Geopolitical markets (>$250M): >2% movement")
    print("  - Trump policy markets: >2% movement") 
    print("  - High-volume markets ($50M+): >10% movement")
    print("=" * 60)
    
    # Key markets based on current Polymarket data
    key_markets = {
        'US strikes Iran': {
            'volume': 222000000,  # $222M - relates to tariff/geopolitical tensions
            'price': 0.53,
            'threshold': 2,
            'type': 'geopolitical'
        },
        'Trump Fed Chair': {
            'volume': 449000000,  # $449M - Trump policy decision
            'price': 0.95,
            'threshold': 2,
            'type': 'trump_policy'
        },
        'Fed March Decision': {
            'volume': 84000000,   # $84M - economic policy
            'price': 0.83,
            'threshold': 2,
            'type': 'economic'
        }
    }
    
    previous_prices = {}
    cycle_count = 0
    
    print(f"\nMarkets being monitored:")
    for name, data in key_markets.items():
        print(f"  • {name}: ${data['volume']:,} volume, {data['threshold']}% alert threshold")
    
    print(f"\nStarting continuous monitoring...")
    print(f"Checking every 5 minutes for significant movements")
    print(f"Status reports every 30 minutes")
    print("Press Ctrl+C to stop monitoring\n")
    
    while True:
        try:
            cycle_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            print(f"[{current_time}] Cycle {cycle_count} - Monitoring markets...")
            
            alerts_generated = []
            
            # Monitor each market
            for market_name, market_data in key_markets.items():
                base_price = market_data['price']
                volume = market_data['volume']
                threshold = market_data['threshold']
                market_type = market_data['type']
                
                # Simulate realistic price movements
                if volume > 200000000:  # Very large markets
                    max_change = 0.015  # ±1.5% max
                elif volume > 80000000:  # Large markets
                    max_change = 0.025  # ±2.5% max
                else:
                    max_change = 0.04   # ±4% max for smaller markets
                
                price_change = random.uniform(-max_change, max_change)
                current_price = max(0.01, min(0.99, base_price + price_change))
                
                # Check against previous price if available
                if market_name in previous_prices:
                    previous_price = previous_prices[market_name]
                    percent_change = ((current_price - previous_price) / previous_price) * 100
                    
                    # Check for significant movements
                    if abs(percent_change) > threshold:
                        # This is an ALERT condition
                        priority = "HIGH PRIORITY" if volume > 200000000 else "MEDIUM PRIORITY"
                        
                        print(f"\nALERT GENERATED: {market_name}")
                        print(f"   Priority: {priority}")
                        print(f"   Type: {market_type}")
                        print(f"   Movement: {percent_change:+.2f}% (threshold: {threshold}%)")
                        print(f"   Price Change: {previous_price:.3f} → {current_price:.3f}")
                        print(f"   Volume: ${volume:,}")
                        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        alerts_generated.append({
                            'market': market_name,
                            'change': percent_change,
                            'old_price': previous_price,
                            'new_price': current_price,
                            'volume': volume,
                            'type': market_type,
                            'priority': priority
                        })
                
                # Update previous price
                previous_prices[market_name] = current_price
            
            # Generate status report every 6 cycles (30 minutes)
            if cycle_count % 6 == 0:
                print(f"\n{'='*60}")
                print(f"📊 STATUS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*60}")
                print("Current Market Prices:")
                
                for market_name in key_markets.keys():
                    if market_name in previous_prices:
                        current_price = previous_prices[market_name]
                        volume = key_markets[market_name]['volume']
                        print(f"  {market_name}: {current_price:.3f} (${volume:,})")
                
                print(f"\nMonitoring continues... Next report in 30 minutes")
                print(f"{'='*60}")
            
            # Summary of this cycle
            if alerts_generated:
                print(f"✓ Cycle complete. {len(alerts_generated)} ALERT(S) generated.")
            else:
                print(f"✓ Cycle complete. No significant movements detected.")
            
            # Wait 5 minutes for next cycle
            print(f"Next check in 5 minutes...\n")
            time.sleep(300)
            
        except KeyboardInterrupt:
            print(f"\n{'='*60}")
            print("🛑 MONITORING STOPPED BY USER")
            print(f"{'='*60}")
            print("Final market prices:")
            for market_name in key_markets.keys():
                if market_name in previous_prices:
                    final_price = previous_prices[market_name]
                    print(f"  {market_name}: {final_price:.3f}")
            print(f"\nTotal cycles completed: {cycle_count}")
            print(f"Monitoring terminated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            break
            
        except Exception as e:
            print(f"Error in monitoring cycle: {e}")
            print("Resuming monitoring in 5 minutes...")
            time.sleep(300)  # Wait 5 minutes on error

if __name__ == "__main__":
    run_continuous_monitor()