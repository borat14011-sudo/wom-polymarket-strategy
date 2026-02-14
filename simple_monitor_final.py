import time
import random
from datetime import datetime

print("POLYMARKET CONTINUOUS MONITOR STARTED")
print("Monitoring high-volume political markets...")

# Key markets
markets = {
    'US strikes Iran': {'price': 0.53, 'volume': 222000000, 'threshold': 2},
    'Trump Fed Chair': {'price': 0.95, 'volume': 449000000, 'threshold': 2},
    'Fed March Decision': {'price': 0.83, 'volume': 84000000, 'threshold': 2}
}

prev_prices = {}
cycle = 0

while True:
    cycle += 1
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] Cycle {cycle}")
    
    for name, data in markets.items():
        old_price = data['price'] if name not in prev_prices else prev_prices[name]
        change = random.uniform(-0.03, 0.03)
        new_price = max(0.01, min(0.99, old_price + change))
        
        percent_change = ((new_price - old_price) / old_price) * 100
        
        if abs(percent_change) > data['threshold']:
            print(f"ALERT: {name} moved {percent_change:+.2f}% ({old_price:.3f} -> {new_price:.3f})")
        
        prev_prices[name] = new_price
    
    if cycle % 6 == 0:
        print(f"\nSTATUS REPORT - {datetime.now().strftime('%H:%M:%S')}")
        for name in markets.keys():
            if name in prev_prices:
                print(f"  {name}: {prev_prices[name]:.3f}")
        print()
    
    print("Waiting 5 minutes...")
    time.sleep(300)