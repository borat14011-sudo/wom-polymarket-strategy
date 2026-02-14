#!/usr/bin/env python3
"""
Polymarket Monitor - Continuous price tracking with alerts
"""
import json
import time
import requests
from datetime import datetime
import os

def fetch_markets():
    """Fetch current market data"""
    url = 'https://gamma-api.polymarket.com/markets'
    params = {'limit': 200, 'closed': False}
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            markets = response.json()
            return {
                'timestamp': datetime.now().isoformat(),
                'markets': markets,
                'count': len(markets)
            }
        else:
            print(f"[ERROR] API returned {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to fetch markets: {e}")
        return None

def load_baseline():
    """Load baseline market data"""
    try:
        with open('market-baseline.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("[ERROR] No baseline data found. Run analyze_markets.py first.")
        return None

def get_focus_markets(markets):
    """Extract key markets for monitoring"""
    focus = {
        'tariff': [],
        'deportation': [],
        'high_volume': []
    }
    
    for market in markets:
        question = market.get('question', '').lower()
        volume = float(market.get('volume', 0))
        
        # Tariff markets
        if 'tariff' in question and ('250' in question or 'billion' in question):
            focus['tariff'].append(market)
        
        # Deportation markets
        elif 'deport' in question:
            focus['deportation'].append(market)
        
        # High volume markets (>$1M)
        if volume > 1000000:
            focus['high_volume'].append(market)
    
    return focus

def calculate_price_change(old_price, new_price):
    """Calculate percentage change between prices"""
    old_val = float(old_price)
    new_val = float(new_price)
    if old_val == 0:
        return 0
    return ((new_val - old_val) / old_val) * 100

def check_alerts(current_data, baseline_data):
    """Check for significant price movements and send alerts"""
    alerts = []
    
    current_markets = {m['id']: m for m in current_data['markets']}
    baseline_markets = {m['id']: m for m in baseline_data.get('tariff_markets', []) + 
                                   baseline_data.get('deportation_markets', []) + 
                                   baseline_data.get('high_volume_markets', [])}
    
    # Check tariff markets (>2% movement)
    for market_id in [m['id'] for m in baseline_data.get('tariff_markets', [])]:
        if market_id in current_markets:
            current = current_markets[market_id]
            baseline = baseline_markets[market_id]
            
            current_price = float(current['outcomePrices'][0])
            baseline_price = float(baseline['outcomePrices'][0])
            
            change = calculate_price_change(baseline_price, current_price)
            
            if abs(change) > 2.0:
                alerts.append({
                    'type': 'TARIFF_ALERT',
                    'market': current['question'],
                    'volume': float(current['volume']),
                    'old_price': baseline_price,
                    'new_price': current_price,
                    'change_pct': change
                })
    
    # Check deportation markets (>5% movement)
    for market_id in [m['id'] for m in baseline_data.get('deportation_markets', [])]:
        if market_id in current_markets:
            current = current_markets[market_id]
            baseline = baseline_markets[market_id]
            
            current_price = float(current['outcomePrices'][0])
            baseline_price = float(baseline['outcomePrices'][0])
            
            change = calculate_price_change(baseline_price, current_price)
            
            if abs(change) > 5.0:
                alerts.append({
                    'type': 'DEPORTATION_ALERT',
                    'market': current['question'],
                    'volume': float(current['volume']),
                    'old_price': baseline_price,
                    'new_price': current_price,
                    'change_pct': change
                })
    
    # Check high volume markets (>10% movement, >$1M volume)
    for market_id in [m['id'] for m in baseline_data.get('high_volume_markets', [])]:
        if market_id in current_markets:
            current = current_markets[market_id]
            baseline = baseline_markets[market_id]
            
            current_price = float(current['outcomePrices'][0])
            baseline_price = float(baseline['outcomePrices'][0])
            volume = float(current['volume'])
            
            change = calculate_price_change(baseline_price, current_price)
            
            if abs(change) > 10.0 and volume > 1000000:
                alerts.append({
                    'type': 'HIGH_VOLUME_ALERT',
                    'market': current['question'],
                    'volume': volume,
                    'old_price': baseline_price,
                    'new_price': current_price,
                    'change_pct': change
                })
    
    return alerts

def format_alert(alert):
    """Format alert message"""
    direction = "📈 UP" if alert['change_pct'] > 0 else "📉 DOWN"
    return f"""
🚨 {alert['type'].replace('_', ' ')} 🚨
{direction} {abs(alert['change_pct']):.1f}%
Market: {alert['market'][:80]}...
Volume: ${alert['volume']:,.0f}
Price: {alert['old_price']:.3f} → {alert['new_price']:.3f}
"""

def main():
    print("=== POLYMARKET MONITOR STARTED ===")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    baseline = load_baseline()
    if not baseline:
        return
    
    check_count = 0
    last_update = time.time()
    
    while True:
        try:
            # Fetch fresh data
            current_data = fetch_markets()
            if not current_data:
                time.sleep(60)  # Wait 1 minute on error
                continue
            
            # Save current data
            with open('active-markets.json', 'w') as f:
                json.dump(current_data, f, indent=2)
            
            # Check for alerts
            alerts = check_alerts(current_data, baseline)
            
            # Send immediate alerts
            for alert in alerts:
                alert_msg = format_alert(alert)
                print(alert_msg)
                # Send to main session via message tool
                # message.send(message=alert_msg.strip())
            
            check_count += 1
            current_time = time.time()
            
            # Send periodic update every 30 minutes
            if current_time - last_update >= 1800:  # 30 minutes
                focus_markets = get_focus_markets(current_data['markets'])
                
                summary = f"""
📊 MARKET MONITOR UPDATE ({datetime.now().strftime('%H:%M:%S')})
Checks performed: {check_count}

🎯 Key Tariff Markets: {len(focus_markets['tariff'])}
👮 Deportation Markets: {len(focus_markets['deportation'])}
💰 High Volume Markets: {len(focus_markets['high_volume'])}

Total alerts triggered: {len(alerts)}
"""
                print(summary)
                # message.send(message=summary.strip())
                last_update = current_time
            
            # Wait 5 minutes before next check
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Check #{check_count} complete. Next check in 5 minutes...")
            time.sleep(300)  # 5 minutes
            
        except KeyboardInterrupt:
            print("\n[STOPPED] Market monitor stopped by user")
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    main()