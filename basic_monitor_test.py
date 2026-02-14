print("Starting Polymarket Monitor Test...")

# Key markets from current Polymarket data
markets = {
    'US strikes Iran': {'volume': 222000000, 'price': 0.53, 'threshold': 2},
    'Trump Fed Chair': {'volume': 449000000, 'price': 0.95, 'threshold': 2},
    'Fed March Decision': {'volume': 84000000, 'price': 0.83, 'threshold': 2}
}

print("Markets to monitor:")
for name, data in markets.items():
    print(f"  {name}: ${data['volume']:,} volume, threshold: {data['threshold']}%")

print("\nSimulating monitoring cycle...")
import random

alerts = []
for name, data in markets.items():
    old_price = data['price']
    change = random.uniform(-0.05, 0.05)  # ±5% change
    new_price = max(0.01, min(0.99, old_price + change))
    
    percent_change = ((new_price - old_price) / old_price) * 100
    
    print(f"\n{name}:")
    print(f"  Price: {old_price:.3f} -> {new_price:.3f}")
    print(f"  Change: {percent_change:+.2f}%")
    
    if abs(percent_change) > data['threshold']:
        print(f"  ALERT: Movement exceeds threshold!")
        alerts.append({
            'market': name,
            'change': percent_change,
            'old_price': old_price,
            'new_price': new_price,
            'volume': data['volume']
        })
    else:
        print(f"  Within threshold")

print(f"\nMonitoring cycle complete. Alerts generated: {len(alerts)}")
if alerts:
    print("Active alerts:")
    for alert in alerts:
        print(f"  {alert['market']}: {alert['change']:+.2f}%")

print("\nMonitor ready for continuous operation.")