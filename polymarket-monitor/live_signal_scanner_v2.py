"""
LIVE POLYMARKET SIGNAL SCANNER V2
More robust with retry logic and better error handling
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# API endpoints
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

class PolymarketScanner:
    """Scans live markets for trading opportunities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def fetch_active_markets_retry(self, max_retries=3) -> List[Dict]:
        """Fetch active markets with retry logic"""
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1}/{max_retries}: Fetching markets...")
                
                # Try primary endpoint
                url = f"{GAMMA_API}/markets"
                params = {
                    'closed': 'false',
                    'limit': 100,
                    '_sort': 'volume24hr',
                    '_order': 'DESC'
                }
                
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                markets = response.json()
                print(f"SUCCESS: Fetched {len(markets)} markets")
                return markets
                
            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    
            except Exception as e:
                print(f"Unexpected error: {e}")
                break
        
        print("FAILED to fetch markets after all retries")
        return []
    
    def analyze_market_patterns(self, markets: List[Dict]) -> Dict:
        """Analyze markets for our 5 edge patterns"""
        signals = {
            'MUSK_FADE_EXTREMES': [],
            'CRYPTO_FADE_BULL': [],
            'SHUTDOWN_POWER_LAW': [],
            'SPOTIFY_MOMENTUM': [],
            'PLAYER_PROPS_UNDER': []
        }
        
        print(f"\nAnalyzing {len(markets)} markets for patterns...\n")
        
        for i, market in enumerate(markets):
            question = market.get('question', '').lower()
            
            # Simple pattern matching (no API calls for prices yet)
            
            # MUSK_FADE_EXTREMES
            if ('elon' in question or 'musk' in question) and ('tweet' in question or 'post' in question):
                if any(x in question for x in ['0-19', '60-79', '80-99', '100+', '0-9']):
                    signals['MUSK_FADE_EXTREMES'].append({
                        'market_id': market.get('id'),
                        'question': market.get('question'),
                        'volume': market.get('volume', 0),
                        'note': 'Extreme Musk tweet prediction detected'
                    })
            
            # CRYPTO_FADE_BULL
            crypto_tokens = ['bitcoin', 'ethereum', 'eth', 'btc', 'solana', 'sol', 'xrp']
            if any(token in question for token in crypto_tokens):
                if 'reach' in question or 'above' in question or 'hit' in question:
                    signals['CRYPTO_FADE_BULL'].append({
                        'market_id': market.get('id'),
                        'question': market.get('question'),
                        'volume': market.get('volume', 0),
                        'note': 'Bullish crypto price target detected'
                    })
            
            # SHUTDOWN_POWER_LAW
            if 'shutdown' in question and ('government' in question or 'federal' in question):
                if any(x in question for x in ['2 day', '4 day', '6 day', '10 day']):
                    signals['SHUTDOWN_POWER_LAW'].append({
                        'market_id': market.get('id'),
                        'question': market.get('question'),
                        'volume': market.get('volume', 0),
                        'note': 'Government shutdown duration market detected'
                    })
            
            # SPOTIFY_MOMENTUM
            if 'spotify' in question and ('#1' in question or 'number 1' in question):
                signals['SPOTIFY_MOMENTUM'].append({
                    'market_id': market.get('id'),
                    'question': market.get('question'),
                    'volume': market.get('volume', 0),
                    'note': 'Spotify chart race detected'
                })
            
            # PLAYER_PROPS_UNDER
            if any(x in question for x in ['points', 'rebounds', 'assists', 'o/u']):
                if any(x in question for x in ['nba', 'lakers', 'warriors', 'celtics', 'bucks']):
                    signals['PLAYER_PROPS_UNDER'].append({
                        'market_id': market.get('id'),
                        'question': market.get('question'),
                        'volume': market.get('volume', 0),
                        'note': 'NBA player prop detected'
                    })
        
        return signals
    
    def generate_report(self, signals: Dict) -> str:
        """Generate human-readable report"""
        lines = []
        lines.append("=" * 80)
        lines.append("POLYMARKET PATTERN DETECTION REPORT")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S CST')}")
        lines.append("=" * 80)
        lines.append("")
        
        total = sum(len(v) for v in signals.values())
        lines.append(f"TOTAL PATTERN MATCHES: {total}")
        lines.append("")
        
        for strategy, matches in signals.items():
            if matches:
                lines.append(f"### {strategy} ({len(matches)} matches)")
                lines.append("")
                
                # Sort by volume
                matches_sorted = sorted(matches, key=lambda x: x.get('volume', 0), reverse=True)
                
                for match in matches_sorted[:5]:  # Top 5 per strategy
                    vol = float(match.get('volume', 0))
                    lines.append(f"  >> {match['question']}")
                    lines.append(f"     Volume: ${vol:,.0f}")
                    lines.append(f"     Note: {match['note']}")
                    lines.append("")
                
                if len(matches) > 5:
                    lines.append(f"  ... and {len(matches) - 5} more")
                    lines.append("")
        
        if total == 0:
            lines.append("No pattern matches found in current active markets.")
        
        lines.append("=" * 80)
        lines.append("")
        lines.append("NEXT STEPS:")
        lines.append("1. Check current prices for each match")
        lines.append("2. Verify edge criteria (Musk <15%, Crypto >40%, etc.)")
        lines.append("3. Execute trades on high-confidence signals")
        lines.append("=" * 80)
        
        return "\n".join(lines)


def main():
    """Main execution"""
    print("Starting Polymarket scanner...")
    print("=" * 80)
    
    scanner = PolymarketScanner()
    
    # Fetch markets
    markets = scanner.fetch_active_markets_retry()
    
    if not markets:
        print("\nNo markets fetched. Check Polymarket API status.")
        return
    
    # Analyze patterns
    signals = scanner.analyze_market_patterns(markets)
    
    # Generate report
    report = scanner.generate_report(signals)
    print("\n" + report)
    
    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = f'live_signals_{timestamp}.json'
    report_file = f'live_report_{timestamp}.txt'
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nFiles saved:")
    print(f"  - {json_file}")
    print(f"  - {report_file}")
    
    return signals


if __name__ == "__main__":
    main()
