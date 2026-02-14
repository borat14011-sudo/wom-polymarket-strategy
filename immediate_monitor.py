#!/usr/bin/env python3
"""
Polymarket Monitor - Immediate Output Version
"""
import json
import time
import requests
import ast
from datetime import datetime

def main():
    print("=== POLYMARKET MONITOR STARTING ===")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load baseline
    try:
        with open('market-baseline.json', 'r') as f:
            baseline = json.load(f)
        print(f"[OK] Loaded baseline with {len(baseline.get('deportation_markets', []))} deportation markets")
    except Exception as e:
        print(f"[ERROR] Failed to load baseline: {e}")
        return
    
    check_count = 0
    
    while True:
        try:
            check_count += 1
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting check #{check_count}")
            
            # Fetch current data
            print("[FETCH] Getting current market data...")
            url = 'https://gamma-api.polymarket.com/markets'
            response = requests.get(url, params={'limit': 200, 'closed': False}, timeout=15)
            
            if response.status_code != 200:
                print(f"[ERROR] API returned {response.status_code}")
                time.sleep(60)
                continue
            
            current_data = {
                'timestamp': datetime.now().isoformat(),
                'markets': response.json(),
                'count': len(response.json())
            }
            
            print(f"[OK] Fetched {current_data['count']} markets")
            
            # Save current data
            with open('active-markets.json', 'w') as f:
                json.dump(current_data, f, indent=2)
            
            # Check deportation markets for changes
            print("[CHECK] Analyzing deportation markets...")
            alerts = []
            
            current_markets = {m['id']: m for m in current_data['markets']}
            
            for baseline_market in baseline.get('deportation_markets', []):
                market_id = baseline_market['id']
                if market_id in current_markets:
                    current_market = current_markets[market_id]
                    
                    old_prices = ast.literal_eval(baseline_market['outcomePrices'])
                    new_prices = ast.literal_eval(current_market['outcomePrices'])
                    
                    old_price = float(old_prices[0])
                    new_price = float(new_prices[0])
                    
                    change = ((new_price - old_price) / old_price) * 100
                    
                    if abs(change) > 5.0:
                        alerts.append({
                            'type': 'DEPORTATION',
                            'question': current_market['question'],
                            'volume': float(current_market['volume']),
                            'old_price': old_price,
                            'new_price': new_price,
                            'change': change
                        })
            
            # Display alerts
            if alerts:
                print(f"\n🚨 ALERTS FOUND: {len(alerts)} 🚨")
                for alert in alerts:
                    direction = "UP" if alert['change'] > 0 else "DOWN"
                    print(f"""
[ALERT] DEPORTATION MARKET {direction} {abs(alert['change']):.1f}%
MARKET: {alert['question'][:60]}...
VOLUME: ${alert['volume']:,.0f}
PRICE: {alert['old_price']:.3f} -> {alert['new_price']:.3f}
""")
            else:
                print("[OK] No significant movements detected")
            
            # Show current key prices
            print("\n[CURRENT KEY MARKETS]")
            
            # Tariff market
            tariff_markets = [m for m in current_data['markets'] if 'tariff' in m.get('question', '').lower() and '250' in m.get('question', '')]
            if tariff_markets:
                market = tariff_markets[0]
                prices = ast.literal_eval(market['outcomePrices'])
                price = float(prices[0])
                volume = float(market['volume'])
                print(f"TARIFF: {market['question'][:50]}...")
                print(f"  Price: {price:.3f} | Volume: ${volume:,.0f}")
            
            # Top deportation markets
            deportation_markets = [m for m in current_data['markets'] if 'deport' in m.get('question', '').lower()]
            if deportation_markets:
                top_3 = sorted(deportation_markets, key=lambda x: float(x['volume']), reverse=True)[:3]
                print("DEPORTATION TOP 3:")
                for market in top_3:
                    prices = ast.literal_eval(market['outcomePrices'])
                    price = float(prices[0])
                    volume = float(market['volume'])
                    print(f"  {market['question'][:40]}...")
                    print(f"    Price: {price:.3f} | Volume: ${volume:,.0f}")
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Check #{check_count} complete.")
            print("[WAIT] Next check in 5 minutes...")
            
            # Wait 5 minutes
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n[STOPPED] Market monitor stopped by user")
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()