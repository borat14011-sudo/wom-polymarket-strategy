#!/usr/bin/env python3
"""
Polymarket Historical Data Scraper
Collects real historical data from resolved markets (2024-2026)
- Final outcomes (YES/NO winners)
- Historical price snapshots
- Volume data
"""

import requests
import json
import csv
import time
from datetime import datetime, timezone
from typing import List, Dict, Any
import os

# API Endpoints
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
DATA_API = "https://data-api.polymarket.com"

class PolymarketScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.all_markets_data = []
        
    def get_resolved_events(self, limit=100, offset=0):
        """Fetch resolved (closed) events from Gamma API"""
        url = f"{GAMMA_API}/events"
        params = {
            'closed': 'true',
            'limit': limit,
            'offset': offset,
            'order': 'id',
            'ascending': 'false'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching events (offset {offset}): {e}")
            return []
    
    def get_market_details(self, market_id):
        """Fetch detailed market information"""
        url = f"{GAMMA_API}/markets/{market_id}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching market {market_id}: {e}")
            return None
    
    def get_market_trades(self, market_id, limit=1000):
        """Fetch trade history for volume calculation"""
        url = f"{CLOB_API}/trades"
        params = {
            'market': market_id,
            'limit': limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching trades for market {market_id}: {e}")
            return []
    
    def parse_outcomes(self, outcomes_str):
        """Parse outcomes JSON string"""
        try:
            return json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
        except:
            return []
    
    def parse_prices(self, prices_str):
        """Parse outcome prices JSON string"""
        try:
            return json.loads(prices_str) if isinstance(prices_str, str) else prices_str
        except:
            return []
    
    def determine_winner(self, market):
        """Determine which outcome won based on final prices or other indicators"""
        # In Polymarket, winning shares resolve to $1.00
        # We can check the final outcome prices or use 'winner' field if available
        
        if 'winner' in market and market['winner']:
            return market['winner']
        
        # Check if there's a resolvedOutcome
        if 'resolvedOutcome' in market and market['resolvedOutcome']:
            return market['resolvedOutcome']
        
        # Parse outcomes and final prices
        outcomes = self.parse_outcomes(market.get('outcomes', '[]'))
        prices = self.parse_prices(market.get('outcomePrices', '[]'))
        
        if not outcomes or not prices or len(outcomes) != len(prices):
            return None
        
        # The outcome with price closest to 1.00 is likely the winner
        max_price_idx = 0
        max_price = float(prices[0])
        
        for i, price in enumerate(prices):
            if float(price) > max_price:
                max_price = float(price)
                max_price_idx = i
        
        # If price is very close to 1.00, it's likely the winner
        if max_price >= 0.95:
            return outcomes[max_price_idx]
        
        return None
    
    def calculate_volume(self, trades):
        """Calculate total volume from trades"""
        if not trades:
            return 0.0
        
        total_volume = 0.0
        for trade in trades:
            # Volume is typically size * price
            try:
                size = float(trade.get('size', 0))
                price = float(trade.get('price', 0))
                total_volume += size * price
            except:
                continue
        
        return total_volume
    
    def extract_market_data(self, event):
        """Extract and structure data from an event and its markets"""
        markets_data = []
        
        event_id = event.get('id')
        event_title = event.get('title', 'Unknown')
        event_slug = event.get('slug', '')
        event_description = event.get('description', '')
        event_end_date = event.get('endDate')
        event_closed = event.get('closed', False)
        
        # Parse markets within the event
        markets = event.get('markets', [])
        
        for market in markets:
            market_id = market.get('id')
            condition_id = market.get('conditionId')
            question = market.get('question', event_title)
            
            # Get outcomes and prices
            outcomes = self.parse_outcomes(market.get('outcomes', '[]'))
            final_prices = self.parse_prices(market.get('outcomePrices', '[]'))
            
            # Determine winner
            winner = self.determine_winner(market)
            
            # Get token IDs for price history
            clob_token_ids = market.get('clobTokenIds', [])
            
            # Fetch trade data for volume (if available)
            # Note: This might not work without proper market address
            # volume_usd = 0.0
            # if condition_id:
            #     trades = self.get_market_trades(condition_id)
            #     volume_usd = self.calculate_volume(trades)
            
            # Use volume from market metadata if available
            volume_usd = market.get('volume', 0.0)
            volume_num = market.get('volumeNum', 0.0)
            
            market_data = {
                'event_id': event_id,
                'event_title': event_title,
                'event_slug': event_slug,
                'event_end_date': event_end_date,
                'market_id': market_id,
                'condition_id': condition_id,
                'question': question,
                'outcomes': '|'.join(outcomes) if outcomes else '',
                'final_prices': '|'.join(map(str, final_prices)) if final_prices else '',
                'winner': winner,
                'closed': event_closed,
                'volume_usd': volume_usd,
                'volume_num': volume_num,
                'clob_token_ids': '|'.join(clob_token_ids) if clob_token_ids else '',
                'description': event_description[:200] if event_description else '',
                'created_time': datetime.now(timezone.utc).isoformat()
            }
            
            markets_data.append(market_data)
        
        return markets_data
    
    def scrape_resolved_markets(self, target_count=100, max_requests=50):
        """Main scraping function to collect resolved markets"""
        print(f"Starting scrape for {target_count}+ resolved markets...")
        print("=" * 80)
        
        offset = 0
        limit = 100  # Max per request
        total_markets = 0
        request_count = 0
        
        while total_markets < target_count and request_count < max_requests:
            print(f"\nFetching events: offset={offset}, limit={limit}")
            
            events = self.get_resolved_events(limit=limit, offset=offset)
            
            if not events:
                print("No more events found.")
                break
            
            print(f"Retrieved {len(events)} events")
            
            for i, event in enumerate(events):
                event_title = event.get('title', 'Unknown')
                event_id = event.get('id')
                event_date = event.get('endDate', 'N/A')
                
                print(f"  [{i+1}/{len(events)}] Processing: {event_title[:60]}... (ID: {event_id})")
                
                # Extract market data from this event
                markets = self.extract_market_data(event)
                
                if markets:
                    self.all_markets_data.extend(markets)
                    total_markets += len(markets)
                    print(f"    → Extracted {len(markets)} market(s). Total: {total_markets}")
                
                # Rate limiting
                time.sleep(0.1)
            
            offset += limit
            request_count += 1
            
            # Pause between batch requests
            if events and len(events) == limit:
                print(f"\nPausing before next batch...")
                time.sleep(1)
            else:
                print(f"\nReceived fewer events than limit - likely reached the end.")
                break
        
        print("\n" + "=" * 80)
        print(f"Scraping complete! Collected {total_markets} markets from {len(self.all_markets_data)} total entries")
        return self.all_markets_data
    
    def save_to_csv(self, filename='polymarket_resolved_markets.csv'):
        """Save collected data to CSV"""
        if not self.all_markets_data:
            print("No data to save!")
            return
        
        fieldnames = [
            'event_id', 'event_title', 'event_slug', 'event_end_date',
            'market_id', 'condition_id', 'question', 'outcomes', 
            'final_prices', 'winner', 'closed', 'volume_usd', 'volume_num',
            'clob_token_ids', 'description', 'created_time'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.all_markets_data)
        
        print(f"✓ Data saved to {filename}")
    
    def save_to_json(self, filename='polymarket_resolved_markets.json'):
        """Save collected data to JSON"""
        if not self.all_markets_data:
            print("No data to save!")
            return
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.all_markets_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✓ Data saved to {filename}")
    
    def print_summary(self):
        """Print summary statistics"""
        if not self.all_markets_data:
            print("No data collected!")
            return
        
        print("\n" + "=" * 80)
        print("DATA SUMMARY")
        print("=" * 80)
        print(f"Total markets collected: {len(self.all_markets_data)}")
        
        # Count markets with winners determined
        with_winners = sum(1 for m in self.all_markets_data if m['winner'])
        print(f"Markets with determined winners: {with_winners}")
        
        # Count markets with volume data
        with_volume = sum(1 for m in self.all_markets_data if float(m.get('volume_usd', 0)) > 0)
        print(f"Markets with volume data: {with_volume}")
        
        # Sample of outcomes
        print("\nSample of collected markets:")
        for i, market in enumerate(self.all_markets_data[:5]):
            print(f"\n{i+1}. {market['question'][:70]}")
            print(f"   Winner: {market['winner']}")
            print(f"   Outcomes: {market['outcomes']}")
            print(f"   Final Prices: {market['final_prices']}")
            print(f"   Volume: ${market.get('volume_usd', 0):,.2f}")

def main():
    scraper = PolymarketScraper()
    
    # Scrape resolved markets
    # Target 100+ markets, allow up to 50 API requests
    scraper.scrape_resolved_markets(target_count=100, max_requests=20)
    
    # Print summary
    scraper.print_summary()
    
    # Save to both CSV and JSON
    scraper.save_to_csv()
    scraper.save_to_json()
    
    print("\n" + "=" * 80)
    print("Scraping complete! Files saved:")
    print("  - polymarket_resolved_markets.csv")
    print("  - polymarket_resolved_markets.json")
    print("=" * 80)

if __name__ == "__main__":
    main()
