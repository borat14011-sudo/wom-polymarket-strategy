#!/usr/bin/env python3
"""
🚀 POLYMARKET LIVE MARKET DATA SYSTEM - KIMI 2.5 EDITION
Complete real-time market monitoring system for Wom's trading operation
"""
import requests
import json
import time
import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PolymarketLiveData:
    """Real-time Polymarket data collector with 2025 focus"""
    
    def __init__(self):
        self.base_urls = {
            'gamma': 'https://gamma-api.polymarket.com',
            'clob': 'https://clob.polymarket.com',
            'data': 'https://data-api.polymarket.com'
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Polymarket-Live-Data-System/1.0 (Wom Trading)'
        })
        
    def test_all_endpoints(self) -> Dict:
        """Test all available Polymarket endpoints"""
        logger.info("Testing all Polymarket API endpoints...")
        results = {}
        
        endpoints = [
            # Gamma API endpoints
            ('gamma', '/markets'),
            ('gamma', '/markets?limit=50'),
            ('gamma', '/conditional-tokens'),
            
            # CLOB API endpoints  
            ('clob', '/markets'),
            ('clob', '/markets?limit=100'),
            ('clob', '/orderbook'),
            
            # Data API endpoints
            ('data', '/markets'),
            ('data', '/trades'),
            ('data', '/prices')
        ]
        
        for api, endpoint in endpoints:
            try:
                url = f"{self.base_urls[api]}{endpoint}"
                logger.info(f"Testing: {url}")
                
                response = self.session.get(url, timeout=15)
                results[f"{api}_{endpoint}"] = {
                    'status': response.status_code,
                    'has_data': bool(response.text),
                    'size': len(response.content),
                    'sample': response.text[:200] if response.status_code == 200 else response.text[:100]
                }
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            results[f"{api}_{endpoint}"]['count'] = len(data)
                        elif isinstance(data, dict):
                            results[f"{api}_{endpoint}"]['keys'] = list(data.keys())
                    except:
                        pass
                        
            except Exception as e:
                results[f"{api}_{endpoint}"] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
                
            time.sleep(0.5)  # Rate limiting
            
        return results
    
    def get_live_markets(self, source: str = 'clob', limit: int = 100) -> List[Dict]:
        """Get live markets from specified source"""
        logger.info(f"Getting live markets from {source} (limit: {limit})")
        
        try:
            if source == 'clob':
                url = f"{self.base_urls['clob']}/markets?limit={limit}"
            elif source == 'gamma':
                url = f"{self.base_urls['gamma']}/markets?limit={limit}"
            else:
                url = f"{self.base_urls['data']}/markets?limit={limit}"
                
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if source == 'clob' and 'data' in data:
                    return data['data']
                elif isinstance(data, list):
                    return data
                else:
                    return []
            else:
                logger.error(f"Failed to get markets: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting live markets: {e}")
            return []
    
    def filter_2025_markets(self, markets: List[Dict]) -> List[Dict]:
        """Filter markets for 2025/current events"""
        logger.info(f"Filtering {len(markets)} markets for 2025/current events...")
        
        filtered = []
        keywords_2025 = [
            '2025', '2026', 'trump', 'biden', 'election', 'musk', 'tesla',
            'bitcoin', 'crypto', 'super bowl', 'chiefs', 'eagles', 'president',
            'impeach', 'indict', 'tweet', 'coronavirus', 'covid'
        ]
        
        for market in markets:
            text = ""
            if 'question' in market:
                text = market['question'].lower()
            elif 'title' in market:
                text = market['title'].lower()
            
            end_date = str(market.get('end_date_iso', '')).lower()
            
            # Check for 2025 in question or end date
            if '2025' in text or '2025' in end_date:
                filtered.append(market)
                continue
                
            # Check for current event keywords
            for keyword in keywords_2025:
                if keyword in text:
                    filtered.append(market)
                    break
        
        logger.info(f"Found {len(filtered)} 2025/current markets")
        return filtered
    
    def get_market_prices(self, market_id: str) -> Optional[Dict]:
        """Get current prices for a specific market"""
        try:
            # Try different price endpoints
            endpoints = [
                f"{self.base_urls['clob']}/prices/{market_id}",
                f"{self.base_urls['gamma']}/markets/{market_id}/prices",
                f"{self.base_urls['data']}/markets/{market_id}/price"
            ]
            
            for url in endpoints:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        return response.json()
                except:
                    continue
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting prices for {market_id}: {e}")
            return None
    
    def create_market_summary(self, markets: List[Dict]) -> Dict:
        """Create summary of market data"""
        summary = {
            'total_markets': len(markets),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'categories': {},
            'high_volume_markets': [],
            'recent_markets': []
        }
        
        for market in markets:
            # Categorize by keywords
            text = market.get('question', market.get('title', '')).lower()
            
            if 'super bowl' in text:
                summary['categories']['super_bowl'] = summary['categories'].get('super_bowl', 0) + 1
            elif 'trump' in text or 'biden' in text:
                summary['categories']['politics'] = summary['categories'].get('politics', 0) + 1
            elif 'musk' in text or 'tesla' in text:
                summary['categories']['musk'] = summary['categories'].get('musk', 0) + 1
            elif 'bitcoin' in text or 'crypto' in text:
                summary['categories']['crypto'] = summary['categories'].get('crypto', 0) + 1
            
            # Get volume if available
            volume = market.get('volume', 0)
            if volume and float(volume) > 10000:
                summary['high_volume_markets'].append({
                    'question': market.get('question', market.get('title', '')),
                    'volume': volume,
                    'market_id': market.get('condition_id', market.get('id', ''))
                })
        
        # Sort high volume markets
        summary['high_volume_markets'] = sorted(
            summary['high_volume_markets'], 
            key=lambda x: float(x.get('volume', 0)), 
            reverse=True
        )[:10]
        
        return summary
    
    def save_results(self, data: Dict, filename: str):
        """Save results to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def run_complete_analysis(self):
        """Run complete market analysis"""
        logger.info("🚀 Starting complete Polymarket analysis...")
        
        # Test all endpoints
        endpoint_results = self.test_all_endpoints()
        self.save_results(endpoint_results, 'polymarket_endpoints_test.json')
        
        # Get live markets from best source
        clob_markets = self.get_live_markets('clob', 1000)
        gamma_markets = self.get_live_markets('gamma', 100)
        
        all_markets = clob_markets + gamma_markets
        logger.info(f"Total markets collected: {len(all_markets)}")
        
        # Filter for 2025/current markets
        current_markets = self.filter_2025_markets(all_markets)
        
        # Create summary
        summary = self.create_market_summary(current_markets)
        
        # Save everything
        self.save_results(all_markets, 'all_polymarket_markets.json')
        self.save_results(current_markets, 'current_2025_markets.json')
        self.save_results(summary, 'market_summary.json')
        
        logger.info("✅ Complete analysis finished!")
        
        return {
            'total_markets': len(all_markets),
            'current_markets': len(current_markets),
            'summary': summary,
            'endpoints_tested': len(endpoint_results)
        }

def main():
    """Main execution"""
    print("POLYMARKET LIVE DATA SYSTEM - KIMI 2.5 EDITION")
    print("=" * 60)
    
    collector = PolymarketLiveData()
    
    try:
        results = collector.run_complete_analysis()
        
        print("\nANALYSIS RESULTS:")
        print(f"Total markets found: {results['total_markets']}")
        print(f"Current 2025 markets: {results['current_markets']}")
        print(f"Endpoints tested: {results['endpoints_tested']}")
        
        if results['summary'].get('categories'):
            print(f"\nMARKET CATEGORIES:")
            for category, count in results['summary']['categories'].items():
                print(f"  {category}: {count} markets")
        
        if results['summary'].get('high_volume_markets'):
            print(f"\nHIGH VOLUME MARKETS:")
            for market in results['summary']['high_volume_markets'][:5]:
                print(f"  - {market['question'][:60]}...")
                print(f"    Volume: ${market['volume']:,.0f}")
        
        print(f"\nFiles created:")
        print("  - polymarket_endpoints_test.json")
        print("  - all_polymarket_markets.json") 
        print("  - current_2025_markets.json")
        print("  - market_summary.json")
        
    except Exception as e:
        print(f"❌ System error: {e}")
        logger.error(f"Main execution error: {e}")

if __name__ == "__main__":
    main()