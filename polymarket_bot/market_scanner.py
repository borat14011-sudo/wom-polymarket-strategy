"""
Market Scanner for Polymarket
Fetches active markets, extracts token IDs, checks order book depth
"""

import requests
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class MarketOpportunity:
    """Represents a tradeable market opportunity"""
    question: str
    condition_id: str
    yes_token_id: str
    no_token_id: str
    volume_24h: float
    best_bid: Optional[float] = None
    best_ask: Optional[float] = None
    midpoint: Optional[float] = None
    liquidity_score: float = 0.0

class MarketScanner:
    """Scans Polymarket for tradeable markets"""
    
    def __init__(self, min_daily_volume: float = 1000, scan_limit: int = 100):
        self.min_daily_volume = min_daily_volume
        self.scan_limit = scan_limit
        self.gamma_api_url = "https://gamma-api.polymarket.com/markets"
    
    def fetch_active_markets(self) -> List[Dict]:
        """Fetch active markets from Gamma API"""
        try:
            params = {
                "closed": "false",
                "limit": self.scan_limit
            }
            
            response = requests.get(self.gamma_api_url, params=params, timeout=30)
            response.raise_for_status()
            
            markets = response.json()
            return markets
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching markets: {e}")
            return []
        except ValueError as e:
            print(f"Error parsing market data: {e}")
            return []
    
    def extract_token_ids(self, market: Dict) -> Tuple[Optional[str], Optional[str]]:
        """Extract YES and NO token IDs from a market"""
        yes_token_id = None
        no_token_id = None
        
        if 'tokens' in market:
            for token in market['tokens']:
                if token.get('outcome') == 'YES':
                    yes_token_id = token.get('token_id')
                elif token.get('outcome') == 'NO':
                    no_token_id = token.get('token_id')
        
        return yes_token_id, no_token_id
    
    def calculate_liquidity_score(self, market: Dict) -> float:
        """Calculate a simple liquidity score for a market"""
        score = 0.0
        
        # Volume-based scoring
        volume_24h = market.get('volume24h', 0)
        if volume_24h > 10000:
            score += 3.0
        elif volume_24h > 5000:
            score += 2.0
        elif volume_24h > 1000:
            score += 1.0
        
        # Liquidity metric
        liquidity = market.get('liquidity', 0)
        if liquidity > 100:
            score += 2.0
        elif liquidity > 50:
            score += 1.0
        
        # Number of trades
        num_trades = market.get('numTrades', 0)
        if num_trades > 100:
            score += 1.0
        
        return score
    
    def scan_opportunities(self) -> List[MarketOpportunity]:
        """
        Scan for tradeable market opportunities
        Returns list of markets meeting minimum criteria
        """
        print(f"Scanning for markets with > ${self.min_daily_volume} daily volume...")
        
        markets = self.fetch_active_markets()
        opportunities = []
        
        for market in markets:
            # Check volume
            volume_24h = market.get('volume24h', 0)
            if volume_24h < self.min_daily_volume:
                continue
            
            # Extract token IDs
            yes_token_id, no_token_id = self.extract_token_ids(market)
            if not yes_token_id or not no_token_id:
                continue
            
            # Calculate liquidity score
            liquidity_score = self.calculate_liquidity_score(market)
            
            # Create opportunity
            opportunity = MarketOpportunity(
                question=market.get('question', 'Unknown'),
                condition_id=market.get('conditionId', ''),
                yes_token_id=yes_token_id,
                no_token_id=no_token_id,
                volume_24h=volume_24h,
                liquidity_score=liquidity_score
            )
            
            opportunities.append(opportunity)
        
        # Sort by liquidity score (highest first)
        opportunities.sort(key=lambda x: x.liquidity_score, reverse=True)
        
        print(f"Found {len(opportunities)} tradeable markets out of {len(markets)} scanned")
        
        return opportunities
    
    def get_market_details(self, condition_id: str) -> Optional[Dict]:
        """Get detailed information for a specific market"""
        try:
            url = f"https://gamma-api.polymarket.com/markets/{condition_id}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching market details for {condition_id}: {e}")
            return None
    
    def print_opportunities(self, opportunities: List[MarketOpportunity], limit: int = 10):
        """Print formatted list of opportunities"""
        print(f"\n{'='*80}")
        print(f"TOP {min(limit, len(opportunities))} TRADEABLE MARKETS")
        print(f"{'='*80}")
        
        for i, opp in enumerate(opportunities[:limit]):
            print(f"\n{i+1}. {opp.question[:80]}...")
            print(f"   Condition ID: {opp.condition_id[:20]}...")
            print(f"   24h Volume: ${opp.volume_24h:,.2f}")
            print(f"   Liquidity Score: {opp.liquidity_score:.1f}")
            print(f"   YES Token: {opp.yes_token_id[:20]}...")
            print(f"   NO Token: {opp.no_token_id[:20]}...")

if __name__ == "__main__":
    # Test the scanner
    scanner = MarketScanner(min_daily_volume=1000, scan_limit=50)
    opportunities = scanner.scan_opportunities()
    scanner.print_opportunities(opportunities, limit=5)