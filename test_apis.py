"""
Polymarket Live Market Data System - Test Suite
Tests all available endpoints and extraction methods
"""

import asyncio
import json
import aiohttp
from datetime import datetime
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolymarketTester:
    """Comprehensive testing of all Polymarket data sources"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'working_endpoints': [],
            'failed_endpoints': [],
            'market_count': 0,
            'markets_2025': []
        }
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, name: str, url: str, method: str = 'GET', 
                           params: Dict = None, headers: Dict = None) -> Dict:
        """Test a single endpoint"""
        test_result = {
            'name': name,
            'url': url,
            'method': method,
            'status': 'pending',
            'response_time': 0,
            'status_code': None,
            'market_count': 0,
            'sample_market': None,
            'error': None
        }
        
        start_time = datetime.now()
        
        try:
            async with self.session.request(
                method, url, params=params, headers=headers, timeout=30
            ) as response:
                test_result['status_code'] = response.status
                test_result['response_time'] = (datetime.now() - start_time).total_seconds()
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        test_result['status'] = 'success'
                        
                        # Count markets
                        if isinstance(data, list):
                            test_result['market_count'] = len(data)
                            if data:
                                test_result['sample_market'] = data[0]
                        elif isinstance(data, dict):
                            if 'data' in data:
                                test_result['market_count'] = len(data['data'])
                                if data['data']:
                                    test_result['sample_market'] = data['data'][0]
                            elif 'markets' in data:
                                test_result['market_count'] = len(data['markets'])
                                if data['markets']:
                                    test_result['sample_market'] = data['markets'][0]
                        
                        self.results['working_endpoints'].append(test_result)
                        
                    except Exception as e:
                        test_result['status'] = 'parse_error'
                        test_result['error'] = str(e)
                        self.results['failed_endpoints'].append(test_result)
                else:
                    test_result['status'] = 'http_error'
                    test_result['error'] = f'HTTP {response.status}'
                    self.results['failed_endpoints'].append(test_result)
                    
        except Exception as e:
            test_result['status'] = 'connection_error'
            test_result['error'] = str(e)
            test_result['response_time'] = (datetime.now() - start_time).total_seconds()
            self.results['failed_endpoints'].append(test_result)
        
        self.results['tests'].append(test_result)
        return test_result
    
    async def run_all_tests(self):
        """Run comprehensive tests on all known endpoints"""
        logger.info("="*80)
        logger.info("POLYMARKET API ENDPOINT TESTING SUITE")
        logger.info("="*80)
        
        # Test 1: Gamma API (known working but historical data)
        logger.info("\n[1] Testing Gamma API...")
        await self.test_endpoint(
            'Gamma API - Markets',
            'https://gamma-api.polymarket.com/markets',
            params={'limit': 10}
        )
        
        # Test 2: Polymarket main API
        logger.info("\n[2] Testing Polymarket API...")
        await self.test_endpoint(
            'Polymarket API - Markets',
            'https://polymarket.com/api/markets',
            params={'limit': 10}
        )
        
        # Test 3: CLOB API
        logger.info("\n[3] Testing CLOB API...")
        await self.test_endpoint(
            'CLOB API - Markets',
            'https://clob.polymarket.com/markets',
            params={'active': 'true', 'limit': 10}
        )
        
        # Test 4: Data API
        logger.info("\n[4] Testing Data API...")
        await self.test_endpoint(
            'Data API',
            'https://data.polymarket.com/markets',
            params={'limit': 10}
        )
        
        # Test 5: Gamma API with filters
        logger.info("\n[5] Testing Gamma API with 2025 filters...")
        result = await self.test_endpoint(
            'Gamma API - Filtered',
            'https://gamma-api.polymarket.com/markets',
            params={'limit': 100, 'active': 'true'}
        )
        
        # Check for 2025 markets in this response
        if result['status'] == 'success' and result['sample_market']:
            await self.check_for_2025_markets(result['sample_market'])
        
        # Test 6: Direct market page scraping
        logger.info("\n[6] Testing direct page scraping...")
        await self.test_page_scraping()
        
        # Test 7: WebSocket (check if available)
        logger.info("\n[7] Checking WebSocket availability...")
        await self.test_websocket()
        
        # Test 8: Orderbook API
        logger.info("\n[8] Testing Orderbook API...")
        await self.test_endpoint(
            'Orderbook API',
            'https://clob.polymarket.com/orderbook/markets',
            params={'limit': 10}
        )
        
        # Print results
        self.print_results()
        
        # Save results
        await self.save_results()
    
    async def test_page_scraping(self) -> Dict:
        """Test scraping the main page for embedded data"""
        test_result = {
            'name': 'Page Scraping',
            'url': 'https://polymarket.com',
            'method': 'GET',
            'status': 'pending',
            'market_count': 0,
            'data_sources': [],
            'error': None
        }
        
        try:
            async with self.session.get('https://polymarket.com', timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    test_result['status'] = 'success'
                    
                    # Check for various data sources
                    if '__NEXT_DATA__' in html:
                        test_result['data_sources'].append('NEXT_DATA')
                    if 'window.__DATA__' in html:
                        test_result['data_sources'].append('WINDOW_DATA')
                    if 'window.__PRELOADED_STATE__' in html:
                        test_result['data_sources'].append('PRELOADED_STATE')
                    if '"markets":' in html:
                        test_result['data_sources'].append('EMBEDDED_JSON')
                    if 'data-testid="market-card"' in html:
                        test_result['data_sources'].append('HTML_CARDS')
                    
                    # Count market references
                    market_refs = html.count('"markets"')
                    test_result['market_refs_found'] = market_refs
                    
                    # Try to extract market count from common patterns
                    import re
                    
                    # Look for market IDs
                    market_ids = re.findall(r'"id":\s*"([^"]+)"', html)
                    unique_ids = set(market_ids)
                    test_result['unique_ids_found'] = len(unique_ids)
                    
                else:
                    test_result['status'] = 'http_error'
                    test_result['error'] = f'HTTP {response.status}'
                    
        except Exception as e:
            test_result['status'] = 'error'
            test_result['error'] = str(e)
        
        self.results['tests'].append(test_result)
        return test_result
    
    async def test_websocket(self) -> Dict:
        """Test WebSocket connection"""
        test_result = {
            'name': 'WebSocket',
            'url': 'wss://ws-subscriptions-clob.polymarket.com/ws',
            'status': 'pending',
            'error': None
        }
        
        try:
            import websockets
            async with websockets.connect(
                'wss://ws-subscriptions-clob.polymarket.com/ws',
                timeout=10
            ) as ws:
                test_result['status'] = 'success'
                # Try to send a ping
                await ws.send(json.dumps({'type': 'ping'}))
                test_result['ping_response'] = True
        except Exception as e:
            test_result['status'] = 'error'
            test_result['error'] = str(e)
        
        self.results['tests'].append(test_result)
        return test_result
    
    async def check_for_2025_markets(self, sample_market: Dict):
        """Check if sample market contains 2025 data"""
        if sample_market:
            title = sample_market.get('title', '')
            description = sample_market.get('description', '')
            combined = f"{title} {description}".lower()
            
            if '2025' in combined:
                self.results['markets_2025'].append(sample_market)
    
    def print_results(self):
        """Print formatted test results"""
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        
        print(f"\n[OK] WORKING ENDPOINTS ({len(self.results['working_endpoints'])}):")
        for endpoint in self.results['working_endpoints']:
            print(f"  [+] {endpoint['name']}")
            print(f"    URL: {endpoint['url']}")
            print(f"    Status: {endpoint['status_code']}")
            print(f"    Markets: {endpoint['market_count']}")
            print(f"    Response Time: {endpoint['response_time']:.2f}s")
            print()
        
        print(f"\n[FAIL] FAILED ENDPOINTS ({len(self.results['failed_endpoints'])}):")
        for endpoint in self.results['failed_endpoints']:
            print(f"  [-] {endpoint['name']}")
            print(f"    URL: {endpoint['url']}")
            print(f"    Error: {endpoint.get('error', 'Unknown')}")
            print()
        
        print("\n" + "="*80)
        print("DETAILED TEST RESULTS")
        print("="*80)
        
        for test in self.results['tests']:
            status_icon = "[OK]" if test['status'] == 'success' else "[FAIL]"
            print(f"\n{status_icon} {test['name']}")
            print(f"   Status: {test['status']}")
            if 'market_count' in test:
                print(f"   Markets Found: {test['market_count']}")
            if 'data_sources' in test:
                print(f"   Data Sources: {', '.join(test['data_sources'])}")
            if test.get('error'):
                print(f"   Error: {test['error']}")
        
        print("\n" + "="*80)
    
    async def save_results(self, filename: str = 'api_test_results.json'):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"\nResults saved to: {filename}")

async def main():
    """Main test runner"""
    async with PolymarketTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())