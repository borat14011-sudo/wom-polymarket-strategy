#!/usr/bin/env python3
"""
Polymarket Trade Alert System
Monitors for high-value trading opportunities
"""

import requests
import time
from datetime import datetime
from typing import List, Dict, Any

class PolymarketAlerts:
    def __init__(self):
        self.base_url = "https://gamma-api.polymarket.com"
        
    def get_active_markets(self) -> List[Dict]:
        """Fetch all active markets"""
        try:
            response = requests.get(
                f"{self.base_url}/markets",
                params={"active": True, "closed": False, "limit": 100},
                timeout=30
            )
            return response.json()
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return []
    
    def analyze_opportunity(self, market: Dict) -> Dict:
        """Score a market for trading opportunity"""
        score = 0
        reasons = []
        
        # Check volume
        volume = float(market.get('volume', 0))
        if volume > 100000:
            score += 2
            reasons.append(f"High volume: ${volume:,.0f}")
        elif volume > 50000:
            score += 1
            reasons.append(f"Good volume: ${volume:,.0f}")
        
        # Check if it's a validated strategy market
        question = market.get('question', '').lower()
        if 'microstrategy' in question or 'mstr' in question:
            score += 3
            reasons.append("BTC_TIME_BIAS strategy match!")
        
        if 'bitcoin' in question and ('500k' in question or '100k' in question):
            score += 2
            reasons.append("BTC price milestone - good edge")
        
        if 'trump' in question:
            score += 2
            reasons.append("Political event - high interest")
        
        # Price opportunity
        best_ask = float(market.get('bestAsk', 0))
        best_bid = float(market.get('bestBid', 0))
        if best_ask > 0 and best_bid > 0:
            spread = best_ask - best_bid
            if spread < 0.02:
                score += 2
                reasons.append("Tight spread - liquid")
        
        return {
            'market': market,
            'score': score,
            'reasons': reasons,
            'recommendation': 'STRONG' if score >= 5 else 'GOOD' if score >= 3 else 'WATCH'
        }
    
    def find_best_trades(self, min_score: int = 3) -> List[Dict]:
        """Find all trades above minimum score"""
        print(f"[{datetime.now()}] Scanning markets...")
        
        markets = self.get_active_markets()
        opportunities = []
        
        for market in markets:
            analysis = self.analyze_opportunity(market)
            if analysis['score'] >= min_score:
                opportunities.append(analysis)
        
        # Sort by score descending
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        return opportunities
    
    def send_alert(self, opportunity: Dict):
        """Send alert about good trade"""
        market = opportunity['market']
        question = market.get('question', 'Unknown')
        
        print(f"\n{'='*60}")
        print(f"TRADE ALERT - {opportunity['recommendation']}")
        print(f"{'='*60}")
        print(f"Market: {question[:80]}...")
        print(f"Score: {opportunity['score']}/10")
        print(f"\nWhy this trade:")
        for reason in opportunity['reasons']:
            print(f"  • {reason}")
        
        # Prices
        best_bid = float(market.get('bestBid', 0))
        best_ask = float(market.get('bestAsk', 0))
        print(f"\nPrices: Bid {best_bid:.2f}¢ / Ask {best_ask:.2f}¢")
        print(f"Volume: ${float(market.get('volume', 0)):,.0f}")
        
        slug = market.get('marketSlug', market.get('slug', ''))
        if slug:
            print(f"\nTrade: https://polymarket.com/event/{slug}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    alerts = PolymarketAlerts()
    
    print("Scanning for best trading opportunities...\n")
    opportunities = alerts.find_best_trades(min_score=3)
    
    print(f"\n{'='*60}")
    print(f"FOUND {len(opportunities)} GOOD TRADES")
    print(f"{'='*60}\n")
    
    for opp in opportunities[:5]:  # Top 5
        alerts.send_alert(opp)
