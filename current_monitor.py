import json
import time
import requests
from datetime import datetime, timedelta

class CurrentPolymarketMonitor:
    def __init__(self):
        self.previous_prices = {}
        self.alerts_sent = {}
        
        # Key markets identified from current Polymarket homepage
        self.key_markets = {
            'trump_fed_chair': {
                'name': 'Who will Trump nominate as Fed Chair?',
                'volume': 449000000,  # $449M
                'current_price': 0.95,  # 95% Kevin Warsh
                'url': 'https://polymarket.com/market/who-will-trump-nominate-as-fed-chair'
            },
            'us_strikes_iran': {
                'name': 'US strikes Iran by...?',
                'volume': 222000000,  # $222M
                'current_price': 0.53,  # 53% chance by June 30
                'url': 'https://polymarket.com/market/us-strikes-iran-by'
            },
            'venezuela_leader': {
                'name': 'Venezuela leader end of 2026?',
                'volume': 36000000,  # $36M
                'current_price': 0.68,  # 68% Delcy Rodriguez
                'url': 'https://polymarket.com/market/venezuela-leader-end-of-2026'
            },
            'bitcoin_feb': {
                'name': 'What price will Bitcoin hit in February?',
                'volume': 47000000,  # $47M
                'current_price': 0.45,  # 45% chance of >$75K
                'url': 'https://polymarket.com/market/what-price-will-bitcoin-hit-in-february'
            },
            'fed_march_decision': {
                'name': 'Fed decision in March?',
                'volume': 84000000,  # $84M
                'current_price': 0.83,  # 83% no change
                'url': 'https://polymarket.com/market/fed-decision-in-march'
            }
        }
    
    def simulate_current_prices(self):
        """Simulate current market prices (since we can't get real-time API access)"""
        # In a real implementation, this would scrape current prices from the website
        # For now, we'll simulate some price movements
        
        current_prices = {}
        for market_id, market_data in self.key_markets.items():
            base_price = market_data['current_price']
            # Simulate small price movements
            import random
            price_change = random.uniform(-0.05, 0.05)  # ±5% random movement
            current_price = max(0.01, min(0.99, base_price + price_change))
            
            current_prices[market_id] = {
                'name': market_data['name'],
                'price': current_price,
                'volume': market_data['volume'],
                'url': market_data['url']
            }
        
        return current_prices
    
    def calculate_price_change(self, current_price, previous_price):
        """Calculate percentage change between prices"""
        if previous_price is None or previous_price == 0:
            return 0
        return ((current_price - previous_price) / previous_price) * 100
    
    def check_alerts(self, current_prices):
        """Check for significant price movements and generate alerts"""
        alerts = []
        
        for market_id, current_data in current_prices.items():
            current_price = current_data['price']
            volume = current_data['volume']
            
            # Check if we have previous price data
            if market_id in self.previous_prices:
                previous_price = self.previous_prices[market_id]['price']
                change = self.calculate_price_change(current_price, previous_price)
                
                # Check for significant movements based on market type
                if 'us_strikes_iran' in market_id and abs(change) > 2:  # >2% for tariff-like markets
                    alerts.append({
                        'type': 'geopolitical_movement',
                        'market': current_data['name'],
                        'change': change,
                        'current_price': current_price,
                        'previous_price': previous_price,
                        'volume': volume,
                        'urgency': 'high'
                    })
                
                if 'trump_fed_chair' in market_id and abs(change) > 5:  # >5% for Trump policy markets
                    alerts.append({
                        'type': 'trump_policy_movement',
                        'market': current_data['name'],
                        'change': change,
                        'current_price': current_price,
                        'previous_price': previous_price,
                        'volume': volume,
                        'urgency': 'high'
                    })
                
                if volume > 50000000 and abs(change) > 10:  # >$50M volume and >10% change
                    alerts.append({
                        'type': 'high_volume_movement',
                        'market': current_data['name'],
                        'change': change,
                        'current_price': current_price,
                        'previous_price': previous_price,
                        'volume': volume,
                        'urgency': 'high'
                    })
            
            # Update previous prices
            self.previous_prices[market_id] = current_data
        
        return alerts
    
    def format_alert_message(self, alert):
        """Format an alert for sending"""
        alert_symbol = "ALERT" if alert['urgency'] == 'high' else "NOTICE"
        
        message = f"**POLYMARKET {alert_symbol}**\n\n"
        message += f"**Type:** {alert['type'].replace('_', ' ').title()}\n"
        message += f"**Market:** {alert['market']}\n"
        message += f"**Change:** {alert['change']:.2f}%\n"
        message += f"**Current Price:** {alert['current_price']:.3f}\n"
        message += f"**Previous Price:** {alert['previous_price']:.3f}\n"
        message += f"**Volume:** ${alert['volume']:,}\n"
        message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return message
    
    def generate_status_report(self, current_prices):
        """Generate a status report with key market information"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'markets': []
        }
        
        for market_id, data in current_prices.items():
            report['markets'].append({
                'name': data['name'],
                'current_price': data['price'],
                'volume': data['volume'],
                'url': data['url']
            })
        
        return report
    
    def format_status_report(self, report):
        """Format a status report for sending"""
        message = "**POLYMARKET STATUS REPORT**\n\n"
        message += f"**Report Time:** {report['timestamp']}\n\n"
        
        # Sort markets by volume
        sorted_markets = sorted(report['markets'], key=lambda x: x['volume'], reverse=True)
        
        message += "**TOP MARKETS BY VOLUME:**\n"
        for i, market in enumerate(sorted_markets, 1):
            message += f"{i}. {market['name']}\n"
            message += f"   Current Price: {market['current_price']:.3f}\n"
            message += f"   Volume: ${market['volume']:,}\n"
            if i < len(sorted_markets):
                message += "\n"
        
        return message
    
    def monitor_cycle(self):
        """Run a single monitoring cycle"""
        print(f"Monitoring cycle - {datetime.now().strftime('%H:%M:%S')}")
        
        # Get current prices (simulated for now)
        current_prices = self.simulate_current_prices()
        
        # Check for alerts
        alerts = self.check_alerts(current_prices)
        
        # Process alerts
        for alert in alerts:
            alert_message = self.format_alert_message(alert)
            print(f"\n{alert_message}")
            print(f"ALERT: {alert['type']} - {alert['change']:.2f}% change detected")
        
        return alerts, current_prices

def main():
    monitor = CurrentPolymarketMonitor()
    print("Starting Polymarket Monitor for Current Markets...")
    print("Monitoring high-volume markets for significant movements...")
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            print(f"\n--- Cycle {cycle_count} ---")
            
            # Run monitoring cycle
            alerts, current_prices = monitor.monitor_cycle()
            
            # Generate status report every 6 cycles (30 minutes)
            if cycle_count % 6 == 0:
                report = monitor.generate_status_report(current_prices)
                report_message = monitor.format_status_report(report)
                print(f"\n{report_message}")
                print("Status report generated")
            
            # Wait 5 minutes before next cycle
            print("Waiting 5 minutes for next cycle...")
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            break
        except Exception as e:
            print(f"Error in monitoring cycle: {e}")
            time.sleep(300)  # Wait 5 minutes on error

if __name__ == "__main__":
    main()