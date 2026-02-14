import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class KalshiAPIClient:
    """Kalshi API client with retry logic and exponential backoff"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elections.kalshi.com/trade-api/v2"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def make_request(self, endpoint: str, params: Optional[Dict] = None, 
                    max_retries: int = 3, timeout: int = 30) -> Optional[Dict]:
        """Make HTTP request with exponential backoff retry logic"""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(max_retries):
            try:
                print(f"  Attempt {attempt + 1}/{max_retries}: {endpoint}")
                response = self.session.get(url, params=params, timeout=timeout)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    print(f"  Authentication failed: {response.text[:100]}")
                    return None
                elif response.status_code == 404:
                    print(f"  Endpoint not found: {endpoint}")
                    return None
                else:
                    print(f"  HTTP {response.status_code}: {response.text[:100]}")
                    
            except requests.exceptions.Timeout:
                print(f"  Timeout after {timeout} seconds")
            except requests.exceptions.ConnectionError as e:
                print(f"  Connection error: {e}")
            except requests.exceptions.RequestException as e:
                print(f"  Request failed: {type(e).__name__}")
            
            # Exponential backoff
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1, 2, 4 seconds
                print(f"  Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        print(f"  All retries exhausted for {endpoint}")
        return None
    
    def get_markets(self, limit: int = 100, cursor: Optional[str] = None) -> Optional[Dict]:
        """Get markets with pagination support"""
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor
        return self.make_request("markets", params=params)
    
    def get_events(self, limit: int = 50, cursor: Optional[str] = None) -> Optional[Dict]:
        """Get events with pagination support"""
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor
        return self.make_request("events", params=params)
    
    def get_all_markets(self, max_pages: int = 10) -> List[Dict]:
        """Get all markets across multiple pages"""
        all_markets = []
        cursor = None
        page = 1
        
        while page <= max_pages:
            print(f"Fetching page {page}/{max_pages}...")
            data = self.get_markets(limit=100, cursor=cursor)
            
            if not data or 'markets' not in data:
                break
            
            markets = data.get('markets', [])
            all_markets.extend(markets)
            
            print(f"  Got {len(markets)} markets (total: {len(all_markets)})")
            
            # Check for next page
            cursor = data.get('cursor')
            if not cursor or len(markets) == 0:
                break
            
            page += 1
        
        return all_markets

class KalshiScanner:
    """Scanner for Kalshi prediction markets"""
    
    def __init__(self, api_key: str):
        self.client = KalshiAPIClient(api_key)
        self.today = datetime.now()
    
    def scan_fast_resolution_markets(self, days_window: int = 7, min_volume: int = 500):
        """Scan for markets resolving within specified days window"""
        print(f"[*] Scanning Kalshi for markets resolving within {days_window} days")
        print(f"    Date: {self.today.strftime('%Y-%m-%d %H:%M PST')}")
        print("=" * 80)
        
        # Get all markets
        print("\n[1] Fetching markets from Kalshi API...")
        markets = self.client.get_all_markets(max_pages=5)
        
        if not markets:
            print("[X] No markets retrieved from API")
            return []
        
        print(f"[+] Retrieved {len(markets)} total markets")
        
        # Filter for markets resolving within the window
        fast_markets = []
        cutoff_date = self.today + timedelta(days=days_window)
        
        for market in markets:
            try:
                # Parse close time
                close_time_str = market.get('close_time')
                if not close_time_str:
                    continue
                
                # Parse ISO format (e.g., "2026-02-28T00:00:00Z")
                close_time = datetime.fromisoformat(close_time_str.replace('Z', '+00:00'))
                close_time = close_time.replace(tzinfo=None)
                
                # Check if within window
                if close_time <= cutoff_date:
                    # Get market data
                    ticker = market.get('ticker', 'N/A')
                    title = market.get('title', 'Unknown')
                    yes_price = market.get('yes_price')
                    no_price = market.get('no_price')
                    volume = market.get('volume', 0)
                    
                    # Use yes_price if available, otherwise calculate from no_price
                    if yes_price is not None:
                        price_cents = yes_price
                    elif no_price is not None:
                        price_cents = 100 - no_price  # Convert no price to yes price
                    else:
                        continue
                    
                    # Convert to dollars
                    price_dollars = price_cents / 100.0
                    
                    # Apply filters
                    if volume >= min_volume and 20 <= price_cents <= 80:
                        days_until = (close_time - self.today).days
                        
                        # Calculate ROI
                        cost = price_dollars
                        payout = 1.00
                        profit = payout - cost
                        
                        if cost > 0:
                            roi_pct = (profit / cost) * 100
                            days_to_resolution = max(days_until, 1)
                            annualized_irr = ((1 + profit/cost) ** (365/days_to_resolution) - 1) * 100
                        else:
                            roi_pct = 0
                            annualized_irr = 0
                        
                        fast_markets.append({
                            'title': title,
                            'ticker': ticker,
                            'close_time': close_time,
                            'days_until': days_until,
                            'price_cents': price_cents,
                            'price_dollars': price_dollars,
                            'volume': volume,
                            'roi_pct': roi_pct,
                            'annualized_irr': annualized_irr,
                            'yes_price': yes_price,
                            'no_price': no_price,
                            'status': market.get('status', 'unknown'),
                            'category': market.get('category', 'unknown')
                        })
                        
            except (ValueError, TypeError, KeyError) as e:
                continue
        
        print(f"\n[2] Filtered to {len(fast_markets)} markets meeting criteria:")
        print(f"    - Resolving within {days_window} days")
        print(f"    - Volume >= {min_volume}")
        print(f"    - Price: 20-80¢")
        
        # Sort by days until close (fastest first), then by volume (highest first)
        fast_markets.sort(key=lambda x: (x['days_until'], -x['volume']))
        
        return fast_markets
    
    def generate_report(self, markets: List[Dict], output_file: str = "kalshi_scanner_report.md"):
        """Generate a markdown report from scanned markets"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Kalshi Prediction Market Scanner Report\n\n")
            f.write(f"**Scan Date:** {self.today.strftime('%Y-%m-%d %H:%M PST')}\n")
            f.write(f"**Markets Found:** {len(markets)}\n")
            f.write(f"**Resolution Window:** {self.today.date()} to {(self.today + timedelta(days=7)).date()}\n\n")
            f.write("---\n\n")
            
            if not markets:
                f.write("## No Markets Found\n\n")
                f.write("No markets found matching the criteria:\n")
                f.write("- Resolution within 7 days\n")
                f.write("- Volume > 500 contracts\n")
                f.write("- Price between 20-80¢\n\n")
                f.write("### Possible Reasons:\n")
                f.write("1. Most Kalshi markets are long-term (politics, climate)\n")
                f.write("2. Short-term markets may have already resolved\n")
                f.write("3. Current API endpoint may not include all market types\n")
                f.write("4. Need authentication for certain market categories\n")
            else:
                f.write(f"## Top {min(10, len(markets))} Opportunities\n\n")
                
                for i, market in enumerate(markets[:10], 1):
                    f.write(f"### {i}. {market['title']}\n\n")
                    f.write(f"**Ticker:** `{market['ticker']}`  \n")
                    f.write(f"**Category:** {market['category']}  \n")
                    f.write(f"**Status:** {market['status']}  \n\n")
                    
                    f.write(f"**Resolution Date:** {market['close_time'].strftime('%Y-%m-%d %H:%M UTC')}  \n")
                    f.write(f"**Days Until:** {market['days_until']} days  \n\n")
                    
                    f.write(f"**Current Price:** ${market['price_dollars']:.2f} ({market['price_cents']}¢)  \n")
                    f.write(f"**Volume:** {market['volume']:,} contracts  \n")
                    
                    if market['yes_price'] is not None:
                        f.write(f"**Yes Price:** {market['yes_price']}¢  \n")
                    if market['no_price'] is not None:
                        f.write(f"**No Price:** {market['no_price']}¢  \n")
                    
                    f.write(f"**ROI if Win:** {market['roi_pct']:.1f}%  \n")
                    f.write(f"**Annualized IRR:** {market['annualized_irr']:.0f}%  \n\n")
                    
                    f.write("---\n\n")
                
                # Summary statistics
                f.write("## Summary Statistics\n\n")
                if markets:
                    avg_price = sum(m['price_cents'] for m in markets) / len(markets)
                    avg_days = sum(m['days_until'] for m in markets) / len(markets)
                    avg_volume = sum(m['volume'] for m in markets) / len(markets)
                    avg_roi = sum(m['roi_pct'] for m in markets) / len(markets)
                    
                    f.write(f"- **Average Price:** {avg_price:.1f}¢\n")
                    f.write(f"- **Average Days to Resolution:** {avg_days:.1f} days\n")
                    f.write(f"- **Average Volume:** {avg_volume:,.0f} contracts\n")
                    f.write(f"- **Average ROI:** {avg_roi:.1f}%\n")
                    
                    # Count by category
                    categories = {}
                    for market in markets:
                        cat = market['category']
                        categories[cat] = categories.get(cat, 0) + 1
                    
                    f.write("\n**Markets by Category:**\n")
                    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                        f.write(f"- {cat}: {count} markets\n")
            
            f.write("\n## Scanner Configuration\n\n")
            f.write("- **API Endpoint:** `https://api.elections.kalshi.com/trade-api/v2`\n")
            f.write("- **Authentication:** Bearer token\n")
            f.write("- **Retry Logic:** Exponential backoff (3 retries)\n")
            f.write("- **Timeout:** 30 seconds per request\n")
            f.write("- **Pagination:** Supports cursor-based pagination\n")
        
        print(f"\n[SUCCESS] Report saved to: {output_file}")

