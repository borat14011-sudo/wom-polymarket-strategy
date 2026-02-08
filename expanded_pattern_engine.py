"""
EXPANDED PATTERN RESEARCH ENGINE
New pattern categories for 2026 edge detection
"""
import json
import re
from datetime import datetime
from collections import defaultdict

class ExpandedPatternEngine:
    """
    Advanced pattern discovery with new categories:
    - Political prediction markets (fade extreme confidence)
    - Sports props (under bias on high lines)
    - Celebrity/entertainment (hype fade)
    - Economic indicators (recency bias)
    - Technology announcements (buy the rumor, sell the news)
    """
    
    def __init__(self):
        self.patterns = {
            'POLITICAL_EXTREME_FADE': {
                'description': 'Fade >85% confidence in political predictions',
                'keywords': ['trump', 'biden', 'election', 'vote', 'senate', 'house', 'congress', 'president'],
                'confidence_threshold': 0.85,
                'edge_theory': 'Political polls overconfident, Black Swan events common'
            },
            'SPORTS_UNDER_BIAS': {
                'description': 'Player props: public bets over, sharp money on under',
                'keywords': ['points', 'yards', 'rebounds', 'assists', 'touchdowns', 'sacks'],
                'min_line': 20,  # High lines indicate inflated expectations
                'edge_theory': 'Recency bias inflates lines after big games'
            },
            'CELEBRITY_HYPE_FADE': {
                'description': 'Fade extreme hype on celebrity markets',
                'keywords': ['kanye', 'taylor swift', 'album', 'tour', 'streaming', 'grammy', 'oscar'],
                'confidence_threshold': 0.80,
                'edge_theory': 'Fan money creates inflated YES prices'
            },
            'TECH_RUMOR_MOMENTUM': {
                'description': 'Buy rumors on big tech announcements',
                'keywords': ['apple', 'iphone', 'tesla', 'ai', 'gpt', 'chatgpt', 'google', 'meta'],
                'trigger_phrases': ['announce', 'release', 'launch', 'unveil'],
                'edge_theory': 'Information leaks create pre-announcement drift'
            },
            'WEATHER_EXTREME_FADE': {
                'description': 'Fade extreme weather predictions (>90%)',
                'keywords': ['temperature', 'snow', 'rain', 'hurricane', 'storm'],
                'confidence_threshold': 0.90,
                'edge_theory': 'Weather models overconfident on extremes'
            },
            'ECONOMIC_RECENCY_FADE': {
                'description': 'Fade extreme predictions based on recent data',
                'keywords': ['inflation', 'jobs report', 'unemployment', 'gdp', 'fed', 'rate'],
                'confidence_threshold': 0.80,
                'edge_theory': 'Markets overreact to recent economic prints'
            },
            'SPORTS_CHALK_FADE': {
                'description': 'Fade heavy favorites in playoff elimination games',
                'keywords': ['win the series', 'sweep', 'elimination', 'game 7', 'advance'],
                'confidence_threshold': 0.75,
                'edge_theory': 'Elimination games more random than priced'
            },
            'NOVELTY_HYPE_CYCLE': {
                'description': 'Fade peak hype on novelty markets',
                'keywords': ['meme', 'viral', 'tiktok', 'trending', 'will happen'],
                'confidence_threshold': 0.85,
                'edge_theory': 'Novelty markets attract dumb money at peak'
            }
        }
        
        self.opportunities_found = []
    
    def analyze_market(self, market: dict) -> list:
        """Analyze single market for all patterns"""
        question = market.get('question', '').lower()
        matches = []
        
        # Get price if available
        outcome_prices = market.get('outcomePrices', [0.5, 0.5])
        try:
            yes_price = float(outcome_prices[0]) if isinstance(outcome_prices[0], str) else 0.5
        except:
            yes_price = 0.5
        
        for pattern_name, pattern_config in self.patterns.items():
            score = 0
            match_data = {
                'pattern': pattern_name,
                'market_id': market.get('id'),
                'question': market.get('question'),
                'yes_price': yes_price,
                'volume': market.get('volume', 0),
                'confidence': 'NONE'
            }
            
            # Check keywords
            keyword_hits = sum(1 for kw in pattern_config['keywords'] if kw in question)
            if keyword_hits == 0:
                continue
            
            score += keyword_hits * 10
            
            # Check confidence threshold for fade patterns
            threshold = pattern_config.get('confidence_threshold', 0.80)
            if yes_price > threshold:
                score += 50
                match_data['confidence'] = 'HIGH'
                match_data['edge'] = f"Fade YES at {yes_price:.0%}"
            elif yes_price > threshold - 0.10:
                score += 30
                match_data['confidence'] = 'MEDIUM'
                match_data['edge'] = f"Watch for fade entry"
            elif yes_price < 0.20:
                # Low confidence = potential value buy
                score += 20
                match_data['confidence'] = 'VALUE'
                match_data['edge'] = f"Potential value at {yes_price:.0%}"
            
            # Check trigger phrases for momentum patterns
            if 'trigger_phrases' in pattern_config:
                trigger_hits = sum(1 for tp in pattern_config['trigger_phrases'] if tp in question)
                score += trigger_hits * 15
            
            # Minimum score to report
            if score >= 20:
                match_data['score'] = score
                match_data['theory'] = pattern_config['edge_theory']
                matches.append(match_data)
        
        return matches
    
    def scan_markets(self, markets: list) -> dict:
        """Scan all markets and categorize opportunities"""
        print("=" * 80)
        print("EXPANDED PATTERN SCAN")
        print(f"Scanning {len(markets)} markets for edge patterns...")
        print("=" * 80)
        
        results = defaultdict(list)
        
        for market in markets:
            matches = self.analyze_market(market)
            for match in matches:
                results[match['pattern']].append(match)
        
        # Sort by score within each category
        for pattern in results:
            results[pattern] = sorted(results[pattern], key=lambda x: x.get('score', 0), reverse=True)
        
        return dict(results)
    
    def generate_opportunities_report(self, results: dict) -> str:
        """Generate trading opportunities report"""
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("TRADING OPPORTUNITIES REPORT")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        
        total = sum(len(v) for v in results.values())
        lines.append(f"\nTotal Opportunities Found: {total}\n")
        
        for pattern, matches in sorted(results.items(), key=lambda x: len(x[1]), reverse=True):
            if not matches:
                continue
            
            lines.append(f"\n### {pattern.replace('_', ' ')} ({len(matches)} matches)")
            lines.append("-" * 60)
            
            # Show top 3 per pattern
            for match in matches[:3]:
                vol = float(match.get('volume', 0))
                lines.append(f"\n  🎯 Score: {match.get('score', 0)}")
                lines.append(f"     Q: {match['question'][:80]}")
                lines.append(f"     YES Price: {match['yes_price']:.2%} | Volume: ${vol:,.0f}")
                lines.append(f"     Edge: {match.get('edge', 'N/A')}")
                lines.append(f"     Theory: {match.get('theory', 'N/A')[:60]}")
            
            if len(matches) > 3:
                lines.append(f"\n  ... and {len(matches) - 3} more matches")
        
        lines.append("\n" + "=" * 80)
        return "\n".join(lines)
    
    def identify_immediate_trades(self, results: dict) -> list:
        """Extract high-confidence immediate trade opportunities"""
        immediate = []
        
        for pattern, matches in results.items():
            for match in matches:
                if match.get('confidence') == 'HIGH' and match.get('score', 0) >= 50:
                    immediate.append({
                        'pattern': pattern,
                        'market_id': match['market_id'],
                        'question': match['question'],
                        'entry_price': match['yes_price'],
                        'edge': match.get('edge', ''),
                        'rationale': match.get('theory', '')
                    })
        
        return sorted(immediate, key=lambda x: x['entry_price'], reverse=True)


