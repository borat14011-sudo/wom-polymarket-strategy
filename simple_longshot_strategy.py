#!/usr/bin/env python3
"""
Simple Longshot Strategy
Rule: Buy NO positions priced 8-20% in high-volume markets (>$1M)
One rule, small trades, forward testing only
"""

import json
from datetime import datetime
from simple_trade_logger import TradeLogger

class SimpleLongshotStrategy:
    def __init__(self, logger):
        self.logger = logger
        self.rule = "Buy NO positions priced 8-20% in markets >$1M volume"
        
    def find_opportunities(self, markets_data):
        """Find markets matching simple rule"""
        opportunities = []
        
        for market in markets_data.get('top_markets', []):
            question = market.get('question', '')
            volume = market.get('volume', 0)
            prices = market.get('outcome_prices', [])
            
            if len(prices) == 2:
                no_price = prices[1]  # Second is NO
                
                # Rule: NO price 8-20% AND volume > $1M
                if 0.08 <= no_price <= 0.20 and volume > 1000000:
                    opportunities.append({
                        'question': question,
                        'slug': market.get('slug'),
                        'no_price': no_price,
                        'volume': volume,
                        'condition_id': market.get('condition_id'),
                        'token_ids': market.get('token_ids', [])
                    })
        
        return opportunities
    
    def assess_opportunity(self, market):
        """Simple assessment - all opportunities passing rule are equal"""
        # Very simple scoring
        score = 0
        
        # Price closer to 8% is better (more upside)
        if market['no_price'] < 0.12:
            score += 2
        elif market['no_price'] < 0.15:
            score += 1
            
        # Higher volume is better
        if market['volume'] > 5000000:
            score += 2
        elif market['volume'] > 2000000:
            score += 1
            
        return score
    
    def generate_trade_signal(self, market):
        """Generate trade signal - all passing markets get signal"""
        score = self.assess_opportunity(market)
        
        return {
            'signal': 'BUY NO',
            'reason': f'NO @ {market["no_price"]:.1%}, Volume: ${market["volume"]:,.0f}',
            'score': score,
            'target_price': market['no_price'],
            'size_usd': 0.20  # Fixed $0.20 test size
        }
    
    def execute_test_cycle(self):
        """Run one test cycle"""
        print("=" * 60)
        print("SIMPLE LONGSHOT STRATEGY - TEST CYCLE")
        print(f"Rule: {self.rule}")
        print("=" * 60)
        
        # Load market data
        try:
            with open('live_bets_output.json', 'r') as f:
                markets_data = json.load(f)
        except FileNotFoundError:
            print("Error: Market data not found.")
            return []
        
        # Find opportunities
        opportunities = self.find_opportunities(markets_data)
        print(f"Found {len(opportunities)} opportunities matching rule")
        
        # Generate signals
        signals = []
        for market in opportunities:
            signal = self.generate_trade_signal(market)
            signals.append((market, signal))
            
            print(f"\n[OPPORTUNITY {len(signals)}]:")
            print(f"   Market: {market['question'][:70]}...")
            print(f"   Signal: {signal['signal']} @ {market['no_price']:.1%}")
            print(f"   Volume: ${market['volume']:,.0f}")
            print(f"   Score: {signal['score']}/4")
            print(f"   Reason: {signal['reason']}")
        
        # Log for tracking
        for market, signal in signals:
            self.logger.log_trade(
                market=market['question'],
                position=signal['signal'],
                entry_price=market['no_price'],
                size_usd=signal['size_usd'],
                fees_paid=signal['size_usd'] * 0.04,  # Estimate 4% fees
                slippage_pct=0.01,  # Estimate 1% slippage
                notes=f"Simple longshot test - {signal['reason']}"
            )
        
        return signals

if __name__ == "__main__":
    logger = TradeLogger()
    strategy = SimpleLongshotStrategy(logger)
    
    signals = strategy.execute_test_cycle()
    
    if signals:
        print("\n" + "=" * 60)
        print("VALIDATION PLAN:")
        print("1. Execute ONE manual trade on Polymarket")
        print("2. Record ACTUAL entry price, fees, slippage")
        print("3. Track for 20+ trades")
        print("4. Calculate REAL win rate, P&L")
        print("=" * 60)
        
        print("\nRECOMMENDED TRADE:")
        best_market, best_signal = max(signals, key=lambda x: x[1]['score'])
        print(f"Market: {best_market['question'][:80]}")
        print(f"Position: {best_signal['signal']} @ {best_market['no_price']:.1%}")
        print(f"Size: ${best_signal['size_usd']}")
        print(f"URL: https://polymarket.com/event/{best_market['slug']}")
    else:
        print("\nNo opportunities found. Market may need updating.")