def main():
    """Main function to run the scanner"""
    # API key from the mission
    api_key = "14a525cf-42d7-4746-8e36-30a8d9c17c96"
    
    print("=" * 80)
    print("KALSHI PREDICTION MARKET SCANNER")
    print("Fixed API Connectivity with Retry Logic")
    print("=" * 80)
    
    try:
        # Initialize scanner
        scanner = KalshiScanner(api_key)
        
        # Scan for markets
        fast_markets = scanner.scan_fast_resolution_markets(days_window=7, min_volume=500)
        
        # Display results
        if fast_markets:
            print(f"\n[SUCCESS] Found {len(fast_markets)} qualifying markets!")
            print("\nTop 5 opportunities:")
            print("-" * 80)
            
            for i, market in enumerate(fast_markets[:5], 1):
                print(f"\n{i}. {market['title'][:60]}...")
                print(f"   Ticker: {market['ticker']}")
                print(f"   Resolves: {market['close_time'].strftime('%Y-%m-%d')} ({market['days_until']} days)")
                print(f"   Price: {market['price_cents']}¢ (${market['price_dollars']:.2f})")
                print(f"   Volume: {market['volume']:,}")
                print(f"   ROI: {market['roi_pct']:.1f}% (IRR: {market['annualized_irr']:.0f}%)")
        else:
            print("\n[INFO] No qualifying markets found with current criteria.")
            print("       Try adjusting filters or check API connectivity.")
        
        # Generate report
        scanner.generate_report(fast_markets, "kalshi_scanner_fixed_report.md")
        
        print("\n" + "=" * 80)
        print("SCAN COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] Scanner failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()