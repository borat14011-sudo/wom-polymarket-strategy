import json
import time
import requests
from datetime import datetime, timedelta
import statistics

class PolymarketMonitor:
    def __init__(self):
        self.base_url = "https://clob.polymarket.com"
        self.previous_prices = {}
        self.alerts_sent = {}
        self.market_data = {}
        
        # Key markets to monitor
        self.focus_markets = {
            'tariff': [],  # Will populate with actual market IDs
            'deportation': [],
            'high_volume': []
        }
        
    def fetch_markets(self, limit=100, offset=0):
        """Fetch current market data from Polymarket API"""
        try:
            url = f"{self.base_url}/markets?limit={limit}&offset={offset}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching markets: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception fetching markets: {e}")
            return None
    
    def identify_focus_markets(self, markets_data):
        """Identify tariff, deportation, and high-volume markets"""
        focus_markets = {
            'tariff': [],
            'deportation': [],
            'high_volume': [],
            'ending_soon': []
        }
        
        if not markets_data or 'data' not in markets_data:
            return focus_markets
            
        current_time = datetime.now()
        
        for market in markets_data['data']:
            if not market.get('active') or market.get('closed'):
                continue
                
            question = market.get('question', '').lower()
            description = market.get('description', '').lower()
            volume = market.get('volume', 0)
            end_date = market.get('end_date_iso')
            
            # Check for tariff markets
            if any(keyword in question + description for keyword in ['tariff', 'tariffs', 'trade war', 'import tax']):
                focus_markets['tariff'].append(market)
            
            # Check for deportation markets
            if any(keyword in question + description for keyword in ['deportation', 'deport', 'immigration', 'border']):
                focus_markets['deportation'].append(market)
            
            # Check for high volume markets ($1M+)
            if volume >= 1000000:
                focus_markets['high_volume'].append(market)
            
            # Check for markets ending within 30 days
            if end_date:
                try:
                    end_time = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    if end_time <= current_time + timedelta(days=30):
                        focus_markets['ending_soon'].append(market)
                except:
                    pass
        
        return focus_markets
    
    def calculate_price_change(self, current_price, previous_price):
        """Calculate percentage change between prices"""
        if previous_price is None or previous_price == 0:
            return 0
        return ((current_price - previous_price) / previous_price) * 100
    
    def check_alerts(self, focus_markets):
        """Check for significant price movements and send alerts"""
        alerts = []
        current_time = datetime.now()
        
        # Check tariff markets (>2% movement)
        for market in focus_markets['tariff']:
            market_id = market['condition_id']
            current_price = market['tokens'][0]['price'] if market['tokens'] else 0
            
            if market_id in self.previous_prices:
                previous_price = self.previous_prices[market_id]
                change = self.calculate_price_change(current_price, previous_price)
                
                if abs(change) > 2:
                    alerts.append({
                        'type': 'tariff_movement',
                        'market': market['question'],
                        'change': change,
                        'current_price': current_price,
                        'previous_price': previous_price,
                        'volume': market.get('volume', 0),
                        'urgency': 'high'
                    })
            
            self.previous_prices[market_id] = current_price
        
        # Check deportation markets (>5% movement)
        for market in focus_markets['deportation']:
            market_id = market['condition_id']
            current_price = market['tokens'][0]['price'] if market['tokens'] else 0
            
            if market_id in self.previous_prices:
                previous_price = self.previous_prices[market_id]
                change = self.calculate_price_change(current_price, previous_price)
                
                if abs(change) > 5:
                    alerts.append({
                        'type': 'deportation_movement',
                        'market': market['question'],
                        'change': change,
                        'current_price': current_price,
                        'previous_price': previous_price,
                        'volume': market.get('volume', 0),
                        'urgency': 'high'
                    })
            
            self.previous_prices[market_id] = current_price
        
        # Check high volume markets (>10% movement)
        for market in focus_markets['high_volume']:
            market_id = market['condition_id']
            current_price = market['tokens'][0]['price'] if market['tokens'] else 0
            
            if market_id in self.previous_prices:
                previous_price = self.previous_prices[market_id]
                change = self.calculate_price_change(current_price, previous_price)
                
                if abs(change) > 10:
                    alerts.append({
                        'type': 'high_volume_movement',
                        'market': market['question'],
                        'change': change,
                        'current_price': current_price,
                        'previous_price': previous_price,
                        'volume': market.get('volume', 0),
                        'urgency': 'high'
                    })
            
            self.previous_prices[market_id] = current_price
        
        return alerts
    
    def generate_status_report(self, focus_markets):
        """Generate a status report with key market information"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'tariff_markets': [],
            'deportation_markets': [],
            'biggest_movers': [],
            'new_high_volume': []
        }
        
        # Add tariff market info
        for market in focus_markets['tariff']:
            if market['tokens']:
                report['tariff_markets'].append({
                    'question': market['question'],
                    'current_price': market['tokens'][0]['price'],
                    'volume': market.get('volume', 0)
                })
        
        # Add deportation market info
        for market in focus_markets['deportation']:
            if market['tokens']:
                report['deportation_markets'].append({
                    'question': market['question'],
                    'current_price': market['tokens'][0]['price'],
                    'volume': market.get('volume', 0)
                })
        
        # Calculate biggest movers
        all_changes = []
        for category in ['tariff', 'deportation', 'high_volume']:
            for market in focus_markets[category]:
                market_id = market['condition_id']
                current_price = market['tokens'][0]['price'] if market['tokens'] else 0
                
                if market_id in self.previous_prices:
                    previous_price = self.previous_prices[market_id]
                    change = self.calculate_price_change(current_price, previous_price)
                    all_changes.append({
                        'market': market['question'],
                        'change': change,
                        'volume': market.get('volume', 0)
                    })
        
        # Sort by absolute change and take top 3
        all_changes.sort(key=lambda x: abs(x['change']), reverse=True)
        report['biggest_movers'] = all_changes[:3]
        
        return report
    
    def format_alert_message(self, alert):
        """Format an alert for sending"""
        alert_symbol = "ALERT" if alert['urgency'] == 'high' else "NOTICE"
        
        message = f"**POLYMARKET {alert_symbol}**\n\n"
        message += f"**Type:** {alert['type'].replace('_', ' ').title()}\n"
        message += f"**Market:** {alert['market'][:100]}{'...' if len(alert['market']) > 100 else ''}\n"
        message += f"**Change:** {alert['change']:.2f}%\n"
        message += f"**Current Price:** {alert['current_price']:.3f}\n"
        message += f"**Previous Price:** {alert['previous_price']:.3f}\n"
        message += f"**Volume:** ${alert['volume']:,}\n"
        message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return message
    
    def format_status_report(self, report):
        """Format a status report for sending"""
        message = "**POLYMARKET STATUS REPORT**\n\n"
        message += f"**Report Time:** {report['timestamp']}\n\n"
        
        # Tariff markets
        if report['tariff_markets']:
            message += "**🎯 TARIFF MARKETS:**\n"
            for market in report['tariff_markets']:
                message += f"• {market['question'][:60]}{'...' if len(market['question']) > 60 else ''}\n"
                message += f"  Price: {market['current_price']:.3f} | Volume: ${market['volume']:,}\n"
            message += "\n"
        
        # Biggest movers
        if report['biggest_movers']:
            message += "**📈 BIGGEST MOVERS (Last 30 min):**\n"
            for mover in report['biggest_movers']:
                message += f"• {mover['market'][:60]}{'...' if len(mover['market']) > 60 else ''}\n"
                message += f"  Change: {mover['change']:.2f}% | Volume: ${mover['volume']:,}\n"
            message += "\n"
        
        # New high volume markets
        if report['new_high_volume']:
            message += "**💰 NEW HIGH-VOLUME MARKETS:**\n"
            for market in report['new_high_volume']:
                message += f"• {market['question'][:60]}{'...' if len(market['question']) > 60 else ''}\n"
                message += f"  Volume: ${market['volume']:,}\n"
        
        return message

def main():
    monitor = PolymarketMonitor()
    print("Starting Polymarket Continuous Monitor...")
    
    # Initial data fetch to identify focus markets
    print("Fetching initial market data...")
    initial_data = monitor.fetch_markets(limit=200)
    if initial_data:
        focus_markets = monitor.identify_focus_markets(initial_data)
        print(f"Identified {len(focus_markets['tariff'])} tariff markets")
        print(f"Identified {len(focus_markets['deportation'])} deportation markets")
        print(f"Identified {len(focus_markets['high_volume'])} high-volume markets")
        print(f"Identified {len(focus_markets['ending_soon'])} markets ending soon")
    else:
        print("Failed to fetch initial data")
        return
    
    # Monitoring loop
    cycle_count = 0
    while True:
        try:
            current_time = datetime.now()
            print(f"\nMonitoring cycle {cycle_count + 1} - {current_time.strftime('%H:%M:%S')}")
            
            # Fetch current market data
            market_data = monitor.fetch_markets(limit=200)
            if not market_data:
                print("Failed to fetch market data")
                time.sleep(300)  # Wait 5 minutes on error
                continue
            
            # Identify focus markets
            focus_markets = monitor.identify_focus_markets(market_data)
            
            # Check for alerts (every 5 minutes)
            alerts = monitor.check_alerts(focus_markets)
            for alert in alerts:
                alert_message = monitor.format_alert_message(alert)
                print(f"\n{alert_message}")
                # In actual implementation, this would send to main session
                print(f"ALERT: {alert['type']} - {alert['change']:.2f}% change detected")
            
            # Generate and send status report (every 30 minutes)
            if cycle_count % 6 == 0:  # 6 cycles * 5 minutes = 30 minutes
                report = monitor.generate_status_report(focus_markets)
                report_message = monitor.format_status_report(report)
                print(f"\n{report_message}")
                print("Status report generated and sent")
            
            cycle_count += 1
            
            # Wait 5 minutes before next cycle
            print(f"Waiting 5 minutes for next cycle...")
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            break
        except Exception as e:
            print(f"Error in monitoring cycle: {e}")
            time.sleep(300)  # Wait 5 minutes on error

if __name__ == "__main__":
    main()