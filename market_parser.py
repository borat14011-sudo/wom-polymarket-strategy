import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from config import *

class MarketParser:
    """Parser for Polymarket market data with 2025 filtering"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.year_patterns = self._compile_year_patterns()
    
    def _compile_year_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for year detection"""
        return {
            '2025': re.compile(r'2025|twenty[-\s]?five|\\b25\\b', re.IGNORECASE),
            'year': re.compile(r'\\b(19|20)\\d{2}\\b'),
            'date': re.compile(r'\\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\\s,]+\\d{1,2}[\\s,]+(?:2025|25)\\b', re.IGNORECASE),
            'month_year': re.compile(r'\\b(?:january|february|march|april|may|june|july|august|september|october|november|december)[\\s,]+2025\\b', re.IGNORECASE)
        }
    
    def filter_2025_markets(self, markets: List[Dict]) -> List[Dict]:
        """Filter markets for 2025 relevance"""
        filtered_markets = []
        
        for market in markets:
            try:
                if self._is_2025_market(market):
                    filtered_markets.append(market)
            except Exception as e:
                self.logger.warning(f"Error filtering market {market.get('id', 'unknown')}: {str(e)}")
                continue
        
        self.logger.info(f"Filtered {len(markets)} markets down to {len(filtered_markets)} 2025 markets")
        return filtered_markets
    
    def _is_2025_market(self, market: Dict) -> bool:
        """Determine if a market is related to 2025"""
        # Check title
        title = market.get('title', '')
        if self.year_patterns['2025'].search(title):
            return True
        
        # Check description
        description = market.get('description', '')
        if self.year_patterns['2025'].search(description):
            return True
        
        # Check if it's a 2025 prediction market
        if self._is_2025_prediction_market(market):
            return True
        
        # Check end date
        end_date = market.get('endDate')
        if end_date and self._is_2025_date(end_date):
            return True
        
        # Check creation date
        created_at = market.get('createdAt')
        if created_at and self._is_2025_date(created_at):
            return True
        
        return False
    
    def _is_2025_prediction_market(self, market: Dict) -> bool:
        """Check if market is a 2025 prediction market"""
        title = market.get('title', '').lower()
        description = market.get('description', '').lower()
        
        # Keywords that suggest 2025 predictions
        prediction_keywords = [
            '2025 election', '2025 president', '2025 crypto', '2025 bitcoin',
            '2025 ethereum', '2025 market', '2025 prediction', '2025 forecast',
            'will happen in 2025', 'by 2025', 'before 2025', 'during 2025'
        ]
        
        combined_text = f"{title} {description}"
        
        for keyword in prediction_keywords:
            if keyword in combined_text:
                return True
        
        return False
    
    def _is_2025_date(self, date_str: str) -> bool:
        """Check if date string refers to 2025"""
        try:
            # Try to parse the date
            if '2025' in str(date_str):
                return True
            
            # Try parsing with dateutil if available
            try:
                from dateutil import parser
                dt = parser.parse(date_str)
                return dt.year == 2025
            except:
                pass
                
        except Exception as e:
            self.logger.debug(f"Error parsing date {date_str}: {str(e)}")
        
        return False
    
    def parse_market_data(self, market: Dict) -> Dict:
        """Parse and standardize market data"""
        try:
            parsed = {
                'id': market.get('id'),
                'title': market.get('title', ''),
                'description': market.get('description', ''),
                'category': market.get('category', ''),
                'subcategory': market.get('subcategory', ''),
                'volume': float(market.get('volume', 0)),
                'liquidity': float(market.get('liquidity', 0)),
                'outcomePrices': market.get('outcomePrices', []),
                'outcomes': market.get('outcomes', []),
                'endDate': market.get('endDate'),
                'createdAt': market.get('createdAt'),
                'closed': market.get('closed', False),
                'resolved': market.get('resolved', False),
                'resolution': market.get('resolution'),
                'image': market.get('image'),
                'icon': market.get('icon'),
                'website': market.get('website'),
                'twitter': market.get('twitter'),
                'discord': market.get('discord'),
                'volume24h': float(market.get('volume24h', 0)),
                'openInterest': float(market.get('openInterest', 0)),
                'lastTradePrice': float(market.get('lastTradePrice', 0)),
                'bestBid': float(market.get('bestBid', 0)),
                'bestAsk': float(market.get('bestAsk', 0)),
                'spread': float(market.get('spread', 0)),
                'lastUpdated': datetime.now().isoformat()
            }
            
            # Add calculated fields
            parsed['is2025'] = self._is_2025_market(market)
            parsed['yearRelevance'] = self._calculate_year_relevance(market)
            parsed['priceChange24h'] = float(market.get('priceChange24h', 0))
            parsed['volumeScore'] = self._calculate_volume_score(parsed)
            parsed['liquidityScore'] = self._calculate_liquidity_score(parsed)
            
            return parsed
            
        except Exception as e:
            self.logger.error(f"Error parsing market {market.get('id', 'unknown')}: {str(e)}")
            return {}
    
    def _calculate_year_relevance(self, market: Dict) -> float:
        """Calculate how relevant a market is to 2025 (0-1 scale)"""
        relevance = 0.0
        
        # Check title and description
        title = market.get('title', '')
        description = market.get('description', '')
        combined_text = f"{title} {description}"
        
        # Direct 2025 mentions
        if self.year_patterns['2025'].search(combined_text):
            relevance += 0.8
        
        # Date patterns
        if self.year_patterns['date'].search(combined_text):
            relevance += 0.3
        
        if self.year_patterns['month_year'].search(combined_text):
            relevance += 0.5
        
        # End date check
        end_date = market.get('endDate')
        if end_date and self._is_2025_date(end_date):
            relevance += 0.6
        
        return min(relevance, 1.0)
    
    def _calculate_volume_score(self, market: Dict) -> float:
        """Calculate volume score (0-1 scale)"""
        volume = market.get('volume', 0)
        
        if volume >= 1000000:  # $1M+
            return 1.0
        elif volume >= 100000:  # $100K+
            return 0.8
        elif volume >= 10000:  # $10K+
            return 0.6
        elif volume >= 1000:  # $1K+
            return 0.4
        else:
            return 0.2
    
    def _calculate_liquidity_score(self, market: Dict) -> float:
        """Calculate liquidity score (0-1 scale)"""
        liquidity = market.get('liquidity', 0)
        
        if liquidity >= 50000:  # $50K+
            return 1.0
        elif liquidity >= 10000:  # $10K+
            return 0.8
        elif liquidity >= 5000:  # $5K+
            return 0.6
        elif liquidity >= 1000:  # $1K+
            return 0.4
        else:
            return 0.2
    
    def filter_by_criteria(self, markets: List[Dict], min_volume: float = MIN_VOLUME_THRESHOLD, 
                          min_liquidity: float = MIN_LIQUIDITY_THRESHOLD) -> List[Dict]:
        """Filter markets by volume and liquidity criteria"""
        filtered = []
        
        for market in markets:
            try:
                volume = float(market.get('volume', 0))
                liquidity = float(market.get('liquidity', 0))
                
                if volume >= min_volume and liquidity >= min_liquidity:
                    filtered.append(market)
                    
            except (ValueError, TypeError):
                continue
        
        self.logger.info(f"Filtered {len(markets)} markets down to {len(filtered)} by volume/liquidity criteria")
        return filtered
    
    def categorize_market(self, market: Dict) -> str:
        """Categorize market based on title and description"""
        title = market.get('title', '').lower()
        description = market.get('description', '').lower()
        combined = f"{title} {description}"
        
        # Politics
        politics_keywords = ['election', 'president', 'vote', 'candidate', 'political', 'democrat', 'republican', 'congress', 'senate']
        if any(keyword in combined for keyword in politics_keywords):
            return 'politics'
        
        # Crypto
        crypto_keywords = ['bitcoin', 'ethereum', 'crypto', 'cryptocurrency', 'blockchain', 'btc', 'eth']
        if any(keyword in combined for keyword in crypto_keywords):
            return 'crypto'
        
        # Sports
        sports_keywords = ['football', 'basketball', 'baseball', 'soccer', 'tennis', 'golf', 'super bowl', 'world cup', 'olympics']
        if any(keyword in combined for keyword in sports_keywords):
            return 'sports'
        
        # Economics
        economics_keywords = ['economy', 'gdp', 'inflation', 'unemployment', 'stock market', 'nasdaq', 'dow', 'federal reserve', 'interest rate']
        if any(keyword in combined for keyword in economics_keywords):
            return 'economics'
        
        # Technology
        tech_keywords = ['technology', 'tech', 'apple', 'google', 'microsoft', 'amazon', 'meta', 'tesla', 'ai', 'artificial intelligence']
        if any(keyword in combined for keyword in tech_keywords):
            return 'technology'
        
        return 'other'