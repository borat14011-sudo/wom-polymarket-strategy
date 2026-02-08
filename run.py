#!/usr/bin/env python3
"""
Polymarket Live Market Data System - Quick Start
One-command execution for Wom's trading operation
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_apis():
    """Run API endpoint tests"""
    print("\n" + "="*80)
    print("🧪 TESTING POLYMARKET API ENDPOINTS")
    print("="*80)
    
    from test_apis import PolymarketTester
    
    async with PolymarketTester() as tester:
        await tester.run_all_tests()
    
    print("\n✓ API testing complete")
    print("Check api_test_results.json for detailed results")

async def scrape_markets(output_file: str = None):
    """Scrape current markets from Polymarket website"""
    print("\n" + "="*80)
    print("🔍 SCRAPING LIVE MARKET DATA FROM POLYMARKET.COM")
    print("="*80)
    
    from web_scraper import PolymarketWebScraper
    
    async with PolymarketWebScraper() as scraper:
        # Scrape all markets
        all_markets = await scraper.scrape_all_markets()
        
        if not all_markets:
            print("\n❌ No markets found via simple scraping")
            print("Trying browser automation...")
            return await scrape_with_browser(output_file)
        
        # Filter for 2025 markets
        markets_2025 = scraper.filter_2025_markets(all_markets)
        
        # Save results
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"polymarket_2025_{timestamp}.json"
        
        await scraper.save_to_json(markets_2025, output_file)
        
        # Display summary
        print(f"\n✓ Scraped {len(all_markets)} total markets")
        print(f"✓ Found {len(markets_2025)} 2025 markets")
        print(f"✓ Saved to: {output_file}")
        
        # Show top markets
        if markets_2025:
            print("\n🏆 TOP 2025 MARKETS BY VOLUME:")
            sorted_markets = sorted(
                markets_2025,
                key=lambda x: float(x.get('volume', 0)),
                reverse=True
            )[:10]
            
            for i, market in enumerate(sorted_markets, 1):
                volume = float(market.get('volume', 0))
                title = market.get('title', 'Unknown')[:60]
                print(f"{i:2d}. ${volume:>12,.0f} | {title}")
        
        return markets_2025

async def scrape_with_browser(output_file: str = None):
    """Scrape markets using browser automation"""
    print("\n" + "="*80)
    print("🌐 USING BROWSER AUTOMATION FOR JAVASCRIPT RENDERED CONTENT")
    print("="*80)
    
    from browser_automation import PolymarketBrowserAutomation
    
    automation = PolymarketBrowserAutomation()
    
    try:
        markets = await automation.fetch_markets_via_browser()
        
        if markets:
            # Filter for 2025
            markets_2025 = [m for m in markets if '2025' in str(m.get('title', '')).lower()]
            
            # Save
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f"polymarket_2025_browser_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(markets_2025, f, indent=2)
            
            print(f"\n✓ Extracted {len(markets)} markets via browser")
            print(f"✓ Found {len(markets_2025)} 2025 markets")
            print(f"✓ Saved to: {output_file}")
            
            return markets_2025
        else:
            print("\n❌ No markets extracted via browser")
            return []
            
    finally:
        await automation.close()

async def start_monitoring(interval: int = 60, duration: int = None):
    """Start live monitoring system"""
    print("\n" + "="*80)
    print("📊 STARTING LIVE MARKET MONITORING SYSTEM")
    print("="*80)
    
    from polymarket_monitor import MarketMonitor
    
    monitor = MarketMonitor(check_interval=interval)
    await monitor.initialize()
    await monitor.run_monitoring(duration_minutes=duration)

async def run_full_system():
    """Run complete system: test, scrape, and monitor"""
    print("\n" + "="*80)
    print("🚀 POLYMARKET LIVE DATA SYSTEM - FULL EXECUTION")
    print("="*80)
    print("\nThis will:")
    print("  1. Test all available API endpoints")
    print("  2. Scrape current market data from website")
    print("  3. Start live monitoring system")
    print("="*80)
    
    # Step 1: Test APIs
    await test_apis()
    
    # Step 2: Scrape markets
    markets = await scrape_markets()
    
    # Step 3: Start monitoring (if markets found)
    if markets:
        print("\n✓ Markets found! Starting monitoring system...")
        await start_monitoring(interval=60, duration=None)
    else:
        print("\n⚠️ No markets found. Starting monitoring with browser automation...")
        await start_monitoring(interval=60, duration=None)

def print_help():
    """Print help information"""
    help_text = """
╔═══════════════════════════════════════════════════════════════════════════╗
║           POLYMARKET LIVE MARKET DATA SYSTEM - QUICK START               ║
╚═══════════════════════════════════════════════════════════════════════════╝

USAGE:
    python run.py [command] [options]

COMMANDS:
    test         Test all API endpoints and report status
    scrape       Scrape current market data from polymarket.com
    monitor      Start live monitoring system
    full         Run complete system (test + scrape + monitor)
    browser      Use browser automation to extract markets
    help         Show this help message

OPTIONS:
    --interval N    Monitoring check interval in seconds (default: 60)
    --duration N    Monitoring duration in minutes (default: unlimited)
    --output FILE   Output file for scraped data

EXAMPLES:
    # Test all APIs
    python run.py test

    # Scrape markets and save to file
    python run.py scrape --output my_markets.json

    # Start monitoring with 30-second intervals
    python run.py monitor --interval 30

    # Monitor for 2 hours
    python run.py monitor --duration 120

    # Run everything
    python run.py full

    # Use browser automation
    python run.py browser

FILES CREATED:
    - api_test_results.json    API endpoint test results
    - polymarket_2025_*.json   Scraped market data
    - market_data/             Directory for monitoring data
    - market_history/          Historical price data
    - alerts/                  Generated alerts

For Wom's trading operation, use: python run.py full
"""
    print(help_text)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Polymarket Live Market Data System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'command',
        choices=['test', 'scrape', 'monitor', 'full', 'browser', 'help'],
        help='Command to execute'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Monitoring check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        help='Monitoring duration in minutes (default: unlimited)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for scraped data'
    )
    
    args = parser.parse_args()
    
    if args.command == 'help':
        print_help()
        return
    
    # Run appropriate command
    if args.command == 'test':
        asyncio.run(test_apis())
    elif args.command == 'scrape':
        asyncio.run(scrape_markets(args.output))
    elif args.command == 'browser':
        asyncio.run(scrape_with_browser(args.output))
    elif args.command == 'monitor':
        asyncio.run(start_monitoring(args.interval, args.duration))
    elif args.command == 'full':
        asyncio.run(run_full_system())

if __name__ == "__main__":
    import json
    main()