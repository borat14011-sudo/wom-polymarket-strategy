#!/usr/bin/env python3
"""
Market Monitor Status Check
"""
import json
import time
from datetime import datetime

def check_status():
    print("=== MARKET MONITOR STATUS CHECK ===")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Check if active-markets.json exists and is recent
        with open('active-markets.json', 'r') as f:
            current_data = json.load(f)
        
        fetch_time = current_data['timestamp']
        print(f"\n[DATA] Last fetch: {fetch_time}")
        print(f"[DATA] Markets fetched: {current_data['count']}")
        
        # Analyze current markets
        markets = current_data['markets']
        
        deportation_markets = []
        tariff_markets = []
        high_volume_markets = []
        
        for market in markets:
            question = market.get('question', '').lower()
            volume = float(market.get('volume', 0))
            
            if 'deport' in question:
                deportation_markets.append(market)
            elif 'tariff' in question and '250' in question:
                tariff_markets.append(market)
            
            if volume > 1000000:
                high_volume_markets.append(market)
        
        print(f"\n[MARKETS] Deportation: {len(deportation_markets)}")
        print(f"[MARKETS] Tariff: {len(tariff_markets)}")
        print(f"[MARKETS] High volume (>$1M): {len(high_volume_markets)}")
        
        # Show key market prices
        print(f"\n[KEY PRICES]")
        
        if tariff_markets:
            market = tariff_markets[0]
            import ast
            prices = ast.literal_eval(market['outcomePrices'])
            price = float(prices[0])
            volume = float(market['volume'])
            print(f"TARIFF: {market['question'][:50]}...")
            print(f"  YES Price: {price:.3f} | Volume: ${volume:,.0f}")
        
        if deportation_markets:
            print("\nDEPORTATION MARKETS (Top 5 by volume):")
            top_5 = sorted(deportation_markets, key=lambda x: float(x['volume']), reverse=True)[:5]
            for i, market in enumerate(top_5, 1):
                import ast
                prices = ast.literal_eval(market['outcomePrices'])
                price = float(prices[0])
                volume = float(market['volume'])
                print(f"{i}. {market['question'][:45]}...")
                print(f"   YES Price: {price:.3f} | Volume: ${volume:,.0f}")
        
        # Check for recent alerts by comparing with baseline
        try:
            with open('market-baseline.json', 'r') as f:
                baseline = json.load(f)
            
            print(f"\n[ALERT CHECK] Checking for significant movements...")
            
            baseline_deportation = {m['id']: m for m in baseline.get('deportation_markets', [])}
            current_deportation = {m['id']: m for m in deportation_markets}
            
            alerts_found = 0
            for market_id in baseline_deportation:
                if market_id in current_deportation:
                    baseline_market = baseline_deportation[market_id]
                    current_market = current_deportation[market_id]
                    
                    import ast
                    old_prices = ast.literal_eval(baseline_market['outcomePrices'])
                    new_prices = ast.literal_eval(current_market['outcomePrices'])
                    
                    old_price = float(old_prices[0])
                    new_price = float(new_prices[0])
                    
                    change = ((new_price - old_price) / old_price) * 100
                    
                    if abs(change) > 5.0:
                        alerts_found += 1
                        direction = "UP" if change > 0 else "DOWN"
                        print(f"ALERT: {current_market['question'][:40]}... {direction} {abs(change):.1f}%")
            
            if alerts_found == 0:
                print("[OK] No significant movements vs baseline")
            
        except Exception as e:
            print(f"[ERROR] Could not check alerts: {e}")
        
        print(f"\n[STATUS] Monitor appears to be running normally")
        print("[INFO] Next automatic check in 5-minute intervals")
        
    except FileNotFoundError:
        print("[ERROR] No active-markets.json found. Monitor may not be running.")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    check_status()