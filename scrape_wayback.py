"""
Wayback Machine Price History Scraper
Downloads archived Polymarket market pages and extracts price data
"""

import requests
import json
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
import csv
import os

class WaybackScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.snapshots_found = 0
        self.prices_extracted = 0
        
    def get_wayback_snapshots(self, market_slug, from_date='20251001', to_date='20260228'):
        """
        Query Wayback Machine CDX API for snapshots of a market page
        
        Args:
            market_slug: Polymarket market slug (e.g., "will-trump-win-2024")
            from_date: Start date in YYYYMMDD format
            to_date: End date in YYYYMMDD format
            
        Returns:
            List of snapshot dictionaries with timestamp and URL
        """
        print(f"🔍 Searching Wayback Machine for: {market_slug}")
        
        cdx_url = "http://web.archive.org/cdx/search/cdx"
        params = {
            'url': f'polymarket.com/event/{market_slug}',
            'output': 'json',
            'from': from_date,
            'to': to_date,
            'filter': 'statuscode:200',
            'collapse': 'timestamp:8'  # One snapshot per 8-hour window
        }
        
        try:
            response = self.session.get(cdx_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if len(data) <= 1:  # Only header or empty
                print(f"  ⚠️ No snapshots found")
                return []
            
            snapshots = []
            for row in data[1:]:  # Skip header row
                timestamp_str = row[1]  # YYYYMMDDHHmmss format
                url = row[2]
                
                # Parse timestamp
                dt = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
                
                snapshots.append({
                    'timestamp': timestamp_str,
                    'datetime': dt,
                    'url': f"http://web.archive.org/web/{timestamp_str}/{url}"
                })
            
            self.snapshots_found += len(snapshots)
            print(f"  ✅ Found {len(snapshots)} snapshots")
            return snapshots
            
        except Exception as e:
            print(f"  ❌ Error querying CDX API: {e}")
            return []
    
    def extract_price_from_snapshot(self, snapshot_url):
        """
        Download a Wayback snapshot and extract price data
        
        Returns:
            dict with timestamp, yes_price, volume or None if extraction fails
        """
        try:
            print(f"  📥 Fetching {snapshot_url}")
            response = self.session.get(snapshot_url, timeout=60)
            response.raise_for_status()
            html = response.text
            
            # Try multiple extraction methods
            price_data = None
            
            # Method 1: Look for __NEXT_DATA__ JSON (Next.js apps)
            next_data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', 
                                       html, re.DOTALL)
            if next_data_match:
                try:
                    next_data = json.loads(next_data_match.group(1))
                    # Navigate through Next.js data structure to find market data
                    props = next_data.get('props', {})
                    page_props = props.get('pageProps', {})
                    market = page_props.get('market', {})
                    
                    if market:
                        yes_price = float(market.get('outcomePrices', ['0', '0'])[0])
                        volume = float(market.get('volume', 0))
                        
                        price_data = {
                            'yes_price': yes_price,
                            'volume': volume
                        }
                        print(f"    ✅ Extracted from __NEXT_DATA__: price={yes_price:.3f}, volume={volume:,.0f}")
                except Exception as e:
                    print(f"    ⚠️ Could not parse __NEXT_DATA__: {e}")
            
            # Method 2: Look for API response data in script tags
            if not price_data:
                api_data_patterns = [
                    r'"outcomePrices"\s*:\s*\["([\d.]+)"\s*,\s*"[\d.]+"\]',
                    r'"volume"\s*:\s*"([\d.]+)"',
                    r'price.*?(\d+\.\d{2,})',
                ]
                
                for pattern in api_data_patterns:
                    matches = re.findall(pattern, html)
                    if matches:
                        print(f"    Found potential price data with regex")
                        # This would need more sophisticated parsing
                        # For now, mark as found but needing manual review
            
            # Method 3: Parse visible HTML elements
            if not price_data:
                soup = BeautifulSoup(html, 'html.parser')
                # Look for common price display patterns
                # This is market-specific and would need to be tuned
                
            if price_data:
                self.prices_extracted += 1
                return price_data
            else:
                print(f"    ❌ Could not extract price data")
                return None
                
        except Exception as e:
            print(f"    ❌ Error fetching snapshot: {e}")
            return None
    
    def scrape_market(self, market_slug, market_id=None, output_file=None):
        """
        Scrape all available snapshots for a market
        
        Args:
            market_slug: Market slug for Wayback search
            market_id: Market condition ID for output
            output_file: CSV file to append results
            
        Returns:
            List of price data dictionaries
        """
        print(f"\n{'='*70}")
        print(f"Scraping market: {market_slug}")
        print(f"{'='*70}")
        
        # Get all snapshots
        snapshots = self.get_wayback_snapshots(market_slug)
        
        if not snapshots:
            return []
        
        price_history = []
        
        # Process each snapshot (with rate limiting)
        for i, snapshot in enumerate(snapshots, 1):
            print(f"\nSnapshot {i}/{len(snapshots)} - {snapshot['datetime']}")
            
            price_data = self.extract_price_from_snapshot(snapshot['url'])
            
            if price_data:
                record = {
                    'market_id': market_id or market_slug,
                    'timestamp': snapshot['datetime'].isoformat(),
                    'yes_price': price_data['yes_price'],
                    'volume': price_data['volume']
                }
                price_history.append(record)
                
                # Append to CSV immediately (incremental save)
                if output_file:
                    file_exists = os.path.exists(output_file)
                    with open(output_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=['market_id', 'timestamp', 'yes_price', 'volume'])
                        if not file_exists:
                            writer.writeheader()
                        writer.writerow(record)
            
            # Rate limiting: wait 5 seconds between requests
            if i < len(snapshots):
                time.sleep(5)
        
        print(f"\n✅ Extracted {len(price_history)} price points for {market_slug}")
        return price_history

def main():
    """Test the scraper with a sample market"""
    scraper = WaybackScraper()
    
    # Test with a sample market
    # Note: Replace with actual market slug from Oct 2025 - Feb 2026
    test_markets = [
        {
            'slug': 'presidential-election-winner-2024',  # Example - adjust for actual markets
            'market_id': '0x...',
        }
    ]
    
    output_file = 'wayback_price_history.csv'
    
    print("🚀 Starting Wayback Machine scraper")
    print(f"📁 Output file: {output_file}")
    
    for market in test_markets:
        scraper.scrape_market(
            market_slug=market['slug'],
            market_id=market['market_id'],
            output_file=output_file
        )
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Snapshots found: {scraper.snapshots_found}")
    print(f"Prices extracted: {scraper.prices_extracted}")
    print(f"Output: {output_file}")

if __name__ == "__main__":
    main()
