#!/usr/bin/env python3
"""
Scrape all resolved Polymarket markets from October 2025
Uses CLOB API, Gamma API, and web scraping to get complete data
"""

import requests
import json
import csv
from datetime import datetime, timezone
from typing import List, Dict
import time

class PolymarketScraper:
    def __init__(self):
        self.clob_base = "https://clob.polymarket.com"
        self.gamma_base = "https://gamma-api.polymarket.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def fetch_markets_gamma(self, limit=100, offset=0, closed=True):
        """Fetch markets from Gamma API"""
        url = f"{self.gamma_base}/markets"
        params = {
            'limit': limit,
            'offset': offset,
            'closed': 'true' if closed else 'false',
            'order': 'volume24hr',
            'ascending': 'false'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching from Gamma API: {e}")
            return None
    
    def fetch_market_details_clob(self, condition_id):
        """Fetch detailed market info from CLOB API"""
        url = f"{self.clob_base}/markets/{condition_id}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching CLOB details for {condition_id}: {e}")
            return None
    
    def is_october_2025(self, timestamp):
        """Check if a timestamp is in October 2025"""
        if not timestamp:
            return False
        
        try:
            # Handle both Unix timestamps and ISO strings
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            
            return dt.year == 2025 and dt.month == 10
        except Exception as e:
            print(f"Error parsing timestamp {timestamp}: {e}")
            return False
    
    def extract_market_data(self, market):
        """Extract relevant fields from market data"""
        try:
            # Get resolution timestamp
            end_date = market.get('endDate') or market.get('end_date_iso') or market.get('resolvedAt')
            
            # Determine outcome
            outcome = None
            outcome_prices = market.get('outcomePrices', [])
            
            if market.get('closed') or market.get('resolved'):
                # Try to determine winner from various fields
                if 'resolvedOutcome' in market:
                    outcome = market['resolvedOutcome']
                elif 'outcome' in market:
                    outcome = market['outcome']
                elif len(outcome_prices) == 2:
                    # If YES price is 1.0 or close to it, YES won
                    if outcome_prices[0] and float(outcome_prices[0]) > 0.95:
                        outcome = "YES"
                    elif outcome_prices[1] and float(outcome_prices[1]) > 0.95:
                        outcome = "NO"
            
            data = {
                'question': market.get('question', ''),
                'outcome': outcome,
                'category': market.get('groupItemTitle', '') or market.get('category', ''),
                'resolution_date': end_date,
                'volume': market.get('volume', 0) or market.get('volume24hr', 0),
                'market_id': market.get('conditionId', '') or market.get('id', ''),
                'closed': market.get('closed', False),
                'resolved': market.get('resolved', False)
            }
            
            return data
        except Exception as e:
            print(f"Error extracting market data: {e}")
            return None
    
    def scrape_october_2025_markets(self):
        """Main scraping function"""
        all_markets = []
        offset = 0
        limit = 100
        
        print("Starting to fetch markets from Gamma API...")
        
        # Fetch markets in batches
        while len(all_markets) < 500:  # Fetch more than needed to filter
            print(f"Fetching batch at offset {offset}...")
            
            data = self.fetch_markets_gamma(limit=limit, offset=offset, closed=True)
            
            if not data:
                print("No data returned, stopping...")
                break
            
            markets = data if isinstance(data, list) else data.get('data', [])
            
            if not markets:
                print("No more markets found")
                break
            
            for market in markets:
                market_data = self.extract_market_data(market)
                
                if market_data and self.is_october_2025(market_data['resolution_date']):
                    print(f"Found October 2025 market: {market_data['question'][:60]}...")
                    all_markets.append(market_data)
            
            offset += limit
            time.sleep(0.5)  # Rate limiting
            
            # If we haven't found any Oct 2025 markets in last batch, might be done
            if len(all_markets) == 0 and offset > 1000:
                print("No October 2025 markets found in first 1000 results")
                break
        
        print(f"\nTotal October 2025 markets found: {len(all_markets)}")
        return all_markets
    
    def save_to_csv(self, markets, filename='oct_2025_resolved.csv'):
        """Save markets to CSV"""
        if not markets:
            print("No markets to save!")
            return
        
        fieldnames = ['question', 'outcome', 'category', 'resolution_date', 'volume', 'market_id']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for market in markets:
                row = {k: market.get(k, '') for k in fieldnames}
                writer.writerow(row)
        
        print(f"Saved {len(markets)} markets to {filename}")

if __name__ == "__main__":
    scraper = PolymarketScraper()
    
    print("=" * 60)
    print("POLYMARKET OCTOBER 2025 RESOLVED MARKETS SCRAPER")
    print("=" * 60)
    print()
    
    markets = scraper.scrape_october_2025_markets()
    
    if markets:
        scraper.save_to_csv(markets)
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total markets collected: {len(markets)}")
        print(f"Markets with outcomes: {sum(1 for m in markets if m.get('outcome'))}")
        print(f"Categories: {len(set(m.get('category', 'Unknown') for m in markets))}")
        
        # Show sample
        print("\nSample markets:")
        for i, m in enumerate(markets[:5], 1):
            print(f"\n{i}. {m['question'][:70]}...")
            print(f"   Outcome: {m.get('outcome', 'Unknown')}")
            print(f"   Category: {m.get('category', 'Unknown')}")
            print(f"   Volume: ${m.get('volume', 0):,.0f}")
    else:
        print("\nNo markets found! Check if October 2025 markets exist yet.")
