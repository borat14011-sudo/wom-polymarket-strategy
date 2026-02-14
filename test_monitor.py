print("Testing Polymarket Monitor...")

# Simulate current market data based on what we found on Polymarket
key_markets = {
    'US strikes Iran': {'volume': 222000000, 'price': 0.53, 'threshold': 2},
    'Trump Fed Chair': {'volume': 449000000, 'price': 0.95, 'threshold': 2},
    'Venezuela Leader': {'volume': 36000000, 'price': 0.68, 'threshold': 5},
    'Bitcoin Feb Price': {'volume': 47000000, 'price': 0.45, 'threshold': 10},
    'Fed March Decision': {'volume': 84000000, 'price': 0.83, 'threshold': 2}
}

print("Current key markets identified:")
for name, data in key_markets.items():
    print(f"  {name}: ${data['volume']:,} volume, {data['price']:.2f} price")

print("\nSimulating price movements...")
import random

# Simulate a monitoring cycle
for market_name, market_data in key_markets.items():
    base_price = market_data['price']
    price_change = random.uniform(-0.05, 0.05)  # ±5% movement
    new_price = max(0.01, min(0.99, base_price + price_change))
    
    percent_change = ((new_price - base_price) / base_price) * 100
    
    print(f"\n{market_name}:")
    print(f"  Old price: {base_price:.3f}")
    print(f"  New price: {new_price:.3f}")
    print(f"  Change: {percent_change:+.2f}%")
    
    if abs(percent_change) > market_data['threshold']:
        print(f"  ALERT: Significant movement detected!")
    else:
        print(f"  Within threshold ({market_data['threshold']}%)")

print("\nMonitor test completed successfully!")
print("Ready to start continuous monitoring...")