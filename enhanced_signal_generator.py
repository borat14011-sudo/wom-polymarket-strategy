#!/usr/bin/env python3
"""
ENHANCED AUTOMATED SIGNAL GENERATOR V2
Combines real-time scanning with expanded pattern detection
"""
import requests
import json
import time
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# API endpoints
GAMMA_API = "https://gamma-api.polymarket.com"

class SignalDirection(Enum):
    BUY = "BUY"
    SELL = "SELL"

class ConfidenceLevel(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class TradingSignal:
    """Complete trading signal with all metadata"""
    market_id: str
    market_question: str
    direction: SignalDirection
    confidence: ConfidenceLevel
    entry_price: float
    position_size_pct: float
    strategy: str
    edge_rationale: str
    timestamp: str
    
    def to_dict(self):
        return {
            **asdict(self),
            'direction': self.direction.value,
            'confidence': self.confidence.value
        }

class EnhancedSignalGenerator:
    """
    Enhanced signal generator with:
    - Real-time market fetching
    - Multi-strategy pattern detection
    - Automated scoring
    - Immediate opportunity identification
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Strategy configurations
        self.strategies = {
            'BTC_TIME_BIAS': {
                'description': 'Buy BTC up on weekends, avoid weekdays',
                'keywords': ['bitcoin up or down'],
                'entry_threshold': 0.55,  # Buy if YES < 55%
                'confidence': 'MEDIUM',
                'size_pct': 0.03
            },
            'WEATHER_FADE_EXTREME': {
                'description': 'Fade >90% weather predictions',
                'keywords': ['temperature', 'snow', 'rain'],
                'fade_threshold': 0.90,
                'confidence': 'HIGH',
                'size_pct': 0.04
            },
            'POLITICAL_EXTREME_FADE': {
                'description': 'Fade >85% political predictions',
                'keywords': ['trump', 'biden', 'election', 'senate', 'house'],
                'fade_threshold': 0.85,
                'confidence': 'HIGH',
                'size_pct': 0.03
            },
            'SPORTS_PROP_UNDER': {
                'description': 'Player props favor under on high lines',
                'keywords': ['points', 'yards', 'rebounds', 'assists'],
                'min_line_indicator': ['30+', '40+', '50+', '100+'],
                'confidence': 'MEDIUM',
                'size_pct': 0.02
            },
            'CELEBRITY_HYPE_FADE': {
                'description': 'Fade extreme celebrity hype',
                'keywords': ['taylor swift', 'album', 'grammy', 'kanye'],
                'fade_threshold': 0.80,
                'confidence': 'MEDIUM',
                'size_pct': 0.02
            },
            'MUSK_TWEET_FADE': {
                'description': 'Fade extreme Elon tweet predictions',
                'keywords': ['elon', 'musk', 'tweet'],
                'fade_threshold': 0.80,
                'confidence': 'HIGH',
                'size_pct': 0.03
            }
        }
    
    def fetch_active_markets(self, limit=100) -> List[Dict]:
        """Fetch active markets from Polymarket"""
        try:
            url = f"{GAMMA_API}/markets"
            params = {
                'closed': 'false',
                'limit': limit,
                '_sort': 'volume24hr',
                '_order': 'DESC'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            markets = response.json()
            print(f"[OK] Fetched {len(markets)} active markets")
            return markets
            
        except Exception as e:
            print(f"[ERR] Error fetching markets: {e}")
            return []
    
    def get_market_price(self, market: Dict) -> Optional[float]:
        """Extract YES price from market data"""
        try:
            outcome_prices = market.get('outcomePrices', [0.5, 0.5])
            if isinstance(outcome_prices, list) and len(outcome_prices) >= 1:
                return float(outcome_prices[0])
            return 0.5
        except:
            return None
    
    def check_strategy_match(self, market: Dict, strategy_name: str, config: Dict) -> Optional[Dict]:
        """Check if market matches strategy criteria"""
        question = market.get('question', '').lower()
        
        # Check keywords
        keyword_matches = sum(1 for kw in config['keywords'] if kw in question)
        if keyword_matches == 0:
            return None
        
        # Get current price
        yes_price = self.get_market_price(market)
        if yes_price is None:
            return None
        
        signal_data = {
            'market_id': market.get('id'),
            'question': market.get('question'),
            'yes_price': yes_price,
            'volume': market.get('volume', 0),
            'strategy': strategy_name,
            'description': config['description']
        }
        
        # Strategy-specific logic
        if 'fade_threshold' in config:
            # Fade strategy: SELL when YES > threshold
            if yes_price >= config['fade_threshold']:
                signal_data['direction'] = SignalDirection.SELL
                signal_data['confidence'] = ConfidenceLevel.HIGH if yes_price > config['fade_threshold'] + 0.05 else ConfidenceLevel.MEDIUM
                signal_data['edge'] = f"Fade extreme confidence at {yes_price:.0%}"
                signal_data['position_size_pct'] = config['size_pct']
                return signal_data
                
        elif 'entry_threshold' in config:
            # Entry strategy: BUY when YES < threshold
            if yes_price <= config['entry_threshold']:
                signal_data['direction'] = SignalDirection.BUY
                signal_data['confidence'] = ConfidenceLevel.HIGH if yes_price < config['entry_threshold'] - 0.05 else ConfidenceLevel.MEDIUM
                signal_data['edge'] = f"Value entry at {yes_price:.0%}"
                signal_data['position_size_pct'] = config['size_pct']
                return signal_data
        
        return None
    
    def generate_signals(self, markets: List[Dict]) -> List[TradingSignal]:
        """Generate trading signals from market list"""
        signals = []
        
        print(f"\nAnalyzing {len(markets)} markets across {len(self.strategies)} strategies...")
        print("=" * 80)
        
        for market in markets:
            for strategy_name, config in self.strategies.items():
                match = self.check_strategy_match(market, strategy_name, config)
                if match:
                    signal = TradingSignal(
                        market_id=match['market_id'],
                        market_question=match['question'],
                        direction=match['direction'],
                        confidence=match['confidence'],
                        entry_price=match['yes_price'],
                        position_size_pct=match['position_size_pct'],
                        strategy=strategy_name,
                        edge_rationale=match['edge'],
                        timestamp=datetime.now().isoformat()
                    )
                    signals.append(signal)
        
        return signals
    
    def display_signal(self, signal: TradingSignal):
        """Display signal in console"""
        icon = "[BUY]" if signal.direction == SignalDirection.BUY else "[SELL]"
        
        print(f"\n{icon} {signal.direction.value} SIGNAL | {signal.strategy}")
        print(f"   Confidence: {signal.confidence.value}")
        print(f"   Market: {signal.market_question[:80]}")
        print(f"   Entry Price: {signal.entry_price:.2%}")
        print(f"   Position Size: {signal.position_size_pct*100:.1f}%")
        print(f"   Edge: {signal.edge_rationale}")
        print("-" * 80)
    
    def generate_report(self, signals: List[TradingSignal]) -> str:
        """Generate comprehensive report"""
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("ENHANCED SIGNAL GENERATOR REPORT")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        
        # Group by strategy
        by_strategy = {}
        for signal in signals:
            if signal.strategy not in by_strategy:
                by_strategy[signal.strategy] = []
            by_strategy[signal.strategy].append(signal)
        
        lines.append(f"\nTotal Signals Generated: {len(signals)}")
        lines.append(f"Strategies Active: {len(by_strategy)}")
        
        for strategy, strat_signals in sorted(by_strategy.items()):
            lines.append(f"\n### {strategy} ({len(strat_signals)} signals)")
            
            for signal in strat_signals[:3]:  # Top 3 per strategy
                icon = "[BUY]" if signal.direction == SignalDirection.BUY else "[SELL]"
                lines.append(f"\n  {icon} {signal.direction.value} | {signal.confidence.value}")
                lines.append(f"     Q: {signal.market_question[:70]}")
                lines.append(f"     Entry: {signal.entry_price:.2%} | Size: {signal.position_size_pct*100:.1f}%")
                lines.append(f"     {signal.edge_rationale}")
        
        # Immediate action items
        high_conf = [s for s in signals if s.confidence == ConfidenceLevel.HIGH]
        if high_conf:
            lines.append("\n" + "=" * 80)
            lines.append("[ALERT] HIGH CONFIDENCE OPPORTUNITIES")
            lines.append("=" * 80)
            for signal in high_conf[:5]:
                icon = "[BUY]" if signal.direction == SignalDirection.BUY else "[SELL]"
                lines.append(f"\n  {icon} {signal.strategy}")
                lines.append(f"     {signal.market_question[:70]}")
                lines.append(f"     Entry: {signal.entry_price:.2%}")
        
        lines.append("\n" + "=" * 80)
        return "\n".join(lines)
    
    def run(self, continuous=False, interval=300):
        """Main execution loop"""
        print("=" * 80)
        print("ENHANCED SIGNAL GENERATOR V2")
        print("=" * 80)
        
        if continuous:
            print(f"Running in continuous mode (interval: {interval}s)")
            print("Press Ctrl+C to stop\n")
            
            try:
                while True:
                    self._run_once()
                    print(f"\n[SLEEP] Sleeping {interval}s...")
                    time.sleep(interval)
            except KeyboardInterrupt:
                print("\n\n[OK] Generator stopped")
        else:
            self._run_once()
    
    def _run_once(self):
        """Single scan execution"""
        # Fetch markets
        markets = self.fetch_active_markets()
        
        if not markets:
            print("[ERR] No markets fetched")
            return
        
        # Generate signals
        signals = self.generate_signals(markets)
        
        # Display results
        if signals:
            print(f"\n[OK] Generated {len(signals)} trading signals\n")
            for signal in signals[:10]:  # Show first 10
                self.display_signal(signal)
        else:
            print("\n[OK] No signals generated (no pattern matches)")
        
        # Generate and save report
        report = self.generate_report(signals)
        print(report)
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        signals_data = [s.to_dict() for s in signals]
        with open(f'enhanced_signals_{timestamp}.json', 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'markets_scanned': len(markets),
                'signals_generated': len(signals),
                'signals': signals_data
            }, f, indent=2)
        
        with open(f'enhanced_report_{timestamp}.txt', 'w') as f:
            f.write(report)
        
        print(f"\n[DONE] Files saved:")
        print(f"   - enhanced_signals_{timestamp}.json")
        print(f"   - enhanced_report_{timestamp}.txt")


def main():
    parser = argparse.ArgumentParser(description='Enhanced Trading Signal Generator')
    parser.add_argument('--continuous', action='store_true', help='Run continuously')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    generator = EnhancedSignalGenerator()
    generator.run(continuous=args.continuous, interval=args.interval)


if __name__ == "__main__":
    main()