def run_expanded_scan(markets_file=None, markets_data=None):
    """Run full expanded pattern scan"""
    engine = ExpandedPatternEngine()
    
    # Load markets
    if markets_data:
        markets = markets_data
    elif markets_file:
        with open(markets_file, 'r') as f:
            markets = json.load(f)
    else:
        # Try to load latest live scan
        try:
            with open('polymarket-monitor/live_signals_20260208_123629.json', 'r') as f:
                signals = json.load(f)
                # Extract markets from signals structure
                markets = []
                for strategy_matches in signals.values():
                    markets.extend(strategy_matches)
        except:
            print("No markets file found. Please provide markets data.")
            return
    
    # Run scan
    results = engine.scan_markets(markets)
    
    # Generate report
    report = engine.generate_opportunities_report(results)
    print(report)
    
    # Identify immediate trades
    immediate = engine.identify_immediate_trades(results)
    if immediate:
        print("\n" + "=" * 80)
        print("⚡ IMMEDIATE TRADE CANDIDATES")
        print("=" * 80)
        for trade in immediate[:5]:
            print(f"\n  Pattern: {trade['pattern']}")
            print(f"  Market: {trade['question'][:70]}")
            print(f"  Entry: {trade['entry_price']:.2%}")
            print(f"  Edge: {trade['edge']}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output = {
        'timestamp': timestamp,
        'markets_scanned': len(markets),
        'patterns_found': results,
        'immediate_trades': immediate
    }
    
    with open(f'expanded_patterns_{timestamp}.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Results saved to: expanded_patterns_{timestamp}.json")
    
    return results


if __name__ == "__main__":
    # Run with latest live scan data
    run_expanded_scan()
