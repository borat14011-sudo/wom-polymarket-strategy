#!/usr/bin/env python3
"""
Kalshi Real-Time Market Monitor
Continuously monitors Kalshi markets and identifies opportunities
"""

import json
import datetime
import time
import csv
import os
from typing import List, Dict, Any

class KalshiMarketMonitor:
    def __init__(self, data_file: str = 'kalshi_markets_raw.json'):
        self.data_file = data_file
        self.last_update = None
        self.market_data = []
        
    def load_data(self) -> bool:
        """Load market data from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8-sig') as f:
                self.market_data = json.load(f)
            self.last_update = datetime.datetime.now()
            print(f"[OK] Loaded {len(self.market_data)} markets from {self.data_file}")
            return True
        except Exception as e:
            print(f"[ERROR] Error loading data: {e}")
            return False
    
    def analyze_markets(self) -> Dict[str, Any]:
        """Analyze all active markets and calculate opportunities"""
        if not self.market_data:
            return {}
        
        current_date = datetime.datetime.now(datetime.timezone.utc)
        opportunities = {
            'top_yes': [],
            'top_no': [],
            'high_volume': [],
            'recent_dips': [],
            'near_term': []
        }
        
        for market in self.market_data:
            if market.get('status') != 'active':
                continue
            
            # Get prices
            yes_ask = market.get('yes_ask')
            yes_bid = market.get('yes_bid')
            if yes_ask is None or yes_bid is None:
                continue
            
            # Calculate metrics
            no_ask = 100 - yes_ask
            no_bid = 100 - yes_bid
            
            # Expected values (after 2% fee)
            ev_yes = ((100 - yes_ask) / yes_ask * 0.98) * 100 if yes_ask > 0 else 0
            ev_no = ((100 - no_ask) / no_ask * 0.98) * 100 if no_ask > 0 else 0
            
            # Volume in dollars
            volume_dollars = market.get('volume', 0) * 0.01
            
            # Days to resolution
            days_to_resolution = None
            close_date_str = market.get('close_date')
            if close_date_str:
                try:
                    close_date = datetime.datetime.fromisoformat(close_date_str.replace('Z', '+00:00'))
                    days_to_resolution = (close_date - current_date).days
                except:
                    pass
            
            market_info = {
                'ticker': market['ticker_name'],
                'title': market['title'],
                'category': market.get('category', ''),
                'yes_ask': yes_ask,
                'yes_bid': yes_bid,
                'no_ask': no_ask,
                'no_bid': no_bid,
                'ev_yes': ev_yes,
                'ev_no': ev_no,
                'volume': volume_dollars,
                'days_to_resolution': days_to_resolution,
                'daily_change': market.get('daily_change_pct', 0),
                'weekly_change': market.get('weekly_change_pct', 0)
            }
            
            # Categorize opportunities
            if ev_yes > 100:  # >100% expected return
                opportunities['top_yes'].append(market_info)
            
            if ev_no > 100:  # >100% expected return
                opportunities['top_no'].append(market_info)
            
            if volume_dollars > 1000:  # High volume
                opportunities['high_volume'].append(market_info)
            
            if market.get('daily_change_pct', 0) < -10:  # >10% daily drop
                opportunities['recent_dips'].append(market_info)
            
            if days_to_resolution and days_to_resolution < 30:  # Near-term resolution
                opportunities['near_term'].append(market_info)
        
        # Sort each category
        opportunities['top_yes'].sort(key=lambda x: x['ev_yes'], reverse=True)
        opportunities['top_no'].sort(key=lambda x: x['ev_no'], reverse=True)
        opportunities['high_volume'].sort(key=lambda x: x['volume'], reverse=True)
        opportunities['recent_dips'].sort(key=lambda x: x['daily_change'])
        opportunities['near_term'].sort(key=lambda x: x['days_to_resolution'])
        
        return opportunities
    
    def generate_report(self, opportunities: Dict[str, List]) -> str:
        """Generate a formatted report"""
        report = []
        report.append("=" * 80)
        report.append("KALSHI REAL-TIME MARKET MONITOR")
        report.append(f"Last Update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        
        # Top YES opportunities
        if opportunities['top_yes']:
            report.append("\n>>> TOP 5 YES OPPORTUNITIES (Highest Expected Value)")
            for i, opp in enumerate(opportunities['top_yes'][:5]):
                report.append(f"{i+1}. {opp['ticker']}")
                report.append(f"   {opp['title'][:70]}...")
                report.append(f"   YES: {opp['yes_ask']}c -> EV: {opp['ev_yes']:.0f}% | NO: {opp['no_ask']}c")
                report.append(f"   Vol: ${opp['volume']:.0f} | Days: {opp['days_to_resolution']}")
        
        # Top NO opportunities
        if opportunities['top_no']:
            report.append("\n>>> TOP 5 NO OPPORTUNITIES (Highest Expected Value)")
            for i, opp in enumerate(opportunities['top_no'][:5]):
                report.append(f"{i+1}. {opp['ticker']}")
                report.append(f"   {opp['title'][:70]}...")
                report.append(f"   NO: {opp['no_ask']}c -> EV: {opp['ev_no']:.0f}% | YES: {opp['yes_ask']}c")
                report.append(f"   Vol: ${opp['volume']:.0f} | Days: {opp['days_to_resolution']}")
        
        # High volume markets
        if opportunities['high_volume']:
            report.append("\n>>> TOP 5 HIGH VOLUME MARKETS")
            for i, opp in enumerate(opportunities['high_volume'][:5]):
                report.append(f"{i+1}. {opp['ticker']}: ${opp['volume']:.0f}")
                report.append(f"   {opp['title'][:70]}...")
        
        # Recent dips
        if opportunities['recent_dips']:
            report.append("\n>>> RECENT PRICE DIPS (>10% Daily Drop)")
            for i, opp in enumerate(opportunities['recent_dips'][:5]):
                report.append(f"{i+1}. {opp['ticker']}: {opp['daily_change']:.1f}% drop")
                report.append(f"   {opp['title'][:70]}...")
        
        # Near-term resolutions
        if opportunities['near_term']:
            report.append("\n>>> NEAR-TERM MARKETS (<30 days to resolution)")
            for i, opp in enumerate(opportunities['near_term'][:5]):
                report.append(f"{i+1}. {opp['ticker']}: {opp['days_to_resolution']} days")
                report.append(f"   {opp['title'][:70]}...")
                report.append(f"   YES: {opp['yes_ask']}c | NO: {opp['no_ask']}c")
        
        # Summary statistics
        total_active = sum(1 for m in self.market_data if m.get('status') == 'active')
        report.append("\n" + "=" * 80)
        report.append("SUMMARY STATISTICS")
        report.append(f"Total Active Markets: {total_active}")
        report.append(f"Top YES Opportunities: {len(opportunities['top_yes'])}")
        report.append(f"Top NO Opportunities: {len(opportunities['top_no'])}")
        report.append(f"High Volume Markets: {len(opportunities['high_volume'])}")
        report.append(f"Recent Dips: {len(opportunities['recent_dips'])}")
        report.append(f"Near-Term Markets: {len(opportunities['near_term'])}")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_opportunities_csv(self, opportunities: Dict[str, List], filename: str = 'kalshi_opportunities.csv'):
        """Save opportunities to CSV file"""
        all_opps = []
        for category, opp_list in opportunities.items():
            for opp in opp_list:
                opp['category_type'] = category
                all_opps.append(opp)
        
        if all_opps:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ticker', 'title', 'category', 'category_type', 'yes_ask', 'yes_bid', 
                            'no_ask', 'no_bid', 'ev_yes', 'ev_no', 'volume', 'days_to_resolution',
                            'daily_change', 'weekly_change']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_opps)
            print(f"[OK] Saved {len(all_opps)} opportunities to {filename}")
    
    def run_monitor_cycle(self):
        """Run one monitoring cycle"""
        print(f"\n{'='*60}")
        print(f"Monitoring Cycle: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        if self.load_data():
            opportunities = self.analyze_markets()
            report = self.generate_report(opportunities)
            print(report)
            
            # Save to file
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            self.save_opportunities_csv(opportunities, f'kalshi_opportunities_{timestamp}.csv')
            
            # Save report
            with open(f'kalshi_report_{timestamp}.txt', 'w', encoding='utf-8') as f:
                f.write(report)
            
            return opportunities
        return None

def main():
    """Main function for continuous monitoring"""
    monitor = KalshiMarketMonitor()
    
    print("Starting Kalshi Real-Time Market Monitor")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            monitor.run_monitor_cycle()
            print(f"\nNext update in 60 seconds...")
            time.sleep(60)  # Wait 60 seconds between updates
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"\nError in monitoring: {e}")

if __name__ == "__main__":
    # Run one cycle for testing
    monitor = KalshiMarketMonitor()
    if monitor.load_data():
        opportunities = monitor.analyze_markets()
        report = monitor.generate_report(opportunities)
        print(report)
        
        # Save files
        monitor.save_opportunities_csv(opportunities)
        with open('kalshi_latest_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("\n[OK] Analysis complete. Files saved:")
        print("  - kalshi_opportunities.csv")
        print("  - kalshi_latest_report.txt")
    else:
        print("Failed to load market data")