#!/usr/bin/env python3
"""
Simple Weather Fade Strategy
Rule: Fade media-hyped weather longshots (prices < 20%)
One market, small trades, 20+ trades for validation
"""

import json
from datetime import datetime

class WeatherFadeStrategy:
    def __init__(self, logger):
        self.logger = logger
        self.rule = "Fade weather longshots priced < 20% when media hype is high"
        
    def find_weather_markets(self, markets_data):
        """Find weather-related markets with prices < 20%"""
        weather_markets = []
        
        for market in markets_data.get('top_markets', []):
            question = market.get('question', '').lower()
            
            # Check if weather-related
            weather_keywords = ['hurricane', 'flood', 'drought', 'heat', 'cold', 
                               'snow', 'rain', 'temperature', 'storm', 'typhoon',
                               'tornado', 'wildfire', 'blizzard']
            
            if any(keyword in question for keyword in weather_keywords):
                # Check for longshot prices (NO side < 20%)
                outcome_prices = market.get('outcome_prices', [])
                if len(outcome_prices) == 2:
                    no_price = outcome_prices[1]  # Assuming second is NO
                    if no_price < 0.20:  # Less than 20%
                        weather_markets.append({
                            'question': market['question'],
                            'slug': market['slug'],
                            'no_price': no_price,
                            'volume': market.get('volume', 0),
                            'condition_id': market.get('condition_id'),
                            'token_ids': market.get('token_ids', [])
                        })
        
        return weather_markets
    
    def assess_hype_level(self, market):
        """Simple hype assessment (to be improved with actual data)"""
        question = market['question'].lower()
        
        hype_score = 0
        # Very simple heuristic
        if 'record' in question:
            hype_score += 2
        if 'worst' in question or 'deadliest' in question:
            hype_score += 2
        if 'historic' in question or 'unprecedented' in question:
            hype_score += 2
        if 'major' in question or 'catastrophic' in question:
            hype_score += 1
            
        return hype_score
    
    def generate_trade_signal(self, market):
        """Generate trade signal based on simple rule"""
        hype_score = self.assess_hype_level(market)
        
        # Rule: Fade if hype >= 2 and price < 20%
        if hype_score >= 2 and market['no_price'] < 0.20:
            return {
                'signal': 'BUY NO',
                'reason': f'Media hype score: {hype_score}, Price: {market["no_price"]:.1%}',
                'confidence': min(hype_score * 10, 70),  # Max 70% confidence
                'target_price': market['no_price'],
                'size_usd': 0.20  # Fixed $0.20 test size
            }
        
        return None
    
    def execute_test_cycle(self):
        """Run one test cycle"""
        print("=" * 60)
        print("WEATHER FADE STRATEGY - TEST CYCLE")
        print("=" * 60)
        
        # Load market data
        try:
            with open('live_bets_output.json', 'r') as f:
                markets_data = json.load(f)
        except FileNotFoundError:
            print("Error: Market data not found. Run live_bets_fetcher.py first.")
            return
        
        # Find weather markets
        weather_markets = self.find_weather_markets(markets_data)
        print(f"Found {len(weather_markets)} weather markets with NO < 20%")
        
        # Assess each market
        signals = []
        for market in weather_markets[:5]:  # Check first 5
            signal = self.generate_trade_signal(market)
            if signal:
                signals.append((market, signal))
                print(f"\n📈 Signal found:")
                print(f"   Market: {market['question'][:60]}...")
                print(f"   Signal: {signal['signal']} @ {market['no_price']:.1%}")
                print(f"   Reason: {signal['reason']}")
                print(f"   Confidence: {signal['confidence']}%")
        
        print(f"\nTotal signals: {len(signals)}")
        
        # Log for tracking (no execution due to Cloudflare)
        for market, signal in signals:
            self.logger.log_trade(
                market=market['question'],
                position=signal['signal'],
                entry_price=market['no_price'],
                size_usd=signal['size_usd'],
                fees_paid=signal['size_usd'] * 0.04,  # Estimate 4% fees
                slippage_pct=0.01,  # Estimate 1% slippage
                notes=f"Weather fade test - {signal['reason']}"
            )
        
        return signals

if __name__ == "__main__":
    from simple_trade_logger import TradeLogger
    
    logger = TradeLogger()
    strategy = WeatherFadeStrategy(logger)
    
    signals = strategy.execute_test_cycle()
    
    if signals:
        print("\n" + "=" * 60)
        print("RECOMMENDED ACTION:")
        print("1. Manually execute ONE of these trades on Polymarket")
        print("2. Track actual entry price, fees, slippage")
        print("3. Update trade logger with real data")
        print("4. Repeat for 20+ trades to validate strategy")
        print("=" * 60)
    else:
        print("\nNo signals generated. Check market data or adjust rules.")